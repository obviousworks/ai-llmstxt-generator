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
        content = page_data['content'][:500].lower() if page_data['content'] else ""
        
        # News site specific categorization
        if any(word in url for word in ['nytimes.com', 'washingtonpost.com', 'cnn.com', 'bbc.com', 'reuters.com']):
            if any(word in url or word in title for word in ['subscription', 'subscribe', 'home-delivery', 'digital']):
                return 'Subscription'
            elif any(word in url or word in title for word in ['politics', 'election', 'government']):
                return 'Politics'
            elif any(word in url or word in title for word in ['business', 'economy', 'finance', 'market']):
                return 'Business'
            elif any(word in url or word in title for word in ['world', 'international', 'global']):
                return 'World News'
            elif any(word in url or word in title for word in ['technology', 'tech', 'science']):
                return 'Technology'
            elif any(word in url or word in title for word in ['opinion', 'editorial', 'op-ed']):
                return 'Opinion'
            elif any(word in url or word in title for word in ['sports', 'game', 'team']):
                return 'Sports'
            elif 'about' in url or 'contact' in url or 'help' in url:
                return 'About'
            else:
                return 'News'
        
        # Regular categorization for other sites
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
        
        # Deduplicate pages by base URL (remove fragment duplicates)
        unique_pages = {}
        for page in self.pages_data:
            # Remove URL fragments and query parameters for deduplication
            base_url = page['url'].split('#')[0].split('?')[0]
            
            # Keep the page with the cleanest URL (shortest) if duplicates exist
            if base_url in unique_pages:
                if len(page['url']) < len(unique_pages[base_url]['url']):
                    unique_pages[base_url] = page
            else:
                unique_pages[base_url] = page
        
        # Convert back to list
        self.pages_data = list(unique_pages.values())
        
        # For news sites, limit subscription pages to avoid repetition
        if any(site in self.base_url for site in ['nytimes.com', 'washingtonpost.com', 'cnn.com']):
            subscription_pages = [p for p in self.pages_data if 'subscription' in p['url'].lower()]
            other_pages = [p for p in self.pages_data if 'subscription' not in p['url'].lower()]
            
            # Keep only the main subscription page
            if subscription_pages:
                main_subscription = min(subscription_pages, key=lambda x: len(x['url']))
                self.pages_data = other_pages + [main_subscription]
        
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
            
            # More aggressive content limits for large crawls
            max_content_length = 3000  # Reduced from 5000
            if len(content) > max_content_length:
                if content_type == "section":
                    # For sections, try to keep complete entries by splitting on newlines
                    lines = content.split('\n')
                    truncated_lines = []
                    current_length = 0
                    
                    for line in lines:
                        if current_length + len(line) + 1 <= max_content_length:
                            truncated_lines.append(line)
                            current_length += len(line) + 1
                        else:
                            break
                    
                    content = '\n'.join(truncated_lines)
                    if len(lines) > len(truncated_lines):
                        content += f"\n\n[Note: {len(lines) - len(truncated_lines)} more items truncated for AI processing]"
                else:
                    content = content[:max_content_length] + "..."
            
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
                max_tokens=1500,  # Reduced from 2000 to be more conservative
                temperature=0.2,
                timeout=15
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
        if any(site in self.base_url for site in ['nytimes.com', 'washingtonpost.com', 'cnn.com', 'bbc.com', 'reuters.com']):
            # News site section order
            section_order = ['News', 'Politics', 'Business', 'World News', 'Technology', 'Opinion', 'Sports', 'About', 'Subscription', 'General']
        else:
            # Regular site section order
            section_order = ['Getting Started', 'Documentation', 'API Reference', 'Examples', 'Support', 'General']
        
        for section_name in section_order:
            if section_name in sections:
                pages = sorted(sections[section_name], key=lambda x: x['importance_score'], reverse=True)
                
                # Only include sections that have important pages
                important_pages = [p for p in pages if p['importance_score'] > 0.3]
                if not important_pages:
                    continue
                
                # Limit pages per section for large crawls to manage AI processing
                total_pages = len(self.pages_data)
                if total_pages > 50:
                    # For very large crawls, limit to top 5 pages per section
                    important_pages = important_pages[:5]
                elif total_pages > 20:
                    # For medium crawls, limit to top 8 pages per section
                    important_pages = important_pages[:8]
                # For small crawls (<=20 pages), use all important pages
                
                # Create clean section with simple format
                section_content = f"## {section_name}\n\n"
                
                for page in important_pages:
                    title = page['title']
                    url = page['url']
                    description = page['description']
                    
                    # Create a comprehensive description
                    final_description = ""
                    
                    if description and len(description.strip()) > 10:
                        # Clean up the existing description
                        clean_desc = description.strip()
                        # Remove common prefixes and suffixes
                        clean_desc = clean_desc.replace("Learn more about ", "").replace("Documentation for ", "")
                        if len(clean_desc) > 120:
                            clean_desc = clean_desc[:117] + "..."
                        final_description = clean_desc
                    else:
                        # Generate a meaningful description based on title, URL, and content
                        url_parts = url.lower()
                        title_lower = title.lower()
                        content_start = page['content'][:300].lower() if page['content'] else ""
                        
                        # API-related pages
                        if any(word in title_lower for word in ['api', 'endpoint', 'reference']):
                            if 'authentication' in url_parts or 'auth' in title_lower:
                                final_description = "API authentication and authorization methods"
                            elif 'key' in title_lower:
                                final_description = "API key management and configuration"
                            elif any(word in title_lower for word in ['create', 'post', 'add']):
                                final_description = "API endpoint for creating or adding resources"
                            elif any(word in title_lower for word in ['get', 'retrieve', 'fetch']):
                                final_description = "API endpoint for retrieving data and information"
                            elif any(word in title_lower for word in ['update', 'modify', 'edit']):
                                final_description = "API endpoint for updating and modifying resources"
                            elif any(word in title_lower for word in ['delete', 'remove']):
                                final_description = "API endpoint for deleting and removing resources"
                            elif 'list' in title_lower:
                                final_description = "API endpoint for listing and browsing resources"
                            else:
                                final_description = "API documentation and technical reference"
                        
                        # Documentation pages
                        elif any(word in title_lower for word in ['guide', 'tutorial', 'how to', 'getting started']):
                            if 'quick' in title_lower or 'start' in title_lower:
                                final_description = "Quick start guide and initial setup instructions"
                            elif 'install' in title_lower:
                                final_description = "Installation and setup guide"
                            else:
                                final_description = "Step-by-step guide and tutorial information"
                        
                        # Example pages
                        elif any(word in title_lower for word in ['example', 'sample', 'demo']):
                            final_description = "Code examples and practical implementation samples"
                        
                        # Configuration pages
                        elif any(word in title_lower for word in ['config', 'setting', 'option']):
                            final_description = "Configuration options and settings documentation"
                        
                        # Error/troubleshooting pages
                        elif any(word in title_lower for word in ['error', 'troubleshoot', 'debug', 'faq']):
                            final_description = "Troubleshooting guide and common issues resolution"
                        
                        # Legal/policy pages
                        elif any(word in title_lower for word in ['privacy', 'terms', 'policy', 'legal']):
                            final_description = "Legal documentation and policy information"
                        
                        # Try to extract meaningful description from content
                        elif page['content'] and len(page['content']) > 50:
                            # Get first meaningful sentence from content
                            content_sentences = page['content'].split('.')[:3]
                            meaningful_content = []
                            for sentence in content_sentences:
                                sentence = sentence.strip()
                                if len(sentence) > 20 and not sentence.startswith(('©', 'Copyright', 'All rights')):
                                    meaningful_content.append(sentence)
                                    if len(meaningful_content) >= 2:
                                        break
                            
                            if meaningful_content:
                                combined = '. '.join(meaningful_content)
                                if len(combined) > 120:
                                    combined = combined[:117] + "..."
                                final_description = combined
                            else:
                                final_description = f"Information and documentation about {title.lower()}"
                        
                        # Final fallback
                        else:
                            final_description = f"Documentation and information about {title.lower()}"
                    
                    # Ensure description starts with capital letter and ends properly
                    if final_description:
                        final_description = final_description[0].upper() + final_description[1:]
                        if not final_description.endswith(('.', '!', '?')):
                            final_description += "."
                    
                    section_content += f"- [{title}]({url}): {final_description}\n"
                
                section_content += "\n"
                
                # Use AI to clean up the section format and descriptions, but be selective
                should_use_ai = True
                total_pages = len(self.pages_data)
                
                # Skip AI for less important sections if there are many pages
                if total_pages > 50:
                    # Only use AI for the most important sections
                    priority_sections = ['Getting Started', 'Documentation', 'API Reference', 'News', 'Politics']
                    should_use_ai = section_name in priority_sections
                elif total_pages > 100:
                    # For very large crawls, skip AI enhancement entirely to avoid timeouts
                    should_use_ai = False
                
                if should_use_ai:
                    cleaned_section = self.cleanup_with_openai(section_content, "section")
                    content += cleaned_section
                else:
                    content += section_content
        
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
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                error_response = json.dumps({'error': 'No request body provided'})
                self.wfile.write(error_response.encode())
                return
            
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Extract parameters
            url = request_data.get('url')
            max_pages = request_data.get('max_pages', 20)
            depth_limit = request_data.get('depth_limit', 3)
            
            if not url:
                error_response = json.dumps({'error': 'URL is required'})
                self.wfile.write(error_response.encode())
                return
            
            # Run the async crawling process
            result = asyncio.run(self.process_request(url, max_pages, depth_limit))
            
            # Ensure result is not None or empty
            if not result:
                error_response = json.dumps({'error': 'Failed to generate result'})
                self.wfile.write(error_response.encode())
                return
            
            # Send response
            response_json = json.dumps(result, ensure_ascii=False)
            self.wfile.write(response_json.encode('utf-8'))
            
        except json.JSONDecodeError as e:
            self._send_error_response(400, f'Invalid JSON in request: {str(e)}')
        except Exception as e:
            print(f"Unexpected error in handler: {str(e)}")
            self._send_error_response(500, f'Error generating llms.txt: {str(e)}')
    
    def _send_error_response(self, status_code: int, error_message: str):
        """Send a properly formatted error response"""
        try:
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = json.dumps({'error': error_message})
            self.wfile.write(error_response.encode('utf-8'))
        except Exception as e:
            print(f"Failed to send error response: {e}")
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    async def process_request(self, url: str, max_pages: int, depth_limit: int):
        start_time = time.time()
        
        try:
            # First, check if the website already has an llms.txt file
            existing_llms_txt = await self.check_existing_llms_txt(url)
            if existing_llms_txt:
                return {
                    'llms_txt': existing_llms_txt,
                    'llms_full_txt': existing_llms_txt,
                    'pages_analyzed': [{
                        'url': f"{url.rstrip('/')}/llms.txt",
                        'title': 'Existing llms.txt',
                        'description': 'Found existing llms.txt file on the website',
                        'content_length': len(existing_llms_txt),
                        'importance_score': 1.0,
                        'section': 'Existing Documentation'
                    }],
                    'generation_time': time.time() - start_time,
                    'ai_enhanced': False,
                    'ai_model': None,
                    'used_existing': True
                }
            
            # Initialize crawler
            crawler = WebsiteCrawler(url, max_pages, depth_limit)
            
            # Crawl the website
            pages_data = await crawler.crawl()
            
            if not pages_data:
                raise Exception("No pages could be crawled from the provided URL")
            
            # Generate llms.txt files
            generator = LLMSTxtGenerator(url, pages_data)
            
            # Log AI processing strategy based on crawl size
            total_pages = len(pages_data)
            if total_pages > 100:
                print(f"Large crawl detected ({total_pages} pages) - AI enhancement disabled to ensure fast processing")
            elif total_pages > 50:
                print(f"Medium-large crawl detected ({total_pages} pages) - AI enhancement limited to priority sections")
            elif total_pages > 20:
                print(f"Medium crawl detected ({total_pages} pages) - AI enhancement with page limits per section")
            else:
                print(f"Small crawl detected ({total_pages} pages) - full AI enhancement enabled")
            
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
                'ai_model': ai_model,
                'used_existing': False
            }
            
        except Exception as e:
            print(f"Error in process_request: {str(e)}")
            raise e
    
    async def check_existing_llms_txt(self, base_url: str) -> Optional[str]:
        """Check if the website already has an llms.txt file"""
        try:
            # Try common locations for llms.txt
            possible_urls = [
                f"{base_url.rstrip('/')}/llms.txt",
                f"{base_url.rstrip('/')}/.well-known/llms.txt",
            ]
            
            # Create SSL context that doesn't verify certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                for llms_url in possible_urls:
                    try:
                        headers = {
                            'User-Agent': 'LLMs.txt Generator Bot',
                            'Accept': 'text/plain,text/markdown,text/*',
                        }
                        
                        async with session.get(
                            llms_url,
                            timeout=aiohttp.ClientTimeout(total=10),
                            headers=headers,
                            ssl=ssl_context
                        ) as response:
                            if response.status == 200:
                                content_type = response.headers.get('content-type', '').lower()
                                if any(ct in content_type for ct in ['text/', 'application/octet-stream']):
                                    content = await response.text()
                                    if content.strip() and len(content) > 50:  # Basic validation
                                        print(f"Found existing llms.txt at {llms_url}")
                                        return content
                    except Exception as e:
                        print(f"Error checking {llms_url}: {e}")
                        continue
            
            return None
            
        except Exception as e:
            print(f"Error checking for existing llms.txt: {e}")
            return None 