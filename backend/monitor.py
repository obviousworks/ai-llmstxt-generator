import asyncio
import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

import aiohttp
from main import WebsiteCrawler, LLMSTxtGenerator

class WebsiteMonitor:
    def __init__(self, storage_path: str = "monitor_data.json"):
        self.storage_path = Path(storage_path)
        self.monitored_sites = self.load_data()
    
    def load_data(self) -> Dict:
        """Load monitoring data from storage"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading data: {e}")
        return {}
    
    def save_data(self):
        """Save monitoring data to storage"""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.monitored_sites, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def add_site(self, url: str, check_interval_hours: int = 24):
        """Add a site to monitoring"""
        self.monitored_sites[url] = {
            'url': url,
            'check_interval_hours': check_interval_hours,
            'last_check': None,
            'last_hash': None,
            'last_generated': None,
            'change_detected': False
        }
        self.save_data()
    
    def remove_site(self, url: str):
        """Remove a site from monitoring"""
        if url in self.monitored_sites:
            del self.monitored_sites[url]
            self.save_data()
    
    async def generate_content_hash(self, url: str) -> Optional[str]:
        """Generate a hash of the website's key content"""
        try:
            crawler = WebsiteCrawler(url, max_pages=10, depth_limit=2)
            pages_data = await crawler.crawl()
            
            if not pages_data:
                return None
            
            # Create a hash from key content elements
            content_elements = []
            for page in pages_data:
                content_elements.append(f"{page['title']}|{page['url']}|{len(page['content'])}")
            
            content_string = "||".join(sorted(content_elements))
            return hashlib.md5(content_string.encode()).hexdigest()
        
        except Exception as e:
            print(f"Error generating hash for {url}: {e}")
            return None
    
    async def check_site_changes(self, url: str) -> bool:
        """Check if a site has changed since last check"""
        if url not in self.monitored_sites:
            return False
        
        site_data = self.monitored_sites[url]
        current_hash = await self.generate_content_hash(url)
        
        if current_hash is None:
            return False
        
        # Update check time
        site_data['last_check'] = datetime.now().isoformat()
        
        # Check for changes
        if site_data['last_hash'] is None:
            # First check
            site_data['last_hash'] = current_hash
            site_data['change_detected'] = False
        elif site_data['last_hash'] != current_hash:
            # Change detected
            site_data['last_hash'] = current_hash
            site_data['change_detected'] = True
            print(f"🔄 Change detected for {url}")
            self.save_data()
            return True
        else:
            site_data['change_detected'] = False
        
        self.save_data()
        return False
    
    async def update_llms_txt(self, url: str) -> Optional[Dict]:
        """Generate updated llms.txt files for a site"""
        try:
            crawler = WebsiteCrawler(url, max_pages=20, depth_limit=3)
            pages_data = await crawler.crawl()
            
            if not pages_data:
                return None
            
            generator = LLMSTxtGenerator(url, pages_data)
            llms_txt = generator.generate_llms_txt()
            llms_full_txt = generator.generate_llms_full_txt()
            
            # Update last generated time
            if url in self.monitored_sites:
                self.monitored_sites[url]['last_generated'] = datetime.now().isoformat()
                self.monitored_sites[url]['change_detected'] = False
                self.save_data()
            
            return {
                'url': url,
                'llms_txt': llms_txt,
                'llms_full_txt': llms_full_txt,
                'pages_count': len(pages_data),
                'generated_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"Error updating llms.txt for {url}: {e}")
            return None
    
    def should_check_site(self, url: str) -> bool:
        """Check if it's time to check a site for updates"""
        if url not in self.monitored_sites:
            return False
        
        site_data = self.monitored_sites[url]
        if site_data['last_check'] is None:
            return True
        
        last_check = datetime.fromisoformat(site_data['last_check'])
        check_interval = timedelta(hours=site_data['check_interval_hours'])
        
        return datetime.now() - last_check >= check_interval
    
    async def run_monitoring_cycle(self):
        """Run one monitoring cycle for all sites"""
        print(f"🔍 Starting monitoring cycle at {datetime.now()}")
        
        sites_to_check = [url for url in self.monitored_sites.keys() if self.should_check_site(url)]
        
        if not sites_to_check:
            print("✅ No sites need checking right now")
            return
        
        print(f"📋 Checking {len(sites_to_check)} sites...")
        
        for url in sites_to_check:
            print(f"🔎 Checking {url}...")
            changed = await self.check_site_changes(url)
            
            if changed:
                print(f"📝 Updating llms.txt for {url}...")
                result = await self.update_llms_txt(url)
                if result:
                    print(f"✅ Updated llms.txt for {url}")
                    # Here you could send notifications, save files, etc.
                else:
                    print(f"❌ Failed to update llms.txt for {url}")
            else:
                print(f"✅ No changes detected for {url}")
        
        print(f"🏁 Monitoring cycle completed at {datetime.now()}")
    
    async def start_monitoring(self, check_interval_minutes: int = 60):
        """Start continuous monitoring"""
        print(f"🚀 Starting continuous monitoring (checking every {check_interval_minutes} minutes)")
        
        while True:
            try:
                await self.run_monitoring_cycle()
                await asyncio.sleep(check_interval_minutes * 60)
            except KeyboardInterrupt:
                print("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in monitoring cycle: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def get_status(self) -> Dict:
        """Get current monitoring status"""
        return {
            'monitored_sites_count': len(self.monitored_sites),
            'sites': {
                url: {
                    'url': data['url'],
                    'check_interval_hours': data['check_interval_hours'],
                    'last_check': data['last_check'],
                    'last_generated': data['last_generated'],
                    'change_detected': data['change_detected'],
                    'needs_check': self.should_check_site(url)
                }
                for url, data in self.monitored_sites.items()
            }
        }

# CLI for testing
if __name__ == "__main__":
    import sys
    
    monitor = WebsiteMonitor()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python monitor.py add <url> [interval_hours]")
        print("  python monitor.py remove <url>")
        print("  python monitor.py check <url>")
        print("  python monitor.py status")
        print("  python monitor.py run")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "add" and len(sys.argv) >= 3:
        url = sys.argv[2]
        interval = int(sys.argv[3]) if len(sys.argv) > 3 else 24
        monitor.add_site(url, interval)
        print(f"✅ Added {url} to monitoring (check every {interval} hours)")
    
    elif command == "remove" and len(sys.argv) >= 3:
        url = sys.argv[2]
        monitor.remove_site(url)
        print(f"✅ Removed {url} from monitoring")
    
    elif command == "check" and len(sys.argv) >= 3:
        url = sys.argv[2]
        async def check():
            changed = await monitor.check_site_changes(url)
            if changed:
                print(f"🔄 Changes detected for {url}")
                result = await monitor.update_llms_txt(url)
                if result:
                    print(f"✅ Generated new llms.txt")
                    print(f"📊 Analyzed {result['pages_count']} pages")
            else:
                print(f"✅ No changes detected for {url}")
        
        asyncio.run(check())
    
    elif command == "status":
        status = monitor.get_status()
        print(f"📊 Monitoring {status['monitored_sites_count']} sites:")
        for url, data in status['sites'].items():
            print(f"  📍 {url}")
            print(f"    Last check: {data['last_check'] or 'Never'}")
            print(f"    Needs check: {'Yes' if data['needs_check'] else 'No'}")
            print(f"    Changes detected: {'Yes' if data['change_detected'] else 'No'}")
    
    elif command == "run":
        asyncio.run(monitor.start_monitoring())
    
    else:
        print("❌ Invalid command")
        sys.exit(1) 