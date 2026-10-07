"""Local Acorn proof of concept. Python stdlib + macOS Vision. No cloud calls."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, re, subprocess, tempfile, os

ROOT = Path(__file__).resolve().parent

def extract_fields(lines):
    text = '\n'.join(line['text'] for line in lines)
    # Deliberately narrow grammar: this is a reviewable draft, not a clinical SIG parser.
    directions = next((line['text'] for line in lines if re.match(r'(?i)^\s*(take|apply|inject|inhale|instil)', line['text'])), '')
    candidates = [line['text'] for line in lines if re.search(r'(?i)\b\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml)\b', line['text']) and line['text'] != directions]
    name = candidates[0] if len(candidates) == 1 else ''
    strength = re.search(r'(?i)\b(\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml))\b', name)
    dose = re.search(r'(?i)\btake\s+(one|two|three|half|\d+(?:\.\d+)?)\s+(tablet[s]?|capsule[s]?|ml)\b', directions)
    times = re.findall(r'(?<!\d)(?:[01]\d|2[0-3]):[0-5]\d(?!\d)', directions)
    complex_sig = bool(re.search(r'(?i)as needed|when required|\bprn\b|\bthen\b|taper|alternate|weekly|every\s+\d+\s+hours|variable|\bbid\b|\btid\b|\bq\.?d\b', directions))
    complex_sig = complex_sig or len(re.findall(r'(?im)^\s*(take|apply|inject|inhale|instil)', text)) != 1 or bool(re.search(r'(?i)for\s+\d+\s+(days?|weeks?)|start\s+date|stop\s+date|until|then|as needed|every\s+\d+\s+hours', text))
    daily = bool(re.search(r'(?i)\b(every day|once daily|once a day|daily)\b', directions))
    simple_daily = bool(re.fullmatch(r'(?i)Take\s+(?:one|two|three|half|\d+(?:\.\d+)?)\s+(?:tablets?|capsules?)\s+by mouth\s+(?:at\s+(?:[01]\d|2[0-3]):[0-5]\d\s+)?(?:every day|once daily|once a day|daily)\.?', directions.strip()))
    critical_lines = [line for line in lines if line['text'] == name or line['text'] == directions]
    low_ocr = any(line.get('ocrConfidence', 1) < 0.8 for line in critical_lines)
    return {'name': name, 'strength': strength.group(1) if strength else '', 'dose': dose.group(1).lower() + ' ' + dose.group(2).lower() if dose else '', 'route': 'By mouth' if re.search(r'(?i)by mouth', directions) else '', 'directions': directions, 'frequency': 'daily' if daily and not complex_sig else 'unresolved', 'times': times if simple_daily else [], 'needsClarification': low_ocr or complex_sig or not simple_daily or not name or not dose, 'multipleCandidates': len(candidates) > 1, 'timingSource': 'prescription' if times and simple_daily else 'patient_preference', 'rawText': text}

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
        if self.path != '/api/extract': self.respond(404, {'error': 'Unknown endpoint'}); return
        if self.headers.get('Origin') not in (None, 'http://127.0.0.1:8765', 'http://localhost:8765'):
            self.respond(403, {'error': 'Local requests only'}); return
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
            result['draft'] = extract_fields(result['lines'])
            self.respond(200, result)
        except subprocess.TimeoutExpired: self.respond(422, {'error': 'Reading took too long. Try a smaller, clearer file.'})
        except Exception: self.respond(500, {'error': 'The file could not be read. Try a clear label image or PDF.'})
        finally:
            if name: os.unlink(name)

if __name__ == '__main__':
    print('Acorn prototype: http://127.0.0.1:8765', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8765), Handler).serve_forever()
