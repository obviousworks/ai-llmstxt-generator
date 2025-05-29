from http.server import BaseHTTPRequestHandler
import json
import asyncio
from .scheduler import AutoUpdater, MONITORED_SITES

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle cron job requests - automatically check all sites"""
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Run the auto-updater
            result = asyncio.run(self.run_scheduled_checks())
            
            response_json = json.dumps(result, ensure_ascii=False)
            self.wfile.write(response_json.encode('utf-8'))
            
        except Exception as e:
            self._send_error_response(500, f'Cron job error: {str(e)}')
    
    def do_POST(self):
        """Handle manual cron triggers"""
        self.do_GET()
    
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
    
    async def run_scheduled_checks(self):
        """Run scheduled checks for all monitored sites"""
        updater = AutoUpdater()
        
        if not MONITORED_SITES:
            return {
                'status': 'completed',
                'message': 'No sites are currently being monitored',
                'sites_checked': 0,
                'updates_made': 0
            }
        
        print(f"Running scheduled checks for {len(MONITORED_SITES)} monitored sites")
        
        results = await updater.check_all_monitored_sites()
        
        # Count updates
        sites_checked = len([r for r in results if r['status'] == 'checked'])
        updates_made = len([r for r in results if r.get('updated', False)])
        
        return {
            'status': 'completed',
            'sites_checked': sites_checked,
            'updates_made': updates_made,
            'total_monitored': len(MONITORED_SITES),
            'results': results
        } 