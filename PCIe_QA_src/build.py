#!/usr/bin/env python3
"""Build the single-file PCIe Q&A study page.

Inputs : shell.html, diagrams.js, modules.json, content/m*.txt
Output : out/PCIe_QA_Study_Guide.html

Authoring format (content/mNN.txt) — one block per question:

@@ 1.03 | Basic | Concept | fig=topology | tags=topology,rc
Q: question text
SHORT: 30-second answer (1-3 sentences)
DEEP:
paragraphs, "- " bullets, "1. " lists, | tables |, ```code fences```, `inline code`, **bold**
FOLLOW:
- follow-up question => brief answer
PITFALL: one common mistake
VERIFY: spec-sensitive facts to double check (optional)
"""
import json, re, sys, glob, os

ROOT = os.path.dirname(os.path.abspath(__file__))
LEVELS = ['Basic', 'Intermediate', 'Advanced', 'Principal']
TYPES = ['Concept', 'Numeric', 'Scenario', 'Debug', 'Cross-layer', 'Trap']
KEYS = ['Q', 'SHORT', 'DEEP', 'FOLLOW', 'PITFALL', 'VERIFY']
KEY_RE = re.compile(r'^(Q|SHORT|DEEP|FOLLOW|PITFALL|VERIFY):[ \t]?(.*)$')


def parse_file(path):
    qs, cur, key, infence = [], None, None, False
    with open(path, encoding='utf-8') as f:
        lines = f.read().split('\n')
    for ln, line in enumerate(lines, 1):
        if line.startswith('@@ '):
            if cur:
                qs.append(cur)
            parts = [p.strip() for p in line[3:].split('|')]
            if len(parts) < 3:
                raise SystemExit(f'{path}:{ln}: bad header {line!r}')
            cur = {'id': parts[0], 'level': parts[1], 'type': parts[2], 'fig': None, 'tags': [],
                   'raw': {k: [] for k in KEYS}, '_src': f'{os.path.basename(path)}:{ln}'}
            for extra in parts[3:]:
                if extra.startswith('fig='):
                    cur['fig'] = extra[4:].strip()
                elif extra.startswith('tags='):
                    cur['tags'] = [t.strip() for t in extra[5:].split(',') if t.strip()]
            key, infence = None, False
            continue
        if cur is None:
            continue  # preamble / comments before first block
        if line.startswith('```'):
            infence = not infence
        m = None if infence else KEY_RE.match(line)
        if m:
            key = m.group(1)
            if m.group(2) != '':
                cur['raw'][key].append(m.group(2))
            continue
        if key:
            cur['raw'][key].append(line)
    if cur:
        qs.append(cur)
    return qs


def finish(q, diagram_keys, problems):
    raw = q.pop('raw')
    src = q.pop('_src')
    one = lambda k: ' '.join(x.strip() for x in raw[k] if x.strip()).strip()
    q['q'] = one('Q')
    q['short'] = one('SHORT')
    q['deep'] = '\n'.join(raw['DEEP']).strip('\n')
    q['pitfall'] = one('PITFALL') or None
    q['verify'] = one('VERIFY') or None
    follow, cur = [], None
    for line in raw['FOLLOW']:
        if line.startswith('- '):
            cur = line[2:].strip()
            follow.append(cur)
        elif line.strip() and follow:
            follow[-1] += ' ' + line.strip()
    q['follow'] = []
    for f in follow:
        if '=>' not in f:
            problems.append(f'{src} {q["id"]}: FOLLOW item without "=>": {f[:50]}')
            continue
        a, b = f.split('=>', 1)
        q['follow'].append({'q': a.strip(), 'a': b.strip()})
    m = re.fullmatch(r'(\d+)\.(\d\d)', q['id'])
    if not m:
        problems.append(f'{src}: bad id {q["id"]!r}')
        q['mod'] = 0
    else:
        q['mod'] = int(m.group(1))
    if q['level'] not in LEVELS:
        problems.append(f'{src} {q["id"]}: bad level {q["level"]!r}')
    if q['type'] not in TYPES:
        problems.append(f'{src} {q["id"]}: bad type {q["type"]!r}')
    for k in ('q', 'short', 'deep'):
        if not q[k]:
            problems.append(f'{src} {q["id"]}: empty {k}')
    if q['fig'] and diagram_keys is not None and q['fig'] not in diagram_keys:
        problems.append(f'{src} {q["id"]}: unknown fig {q["fig"]!r}')
    if len(q['short']) > 500:
        problems.append(f'{src} {q["id"]}: SHORT is {len(q["short"])} chars (limit 500)')
    return q


def check_only(paths):
    """Validate individual content files without requiring diagrams (used while authoring)."""
    with open(os.path.join(ROOT, 'modules.json'), encoding='utf-8') as f:
        mod_ids = {m['id'] for m in json.load(f)}
    problems, qs = [], []
    for path in paths:
        for q in parse_file(path):
            qs.append(finish(q, None, problems))
    for q in qs:
        if q['mod'] not in mod_ids:
            problems.append(f'{q["id"]}: module {q["mod"]} not in modules.json')
    ids = [q['id'] for q in qs]
    for i in set(ids):
        if ids.count(i) > 1:
            problems.append(f'duplicate id {i}')
    for p in problems:
        print('ERROR ' + p)
    from collections import Counter
    print(f'{len(qs)} questions | levels {dict(Counter(q["level"] for q in qs))} | types {dict(Counter(q["type"] for q in qs))}')
    print('figs used:', sorted({q["fig"] for q in qs if q["fig"]}))
    sys.exit(1 if problems else 0)


def main():
    if len(sys.argv) > 2 and sys.argv[1] == '--check':
        check_only(sys.argv[2:])
    with open(os.path.join(ROOT, 'diagrams.js'), encoding='utf-8') as f:
        diagrams = f.read()
    diagram_keys = set(re.findall(r'DIAGRAMS\.(\w+)\s*=', diagrams))
    with open(os.path.join(ROOT, 'modules.json'), encoding='utf-8') as f:
        modules = json.load(f)
    problems, questions = [], []
    for path in sorted(glob.glob(os.path.join(ROOT, 'content', 'm*.txt'))):
        for q in parse_file(path):
            questions.append(finish(q, diagram_keys, problems))
    ids = [q['id'] for q in questions]
    for i in set(ids):
        if ids.count(i) > 1:
            problems.append(f'duplicate id {i}')
    mod_ids = {m['id'] for m in modules}
    for q in questions:
        if q['mod'] not in mod_ids:
            problems.append(f'{q["id"]}: module {q["mod"]} not in modules.json')
    questions.sort(key=lambda q: (q['mod'], q['id']))
    used = {q['fig'] for q in questions if q['fig']}
    for k in sorted(diagram_keys - used):
        problems.append(f'note: diagram {k!r} defined but never used')

    hard = [p for p in problems if not p.startswith('note:')]
    for p in problems:
        print(('ERROR ' if p in hard else '') + p)
    if hard:
        sys.exit(1)

    data = {'modules': modules, 'questions': questions}
    blob = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    with open(os.path.join(ROOT, 'shell.html'), encoding='utf-8') as f:
        html = f.read()
    html = html.replace('/*__DIAGRAMS__*/', diagrams).replace('/*__DATA__*/', 'var DATA=' + blob + ';')
    out = os.path.join(ROOT, 'out', 'PCIe_QA_Study_Guide.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'\nBuilt {out}  ({os.path.getsize(out) / 1024:.0f} KB)')
    print(f'Questions: {len(questions)}   Modules live: {len({q["mod"] for q in questions})}/{len(modules)}   Diagrams: {len(diagram_keys)}')
    for lv in LEVELS:
        print(f'  {lv:13s}{sum(1 for q in questions if q["level"] == lv)}')
    for ty in TYPES:
        print(f'  {ty:13s}{sum(1 for q in questions if q["type"] == ty)}')
    print('  per module:', {m: sum(1 for q in questions if q["mod"] == m) for m in sorted({q["mod"] for q in questions})})
    print('  flagged verify:', sum(1 for q in questions if q['verify']))
    words = sum(len((q['short'] + ' ' + q['deep']).split()) for q in questions)
    print('  words (short+deep):', words)


main()
