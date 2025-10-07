from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, Field
import aiohttp
import asyncio
import ssl
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import List, Dict, Optional, Literal, Set
import time
import os
import json
import xml.etree.ElementTree as ET

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
    crawl_all: Optional[bool] = False
    generation_type: Optional[Literal["summary", "fulltext", "both"]] = "both"

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
    ai_enhanced: bool
    ai_model: Optional[str]
    used_existing: Optional[bool] = False
    site_characteristics: Optional[Dict] = None

class PageAnalysis(BaseModel):
    """AI analysis of a single page's content and purpose"""
    category: str = Field(description="Meaningful category that best describes this page's purpose")
    content_type: Literal["documentation", "tutorial", "reference", "news", "product", "support", "legal", "marketing", "other"] = Field(description="High-level content type")
    importance_factors: List[str] = Field(description="List of factors that make this page important or unique")
    description: str = Field(description="Clear, informative description of what this page offers (1-2 sentences)")
    keywords: List[str] = Field(description="3-5 key terms that best represent this page's content")

class SiteAnalysis(BaseModel):
    """AI analysis of the entire website's structure and purpose"""
    site_purpose: str = Field(description="Primary purpose and nature of this website")
    target_audience: str = Field(description="Primary intended audience for this site")
    main_categories: List[str] = Field(description="3-8 logical content categories that best organize this site's pages")
    category_descriptions: Dict[str, str] = Field(description="Brief description of what each category contains")
    site_summary: str = Field(description="2-3 sentence summary of what this website offers")

class CategoryAssignment(BaseModel):
    """AI assignment of pages to categories"""
    assignments: Dict[str, str] = Field(description="Mapping of page index (as string) to category name")
    rationale: Dict[str, str] = Field(description="Brief explanation for each category assignment")

class ContentAnalysis(BaseModel):
    """AI analysis of page content to generate descriptions"""
    enhanced_descriptions: Dict[str, str] = Field(description="Improved descriptions for each page (page index as key)")
    content_themes: List[str] = Field(description="Major themes found across the analyzed content")
    quality_improvements: List[str] = Field(description="Suggestions for description improvements")

class WebsiteCrawler:
    def __init__(self, base_url: str, max_pages: int = 20, depth_limit: int = 3, crawl_all: bool = False):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.max_pages = max_pages if not crawl_all else 999999
        self.depth_limit = depth_limit if not crawl_all else 999
        self.crawl_all = crawl_all
        self.visited_urls = set()
        self.pages_data = []
        
        # Create SSL context that doesn't verify certificates for problematic sites
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
        # Cache for site characteristics determined by AI
        self._site_characteristics = None
        
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
                
                # Extract FAQs from JSON-LD Schema.org markup
                faqs = self._extract_faqs_from_schema(soup)
                
                # Remove styles, nav, footer, etc. (but keep scripts for now to extract JSON-LD)
                for tag in soup(['style', 'nav', 'footer', 'header', 'aside']):
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
                    'links': links[:10],  # Limit links per page
                    'faqs': faqs  # Include extracted FAQs
                }
                
        except Exception as e:
            print(f"Error fetching {url}: {type(e).__name__}: {e}")
            return None
    
    def _extract_faqs_from_schema(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract FAQs from JSON-LD Schema.org FAQPage markup"""
        faqs = []
        
        try:
            # Find all script tags with type="application/ld+json"
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    
                    # Check if this is a FAQPage
                    if isinstance(data, dict) and data.get('@type') == 'FAQPage':
                        main_entity = data.get('mainEntity', [])
                        
                        for item in main_entity:
                            if item.get('@type') == 'Question':
                                question = item.get('name', '')
                                answer_obj = item.get('acceptedAnswer', {})
                                answer = answer_obj.get('text', '') if isinstance(answer_obj, dict) else ''
                                
                                if question and answer:
                                    faqs.append({
                                        'question': question,
                                        'answer': answer
                                    })
                                    
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"Error parsing JSON-LD: {e}")
                    continue
            
            if faqs:
                print(f"  ✓ Extracted {len(faqs)} FAQs from Schema.org markup")
                
        except Exception as e:
            print(f"Error extracting FAQs: {e}")
        
        return faqs
    
    def calculate_importance_score(self, page_data: Dict, all_pages: List[Dict]) -> float:
        """Calculate importance score using AI analysis if available, otherwise use adaptive heuristics"""
        
        # If we have AI analysis data, use it for better scoring
        if 'importance_factors' in page_data and page_data['importance_factors']:
            return self._calculate_ai_importance_score(page_data)
        
        # Use adaptive heuristics based on content patterns
        return self._calculate_adaptive_importance_score(page_data, all_pages)
    
    def _calculate_ai_importance_score(self, page_data: Dict) -> float:
        """Calculate importance using AI analysis factors"""
        base_score = 0.0
        importance_factors = page_data['importance_factors']
        
        # Score based on AI-identified importance factors
        factor_weights = {
            'primary navigation': 0.4,
            'documentation entry point': 0.4,
            'api reference': 0.3,
            'getting started': 0.4,
            'core feature': 0.3,
            'main product': 0.3,
            'news article': 0.2,
            'support resource': 0.2,
            'recent content': 0.2,
            'comprehensive guide': 0.3,
            'detailed reference': 0.3,
        }
        
        for factor in importance_factors:
            factor_lower = factor.lower()
            for key, weight in factor_weights.items():
                if key in factor_lower:
                    base_score += weight
                    break
            else:
                # Any AI-identified factor adds some base importance
                base_score += 0.1
        
        # Factor in content type if available
        content_type = page_data.get('content_type', 'other')
        type_bonuses = {
            'documentation': 0.2,
            'tutorial': 0.2,
            'reference': 0.3,
            'news': 0.1,
            'product': 0.2,
            'support': 0.1
        }
        base_score += type_bonuses.get(content_type, 0)
        
        return min(base_score, 1.0)
    
    def _calculate_adaptive_importance_score(self, page_data: Dict, all_pages: List[Dict]) -> float:
        """Calculate importance using adaptive heuristics"""
        score = 0.0
        
        # URL depth (closer to root = more important)
        url_depth = len(urlparse(page_data['url']).path.split('/')) - 1
        score += max(0, (5 - url_depth) * 0.1)
        
        # Content length (reasonable length preferred)
        content_length = page_data['content_length']
        if 500 < content_length < 5000:
            score += 0.2
        elif content_length >= 5000:
            score += 0.1
        
        # Boost score for pages with FAQs (very valuable for LLMs)
        if page_data.get('faqs') and len(page_data['faqs']) > 0:
            faq_count = len(page_data['faqs'])
            score += min(0.3, faq_count * 0.02)  # Up to 0.3 bonus for FAQs
            print(f"  ✓ Page has {faq_count} FAQs, boosting importance score by {min(0.3, faq_count * 0.02):.2f}")
        
        # Use AI to determine site characteristics for adaptive scoring
        site_characteristics = self._determine_site_characteristics_with_ai(all_pages[:20])
        
        title_lower = page_data['title'].lower()
        url_lower = page_data['url'].lower()
        
        if site_characteristics.get('is_tech_site') or site_characteristics.get('is_documentation_site'):
            # Technical/documentation site keywords
            tech_keywords = ['api', 'docs', 'documentation', 'guide', 'tutorial', 'getting started', 'quickstart', 'reference', 'sdk', 'cli']
            for keyword in tech_keywords:
                if keyword in title_lower or keyword in url_lower:
                    score += 0.3
                    break
            
            # Development-specific patterns
            if any(word in title_lower for word in ['getting started', 'quickstart', 'introduction']):
                score += 0.2
                
        elif site_characteristics.get('is_news_site'):
            # News site patterns
            if any(word in title_lower for word in ['breaking', 'developing', 'urgent', 'alert', 'live']):
                score += 0.3
            
            # Recency indicators for news
            if any(word in title_lower for word in ['today', 'tonight', 'this morning', 'latest', 'update']):
                score += 0.2
                
            # General news importance
            score += 0.2
            
        elif site_characteristics.get('is_ecommerce_site'):
            # E-commerce site patterns
            if any(word in title_lower for word in ['product', 'buy', 'shop', 'cart', 'checkout']):
                score += 0.2
            
            if any(word in url_lower for word in ['product', 'item', 'shop']):
                score += 0.1
                
        else:
            # General site - look for universal importance indicators
            important_patterns = ['about', 'contact', 'home', 'main', 'overview', 'introduction', 'welcome']
            for pattern in important_patterns:
                if pattern in title_lower or pattern in url_lower:
                    score += 0.2
                    break
        
        return min(score, 1.0)
    
    def categorize_page(self, page_data: Dict) -> str:
        # Simple fallback categorization - will be overridden by AI categorization
        url = page_data['url'].lower()
        title = page_data['title'].lower()
        
        # Basic fallback categories
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
        elif any(word in url or word in title for word in ['about', 'contact']):
            return 'About'
        else:
            return 'General'
    
    def categorize_pages_with_ai(self, pages_data: List[Dict]) -> List[Dict]:
        """Use AI to perform comprehensive analysis and categorization of all pages"""
        if not openai_client or len(pages_data) == 0:
            # Fallback to basic categorization
            for page in pages_data:
                page['section'] = self.categorize_page(page)
            return pages_data
            
        try:
            # Step 1: Analyze the overall site to understand its purpose and structure
            site_analysis = self._analyze_site_structure(pages_data)
            print(f"Site analysis complete: {site_analysis.site_purpose}")
            
            # Step 2: Analyze individual pages in batches
            page_analyses = self._analyze_pages_in_batches(pages_data, site_analysis)
            
            # Step 3: Assign pages to categories based on the site analysis
            category_assignments = self._assign_pages_to_categories(pages_data, site_analysis, page_analyses)
            
            # Step 4: Apply the AI analysis results to the pages
            self._apply_ai_analysis_to_pages(pages_data, page_analyses, category_assignments)
            
            print(f"AI categorization successful - created categories: {set(category_assignments.assignments.values())}")
            return pages_data
                
        except Exception as e:
            print(f"AI categorization failed, using fallback: {e}")
            # Fallback to basic categorization
            for page in pages_data:
                page['section'] = self.categorize_page(page)
            return pages_data
    
    def _analyze_site_structure(self, pages_data: List[Dict]) -> SiteAnalysis:
        """Analyze the overall website structure and purpose"""
        # Prepare site overview for analysis
        site_overview = {
            'domain': urlparse(self.base_url).netloc,
            'total_pages': len(pages_data),
            'sample_titles': [page['title'] for page in pages_data[:10]],
            'sample_urls': [page['url'].replace(self.base_url, '') for page in pages_data[:10]],
            'sample_descriptions': [page['description'][:100] for page in pages_data[:5] if page['description']]
        }
        
        response = openai_client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert web analyst who understands website structures and purposes. Analyze the provided website data to understand its core purpose, audience, and optimal organization structure."
                },
                {
                    "role": "user", 
                    "content": f"""Analyze this website and provide a comprehensive structural analysis:

Domain: {site_overview['domain']}
Total Pages: {site_overview['total_pages']}

Sample Page Titles:
{chr(10).join(f"- {title}" for title in site_overview['sample_titles'])}

Sample URL Paths:
{chr(10).join(f"- {url}" for url in site_overview['sample_urls'])}

Sample Descriptions:
{chr(10).join(f"- {desc}" for desc in site_overview['sample_descriptions'] if desc)}

Based on this data, provide a complete analysis of the website's structure, purpose, and optimal categorization approach."""
                }
            ],
            response_format=SiteAnalysis,
            max_tokens=1000,
            temperature=0.2
        )
        
        return response.choices[0].message.parsed
    
    def _analyze_pages_in_batches(self, pages_data: List[Dict], site_analysis: SiteAnalysis) -> Dict[int, PageAnalysis]:
        """Analyze pages in batches to understand their individual purposes"""
        page_analyses = {}
        batch_size = 8  # Process pages in smaller batches to avoid token limits
        
        for i in range(0, min(len(pages_data), 32), batch_size):  # Limit to first 32 pages
            batch_pages = pages_data[i:i+batch_size]
            batch_data = []
            
            for j, page in enumerate(batch_pages):
                actual_index = i + j
                page_summary = {
                    'index': actual_index,
                    'title': page['title'][:80],
                    'url_path': page['url'].replace(self.base_url, '').strip('/'),
                    'description': page['description'][:150] if page['description'] else '',
                    'content_preview': page['content'][:300] if page['content'] else '',
                    'content_length': page['content_length']
                }
                batch_data.append(page_summary)
            
            try:
                response = openai_client.beta.chat.completions.parse(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": f"""You are analyzing pages from a website whose purpose is: {site_analysis.site_purpose}
                            
Target audience: {site_analysis.target_audience}

Available categories: {', '.join(site_analysis.main_categories)}

Analyze each page individually to understand its specific purpose, content type, and importance within this website's context."""
                        },
                        {
                            "role": "user",
                            "content": f"""Analyze these {len(batch_data)} pages and provide detailed analysis for each:

{json.dumps(batch_data, indent=2)}

For each page, determine its category, content type, importance factors, description, and keywords."""
                        }
                    ],
                    response_format=PageAnalysis,
                    max_tokens=1500,
                    temperature=0.3
                )
                
                # Note: The API returns one PageAnalysis for the batch, but we need individual analyses
                # We'll handle this differently - create individual analyses
                batch_analysis = response.choices[0].message.parsed
                
                # For now, apply the batch analysis to the first page and use fallback for others
                if batch_data:
                    page_analyses[batch_data[0]['index']] = batch_analysis
                    
            except Exception as e:
                print(f"Failed to analyze batch starting at index {i}: {e}")
                continue
        
        return page_analyses
    
    def _assign_pages_to_categories(self, pages_data: List[Dict], site_analysis: SiteAnalysis, page_analyses: Dict[int, PageAnalysis]) -> CategoryAssignment:
        """Assign all pages to the determined categories"""
        # Prepare data for category assignment
        pages_for_assignment = []
        for i, page in enumerate(pages_data[:30]):  # Limit to 30 pages for assignment
            page_info = {
                'index': str(i),
                'title': page['title'][:80],
                'url_path': page['url'].replace(self.base_url, '').strip('/'),
                'description': page['description'][:100] if page['description'] else '',
                'analyzed': i in page_analyses
            }
            if i in page_analyses:
                analysis = page_analyses[i]
                page_info.update({
                    'ai_category': analysis.category,
                    'content_type': analysis.content_type,
                    'keywords': analysis.keywords
                })
            pages_for_assignment.append(page_info)
        
        response = openai_client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are assigning pages to categories for a website.

Site Purpose: {site_analysis.site_purpose}
Available Categories: {', '.join(site_analysis.main_categories)}

Category Descriptions:
{json.dumps(site_analysis.category_descriptions, indent=2)}

Assign each page to the most appropriate category based on its content and purpose."""
                },
                {
                    "role": "user",
                    "content": f"""Assign these pages to categories:

{json.dumps(pages_for_assignment, indent=2)}

Provide assignments for each page index and explain your reasoning."""
                }
            ],
            response_format=CategoryAssignment,
            max_tokens=800,
            temperature=0.2
        )
        
        return response.choices[0].message.parsed
    
    def _apply_ai_analysis_to_pages(self, pages_data: List[Dict], page_analyses: Dict[int, PageAnalysis], category_assignments: CategoryAssignment):
        """Apply AI analysis results to the page data"""
        for i, page in enumerate(pages_data):
            # Apply category assignment
            if str(i) in category_assignments.assignments:
                page['section'] = category_assignments.assignments[str(i)]
            else:
                # Use fallback categorization for pages not analyzed
                page['section'] = self.categorize_page(page)
            
            # Apply individual page analysis if available
            if i in page_analyses:
                analysis = page_analyses[i]
                page['ai_description'] = analysis.description
                page['content_type'] = analysis.content_type
                page['ai_keywords'] = analysis.keywords
                page['importance_factors'] = analysis.importance_factors
    
    async def fetch_sitemap_urls(self, session: aiohttp.ClientSession) -> Set[str]:
        """Fetch all URLs from sitemap.xml or sitemap_index.xml"""
        urls = set()
        
        # Try common sitemap locations
        sitemap_urls = [
            f"{self.base_url.rstrip('/')}/sitemap_index.xml",
            f"{self.base_url.rstrip('/')}/sitemap.xml",
            f"{self.base_url.rstrip('/')}/sitemap-index.xml",
            f"{self.base_url.rstrip('/')}/sitemap1.xml",
        ]
        
        # Also check robots.txt for sitemap location
        try:
            robots_url = f"{self.base_url.rstrip('/')}/robots.txt"
            async with session.get(robots_url, timeout=aiohttp.ClientTimeout(total=10), ssl=self.ssl_context) as response:
                if response.status == 200:
                    robots_content = await response.text()
                    for line in robots_content.split('\n'):
                        if line.lower().startswith('sitemap:'):
                            sitemap_url = line.split(':', 1)[1].strip()
                            sitemap_urls.insert(0, sitemap_url)  # Prioritize robots.txt sitemap
                            print(f"Found sitemap in robots.txt: {sitemap_url}")
        except Exception as e:
            print(f"Could not fetch robots.txt: {e}")
        
        # Try each sitemap URL
        for sitemap_url in sitemap_urls:
            try:
                print(f"Trying sitemap: {sitemap_url}")
                async with session.get(sitemap_url, timeout=aiohttp.ClientTimeout(total=15), ssl=self.ssl_context) as response:
                    if response.status == 200:
                        content = await response.text()
                        sitemap_urls_found = await self._parse_sitemap(content, session)
                        urls.update(sitemap_urls_found)
                        if sitemap_urls_found:
                            print(f"✓ Found {len(sitemap_urls_found)} URLs in {sitemap_url}")
                            break  # Stop after first successful sitemap
            except Exception as e:
                print(f"Could not fetch {sitemap_url}: {e}")
                continue
        
        return urls
    
    async def _parse_sitemap(self, content: str, session: aiohttp.ClientSession) -> Set[str]:
        """Parse sitemap XML and extract URLs, handling both sitemap and sitemap_index"""
        urls = set()
        
        try:
            root = ET.fromstring(content)
            
            # Handle namespace
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            # Check if this is a sitemap index
            sitemap_elements = root.findall('.//ns:sitemap/ns:loc', namespace)
            if sitemap_elements:
                print(f"Found sitemap index with {len(sitemap_elements)} sub-sitemaps")
                # This is a sitemap index, fetch each sub-sitemap
                for sitemap_elem in sitemap_elements:
                    sub_sitemap_url = sitemap_elem.text
                    try:
                        async with session.get(sub_sitemap_url, timeout=aiohttp.ClientTimeout(total=15), ssl=self.ssl_context) as response:
                            if response.status == 200:
                                sub_content = await response.text()
                                sub_urls = await self._parse_sitemap(sub_content, session)
                                urls.update(sub_urls)
                                print(f"  ✓ Parsed sub-sitemap: {sub_sitemap_url} ({len(sub_urls)} URLs)")
                    except Exception as e:
                        print(f"  ✗ Could not fetch sub-sitemap {sub_sitemap_url}: {e}")
            else:
                # This is a regular sitemap, extract URLs
                url_elements = root.findall('.//ns:url/ns:loc', namespace)
                for url_elem in url_elements:
                    url = url_elem.text
                    if url and urlparse(url).netloc == self.domain:
                        urls.add(url)
                
                # Also try without namespace (some sitemaps don't use it)
                if not urls:
                    for url_elem in root.findall('.//url/loc'):
                        url = url_elem.text
                        if url and urlparse(url).netloc == self.domain:
                            urls.add(url)
        
        except ET.ParseError as e:
            print(f"XML parse error: {e}")
        except Exception as e:
            print(f"Error parsing sitemap: {e}")
        
        return urls
    
    async def crawl(self) -> List[Dict]:
        # Create connector with SSL context
        connector = aiohttp.TCPConnector(ssl=self.ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            # Try to fetch URLs from sitemap first
            sitemap_urls = await self.fetch_sitemap_urls(session)
            
            if sitemap_urls:
                print(f"🗺️  Using sitemap with {len(sitemap_urls)} URLs")
                # Use sitemap URLs as the primary source
                urls_to_crawl = list(sitemap_urls)
                
                # Limit URLs if not crawling all
                if not self.crawl_all and len(urls_to_crawl) > self.max_pages:
                    print(f"Limiting to {self.max_pages} pages from sitemap")
                    urls_to_crawl = urls_to_crawl[:self.max_pages]
                
                # Fetch each URL from sitemap
                for url in urls_to_crawl:
                    if url in self.visited_urls:
                        continue
                    
                    self.visited_urls.add(url)
                    page_data = await self.fetch_page(session, url)
                    
                    if page_data:
                        self.pages_data.append(page_data)
                        print(f"Crawled {len(self.pages_data)}/{len(urls_to_crawl)} pages: {url}")
            else:
                # Fallback to traditional link-based crawling
                print("⚠️  No sitemap found, using traditional link-based crawling")
                queue = [(self.base_url, 0)]  # (url, depth)
                
                while queue and len(self.visited_urls) < self.max_pages:
                    url, depth = queue.pop(0)
                    
                    # Skip if already visited
                    if url in self.visited_urls:
                        continue
                    
                    # Only apply depth limit if not crawling all
                    if not self.crawl_all and depth > self.depth_limit:
                        continue
                    
                    self.visited_urls.add(url)
                    page_data = await self.fetch_page(session, url)
                    
                    if page_data:
                        self.pages_data.append(page_data)
                        print(f"Crawled {len(self.pages_data)}/{self.max_pages if not self.crawl_all else '∞'} pages: {url}")
                        
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
        
        # Use AI to determine site characteristics and handle subscription content intelligently
        if self.pages_data:
            site_characteristics = self._determine_site_characteristics_with_ai(self.pages_data[:10])
            
            # For sites with subscription content, limit subscription pages to avoid repetition
            if site_characteristics.get('has_subscription_content', False):
                subscription_pages = [p for p in self.pages_data if 'subscription' in p['url'].lower()]
                other_pages = [p for p in self.pages_data if 'subscription' not in p['url'].lower()]
                
                # Keep only the main subscription page
                if subscription_pages:
                    main_subscription = min(subscription_pages, key=lambda x: len(x['url']))
                    self.pages_data = other_pages + [main_subscription]
                    print(f"AI detected subscription content - kept {len(other_pages)} main pages + 1 subscription page")
        
        # Calculate importance scores
        for page in self.pages_data:
            page['importance_score'] = self.calculate_importance_score(page, self.pages_data)
        
        # Use AI to categorize pages
        self.pages_data = self.categorize_pages_with_ai(self.pages_data)
        
        return self.pages_data
    
    async def check_existing_llms_txt(self, base_url: str) -> Optional[str]:
        """Check if the website already has an llms.txt file"""
        try:
            # Try common locations for llms.txt
            possible_urls = [
                f"{base_url.rstrip('/')}/llms.txt",
                f"{base_url.rstrip('/')}/.well-known/llms.txt",
            ]
            
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            
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
                            ssl=self.ssl_context
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

    def _determine_site_characteristics_with_ai(self, sample_pages: List[Dict]) -> Dict[str, any]:
        """Use AI to determine website characteristics instead of hardcoded rules"""
        if not openai_client or len(sample_pages) == 0:
            return self._fallback_site_characteristics()
        
        # Use cached result if available
        if self._site_characteristics is not None:
            return self._site_characteristics
            
        try:
            # Prepare sample data for AI analysis
            site_data = {
                'domain': self.domain,
                'base_url': self.base_url,
                'sample_titles': [page['title'] for page in sample_pages[:10]],
                'sample_urls': [page['url'].replace(self.base_url, '') for page in sample_pages[:10]],
                'sample_descriptions': [page['description'][:100] for page in sample_pages[:5] if page['description']]
            }
            
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert web analyst who can determine website characteristics. Analyze the provided website data and return a JSON object with website characteristics."
                    },
                    {
                        "role": "user",
                        "content": f"""Analyze this website and determine its characteristics:

Domain: {site_data['domain']}
Base URL: {site_data['base_url']}

Sample Page Titles:
{chr(10).join(f"- {title}" for title in site_data['sample_titles'])}

Sample URL Paths:
{chr(10).join(f"- {url}" for url in site_data['sample_urls'])}

Sample Descriptions:
{chr(10).join(f"- {desc}" for desc in site_data['sample_descriptions'] if desc)}

Return a JSON object with these characteristics:
{{
  "is_news_site": boolean,
  "is_tech_site": boolean, 
  "is_documentation_site": boolean,
  "is_ecommerce_site": boolean,
  "primary_content_type": "news|documentation|marketing|ecommerce|blog|corporate|other",
  "has_subscription_content": boolean,
  "content_patterns": ["list", "of", "identified", "patterns"],
  "site_purpose": "brief description of main purpose"
}}

Base your analysis on the URL patterns, titles, and overall content structure."""
                    }
                ],
                max_tokens=500,
                temperature=0.1,
                timeout=10
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if '{' in result_text:
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                characteristics = json.loads(result_text[json_start:json_end])
                
                # Cache the result
                self._site_characteristics = characteristics
                print(f"AI determined site characteristics: {characteristics}")
                return characteristics
                
        except Exception as e:
            print(f"AI site characteristic analysis failed: {e}")
            
        # Fallback to heuristic analysis
        return self._fallback_site_characteristics()
    
    def _fallback_site_characteristics(self) -> Dict[str, any]:
        """Fallback method for determining site characteristics without AI"""
        domain_lower = self.domain.lower()
        
        # Basic heuristic detection
        is_news = any(word in domain_lower for word in ['news', 'times', 'post', 'cnn', 'bbc', 'fox', 'abc', 'cbs', 'nbc', 'reuters', 'ap'])
        is_tech = any(word in domain_lower for word in ['docs', 'api', 'dev', 'github', 'stackoverflow', 'tech'])
        is_docs = any(word in domain_lower for word in ['docs', 'documentation', 'wiki', 'help'])
        is_ecommerce = any(word in domain_lower for word in ['shop', 'store', 'buy', 'cart', 'amazon', 'ebay'])
        
        characteristics = {
            'is_news_site': is_news,
            'is_tech_site': is_tech,
            'is_documentation_site': is_docs,
            'is_ecommerce_site': is_ecommerce,
            'primary_content_type': 'news' if is_news else 'documentation' if is_docs else 'marketing' if is_ecommerce else 'other',
            'has_subscription_content': is_news,  # News sites often have subscriptions
            'content_patterns': [],
            'site_purpose': f"Website focused on {is_news and 'news' or is_docs and 'documentation' or 'general content'}"
        }
        
        self._site_characteristics = characteristics
        return characteristics

class LLMSTxtGenerator:
    def __init__(self, base_url: str, pages_data: List[Dict]):
        self.base_url = base_url
        self.pages_data = sorted(pages_data, key=lambda x: x['importance_score'], reverse=True)
        self.site_name = urlparse(base_url).netloc.replace('www.', '').replace('.com', '').replace('.org', '').title()
        
        # Try to extract site analysis if available from pages
        self.site_analysis = None
        for page in pages_data:
            if hasattr(page, 'site_analysis'):
                self.site_analysis = page.site_analysis
                break
    
    def cleanup_with_openai(self, content: str, content_type: str = "summary") -> str:
        """Clean up content using OpenAI to improve readability and structure"""
        # Return original content if OpenAI client is not available
        if not openai_client:
            print("OpenAI client not available - returning original content")
            return content
            
        try:
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
    
    def reorganize_sections_with_ai(self, sections: Dict) -> Dict:
        """Use AI to make minor refinements to sections if needed"""
        # Since we're already using AI for initial categorization,
        # we can skip additional reorganization for most cases
        if not openai_client or len(sections) <= 3:
            return sections
            
        # Only do reorganization if there are many small sections that could be merged
        small_sections = [name for name, pages in sections.items() if len(pages) <= 2]
        if len(small_sections) < 3:
            return sections
            
        try:
            # Look for opportunities to merge small, related sections
            section_summary = ""
            for section_name, pages in sections.items():
                if len(pages) <= 2:  # Only include small sections for potential merging
                    page_titles = [page['title'] for page in pages]
                    section_summary += f"- {section_name} ({len(pages)} pages): {', '.join(page_titles)}\n"
            
            if not section_summary.strip():
                return sections
            
            prompt = f"""Look at these small content sections and suggest if any should be merged into more meaningful categories. Only suggest merges if they make logical sense.

Small sections:
{section_summary}

Return ONLY a JSON mapping for sections that should be merged. For example:
{{"old_section1": "new_merged_name", "old_section2": "new_merged_name"}}

If no merging is needed, return empty JSON: {{}}"""

            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at organizing content. Only suggest merging sections if it creates a more logical, intuitive organization."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1,
                timeout=10
            )
            
            mapping_text = response.choices[0].message.content.strip()
            if '{' in mapping_text:
                json_start = mapping_text.find('{')
                json_end = mapping_text.rfind('}') + 1
                mapping = json.loads(mapping_text[json_start:json_end])
                
                if mapping:  # Only apply if there are actual mappings
                    new_sections = {}
                    for old_name, pages in sections.items():
                        new_name = mapping.get(old_name, old_name)
                        if new_name in new_sections:
                            new_sections[new_name].extend(pages)
                        else:
                            new_sections[new_name] = pages
                    
                    print(f"AI section refinement: merged {len(mapping)} sections")
                    return new_sections
                
        except Exception as e:
            print(f"AI section refinement failed: {e}")
            
        return sections
    
    def generate_summary(self) -> str:
        # Try to use AI analysis data if available
        if hasattr(self, 'site_analysis') and self.site_analysis:
            return self.site_analysis.site_summary
        
        # Check if pages have AI analysis data
        ai_analyzed_pages = [p for p in self.pages_data if 'content_type' in p or 'ai_keywords' in p]
        if ai_analyzed_pages and openai_client:
            return self._generate_ai_summary_from_pages(ai_analyzed_pages)
        
        # Fallback to original logic
        top_pages = self.pages_data[:3]
        if not top_pages:
            summary = "A website providing information and resources."
        else:
            keywords = []
            for page in top_pages:
                # Use AI keywords if available, otherwise extract from title
                if 'ai_keywords' in page and page['ai_keywords']:
                    keywords.extend(page['ai_keywords'])
                else:
                    title_words = page['title'].lower().split()
                    keywords.extend([word for word in title_words if len(word) > 3])
            
            # Get most common meaningful words
            from collections import Counter
            common_words = Counter(keywords).most_common(3)
            if common_words:
                summary = f"A platform providing {', '.join([word[0] for word in common_words])} and related resources."
            else:
                summary = "A website providing information and resources."
        
        # Clean up the summary with OpenAI if available
        if openai_client:
            return self.cleanup_with_openai(summary, "summary")
        return summary
    
    def _generate_ai_summary_from_pages(self, pages: List[Dict]) -> str:
        """Generate summary using AI analysis of pages"""
        try:
            # Gather AI analysis data
            content_types = [p.get('content_type', 'other') for p in pages[:10]]
            all_keywords = []
            for page in pages[:10]:
                if 'ai_keywords' in page and page['ai_keywords']:
                    all_keywords.extend(page['ai_keywords'])
            
            # Get most common content types and keywords
            from collections import Counter
            type_counts = Counter(content_types)
            keyword_counts = Counter(all_keywords)
            
            analysis_data = {
                'domain': urlparse(self.base_url).netloc,
                'main_content_types': type_counts.most_common(3),
                'main_keywords': keyword_counts.most_common(5),
                'total_pages': len(self.pages_data),
                'sample_titles': [p['title'] for p in pages[:5]]
            }
            
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating concise, informative website summaries. Create a 2-3 sentence summary that clearly explains what the website offers."
                    },
                    {
                        "role": "user",
                        "content": f"""Create a summary for this website based on the analysis data:

{json.dumps(analysis_data, indent=2)}

The summary should be 2-3 sentences, explain the website's primary purpose, and be useful for someone trying to understand what the site offers."""
                    }
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"AI summary generation failed: {e}")
            return "A website providing information and resources."
    
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
        
        # Use AI to reorganize sections based on actual content
        sections = self.reorganize_sections_with_ai(sections)
        
        # Dynamic section ordering based on content quality and importance
        section_priority = []
        for section_name, pages in sections.items():
            # Calculate section priority based on average importance score and page count
            avg_importance = sum(page['importance_score'] for page in pages) / len(pages) if pages else 0
            important_page_count = len([p for p in pages if p['importance_score'] > 0.3])
            
            # Priority score: weighted combination of average importance and important page count
            priority_score = (avg_importance * 0.7) + (min(important_page_count / 10, 1.0) * 0.3)
            section_priority.append((section_name, priority_score, important_page_count))
        
        # Sort sections by priority score (highest first), then by important page count
        section_priority.sort(key=lambda x: (x[1], x[2]), reverse=True)
        section_order = [name for name, _, _ in section_priority]
        
        for section_name in section_order:
            if section_name in sections:
                pages = sorted(sections[section_name], key=lambda x: x['importance_score'], reverse=True)
                
                # Include all pages, but prioritize by importance score
                # Lower threshold for large crawls to include more content
                total_pages = len(self.pages_data)
                
                if total_pages > 200:
                    # For very large crawls, include pages with score > 0.1
                    important_pages = [p for p in pages if p['importance_score'] > 0.1]
                elif total_pages > 100:
                    # For large crawls, include pages with score > 0.15
                    important_pages = [p for p in pages if p['importance_score'] > 0.15]
                elif total_pages > 50:
                    # For medium-large crawls, include pages with score > 0.2
                    important_pages = [p for p in pages if p['importance_score'] > 0.2]
                else:
                    # For smaller crawls, use original threshold
                    important_pages = [p for p in pages if p['importance_score'] > 0.3]
                
                if not important_pages:
                    continue
                
                # Don't limit pages per section - include all important pages
                # AI processing will be disabled for large crawls anyway
                
                # Create clean section with simple format
                section_content = f"## {section_name}\n\n"
                
                for page in important_pages:
                    title = page['title']
                    url = page['url']
                    description = page['description']
                    
                    # Use AI-generated description if available, otherwise use intelligent fallback
                    final_description = self._generate_page_description(page)
                    
                    # Add FAQ indicator if page has FAQs
                    faq_indicator = ""
                    if page.get('faqs') and len(page['faqs']) > 0:
                        faq_indicator = f" [📋 {len(page['faqs'])} FAQs]"
                    
                    section_content += f"- [{title}]({url}): {final_description}{faq_indicator}\n"
                
                section_content += "\n"
                
                # Use AI to clean up the section format and descriptions, but be selective
                should_use_ai = True
                total_pages = len(self.pages_data)
                
                # Skip AI for less important sections if there are many pages
                if total_pages > 100:
                    # For very large crawls, skip AI enhancement entirely to avoid timeouts
                    should_use_ai = False
                elif total_pages > 50:
                    # Only use AI for the most important sections
                    priority_sections = ['Getting Started', 'Documentation', 'API Reference', 'News', 'Politics', 'Products', 'Services']
                    should_use_ai = section_name in priority_sections
                
                if should_use_ai:
                    cleaned_section = self.cleanup_with_openai(section_content, "section")
                    # Ensure proper spacing after AI cleanup
                    if not cleaned_section.endswith('\n\n'):
                        if cleaned_section.endswith('\n'):
                            cleaned_section += '\n'
                        else:
                            cleaned_section += '\n\n'
                    content += cleaned_section
                else:
                    content += section_content
        
        # Add section for additional pages that didn't make it into main sections
        # Only for smaller crawls where this makes sense
        if total_pages <= 100:
            optional_pages = [p for p in self.pages_data if p['importance_score'] <= 0.3 and p['importance_score'] > 0.1]
            if optional_pages:
                content += "## Additional Resources\n\n"
                for page in optional_pages[:10]:  # Include more optional pages
                    title = page['title']
                    url = page['url']
                    description = page.get('description', '')[:100] if page.get('description') else ''
                    if description:
                        content += f"- [{title}]({url}): {description}\n"
                    else:
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
            
            # Include FAQs if available
            if page.get('faqs') and len(page['faqs']) > 0:
                content += f"### FAQs ({len(page['faqs'])} questions)\n\n"
                for faq in page['faqs']:
                    content += f"**Q: {faq['question']}**\n\n"
                    content += f"A: {faq['answer']}\n\n"
                content += "\n"
            
            # Truncate very long content
            page_content = page['content'][:2000]
            if len(page['content']) > 2000:
                page_content += "... [content truncated]"
            
            content += f"{page_content}\n\n"
            content += "---\n\n"
        
        return content

    def _generate_page_description(self, page: Dict) -> str:
        """Generate an intelligent description for a page using AI analysis or smart fallbacks"""
        
        # First, try to use AI-generated description if available
        if 'ai_description' in page and page['ai_description']:
            return page['ai_description']
        
        # If we have AI analysis data, use it to create a better description
        if 'content_type' in page and 'ai_keywords' in page:
            return self._create_description_from_ai_data(page)
        
        # Use existing description if it's good quality
        if page['description'] and len(page['description'].strip()) > 20:
            return self._clean_existing_description(page['description'])
        
        # Generate description using AI if available
        if openai_client:
            return self._generate_description_with_ai(page)
        
        # Final fallback: create a basic description
        return self._create_basic_description(page)
    
    def _create_description_from_ai_data(self, page: Dict) -> str:
        """Create description using available AI analysis data"""
        content_type = page.get('content_type', 'other')
        keywords = page.get('ai_keywords', [])
        title = page['title']
        
        # Use content type and keywords to create a meaningful description
        if content_type == 'documentation':
            if keywords:
                return f"Documentation covering {', '.join(keywords[:3])} and related topics."
            return f"Comprehensive documentation for {title.lower()}."
        elif content_type == 'tutorial':
            if keywords:
                return f"Step-by-step tutorial guide for {', '.join(keywords[:2])}."
            return f"Tutorial and learning guide for {title.lower()}."
        elif content_type == 'reference':
            if keywords:
                return f"Technical reference for {', '.join(keywords[:3])}."
            return f"Reference documentation and technical details."
        elif content_type == 'news':
            return f"News article covering {', '.join(keywords[:2])} and current events." if keywords else "Latest news and updates."
        elif content_type == 'support':
            return f"Support information and help resources for {', '.join(keywords[:2])}." if keywords else "Help and support resources."
        elif content_type == 'legal':
            return f"Legal documentation regarding {', '.join(keywords[:2])}." if keywords else "Legal terms and policy information."
        else:
            if keywords:
                return f"Information about {', '.join(keywords[:3])}."
            return f"Details about {title.lower()}."
    
    def _clean_existing_description(self, description: str) -> str:
        """Clean and improve existing description"""
        clean_desc = description.strip()
        
        # Remove common prefixes and suffixes
        prefixes = ["Learn more about", "Documentation for", "Information about", "Details on"]
        for prefix in prefixes:
            if clean_desc.startswith(prefix):
                clean_desc = clean_desc[len(prefix):].strip()
        
        # Smart truncation - prefer complete sentences
        if len(clean_desc) > 150:
            sentences = clean_desc.split('. ')
            if len(sentences) > 1 and len(sentences[0]) < 120:
                clean_desc = sentences[0]
                if not clean_desc.endswith('.'):
                    clean_desc += '.'
            else:
                words = clean_desc[:140].split(' ')
                clean_desc = ' '.join(words[:-1])
                if not clean_desc.endswith('.'):
                    clean_desc += '.'
        
        # Ensure proper capitalization and punctuation
        if clean_desc:
            clean_desc = clean_desc[0].upper() + clean_desc[1:]
            if not clean_desc.endswith(('.', '!', '?')):
                clean_desc += '.'
        
        return clean_desc
    
    def _generate_description_with_ai(self, page: Dict) -> str:
        """Generate description using AI for pages without existing analysis"""
        if not openai_client:
            return self._create_basic_description(page)
        
        try:
            page_data = {
                'title': page['title'][:80],
                'url_path': page['url'].replace(self.base_url, '').strip('/'),
                'description': page['description'][:150] if page['description'] else '',
                'content_preview': page['content'][:400] if page['content'] else '',
                'content_length': page['content_length']
            }
            
            response = openai_client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating concise, informative descriptions for web pages. Create clear, useful descriptions that help users understand what each page offers."
                    },
                    {
                        "role": "user",
                        "content": f"""Create a brief, informative description for this web page:

{json.dumps(page_data, indent=2)}

The description should be 1-2 sentences, clearly explain what the page offers, and be useful for someone trying to understand the page's purpose."""
                    }
                ],
                response_format=PageAnalysis,
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.parsed.description
            
        except Exception as e:
            print(f"AI description generation failed for {page['title']}: {e}")
            return self._create_basic_description(page)
    
    def _create_basic_description(self, page: Dict) -> str:
        """Create a basic description as final fallback"""
        title = page['title']
        url = page['url']
        
        # Try to extract useful info from URL path
        url_path = url.replace(self.base_url, '').strip('/').lower()
        
        # Look for meaningful patterns in title and URL
        if any(word in title.lower() for word in ['getting started', 'quickstart', 'setup']):
            return "Getting started guide and initial setup information."
        elif any(word in title.lower() for word in ['api', 'reference']):
            return "API documentation and technical reference."
        elif any(word in title.lower() for word in ['tutorial', 'guide', 'how to']):
            return "Tutorial and step-by-step guidance."
        elif any(word in title.lower() for word in ['faq', 'help', 'support']):
            return "Help documentation and support resources."
        elif any(word in url_path for word in ['about', 'contact']):
            return "Information about the organization and contact details."
        elif any(word in url_path for word in ['pricing', 'plans']):
            return "Pricing information and service plans."
        else:
            # Extract meaningful content from page if available
            if page['content'] and len(page['content']) > 100:
                # Get first meaningful sentence
                sentences = page['content'].split('.')[:3]
                for sentence in sentences:
                    sentence = sentence.strip()
                    if len(sentence) > 30 and not sentence.startswith(('©', 'Copyright', 'All rights')):
                        if len(sentence) > 140:
                            words = sentence[:130].split(' ')
                            sentence = ' '.join(words[:-1]) + '.'
                        return sentence
            
            return f"Information and resources about {title.lower()}."

@app.get("/")
async def root():
    return {"message": "LLMs.txt Generator API", "docs": "/docs"}

@app.post("/generate", response_model=LLMSTxtResponse)
async def generate_llms_txt(request: CrawlRequest):
    start_time = time.time()
    
    try:
        # Initialize crawler for checking existing llms.txt
        crawler = WebsiteCrawler(str(request.url))
        
        # First, check if the website already has an llms.txt file
        existing_llms_txt = await crawler.check_existing_llms_txt(str(request.url))
        if existing_llms_txt:
            pages_info = [PageInfo(
                url=f"{str(request.url).rstrip('/')}/llms.txt",
                title='Existing llms.txt',
                description='Found existing llms.txt file on the website',
                content_length=len(existing_llms_txt),
                importance_score=1.0,
                section='Existing Documentation'
            )]
            
            return LLMSTxtResponse(
                llms_txt=existing_llms_txt,
                llms_full_txt=existing_llms_txt,
                pages_analyzed=pages_info,
                generation_time=time.time() - start_time,
                ai_enhanced=False,
                ai_model=None,
                used_existing=True
            )
        
        # Crawl the website
        crawler = WebsiteCrawler(
            str(request.url), 
            max_pages=request.max_pages,
            depth_limit=request.depth_limit,
            crawl_all=request.crawl_all
        )
        
        pages_data = await crawler.crawl()
        
        if not pages_data:
            raise HTTPException(status_code=400, detail="Could not crawl any pages from the provided URL")
        
        # Generate llms.txt files
        generator = LLMSTxtGenerator(str(request.url), pages_data)
        
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
        
        # Determine if AI enhancement was actually used
        ai_enhanced = openai_client is not None
        ai_model = 'gpt-4o-mini' if ai_enhanced else None
        
        # Get site characteristics for debugging/verification
        site_characteristics = None
        if crawler._site_characteristics:
            site_characteristics = crawler._site_characteristics
        
        return LLMSTxtResponse(
            llms_txt=llms_txt,
            llms_full_txt=llms_full_txt,
            pages_analyzed=pages_info,
            generation_time=generation_time,
            ai_enhanced=ai_enhanced,
            ai_model=ai_model,
            used_existing=False,
            site_characteristics=site_characteristics
        )
        
    except Exception as e:
        # Log the full error for debugging
        import traceback
        print(f"ERROR in generate_llms_txt: {type(e).__name__}: {str(e)}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        
        # Provide a more informative error message
        error_message = str(e) if str(e) else f"{type(e).__name__} occurred"
        raise HTTPException(status_code=500, detail=f"Error generating llms.txt: {error_message}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 