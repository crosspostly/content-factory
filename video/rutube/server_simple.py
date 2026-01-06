import http.server
import socketserver
import os
import json
import threading
import config

PORT = config.SERVER_PORT
UPLOAD_FOLDER = config.UPLOADS_DIR
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_HEAD(self):
        print("DEBUG: do_HEAD called")
        self.serve_request(send_body=False)

    def do_GET(self):
        self.serve_request(send_body=True)

    def serve_request(self, send_body=True):
        print(f"DEBUG: {self.command} path={self.path}")
        
        # Эндпоинт проверки здоровья (GET only usually, but HEAD ok)
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            if send_body:
                self.wfile.write(json.dumps({"status": "ok", "service": "Rutube Native Server"}).encode())
            return

        filename = None
        
        # 1. Webhook Hack
        if self.path.startswith('/webhook') and 'file=' in self.path:
            try:
                from urllib.parse import urlparse, parse_qs
                query = parse_qs(urlparse(self.path).query)
                filename = query.get('file', [None])[0]
            except: pass
            
        # 2. Static paths
        elif self.path.startswith('/static/'):
            filename = self.path.replace('/static/', '')
        elif self.path.startswith('/rutube-webhook/static/'):
            filename = self.path.replace('/rutube-webhook/static/', '')

        if filename:
            # Prevent directory traversal
            filename = os.path.basename(filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            print(f"DEBUG: Serving {file_path}")
            
            if os.path.exists(file_path):
                try:
                    file_size = os.path.getsize(file_path)
                    self.send_response(200)
                    self.send_header("Content-Type", "video/mp4") # Force MP4
                    self.send_header("Content-Length", str(file_size))
                    self.end_headers()
                    
                    if send_body:
                        with open(file_path, 'rb') as f:
                            import shutil
                            shutil.copyfileobj(f, self.wfile)
                        print(f"DEBUG: Served {file_size} bytes")
                except Exception as e:
                    print(f"ERROR serving file: {e}")
            else:
                print(f"DEBUG: File not found: {file_path}")
                self.send_response(404)
                self.end_headers()
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        # Заглушка для вебхука (без Flask сложно парсить multipart, оставим простую логику)
        if self.path == '/webhook':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            print(f"Received webhook data: {len(post_data)} bytes")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "accepted", "message": "Webhook received (native)"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

print(f"Starting native server on port {PORT}...")
print(f"Serving files from: {UPLOAD_FOLDER}")

# Разрешаем повторное использование порта
socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()