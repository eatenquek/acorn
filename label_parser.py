"""Turns OCR lines from a medication label into draft schedules for a person to review.

Everything here is a draft: nothing is scheduled until the person checks it against their label.
Directions that need interpretation (as needed, tapering, weekly, injections) are held, never guessed.
"""
import re

WORD_NUMBERS = {'a': 1, 'an': 1, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7,
                'eight': 8, 'nine': 9, 'ten': 10, 'eleven': 11, 'twelve': 12, 'half': 0.5}
NUM = r'(?:\d+(?:\.\d+)?|\d+/\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|half|an?)'
FORMS = [('tablet', r'tablets?|tabs?|caplets?|pills?'), ('capsule', r'capsules?|caps?|softgels?'),
         ('ml', r'mls?|millilit(?:re|er)s?'), ('drop', r'drops?|gtts?'), ('puff', r'puffs?|inhalations?'),
         ('spray', r'sprays?'), ('sachet', r'sachets?'), ('patch', r'patch(?:es)?'), ('unit', r'units?|iu')]
FORM = '|'.join(pattern for _, pattern in FORMS)
DOSE = re.compile(rf'(?i)\b({NUM})\s*({FORM})(?![a-z])')
ACTION = r'(?:take|swallow|give|chew|dissolve|apply|inhale|instil|instill|use|insert|place|put|spray|inject)'
STRENGTH = re.compile(r'(?i)\b(\d+(?:\.\d+)?\s*(?:mg|mcg|µg|ug|g|iu|%)(?:\s*/\s*\d*(?:\.\d+)?\s*(?:ml|g|dose|actuation))?)(?![a-z])')
NOISE = re.compile(r'(?i)\b(?:qty|quantity|refills?|rx\s*(?:no|#)|ndc|tel|phone|fax|expir\w*|exp|dispensed|date|dr|doctor|prescriber|patient|address|pharmacy|clinic|hospital|polyclinic|keep|warning|caution|lot|batch|price|cost|www|street|road|avenue)\b|\$|@')
CONTINUATION = re.compile(r'(?i)\b(daily|day|days|times?|morning|noon|afternoon|evening|night|bedtime|breakfast|lunch|dinner|supper|food|meals?|hours?|hrs?|weeks?|months?|by mouth|orally|for\s+\d+|bd|tds|qds|om|on|am|pm|until|finished|completed|course|stomach|water)\b')

COMPLEX = re.compile(r'(?i)as needed|when needed|if needed|when required|if required|\bprn\b|\bsos\b|\bthen\b|followed by|taper|reduc|increas|alternate|every other|weekly|\ba week\b|per week|fortnight|monthly|\ba month\b|sliding scale|as directed|as instructed|as advised|\bup to\b|\bmax(?:imum)?\b|\bif (?:pain|fever|necessary)|\bon (?:mon|tue|wed|thu|fri|sat|sun)')
UNTIL_OK = re.compile(r'(?i)\buntil\b(?!\s+(?:finished|completed|all\b|the course|course|gone))')
DOSE_RANGE = re.compile(rf'(?i)\b{NUM}\s*(?:-|to|or)\s*{NUM}\s*(?:{FORM})(?![a-z])')

MEALS = {'breakfast': '08:00', 'lunch': '13:00', 'dinner': '19:00', 'supper': '19:00'}
DEFAULT_TIMES = {1: ['08:00'], 2: ['08:00', '20:00'], 3: ['08:00', '14:00', '20:00'], 4: ['08:00', '12:00', '16:00', '20:00']}
MEAL_TIMES = {2: ['08:00', '19:00'], 3: ['08:00', '13:00', '19:00']}
ROUTES = [('Under the tongue', r'under the tongue|sublingual'), ('Inhaled', r'\binhale|\bpuffs?\b|inhaler'),
          ('Eye', r'\beyes?\b|\bocular'), ('Ear', r'\bears?\b'), ('Nose', r'\bnostrils?\b|\bnose\b|\bnasal'),
          ('On the skin', r'\bapply\b|\bskin\b|affected area|topical'), ('By mouth', r'by mouth|\borally\b|\boral\b|\bpo\b|\bswallow|\bchew')]
WARNINGS = {'low_confidence': 'Parts of this label were hard to read. Check each detail carefully.',
            'route_assumed': 'The label does not say how to take it. We filled in “By mouth” for a tablet or capsule; change it if that is wrong.',
            'no_name': 'We could not find the medicine name. Type it as written on the label.',
            'no_dose': 'We could not find the amount per dose. Add it from your label.',
            'no_frequency': 'We could not tell how often to take this. Check the directions match your label.',
            'no_directions': 'We could not find the directions. Type them as written on the label.'}
HOLDS = {'complex_directions': '“As needed”, tapering, weekly or changing directions do not become daily reminders.',
         'unsupported_interval': 'This dosing interval does not divide evenly into a day, so it needs a different setup.',
         'injection': 'Injections and unit-based doses need a setup checked by your care team.'}


def normalize(text):
    t = text.replace('½', '1/2').replace('¼', '1/4').replace('’', "'").replace('–', '-')
    t = re.sub(r'(?i)\((s|es)\)', r'\1', t)                                    # tablet(s) -> tablets
    t = re.sub(r'(?i)\b(one|two|three|four|half)\s*\(\s*[\d/.]+\s*\)', r'\1', t)  # ONE (1) -> ONE
    t = re.sub(r'(?i)\b(\d+(?:\.\d+)?)\s*\(\s*[a-z]+\s*\)', r'\1', t)           # 1 (one) -> 1
    t = re.sub(r'(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])', ' ', t)               # OCR: "TAKE1CAPSULE", "500mg"
    t = re.sub(r'(?i)(?<![\w.])[lI|](?=\s*(?:tab|cap|tablet|capsule)s?\b)', '1', t)  # OCR: "l tablet"
    return re.sub(r'\s+', ' ', t).strip()


def number(word):
    word = word.lower()
    if word in WORD_NUMBERS:
        return WORD_NUMBERS[word]
    if '/' in word:
        top, bottom = word.split('/')
        return int(top) / int(bottom) if int(bottom) else None
    return float(word)


def amount_text(value):
    return {0.5: '1/2', 0.25: '1/4'}.get(value, f'{value:g}')


def form_of(word):
    return next(name for name, pattern in FORMS if re.fullmatch(pattern, word, re.I))


def dose_of(text):
    """'TAKE ONE (1) TAB' -> '1 tablet'; '' when no amount is written."""
    match = DOSE.search(normalize(text))
    if not match:
        return ''
    value, form = number(match.group(1)), form_of(match.group(2))
    plural = '' if value <= 1 or form == 'ml' else ('es' if form == 'patch' else 's')
    return f'{amount_text(value)} {form}{plural}'


def clock(hour, minute, meridiem):
    hour = int(hour)
    if meridiem:
        hour = hour % 12 + (12 if meridiem.lower().startswith('p') else 0)
    return f'{hour:02d}:{int(minute or 0):02d}'


def explicit_times(text):
    found = [clock(h, m, ap) for h, m, ap in re.findall(r'(?i)\b([01]?\d|2[0-3]):([0-5]\d)\s*(a\.?m\.?|p\.?m\.?)?', text)]
    found += [clock(h, m, ap) for h, m, ap in re.findall(r'(?i)\b(1[0-2]|0?[1-9])(?:\.([0-5]\d))?\s*(a\.?m\.?|p\.?m\.?)(?![a-z])', text)]
    return sorted(set(found))


def frequency(text, original):
    """Returns (per_day, interval_hours, label_times, hold_reason)."""
    interval = re.search(rf'(?i)\b(?:every|each)\s+({NUM})\s*(?:(?:-|to|or)\s*({NUM})\s*)?(?:hours?|hrs?|h)\b|\bq\s*(\d+)\s*h(?:rs?|ours?)?\b', text)
    if interval:
        if interval.group(2):
            return None, None, [], 'complex_directions'
        hours = number(interval.group(1) or interval.group(3))
        if hours not in (4, 6, 8, 12, 24):
            return None, None, [], 'unsupported_interval'
        hours = int(hours)
        return 24 // hours, hours, [], None
    counted = re.search(rf'(?i)\b(?:(once|twice|thrice)|({NUM})\s*(?:x|times?))(?![a-z])(?!\s*(?:a|per|every|each)?\s*(?:week|wk|month|fortnight|hour))', text) \
        or re.search(r'(?i)\bx\s*(\d)\s*(?:a|per|/)?\s*(?:day|daily)\b', text)
    if counted:
        groups = [g for g in counted.groups() if g]
        per_day = {'once': 1, 'twice': 2, 'thrice': 3}.get(groups[0].lower()) or number(groups[0])
        if per_day == int(per_day) and 1 <= per_day <= 6:
            return int(per_day), None, [], None
    for pattern, per_day in [(r'\b(?:qds|qid|q\.d\.s\.?|q\.i\.d\.?)\b', 4), (r'\b(?:tds|tid|t\.d\.s\.?|t\.i\.d\.?)\b', 3),
                             (r'\b(?:bd|bid|b\.d\.?|b\.i\.d\.?)\b', 2)]:
        if re.search(pattern, text, re.I):
            return per_day, None, [], None
    # Short Latin forms that are also English words count only in capitals: "1 tab ON", not "put it on".
    if re.search(r'\b(?:OM|QAM)\b|\bmane\b', original):
        return 1, None, ['08:00'], None
    if re.search(r'\b(?:ON|HS|QHS|QPM)\b|\bnocte\b', original):
        return 1, None, ['21:00'], None
    if re.search(r'\b(?:OD|QD)\b', original):
        return 1, None, [], None
    low = text.lower()
    if re.search(r'morning\b.*\b(?:noon|midday|afternoon|lunch)\b.*\b(?:night|evening|bedtime)', low):
        return 3, None, ['08:00', '13:00', '21:00'], None
    if re.search(r'morning\s*(?:and|&|,|/)\s*(?:at\s+)?(?:night|evening|bedtime)', low):
        return 2, None, ['08:00', '21:00'], None
    meals = [meal for meal in MEALS if re.search(rf'\b{meal}\b', low)]
    if meals:
        return len(meals), None, sorted({MEALS[m] for m in meals}), None
    if re.search(r'\b(?:every|each|in the) morning\b|\bmornings?\b', low):
        return 1, None, ['08:00'], None
    if re.search(r'\b(?:every|each|at|in the) (?:night|evening)\b|\bnightly\b|\bbedtime\b|before bed\b', low):
        return 1, None, ['21:00'], None
    if re.search(r'\b(?:daily|every day|each day|a day|per day|once)\b', low):
        return 1, None, [], None
    return None, None, [], None


def route_of(text):
    low = text.lower()
    return next((name for name, pattern in ROUTES if re.search(pattern, low)), '')


def parse_directions(directions):
    text = normalize(directions)
    dose = dose_of(text)
    per_day, interval, label_times, hold = frequency(text, text)
    if COMPLEX.search(text) or UNTIL_OK.search(text) or DOSE_RANGE.search(text):
        hold = 'complex_directions'
    if re.search(r'(?i)\binject|\b\d+\s*(?:units?|iu)\b', text):
        hold = hold or 'injection'
    duration = re.search(rf'(?i)\b(?:for|x)\s*({NUM})\s*(days?|weeks?|wks?)\b', text)
    days = None
    if duration:
        days = int(number(duration.group(1)) * (7 if duration.group(2).lower().startswith('w') else 1))
    written = explicit_times(text)
    instructions = ', '.join(dict.fromkeys(m.group(0).lower() for m in re.finditer(
        r'(?i)\b(?:before|after|with|without)\s+(?:food|meals?|breakfast|lunch|dinner|supper|milk)\b|on an empty stomach|with (?:a full glass of )?water|swallow whole|do not (?:crush|chew)', text)))
    if written and len(written) == per_day:
        times, source = written, 'prescription'
    elif interval:
        first = 6 if interval == 8 else 8  # 06:00 · 14:00 · 22:00 rather than a midnight dose
        times, source = sorted(f'{(first + k * interval) % 24:02d}:00' for k in range(per_day)), 'interval'
    elif label_times and len(label_times) == per_day:
        times, source = label_times, 'suggested'
    elif per_day in MEAL_TIMES and re.search(r'(?i)\bmeals?\b|\bfood\b', text):
        times, source = MEAL_TIMES[per_day], 'suggested'
    else:
        times, source = DEFAULT_TIMES.get(per_day, []), 'suggested'
    if per_day and per_day > 4 and not interval:
        hold = hold or 'unsupported_interval'
    return {'dose': dose, 'perDay': per_day, 'intervalHours': interval, 'durationDays': days, 'times': times,
            'timingSource': source, 'route': route_of(text), 'instructions': instructions, 'hold': hold}


def is_directions_start(text):
    t = normalize(text)
    if re.match(rf'(?i)^\W*{ACTION}\b', t):
        return bool(DOSE.search(t) or frequency(t, t)[0] or re.match(r'(?i)^\W*apply\b', t))
    return bool(DOSE.search(t)) and not STRENGTH.search(t) and not NOISE.search(t)


def strength_of(text):
    match = STRENGTH.search(text)
    return re.sub(r'\s+', ' ', match.group(1)).strip() if match else ''


def name_like(text):
    letters = re.sub(r'[^a-z]', '', text.lower())
    return 3 <= len(letters) and len(text) <= 70 and not NOISE.search(text) and not re.search(r'\d{3,}', text)


def split_rows(lines):
    """Records and tables often put name and directions on one row: "Amlodipine 5 mg tablet Take 1 tablet daily"."""
    out = []
    for line in lines:
        text = line['text']
        strength = STRENGTH.search(text)
        verb = re.search(rf'(?i)\b{ACTION}\b', text[strength.end():]) if strength else None
        if verb and text[:strength.end() + verb.start()].strip():
            cut = strength.end() + verb.start()
            out += [{**line, 'text': text[:cut].strip(' |;,-')}, {**line, 'text': text[cut:].strip()}]
        else:
            out.append(line)
    return out


def extract(lines):
    """OCR lines -> list of draft medicines, in label order."""
    lines = split_rows(lines)
    texts = [normalize(line['text']) for line in lines]  # for matching
    shown = [re.sub(r'\s+', ' ', line['text']).strip() for line in lines]  # as printed, for the person to compare
    used, blocks = set(), []
    for i, text in enumerate(texts):
        if i in used or not is_directions_start(text):
            continue
        block = [i]
        for j in range(i + 1, min(i + 4, len(texts))):
            nxt = texts[j]
            if is_directions_start(nxt) or STRENGTH.search(nxt) or NOISE.search(nxt) or not CONTINUATION.search(nxt):
                break
            block.append(j)
        # Without a verb, a dose fragment only counts if a frequency follows (e.g. "1 TABLET" / "TWICE DAILY").
        if not re.match(rf'(?i)^\W*{ACTION}\b', text) and not parse_directions(' '.join(texts[k] for k in block))['perDay']:
            continue
        used.update(block)
        blocks.append(block)
    # Duplicated labels (a bottle beside its label, a repeated page) give the same directions twice.
    unique, seen = [], set()
    for block in blocks:
        key = re.sub(r'\W+', '', ' '.join(texts[i] for i in block).lower())
        if key not in seen:
            seen.add(key)
            unique.append(block)
    blocks = unique

    candidates = []
    for i, text in enumerate(texts):
        if i in used or not STRENGTH.search(text) or (NOISE.search(text) and not re.search(r'(?i)\b(?:tablets?|capsules?)\b', text)):
            continue
        name = shown[i]
        letters = re.sub(r'(?i)\b(?:mg|mcg|g|ml|iu|tablets?|tabs?|capsules?|caps?)\b|[^a-z]', '', text.lower())
        if len(letters) < 3 and i > 0 and i - 1 not in used and name_like(texts[i - 1]):
            name = shown[i - 1] + ' ' + shown[i]  # "AMOXICILLIN" / "500MG CAPSULES"
        candidates.append((i, name))
    unique_names, seen = [], set()
    for i, name in candidates:
        key = re.sub(r'\W+', '', name.lower())
        if key not in seen:
            seen.add(key)
            unique_names.append((i, name))
    candidates = unique_names

    raw = '\n'.join(line['text'] for line in lines)
    if not blocks:
        name = candidates[0][1] if candidates else ''
        return [draft(name, '', [line for line in lines], raw, [n for _, n in candidates[1:]], extra=['no_directions'])]

    medicines, taken = [], set()
    for b, block in enumerate(blocks):
        start, end = block[0], block[-1]
        prev_end = blocks[b - 1][-1] if b else -1
        next_start = blocks[b + 1][0] if b + 1 < len(blocks) else len(texts)
        before = [c for c in candidates if prev_end < c[0] < start and c[0] not in taken]
        after = [c for c in candidates if end < c[0] < next_start and c[0] not in taken]
        # A name above the directions belongs to them; below is the next best guess (common label layout).
        chosen = before[-1] if before else (after[0] if after else None)
        name = chosen[1] if chosen else ''
        if not chosen:
            above = [k for k in range(start - 1, max(prev_end, start - 4), -1) if name_like(texts[k]) and k not in used]
            name = shown[above[0]] if above else ''
        if chosen:
            taken.add(chosen[0])
        directions = ' '.join(shown[i] for i in block)
        critical = [lines[i] for i in block] + ([lines[chosen[0]]] if chosen else [])
        medicines.append(draft(name, directions, critical, raw, []))
    if len(medicines) == 1:
        medicines[0]['otherCandidates'] = [n for i, n in candidates if i not in taken]
    return medicines


def draft(name, directions, critical_lines, raw, others, extra=()):
    parsed = parse_directions(directions)
    warnings = list(extra)
    if any(line.get('ocrConfidence', 1) < 0.8 for line in critical_lines):
        warnings.append('low_confidence')
    if not name:
        warnings.append('no_name')
    if directions and not parsed['dose'] and not parsed['hold']:
        warnings.append('no_dose')
    if directions and not parsed['perDay'] and not parsed['hold']:
        warnings.append('no_frequency')
    route = parsed['route']
    if not route and re.search(r'^\d.* (?:tablet|capsule)', parsed['dose']):
        route = 'By mouth'
        warnings.append('route_assumed')
    holds = [parsed['hold']] if parsed['hold'] else []
    return {'name': name, 'strength': strength_of(name), 'dose': parsed['dose'], 'route': route, 'directions': directions,
            'instructions': parsed['instructions'], 'frequency': 'daily' if parsed['perDay'] else 'unresolved',
            'perDay': parsed['perDay'], 'intervalHours': parsed['intervalHours'], 'durationDays': parsed['durationDays'],
            'times': parsed['times'], 'timingSource': parsed['timingSource'], 'needsClarification': bool(holds),
            'holdReasons': holds, 'holdMessages': [HOLDS[h] for h in holds], 'warnings': warnings,
            'warningMessages': [WARNINGS[w] for w in warnings], 'otherCandidates': list(others), 'rawText': raw}


def validate(d):
    """Re-checks a draft after the person edits it. Returns {'draft'} plus 'error' or 'hold' when it cannot be scheduled."""
    directions = (d.get('directions') or '').strip()
    parsed = parse_directions(directions)
    name, strength = (d.get('name') or '').strip(), (d.get('strength') or '').strip()
    dose, route = (d.get('dose') or '').strip(), (d.get('route') or '').strip()
    if parsed['hold']:
        return {'hold': True, 'draft': {**d, 'needsClarification': True, 'holdReasons': [parsed['hold']], 'holdMessages': [HOLDS[parsed['hold']]]}}
    error = None
    in_name = strength_of(name)
    if not name:
        error = 'Add the medicine name as written on the label.'
    elif not directions:
        error = 'Add the directions as written on the label.'
    elif not parsed['perDay']:
        error = 'We could not tell how often to take this from the directions. Check they match your label, or ask your pharmacist if the label does not say.'
    elif not dose:
        error = 'Add the amount per dose.'
    elif not route:
        error = 'Add how it is taken, for example by mouth.'
    elif strength and in_name and in_name.replace(' ', '').lower() != strength.replace(' ', '').lower():
        error = 'The strength differs from the medicine name. Correct the fields so they match.'
    elif parsed['dose'] and dose_of(dose) != parsed['dose']:
        error = 'The amount per dose differs from the directions. Correct the fields so they match.'
    elif parsed['route'] and route.lower() != parsed['route'].lower():
        error = 'The route differs from the directions. Correct the fields so they match.'
    if error:
        return {'error': error, 'draft': d}
    keep = {k: parsed[k] for k in ('perDay', 'intervalHours', 'durationDays', 'times', 'timingSource', 'instructions')}
    return {'draft': {**d, **keep, 'frequency': 'daily', 'needsClarification': False}}
