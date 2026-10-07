"""Local Acorn proof of concept. Python stdlib + macOS Vision. No cloud calls."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, re, subprocess, tempfile, os

ROOT = Path(__file__).resolve().parent

ACTION = r'(?:take|swallow|apply|inject|inhale|instil|use)'
STRENGTH = r'\b(\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml))\b'
NUMBERS = {'one': '1', 'two': '2', 'three': '3', 'four': '4', 'half': '0.5', 'a': '1', 'an': '1'}
FORM = r'(tablets?|tabs?|capsules?|caps?)'
ROUTE = r'\b(?:by mouth|orally|oral|po)\b'
CONTINUATION = r'(?i)\b(daily|day|days|times|morning|night|bedtime|food|meals?|hours?|weeks?|by mouth|orally|for\s+\d+)\b'
# Directions we never turn into reminders: they need a person to interpret them.
COMPLEX = r'(?i)as needed|when required|if needed|\bprn\b|\bthen\b|taper|alternate|weekly|every\s+\d+\s+hours|every other|variable|until|sliding scale|as directed'
FREQUENCIES = [
    (r'\b(?:(?:four|4) times (?:daily|a day|per day)|qid|qds)\b', 4),
    (r'\b(?:(?:three|3) times (?:daily|a day|per day)|thrice daily|tid|tds)\b', 3),
    (r'\b(?:twice (?:daily|a day|per day)|(?:two|2) times (?:daily|a day|per day)|bid|bd)\b', 2),
    (r'\b(?:once (?:daily|a day|per day)|every day|each day|daily|every (?:morning|night)|in the (?:morning|evening)|at (?:night|bedtime))\b', 1),
]
DEFAULT_TIMES = {1: ['08:00'], 2: ['08:00', '20:00'], 3: ['08:00', '14:00', '20:00'], 4: ['08:00', '12:00', '16:00', '20:00']}

def parse_directions(directions):
    """Shared with app.js (parseDirections): keep the two in step."""
    low = directions.lower()
    dose = re.search(r'(?i)\b' + ACTION + r'\s+(one|two|three|four|half|an?|\d+(?:\.\d+)?)\s+' + FORM + r'\b', directions)
    per_day = next((count for pattern, count in FREQUENCIES if re.search(pattern, low)), None)
    duration = re.search(r'(?i)\bfor\s+(\d+)\s+(days?|weeks?)\b', directions)
    days = int(duration.group(1)) * (7 if duration.group(2).lower().startswith('week') else 1) if duration else None
    times = re.findall(r'(?<!\d)(?:[01]\d|2[0-3]):[0-5]\d(?!\d)', directions)
    form = ''
    if dose:
        form = 'capsule' if dose.group(2).lower().startswith('cap') else 'tablet'
        amount = NUMBERS.get(dose.group(1).lower(), dose.group(1))
        dose_text = amount + ' ' + form + ('' if amount in ('1', '0.5') else 's')
    else:
        dose_text = ''
    if per_day == 1 and re.search(r'(?i)at (?:night|bedtime)|every night|in the evening', directions) and not times:
        default = ['21:00']
    else:
        default = DEFAULT_TIMES.get(per_day, [])
    return {'dose': dose_text, 'perDay': per_day, 'durationDays': days, 'times': times, 'defaultTimes': default,
            'route': 'By mouth' if re.search(ROUTE, low) else '', 'complex': bool(re.search(COMPLEX, directions))}

def extract_fields(lines):
    text = '\n'.join(line['text'] for line in lines)
    # Directions often wrap across lines on real labels: join a start line with up to two continuation lines.
    directions, used, start = '', set(), None
    for i, line in enumerate(lines):
        if re.match(r'(?i)^\s*' + ACTION + r'\b', line['text']):
            start = i
            break
    if start is not None:
        parts, used = [lines[start]['text'].strip()], {start}
        for j in range(start + 1, min(start + 3, len(lines))):
            nxt = lines[j]['text'].strip()
            if re.match(r'(?i)^\s*' + ACTION + r'\b', nxt) or re.search(r'(?i)' + STRENGTH, nxt) or not re.search(CONTINUATION, nxt):
                break
            parts.append(nxt); used.add(j)
        directions = ' '.join(parts)
    # Another dosing instruction elsewhere (not advice like "Take with food") means a second medicine or a changing regimen.
    other_directions = [l['text'] for i, l in enumerate(lines) if i not in used and re.match(r'(?i)^\s*' + ACTION + r'\s+(?:one|two|three|four|half|an?|\d)', l['text'])]
    seen, candidates = set(), []
    for i, line in enumerate(lines):
        key = re.sub(r'\W+', '', line['text'].lower())
        if i not in used and re.search(r'(?i)' + STRENGTH, line['text']) and key not in seen:
            seen.add(key); candidates.append(line)
    # The first clearly read candidate is used; anything else is shown on review so the person picks deliberately.
    best = max(candidates, key=lambda l: l.get('ocrConfidence', 1), default=None) if candidates else None
    name = best['text'].strip() if best else ''
    strength = re.search(r'(?i)' + STRENGTH, name)
    parsed = parse_directions(directions)
    critical = [lines[i] for i in used] + ([best] if best else [])
    low_ocr = any(line.get('ocrConfidence', 1) < 0.8 for line in critical)
    times = parsed['times'] if parsed['times'] and len(parsed['times']) == parsed['perDay'] else []
    reasons = [reason for reason, failed in [
        ('low_confidence', low_ocr), ('complex_directions', parsed['complex']), ('second_directions', bool(other_directions)),
        ('no_frequency', parsed['perDay'] is None), ('no_dose', not parsed['dose']), ('no_name', not name)] if failed]
    return {'name': name, 'strength': strength.group(1) if strength else '', 'dose': parsed['dose'], 'route': parsed['route'],
            'directions': directions, 'frequency': 'daily' if parsed['perDay'] else 'unresolved', 'perDay': parsed['perDay'],
            'durationDays': parsed['durationDays'], 'times': times or parsed['defaultTimes'],
            'timingSource': 'prescription' if times else 'suggested', 'needsClarification': bool(reasons), 'holdReasons': reasons,
            'multipleCandidates': bool(other_directions), 'otherCandidates': [l['text'].strip() for l in candidates if l is not best],
            'rawText': text}

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
