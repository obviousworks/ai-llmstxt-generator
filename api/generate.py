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
        
        return summary
    
    def generate_llms_txt(self) -> str:
        domain = urlparse(self.base_url).netloc
        
        # Header
        content = f"# {domain}\n\n"
        content += self.generate_summary() + "\n\n"
        
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
                content += f"## {section_name}\n\n"
                
                for page in pages:
                    if page['importance_score'] > 0.3:  # Only include important pages
                        content += f"### {page['title']}\n"
                        content += f"URL: {page['url']}\n"
                        if page['description']:
                            content += f"Description: {page['description']}\n"
                        
                        # Truncate content for readability
                        page_content = page['content'][:1000]
                        if len(page['content']) > 1000:
                            page_content += "..."
                        
                        content += f"\n{page_content}\n\n"
                        content += "---\n\n"
        
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
        
        return {
            'llms_txt': llms_txt,
            'llms_full_txt': llms_full_txt,
            'pages_analyzed': pages_analyzed,
            'generation_time': generation_time
        } 