#!/usr/bin/env python3
"""Part D diagrams for the NVMe page: fabrics, fdp, ftl, gc, latstack."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'study_common'))
import dlib
from dlib import rect, text, line, arrow, poly_arrow, svg, add


def badge(x, y, n):
    """Small amber numbered circle centred on (x, y)."""
    return [rect(x - 8, y - 8, 16, 16, 'tl', 8), text(x, y + 3.5, str(n), 'xs h')]


# ------------------------------------------------------------------ fabrics
b = []
b += [text(10, 18, 'One command: host to backend', 's h', 'start')]
# host
b += [rect(10, 34, 120, 136, 'tl'), text(70, 56, 'Host', 'h')]
b += [text(70, 78, 'NVMe driver', 'xs'), text(70, 92, 'fabric transport', 'xs'), text(70, 106, 'initiator', 'xs')]
b += [text(70, 134, 'no BAR, no', 'xs d'), text(70, 148, 'doorbells', 'xs d')]
# fabric
b += [rect(190, 34, 240, 136, 'grp'), text(310, 54, 'Fabric transport', 's h')]
for x, l1, l2 in [(200, 'RDMA', ''), (278, 'TCP', ''), (356, 'Fibre', 'Channel')]:
    b += [rect(x, 66, 66, 50, 'box')]
    if l2:
        b += [text(x + 33, 87, l1, 's h'), text(x + 33, 102, l2, 's h')]
    else:
        b += [text(x + 33, 96, l1, 's h')]
b += [text(310, 140, 'capsules travel as network', 'xs d'), text(310, 155, 'messages, not MMIO or DMA', 'xs d')]
# capsule arrows
b += [arrow(130, 80, 190, 80, 'lna'), text(160, 72, 'command', 'xs')]
b += [arrow(190, 116, 130, 116, 'lnc'), text(160, 134, 'response', 'xs')]
b += [arrow(430, 80, 490, 80, 'lna'), text(460, 72, 'command', 'xs')]
b += [arrow(490, 116, 430, 116, 'lnc'), text(460, 134, 'response', 'xs')]
# target
b += [rect(490, 34, 260, 100, 'dl'), text(620, 54, 'Target: NVM subsystem', 's h')]
b += [rect(500, 66, 126, 56, 'box'), text(563, 84, 'Controller', 's h'), text(563, 99, 'admin + I/O queues', 'xs d'), text(563, 113, 'one connection each', 'xs d')]
b += [rect(636, 66, 106, 56, 'box'), text(689, 88, 'Namespaces', 's h'), text(689, 104, 'NVM, ZNS sets', 'xs d')]
# backend
b += [arrow(620, 134, 620, 150, 'lnc')]
b += [rect(490, 150, 260, 84, 'pl'), text(620, 168, 'Backend behind the target', 's h')]
for i, s in enumerate(['SSD behind a software target', 'array controller', 'DPU or bridge in a JBOF/EBOF', 'rarely an SSD with a native fabric port']):
    b += [text(620, 184 + i * 13, s, 'xs')]
# bring-up
b += [text(10, 262, 'Bring-up before any I/O', 's h', 'start')]
steps = [(10, 'Discovery', 'read the discovery log from', 'a discovery controller'),
         (272, 'Connect: admin queue', 'of the chosen subsystem', 'one connection'),
         (534, 'Connect: each I/O queue', 'of the same subsystem', 'one connection per queue')]
for i, (x, t1, t2, t3) in enumerate(steps):
    b += [rect(x, 270, 216, 54, 'tl'), text(x + 108, 288, t1, 's h'), text(x + 108, 302, t2, 'xs'), text(x + 108, 315, t3, 'xs d')]
b += [arrow(226, 297, 272, 297, 'lna'), arrow(488, 297, 534, 297, 'lna')]
# capsule format
b += [text(10, 346, 'Capsule format (not to scale)', 's h', 'start')]
b += [text(10, 374, 'Command capsule', 's', 'start')]
b += [rect(150, 354, 170, 40, 'tl'), text(235, 371, 'SQE, 64 B', 's h'), text(235, 385, 'the NVMe command', 'xs d')]
b += [rect(320, 354, 250, 40, 'grp'), text(445, 371, 'in-capsule data', 's h'), text(445, 385, 'optional', 'xs d')]
b += [text(10, 428, 'Response capsule', 's', 'start')]
b += [rect(150, 408, 100, 40, 'dl'), text(200, 425, 'CQE, 16 B', 's h'), text(200, 439, 'the completion', 'xs d')]
b += [text(290, 423, 'Bulk data is not in the capsule. It moves by', 'xs d', 'start'), text(290, 437, 'RDMA Read/Write or TCP data PDUs.', 'xs d', 'start')]
add('fabrics', 'NVMe over Fabrics: same commands, new transport',
    'Amber is the host side, blue the target side. The 64-byte command and 16-byte completion are the same as over PCIe; a capsule simply carries them in a network message, and each queue gets its own Connect. Widths in the capsule strips are not to scale.',
    svg(760, 456, 'NVMe over Fabrics path, bring-up sequence and capsule format', ''.join(b)))

# ------------------------------------------------------------------ fdp
b = []
b += [text(10, 18, 'Conventional SSD: hot and cold writes share one open block', 's h', 'start')]
b += [rect(506, 28, 12, 12, 'tl', 2), text(526, 38, 'hot, short-lived data', 'xs', 'start')]
b += [rect(506, 46, 12, 12, 'dl', 2), text(526, 56, 'cold, long-lived data', 'xs', 'start')]
pattern = 'HCHHCHCH'
b += [text(10, 56, 'written together', 's', 'start')]
for i, c in enumerate(pattern):
    b += [rect(150 + i * 42, 34, 38, 30, 'tl' if c == 'H' else 'dl', 3), text(169 + i * 42, 54, c, 's h')]
b += [text(10, 108, 'after hot data dies', 's', 'start')]
for i, c in enumerate(pattern):
    if c == 'H':
        b += [rect(150 + i * 42, 86, 38, 30, 'er', 3), text(169 + i * 42, 106, 'x', 's d')]
    else:
        b += [rect(150 + i * 42, 86, 38, 30, 'dl', 3), text(169 + i * 42, 106, 'C', 's h')]
b += [text(506, 92, 'garbage collection must copy the', 'xs d', 'start'), text(506, 106, 'cold survivors before it can', 'xs d', 'start'), text(506, 120, 'erase this block', 'xs d', 'start')]
b += [line(10, 138, 750, 138, 'ln')]

b += [text(10, 160, 'FDP (enabled per Endurance Group): the host names a placement identifier', 's h', 'start')]
# host writes
b += [text(80, 190, 'Write command', 's h'), text(80, 204, 'DTYPE=2, DSPEC=PID', 'xs d')]
b += [rect(10, 214, 140, 54, 'tl'), text(80, 234, 'hot write', 's h'), text(80, 248, 'PID 0003h', 'xs'), text(80, 261, 'RG0, handle 3', 'xs d')]
b += [rect(10, 280, 140, 54, 'tl'), text(80, 300, 'cold write', 's h'), text(80, 314, 'PID 0004h', 'xs'), text(80, 327, 'RG0, handle 4', 'xs d')]
# RUHs
b += [text(255, 190, 'RUHs', 's h'), text(255, 204, 'point at the open RU', 'xs d')]
b += [rect(195, 214, 120, 54, 'dl'), text(255, 236, 'RUH', 's h'), text(255, 252, 'placement handle 3', 'xs d')]
b += [rect(195, 280, 120, 54, 'dl'), text(255, 302, 'RUH', 's h'), text(255, 318, 'placement handle 4', 'xs d')]
b += [arrow(150, 241, 195, 241, 'lna'), arrow(150, 307, 195, 307, 'lna')]
# RG0
b += [rect(365, 174, 205, 172, 'grp'), text(467, 192, 'Reclaim group RG0', 's h')]
b += [arrow(315, 241, 380, 241, 'lnc'), arrow(315, 307, 380, 307, 'lnc')]
b += [rect(380, 214, 176, 54, 'box'), text(468, 229, 'reclaim unit: hot only', 'xs d')]
for i in range(4):
    b += [rect(390 + i * 30, 238, 26, 20, 'tl', 2), text(403 + i * 30, 252, 'H', 'xs h')]
b += [rect(510, 238, 36, 20, 'grp', 2)]
b += [rect(380, 280, 176, 54, 'box'), text(468, 295, 'reclaim unit: cold only', 'xs d')]
for i in range(3):
    b += [rect(390 + i * 30, 304, 26, 20, 'dl', 2), text(403 + i * 30, 318, 'C', 'xs h')]
b += [rect(480, 304, 66, 20, 'grp', 2)]
# RG1
b += [rect(585, 174, 165, 172, 'grp'), text(667, 192, 'Reclaim group RG1', 's h')]
b += [rect(597, 214, 141, 54, 'box'), text(667, 246, 'reclaim unit', 'xs d')]
b += [rect(597, 280, 141, 54, 'box'), text(667, 312, 'reclaim unit', 'xs d')]
# result
b += [rect(10, 358, 560, 66, 'pl')]
b += [text(24, 378, 'Each lifetime class fills its own RU, so a whole RU tends to die together.', 'xs', 'start'),
      text(24, 394, 'Reclaim then finds a mostly invalid RU and cold data is not dragged along.', 'xs', 'start'),
      text(24, 410, 'Reclaim is still the controller job: the host cannot erase or reset an RU.', 'xs d', 'start')]
b += [rect(585, 358, 165, 66, 'box'), text(667, 380, 'PID 8003h = handle 3', 'xs'), text(667, 394, 'in RG1 (2 RGs, RGIF = 1:', 'xs d'), text(667, 408, 'RG in the top bit)', 'xs d')]
add('fdp', 'FDP: placement identifiers versus mixed writes',
    'Amber is short-lived (hot) data and blue is long-lived (cold). Without FDP the two interleave in one block and GC copies the cold survivors. With FDP the PID in each write picks a reclaim group and a handle, so each lifetime class lands in its own reclaim unit.',
    svg(760, 436, 'Mixed writes in one block versus Flexible Data Placement reclaim groups, reclaim units and handles', ''.join(b)))

# ------------------------------------------------------------------ ftl
b = []
# host + L2P
b += [rect(10, 20, 180, 46, 'tl'), text(100, 40, 'Host', 'h'), text(100, 56, 'write LBA 100', 'xs')]
b += [arrow(100, 66, 100, 110, 'lna')]
b += [rect(10, 110, 180, 160, 'dl'), text(100, 130, 'FTL: L2P table', 's h'), text(100, 144, 'held in DRAM', 'xs d')]
b += [rect(38, 156, 140, 30, 'tl'), text(108, 176, 'L2P[100] = P1', 's h')]
b += [text(100, 204, 'before the write: P0', 'xs d')]
b += [text(100, 236, 'a read looks up this', 'xs d'), text(100, 250, 'entry first', 'xs d')]
# NAND blocks
b += [rect(240, 34, 250, 90, 'box'), text(365, 52, 'Block X (older data)', 'xs h')]
for i in range(8):
    cls = 'er' if i == 2 else 'pl'
    b += [rect(252 + i * 29, 62, 25, 28, cls, 3)]
    if i == 2:
        b += [text(252 + i * 29 + 12.5, 80, 'P0', 'xs h')]
b += [text(365, 112, 'P0: invalid, still in NAND', 'xs rd')]
b += [rect(240, 170, 250, 90, 'box'), text(365, 188, 'Open block Y', 'xs h')]
for i in range(8):
    x = 252 + i * 29
    if i < 3:
        b += [rect(x, 198, 25, 28, 'pl', 3)]
    elif i == 3:
        b += [rect(x, 198, 25, 28, 'tl', 3), text(x + 12.5, 216, 'P1', 'xs h')]
    else:
        b += [rect(x, 198, 25, 28, 'grp', 3)]
b += [text(365, 248, 'P1: newest copy, valid', 'xs ac')]
b += [arrow(190, 212, 240, 212, 'lna')]
b += [poly_arrow([(190, 140), (215, 140), (215, 79), (240, 79)], 'lnr')]
b += badge(215, 110, 3)
b += badge(215, 190, 1)
b += badge(24, 171, 2)
# GC flow
b += [text(520, 24, 'Later: garbage collection', 's h', 'start')]
gc_steps = [('Pick a victim block', 'most of its pages invalid', 'pl'),
            ('Copy the valid pages', 'valid = L2P still points here', 'pl'),
            ('Update L2P', 'for each page that moved', 'dl'),
            ('Erase the victim', 'block joins the free pool', 'pl')]
for i, (t1, t2, c) in enumerate(gc_steps):
    y = 34 + i * 62
    b += [rect(520, y, 230, 46, c), text(635, y + 20, t1, 's h'), text(635, y + 36, t2, 'xs d')]
    if i < 3:
        b += [arrow(635, y + 46, 635, y + 62, 'lna')]
# read badge (4) shown in the L2P box
b += badge(24, 243, 4)
# legend text
b += [rect(10, 290, 740, 104, 'box')]
lg = [('1', 'The FTL takes the next free page P1 in the open block and programs the new data there.'),
      ('2', 'L2P[100] changes from P0 to P1.'),
      ('3', 'The old copy P0 is marked invalid. Nothing is erased; P0 stays in NAND.'),
      ('4', 'A read of LBA 100 uses L2P[100] to find P1. An unmapped entry needs no NAND read.'),
      ('', 'Each page also stores its LBA, so GC can compare it with the L2P entry.')]
for i, (n, s) in enumerate(lg):
    y = 310 + i * 18
    if n:
        b += [text(24, y, n, 's h ac', 'start')]
    b += [text(42, y, s, 'xs', 'start')]
add('ftl', 'FTL: write somewhere else, invalidate the old copy',
    'A write programs a new page and repoints the L2P entry, which turns the old page invalid without erasing anything. Green pages are valid, red is invalid, amber is the newest copy and dashed cells are free. GC reclaims blocks later.',
    svg(760, 406, 'Logical to physical mapping, out-of-place write, and the garbage collection flow', ''.join(b)))

# ------------------------------------------------------------------ gc
N = 8
valid = 6
invalid = N - valid
u = valid / N
gc_copies = valid
freed = N - valid
host_pages = freed
nand_writes = gc_copies + host_pages
waf = nand_writes / host_pages
assert (N, valid, invalid) == (8, 6, 2) and u == 0.75
assert freed == 2 and nand_writes == 8 and waf == 4.0 and abs(1 / (1 - u) - 4.0) < 1e-12
table = [(uu, 1 / (1 - uu)) for uu in (0.0, 0.5, 0.75, 0.9)]
assert [round(w, 1) for _, w in table] == [1.0, 2.0, 4.0, 10.0]

b = []
PX = [10, 275, 540]
titles = [('Victim block', 'N = 8: 6 valid, 2 invalid'),
          ('New block (GC target)', 'takes the 6 valid pages'),
          ('Same block, filled', '2 host pages arrive')]
for x, (t1, t2) in zip(PX, titles):
    b += [text(x + 87, 20, t1, 's h'), text(x + 87, 34, t2, 'xs d')]
vic = 'VVIVVVIV'
assert vic.count('V') == valid and vic.count('I') == invalid and len(vic) == N
for i, c in enumerate(vic):
    x = PX[0] + i * 22
    b += [rect(x, 44, 20, 24, 'pl' if c == 'V' else 'er', 2)]
for i in range(N):
    x = PX[1] + i * 22
    b += [rect(x, 44, 20, 24, 'dl' if i < gc_copies else 'grp', 2)]
for i in range(N):
    x = PX[2] + i * 22
    b += [rect(x, 44, 20, 24, 'dl' if i < gc_copies else 'tl', 2)]
b += [text(PX[0] + 87, 86, 'u = %d / %d = %.2f' % (valid, N, u), 's ac')]
b += [text(PX[0] + 87, 100, 'then erased: block is free', 'xs gr')]
b += [text(PX[1] + 87, 86, '%d NAND writes, no host data' % gc_copies, 'xs')]
b += [text(PX[2] + 87, 86, 'room gained %d - %d = %d pages' % (N, valid, freed), 'xs')]
b += [arrow(184, 56, 275, 56, 'lna'), text(229, 48, 'copy %d valid' % valid, 'xs')]
b += [arrow(449, 56, 540, 56, 'lna'), text(494, 48, 'host: %d pages' % host_pages, 'xs')]
# legend
lx = 10
for cls, lab, w in [('pl', 'valid', 80), ('er', 'invalid', 90), ('dl', 'GC copy', 100), ('tl', 'host write', 120), ('grp', 'free', 80)]:
    b += [rect(lx, 114, 12, 12, cls, 2), text(lx + 18, 124, lab, 'xs', 'start')]
    lx += w
# ledger
b += [rect(10, 144, 360, 152, 'box'), text(190, 164, 'Count the NAND writes', 's h')]
b += [text(26, 188, 'GC copies of valid pages', 'xs', 'start'), text(354, 188, str(gc_copies), 's h', 'end')]
b += [text(26, 206, 'host pages written', 'xs', 'start'), text(354, 206, str(host_pages), 's h', 'end')]
b += [line(26, 214, 354, 214, 'ln')]
b += [text(26, 230, 'NAND writes = %d + %d' % (gc_copies, host_pages), 'xs', 'start'), text(354, 230, str(nand_writes), 's h', 'end')]
b += [text(26, 248, 'host writes', 'xs', 'start'), text(354, 248, str(host_pages), 's h', 'end')]
b += [text(190, 276, 'WAF = %d / %d = %d = 1 / (1 - %.2f)' % (nand_writes, host_pages, waf, u), 's h ac')]
# WAF vs u bars
b += [text(400, 164, 'WAF = 1 / (1 - u)', 's h', 'start'), text(750, 164, 'u = victim valid fraction', 'xs d', 'end')]
for i, (uu, w) in enumerate(table):
    y = 178 + i * 28
    hi = abs(uu - 0.75) < 1e-9
    b += [text(400, y + 15, 'u = %.2f' % uu, 'xs h' if hi else 'xs', 'start')]
    b += [rect(466, y, w * 24, 20, 'tl' if hi else 'dl', 2), text(466 + w * 24 + 8, y + 15, '%.1f' % w, 's h' if hi else 's', 'start')]
add('gc', 'Write amplification from the GC victim valid fraction',
    'One 8-page victim block with 6 valid pages: GC copies 6, the erase nets 2 free pages, 2 host pages fill them, so 8 NAND writes serve 2 host writes and WAF = 8 / 2 = 4. The bars show WAF = 1/(1-u); the u = 0.75 case is highlighted.',
    svg(760, 306, 'Worked write amplification example with valid and invalid pages in a GC victim block', ''.join(b)))

# ------------------------------------------------------------------ latstack
host_us, pcie_us, fw_us, nand_us = 6, 3, 7, 66
total = host_us + pcie_us + fw_us + nand_us
assert total == 82
tR, xfer, ecc = 60, 3.6, 2.5
assert abs(tR + xfer + ecc - nand_us) < 0.2
assert abs(4480 / 7.88e3 - 0.57) < 0.01  # 4,480 B / 7.88 GB/s in us
assert abs(4300 / 1.2e3 - xfer) < 0.05     # about 4.3 KB at 1.2 GB/s
assert round(100 * nand_us / total) == 80

b = []
b += [text(20, 20, 'One 4 KiB random read at QD1: about %d us (illustrative TLC drive, Gen4 x4)' % total, 's h', 'start')]
k = 720.0 / total
x = 20.0
segs = [('Host', host_us, 'tl'), ('PCIe', pcie_us, 'box'), ('FW', fw_us, 'dl'), ('NAND', nand_us, 'pl')]
pos = {}
for name, us, cls in segs:
    w = us * k
    pos[name] = (x, w)
    b += [rect(round(x, 1), 56, round(w, 1), 40, cls, 2)]
    x += w
hx, hw = pos['Host']
b += [text(hx + hw / 2, 74, 'Host', 's h'), text(hx + hw / 2, 88, '%d us' % host_us, 'xs')]
px, pw = pos['PCIe']
b += [text(px + pw / 2, 48, 'PCIe %d us' % pcie_us, 'xs')]
fx, fw_ = pos['FW']
b += [text(fx + fw_ / 2, 74, 'FW', 's h'), text(fx + fw_ / 2, 88, '%d us' % fw_us, 'xs')]
nx, nw = pos['NAND']
b += [text(nx + nw / 2, 74, 'NAND %d us' % nand_us, 's h'), text(nx + nw / 2, 88, 'about 80 percent of the total', 'xs d')]
# zoom lines
b += [line(round(nx, 1), 96, 20, 160, 'lnd'), line(740, 96, 740, 160, 'lnd')]
k2 = 720.0 / (tR + xfer + ecc)
w1, w2, w3 = tR * k2, xfer * k2, ecc * k2
b += [rect(20, 160, round(w1, 1), 36, 'pl', 2), text(20 + w1 / 2, 182, 'tR about %d us (array read)' % tR, 's h')]
b += [rect(round(20 + w1, 1), 160, round(w2, 1), 36, 'pl', 2), rect(round(20 + w1 + w2, 1), 160, round(w3, 1), 36, 'pl', 2)]
xc = 20 + w1 + w2 / 2
ec = 20 + w1 + w2 + w3 / 2
b += [line(round(xc, 1), 196, round(xc, 1), 214, 'ln'), text(round(xc + 6, 1), 226, 'channel transfer %.1f us' % xfer, 'xs', 'end')]
b += [line(round(ec, 1), 196, round(ec, 1), 244, 'ln'), text(round(ec + 6, 1), 256, 'ECC decode %.1f us' % ecc, 'xs', 'end')]
b += [text(20, 226, 'NAND zoomed to full width:', 'xs d', 'start'), text(20, 240, 'tR + transfer + ECC = about %d us' % nand_us, 'xs d', 'start')]
# tail boxes
b += [text(20, 288, 'Where the tail comes from, by layer', 's h', 'start')]
cols = [('Host software', '6 us', 'tl', ['interrupt moderation', 'CPU C-states', 'softirq scheduling']),
        ('PCIe', '3 us', 'box', ['replay or retrain', 'adds microseconds', 'to milliseconds']),
        ('Controller FW', '7 us', 'dl', ['housekeeping, GC work', 'journal or checkpoint', 'error handling']),
        ('NAND', '66 us', 'pl', ['read retry: about 60 us', 'more per attempt', 'read stuck behind a', 'program or erase'])]
for i, (nm, us, cls, lines_) in enumerate(cols):
    cx = 20 + i * 183
    b += [rect(cx, 298, 171, 98, cls), text(cx + 85, 316, '%s  %s' % (nm, us), 's h')]
    for j, s in enumerate(lines_):
        b += [text(cx + 85, 334 + j * 14, s, 'xs d')]
add('latstack', 'Latency budget for a 4 KiB random read',
    'Segment widths are to scale. Amber is host software, the dark unfilled segment is PCIe, blue is controller firmware and hardware, green is NAND. At QD1 the media dominates, and the tail comes from events that add whole NAND operations, such as retries or a wait behind a program or erase.',
    svg(760, 408, 'Latency budget stack for a 4 KiB random read across host, PCIe, controller and NAND', ''.join(b)))

dlib.write(os.path.dirname(os.path.abspath(__file__)), 'diagrams_D.js')
