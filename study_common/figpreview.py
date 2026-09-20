#!/usr/bin/env python3
"""Render every diagram in a diagrams JS file to PNG for visual QA.
usage: python3 figpreview.py <topic_dir> <diagrams_js_filename> [key ...]
PNGs go to <topic_dir>/out/figs/<key>.png ; view them with the Read tool."""
import re, sys, os
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
topic, jsname = os.path.abspath(sys.argv[1]), sys.argv[2]
only = sys.argv[3:]
css = re.search(r'<style>(.*?)</style>', open(os.path.join(HERE, 'shell.html'), encoding='utf-8').read(), re.S).group(1)
# same CSS variables as the app
js = open(os.path.join(topic, jsname), encoding='utf-8').read()
os.makedirs(os.path.join(topic, 'out', 'figs'), exist_ok=True)
page = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{css}
body{{background:#0e2036;padding:20px;width:940px;display:block;height:auto;overflow:visible}} .fig{{margin-bottom:24px}}</style></head><body><div id="root"></div>
<script>{js}
var r=document.getElementById('root');
Object.keys(DIAGRAMS).forEach(function(k){{var d=DIAGRAMS[k];var f=document.createElement('figure');f.className='fig';f.id='fig-'+k;
f.innerHTML='<div class="fig-title">FIG · '+d.title.toUpperCase()+'</div>'+d.svg+'<figcaption>'+d.cap+'</figcaption>';r.appendChild(f);}});
</script></body></html>"""
p = os.path.join(topic, 'out', 'figs_preview.html')
open(p, 'w', encoding='utf-8').write(page)
with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={'width': 1000, 'height': 900})
    pg.goto('file://' + p)
    pg.wait_for_timeout(300)
    keys = pg.evaluate("Object.keys(DIAGRAMS)")
    for k in keys:
        if only and k not in only:
            continue
        pg.locator('#fig-' + k).screenshot(path=os.path.join(topic, 'out', 'figs', k + '.png'))
        print('rendered', k)
    b.close()
