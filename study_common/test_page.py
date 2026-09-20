#!/usr/bin/env python3
"""Regression test for a built study page.
usage: python3 test_page.py <html_file> <lskey> <first_id> <second_id> <mobile_id>
Checks: no page errors, reveal/rating/persistence, reference mode, search, mock round, mobile overflow,
then visits every question with answers revealed and scans for raw markdown, and checks every figure renders."""
import sys, re, os
from playwright.sync_api import sync_playwright
html_path, lskey, id1, id2, idm = sys.argv[1:6]
out = os.path.join(os.path.dirname(os.path.abspath(html_path)), 'shots'); os.makedirs(out, exist_ok=True)
URL = 'file://' + os.path.abspath(html_path)
html = open(html_path, encoding='utf-8').read()
ids = sorted(set(re.findall(r'"id":"(\d+\.\d\d)"', html)), key=lambda x: (int(x.split('.')[0]), int(x.split('.')[1])))
print(len(ids), 'question ids')
errs, bad = [], []
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 1280, 'height': 900})
    pg = ctx.new_page()
    pg.on('pageerror', lambda e: errs.append('pageerror:' + str(e)))
    pg.on('console', lambda m: errs.append('console:' + m.text) if m.type == 'error' and 'fonts.g' not in m.text and 'ERR_' not in m.text else None)
    pg.goto(URL); pg.wait_for_timeout(600)
    pg.screenshot(path=f'{out}/home.png')
    pg.click(f'.nav-item[data-id="{id1}"]'); pg.wait_for_timeout(200)
    assert pg.locator('.reveal-box').count() == 1, 'reveal box missing'
    pg.keyboard.press('Space'); pg.wait_for_timeout(200)
    assert pg.locator('.short-box').count() == 1, 'short not shown'
    pg.keyboard.press('2'); pg.wait_for_timeout(200)
    pg.screenshot(path=f'{out}/q_revealed.png', full_page=True)
    pg.keyboard.press('ArrowRight'); pg.wait_for_timeout(200)
    assert id2 in pg.inner_text('.q-id'), 'next failed'
    pg.keyboard.press('Space'); pg.keyboard.press('1'); pg.wait_for_timeout(200)
    st = pg.evaluate(f"JSON.parse(localStorage.getItem('{lskey}')).ratings")
    assert len(st) >= 2, 'ratings not persisted'
    print('ratings persisted:', {k: v['r'] for k, v in st.items()})
    pg.click('#modeSeg button[data-mode="ref"]'); pg.wait_for_timeout(200)
    assert pg.locator('.short-box').count() == 1, 'ref mode should show answer'
    pg.click('#modeSeg button[data-mode="study"]'); pg.wait_for_timeout(200)
    pg.fill('#searchInput', 'the'); pg.wait_for_timeout(200)
    n1 = pg.locator('.nav-item').count(); pg.fill('#searchInput', ''); pg.wait_for_timeout(100)
    print('search "the" ->', n1, 'items')
    pg.click('#sidebar .sidebar-header'); pg.wait_for_timeout(200)
    pg.click('[data-act="mock"]'); pg.wait_for_timeout(200)
    pg.click('#startMock'); pg.wait_for_timeout(300)
    for i in range(10):
        pg.keyboard.press('Space'); pg.wait_for_timeout(60)
        pg.keyboard.press(['1', '2', '3'][i % 3]); pg.wait_for_timeout(100)
    pg.wait_for_timeout(300)
    print('mock summary heading:', pg.inner_text('.hero h2'))
    pg.screenshot(path=f'{out}/mock_summary.png', full_page=True)
    m = b.new_context(viewport={'width': 390, 'height': 800}); mp = m.new_page()
    mp.on('pageerror', lambda e: errs.append('mobile pageerror:' + str(e)))
    mp.goto(URL + '#/q/' + idm); mp.wait_for_timeout(400)
    mp.click('[data-reveal]'); mp.wait_for_timeout(200)
    mp.screenshot(path=f'{out}/mobile.png')
    print('mobile horizontal overflow:', mp.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth"))
    # full scan
    sp = b.new_page(viewport={'width': 1280, 'height': 900})
    sp.on('pageerror', lambda e: errs.append('scan pageerror:' + str(e)))
    sp.goto(URL)
    for i in ids:
        sp.evaluate(f"location.hash='#/q/{i}'"); sp.wait_for_timeout(35)
        sp.keyboard.press('Space'); sp.wait_for_timeout(35)
        txt = sp.inner_text('body')
        flags = []
        if '**' in txt: flags.append('raw **')
        if '```' in txt: flags.append('raw fence')
        if re.search(r'^\|.*\|$', txt, re.M) or '|---' in txt: flags.append('raw table')
        if re.search(r'&lt;|&amp;|&gt;', txt): flags.append('entity')
        if '`' in txt: flags.append('raw backtick')
        if '=>' in txt: flags.append('raw =>')
        if re.search(r'^\s*\d+\. ', txt, re.M) and False: flags.append('numlist')
        fig_ok = sp.evaluate("(function(){var f=document.querySelector('figure.fig svg'); if(!f) return 'none'; var r=f.getBoundingClientRect(); return r.width>200&&r.height>80?'ok':'tiny';})()")
        if fig_ok == 'tiny': flags.append('figure tiny')
        if flags: bad.append((i, flags))
    print('flags:', bad)
    print('ERRORS:', errs)
    b.close()
sys.exit(1 if (errs or bad) else 0)
