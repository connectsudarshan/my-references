#!/usr/bin/env python3
"""Generates diagrams.js (inline SVG figures) for the PCIe Q&A page."""
import math, os, html

ROOT = os.path.dirname(os.path.abspath(__file__))
out = []


def e(s):
    return html.escape(str(s), quote=False)


def rect(x, y, w, h, cls='box', rx=6, extra=''):
    return f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" {extra}/>'


def text(x, y, s, cls='', anchor='middle'):
    a = '' if anchor == 'middle' else f' text-anchor="{anchor}"'
    return f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor if anchor != "middle" else "middle"}">{e(s)}</text>'


def line(x1, y1, x2, y2, cls='ln'):
    return f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>'


def head(x, y, ux, uy, hc):
    px, py = -uy, ux
    bx, by = x - ux * 9, y - uy * 9
    return f'<polygon class="{hc}" points="{x:.1f},{y:.1f} {bx + px * 4.5:.1f},{by + py * 4.5:.1f} {bx - px * 4.5:.1f},{by - py * 4.5:.1f}"/>'


HC = {'lna': 'ah', 'lnc': 'ahc', 'lnd': 'ahd', 'lnr': 'ahr', 'lng': 'ah', 'ln': 'ahd'}


def arrow(x1, y1, x2, y2, cls='lna'):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    bx, by = x2 - ux * 8, y2 - uy * 8
    return (f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{bx:.1f}" y2="{by:.1f}"/>' + head(x2, y2, ux, uy, HC[cls]))


def poly_arrow(pts, cls='lna'):
    """polyline with arrowhead on the last segment"""
    (xa, ya), (xb, yb) = pts[-2], pts[-1]
    dx, dy = xb - xa, yb - ya
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    bx, by = xb - ux * 8, yb - uy * 8
    body = ' '.join(f'{x},{y}' for x, y in pts[:-1]) + f' {bx:.1f},{by:.1f}'
    return f'<polyline class="{cls}" points="{body}"/>' + head(xb, yb, ux, uy, HC[cls])


def svg(w, h, label, body):
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{e(label)}"><title>{e(label)}</title>{body}</svg>'


def add(key, title, cap, svgstr):
    assert '`' not in svgstr
    out.append(f'DIAGRAMS.{key}={{title:{title!r},cap:{cap!r},svg:`{svgstr}`}};')


# ---------------------------------------------------------------- topology
b = []
b += [rect(280, 8, 200, 36), text(380, 31, 'CPU + Memory', 'h'), line(380, 44, 380, 66)]
b += [rect(230, 66, 300, 74, 'tl'), text(380, 86, 'Root Complex (RC)', 'h')]
b += [rect(250, 104, 110, 28), text(305, 122, 'Root Port A', 's'), rect(400, 104, 110, 28), text(455, 122, 'Root Port B', 's')]
b += [poly_arrow([(305, 132), (305, 190), (130, 190), (130, 248)], 'lna'), text(218, 183, 'x4 · Gen4', 's d')]
b += [rect(60, 250, 140, 52, 'dl'), text(130, 273, 'Endpoint', 'h'), text(130, 290, 'NVMe SSD', 's d')]
b += [line(455, 132, 455, 190, 'lna'), text(470, 165, 'x8', 's d', 'start')]
b += [rect(380, 190, 150, 52, 'pl'), text(455, 212, 'Switch', 'h'), text(455, 229, 'upstream port on top', 'xs d')]
b += [line(455, 242, 455, 272), line(390, 272, 670, 272)]
for cx, nm in [(390, 'NIC'), (530, 'GPU'), (670, 'NVMe SSD')]:
    b += [line(cx, 272, cx, 320), rect(cx - 60, 320, 120, 52, 'dl'), text(cx, 343, 'Endpoint', 'h'), text(cx, 360, nm, 's d')]
b += [text(560, 264, 'downstream ports', 'xs d')]
b += [text(20, 26, 'Every link is point-to-point.', 's d', 'start'), text(20, 42, 'xN = lanes in that link.', 's d', 'start')]
b += [text(20, 392, 'A strict tree: every endpoint has exactly one path back to the Root Complex.', 's d', 'start')]
add('topology', 'PCIe topology', 'Root Complex at the top, an endpoint on one Root Port, a switch with three endpoints on the other. Routing is simple because every device has exactly one path to the root.',
    svg(760, 400, 'PCIe tree topology', ''.join(b)))

# ---------------------------------------------------------------- lane
b = [rect(20, 20, 150, 210), text(95, 46, 'Device A', 'h'), text(95, 64, 'e.g. Root Port', 's d'),
     rect(590, 20, 150, 210), text(665, 46, 'Device B', 'h'), text(665, 64, 'e.g. NVMe SSD', 's d')]
for i in range(4):
    y0 = 92 + i * 34
    b += [text(380, y0 - 5, f'Lane {i}', 'xs d'), arrow(170, y0, 590, y0, 'lna'), arrow(590, y0 + 12, 170, y0 + 12, 'lnc')]
b += [line(20, 252, 46, 252, 'lna'), text(54, 256, 'TX pair of A = RX pair of B', 's', 'start')]
b += [line(20, 274, 46, 274, 'lnc'), text(54, 278, 'TX pair of B = RX pair of A', 's', 'start')]
b += [text(740, 256, 'One lane = 2 differential pairs = 4 wires', 's d', 'end'), text(740, 278, 'An x4 link = 4 lanes = 16 signal wires', 's d', 'end')]
add('lane', 'Lanes and links', 'Each lane carries one transmit pair and one receive pair, so both directions run at full speed at the same time. Link width is the number of lanes bonded together.',
    svg(760, 296, 'Lane and link wiring for an x4 link', ''.join(b)))

# ---------------------------------------------------------------- gens
b = [text(20, 22, 'GEN', 'xs f', 'start'), text(70, 22, 'PER-LANE RATE', 'xs f', 'start'), text(340, 22, 'GT/S', 'xs f', 'start'),
     text(410, 22, 'ENCODING', 'xs f', 'start'), text(555, 22, 'x4 GB/S', 'xs f', 'start'), text(650, 22, 'x16 GB/S', 'xs f', 'start')]
rows = [('Gen1', 2.5, '8b/10b', '1.0', '4.0'), ('Gen2', 5, '8b/10b', '2.0', '8.0'), ('Gen3', 8, '128b/130b', '3.94', '15.75'),
        ('Gen4', 16, '128b/130b', '7.88', '31.5'), ('Gen5', 32, '128b/130b', '15.75', '63.0'), ('Gen6', 64, 'PAM4 + FLIT', '~32*', '~128*')]
for i, (g, r, enc, x4, x16) in enumerate(rows):
    y = 38 + i * 44
    b += [text(20, y + 20, g, 'h', 'start'), rect(70, y + 5, max(4, r / 64 * 250), 22, 'pl' if g == 'Gen6' else 'tl', 3),
          text(340, y + 21, str(r), '', 'start'), text(410, y + 21, enc, 'd', 'start'), text(555, y + 21, x4, 'ac h', 'start'), text(650, y + 21, x16, 'ac h', 'start')]
b += [text(20, 320, '* Gen6 is shown raw: FLIT framing and FEC take a few percent of the raw rate.', 'xs d', 'start'), text(20, 334, 'All figures are per direction and before TLP/DLLP protocol overhead.', 'xs d', 'start')]
add('gens', 'Generations at a glance', 'The per-lane rate doubles every generation. GB/s figures include encoding overhead but not protocol overhead.',
    svg(760, 342, 'PCIe generations, encodings and bandwidth', ''.join(b)))

# ---------------------------------------------------------------- stack
b = []
for x in (30, 510):
    b += [rect(x, 16, 220, 44), text(x + 110, 43, 'Device core / NVMe controller', 's')]
    b += [rect(x, 88, 220, 64, 'tl'), text(x + 110, 113, 'Transaction Layer', 'h'), text(x + 110, 133, 'TLPs · flow control · ordering', 's d')]
    b += [rect(x, 172, 220, 64, 'dl'), text(x + 110, 197, 'Data Link Layer', 'h'), text(x + 110, 217, 'seq# · LCRC · ACK/NAK · replay', 's d')]
    b += [rect(x, 256, 220, 64, 'pl'), text(x + 110, 281, 'Physical Layer', 'h'), text(x + 110, 301, 'framing · SerDes · LTSSM', 's d')]
    for (y1, y2) in ((60, 88), (152, 172), (236, 256)):
        b += [arrow(x + 50, y1, x + 50, y2, 'lna'), arrow(x + 170, y2, x + 170, y1, 'lnc')]
b += [text(380, 112, 'TLP: end-to-end meaning', 's ac'), line(250, 120, 510, 120, 'lnd')]
b += [text(380, 196, 'DLLP, seq#, LCRC: one hop only', 's cy'), line(250, 204, 510, 204, 'lnd')]
b += [text(380, 262, 'serial lanes: symbols, ordered sets', 's gr'), arrow(250, 276, 510, 276, 'lna'), arrow(510, 294, 250, 294, 'lnc')]
b += [text(380, 352, 'Send: down the stack. Receive: up the stack. Each layer talks to its peer through the layers below it.', 's d')]
add('stack', 'Three layers, two devices', 'Amber arrows go down on the sender, cyan arrows go up on the receiver. Dashed lines are logical conversations between peer layers; only the Physical Layer touches the wire.',
    svg(760, 372, 'Layer stack of two PCIe devices', ''.join(b)))

# ---------------------------------------------------------------- encap
segs = [('STP', 'framing', 62, 'pl'), ('Seq#', '2 B', 62, 'dl'), ('Header', '12 or 16 B', 120, 'tl'), ('Data payload', '0 to 4096 B', 190, 'tl'),
        ('ECRC', '4 B, opt.', 62, 'tl'), ('LCRC', '4 B', 66, 'dl'), ('END', 'framing', 58, 'pl')]
x = 50
b = []
pos = []
for nm, sub, w, cls in segs:
    b += [rect(x, 40, w, 60, cls, 3), text(x + w / 2, 66, nm, 's h'), text(x + w / 2, 84, sub, 'xs d')]
    pos.append((x, w))
    x += w


def bracket(x1, x2, y, label, cls):
    return [line(x1, y, x2, y, 'ln'), line(x1, y - 6, x1, y, 'ln'), line(x2, y - 6, x2, y, 'ln'), text((x1 + x2) / 2, y + 20, label, 's ' + cls)]


b += bracket(pos[2][0], pos[4][0] + pos[4][1], 122, 'Transaction Layer: the TLP (header, payload, optional ECRC), not modified hop by hop', 'ac')
b += bracket(pos[1][0], pos[5][0] + pos[5][1], 170, 'Data Link Layer: adds Seq# and LCRC, regenerated on every hop', 'cy')
b += bracket(pos[0][0], pos[6][0] + pos[6][1], 218, 'Physical Layer: framing (STP/END; 128b/130b uses length tokens) plus encoding and scrambling', 'gr')
b += [text(50, 282, 'ECRC is optional and end-to-end. LCRC is mandatory and per link.', 's d', 'start')]
add('encap', 'A TLP on the wire', 'Who adds what: the Transaction Layer builds the TLP, the Data Link Layer wraps it with a sequence number and LCRC, and the Physical Layer frames it.',
    svg(760, 296, 'TLP encapsulation across the three layers', ''.join(b)))

# ---------------------------------------------------------------- pam4
b = [text(190, 26, 'NRZ (Gen1-5): 2 levels, 1 bit per symbol', 's h'), text(570, 26, 'PAM4 (Gen6): 4 levels, 2 bits per symbol', 's h'), line(380, 40, 380, 280, 'lnd')]
for y, lab in ((70, '1'), (230, '0')):
    b += [line(60, y, 320, y, 'lnd'), text(46, y + 4, lab, 's d', 'end')]
b += ['<polygon class="pl" points="100,150 130,74 250,74 280,150 250,226 130,226"/>', text(190, 146, 'one wide eye', 's'), text(190, 163, 'full swing', 's d')]
b += [text(190, 262, 'eye height = 1 x swing', 's gr')]
for y, lab in ((70, '11'), (123, '10'), (177, '01'), (230, '00')):
    b += [line(440, y, 700, y, 'lnd'), text(426, y + 4, lab, 's d', 'end')]
for cy in (96.5, 150, 203.5):
    b += [f'<polygon class="er" points="500,{cy} 530,{cy - 22} 610,{cy - 22} 640,{cy} 610,{cy + 22} 530,{cy + 22}"/>']
b += [text(570, 262, 'three eyes, each 1/3 of the swing = about -9.5 dB SNR', 's rd')]
add('pam4', 'NRZ versus PAM4', 'Same symbol rate as Gen5, twice the bits per symbol, but each eye is a third as tall. That lost margin is why Gen6 makes FEC mandatory.',
    svg(760, 284, 'NRZ and PAM4 eye diagrams compared', ''.join(b)))

# ---------------------------------------------------------------- ltssm
b = [rect(20, 40, 110, 50, 'dl'), text(75, 70, 'Detect', 'h'), rect(190, 40, 110, 50, 'dl'), text(245, 70, 'Polling', 'h'),
     rect(360, 40, 130, 50, 'dl'), text(425, 70, 'Configuration', 'h'), rect(550, 40, 110, 50, 'tl'), text(605, 70, 'L0', 'h lg'),
     rect(760, 40, 100, 50, 'pl'), text(810, 70, 'L0s', 'h'),
     rect(550, 200, 110, 50, 'er'), text(605, 230, 'Recovery', 'h'), rect(760, 200, 100, 50, 'pl'), text(810, 230, 'L1', 'h'),
     rect(20, 360, 110, 50), text(75, 390, 'Disabled', 'h'), rect(190, 360, 110, 50), text(245, 390, 'Loopback', 'h'),
     rect(360, 360, 130, 50), text(425, 390, 'Hot Reset', 'h'), rect(760, 360, 100, 50, 'pl'), text(810, 390, 'L2', 'h')]
b += [text(75, 30, 'receiver detect', 'xs d'), text(245, 30, 'bit/symbol lock, TS1/TS2', 'xs d'), text(425, 30, 'link #, lane #, width', 'xs d'), text(605, 30, 'normal operation', 'xs d'), text(810, 30, 'quick idle', 'xs d')]
b += [arrow(130, 65, 190, 65), arrow(300, 65, 360, 65), arrow(490, 65, 550, 65)]
b += [arrow(660, 55, 760, 55), arrow(760, 76, 660, 76)]
b += [arrow(580, 90, 580, 200), arrow(630, 200, 630, 90)]
b += [text(570, 150, 'errors, speed or', 'xs d', 'end'), text(570, 163, 'width change, L1 exit', 'xs d', 'end')]
b += [poly_arrow([(550, 225), (425, 225), (425, 90)], 'lnd'), text(432, 200, 'width change', 'xs d', 'start')]
b += [poly_arrow([(580, 250), (580, 320), (75, 320), (75, 90)], 'lnd')]
for xx in (75, 245, 425):
    pass
b += [arrow(75, 320, 75, 360, 'lnd'), arrow(245, 320, 245, 360, 'lnd'), arrow(425, 320, 425, 360, 'lnd')]
b += [text(100, 312, 'timeout: back to Detect.  Or directed: Disabled, Loopback, Hot Reset', 'xs d', 'start')]
b += [poly_arrow([(660, 88), (710, 88), (710, 385), (760, 385)], 'lng'), arrow(710, 225, 760, 225, 'lng')]
b += [arrow(760, 208, 660, 208, 'lnc')]
b += [text(810, 428, 'aux power, beacon/WAKE#', 'xs d')]
b += [text(20, 436, 'amber = normal path  |  dashed = fallback or directed  |  green = low-power entry from L0  |  cyan = L1 exit via Recovery', 'xs d', 'start')]
add('ltssm', 'LTSSM overview', 'The link comes up Detect, Polling, Configuration, L0. Recovery is the hub for retraining, and low-power states leave through it (L1) or directly (L0s).',
    svg(880, 446, 'LTSSM state diagram', ''.join(b)))

# ---------------------------------------------------------------- recovery
b = [rect(20, 132, 90, 46, 'tl'), text(65, 160, 'L0', 'h lg'), rect(150, 60, 520, 250, 'grp'), text(162, 82, 'Recovery', 's h ac', 'start')]
b += [rect(170, 130, 130, 50, 'er'), text(235, 160, 'RcvrLock', 'h'), rect(350, 130, 130, 50, 'er'), text(415, 160, 'RcvrCfg', 'h'),
      rect(530, 130, 120, 50, 'er'), text(590, 160, 'Idle', 'h'),
      rect(170, 230, 130, 50), text(235, 260, 'Equalization', 'h'), rect(350, 230, 130, 50), text(415, 260, 'Speed', 'h')]
b += [arrow(110, 155, 170, 155), arrow(300, 155, 350, 155), arrow(480, 155, 530, 155)]
b += [poly_arrow([(590, 130), (590, 100), (65, 100), (65, 132)], 'lna'), text(330, 94, 'both sides see idle: back to L0', 'xs d')]
b += [arrow(215, 180, 215, 230), arrow(255, 230, 255, 180, 'lnc'), text(268, 210, 'EQ needed', 'xs d', 'start')]
b += [arrow(400, 180, 400, 230), text(410, 210, 'speed change', 'xs d', 'start')]
b += [poly_arrow([(350, 250), (325, 250), (325, 168), (300, 168)], 'lnc')]
b += [rect(715, 108, 100, 44, 'dl'), text(765, 135, 'Configuration', 's h'), arrow(670, 130, 715, 130, 'lnd'), text(765, 168, 'lane / width change', 'xs d')]
b += [rect(715, 200, 100, 44, 'dl'), text(765, 227, 'Detect', 's h'), arrow(670, 222, 715, 222, 'lnd'), text(765, 260, 'timeout, lost link', 'xs d')]
b += [text(20, 328, 'RcvrLock: bit/symbol lock and TS1 exchange.  RcvrCfg: TS2 exchange, agree speed and lane config.  Idle: idle data, then L0.', 'xs d', 'start')]
add('recovery', 'Inside Recovery', 'Recovery is a small state machine of its own. Speed changes go RcvrCfg to Speed and back to RcvrLock at the new rate; equalization (Gen3+) branches off RcvrLock.',
    svg(830, 342, 'LTSSM Recovery sub-states', ''.join(b)))

# ---------------------------------------------------------------- eq chain
b = []
blocks = [(20, 130, 'tl', 'TX FIR', 'pre · main · post'), (185, 130, 'box', 'Channel', 'loss · reflections'), (350, 120, 'pl', 'RX CTLE', 'analog boost'),
          (505, 110, 'pl', 'RX DFE', 'removes ISI'), (650, 100, 'dl', 'CDR + slicer', 'clock + decision')]
for x, w, cls, nm, sub in blocks:
    b += [rect(x, 30, w, 56, cls), text(x + w / 2, 55, nm, 'h'), text(x + w / 2, 73, sub, 'xs d')]
for xa, xb in ((150, 185), (315, 350), (470, 505), (615, 650)):
    b += [arrow(xa, 58, xb, 58)]
plots = [(20, 150, 'M28,190 Q90,186 145,130', 'lna', 'boosts highs'), (185, 315, 'M193,130 Q250,186 310,196', 'lnr', 'loses highs'),
         (350, 470, 'M358,190 Q420,186 465,136', 'lng', 'peaks at highs')]
for x0, x1, d, cls, lab in plots:
    b += [line(x0, 200, x1, 200), line(x0, 116, x0, 200), f'<path class="{cls}" d="{d}"/>', text(x1, 214, 'freq', 'xs f', 'end'), text((x0 + x1) / 2, 236, lab, 'xs d')]
b += [line(505, 200, 745, 200), line(505, 116, 505, 200), '<path class="lng" d="M513,160 L740,160"/>', text(745, 214, 'freq', 'xs f', 'end'), text(625, 236, 'goal: flat up to Nyquist', 'xs d')]
b += [text(20, 274, 'The channel steals high frequencies. TX FIR and the CTLE give them back,', 's d', 'start'), text(20, 290, 'and the DFE removes the inter-symbol interference that remains.', 's d', 'start')]
add('eq', 'The equalization chain', 'Three tools fight one problem. TX equalization and the CTLE reshape the frequency response; the DFE cleans up inter-symbol interference after the slicer decision.',
    svg(760, 304, 'TX and RX equalization chain with frequency responses', ''.join(b)))

# ---------------------------------------------------------------- eq phases
b = [text(150, 20, 'Downstream Port (DSP)', 's h'), text(610, 20, 'Upstream Port (USP)', 's h'), line(150, 34, 150, 392), line(610, 34, 610, 392)]
for i in range(4):
    if i % 2 == 0:
        b += [f'<rect x="20" y="{44 + i * 84}" width="720" height="84" style="fill:rgba(255,255,255,.03);stroke:none"/>']
b += [text(30, 66, 'PHASE 0', 's h ac', 'start'), text(30, 82, 'at 2.5/5 GT/s', 'xs d', 'start'), arrow(150, 100, 610, 100, 'lna'), text(380, 92, 'EQ TS2: preset for USP TX + Rx hint', 's'), text(380, 120, 'agreed before the speed change to 8 GT/s or faster', 'xs d')]
b += [text(30, 150, 'PHASE 1', 's h ac', 'start'), text(30, 166, 'new data rate', 'xs d', 'start'), arrow(150, 150, 610, 150, 'lna'), arrow(610, 174, 150, 174, 'lnc'),
      text(380, 143, 'TS1: preset · FS · LF (DSP to USP)', 's'), text(380, 167, 'TS1: preset · FS · LF (USP to DSP)', 's'), text(380, 198, 'bit lock, symbol lock, block alignment: does the link work at all?', 'xs d')]
b += [text(30, 234, 'PHASE 2', 's h ac', 'start'), text(30, 250, 'USP tunes DSP', 'xs d', 'start'), arrow(610, 246, 150, 246, 'lnc'), text(380, 238, 'USP asks: change your TX coefficients', 's'),
      text(380, 268, 'USP measures its receiver and iterates until satisfied', 'xs d')]
b += [text(30, 318, 'PHASE 3', 's h ac', 'start'), text(30, 334, 'DSP tunes USP', 'xs d', 'start'), arrow(150, 330, 610, 330, 'lna'), text(380, 322, 'DSP asks: change your TX coefficients', 's'),
      text(380, 352, 'DSP measures its receiver and iterates until satisfied', 'xs d')]
add('eqphases', 'Gen3+ link equalization phases', 'Each side ends up with a TX setting chosen by its partner, based on what the partner actually sees at its receiver.',
    svg(760, 400, 'Four phases of link equalization between downstream and upstream port', ''.join(b)))

# ---------------------------------------------------------------- replay
b = [text(170, 20, 'Sender (TX)', 's h'), text(590, 20, 'Receiver (RX)', 's h'), line(170, 32, 170, 372), line(590, 32, 590, 372)]
sends = [(60, 'TLP #41'), (100, 'TLP #42'), (140, 'TLP #43'), (180, 'TLP #44')]
for y, lab in sends:
    b += [arrow(170, y, 590, y + 20, 'lna'), text(380, y + 4, lab, 's')]
b += [line(566, 152, 578, 164, 'lnr'), line(578, 152, 566, 164, 'lnr')]
b += [arrow(590, 216, 170, 236, 'lnr'), text(380, 220, 'NAK (seq 42)', 's rd')]
b += [arrow(170, 268, 590, 288, 'lna'), text(380, 272, 'replay #43', 's'), arrow(170, 296, 590, 316, 'lna'), text(380, 300, 'replay #44', 's')]
b += [arrow(590, 334, 170, 354, 'lnc'), text(380, 338, 'ACK 44', 's cy')]
L = [(70, 'buffer: 41'), (110, 'buffer: 41,42'), (150, '+43'), (190, '+44'), (236, 'NAK 42: purge to 42'), (250, 'keep 43,44'), (354, 'ACK 44: buffer empty')]
for y, t in L:
    b += [text(6, y, t, 'xs d', 'start')]
R = [(160, 'LCRC bad: drop, NAK'), (206, '#44 out of seq: drop'), (300, '#43, #44 in order: accept')]
for y, t in R:
    b += [text(602, y, t, 'xs d', 'start')]
add('replay', 'ACK/NAK and replay', 'Cumulative ACKs free the replay buffer. A NAK acknowledges everything up to its sequence number and asks for the rest to be re-sent in order (go-back-N).',
    svg(760, 384, 'ACK NAK replay sequence between sender and receiver', ''.join(b)))

# ---------------------------------------------------------------- dllp
b = []
x = 135
for nm, sub, w, cls in [('SDP', 'start', 70, 'pl'), ('Type', '1 B', 90, 'dl'), ('Payload', '3 B', 150, 'dl'), ('CRC-16', '2 B', 110, 'dl'), ('END', 'end', 70, 'pl')]:
    b += [rect(x, 30, w, 50, cls, 3), text(x + w / 2, 53, nm, 's h'), text(x + w / 2, 69, sub, 'xs d')]
    x += w
b += [text(20, 118, 'DLLP KIND', 'xs f', 'start'), text(210, 118, 'TYPE BYTE', 'xs f', 'start'), text(400, 118, 'PAYLOAD (BYTES 1-3)', 'xs f', 'start')]
rows = [('Ack', '0000 0000', 'AckNak_Seq_Num (12 bits)'), ('Nak', '0001 0000', 'AckNak_Seq_Num (12 bits)'),
        ('InitFC1/2, UpdateFC', 'kind in high bits, VC in low 3', 'HdrFC (8 bits), DataFC (12 bits)'), ('PM_Enter_L1 / L23 / Request_Ack', '0010 0xxx', 'no payload')]
for i, (a, t, p) in enumerate(rows):
    y = 140 + i * 20
    b += [text(20, y, a, 'xs', 'start'), text(210, y, t, 'xs d', 'start'), text(400, y, p, 'xs d', 'start')]
add('dllp', 'DLLP format', 'A DLLP is six bytes plus framing: one type byte, three payload bytes, and a 16-bit CRC. DLLPs are not sequence-numbered and never leave the link.',
    svg(760, 236, 'Data Link Layer Packet format', ''.join(b)))


# ================================================================ PHASE 2 DIAGRAMS
# ---------------------------------------------------------------- tlphdr
UB = 20  # px per bit
X0 = 96
def fld(row_y, hi, lo, label, cls='dl', sub=None):
    x = X0 + (31 - hi) * UB
    w = (hi - lo + 1) * UB
    s = [rect(x, row_y, w, 40, cls, 2)]
    if w >= 60:
        s += [text(x + w / 2, row_y + 19, label, 's h'), text(x + w / 2, row_y + 33, sub or f'[{hi}:{lo}]' if hi != lo else (sub or f'[{hi}]'), 'xs d')]
    elif w >= 40:
        s += [text(x + w / 2, row_y + 19, label, 's h'), text(x + w / 2, row_y + 33, sub or f'[{hi}:{lo}]', 'xs d')]
    else:
        s += [text(x + w / 2, row_y + 24, label, 'xs h')]
    return s
b = []
for k in (31, 24, 16, 8, 0):
    b += [text(X0 + (31 - k) * UB + (UB / 2 if k in (0,) else UB / 2), 16, str(k), 'xs f')]
rows = [
    ('DW0', [(31, 29, 'Fmt', 'tl'), (28, 24, 'Type', 'tl'), (23, 23, 'R*', 'box'), (22, 20, 'TC', 'dl'), (19, 19, 'R*', 'box'), (18, 18, 'At', 'dl'),
             (17, 17, 'R*', 'box'), (16, 16, 'TH', 'dl'), (15, 15, 'TD', 'dl'), (14, 14, 'EP', 'er'), (13, 12, 'Attr', 'dl'), (11, 10, 'AT', 'dl'), (9, 0, 'Length (DW)', 'pl')]),
    ('DW1', [(31, 16, 'Requester ID', 'dl'), (15, 8, 'Tag', 'dl'), (7, 4, 'Last BE', 'pl'), (3, 0, '1st BE', 'pl')]),
    ('DW2', [(31, 0, 'Address [63:32]  (4DW header only)', 'tl')]),
    ('DW3', [(31, 2, 'Address [31:2]', 'tl'), (1, 0, 'PH', 'box')]),
]
for i, (nm, fl) in enumerate(rows):
    y = 26 + i * 52
    b += [text(X0 - 12, y + 24, nm, 's h', 'end')]
    for hi, lo, lab, cls in fl:
        b += fld(y, hi, lo, lab, cls)
b += [text(20, 246, 'Fmt: 000 = 3DW no data, 001 = 4DW no data, 010 = 3DW with data, 011 = 4DW with data.', 'xs d', 'start'),
      text(20, 262, 'Length 0 encodes 1024 DW.  3DW request: address [31:2] is in DW2 and there is no DW3.', 'xs d', 'start'),
      text(20, 278, 'Completions reuse DW1/DW2 for Completer ID, Status, Byte Count and Lower Address.', 'xs d', 'start'),
      text(20, 294, '* Reserved, or extended-tag / LN bits, depending on the spec revision.  At = Attr[2].  PH = processing hint (TH set).', 'xs d', 'start')]
add('tlphdr', 'Memory request TLP header (4DW)', 'DW0 is common to every TLP. In a memory request DW1 identifies the requester and its tag and carries the byte enables, and DW2/DW3 hold the 64-bit address.',
    svg(760, 304, 'Bit map of a four-DW memory request TLP header', ''.join(b)))

# ---------------------------------------------------------------- fc
b = [rect(20, 20, 250, 250, 'box'), text(145, 44, 'Transmitter', 's h'), text(145, 60, 'Transaction Layer', 'xs d')]
b += [rect(40, 76, 210, 48, 'tl'), text(145, 96, 'CREDITS_CONSUMED', 's h'), text(145, 112, 'total credits used so far', 'xs d')]
b += [rect(40, 134, 210, 48, 'dl'), text(145, 154, 'CREDIT_LIMIT', 's h'), text(145, 170, 'latest total granted', 'xs d')]
b += [rect(40, 198, 210, 56, 'pl'), text(145, 217, 'Gate: send only if', 's'), text(145, 234, 'CONSUMED + needed <= LIMIT', 's h'), text(145, 248, '(modulo arithmetic)', 'xs d')]
b += [rect(490, 20, 250, 250, 'box'), text(615, 44, 'Receiver', 's h'), text(615, 60, 'Transaction Layer buffers', 'xs d')]
for i in range(6):
    b += [rect(510 + i * 34, 76, 30, 40, 'tl' if i < 3 else 'box', 2)]
b += [text(615, 132, 'buffer slots: used / free', 'xs d')]
b += [rect(510, 146, 210, 48, 'pl'), text(615, 166, 'CREDITS_ALLOCATED', 's h'), text(615, 182, 'initial + slots freed so far', 'xs d')]
b += [rect(510, 208, 210, 46, 'box'), text(615, 227, 'CREDITS_RECEIVED', 's h'), text(615, 243, 'optional overflow check', 'xs d')]
b += [arrow(270, 100, 490, 100, 'lna'), text(380, 92, 'TLP (uses credits)', 's')]
b += [arrow(490, 170, 270, 170, 'lnc'), text(380, 162, 'UpdateFC DLLP', 's cy'), text(380, 186, 'P / NP / Cpl, header + data', 'xs d')]
b += [text(380, 232, 'A credit returns when the receiver', 'xs d'), text(380, 246, 'DRAINS a slot, not when it ACKs.', 'xs d')]
add('fc', 'The flow-control credit loop', 'The transmitter may send only while its cumulative consumed count stays inside the cumulative limit the receiver granted. Credits come back as buffers drain, via UpdateFC DLLPs.',
    svg(760, 284, 'Flow control credit loop between transmitter and receiver', ''.join(b)))

# ---------------------------------------------------------------- cfgspace
b = [text(110, 16, '4 KB per function', 's h')]
b += [rect(30, 26, 160, 56, 'tl'), text(110, 48, 'Header', 'h'), text(110, 64, '00h - 3Fh', 's d'), text(110, 77, 'Type 0 or Type 1', 'xs d')]
b += [rect(30, 88, 160, 116, 'dl'), text(110, 110, 'Capabilities', 'h'), text(110, 126, '40h - FFh', 's d'), text(110, 144, 'linked list', 'xs d'), text(110, 158, 'pointer at 34h', 'xs d')]
b += [rect(30, 210, 160, 150, 'pl'), text(110, 234, 'Extended capabilities', 'h'), text(110, 250, '100h - FFFh', 's d'), text(110, 268, 'linked list', 'xs d'), text(110, 282, 'starts at 100h', 'xs d')]
b += [text(30, 378, 'Legacy CF8h/CFCh reaches only 00h - FFh.', 'xs d', 'start'), text(30, 392, 'ECAM reaches the full 4 KB.', 'xs d', 'start')]
# capability chain
caps = [('PM', '01h'), ('MSI', '05h'), ('PCI Express', '10h'), ('MSI-X', '11h')]
b += [text(500, 16, 'Capability chain (8-bit ID, 8-bit next)', 's h')]
cx = 230
b += [rect(cx, 96, 84, 42, 'box'), text(cx + 42, 114, 'Cap Ptr', 's h'), text(cx + 42, 129, 'at 34h', 'xs d')]
prev = cx + 84
for i, (nm, cid) in enumerate(caps):
    x = 340 + i * 105
    b += [arrow(prev, 117, x, 117, 'lnc'), rect(x, 96, 92, 42, 'dl'), text(x + 46, 114, nm, 's h'), text(x + 46, 129, 'ID ' + cid, 'xs d')]
    prev = x + 92
b += [text(500, 168, 'ends when Next = 00h', 'xs d')]
b += [text(500, 218, 'Extended chain (16-bit ID, 4-bit version, 12-bit next)', 's h')]
ext = ['AER', 'Serial No.', 'SR-IOV', 'ATS']
prev = 230
b += [rect(230, 234, 84, 42, 'box'), text(272, 252, 'at 100h', 's h'), text(272, 267, 'first entry', 'xs d')]
prev = 314
for i, nm in enumerate(ext[:4]):
    x = 340 + i * 105
    b += [arrow(prev, 255, x, 255, 'lng'), rect(x, 234, 92, 42, 'pl'), text(x + 46, 260, nm, 's h')]
    prev = x + 92
b += [text(500, 302, 'order and presence vary by device; walk the list, never assume offsets', 'xs d')]
b += [text(230, 336, 'Type 0 BARs: 10h - 24h (six 32-bit, or three 64-bit).', 'xs d', 'start'), text(230, 352, 'Type 1 adds bus numbers and bridge windows.', 'xs d', 'start')]
add('cfgspace', 'Configuration space map', 'One 4 KB space per function: a 64-byte header, a capability list that starts from the pointer at 34h, and extended capabilities from 100h onward. Always walk the lists; offsets differ between devices.',
    svg(760, 404, 'Configuration space layout with capability chains', ''.join(b)))

# ---------------------------------------------------------------- msix
b = [rect(10, 20, 190, 130, 'dl'), text(105, 42, 'MSI-X capability', 'h'), text(105, 58, '(config space)', 'xs d'),
     text(20, 82, 'Message Control:', 'xs', 'start'), text(20, 96, ' table size, enable, mask', 'xs d', 'start'),
     text(20, 114, 'Table Offset + BIR', 'xs', 'start'), text(20, 130, 'PBA Offset + BIR', 'xs', 'start')]
b += [arrow(200, 70, 262, 62, 'lnc'), arrow(200, 132, 262, 216, 'lnc')]
b += [text(270, 14, 'MSI-X Table (in a BAR): 16 bytes per vector', 's h')]
CW_ = [('Addr Lo', 85), ('Addr Hi', 85), ('Data', 70), ('Ctrl', 60)]
for j_, (nm, w) in enumerate(CW_):
    x = 262 + sum(v for _, v in CW_[:j_])
    b += [text(x + w / 2, 30, nm, 'xs d')]
    for r in range(3):
        b += [rect(x, 36 + r * 28, w, 24, 'tl' if r != 1 else 'dl', 2)]
b += [text(262, 152, 'vector 0, vector 1, ... up to 2048', 'xs d', 'start')]
b += [text(270, 196, 'Pending Bit Array (PBA): one bit per vector', 's h')]
for i_ in range(16):
    b += [rect(262 + i_ * 20, 206, 18, 24, 'er' if i_ in (3, 9) else 'box', 2)]
b += [text(262, 250, 'a bit is set while its vector is masked, and cleared when the message is sent', 'xs d', 'start')]
b += [rect(600, 30, 150, 92, 'pl'), text(675, 54, 'Interrupt target', 'h'), text(675, 72, 'local APIC, or', 's d'), text(675, 86, 'interrupt remapping', 's d'), text(675, 106, '(IOMMU)', 'xs d')]
b += [arrow(562, 76, 600, 76, 'lna')]
b += [text(675, 144, 'posted MWr:', 'xs ac'), text(675, 158, 'Addr = entry Addr', 'xs d'), text(675, 172, 'payload = entry Data', 'xs d')]
b += [text(10, 282, 'BIR (BAR indicator) says which BAR holds each structure.  Vector Ctrl bit 0 masks one vector; Function Mask masks all.', 'xs d', 'start'),
      text(10, 298, 'Memory Space Enable and Bus Master Enable must both be on before a message can be sent.', 'xs d', 'start')]
add('msix', 'MSI-X structures', 'The capability points at a vector table and a pending bit array inside BARs. Firing a vector is nothing more than a 4-byte posted memory write to the address in that table entry.',
    svg(760, 308, 'MSI-X capability, table, pending bit array and interrupt write', ''.join(b)))

# ---------------------------------------------------------------- pmstates
b = [text(140, 18, 'D0 (function on)', 's h ac'), text(400, 18, 'D3hot', 's h ac'), text(630, 18, 'D3cold', 's h ac')]
b += [rect(20, 28, 240, 250, 'grp'), rect(290, 28, 220, 250, 'grp'), rect(540, 28, 200, 250, 'grp')]
b += [rect(70, 48, 140, 40, 'tl'), text(140, 72, 'L0', 'h')]
b += [rect(30, 130, 90, 40, 'dl'), text(75, 148, 'L0s', 'h'), text(75, 162, 'ASPM, per dir', 'xs d')]
b += [rect(150, 130, 100, 40, 'dl'), text(200, 148, 'L1', 'h'), text(200, 162, 'ASPM', 'xs d')]
b += [rect(150, 200, 100, 62, 'pl'), text(200, 220, 'L1.1', 'h'), text(200, 238, 'L1.2', 'h'), text(200, 254, 'CLKREQ#, LTR', 'xs d')]
b += [arrow(120, 88, 90, 128, 'lnc'), arrow(180, 88, 200, 128, 'lnc'), arrow(200, 170, 200, 198, 'lng')]
b += [rect(330, 100, 140, 56, 'dl'), text(400, 124, 'L1', 'h'), text(400, 142, 'forced by software', 'xs d')]
b += [rect(570, 60, 140, 46, 'box'), text(640, 80, 'L2', 'h'), text(640, 96, 'aux power on', 'xs d')]
b += [rect(570, 130, 140, 46, 'box'), text(640, 150, 'L3', 'h'), text(640, 166, 'everything off', 'xs d')]
b += [arrow(260, 128, 330, 128, 'lna'), text(295, 118, 'PMCSR', 'xs ac'), text(295, 148, 'PM_Enter_L1', 'xs d')]
b += [arrow(470, 128, 570, 100, 'lna'), text(520, 152, 'PME_Turn_Off', 'xs d'), text(520, 166, 'PM_Enter_L23', 'xs d')]
b += [arrow(640, 106, 640, 130, 'lnd')]
b += [text(20, 298, 'D-state: software, per function.  L-state: the link, run by both ports (and by ASPM on its own).', 'xs d', 'start'),
      text(20, 314, 'D3hot forces L1.  D3cold means the link is in L2 or L3.', 'xs d', 'start'),
      text(20, 330, 'NVMe PS0..PSn is a third, independent ladder inside the controller.', 'xs d', 'start')]
add('pmstates', 'D-states, L-states and how they map', 'The device state and the link state are different families tied by rules. Software moves the D-state; the ports move the L-state, sometimes on their own through ASPM.',
    svg(760, 342, 'Mapping of D-states to link L-states', ''.join(b)))

# ---------------------------------------------------------------- aer
b = [rect(10, 110, 130, 60, 'box'), text(75, 136, 'Error detected', 'h'), text(75, 154, 'PHY / DLL / TL', 'xs d')]
cls = [('Correctable', 'ERR_COR', 'pl', ('Bad TLP, Bad DLLP,', 'Replay Timeout, Rx Error'), 20, (450, 66)),
       ('Uncorrectable non-fatal', 'ERR_NONFATAL', 'tl', ('UR, CA, Completion Timeout,', 'Poisoned TLP, ECRC'), 110, (435, 124)),
       ('Uncorrectable fatal', 'ERR_FATAL', 'er', ('Malformed TLP, Surprise Down,', 'DL Protocol Error, FC error'), 200, (452, 214))]
for nm, msg, c, ex, y, (lx, ly) in cls:
    b += [arrow(140, 140, 200, y + 28, 'lna' if c != 'er' else 'lnr'), rect(200, y, 200, 56, c), text(300, y + 22, nm, 's h'), text(300, y + 37, ex[0], 'xs d'), text(300, y + 49, ex[1], 'xs d')]
    b += [arrow(400, y + 28, 470, 140, 'lnc'), text(lx, ly, msg, 'xs cy')]
b += [rect(470, 100, 120, 80, 'dl'), text(530, 126, 'Root Complex', 'h'), text(530, 144, 'Root Error Status', 'xs d'), text(530, 158, 'Error Source ID', 'xs d')]
b += [arrow(590, 140, 640, 140, 'lna')]
b += [rect(640, 60, 110, 44, 'box'), text(695, 80, 'Firmware-first', 's h'), text(695, 95, 'may see it first', 'xs d')]
b += [rect(640, 112, 110, 44, 'box'), text(695, 132, 'OS AER driver', 's h'), text(695, 147, 'log, reset, retry', 'xs d')]
b += [rect(640, 164, 110, 44, 'er'), text(695, 184, 'DPC', 's h'), text(695, 199, 'contain the port', 'xs d')]
b += [text(20, 274, 'Severity of each uncorrectable type is programmable (Uncorrectable Error Severity); the placement above is the default.', 'xs d', 'start'),
      text(20, 290, 'Header Log holds the offending TLP header, when the error came with one.', 'xs d', 'start')]
add('aer', 'Error classes and reporting path', 'Errors are classed, reported to the Root Complex as ERR_* messages, and then handled by firmware, the OS AER driver, or by Downstream Port Containment.',
    svg(760, 302, 'PCIe error classification and reporting path', ''.join(b)))

# ---------------------------------------------------------------- sriov
b = [rect(230, 8, 300, 46, 'tl'), text(380, 28, 'Host memory + IOMMU', 'h'), text(380, 44, 'translates each requester ID separately', 'xs d')]
b += [rect(290, 76, 180, 34, 'box'), text(380, 98, 'Root Port', 's h'), arrow(380, 54, 380, 76, 'lnd'), line(380, 110, 380, 150, 'lna'), text(396, 134, 'one shared link', 'xs d', 'start')]
b += [rect(20, 150, 720, 190, 'grp'), text(36, 168, 'One SSD, one link, one controller', 's d', 'start')]
b += [rect(40, 180, 150, 140, 'tl'), text(115, 202, 'PF', 'h'), text(115, 218, 'RID  b:d.0', 'xs'), text(115, 234, 'full config space', 'xs d'), text(115, 248, 'SR-IOV capability', 'xs d'), text(115, 262, 'admin, VF setup', 'xs d'), text(115, 300, 'owns VF enable', 'xs d')]
for i in range(3):
    x = 220 + i * 170
    b += [rect(x, 180, 150, 140, 'dl'), text(x + 75, 202, f'VF{i + 1}', 'h'), text(x + 75, 218, f'RID  b:d.{i + 1}*', 'xs'), text(x + 75, 234, 'own BAR slice', 'xs d'), text(x + 75, 248, 'own MSI-X vectors', 'xs d'), text(x + 75, 262, 'own queues', 'xs d'), text(x + 75, 300, 'own FLR', 'xs d')]
    b += [poly_arrow([(x + 75, 180), (x + 75, 152), (380, 152)], 'lng')] if False else []
b += [text(380, 358, 'DMA from each VF carries that VF\'s requester ID, so the IOMMU can give every VM its own mapping.', 's d'),
      text(380, 374, '* Routing IDs come from the PF\'s First VF Offset and VF Stride, and may cross into higher bus numbers.', 'xs d')]
add('sriov', 'SR-IOV: one PF, many VFs', 'A Physical Function creates lightweight Virtual Functions, each with its own routing ID, BAR slice and interrupt vectors. They all share the same link and the same device internals.',
    svg(760, 384, 'SR-IOV physical function and virtual functions sharing one link', ''.join(b)))

# ---------------------------------------------------------------- flit
b = [text(20, 18, 'NON-FLIT: each TLP framed separately', 's h ac', 'start')]
x = 20
for nm, w, c in [('STP', 60, 'pl'), ('Seq #', 70, 'dl'), ('Header', 110, 'tl'), ('Payload', 250, 'tl'), ('ECRC', 60, 'tl'), ('LCRC', 70, 'dl'), ('END', 60, 'pl')]:
    b += [rect(x, 28, w, 40, c, 2), text(x + w / 2, 53, nm, 's h')]
    x += w
b += [text(20, 88, 'DLLPs are separate 6-byte packets. Sequence number and LCRC are per TLP.', 'xs d', 'start')]
b += [text(20, 126, 'FLIT MODE: fixed 256-byte flit (bar is not to scale)', 's h ac', 'start')]
segs = [('TLP area  236 B', 460, 'tl'), ('DLP 6 B', 80, 'dl'), ('CRC 8 B', 80, 'er'), ('FEC 6 B', 80, 'pl')]
x = 20
pos = {}
for nm, w, c in segs:
    b += [rect(x, 136, w, 50, c, 2), text(x + w / 2, 166, nm, 's h')]
    pos[nm] = (x, x + w)
    x += w
b += [line(20, 200, 640, 200, 'lna'), line(20, 196, 20, 204, 'lna'), line(640, 196, 640, 204, 'lna'), text(330, 216, 'CRC covers TLP area + DLP (bytes 0 - 241)', 'xs ac')]
b += [line(20, 228, 720, 228, 'lnc'), line(20, 224, 20, 232, 'lnc'), line(720, 224, 720, 232, 'lnc'), text(370, 244, 'FEC (three interleaved 2-byte groups) protects everything before it', 'xs cy')]
b += [text(20, 274, 'Overhead is 20 of 256 bytes: DLP 6 + CRC 8 + FEC 6.', 'xs d', 'start'),
      text(20, 290, 'Acks, Naks and credits ride in the DLP; a bad CRC after FEC triggers a flit replay.', 'xs d', 'start'),
      text(20, 306, 'The 236 / 6 / 8 / 6 split is the commonly published layout; confirm it in the Base Specification before quoting.', 'xs d', 'start')]
add('flit', 'FLIT versus non-FLIT framing', 'FLIT mode replaces per-TLP framing, sequence numbers and LCRC with fixed 256-byte flits protected by a flit CRC and a light-weight FEC.',
    svg(760, 316, 'Non-FLIT TLP framing compared with a 256 byte flit', ''.join(b)))

# ---------------------------------------------------------------- resets
cols = ['Link', 'Config regs', 'Device logic', 'Sticky (AER)', 'NVMe controller']
rowsd = [
    ('PERST# (fundamental)', [('retrains', 'er'), ('reset', 'er'), ('reset', 'er'), ('cleared*', 'er'), ('reset', 'er')]),
    ('Hot reset (secondary bus)', [('retrains', 'er'), ('reset', 'er'), ('reset', 'er'), ('kept', 'pl'), ('reset', 'er')]),
    ('FLR', [('stays up', 'pl'), ('reset', 'er'), ('function only', 'er'), ('kept', 'pl'), ('reset', 'er')]),
    ('D3hot to D0', [('stays up', 'pl'), ('if soft reset', 'tl'), ('if soft reset', 'tl'), ('kept', 'pl'), ('varies', 'tl')]),
    ('NVMe CC.EN 1 to 0', [('untouched', 'pl'), ('untouched', 'pl'), ('controller only', 'tl'), ('kept', 'pl'), ('reset', 'er')]),
    ('NVMe NSSR', [('varies', 'tl'), ('varies', 'tl'), ('subsystem', 'er'), ('varies', 'tl'), ('reset', 'er')]),
]
X1, CW = 200, 108
b = []
for j, c in enumerate(cols):
    b += [text(X1 + j * CW + CW / 2, 20, c, 'xs f')]
for i, (nm, cells) in enumerate(rowsd):
    y = 30 + i * 44
    b += [text(10, y + 26, nm, 's h', 'start')]
    for j, (val, c) in enumerate(cells):
        b += [rect(X1 + j * CW + 2, y, CW - 4, 38, c, 3), text(X1 + j * CW + CW / 2, y + 24, val, 'xs')]
b += [text(10, 306, 'Red = cleared or restarted.  Green = untouched.  Amber = depends on the device or on a config bit.', 'xs d', 'start'),
      text(10, 322, '* Sticky registers survive a Fundamental Reset only when auxiliary power keeps them alive. Read and log AER before you reset.', 'xs d', 'start'),
      text(10, 338, 'Exact behavior of NSSR, D3hot to D0 and sticky rules is device- and spec-revision dependent: verify for your part.', 'xs d', 'start')]
add('resets', 'What each reset clears', 'Reset types differ in scope. Only a Fundamental Reset restarts everything, and error status in sticky registers survives most of the others, so read it before you reset.',
    svg(760, 350, 'Matrix of reset types against what each resets', ''.join(b)))

# ---------------------------------------------------------------- nvmeflow
b = [text(170, 20, 'Host CPU + memory', 's h'), text(590, 20, 'NVMe SSD', 's h'), line(170, 32, 170, 424), line(590, 32, 590, 424)]
def step(y, n, label, direction, cls, sub=None):
    s = []
    if direction == '>':
        s += [arrow(170, y, 590, y + 8, cls)]
    elif direction == '<':
        s += [arrow(590, y, 170, y + 8, cls)]
    s += [text(380, y - 6, label, 's')]
    if sub:
        s += [text(380, y + 20, sub, 'xs d')]
    s += [text(6, y + 4, str(n), 's ac', 'start')]
    return s
b += [rect(180, 44, 200, 26, 'box'), text(280, 61, 'write 64 B SQE into SQ ring (no bus event)', 'xs d'), text(6, 60, '1', 's ac', 'start')]
b += step(96, 2, 'MWr 4 B: SQ tail doorbell', '>', 'lna')
b += step(146, 3, 'MRd 64 B: fetch SQE', '<', 'lnc', 'non-posted, needs a tag')
b += step(196, '', 'CplD 64 B: the SQE', '>', 'lnc')
b += step(246, 4, 'MWr x N: 4 KB data, each <= MPS', '<', 'lna', 'after the NAND read')
b += step(296, 5, 'MWr 16 B: CQE with phase tag', '<', 'lna')
b += step(340, 6, 'MWr 4 B: MSI-X message', '<', 'lna')
b += step(384, 7, 'MWr 4 B: CQ head doorbell', '>', 'lna', 'after the host consumed the CQE')
b += [rect(600, 232, 150, 66, 'er', 3), text(675, 252, 'posted stream', 's h'), text(675, 268, 'data, CQE, MSI-X', 'xs d'), text(675, 284, 'stay in order', 'xs d')]
add('nvmeflow', 'One 4 KB NVMe read on the bus', 'Only the SQE fetch is non-posted. The data, the completion entry and the interrupt are posted writes that arrive in order, which is what lets the host trust the completion.',
    svg(760, 436, 'Sequence of PCIe transactions for a 4 KB NVMe read', ''.join(b)))

with open(os.path.join(ROOT, 'diagrams.js'), 'w', encoding='utf-8') as f:
    f.write('var DIAGRAMS={};\n' + '\n'.join(out) + '\n')
print('wrote diagrams.js with', len(out), 'diagrams')
