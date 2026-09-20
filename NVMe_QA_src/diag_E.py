#!/usr/bin/env python3
"""Part E diagrams for the NVMe study page: swstack (19.01), valpyramid (20.01), triage (21.01)."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'study_common'))
import dlib
from dlib import rect, text, line, arrow, poly_arrow, svg, add

XS, S, D = 5.7, 6.3, 7.3


def chk(s, cls, avail, what=''):
    """assert a string fits the available width (px)"""
    per = XS if 'xs' in cls.split() else S
    if 'h' in cls.split():
        per *= 1.06
    w = len(s) * per
    assert w <= avail, f'text too wide ({w:.0f} > {avail}): {s}'


def T(x, y, s, cls='', anchor='middle', avail=None):
    if avail:
        chk(s, cls, avail)
    return text(x, y, s, cls, anchor)


def dot(x, y, r=3.5):
    return f'<circle class="ah" cx="{x}" cy="{y}" r="{r}"/>'


# ------------------------------------------------------------------ swstack
b = []
LX, LW = 150, 260           # layer column
RX = LX + LW                # right edge of layers = 410
layers = [
    ('Applications and filesystems', None, 40, 44),
    ('Block layer with blk-mq', 'requests, one hctx per NVMe queue', 100, 44),
    ('nvme-core (nvme_core.ko)', 'state machine, Identify, ioctls', 160, 76),
    ('nvme PCIe transport (nvme.ko)', 'BAR0, queues, doorbells, MSI-X', 252, 44),
    ('PCI core', 'enumeration, hot-plug, AER, resets', 312, 44),
]
# dashed group around the host stack
b += [rect(LX - 10, 22, LW + 24, 346, 'grp', 8)]
b += [T(LX - 4, 15, 'Linux host stack', 'xs d', 'start')]
for i, (nm, sub, y, h) in enumerate(layers):
    b += [rect(LX, y, LW, h, 'tl')]
    if sub:
        b += [T(LX + LW / 2, y + h / 2 - 3, nm, 's h', avail=LW - 12), T(LX + LW / 2, y + h / 2 + 11, sub, 'xs d', avail=LW - 12)]
    else:
        b += [T(LX + LW / 2, y + h / 2 + 4, nm, 's h', avail=LW - 12)]
for i in range(4):
    y1 = layers[i][2] + layers[i][3]
    y2 = layers[i + 1][2]
    b += [line(LX + LW / 2, y1, LX + LW / 2, y2, 'ln')]
# SSD
b += [rect(10, 386, RX - 10, 40, 'dl'), T((10 + RX) / 2, 411, 'NVMe SSD', 'h')]
b += [line(LX + LW / 2, 356, LX + LW / 2, 386, 'ln')]

# SPDK bypass
b += [rect(10, 40, 108, 56, 'box')]
b += [T(64, 58, 'SPDK', 's h'), T(64, 73, 'user-space', 'xs d'), T(64, 87, 'driver', 'xs d')]
b += [arrow(30, 96, 30, 386, 'lnd')]
for i, s in enumerate(['via VFIO,', 'bypasses the', 'kernel nvme', 'path']):
    b += [T(42, 190 + i * 13, s, 'xs d', 'start', avail=96)]

# tools column
TX, TW, TH = 456, 296, 38
tools = [
    ('fio, filesystem tests', 'top: block device or file, end to end'),
    ('blktrace, block tracepoints', 'block layer, above the driver'),
    ('nvme-cli, passthrough', 'ioctl on /dev/nvmeX char devices'),
    ('sysfs, /proc/interrupts', 'controller, queue and IRQ mapping state'),
    ('ftrace nvme events', 'inside nvme-core: setup and completion'),
    ('dmesg, journalctl -k', 'printk from nvme-core, nvme, PCI core'),
    ('perf, bpftrace', 'kprobes and tracepoints at any layer'),
]
tops = [40 + 46 * i for i in range(7)]
for (nm, sub), ty in zip(tools, tops):
    b += [rect(TX, ty, TW, TH, 'box'), T(TX + TW / 2, ty + 16, nm, 's h', avail=TW - 12), T(TX + TW / 2, ty + 30, sub, 'xs d', avail=TW - 12)]
cy = [t + TH / 2 for t in tops]
taps = [
    [(RX, 62)],                 # fio -> top layer
    [(RX, 122)],                # blktrace -> block layer
    [(RX, 172)],                # nvme-cli -> nvme-core
    [(RX, 192)],                # sysfs -> nvme-core
    [(RX - 14, 210)],           # ftrace inside nvme-core
    [(RX, 224), (RX, 276), (RX, 336)],   # dmesg -> nvme-core, nvme, PCI core
    [(RX + 12, 352)],           # perf -> anywhere (group outline)
]
for c, ts in zip(cy, taps):
    for (x, y) in ts:
        b += [line(TX, c, x, y, 'ln'), dot(x, y)]

add('swstack', 'Linux NVMe host stack and tool tap points',
    'Each tool sees only what crosses the layer where it attaches. Amber layers are the kernel host path, blue is the SSD, and dots mark where each tool taps in. The dashed path is SPDK, which bypasses the kernel nvme driver through VFIO.',
    svg(760, 436, 'Linux NVMe host stack layers with the tools that tap into each layer', ''.join(b)))

# ---------------------------------------------------------------- valpyramid
b = []
CX = 196
Y0 = 34
RH, GAP = 62, 4
YB = Y0 + 5 * (RH + GAP) - GAP
WT, WB = 176, 372


def wid(y):
    return WT + (WB - WT) * (y - Y0) / (YB - Y0)


rows = [
    ('System and platform', 'real hosts, OSes, workloads', 'turn: days to weeks', 'dl',
     ['interop with real BIOS, OS, drivers, RAID and HBAs,', 'long soak, compliance'],
     'root cause: shows the symptom, not the layer'),
    ('Silicon characterization', 'timing, NAND and PHY behavior', 'turn: days', 'dl',
     ['PHY and link margin, NAND timing and error rates,', 'power, thermal, ECC margin'],
     'rare host behaviors you have not plugged in'),
    ('Emulation or FPGA with RTL', 'firmware on real RTL', 'turn: hours, MHz-class speed', 'tl',
     ['HW/FW interface bugs, DMA and doorbell races,', 'register semantics, PCIe MAC behavior'],
     'real NAND, real PHY, full-speed performance'),
    ('FW simulation', 'virtual controller and NAND model', 'turn: minutes', 'tl',
     ['command flow, FTL and GC logic, exhaustive power-cut', 'points, error injection, deterministic replay'],
     'real latencies, HW quirks, NAND analog behavior'),
    ('Unit', 'host-compiled firmware, mocked HW', 'turn: seconds, every commit', 'tl',
     ['logic and boundary bugs in parsers, FTL algorithms,', 'ECC math, state machines'],
     'timing, real HW registers, multi-core concurrency'),
]
b += [T(CX, 16, 'layer, what it runs, turn time', 'xs d')]
b += [T(400, 16, 'what it catches, and what it is blind to', 'xs d', 'start')]
for i, (nm, desc, turn, cls, catch, blind) in enumerate(rows):
    yt = Y0 + i * (RH + GAP)
    yb = yt + RH
    hw_t, hw_b = wid(yt) / 2, wid(yb) / 2
    pts = f'{CX - hw_t:.1f},{yt} {CX + hw_t:.1f},{yt} {CX + hw_b:.1f},{yb} {CX - hw_b:.1f},{yb}'
    b += [f'<polygon class="{cls}" points="{pts}"/>']
    # text must fit at its own baseline
    for s, cl, dy in [(nm, 's h', 21), (desc, 'xs d', 37), (turn, 'xs ac', 52)]:
        wy = wid(yt + dy - 9)
        chk(s, cl, wy - 16)
        b += [T(CX, yt + dy, s, cl)]
    b += [T(400, yt + 20, 'catches', 'xs h gr', 'start'), T(458, yt + 20, catch[0], 'xs', 'start', avail=298),
          T(458, yt + 33, catch[1], 'xs', 'start', avail=298),
          T(400, yt + 52, 'blind to', 'xs h rd', 'start'), T(458, yt + 52, blind, 'xs d', 'start', avail=298)]
b += [T(20, 382, 'Test count and speed grow toward the base. Cost per bug and turn time grow toward the top.', 's d', 'start', avail=730)]
b += [T(20, 400, 'Rule: push every bug to the lowest layer that can reproduce it.', 's d', 'start', avail=730)]
add('valpyramid', 'The validation pyramid',
    'Many fast tests sit at the base, few slow ones at the top. Amber layers run before real silicon exists, blue layers run on real hardware. Each layer catches a class of bug the others cannot, and finds it cheaper than the next one up.',
    svg(760, 412, 'Validation pyramid from unit test at the base to system test at the top, with what each layer catches and misses', ''.join(b)))

# -------------------------------------------------------------------- triage
b = []
C1X, C1W = 8, 192           # decision column 1
C2X, C2W = 234, 180         # decision column 2
LFX, LFW = 548, 204         # leaves
LH = 32


def step(x, y, w, h, l1, l2=None, l3=None):
    s = [rect(x, y, w, h, 'box')]
    cx, cy_ = x + w / 2, y + h / 2
    lines = [(l1, 's h')] + ([(l2, 'xs d')] if l2 else []) + ([(l3, 'xs d')] if l3 else [])
    n = len(lines)
    ys = [cy_ + (k - (n - 1) / 2) * 13 + 4 for k in range(n)]
    for (t, cl), yy in zip(lines, ys):
        s += [T(cx, yy, t, cl, avail=w - 12)]
    return s


def leaf(y, cls, l1, l2=None):
    s = [rect(LFX, y - LH / 2, LFW, LH, cls)]
    if l2:
        s += [T(LFX + LFW / 2, y - 2, l1, 's h', avail=LFW - 12), T(LFX + LFW / 2, y + 10, l2, 'xs d', avail=LFW - 12)]
    else:
        s += [T(LFX + LFW / 2, y + 4, l1, 's h', avail=LFW - 12)]
    return s


AC = {'er': 'lnr', 'tl': 'lna', 'dl': 'lnc', 'pl': 'lng'}
r = [21, 75, 129, 169, 209, 263, 316, 356, 409]
S1y, S2y = r[0] - LH / 2, r[1] - LH / 2
S3top, S3bot = r[2] - 17, r[4] + 17
# decision steps
b += step(C1X, S1y, C1W, LH, 'Step 1: function present?', 'config space Vendor ID, LnkSta')
b += step(C1X, S2y, C1W, LH, 'Step 2: controller alive?', 'CSTS and CC, after step 1')
b += step(C1X, S3top, C1W, S3bot - S3top, 'Step 3: commands complete?', 'and with which status type?')
b += step(C2X, r[5] - 17, C2W, 34, 'Step 4: timeout', 'CQE already in host memory?')
b += step(C2X, r[6] - 16, C2W, r[7] - r[6] + 32, 'Step 4: no CQE yet', 'was the SQE fetched?', 'analyzer or SSD log')
b += step(C2X, r[8] - 17, C2W, 34, 'Step 5: Success returned', 'is the data right?')
# continue arrows (neutral)
b += [arrow(C1X + 60, S1y + LH, C1X + 60, S2y, 'ln'), T(C1X + 68, S1y + LH + 14, 'valid ID', 'xs d', 'start')]
b += [arrow(C1X + 60, S2y + LH, C1X + 60, S3top, 'ln'), T(C1X + 68, S2y + LH + 14, 'CFS clear, RDY held', 'xs d', 'start')]
# leaves + exits from steps 1 and 2
leafs = [
    (0, 'er', 'Link', 'slot power, or device gone', 'No: config read returns all ones', C1X + C1W),
    (1, 'dl', 'Controller firmware', None, 'CFS = 1, or RDY fell unexpectedly', C1X + C1W),
    (2, 'pl', 'Media or FTL', None, 'SCT 2: media and data integrity failure', C1X + C1W),
    (3, 'er', 'Link or host memory path', None, 'status 04h Data Transfer Error: a DMA failed', C1X + C1W),
    (4, 'tl', 'Host', 'unless legal command rejected', 'status 01h, 02h, 0Bh: the command was wrong', C1X + C1W),
    (5, 'tl', 'Host interrupt path', 'or firmware signaling', 'yes: CQE is there', C2X + C2W),
    (6, 'er', 'Link, host BAR access', 'or firmware', 'no: no SQE fetch', C2X + C2W),
    (7, 'dl', 'Firmware or NAND stall', None, 'yes: fetched, no CQE', C2X + C2W),
    (8, 'pl', 'Media or FTL', 'or transport and host buffer', 'no: data is wrong', C2X + C2W),
]
for k, cls, l1, l2, lab, xs in leafs:
    y = r[k]
    b += leaf(y, cls, l1, l2)
    b += [arrow(xs, y, LFX, y, AC[cls])]
    mid = (xs + LFX) / 2
    b += [T(mid, y - 6, lab, 'xs d', avail=LFX - xs - 8)]
# step 3 -> step 4 (timeout) and step 3 -> step 5 (success)
b += [poly_arrow([(150, S3bot), (150, r[5]), (C2X, r[5])], 'ln'), T(192, r[5] - 6, 'timeout', 'xs d')]
b += [poly_arrow([(60, S3bot), (60, r[8]), (C2X, r[8])], 'ln'), T(147, r[8] - 6, 'Success', 'xs d')]
# step 4 -> step 4b
b += [arrow(C2X + 90, r[5] + 17, C2X + 90, r[6] - 16, 'ln'), T(C2X + 98, r[5] + 17 + 13, 'no CQE', 'xs d', 'start')]
# legend
lx, ly = 80, 296
b += [T(lx, ly, 'leaf color is the', 'xs d', 'start', avail=140), T(lx, ly + 12, 'first bucket named', 'xs d', 'start', avail=140)]
for i, (cls, nm) in enumerate([('tl', 'host'), ('er', 'link'), ('dl', 'controller'), ('pl', 'media')]):
    yy = ly + 22 + i * 16
    b += [rect(lx, yy, 16, 11, cls, 2), T(lx + 24, yy + 9, nm, 'xs', 'start')]
add('triage', 'Fault-isolation decision tree',
    'Ask in order and stop at the first question that answers. Steps 1 to 3 are cheap reads on the failing system, and the analyzer comes last. Leaf color is the first bucket named: amber host, red link, blue controller, green media.',
    svg(760, 436, 'Decision tree that sends a failing SSD to the host, link, controller or media bucket', ''.join(b)))

dlib.write(os.path.dirname(os.path.abspath(__file__)), 'diagrams_E.js')
