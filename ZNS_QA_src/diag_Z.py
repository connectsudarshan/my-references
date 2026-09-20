#!/usr/bin/env python3
"""Part Z diagrams for the ZNS page: conv_vs_zns, zonemodel, zstates, append, zoneres, zns_ftl, zrwa."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'study_common'))
import dlib
from dlib import rect, text, line, arrow, poly_arrow, svg, add, bracket, fld

ROOT = os.path.dirname(os.path.abspath(__file__))


def cells(x, y, kinds, w=18, gap=3, h=18, pad=6):
    """A block of page cells. kinds: 'h' hot, 'c' cold, 's' stale, 'e' empty."""
    n = len(kinds)
    tw = n * w + (n - 1) * gap + 2 * pad
    s = [rect(x, y, tw, h + 2 * pad, 'box', 4)]
    for i, k in enumerate(kinds):
        cx = x + pad + i * (w + gap)
        cls = {'h': 'tl', 'c': 'dl', 's': 'er', 'e': 'box'}[k]
        s.append(rect(cx, y + pad, w, h, cls, 2))
        if k == 's':
            s.append(text(cx + w / 2, y + pad + 13, 'x', 'xs rd'))
    return s, tw


# ---------------------------------------------------------------- conv_vs_zns
b = [rect(10, 32, 360, 304, 'grp'), rect(390, 32, 360, 304, 'grp'),
     text(190, 24, 'Conventional SSD', 'h'), text(570, 24, 'Zoned (ZNS) SSD', 'h')]
# left panel
b += [rect(30, 48, 320, 44, 'tl'), text(190, 67, 'Host: hot and cold data mixed', 's h'), text(190, 83, 'any LBA, any order, overwrite allowed', 'xs d')]
b += [rect(30, 112, 320, 44, 'dl'), text(190, 131, 'Device FTL decides placement', 's h'), text(190, 147, 'page-level L2P, GC, large over-provisioning', 'xs d')]
sa, wa = cells(30, 182, ['s', 'c', 's', 'h'])
sb, wb = cells(150, 182, ['c', 's', 's', 'c'])
b += sa + sb
b += [arrow(76, 156, 76, 182, 'lnc'), arrow(196, 156, 196, 182, 'lnc')]
b += [text(76, 228, 'block A', 'xs d'), text(196, 228, 'block B', 'xs d')]
sc, wc = cells(150, 268, ['c', 'h', 'c', 'c'])
b += sc
b += [poly_arrow([(76, 236), (76, 282), (150, 282)], 'lnr'), arrow(196, 236, 196, 268, 'lnr')]
b += [text(196, 314, 'block C', 'xs d')]
b += [text(255, 282, 'GC copies', 'xs rd', 'start'), text(255, 296, 'live pages,', 'xs rd', 'start'), text(255, 310, 'erases A and B', 'xs rd', 'start')]
# right panel
b += [rect(410, 48, 320, 44, 'tl'), text(570, 67, 'Host: places data by lifetime', 's h'), text(570, 83, 'writes sequentially at each write pointer', 'xs d')]
b += [rect(410, 112, 320, 44, 'dl'), text(570, 131, 'Device: zone to erase-block map', 's h'), text(570, 147, 'no overwrites seen, so no remap and no GC', 'xs d')]
za, wz = cells(440, 182, ['s', 's', 's', 's'])
zb, _ = cells(600, 182, ['c', 'c', 'c', 'e'])
b += za + zb
b += [arrow(486, 156, 486, 182, 'lnc'), arrow(646, 156, 646, 182, 'lnc')]
b += [text(486, 228, 'Zone 0: hot, all stale', 'xs d'), text(646, 228, 'Zone 1: cold, live', 'xs d')]
zc, _ = cells(440, 268, ['e', 'e', 'e', 'e'])
b += zc
b += [arrow(486, 236, 486, 268, 'lna'), text(498, 256, 'Reset Zone', 'xs ac', 'start')]
b += [text(646, 268, 'untouched: no copying', 'xs d'), text(646, 282, 'while its data lives', 'xs d')]
b += [text(570, 314, 'Zone 0 is empty again, zero pages copied', 'xs gr')]
# legend
lx = 200
b += [rect(lx, 348, 16, 14, 'tl', 2), text(lx + 22, 359, 'hot data', 'xs', 'start'),
      rect(lx + 100, 348, 16, 14, 'dl', 2), text(lx + 122, 359, 'cold data', 'xs', 'start'),
      rect(lx + 210, 348, 16, 14, 'er', 2), text(lx + 232, 359, 'stale (x)', 'xs', 'start')]
add('conv_vs_zns', 'Conventional versus zoned placement',
    'Left: the device mixes hot and cold pages in the same erase blocks, so GC must copy live pages before it can erase. Right: the host puts data of one lifetime in one zone, so resetting a dead zone frees it with nothing to copy. In the top boxes amber is the host and blue is the device.',
    svg(760, 372, 'Conventional SSD with mixed placement and garbage collection versus zoned placement with zone reset', ''.join(b)))

# ---------------------------------------------------------------- zonemodel
b = [text(40, 16, 'LBA space of the namespace, in increasing LBA order, zones back to back', 'xs d', 'start')]
ZW, CAPW, X0Z, YB, HB = 220, 150, 40, 62, 50
for i in range(3):
    x = X0Z + i * ZW
    b += [rect(x, YB, ZW, HB, 'box', 3)]
# zone 0: written 100, zone 1: written 60, zone 2: written to capacity
wr = [100, 60, CAPW]
for i in range(3):
    x = X0Z + i * ZW
    b += [rect(x, YB, wr[i], HB, 'dl', 3)]
    b += [rect(x + CAPW, YB, ZW - CAPW, HB, 'grp', 0), text(x + CAPW + (ZW - CAPW) / 2, YB + 29, 'not usable', 'xs f')]
    b += [text(x + wr[i] / 2, YB + 29, 'written' if i < 2 else 'written to capacity', 'xs')]
    b += [text(x + 4, YB + HB + 34, 'Zone %d' % i, 's h', 'start'),
          text(x + 4, YB + HB + 18, ['ZSLBA = 0', 'ZSLBA = 1 x ZSZE', 'ZSLBA = 2 x ZSZE'][i], 'xs d', 'start'),
          line(x, YB + HB, x, YB + HB + 8, 'ln')]
b += [line(X0Z + 3 * ZW, YB + HB, X0Z + 3 * ZW, YB + HB + 8, 'ln')]
# write pointers
for x, lab in ((X0Z + 100, 'WP of zone 0'), (X0Z + ZW + 60, 'WP of zone 1')):
    b += [arrow(x, 34, x, YB, 'lna'), text(x + 8, 32, lab, 'xs ac', 'start')]
b += [text(X0Z + 2 * ZW + 60, 32, 'Full: WP no longer valid', 'xs d', 'start')]
# brackets on zone 0
def lbr(x1, x2, y, label, cls):
    return [line(x1, y, x2, y, 'ln'), line(x1, y - 6, x1, y, 'ln'), line(x2, y - 6, x2, y, 'ln'), text(x1, y + 20, label, 's ' + cls, 'start')]
b += lbr(X0Z, X0Z + CAPW, 178, 'ZCAP: usable LBAs, counted from ZSLBA (at most ZSZE)', 'gr')
b += lbr(X0Z, X0Z + ZW, 226, 'ZSZE: LBAs the zone occupies in the address space', 'cy')
b += [text(X0Z, 282, 'Zone n starts at LBA n x ZSZE. ZSZE is the same for every zone. The write pointer moves only forward until Reset Zone.', 'xs d', 'start'),
      text(X0Z, 298, 'Blue is written, plain is writable up to ZCAP, dashed is the gap from ZCAP to ZSZE. Zone 2 is Full.', 'xs d', 'start')]
add('zonemodel', 'Zone size, zone capacity and the write pointer',
    'Each zone spans ZSZE LBAs but only the first ZCAP LBAs are usable. The write pointer marks the next LBA to write and only moves forward. Zone 2 has been filled to its capacity, so the zone is Full.',
    svg(760, 312, 'LBA space divided into three zones with zone size, zone capacity and write pointer', ''.join(b)))

# ---------------------------------------------------------------- zstates
b = []
b += [rect(10, 96, 610, 196, 'grp'), text(22, 112, 'Empty, open or Closed', 'xs f', 'start')]
b += [rect(220, 108, 190, 168, 'grp'), text(232, 122, 'open zones', 'xs f', 'start')]
b += [rect(30, 175, 110, 46, 'box'), text(85, 203, 'Empty', 's h')]
b += [rect(235, 132, 160, 40, 'dl'), text(315, 157, 'Implicitly Opened', 's h')]
b += [rect(235, 224, 160, 40, 'dl'), text(315, 249, 'Explicitly Opened', 's h')]
b += [rect(485, 165, 100, 66, 'box'), text(535, 202, 'Closed', 's h')]
b += [rect(690, 175, 60, 46, 'box'), text(720, 203, 'Full', 's h')]
b += [rect(140, 12, 130, 44, 'er'), text(205, 31, 'Read Only', 's h'), text(205, 46, 'no writes', 'xs d')]
b += [rect(455, 12, 130, 44, 'er'), text(520, 31, 'Offline', 's h'), text(520, 46, 'no reads or writes', 'xs d')]
# host-driven transitions
b += [arrow(140, 185, 235, 156, 'lna'), text(190, 157, 'Write, Append', 'xs ac', 'end')]
b += [arrow(140, 211, 235, 236, 'lna'), text(196, 246, 'Open Zone', 'xs ac', 'end')]
b += [arrow(315, 172, 315, 224, 'lna'), text(323, 202, 'Open Zone', 'xs ac', 'start')]
b += [arrow(410, 198, 485, 198, 'lna'), text(447, 190, 'Close Zone', 'xs ac')]
b += [arrow(485, 180, 395, 158, 'lna'), text(452, 162, 'Write', 'xs ac')]
b += [arrow(485, 216, 395, 236, 'lna'), text(440, 252, 'Open Zone', 'xs ac')]
b += [arrow(620, 198, 690, 198, 'lna'), text(655, 190, 'Finish Zone', 'xs ac')]
# reset bus
b += [line(720, 221, 720, 316, 'lna'), line(315, 276, 315, 316, 'lna'), line(535, 231, 535, 316, 'lna'),
      poly_arrow([(720, 316), (85, 316), (85, 221)], 'lna'),
      text(400, 338, 'Reset Zone from open, Closed or Full: WP becomes ZSLBA, zone is Empty', 'xs ac')]
# controller transitions and host Offline Zone
b += [arrow(270, 34, 455, 34, 'lna'), text(362, 26, 'Offline Zone', 'xs ac'), text(362, 50, 'host command', 'xs d')]
b += [arrow(205, 96, 205, 56, 'lnd'), text(213, 80, 'controller', 'xs d', 'start')]
b += [arrow(520, 96, 520, 56, 'lnd'), text(528, 80, 'controller', 'xs d', 'start')]
b += [text(20, 366, 'Finish Zone works from Empty, open and Closed zones. A write that reaches ZCAP also takes an open zone to Full.', 'xs d', 'start'),
      text(20, 381, 'The controller may close an Implicitly Opened zone to free an open resource. It never closes an Explicitly Opened one.', 'xs d', 'start'),
      text(20, 396, 'Dashed: the controller moves a zone to Read Only or Offline for media reasons (source states not drawn). Offline is terminal.', 'xs d', 'start')]
add('zstates', 'Zone state machine',
    'Host commands are amber, controller-initiated moves are dashed. Blue states are the two open states, red states are degraded. Only transitions the question states outright are drawn; edge cases such as Close on an Empty zone are left out.',
    svg(760, 408, 'Zone state machine with seven states and command-labelled transitions', ''.join(b)))

# ---------------------------------------------------------------- append
b = []
hosts = [(20, 'Append A', '8 LBAs', '0x1010'), (270, 'Append B', '16 LBAs', '0x1000'), (520, 'Append C', '8 LBAs', '0x1018')]
for x0, nm, ln_, alba in hosts:
    b += [rect(x0, 20, 220, 52, 'tl'), text(x0 + 110, 40, nm, 's h'), text(x0 + 110, 58, 'ZSLBA 0x1000, ' + ln_, 'xs d')]
    b += [arrow(x0 + 40, 72, x0 + 40, 128, 'lna'), text(x0 + 48, 104, 'submit', 'xs ac', 'start')]
    b += [arrow(x0 + 120, 128, x0 + 120, 72, 'lnc'), text(x0 + 128, 96, 'CQE:', 'xs cy', 'start'), text(x0 + 128, 110, 'ALBA ' + alba, 'xs cy', 'start')]
b += [rect(20, 128, 720, 48, 'dl'), text(380, 147, 'Controller owns the write pointer: appends may arrive in any order, from any queue', 's h'),
      text(380, 164, 'here it happens to process B, then A, then C, and places each at the current WP', 'xs d')]
# zone strip
YZ = 226
b += [rect(20, YZ, 90, 50, 'box', 3), text(65, YZ + 29, 'earlier data', 'xs d')]
b += [rect(110, YZ, 180, 50, 'dl', 3), text(200, YZ + 22, 'B', 's h'), text(200, YZ + 39, '0x1000 - 0x100F', 'xs')]
b += [rect(290, YZ, 90, 50, 'dl', 3), text(335, YZ + 22, 'A', 's h'), text(335, YZ + 39, '0x1010', 'xs')]
b += [rect(380, YZ, 90, 50, 'dl', 3), text(425, YZ + 22, 'C', 's h'), text(425, YZ + 39, '0x1018', 'xs')]
b += [rect(470, YZ, 270, 50, 'grp', 3), text(605, YZ + 29, 'unwritten, up to ZCAP', 'xs f')]
for x, lab in ((110, '0x1000'), (290, '0x1010'), (380, '0x1018'), (470, '0x1020')):
    b += [line(x, YZ + 50, x, YZ + 58, 'ln'), text(x, YZ + 71, lab, 'xs d')]
b += [text(110, YZ + 87, 'WP before', 'xs ac'), text(470, YZ + 87, 'WP after', 'xs ac')]
for x, lab in ((200, '1st'), (335, '2nd'), (425, '3rd')):
    b += [arrow(x, 176, x, YZ, 'lnc'), text(x + 8, 205, lab, 'xs d', 'start')]
b += [text(20, 346, 'LBAs are illustrative. The host chose neither the order nor the addresses: it learns each address from the CQE.', 'xs d', 'start'),
      text(20, 362, 'Every append names the zone start, not a write address, so none can fail because a peer moved the write pointer first.', 'xs d', 'start')]
add('append', 'Concurrent Zone Appends to one zone',
    'Three appends to the same zone are in flight at once. The controller serializes them at the write pointer and hands each one its address in the completion entry. Amber is the host, blue is the controller and device.',
    svg(760, 372, 'Three concurrent Zone Append commands to one zone, with the controller assigning LBAs returned in completion entries', ''.join(b)))

# ---------------------------------------------------------------- zoneres
b = []
b += [rect(10, 40, 150, 290, 'grp'), text(20, 58, 'hold no resource', 'xs f', 'start')]
for y, nm, cls in ((104, 'Empty', 'box'), (158, 'Full', 'box'), (212, 'Read Only', 'er'), (266, 'Offline', 'er')):
    b += [rect(20, y, 130, 44, cls), text(85, y + 27, nm, 's h')]
b += [rect(230, 40, 520, 290, 'grp'), text(240, 58, 'Active zones: count <= MAR', 's h ac', 'start')]
b += [rect(256, 72, 178, 228, 'grp'), text(266, 90, 'Open zones: count <= MOR', 'xs h cy', 'start')]
b += [rect(270, 104, 150, 44, 'dl'), text(345, 131, 'Implicitly Opened', 's h')]
b += [rect(270, 196, 150, 44, 'dl'), text(345, 223, 'Explicitly Opened', 's h')]
b += [rect(620, 140, 115, 90, 'box'), text(677, 176, 'Closed', 's h'), text(677, 194, 'keeps data', 'xs d'), text(677, 207, 'and WP', 'xs d')]
# zone moving between states
b += [arrow(150, 126, 270, 126, 'lna'), text(190, 100, 'Write or', 'xs ac'), text(190, 111, 'Open Zone', 'xs ac'), text(190, 141, '+1 active', 'xs d'), text(190, 152, '+1 open', 'xs d')]
b += [arrow(345, 148, 345, 196, 'lna'), text(353, 168, 'Open Zone', 'xs ac', 'start'), text(353, 181, '(no change)', 'xs d', 'start')]
b += [arrow(434, 156, 620, 156, 'lna'), text(527, 146, 'Close Zone', 'xs ac'), text(527, 172, 'frees 1 open, keeps 1 active', 'xs d')]
b += [arrow(620, 214, 434, 214, 'lna'), text(527, 205, 'Open Zone', 'xs ac'), text(527, 231, 'needs 1 free open resource', 'xs d'), text(527, 246, 'a Write here opens it implicitly', 'xs d')]
b += [text(20, 352, 'Open is a subset of active: every open zone also holds an active resource, and Closed zones are active but not open.', 'xs d', 'start'),
      text(20, 367, 'Two independent budgets. Out of active resources blocks new zones from starting, out of open resources blocks new writers.', 'xs d', 'start'),
      text(20, 382, 'Empty, Full, Read Only and Offline zones consume neither. Reaching Full, Reset or a controller fault releases what a zone held.', 'xs d', 'start')]
add('zoneres', 'Active versus open zones',
    'Two nested sets with two limits. Open zones (blue) are inside the active set, Closed zones are active but not open. Amber arrows show a zone moving between states and what each move takes or gives back.',
    svg(760, 392, 'Nested active and open zone sets with MAR and MOR limits and zone state moves between them', ''.join(b)))

# ---------------------------------------------------------------- zns_ftl
b = []
b += [rect(20, 14, 210, 46, 'tl'), text(125, 33, 'Zone k, as the host sees it', 's h'), text(125, 50, 'ZSLBA, ZSZE, ZCAP, WP, state', 'xs d')]
b += [rect(290, 14, 230, 46, 'dl'), text(405, 33, 'Write buffer', 's h'), text(405, 50, 'cut into program units', 'xs d')]
b += [rect(580, 14, 160, 46, 'dl'), text(660, 33, 'Per-zone record', 's h'), text(660, 50, 'state, WP, 48 blocks', 'xs d')]
b += [arrow(230, 37, 290, 37, 'lna')]
XC = [75 + i * 115 for i in range(6)]
b += [line(XC[0], 84, XC[-1], 84, 'ln'), arrow(405, 60, 405, 84, 'lnc'), arrow(660, 60, 660, 84, 'lnd')]
YA, YB2, DH = 126, 198, 58
for i, xc in enumerate(XC):
    b += [line(xc, 84, xc, 96, 'ln'), rect(xc - 30, 96, 60, 20, 'dl'), text(xc, 110, 'CH%d' % i, 'xs h'), line(xc, 116, xc, YB2 + DH, 'ln')]
for row, y in enumerate((YA, YB2)):
    for i, xc in enumerate(XC):
        b += [rect(xc - 50, y, 100, DH, 'box', 5), text(xc - 42, y + 15, 'Die %d' % row, 'xs', 'start'), text(xc + 44, y + 15, '#%d' % (row * 6 + i + 1), 'xs d', 'end')]
        for pl in range(4):
            b += [rect(xc - 42 + pl * 22, y + 28, 18, 18, 'pl', 2)]
b += [line(25, 270, 725, 270, 'ln'), line(25, 264, 25, 270, 'ln'), line(725, 264, 725, 270, 'ln'),
      text(375, 288, 'One zone = one erase block per plane on every die = 12 dies x 4 planes = 48 blocks = 768 MiB', 's gr')]
b += [rect(70, 304, 620, 46, 'er'), text(380, 324, 'Reset Zone: the block list returns to the free pool and all 48 blocks are erased', 's h'),
      text(380, 341, 'No block holds data of any other zone, so nothing has to be copied first', 'xs d')]
b += [text(20, 372, 'Example geometry: 6 channels x 2 dies, 4 planes per die, 16 MiB blocks. Layout and interleave are vendor specific.', 'xs d', 'start'),
      text(20, 387, 'Green squares are erase blocks, four per die (one per plane). #n is the order program units visit the dies in this illustration.', 'xs d', 'start')]
add('zns_ftl', 'A zone striped over dies and channels',
    'The host sees only zone start, size, capacity, WP and state. Inside, a zone is a stripe of erase blocks over every die, so sequential writes use all channels in parallel and Reset Zone releases and erases the whole set.',
    svg(760, 398, 'A zone mapped onto 12 dies over 6 channels as a stripe of 48 erase blocks that Reset Zone erases together', ''.join(b)))

# ---------------------------------------------------------------- zrwa
def strip(y, wp):
    """zone strip with committed / window / second region / beyond; wp = x of write pointer"""
    r = [rect(20, y, wp - 20, 50, 'dl', 3), text(20 + (wp - 20) / 2, y + 22, 'committed', 'xs h'), text(20 + (wp - 20) / 2, y + 38, 'no overwrite', 'xs d')]
    r += [rect(wp, y, 200, 50, 'tl', 3), text(wp + 100, y + 22, 'ZRWA window', 's h'), text(wp + 100, y + 38, 'any order, overwrite ok', 'xs d')]
    r += [rect(wp + 200, y, 200, 50, 'grp', 3), text(wp + 300, y + 22, 'second region', 's h'), text(wp + 300, y + 38, 'a write ending here flushes', 'xs d')]
    r += [rect(wp + 400, y, 740 - wp - 400, 50, 'er', 3), text(wp + 400 + (740 - wp - 400) / 2, y + 22, 'beyond', 's h'), text(wp + 400 + (740 - wp - 400) / 2, y + 38, 'Zone Invalid Write', 'xs d')]
    return r


def dim(x1, x2, y, label, cls='d'):
    return [line(x1, y, x2, y, 'ln'), line(x1, y, x1, y + 6, 'ln'), line(x2, y, x2, y + 6, 'ln'), text((x1 + x2) / 2, y - 6, label, 'xs ' + cls)]


b = [text(20, 14, 'Offsets from ZSLBA increase to the right. WP is the committed write pointer.', 'xs d', 'start')]
b += [text(20, 38, '1. Before', 's h', 'start')]
b += dim(120, 320, 56, 'ZRWASZ', 'ac') + dim(320, 520, 56, 'second region: size VERIFY')
b += strip(66, 120)
b += [arrow(120, 142, 120, 116, 'lna'), text(128, 136, 'WP', 'xs ac', 'start')]
b += [arrow(170, 116, 170, 226, 'lna'), text(182, 150, 'Flush Explicit ZRWA (Zone Send Action 11h)', 'xs ac', 'start'),
      text(182, 165, 'SLBA = last LBA to commit: [WP, SLBA] is committed,', 'xs d', 'start'),
      text(182, 178, 'WP becomes SLBA + 1 and the window slides up', 'xs d', 'start')]
b += [text(20, 210, '2. After the explicit flush', 's h', 'start')]
b += dim(200, 400, 216, 'ZRWASZ', 'ac') + dim(400, 600, 216, 'second region: size VERIFY')
b += strip(226, 200)
b += [arrow(200, 302, 200, 276, 'lna'), text(208, 296, 'new WP', 'xs ac', 'start')]
b += [text(20, 330, 'Committed data is sequential-only. Writes inside the window may come in any order and may overwrite until committed.', 'xs d', 'start'),
      text(20, 345, 'A write that reaches into the second region also moves WP (implicit flush), with no flush command from the host.', 'xs d', 'start'),
      text(20, 360, 'VERIFY: size of the second region, implicit-flush rounding (ZRWAFG units), and alignment rules for writes and flush ranges.', 'xs d', 'start')]
add('zrwa', 'ZRWA window and write pointer',
    'The window sits just above the committed write pointer. An explicit flush commits a range from WP up to the last LBA named, so WP moves up and the window slides with it. Amber is the writable window, blue is committed data, red is out of range.',
    svg(760, 372, 'Zone Random Write Area window above the write pointer, before and after an explicit flush', ''.join(b)))

dlib.write(ROOT, 'diagrams_Z.js')
