"""
serve.py - Local Development Server with Auto-Reindexing for Gabriele Antonini's Website.

Serves the website locally at http://localhost:8000 and automatically rebuilds
the index when any file inside 'notes/' changes.

Usage:
    python serve.py
"""

import threading
import http.server
import socketserver
import os
from pathlib import Path
from watch_site import watch

PORT = 8000
DIRECTORY = Path(__file__).resolve().parent

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def log_message(self, format, *args):
        # Cleaner console logs
        pass

def run_server():
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"\n[HTTP SERVER] Website is live at: http://localhost:{PORT}")
        print(f"[HTTP SERVER] Serving files from: {DIRECTORY}")
        httpd.serve_forever()

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    # Start file watcher in background thread
    watcher_thread = threading.Thread(target=watch, daemon=True)
    watcher_thread.start()
    
    # Run HTTP server in main thread
    try:
        run_server()
    except KeyboardInterrupt:
        print("\n[*] Server stopped.")
