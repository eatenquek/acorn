"""Local Acorn proof of concept. Python stdlib + macOS Vision. No cloud calls."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, subprocess, tempfile, os
import label_parser

ROOT = Path(__file__).resolve().parent

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs): super().__init__(*args, directory=str(ROOT), **kwargs)
    def log_message(self, *_): pass  # Do not log uploaded data or filenames.
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()
    def do_GET(self):
        if self.path.split('?')[0] not in ['/', '/index.html', '/styles.css', '/app.js', '/sample-label.png', '/sample-record.pdf', '/storyboard.svg', '/favicon.ico']:
            self.send_error(404); return
        super().do_GET()
    def respond(self, status, data):
        body = json.dumps(data).encode(); self.send_response(status)
        self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(body)))
        self.end_headers(); self.wfile.write(body)
    def do_POST(self):
        if self.path not in ('/api/extract', '/api/validate'): self.respond(404, {'error': 'Unknown endpoint'}); return
        if self.headers.get('Origin') not in (None, 'http://127.0.0.1:8765', 'http://localhost:8765'):
            self.respond(403, {'error': 'Local requests only'}); return
        if self.path == '/api/validate':
            try:
                length = int(self.headers.get('Content-Length', 0))
                if not 0 < length <= 64 * 1024: raise ValueError
                self.respond(200, label_parser.validate(json.loads(self.rfile.read(length))))
            except (ValueError, TypeError, AttributeError): self.respond(400, {'error': 'The details could not be checked.'})
            return
        try: length = int(self.headers.get('Content-Length', 0))
        except ValueError: length = 0
        if not 0 < length <= 10 * 1024 * 1024: self.respond(413, {'error': 'Choose a file smaller than 10 MB.'}); return
        name = None
        try:
            with tempfile.NamedTemporaryFile(prefix='acorn-', delete=False) as f:
                name = f.name; f.write(self.rfile.read(length))
            process = subprocess.run([str(ROOT / 'ocr'), name], capture_output=True, text=True, timeout=40)
            result = json.loads(process.stdout)
            if result.get('error'): self.respond(422, result); return
            if not result.get('lines'): self.respond(422, {'error': 'No readable text found. Retake the photo in brighter light.'}); return
            result['medicines'] = label_parser.extract(result['lines'])
            result['draft'] = result['medicines'][0]
            self.respond(200, result)
        except subprocess.TimeoutExpired: self.respond(422, {'error': 'Reading took too long. Try a smaller, clearer file.'})
        except Exception: self.respond(500, {'error': 'The file could not be read. Try a clear label image or PDF.'})
        finally:
            if name: os.unlink(name)

if __name__ == '__main__':
    print('Acorn prototype: http://127.0.0.1:8765', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8765), Handler).serve_forever()
