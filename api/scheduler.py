from http.server import BaseHTTPRequestHandler
import json
import asyncio
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from .generate import WebsiteCrawler, LLMSTxtGenerator

# In-memory storage for demo (in production, use a database)
MONITORED_SITES = {}
UPDATE_HISTORY = {}

class ChangeDetector:
    def __init__(self):
        pass
    
    def calculate_structure_hash(self, pages_data: List[Dict]) -> str:
        """Calculate a hash representing the website's structure"""
        # Create a signature based on URLs, titles, and section distribution
        structure_signature = ""
        
        # Sort pages by URL for consistent hashing
        sorted_pages = sorted(pages_data, key=lambda x: x['url'])
        
        for page in sorted_pages:
            # Include URL, title, and section in the signature
            structure_signature += f"{page['url']}|{page['title']}|{page['section']}\n"
        
        # Also include section distribution (how many pages in each section)
        sections = {}
        for page in pages_data:
            section = page['section']
            sections[section] = sections.get(section, 0) + 1
        
        section_dist = "|".join([f"{k}:{v}" for k, v in sorted(sections.items())])
        structure_signature += f"SECTIONS:{section_dist}"
        
        return hashlib.md5(structure_signature.encode()).hexdigest()
    
    def detect_changes(self, old_hash: str, new_hash: str, old_pages: List[Dict], new_pages: List[Dict]) -> Dict:
        """Detect what changed between two crawls"""
        changes = {
            'structure_changed': old_hash != new_hash,
            'new_pages': [],
            'removed_pages': [],
            'modified_pages': [],
            'section_changes': {},
            'severity': 'none'
        }
        
        if not changes['structure_changed']:
            return changes
        
        # Compare pages
        old_urls = {page['url']: page for page in old_pages}
        new_urls = {page['url']: page for page in new_pages}
        
        # Find new and removed pages
        changes['new_pages'] = [url for url in new_urls if url not in old_urls]
        changes['removed_pages'] = [url for url in old_urls if url not in new_urls]
        
        # Find modified pages (title or section changes)
        for url in set(old_urls.keys()) & set(new_urls.keys()):
            old_page = old_urls[url]
            new_page = new_urls[url]
            
            if old_page['title'] != new_page['title'] or old_page['section'] != new_page['section']:
                changes['modified_pages'].append({
                    'url': url,
                    'old_title': old_page['title'],
                    'new_title': new_page['title'],
                    'old_section': old_page['section'],
                    'new_section': new_page['section']
                })
        
        # Calculate severity
        total_changes = len(changes['new_pages']) + len(changes['removed_pages']) + len(changes['modified_pages'])
        total_pages = len(old_pages)
        
        if total_pages == 0:
            change_percentage = 100
        else:
            change_percentage = (total_changes / total_pages) * 100
        
        if change_percentage >= 50:
            changes['severity'] = 'major'
        elif change_percentage >= 20:
            changes['severity'] = 'moderate'
        elif change_percentage >= 5:
            changes['severity'] = 'minor'
        else:
            changes['severity'] = 'minimal'
        
        return changes

class AutoUpdater:
    def __init__(self):
        self.change_detector = ChangeDetector()
    
    async def check_site_for_updates(self, site_config: Dict) -> Dict:
        """Check a single site for updates"""
        url = site_config['url']
        last_hash = site_config.get('last_hash')
        last_check = site_config.get('last_check', 0)
        
        print(f"Checking {url} for updates...")
        
        try:
            # Crawl the website
            crawler = WebsiteCrawler(url, site_config.get('max_pages', 20))
            pages_data = await crawler.crawl()
            
            if not pages_data:
                return {
                    'url': url,
                    'status': 'error',
                    'message': 'Failed to crawl website',
                    'timestamp': time.time()
                }
            
            # Calculate new structure hash
            new_hash = self.change_detector.calculate_structure_hash(pages_data)
            
            result = {
                'url': url,
                'status': 'checked',
                'timestamp': time.time(),
                'pages_count': len(pages_data),
                'new_hash': new_hash,
                'changes': None,
                'updated': False
            }
            
            # Check for changes
            if last_hash and last_hash != new_hash:
                old_pages = site_config.get('last_pages', [])
                changes = self.change_detector.detect_changes(last_hash, new_hash, old_pages, pages_data)
                result['changes'] = changes
                
                # Decide whether to regenerate based on severity
                should_update = changes['severity'] in ['major', 'moderate', 'minor']
                
                if should_update:
                    # Regenerate llms.txt
                    generator = LLMSTxtGenerator(url, pages_data)
                    new_llms_txt = generator.generate_llms_txt()
                    
                    result.update({
                        'updated': True,
                        'new_llms_txt': new_llms_txt,
                        'update_reason': f"Website structure changed ({changes['severity']} changes detected)"
                    })
                    
                    # Update stored data
                    MONITORED_SITES[url].update({
                        'last_hash': new_hash,
                        'last_pages': pages_data,
                        'last_update': time.time(),
                        'llms_txt': new_llms_txt
                    })
                    
                    print(f"Updated {url} - {changes['severity']} changes detected")
                else:
                    print(f"Changes detected in {url} but not significant enough to update")
            
            elif not last_hash:
                # First time checking this site
                generator = LLMSTxtGenerator(url, pages_data)
                new_llms_txt = generator.generate_llms_txt()
                
                MONITORED_SITES[url] = {
                    'url': url,
                    'last_hash': new_hash,
                    'last_pages': pages_data,
                    'last_check': time.time(),
                    'last_update': time.time(),
                    'llms_txt': new_llms_txt,
                    'max_pages': site_config.get('max_pages', 20),
                    'check_interval': site_config.get('check_interval', 86400)  # 24 hours default
                }
                
                result.update({
                    'updated': True,
                    'new_llms_txt': new_llms_txt,
                    'update_reason': 'Initial setup for monitoring'
                })
            
            else:
                print(f"No changes detected in {url}")
            
            # Update last check time
            if url in MONITORED_SITES:
                MONITORED_SITES[url]['last_check'] = time.time()
            
            return result
            
        except Exception as e:
            return {
                'url': url,
                'status': 'error',
                'message': str(e),
                'timestamp': time.time()
            }
    
    async def check_all_monitored_sites(self) -> List[Dict]:
        """Check all monitored sites for updates"""
        results = []
        current_time = time.time()
        
        for url, config in MONITORED_SITES.items():
            last_check = config.get('last_check', 0)
            check_interval = config.get('check_interval', 86400)  # 24 hours
            
            # Check if it's time to check this site
            if current_time - last_check >= check_interval:
                result = await self.check_site_for_updates(config)
                results.append(result)
            else:
                next_check = last_check + check_interval
                results.append({
                    'url': url,
                    'status': 'skipped',
                    'message': f'Next check scheduled for {datetime.fromtimestamp(next_check)}',
                    'timestamp': current_time
                })
        
        return results

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                error_response = json.dumps({'error': 'No request body provided'})
                self.wfile.write(error_response.encode())
                return
            
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            action = request_data.get('action')
            
            if action == 'add_site':
                # Add a site to monitoring
                url = request_data.get('url')
                max_pages = request_data.get('max_pages', 20)
                check_interval = request_data.get('check_interval', 86400)  # 24 hours
                
                if not url:
                    error_response = json.dumps({'error': 'URL is required'})
                    self.wfile.write(error_response.encode())
                    return
                
                result = asyncio.run(self.add_site_to_monitoring(url, max_pages, check_interval))
                
            elif action == 'check_updates':
                # Check for updates manually
                url = request_data.get('url')
                if url:
                    # Check specific site
                    if url in MONITORED_SITES:
                        result = asyncio.run(AutoUpdater().check_site_for_updates(MONITORED_SITES[url]))
                    else:
                        result = {'error': f'Site {url} is not being monitored'}
                else:
                    # Check all sites
                    results = asyncio.run(AutoUpdater().check_all_monitored_sites())
                    result = {'checked_sites': results, 'total_sites': len(MONITORED_SITES)}
            
            elif action == 'list_sites':
                # List all monitored sites
                sites_info = []
                for url, config in MONITORED_SITES.items():
                    sites_info.append({
                        'url': url,
                        'last_check': datetime.fromtimestamp(config.get('last_check', 0)).isoformat(),
                        'last_update': datetime.fromtimestamp(config.get('last_update', 0)).isoformat(),
                        'check_interval_hours': config.get('check_interval', 86400) / 3600,
                        'max_pages': config.get('max_pages', 20)
                    })
                result = {'monitored_sites': sites_info}
            
            elif action == 'get_llms_txt':
                # Get current llms.txt for a site
                url = request_data.get('url')
                if url in MONITORED_SITES:
                    result = {
                        'url': url,
                        'llms_txt': MONITORED_SITES[url].get('llms_txt', ''),
                        'last_update': MONITORED_SITES[url].get('last_update', 0)
                    }
                else:
                    result = {'error': f'Site {url} is not being monitored'}
            
            else:
                result = {'error': 'Invalid action. Use: add_site, check_updates, list_sites, or get_llms_txt'}
            
            response_json = json.dumps(result, ensure_ascii=False)
            self.wfile.write(response_json.encode('utf-8'))
            
        except Exception as e:
            self._send_error_response(500, f'Error in scheduler: {str(e)}')
    
    def _send_error_response(self, status_code: int, error_message: str):
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
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    async def add_site_to_monitoring(self, url: str, max_pages: int, check_interval: int):
        """Add a site to the monitoring system"""
        updater = AutoUpdater()
        
        site_config = {
            'url': url,
            'max_pages': max_pages,
            'check_interval': check_interval
        }
        
        result = await updater.check_site_for_updates(site_config)
        
        if result['status'] != 'error':
            return {
                'message': f'Site {url} added to monitoring',
                'check_interval_hours': check_interval / 3600,
                'initial_result': result
            }
        else:
            return result 