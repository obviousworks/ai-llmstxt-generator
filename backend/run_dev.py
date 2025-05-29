#!/usr/bin/env python3
"""
Development server runner for LLMs.txt Generator
Runs both the main API and scheduler service on different ports
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def run_servers():
    # Get the backend directory
    backend_dir = Path(__file__).parent
    
    # Processes list to track
    processes = []
    
    try:
        print("🚀 Starting LLMs.txt Generator Development Servers")
        print("=" * 50)
        
        # Start main API server on port 8000
        print("📡 Starting main API server on http://localhost:8000")
        main_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app", 
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ], cwd=backend_dir)
        processes.append(("Main API", main_process))
        
        # Wait a moment before starting scheduler
        time.sleep(2)
        
        # Start scheduler server on port 8001
        print("⏰ Starting scheduler service on http://localhost:8001")
        scheduler_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "scheduler:scheduler_app",
            "--host", "0.0.0.0", "--port", "8001", "--reload"
        ], cwd=backend_dir)
        processes.append(("Scheduler", scheduler_process))
        
        print("\n✅ Both servers are running!")
        print("📋 Main API: http://localhost:8000")
        print("📋 API Docs: http://localhost:8000/docs")
        print("🔄 Scheduler: http://localhost:8001")
        print("🔄 Scheduler Docs: http://localhost:8001/docs")
        print("\n💡 Make sure your frontend .env has:")
        print("   NEXT_PUBLIC_API_URL=http://localhost:8000")
        print("\n🛑 Press Ctrl+C to stop all servers")
        print("=" * 50)
        
        # Wait for processes
        while True:
            time.sleep(1)
            # Check if any process died
            for name, process in processes:
                if process.poll() is not None:
                    print(f"❌ {name} server stopped unexpectedly")
                    return
                    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Cleanup processes
        for name, process in processes:
            try:
                print(f"🔄 Stopping {name} server...")
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"⚠️  Force killing {name} server...")
                process.kill()
                process.wait()
        print("✅ All servers stopped")

if __name__ == "__main__":
    run_servers() 