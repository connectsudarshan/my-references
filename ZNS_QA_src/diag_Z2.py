#!/usr/bin/env python3
"""Part Z2 diagrams for the ZNS page: zmgmt, zdesc, zwrite, zstack, zplan, zstore."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'study_common'))
import dlib
from dlib import rect, text, line, arrow, poly_arrow, svg, add

ROOT = os.path.dirname(os.path.abspath(__file__))


def table(x, y, cols, rows, head_cls='dl', rh=24, first_cls=None):
    """cols: [(title, width)]; rows: list of cell tuples. Returns svg parts and the table height."""
    s, cx = [], x
    for title, w in cols:
        s += [rect(cx, y, w, rh, head_cls, 2), text(cx + 8, y + 16, title, 's h', 'start')]
        cx += w
    for r, cells in enumerate(rows):
        cy, cx = y + rh * (r + 1), x
        for c, ((_, w), val) in enumerate(zip(cols, cells)):
            cls = first_cls if (c == 0 and first_cls) else 'box'
            s += [rect(cx, cy, w, rh, cls, 2), text(cx + 8, cy + 16, val, 'xs' + (' h' if c == 0 else ''), 'start')]
            cx += w
    return s, rh * (len(rows) + 1)


# ---------------------------------------------------------------- zmgmt
b = [rect(20, 12, 720, 46, 'tl'), text(380, 31, 'Zone Management Send (opcode 79h)', 'h'),
     text(380, 48, 'CDW10-11 SLBA = zone start LBA | CDW13 bits 7:0 ZSA, bit 8 Select All', 'xs d')]
cols = [('ZSA', 56), ('Action', 176), ('One zone: source -> target', 256), ('Select All acts on', 232)]
rows = [('01h', 'Close Zone', 'Open -> Closed', 'Implicitly + Explicitly Open'),
        ('02h', 'Finish Zone', 'Empty, Open, Closed -> Full', 'Open, Closed'),
        ('03h', 'Open Zone', 'Empty, Imp. Open, Closed -> Exp. Open', 'Closed (never Empty)'),
        ('04h', 'Reset Zone', 'Open, Closed, Full -> Empty, WP = ZSLBA', 'Open, Closed, Full'),
        ('05h', 'Offline Zone', 'Read Only -> Offline', 'Read Only'),
        ('10h', 'Set Zone Descr. Ext.', 'Empty -> Closed, writes extension data', 'not allowed'),
        ('11h', 'Flush Explicit ZRWA', 'commits ZRWA data up to SLBA', 'see ZRWA module')]
t, th = table(20, 72, cols, rows)
b += t
y = 72 + th + 16
b += [rect(20, y, 720, 104, 'dl'), text(380, y + 20, 'Zone Management Receive (opcode 7Ah)', 'h'),
      text(36, y + 42, 'ZRA 00h Report Zones, 01h Extended Report Zones (descriptors plus extensions)', 'xs', 'start'),
      text(36, y + 60, 'ZRAS filter: 00h all, 01h Empty, 02h Imp. Open, 03h Exp. Open, 04h Closed,', 'xs', 'start'),
      text(36, y + 76, '             05h Full, 06h Read Only, 07h Offline (ZNS 1.4 numbering)', 'xs', 'start'),
      text(36, y + 94, 'Partial Report = 1: Number of Zones counts only the descriptors returned', 'xs d', 'start')]
H = y + 104 + 14
add('zmgmt', 'Zone management actions',
    'Each Send action moves one zone from a set of source states to a target state; with Select All the controller applies it to every zone in those source states and skips the rest without error. Receive reads zone state back, optionally filtered by state.',
    svg(760, H, 'Zone Management Send actions with source and target states, Select All scope, and Zone Management Receive options', ''.join(b)))

# ---------------------------------------------------------------- zdesc
b = [text(20, 18, 'Report Zones data (all values little-endian, addresses in LBAs)', 's h', 'start')]
# header + descriptors strip
b += [rect(20, 28, 140, 44, 'tl', 3), text(90, 47, 'Header 64 B', 's h'), text(90, 63, 'bytes 7:0 = Nr Zones', 'xs d')]
b += [rect(166, 28, 140, 44, 'dl', 3), text(236, 47, 'Descriptor 0', 's h'), text(236, 63, '64 B', 'xs d')]
b += [rect(312, 28, 110, 44, 'grp', 3), text(367, 47, 'Extension 0', 's h'), text(367, 63, 'ZDES x 64 B', 'xs d')]
b += [rect(428, 28, 140, 44, 'dl', 3), text(498, 47, 'Descriptor 1', 's h'), text(498, 63, '64 B', 'xs d')]
b += [rect(574, 28, 110, 44, 'grp', 3), text(629, 47, 'Extension 1', 's h'), text(629, 63, 'ZDES x 64 B', 'xs d')]
b += [text(712, 55, '...', 'h')]
b += [text(367, 88, 'extensions only in Extended Report Zones', 'xs d')]
# descriptor fields
fx = [(20, 70, '0', 'ZT', 'type 3:0'), (90, 70, '1', 'ZS', 'state 7:4'), (160, 70, '2', 'ZA', 'attributes'),
      (230, 90, '7:3', 'rsvd', ''), (320, 130, '15:8', 'ZCAP', 'zone capacity'),
      (450, 130, '23:16', 'ZSLBA', 'zone start'), (580, 100, '31:24', 'WP', 'write pointer'),
      (680, 60, '63:32', 'rsvd', '')]
b += [text(20, 118, 'Each zone descriptor (64 bytes), by byte offset', 's h', 'start')]
for x, w, byt, name, sub in fx:
    cls = 'box' if name == 'rsvd' else 'dl'
    b += [rect(x, 132, w, 50, cls, 2), text(x + w / 2, 148, byt, 'xs d'), text(x + w / 2, 164, name, 's h')]
    if sub:
        b += [text(x + w / 2, 177, sub, 'xs d')]
# decode tables
cols = [('ZS value', 90), ('Zone state', 170)]
rows = [('1h', 'Empty'), ('2h', 'Implicitly Opened'), ('3h', 'Explicitly Opened'), ('4h', 'Closed'),
        ('Dh', 'Read Only'), ('Eh', 'Full'), ('Fh', 'Offline')]
t, th = table(20, 200, cols, rows, rh=22)
b += t
cols = [('ZA bit', 70), ('Meaning', 250)]
rows = [('0', 'ZFC: finished by controller'), ('1', 'FZR: finish recommended'), ('2', 'RZR: reset recommended'),
        ('3', 'ZRWAV: ZRWA valid'), ('7', 'ZDEV: extension valid')]
t2, th2 = table(300, 200, cols, rows, rh=22)
b += t2
b += [text(690, 214, 'ZT 2h =', 'xs h'), text(690, 228, 'Sequential', 'xs d'), text(690, 241, 'Write Required', 'xs d'),
      text(690, 272, 'WP is only', 'xs h'), text(690, 286, 'meaningful for', 'xs d'), text(690, 299, 'Empty, Open,', 'xs d'),
      text(690, 312, 'Closed zones', 'xs d')]
H = 200 + th + 14
add('zdesc', 'Report Zones data layout',
    'A 64-byte header carries the number of zones, then one 64-byte descriptor per zone; Extended Report Zones adds each zone\'s extension after its descriptor. Byte 1 holds the state in its upper nibble, and bytes 8 to 31 hold capacity, start LBA and write pointer.',
    svg(760, H, 'Report Zones header, zone descriptor byte layout, zone state codes and zone attribute bits', ''.join(b)))

# ---------------------------------------------------------------- zwrite
b = [rect(270, 10, 220, 40, 'tl'), text(380, 27, 'Write (SLBA, NLB)', 'h'), text(380, 42, 'to one zone', 'xs d')]
b += [arrow(380, 50, 380, 72, 'lna')]
b += [rect(270, 72, 220, 36, 'box'), text(380, 94, 'Zone state?', 's h')]
# error states to the left
errs = [(118, 'Full', 'Zone Is Full', 'B9h'), (164, 'Read Only', 'Zone Is Read Only', 'BAh'), (210, 'Offline', 'Zone Is Offline', 'BBh')]
for yy, st, name, code in errs:
    b += [poly_arrow([(270, 90), (252, 90), (252, yy + 18), (190, yy + 18)], 'lnr'), text(221, yy + 12, st, 'xs rd')]
    b += [rect(20, yy, 170, 36, 'er'), text(105, yy + 16, name, 's h'), text(105, yy + 30, 'SC ' + code, 'xs d')]
# writable path
b += [arrow(380, 108, 380, 140, 'lna'), text(388, 128, 'Empty, Open, Closed', 'xs ac', 'start')]
b += [rect(270, 140, 220, 36, 'box'), text(380, 162, 'SLBA == write pointer?', 's h')]
b += [arrow(490, 158, 544, 158, 'lnr'), text(498, 151, 'no', 'xs rd', 'start'),
      rect(544, 140, 196, 36, 'er'), text(642, 156, 'Zone Invalid Write', 's h'), text(642, 170, 'SC BCh', 'xs d')]
b += [arrow(380, 176, 380, 204, 'lna'), text(388, 194, 'yes', 'xs ac', 'start')]
b += [rect(270, 204, 220, 36, 'box'), text(380, 220, 'SLBA + NLB within', 's h'), text(380, 234, 'ZSLBA + ZCAP?', 's h')]
b += [arrow(490, 222, 544, 222, 'lnr'), text(498, 215, 'no', 'xs rd', 'start'),
      rect(544, 204, 196, 36, 'er'), text(642, 220, 'Zone Boundary Error', 's h'), text(642, 234, 'SC B8h', 'xs d')]
b += [arrow(380, 240, 380, 268, 'lna'), text(388, 258, 'yes', 'xs ac', 'start')]
b += [rect(270, 268, 220, 36, 'box'), text(380, 284, 'Empty or Closed: active', 's h'), text(380, 298, 'and open slots free?', 's h')]
b += [arrow(490, 286, 544, 286, 'lnr'), text(498, 279, 'no', 'xs rd', 'start'),
      rect(544, 268, 196, 36, 'er'), text(642, 284, 'Too Many Active / Open', 's h'), text(642, 298, 'SC BDh / BEh', 'xs d')]
b += [arrow(380, 304, 380, 332, 'lna'), text(388, 322, 'yes', 'xs ac', 'start')]
b += [rect(250, 332, 260, 44, 'pl'), text(380, 350, 'Success: WP += NLB', 's h'), text(380, 366, 'zone Open, or Full at capacity', 'xs d')]
b += [text(20, 300, 'Rejected writes leave', 'xs d', 'start'), text(20, 313, 'state and WP unchanged.', 'xs d', 'start'),
      text(20, 340, 'All codes: SCT 1h', 'xs d', 'start'), text(20, 353, '(command specific).', 'xs d', 'start')]
b += [text(380, 398, 'The check order drawn is one reasonable order. ZNS 1.4 defines no precedence when several faults', 'xs d'),
      text(380, 412, 'apply at once, so a validator accepts the set of possible statuses for multi-fault writes (7.11).', 'xs d')]
add('zwrite', 'Write outcome by zone state and address',
    'A write succeeds only in a writable zone, exactly at the write pointer, within zone capacity and with an active and open slot available. Each failed check has its own zone status code, and a rejected write changes nothing.',
    svg(760, 424, 'Decision flow for a Write to a zone with the zone status code returned at each failed check', ''.join(b)))

# ---------------------------------------------------------------- zstack
layers = [('Application', 'RocksDB + ZenFS, log engines, fio zbd', 'picks zone, tracks WP, resets, recovers', 'tl'),
          ('File system', 'zonefs, f2fs, btrfs zoned', 'append-only allocation and reclaim', 'tl'),
          ('Device mapper', 'dm-linear, dm-crypt, dm-zoned', 'pass zones through; dm-zoned hides them', 'tl'),
          ('Block layer', 'zone write plugging', 'orders writes per zone, tracks WP', 'dl'),
          ('NVMe driver', 'nvme', 'Identify to limits, Report Zones', 'dl'),
          ('ZNS SSD', 'firmware', 'enforces WP, states, MAR/MOR', 'pl')]
b = [text(128, 18, 'Layer', 's h'), text(328, 18, 'Examples', 's h'), text(588, 18, 'Job for sequential writes', 's h')]
for i, (name, ex, job, cls) in enumerate(layers):
    y = 28 + i * 52
    b += [rect(60, y, 136, 40, cls), text(128, y + 24, name, 's h'),
          rect(206, y, 244, 40, 'box'), text(328, y + 24, ex, 'xs'),
          rect(460, y, 280, 40, 'box'), text(600, y + 24, job, 'xs')]
    if i < len(layers) - 1:
        b += [arrow(128, y + 40, 128, y + 52, 'lna')]
# bypass paths on the left edge
b += [poly_arrow([(60, 40), (24, 40), (24, 256), (58, 256)], 'lnd'),
      poly_arrow([(60, 58), (40, 58), (40, 308), (58, 308)], 'lnd')]
b += [text(20, 344, 'Dashed: NVMe passthrough (/dev/ng char device, io_uring cmd) reaches the driver without the block layer;', 'xs d', 'start'),
      text(20, 358, 'SPDK and similar user-space drivers reach the device directly. Then write ordering is the caller\'s job.', 'xs d', 'start'),
      text(20, 376, 'Amber: layers above the block layer. Blue: block layer and NVMe driver. Green: device, the last line of defense.', 'xs d', 'start')]
add('zstack', 'Linux host stack for a ZNS namespace',
    'Every layer above the device must keep writes sequential per zone; the block layer orders them and tracks the write pointer, and the device only enforces the rules with status codes. Passthrough and user-space drivers skip the ordering layers.',
    svg(760, 388, 'Linux layers from application to ZNS SSD with examples and each layer\'s job, plus passthrough bypass paths', ''.join(b)))

# ---------------------------------------------------------------- zplan
phases = [('0', 'Profile'), ('1', 'Static'), ('2', 'State machine'), ('3', 'I/O rules'),
          ('4', 'Resources'), ('5', 'Append'), ('6', 'Persistence'),
          ('7', 'Integrity, soak'), ('8', 'Faults'), ('9', 'Performance'), ('10', 'Host stack')]
tiers = [('Smoke gate: every firmware build, minutes', 0, 4, 'pl'),
         ('Nightly', 4, 7, 'dl'),
         ('Weekly and release gate', 7, 11, 'tl')]
b = []
y = 14
for label, a, z, cls in tiers:
    n = z - a
    b += [rect(20, y, 720, 92, 'grp', 6), text(34, y + 18, label, 's h', 'start')]
    w = (700 - (n - 1) * 12) / n
    for k in range(n):
        num, name = phases[a + k]
        x = 30 + k * (w + 12)
        b += [rect(round(x), y + 30, round(w), 48, cls, 4), text(round(x + w / 2), y + 50, 'Phase ' + num, 'xs d'),
              text(round(x + w / 2), y + 67, name, 's h')]
        if k < n - 1:
            b += [arrow(round(x + w), y + 54, round(x + w + 12), y + 54, 'ln')]
    if z < 11:
        b += [arrow(380, y + 92, 380, y + 108, 'lna')]
    y += 108
b += [text(20, y + 6, 'Arrows show dependency: a broken Reset or Report Zones in an early phase invalidates every later result,', 'xs d', 'start'),
      text(20, y + 20, 'so later phases run only when earlier ones pass. Expected values come from the spec tables, not the device.', 'xs d', 'start')]
add('zplan', 'ZNS validation phases and gates',
    'Phases run in dependency order and are grouped by how often they run: the first four as a fast gate on every build, the middle three nightly, and the long-running phases weekly and before release.',
    svg(760, y + 32, 'Eleven ZNS validation phases grouped into smoke, nightly and weekly gates in dependency order', ''.join(b)))

# ---------------------------------------------------------------- zstore
b = [rect(20, 10, 720, 36, 'tl'), text(380, 33, 'Application writes objects', 'h')]
b += [arrow(380, 46, 380, 64, 'lna')]
b += [rect(20, 64, 720, 50, 'grp', 6), text(34, 80, 'Placement by expected lifetime (one open zone per stream)', 's h', 'start')]
streams = ['WAL', 'hot', 'cold', 'GC output']
for i, s_ in enumerate(streams):
    x = 34 + i * 176
    b += [rect(x, 86, 164, 22, 'tl', 3), text(x + 82, 101, s_, 'xs h')]
b += [arrow(380, 114, 380, 132, 'lna')]
# zones row
zones = [('open', 'tl'), ('open', 'tl'), ('full', 'dl'), ('full', 'dl'), ('full', 'dl'), ('empty', 'box'), ('empty', 'box'), ('victim', 'er')]
b += [text(34, 148, 'Zones', 's h', 'start')]
for i, (lab, cls) in enumerate(zones):
    x = 90 + i * 82
    b += [rect(x, 134, 72, 30, cls, 3), text(x + 36, 153, lab, 'xs')]
# components
comps = [(20, 'Index', 'object -> zone,', 'offset, length'),
         (206, 'Zone allocator', 'Empty pool from', 'Report Zones; MAR/MOR'),
         (392, 'Host GC', 'live bytes per zone:', 'copy live, then Reset'),
         (578, 'Recovery', 'checkpoint, then scan', 'each zone up to WP')]
for x, name, l1, l2 in comps:
    b += [rect(x, 186, 162, 66, 'tl'), text(x + 81, 205, name, 's h'), text(x + 81, 222, l1, 'xs d'), text(x + 81, 237, l2, 'xs d')]
b += [poly_arrow([(700, 164), (700, 175), (500, 175), (500, 186)], 'lnr')]
b += [text(473, 270, 'after Reset the victim zone joins the Empty pool', 'xs d')]
b += [rect(20, 296, 720, 46, 'pl'), text(380, 315, 'Device keeps media management', 's h'),
      text(380, 332, 'ECC and parity, bad blocks, wear and refresh inside zones, write pointer and state enforcement', 'xs d')]
b += [text(20, 360, 'Amber: jobs the host store now owns (the FTL did them on a conventional SSD). Green: still done by the device.', 'xs d', 'start')]
add('zstore', 'Host log-structured store on ZNS',
    'The store separates writes by expected lifetime so zones empty together, keeps its own index from objects to zone offsets, reclaims space by copying live data out of a victim zone and resetting it, and rebuilds state after a crash by scanning each zone up to its write pointer.',
    svg(760, 372, 'Components of a host-managed log-structured store on a ZNS SSD and the work the device still does', ''.join(b)))

dlib.write(ROOT, 'diagrams_Z2.js')
