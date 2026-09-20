#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'study_common'))
import dlib
from dlib import rect, text, line, arrow, poly_arrow, svg, add


def cell(x, y, w, h, cls, lines, first='s h', rest='xs d'):
    """box with 1..n centred text lines"""
    s = [rect(x, y, w, h, cls, 4)]
    n = len(lines)
    step = 13
    y0 = y + h / 2 - (n - 1) * step / 2 + 4
    for i, t in enumerate(lines):
        s.append(text(x + w / 2, y0 + i * step, t, first if i == 0 else rest))
    return s

# ---------------------------------------------------------------- nvmereset (9.12)
b = []
cols = [(10, 140, 'Trigger', ''), (156, 110, 'Scope', ''), (272, 90, 'NVMe regs,', 'queues, I/O'),
        (368, 160, 'PCIe config', 'and link'), (534, 216, 'Host must', 'redo')]
for x, w, l1, l2 in cols:
    b += [rect(x, 8, w, 40, 'box', 4)]
    if l2:
        b += [text(x + w / 2, 24, l1, 's h'), text(x + w / 2, 38, l2, 's h')]
    else:
        b += [text(x + w / 2, 32, l1, 's h')]
rows = [
    ('CC.EN 1 to 0', ['controller level'], 'One controller', 'Cleared', ('Kept', 'pl'), 'AQA, ASQ, ACQ, CC, then queues'),
    ('FLR', ['PCIe reset,', 'controller level'], 'One function', 'Cleared', ('Config reset', 'tl'), 'Restore config, then init'),
    ('Hot reset', ['PCIe reset,', 'controller level'], 'The device', 'Cleared', ('Reset, link retrains', 'tl'), 'Re-enumerate, then init'),
    ('NSSR', ['subsystem level'], 'All controllers', 'Cleared', ('Device dependent', 'grp'), 'Check NSSRO, maybe re-enumerate'),
    ('PERST# / power cycle', ['subsystem level,', 'NSSR mapping: VERIFY'], 'Whole subsystem', 'Cleared', ('Fully reset', 'tl'), 'Full enumeration and init'),
]
y = 54
for name, sub, scope, nv, (pc, pcls), redo in rows:
    h = 50
    b += [rect(10, y, 140, h, 'box', 4), text(80, y + 17, name, 's h')]
    for i, t in enumerate(sub):
        b += [text(80, y + 31 + i * 11, t, 'xs d')]
    b += cell(156, y, 110, h, 'box', [scope], 's')
    b += cell(272, y, 90, h, 'tl', [nv], 's')
    if pcls == 'grp':
        b += [rect(368, y, 160, h, 'grp', 4), text(448, y + 22, pc, 's h'), text(448, y + 37, 'link drop: VERIFY', 'xs d')]
    else:
        b += cell(368, y, 160, h, pcls, [pc], 's')
    b += cell(534, y, 216, h, 'box', [redo], 'xs')
    y += 54
# NSSR row is index 3 -> hedge also on Cleared? no: text says Cleared.
py = 54 + 5 * 54 + 4
panels = [
    (10, 'pl', 'Survives every trigger', ['NAND contents, namespaces and', 'attachments, saved feature values,', 'persistent logs. Unsaved feature', 'values return to defaults.']),
    (259, 'tl', 'Commands in flight', ['No CQE arrives. The host completes', 'them itself. Acknowledged writes', 'should survive. An in-flight write', 'is old or new data, never a mix.']),
    (508, 'dl', 'Telling them apart', ['NSSR: CSTS.NSSRO set (write 1 to', 'clear), Power Cycles unchanged.', 'CC.EN toggle: only RDY moved. Wait', 'for RDY = 0 (CAP.TO x 500 ms).']),
]
for x, c, t, ls in panels:
    b += [rect(x, py, 242, 84, c, 5), text(x + 121, py + 16, t, 's h')]
    for i, l in enumerate(ls):
        b += [text(x + 121, py + 32 + i * 12, l, 'xs')]
b += [text(10, py + 102, 'Green = kept or preserved, amber = cleared or reset, dashed = device dependent. No trigger erases NAND data.', 'xs d', 'start')]
add('nvmereset', 'Which reset clears what', 'Five triggers against scope, NVMe state, PCIe config and link, and what the host must redo. NVMe state is cleared by every trigger. The NSSR link cell is device dependent, and whether PERST# counts as an NSSR is a spec mapping to VERIFY.',
    svg(760, py + 112, 'Matrix of reset triggers against scope and what each preserves or clears', ''.join(b)))



def chk(t, cls, maxw, what=''):
    """assert estimated text width fits (px per char: 7.3 default, 6.3 s, 5.7 xs; bold slightly wider)"""
    per = 5.7 if 'xs' in cls.split() else (6.3 if 's' in cls.split() else 7.3)
    if 'h' in cls.split():
        per *= 1.05
    w = len(t) * per
    assert w <= maxw, 'text too wide (%d > %d): %s %s' % (w, maxw, t, what)


def tbox(x, y, w, h, cls, title, lines, tcls='s h', lcls='xs', ty=16, ly=30, step=12):
    s = [rect(x, y, w, h, cls, 5)]
    chk(title, tcls, w - 12, 'title')
    s.append(text(x + w / 2, y + ty, title, tcls))
    for k, l in enumerate(lines):
        chk(l, lcls, w - 12)
        s.append(text(x + w / 2, y + ly + k * step, l, lcls))
    return s


# ---------------------------------------------------------------- intpath (10.01, 10.06)
b = []
BW, PITCH, X0C = 136, 148, 14


def cx(i):
    return X0C + i * PITCH


def mid(i):
    return cx(i) + BW / 2


AY, AH = 6, 94          # controller band
MY, MH = 104, 102       # host memory band
CY, CH = 210, 94        # host CPU band
BY_A, BY_C, BH = 26, 232, 68
b += [rect(6, AY, 748, AH, 'grp', 6), text(14, AY + 12, 'Controller firmware: steps 1 to 3 (NAND read done, SQE was taken from the SQ)', 'xs d', 'start')]
b += [rect(6, MY, 748, MH, 'grp', 6), text(14, MY + 12, 'Host memory', 'xs d', 'start')]
b += [rect(6, CY, 748, CH, 'grp', 6), text(14, CY + 12, 'Host driver on the CPU: steps 4 to 6', 'xs d', 'start')]
b += tbox(cx(0), BY_A, BW, BH, 'dl', '1 Post CQE', ['16 B posted write,', 'phase tag set,', 'CQ tail advances'])
b += tbox(cx(1), BY_A, BW, BH, 'dl', '2 Decide', ['checks CQ IEN, IV,', 'mask, coalescing', '(see 10.05)'])
b += tbox(cx(2), BY_A, BW, BH, 'dl', '3 Signal', ['one posted write to', 'the vector address;', 'no queue, CID, data'])
b += tbox(cx(3), BY_A, BW, BH, 'dl', 'CQ Head Doorbell', ['BAR0 register, frees', 'CQ slots. SQ slots', 'free via SQ Head Ptr'])
b += tbox(cx(2), BY_C, BW, BH, 'tl', '4 Deliver', ['ISR runs on the', 'vector CPU: reads CQE', 'at head, checks phase'], lcls='xs')
b += tbox(cx(3), BY_C, BW, BH, 'tl', '5 Drain, ack', ['repeat until phase', 'differs, then ONE', 'CQ Head DB write'])
b += tbox(cx(4), BY_C, BW, BH, 'tl', '6 Finish', ['complete by CID,', 'blk-mq ends request,', 'task is woken'])
for l, t in enumerate(['CQE first, then the', 'vector write. The', 'interrupt is only a', 'hint that it is there.']):
    b += [text(cx(4) + 6, BY_A + 14 + l * 12, t, 'xs d', 'start')]
b += [arrow(cx(0) + BW, BY_A + 34, cx(1), BY_A + 34, 'lnc'), arrow(cx(1) + BW, BY_A + 34, cx(2), BY_A + 34, 'lnc')]
b += [arrow(cx(2) + BW, BY_C + 34, cx(3), BY_C + 34, 'lna'), arrow(cx(3) + BW, BY_C + 34, cx(4), BY_C + 34, 'lna')]
# vector write: Signal down to Deliver
b += [arrow(mid(2), BY_A + BH, mid(2), BY_C, 'lnc'), text(mid(2) + 8, MY + 40, 'vector write', 'xs cy', 'start'), text(mid(2) + 8, MY + 52, '(posted)', 'xs cy', 'start')]
# doorbell write: Drain up to doorbell
b += [arrow(mid(3), BY_C, mid(3), BY_A + BH, 'lna'), text(mid(3) + 8, MY + 46, 'one DB write', 'xs ac', 'start')]
# CQ ring
RX, RY, RS = 18, MY + 34, 20
for k in range(8):
    b += [rect(RX + k * RS, RY, RS, 18, 'dl' if 0 <= k < 3 else 'box', 2)]
b += [text(RX + RS / 2, RY - 5, 'head', 'xs ac'), text(RX + 3 * RS + RS / 2, RY + 30, 'tail', 'xs cy')]
b += [arrow(RX + 3 * RS + RS / 2, BY_A + BH, RX + 3 * RS + RS / 2, RY, 'lnc')]
for k, t in enumerate(['CQ ring of 16 B CQEs. Each has', 'DW0, SQ Head Ptr, SQ ID,', 'CID, phase bit, status']):
    b += [text(188, RY + 8 + k * 12, t, 'xs d', 'start')]
# ISR reads the CQ from head
b += [poly_arrow([(cx(2), BY_C + 34), (RX + RS / 2, BY_C + 34), (RX + RS / 2, RY + 18)], 'lna'), text(RX + 30, BY_C + 28, 'ISR reads CQEs from head', 'xs ac', 'start')]
# SQ ring
SX = 640
for k in range(4):
    b += [rect(SX + k * 22, RY, 22, 18, 'tl' if k < 3 else 'box', 2)]
b += [text(SX + 44, RY + 32, 'SQ ring of 64 B SQEs', 'xs d'), text(SX + 44, RY + 44, 'freed by SQ Head Ptr', 'xs d')]
b += [text(14, CY + CH + 16, 'Several CQs may share one vector. The message carries only the vector, so the ISR scans every CQ mapped to it.', 'xs d', 'start')]
# coalescing timeline
T0 = CY + CH + 42
X0, K = 150, 5.2


def tx(t):
    return X0 + t * K


b += [text(10, T0, 'Step 2 in time: example THR 3 (4 entries) and TIME 1 (100 us), one CQE every 20 us', 's h', 'start')]


def lane(yb, label, cqes, fire, why, side):
    s = [text(10, yb - 8, label[0], 'xs h', 'start'), text(10, yb + 4, label[1], 'xs d', 'start'), line(X0 - 8, yb, tx(112), yb, 'ln')]
    for t in cqes:
        s += [rect(tx(t) - 5, yb - 18, 10, 18, 'dl', 2)]
    s += [line(tx(0), yb + 4, tx(fire), yb + 4, 'lnd')]
    lab = 'MSI-X write at %d us: %s' % (fire, why)
    chk(lab, 'xs', 250)
    s += [arrow(tx(fire), yb + 28, tx(fire), yb + 4, 'lna')]
    if side == 'right':
        s += [text(tx(fire) + 10, yb + 22, lab, 'xs ac', 'start')]
    else:
        s += [text(tx(fire) - 10, yb + 22, lab, 'xs ac', 'end')]
    return s


L1, L2 = T0 + 30, T0 + 84
b += lane(L1, ('Threshold hit', '4 CQEs in a burst'), [0, 20, 40, 60], 60, '4th CQE reached THR', 'right')
b += lane(L2, ('Timer hit', 'a lone CQE'), [0], 100, 'TIME ran out', 'left')
AXY = L2 + 40
b += [line(tx(0), AXY, tx(112), AXY, 'ln')]
for t in (0, 20, 40, 60, 80, 100):
    b += [line(tx(t), AXY, tx(t), AXY + 5, 'ln'), text(tx(t), AXY + 17, str(t), 'xs d')]
b += [text(tx(112), AXY + 17, 'us', 'xs d', 'end')]
b += [text(10, AXY + 34, 'Every CQE is already in host memory at its blue box; a polling host sees it there. Only the vector write is held back.', 'xs d', 'start')]
H_INT = AXY + 44
assert H_INT <= 520, H_INT
add('intpath', 'A completion from CQE to CPU', 'Blue = controller side, amber = host side. The controller writes the CQE first and only then decides whether and when to signal. Timeline: the vector write waits for the threshold or the timer (values from 10.06; the algorithm is vendor specific).',
    svg(760, H_INT, 'Path of a completion from SQ to CQ to MSI-X vector to CPU, with a coalescing timeline', ''.join(b)))

# ---------------------------------------------------------------- nvmepower (11.05)
b = []
hd = [(10, 80, ['State']), (96, 200, ['Descriptor', 'ENLAT / EXLAT (total)']), (302, 210, ['Recent mainline', '100 ms if total is 15 ms or less']),
      (518, 232, ['Older rule', 'idle = 50 x (ENLAT + EXLAT)'])]
for x, w, ls in hd:
    b += [rect(x, 6, w, 38, 'box', 4)]
    if len(ls) == 1:
        b += [text(x + w / 2, 29, ls[0], 's h')]
    else:
        chk(ls[1], 'xs', w - 12)
        b += [text(x + w / 2, 21, ls[0], 's h'), text(x + w / 2, 35, ls[1], 'xs d')]
rows = [
    ('PS0-PS2', 'operational', None, 'PS4 after 100 ms', 'PS3 after 71 ms', '50 x 1.41 ms'),
    ('PS3', 'non-op', '210 us / 1,200 us (1.41 ms)', 'PS4 after 100 ms', 'PS4 after 500 ms', '50 x 10 ms'),
    ('PS4', 'non-op', '1,000 us / 9,000 us (10 ms)', 'none', 'none', None),
]
y = 48
for st, kind, desc, new, old, calc in rows:
    b += [rect(10, y, 80, 38, 'box', 4), text(50, y + 17, st, 's h'), text(50, y + 30, kind, 'xs d')]
    b += cell(96, y, 200, 38, 'box', [desc] if desc else ['operational:', 'no ENLAT or EXLAT used'], 'xs', 'xs')
    b += cell(302, y, 210, 38, 'dl' if new != 'none' else 'box', [new], 's')
    b += cell(518, y, 232, 38, 'tl' if old != 'none' else 'box', [old, '(%s)' % calc] if calc else [old], 's', 'xs d')
    y += 42
b += [text(10, 186, 'PS3 is skipped in the recent scheme: both PS3 and PS4 fall inside the 15 ms primary tolerance, so only the deepest is used.', 'xs d', 'start'),
      text(10, 199, 'A state with total latency between 15 ms and 100 ms would form a second tier with a 2,000 ms timeout.', 'xs d', 'start')]
b += [text(10, 226, 'Idle timeline, PS4 example (ENLAT 1 ms, EXLAT 9 ms), recent scheme. Not to scale after t = 100 ms.', 's h', 'start')]
LY = 240
segs = [(30, 330, 'dl', 'PS0, idle timer runs (100 ms)'), (330, 372, 'tl', 'ENLAT'), (372, 560, 'pl', None), (560, 612, 'tl', 'EXLAT'), (612, 740, 'dl', 'operational')]
for x1, x2, c, l in segs:
    b += [rect(x1, LY, x2 - x1, 38, c, 3)]
    if l:
        b += [text((x1 + x2) / 2, LY + 24, l, 'xs h' if c == 'tl' else 's')]
b += [text(466, LY + 17, 'PS4 dwell', 's h'), text(466, LY + 31, 'power falls, L1.2 possible', 'xs')]
for x in (30, 330, 560):
    b += [line(x, LY + 38, x, LY + 52, 'lnd')]
b += [text(30, LY + 64, 't = 0: last I/O completes,', 'xs', 'start'), text(30, LY + 76, 'idle timer starts in PS0', 'xs', 'start')]
b += [text(330, LY + 64, 't = 100 ms: timer expires,', 'xs', 'middle'), text(330, LY + 76, 'enter PS4 (up to ENLAT)', 'xs', 'middle')]
b += [text(560, LY + 64, 'doorbell write arrives,', 'xs', 'middle'), text(560, LY + 76, 'exit takes up to EXLAT', 'xs', 'middle')]
b += [text(740, LY + 92, 'I/O completes after exit plus normal service time', 'xs d', 'end')]
L2 = 366
b += [text(10, L2 - 10, 'Same drive under the older 50 x rule (PS0 to PS2 start):', 's h', 'start')]
b += [rect(30, L2, 213, 34, 'dl', 3), text(136, L2 + 21, 'PS0, idle 71 ms', 's'),
      rect(243, L2, 317, 34, 'pl', 3), text(401, L2 + 14, 'PS3 dwell', 's h'), text(401, L2 + 27, 'its own timer: PS4 after 500 ms', 'xs'),
      rect(560, L2, 180, 34, 'pl', 3), text(650, L2 + 21, 'PS4', 's h')]
# markers below the lane, labels on separate sides so they cannot collide
b += [line(243, L2 + 34, 243, L2 + 44, 'lnd'), text(237, L2 + 56, '71 ms: enter PS3', 'xs d', 'end')]
b += [line(330, L2 + 34, 330, L2 + 44, 'lnd'), text(337, L2 + 56, '100 ms: recent scheme is already in PS4', 'xs d', 'start')]
add('nvmepower', 'APST table and idle timeline', 'Rows are the current state, and entry N of the APST table applies in state N. Blue = operational or idle timer, amber = entry or exit latency, green = low-power state. Both timer schemes use the same PS3 and PS4 latencies.',
    svg(760, 436, 'Power state and APST target table with an idle timeline', ''.join(b)))

# ---------------------------------------------------------------- eraseops (12.02)
b = []
CW = [58, 58, 72, 58]
SXS = [152]
for w in CW[:-1]:
    SXS.append(SXS[-1] + w + 4)
GX, GW = 416, 190
PX, PW = 612, 140
# header
b += [rect(8, 6, 138, 40, 'box', 4), text(77, 30, 'Operation', 's h')]
for x, w, l1, l2 in [(SXS[0], CW[0], 'NS 1', 'target'), (SXS[1], CW[1], 'NS 2', 'other'), (SXS[2], CW[2], 'Unattached', 'NS'), (SXS[3], CW[3], 'Caches', '')]:
    b += [rect(x, 6, w, 40, 'box', 4)]
    if l2:
        b += [text(x + w / 2, 21, l1, 'xs h'), text(x + w / 2, 35, l2, 'xs d')]
    else:
        b += [text(x + w / 2, 30, l1, 'xs h')]
b += [rect(GX, 6, GW, 40, 'box', 4), text(GX + GW / 2, 30, 'Physical guarantee', 's h')]
b += [rect(PX, 6, PW, 40, 'box', 4), text(PX + PW / 2, 21, 'Survives', 's h'), text(PX + PW / 2, 35, 'power loss', 's h')]
b += [text(SXS[0] + 125, 2 + 0, '', 'xs')]
FULL, PART, NONE = 'f', 'p', 'n'
ops = [
    (('Deallocate', 'Dataset Management'), [(PART, 'listed', 'LBAs'), NONE, NONE, NONE],
     'er', ['None, it is a hint', 'logical: mapping changes'], ('box', ['Not applicable'])),
    (('Format NVM', 'SES=0'), [FULL, (PART, 'if all', ''), NONE, NONE],
     'er', ['None: layout changes,', 'data unreachable'], ('grp', ['Vendor specific'])),
    (('Format NVM', 'SES=1 or 2'), [FULL, (PART, 'if FNA', 'says so'), NONE, FULL],
     'pl', ['User data erased, including', 'caches and deallocated LBAs'], ('grp', ['Test it: spec is less', 'explicit than for', 'Sanitize'])),
    (('Sanitize', 'block erase, overwrite'), [FULL, FULL, FULL, FULL],
     'pl', ['Media erased or overwritten', 'physical: changes the media'], ('pl', ['Yes, continues', 'after reset'])),
    (('Crypto erase', 'Sanitize crypto, or', 'Opal Revert / GenKey'), [FULL, FULL, FULL, FULL],
     'pl', ['Key destroyed, ciphertext', 'remains but is useless', 'physical: changes the key'], ('pl', ['Yes, once the key', 'change is committed'])),
]
y = 52
RH = 50
for names, cells, gcls, gl, (pcls, pl_) in ops:
    b += [rect(8, y, 138, RH, 'box', 4), text(77, y + 17, names[0], 's h')]
    for k, t in enumerate(names[1:]):
        chk(t, 'xs d', 126)
        b += [text(77, y + 30 + k * 11, t, 'xs d')]
    for x, w, c in zip(SXS, CW, cells):
        if c == FULL:
            b += [rect(x, y, w, RH, 'tl', 4)]
        elif c == NONE:
            b += [rect(x, y, w, RH, 'box', 4, 'opacity="0.45"')]
        else:
            b += [rect(x, y, w, RH, 'grp', 4), text(x + w / 2, y + 22, c[1], 'xs'), text(x + w / 2, y + 34, c[2], 'xs') if c[2] else '']
    b += [rect(GX, y, GW, RH, gcls, 4)]
    n = len(gl)
    for k, t in enumerate(gl):
        chk(t, 'xs h' if k == 0 else 'xs', GW - 12)
        b += [text(GX + GW / 2, y + RH / 2 - (n - 1) * 6 + 4 + k * 12, t, 'xs h' if k == 0 else 'xs d')]
    b += [rect(PX, y, PW, RH, pcls, 4)]
    n = len(pl_)
    for k, t in enumerate(pl_):
        chk(t, 'xs', PW - 12)
        b += [text(PX + PW / 2, y + RH / 2 - (n - 1) * 6 + 4 + k * 12, t, 'xs')]
    y += 54
f1 = 'Filled = in scope. Dashed = only if asked for (all namespaces, FNA, listed LBAs). Blank = outside the scope the text gives.'
f2 = 'Opal Revert or GenKey can act on one locking range, not the whole subsystem. SES=0 read-back and secure-erase wording: VERIFY.'
chk(f1, 'xs', 740); chk(f2, 'xs', 740)
b += [text(10, y + 10, f1, 'xs d', 'start'), text(10, y + 22, f2, 'xs d', 'start')]
py = y + 34
panels = [
    (8, 'dl', 'Scope first', ['Format can be limited to one', 'namespace. Sanitize cannot: on a', 'drive with two namespaces it', 'destroys both, attached or not.']),
    (259, 'pl', 'Guarantee second', ['Logical (Deallocate, Format SES=0):', 'the mapping changes. Physical (block', 'erase, overwrite, key destruction):', 'the media or the key changes.']),
    (510, 'tl', 'Speed third', ['Crypto erase takes seconds, block', 'erase seconds to minutes, overwrite', 'hours. Zero reads prove less than', 'you think: see the Trap question.']),
]
for x, c, t, ls in panels:
    b += tbox(x, py, 242, 74, c, t, ls, ly=32)
add('eraseops', 'Deallocate, Format, Sanitize, crypto erase', 'Scope, physical guarantee and power-loss behavior as 12.02 states them. Amber cells are in scope, red = no physical guarantee, green = physical or committed erase. Sanitize is subsystem-wide, Format is per namespace, crypto erase destroys the key and leaves ciphertext.',
    svg(760, py + 82, 'Comparison of Deallocate, Format NVM, Sanitize and crypto erase by scope and guarantee', ''.join(b)))

# ---------------------------------------------------------------- multictrl (14.01, 14.02, 7.02)
b = []
GXL, GXR = 6, 754
b += [rect(GXL, 92, GXR - GXL, 328, 'grp', 6), text(16, 106, 'NVM subsystem, one NQN', 'xs d', 'start')]
CXA, CXB, CWD = 50, 420, 290
for hx, nm, lk in [(100, 'Host A', 'link 0'), (470, 'Host B', 'link 1')]:
    b += tbox(hx, 6, 190, 50, 'tl', nm, ['own driver instance'], ly=32)
    b += [line(hx + 95, 56, hx + 95, 116, 'lna'), text(hx + 103, 80, 'PCIe %s (port %s)' % (lk, lk[-1]), 'xs ac', 'start')]
for cxx, n in [(CXA, 0), (CXB, 1)]:
    b += [rect(cxx, 116, CWD, 110, 'dl', 5), text(cxx + CWD / 2, 132, 'Controller %d, own CNTLID' % n, 's h')]
    for k, t in enumerate(['BAR0: CAP, CC, CSTS, doorbells', 'admin queue and I/O queues', 'MSI-X table, Set Features state', 'AER queue, controller-scoped logs']):
        b += [text(cxx + CWD / 2, 148 + k * 12, t, 'xs')]
    b += [rect(cxx + 12, 198, CWD - 24, 20, 'pl', 3), text(cxx + CWD / 2, 212, 'ANA group 1 seen here: Optimized (01h)', 'xs')]
NY, NH = 290, 52
nsb = [(40, 190, 'NS 1, private', ['attached to controller 0', 'only']), (285, 190, 'NS 2, shared', ['NMIC bit 0 set, attached', 'to both, ANA group 1']), (530, 190, 'NS 3, private', ['attached to controller 1', 'only'])]
for x, w, t, ls in nsb:
    b += tbox(x, NY, w, NH, 'pl' if 'shared' in t else 'box', t, ls)
b += [arrow(135, 226, 135, NY, 'lnc'), arrow(300, 226, 335, NY, 'lnc'), arrow(460, 226, 425, NY, 'lnc'), arrow(625, 226, 625, NY, 'lnc')]
b += [text(305, 268, 'attach', 'xs cy', 'end'), text(455, 268, 'attach', 'xs cy', 'start')]
b += [rect(40, 366, 680, 42, 'pl', 5), text(380, 383, 'Shared by all controllers: NAND media and FTL, namespace contents,', 'xs'),
      text(380, 397, 'subsystem NQN, reservation state per namespace, NVM Subsystem Reset domain', 'xs')]
for x in (135, 380, 625):
    b += [line(x, NY + NH, x, 366, 'lnd')]
b += [text(10, 436, 'ANA state is per (controller, ANA group): Optimized 01h, Non-optimized 02h, Inaccessible 03h, Persistent Loss 04h, Change 0Fh.', 'xs d', 'start'),
      text(10, 449, 'Plain dual-port drive: usually Optimized on both. After a fault one controller can report Inaccessible for the same group.', 'xs d', 'start')]
add('multictrl', 'Dual-port SSD, two controllers', 'Amber = host, blue = per-controller state, green = shared by the whole subsystem. Queues, doorbells and interrupts belong to one controller. Media, namespaces and NQN are shared, and CNTLID is unique only inside this subsystem.',
    svg(760, 460, 'Two hosts, two controllers and shared and private namespaces in one NVM subsystem', ''.join(b)))
dlib.write(os.path.dirname(os.path.abspath(__file__)), 'diagrams_C.js')
