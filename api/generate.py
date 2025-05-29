from http.server import BaseHTTPRequestHandler
import json
import asyncio
import aiohttp
import ssl
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import List, Dict, Optional
import time
import os

# Initialize OpenAI client only if API key is available
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai_client = None

if OPENAI_API_KEY:
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        print("OpenAI client initialized successfully")
    except ImportError:
        print("OpenAI library not available")
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}")
        openai_client = None
else:
    print("No OpenAI API key found - AI enhancement will be disabled")

class WebsiteCrawler:
    def __init__(self, base_url: str, max_pages: int = 20, depth_limit: int = 3):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.max_pages = max_pages
        self.depth_limit = depth_limit
        self.visited_urls = set()
        self.pages_data = []
        
        # Create SSL context that doesn't verify certificates for problematic sites
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
    async def fetch_page(self, session: aiohttp.ClientSession, url: str) -> Optional[Dict]:
        try:
            # Add proper headers to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            async with session.get(
                url, 
                timeout=aiohttp.ClientTimeout(total=15),
                headers=headers,
                ssl=self.ssl_context
            ) as response:
                if response.status != 200:
                    return None
                
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract metadata
                title = soup.find('title')
                title = title.get_text().strip() if title else url.split('/')[-1]
                
                description = soup.find('meta', attrs={'name': 'description'})
                description = description.get('content', '').strip() if description else ''
                
                # Remove scripts, styles, nav, footer, etc.
                for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                    tag.decompose()
                
                # Get main content
                main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main'))
                if not main_content:
                    main_content = soup.find('body')
                
                content_text = main_content.get_text() if main_content else soup.get_text()
                content_text = ' '.join(content_text.split())  # Clean whitespace
                
                # Find internal links
                links = []
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(url, href)
                    if urlparse(full_url).netloc == self.domain and full_url not in self.visited_urls:
                        links.append(full_url)
                
                return {
                    'url': url,
                    'title': title,
                    'description': description,
                    'content': content_text,
                    'content_length': len(content_text),
                    'links': links[:10]  # Limit links per page
                }
                
        except Exception as e:
            print(f"Error fetching {url}: {type(e).__name__}: {e}")
            return None
    
    def calculate_importance_score(self, page_data: Dict, all_pages: List[Dict]) -> float:
        score = 0.0
        
        # Title keywords that suggest importance
        important_keywords = ['api', 'docs', 'documentation', 'guide', 'tutorial', 'getting started', 'quickstart', 'reference']
        title_lower = page_data['title'].lower()
        for keyword in important_keywords:
            if keyword in title_lower:
                score += 0.3
        
        # URL depth (closer to root = more important)
        url_depth = len(urlparse(page_data['url']).path.split('/')) - 1
        score += max(0, (5 - url_depth) * 0.1)
        
        # Content length (reasonable length preferred)
        content_length = page_data['content_length']
        if 500 < content_length < 5000:
            score += 0.2
        elif content_length >= 5000:
            score += 0.1
        
        # Check if URL suggests it's important content
        url_lower = page_data['url'].lower()
        for keyword in important_keywords:
            if keyword in url_lower:
                score += 0.2
        
        return min(score, 1.0)
    
    def categorize_page(self, page_data: Dict) -> str:
        url = page_data['url'].lower()
        title = page_data['title'].lower()
        
        if any(word in url or word in title for word in ['api', 'reference']):
            return 'API Reference'
        elif any(word in url or word in title for word in ['guide', 'tutorial', 'getting-started', 'quickstart']):
            return 'Getting Started'
        elif any(word in url or word in title for word in ['docs', 'documentation']):
            return 'Documentation'
        elif any(word in url or word in title for word in ['example', 'demo']):
            return 'Examples'
        elif any(word in url or word in title for word in ['faq', 'help', 'support']):
            return 'Support'
        else:
            return 'General'
    
    async def crawl(self) -> List[Dict]:
        # Create connector with SSL context
        connector = aiohttp.TCPConnector(ssl=self.ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            queue = [(self.base_url, 0)]  # (url, depth)
            
            while queue and len(self.visited_urls) < self.max_pages:
                url, depth = queue.pop(0)
                
                if url in self.visited_urls or depth > self.depth_limit:
                    continue
                
                self.visited_urls.add(url)
                page_data = await self.fetch_page(session, url)
                
                if page_data:
                    self.pages_data.append(page_data)
                    
                    # Add new links to queue
                    for link in page_data['links']:
                        if link not in self.visited_urls:
                            queue.append((link, depth + 1))
        
        # Calculate importance scores
        for page in self.pages_data:
            page['importance_score'] = self.calculate_importance_score(page, self.pages_data)
            page['section'] = self.categorize_page(page)
        
        return self.pages_data

class LLMSTxtGenerator:
    def __init__(self, base_url: str, pages_data: List[Dict]):
        self.base_url = base_url
        self.pages_data = sorted(pages_data, key=lambda x: x['importance_score'], reverse=True)
    
    def cleanup_with_openai(self, content: str, content_type: str = "summary") -> str:
        """Clean up content using OpenAI to improve readability and structure"""
        global openai_client
        
        try:
            if not openai_client:
                return content
            
            # Limit content length to avoid token limits (increased from 3000)
            if len(content) > 5000:
                content = content[:5000] + "..."
                return content
            
            if content_type == "summary":
                prompt = f"""Please clean up and improve this website summary for an llms.txt file. Make it more concise, professional, and informative while maintaining all key information. Focus on clarity and usefulness for AI systems:

{content}

Return only the improved summary without any additional commentary."""
            
            elif content_type == "section":
                prompt = f"""Please clean up and improve this documentation section for an llms.txt file. Your goals:

1. **Keep the simple format**: Maintain the "- [Title](URL): Description" format for each link
2. **Improve descriptions**: Make descriptions concise, clear, and informative (1-2 sentences max)
3. **Remove redundancy**: Eliminate duplicate information between titles and descriptions
4. **Standardize language**: Use consistent, professional language throughout
5. **Preserve all links**: Keep every URL and title exactly as provided
6. **Organize logically**: Ensure items are in a logical order within the section

The output should be a clean, simple list like this example:
- [API Reference](url): Clear description of what this covers
- [Getting Started Guide](url): Brief explanation of the content

Original content:
{content}

Return only the improved section with the same simple link format."""
            
            else:
                return content  # Return original if unknown type
            
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert technical writer and documentation specialist. Your goal is to transform raw web content into well-structured, highly readable documentation that's perfect for AI consumption. Focus on clarity, organization, and preserving all important information while dramatically improving readability."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,  # Increased from 1000 to allow more comprehensive cleanup
                temperature=0.2,  # Lower temperature for more consistent formatting
                timeout=15  # Increased timeout for more complex processing
            )
            
            cleaned_content = response.choices[0].message.content.strip()
            return cleaned_content if cleaned_content else content
            
        except Exception as e:
            print(f"OpenAI cleanup failed: {e}")
            return content  # Return original content if OpenAI fails
    
    def generate_summary(self) -> str:
        # Simple summary based on most important pages
        domain = urlparse(self.base_url).netloc
        top_pages = self.pages_data[:5]
        
        summary = f"# {domain}\n\n"
        summary += f"This documentation covers {len(self.pages_data)} pages from {domain}.\n\n"
        
        # Group by sections
        sections = {}
        for page in self.pages_data:
            section = page['section']
            if section not in sections:
                sections[section] = []
            sections[section].append(page)
        
        summary += "## Sections\n\n"
        for section, pages in sections.items():
            summary += f"- **{section}**: {len(pages)} pages\n"
        
        summary += "\n## Key Pages\n\n"
        for page in top_pages:
            summary += f"- [{page['title']}]({page['url']})\n"
        
        # Clean up the summary with OpenAI
        return self.cleanup_with_openai(summary, "summary")
    
    def generate_llms_txt(self) -> str:
        domain = urlparse(self.base_url).netloc
        
        # Header
        content = f"# {domain}\n\n"
        
        # Group pages by section
        sections = {}
        for page in self.pages_data:
            section = page['section']
            if section not in sections:
                sections[section] = []
            sections[section].append(page)
        
        # Sort sections by importance
        section_order = ['Getting Started', 'Documentation', 'API Reference', 'Examples', 'Support', 'General']
        
        for section_name in section_order:
            if section_name in sections:
                pages = sorted(sections[section_name], key=lambda x: x['importance_score'], reverse=True)
                
                # Only include sections that have important pages
                important_pages = [p for p in pages if p['importance_score'] > 0.3]
                if not important_pages:
                    continue
                
                # Create clean section with simple format
                section_content = f"## {section_name}\n\n"
                
                for page in important_pages:
                    title = page['title']
                    url = page['url']
                    description = page['description']
                    
                    # Create a clean description
                    if description and len(description) > 10:
                        # Clean up the description
                        clean_desc = description.strip()
                        if len(clean_desc) > 100:
                            clean_desc = clean_desc[:97] + "..."
                        section_content += f"- [{title}]({url}): {clean_desc}\n"
                    else:
                        # Generate a simple description from title or content
                        if 'api' in title.lower():
                            simple_desc = "API documentation and reference"
                        elif 'guide' in title.lower() or 'tutorial' in title.lower():
                            simple_desc = "Guide and tutorial information"
                        elif 'example' in title.lower():
                            simple_desc = "Examples and sample code"
                        elif 'doc' in title.lower():
                            simple_desc = "Documentation and information"
                        else:
                            # Extract a brief description from content
                            content_words = page['content'][:200].split()
                            if len(content_words) > 10:
                                simple_desc = ' '.join(content_words[:15]) + "..."
                            else:
                                simple_desc = f"Information about {title.lower()}"
                        
                        section_content += f"- [{title}]({url}): {simple_desc}\n"
                
                section_content += "\n"
                
                # Use AI to clean up the section format and descriptions
                cleaned_section = self.cleanup_with_openai(section_content, "section")
                content += cleaned_section
        
        # Add optional section for less important but potentially useful pages
        optional_pages = [p for p in self.pages_data if p['importance_score'] <= 0.3 and p['importance_score'] > 0.1]
        if optional_pages:
            content += "## Optional\n\n"
            for page in optional_pages[:5]:  # Limit to 5 optional pages
                title = page['title']
                url = page['url']
                content += f"- [{title}]({url})\n"
            content += "\n"
        
        return content
    
    def generate_llms_full_txt(self) -> str:
        domain = urlparse(self.base_url).netloc
        
        content = f"# {domain} - Complete Documentation\n\n"
        content += f"Generated from {len(self.pages_data)} pages\n\n"
        
        for page in self.pages_data:
            content += f"## {page['title']}\n"
            content += f"URL: {page['url']}\n"
            content += f"Section: {page['section']}\n"
            content += f"Importance: {page['importance_score']:.2f}\n"
            if page['description']:
                content += f"Description: {page['description']}\n"
            content += f"\n{page['content']}\n\n"
            content += "=" * 80 + "\n\n"
        
        return content

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Set CORS headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Extract parameters
            url = request_data.get('url')
            max_pages = request_data.get('max_pages', 20)
            depth_limit = request_data.get('depth_limit', 3)
            
            if not url:
                self.wfile.write(json.dumps({'error': 'URL is required'}).encode())
                return
            
            # Run the async crawling process
            result = asyncio.run(self.process_request(url, max_pages, depth_limit))
            
            # Send response
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    async def process_request(self, url: str, max_pages: int, depth_limit: int):
        start_time = time.time()
        
        # Initialize crawler
        crawler = WebsiteCrawler(url, max_pages, depth_limit)
        
        # Crawl the website
        pages_data = await crawler.crawl()
        
        if not pages_data:
            raise Exception("No pages could be crawled from the provided URL")
        
        # Generate llms.txt files
        generator = LLMSTxtGenerator(url, pages_data)
        llms_txt = generator.generate_llms_txt()
        llms_full_txt = generator.generate_llms_full_txt()
        
        # Prepare response
        pages_analyzed = []
        for page in pages_data:
            pages_analyzed.append({
                'url': page['url'],
                'title': page['title'],
                'description': page['description'],
                'content_length': page['content_length'],
                'importance_score': page['importance_score'],
                'section': page['section']
            })
        
        generation_time = time.time() - start_time
        
        # Determine if AI enhancement was actually used
        ai_enhanced = openai_client is not None
        ai_model = 'gpt-4o-mini' if ai_enhanced else None
        
        return {
            'llms_txt': llms_txt,
            'llms_full_txt': llms_full_txt,
            'pages_analyzed': pages_analyzed,
            'generation_time': generation_time,
            'ai_enhanced': ai_enhanced,
            'ai_model': ai_model
        } 