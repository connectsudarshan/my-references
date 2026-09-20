# Diagram brief (NVMe and ZNS study pages)

You draw inline SVG figures for a Q&A study page. Each figure is attached to ONE question (`fig=<key>` in the content file). The figure must illustrate exactly what that question teaches and must not contradict any number, name or rule in the question text or its module.

## Tools
- Helper library: `/home/claude/study/dlib.py`. Use it like this (see /home/claude/pcie/gen_diagrams.py for ~22 finished examples of the house style, e.g. `topology`, `tlphdr`, `fc`, `msix`, `pmstates`, `resets`, `nvmeflow`; look at a few):
```python
import sys; sys.path.insert(0, '/home/claude/study')
import dlib
from dlib import rect, text, line, arrow, poly_arrow, svg, add, bracket, fld
b = []
b += [rect(x, y, w, h, 'tl'), text(cx, cy, 'Label', 'h'), arrow(x1, y1, x2, y2, 'lna')]
add('key', 'Figure title', 'One or two sentence caption (plain ASCII, no em dashes).', svg(760, H, 'aria label', ''.join(b)))
dlib.write('/home/claude/<topic>', '<your part file>.js')   # e.g. diagrams_partA.js, at the very end
```
- Canvas is `svg(760, H, ...)` with viewBox width 760 (keep H <= 460). Fonts are monospaced (about 6.3 px per char at class `s`, 5.7 px at `xs`, 7.3 at default): budget text width carefully so nothing clips or overlaps. Wrap long text into several `text()` lines.
- Style classes: boxes `box` (neutral), `tl` (amber), `dl` (blue), `pl` (green), `er` (red); dashed group `grp`; lines `ln` (neutral), `lna` (amber arrow), `lnc` (blue), `lng` (green), `lnr` (red), `lnd` (dashed grey); text classes: default, `s` (small), `xs` (extra small), `h` (bold), `d` (dim), `f` (faint), `ac` (amber), `cy`, `gr`, `rd`. `arrow()` accepts cls in lna/lnc/lnd/lnr/lng/ln. For text anchoring pass a 4th arg 'start' or 'end'.
- Give every text at least 6 px clearance from box edges. Do not place text over lines. Keep at most about 40 text items per figure. Use color to encode meaning (amber = host/software, blue = controller/device, green = OK/media, red = error/problem) consistently and say so in the caption when it is not obvious.
- Do not use backticks inside SVG strings.

## Workflow
1. Read the assigned question(s) in full (`grep -n "^@@ .*fig=KEY" /home/claude/<topic>/content/m*.txt`, then read that question block) plus the module's neighboring questions for context, so the picture matches the text.
2. Write ONE generator file `/home/claude/<topic>/diag_<part>.py` that adds your figures and writes `/home/claude/<topic>/diagrams_<part>.js` (via `dlib.write(root, name)`).
3. Run it, then render: `python3 /home/claude/study/figpreview.py /home/claude/<topic> diagrams_<part>.js` and LOOK at every PNG in `/home/claude/<topic>/out/figs/` with the Read tool. Fix clipping, overlaps, misalignment, unreadable text, wrong facts. Re-render until clean. Look at each figure at least twice (once after the first draft, once after fixes).
4. Report (under 100 words): file names, figure keys done, anything in the question text that looks wrong or inconsistent with what you drew (do not edit content files).

Use real spec/driver facts only as stated in the question text; when the question says VERIFY, keep the figure generic on that detail rather than inventing specifics.
