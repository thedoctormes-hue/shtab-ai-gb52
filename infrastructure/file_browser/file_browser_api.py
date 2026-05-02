#!/usr/bin/env python3
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

QWIEN_DIR = Path('/root/.qwen')
SYNC_FOLDER = Path('/var/syncthing/Sync')  # Syncthing shared folder

class FileBrowserAPI(BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    
    def do_GET(self):
        path = self.path.split('?')[0]
        if path == '/api/files':
            self.list_files()
        elif path.startswith('/api/file/'):
            filepath = path.replace('/api/file/', '')
            self.read_file(filepath)
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/upload':
            self.upload_file()
        else:
            self.send_error(404)
    
    def list_files(self):
        files = []
        for f in list(QWIEN_DIR.rglob('*'))[:100]:
            if f.is_file():
                files.append({
                    'name': f.name,
                    'path': str(f.relative_to(QWIEN_DIR)),
                    'size': f.stat().st_size,
                    'modified': f.stat().st_mtime
                })
        self.send_json(files)
    
    def read_file(self, filepath):
        try:
            f = QWIEN_DIR / filepath
            if f.exists() and f.is_file():
                content = f.read_text()[:10000]
                self.send_json({'content': content, 'size': len(content)})
            else:
                self.send_error(404)
        except Exception as e:
            self.send_json({'error': str(e)})
    
    def upload_file(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            content_type = self.headers.get('Content-Type', '')
            
            # Parse multipart
            boundary = None
            for part in content_type.split(';'):
                if 'boundary=' in part:
                    boundary = part.split('=')[1]
                    break
            
            if not boundary:
                self.send_json({'error': 'No boundary'})
                return
            
            body = self.rfile.read(content_length)
            body_str = body.decode('utf-8', errors='ignore')
            
            # Extract filename and content
            lines = body_str.split('\r\n')
            filename = 'upload.txt'
            content = ''
            
            for i, line in enumerate(lines):
                if 'filename=' in line:
                    filename = line.split('filename=')[1].strip('"').strip()
                    continue
                if i > 3 and line and not line.startswith('--'):
                    content = line
                    # Get rest of content
                    content = '\r\n'.join(lines[i:])
                    content = content.split('--' + boundary)[0].strip('\r\n')
                    break
            
            # Save to sync folder
            SYNC_FOLDER.mkdir(parents=True, exist_ok=True)
            filepath = SYNC_FOLDER / filename
            filepath.write_text(content)
            
            self.send_json({'status': 'ok', 'path': str(filepath)})
        except Exception as e:
            self.send_json({'error': str(e)})
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    HTTPServer(('', 8001), FileBrowserAPI).serve_forever()