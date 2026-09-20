import json, re, sys
from playwright.sync_api import sync_playwright
html = open('out/PCIe_QA_Study_Guide.html', encoding='utf-8').read()
m = re.search(r'var DATA\s*=\s*(\{.*?\});\s*\n', html, re.S)
ids = re.findall(r'"id":"(\d+\.\d\d)"', html)
ids = sorted(set(ids), key=lambda x: (int(x.split('.')[0]), x))
print(len(ids), 'ids')
bad = []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1280, 'height': 900})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file:///home/claude/pcie/out/PCIe_QA_Study_Guide.html')
    for i in ids:
        pg.evaluate(f"location.hash='#/q/{i}'")
        pg.wait_for_timeout(40)
        # reveal
        try:
            pg.keyboard.press('Space')
        except Exception: pass
        pg.wait_for_timeout(40)
        txt = pg.inner_text('body')
        flags = []
        if '**' in txt: flags.append('raw **')
        if '```' in txt: flags.append('raw fence')
        if '|---' in txt or re.search(r'^\|.*\|$', txt, re.M): flags.append('raw table')
        if re.search(r'^\s*[-]\s', txt, re.M) and False: flags.append('dash')
        if re.search(r'&lt;|&amp;', txt): flags.append('entity')
        if '`' in txt: flags.append('raw backtick')
        if '=>' in txt: flags.append('raw =>')
        if flags: bad.append((i, flags))
    print('page errors:', errs)
    print('flags:', bad)
    b.close()
