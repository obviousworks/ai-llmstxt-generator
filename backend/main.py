from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import aiohttp
import asyncio
import ssl
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import List, Dict, Optional
import time

app = FastAPI(title="LLMs.txt Generator", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CrawlRequest(BaseModel):
    url: HttpUrl
    max_pages: Optional[int] = 20
    depth_limit: Optional[int] = 3

class PageInfo(BaseModel):
    url: str
    title: str
    description: str
    content_length: int
    importance_score: float
    section: str

class LLMSTxtResponse(BaseModel):
    llms_txt: str
    llms_full_txt: str
    pages_analyzed: List[PageInfo]
    generation_time: float

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
        self.site_name = urlparse(base_url).netloc.replace('www.', '').replace('.com', '').replace('.org', '').title()
    
    def generate_summary(self) -> str:
        # Simple summary based on most important pages
        top_pages = self.pages_data[:3]
        if not top_pages:
            return f"A website providing information and resources."
        
        keywords = []
        for page in top_pages:
            title_words = page['title'].lower().split()
            keywords.extend([word for word in title_words if len(word) > 3])
        
        # Get most common meaningful words
        from collections import Counter
        common_words = Counter(keywords).most_common(3)
        if common_words:
            summary = f"A platform providing {', '.join([word[0] for word in common_words])} and related resources."
        else:
            summary = "A website providing information and resources."
        
        return summary
    
    def generate_llms_txt(self) -> str:
        summary = self.generate_summary()
        
        # Group pages by section
        sections = {}
        for page in self.pages_data:
            section = page['section']
            if section not in sections:
                sections[section] = []
            sections[section].append(page)
        
        # Build llms.txt content
        content = f"# {self.site_name}\n\n"
        content += f"> {summary}\n\n"
        
        # Add important information
        top_pages = self.pages_data[:5]
        if top_pages:
            content += "Key information available on this site:\n\n"
            for page in top_pages:
                if page['description']:
                    content += f"- {page['title']}: {page['description']}\n"
                else:
                    content += f"- {page['title']}\n"
            content += "\n"
        
        # Add sections
        for section_name, pages in sections.items():
            if not pages:
                continue
                
            content += f"## {section_name}\n\n"
            
            # Sort by importance within section
            sorted_pages = sorted(pages, key=lambda x: x['importance_score'], reverse=True)
            
            for page in sorted_pages[:10]:  # Limit per section
                title = page['title']
                url = page['url']
                desc = page['description'] if page['description'] else f"Information about {title.lower()}"
                content += f"- [{title}]({url}): {desc}\n"
            
            content += "\n"
        
        # Add optional section for less important content
        optional_pages = [p for p in self.pages_data if p['importance_score'] < 0.3]
        if optional_pages:
            content += "## Optional\n\n"
            for page in optional_pages[:5]:
                title = page['title']
                url = page['url']
                content += f"- [{title}]({url})\n"
            content += "\n"
        
        return content
    
    def generate_llms_full_txt(self) -> str:
        content = f"# {self.site_name} - Complete Documentation\n\n"
        
        summary = self.generate_summary()
        content += f"> {summary}\n\n"
        
        for page in self.pages_data:
            content += f"## {page['title']}\n\n"
            content += f"URL: {page['url']}\n\n"
            if page['description']:
                content += f"Description: {page['description']}\n\n"
            
            # Truncate very long content
            page_content = page['content'][:2000]
            if len(page['content']) > 2000:
                page_content += "... [content truncated]"
            
            content += f"{page_content}\n\n"
            content += "---\n\n"
        
        return content

@app.get("/")
async def root():
    return {"message": "LLMs.txt Generator API", "docs": "/docs"}

@app.post("/generate", response_model=LLMSTxtResponse)
async def generate_llms_txt(request: CrawlRequest):
    start_time = time.time()
    
    try:
        # Crawl the website
        crawler = WebsiteCrawler(
            str(request.url), 
            max_pages=request.max_pages,
            depth_limit=request.depth_limit
        )
        
        pages_data = await crawler.crawl()
        
        if not pages_data:
            raise HTTPException(status_code=400, detail="Could not crawl any pages from the provided URL")
        
        # Generate llms.txt files
        generator = LLMSTxtGenerator(str(request.url), pages_data)
        llms_txt = generator.generate_llms_txt()
        llms_full_txt = generator.generate_llms_full_txt()
        
        # Prepare response
        pages_info = []
        for page in pages_data:
            pages_info.append(PageInfo(
                url=page['url'],
                title=page['title'],
                description=page['description'],
                content_length=page['content_length'],
                importance_score=page['importance_score'],
                section=page['section']
            ))
        
        generation_time = time.time() - start_time
        
        return LLMSTxtResponse(
            llms_txt=llms_txt,
            llms_full_txt=llms_full_txt,
            pages_analyzed=pages_info,
            generation_time=generation_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating llms.txt: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 