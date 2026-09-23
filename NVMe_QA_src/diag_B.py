#!/usr/bin/env python3
"""NVMe study page, diagrams part B: prp, fwslots, nsmodel, pifmt, cqestatus."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'study_common'))
import dlib
from dlib import rect, text, line, arrow, poly_arrow, svg, add, bracket


def card(x, y, w, h, cls, title, lines, tcls='s h', lcls='xs', lh=13):
    """Box with a bold title line and small detail lines (left aligned inside)."""
    s = [rect(x, y, w, h, cls)]
    ty = y + 17
    s.append(text(x + w / 2, ty, title, tcls))
    ly = ty + 15
    for ln in lines:
        s.append(text(x + w / 2, ly, ln, lcls))
        ly += lh
    return s


# ------------------------------------------------------------------ prp
b = []
for i, (x, cls, t1, t2) in enumerate([
        (10, 'box', '1 page', 'PRP1 = data, PRP2 unused'),
        (262, 'box', '2 pages', 'PRP1 = data, PRP2 = 2nd page'),
        (514, 'tl', '3 or more pages (drawn below)', 'PRP1 = data, PRP2 = list pointer')]):
    b += [rect(x, 6, 236, 44, cls), text(x + 118, 24, t1, 's h'), text(x + 118, 40, t2, 'xs')]

# DPTR group
b += [rect(4, 62, 122, 100, 'grp')]
b += [rect(10, 68, 110, 40, 'tl'), text(65, 86, 'PRP1', 's h'), text(65, 100, '8 B, offset ok', 'xs d')]
b += [rect(10, 116, 110, 40, 'tl'), text(65, 134, 'PRP2', 's h'), text(65, 148, '8 B, list ptr', 'xs d')]
b += [text(65, 178, 'DPTR (16 B in SQE)', 'xs d')]

# data page 1
b += [arrow(120, 88, 560, 88, 'lna'), text(340, 80, 'first page, may start at an offset', 'xs d')]
b += [rect(560, 72, 190, 32, 'dl'), text(655, 92, 'data page 1', 's h')]

# list page A
b += [rect(200, 118, 200, 142, 'tl'), text(300, 134, 'PRP list page A (4 KiB)', 's h')]
b += [arrow(120, 136, 200, 136, 'lna')]
rowsA = [(142, 'slot 0', 'box', 'data page 2'), (164, 'slot 1', 'box', 'data page 3'),
         (186, '...', None, None), (208, 'slot 510', 'box', 'data page 512'), (230, 'slot 511: link', 'tl', None)]
for y, lab, cls, dp in rowsA:
    if cls:
        b += [rect(206, y, 188, 20, cls, 2), text(300, y + 14, lab, 's')]
    else:
        b += [text(300, y + 14, lab, 's d')]
    if dp:
        b += [arrow(394, y + 10, 560, y + 10, 'lna'), rect(560, y, 190, 20, 'dl', 2), text(655, y + 14, dp, 's')]
b += [text(655, 200, '...', 's d')]
b += [text(10, 208, 'Slots 0 to 510: one data', 'xs d', 'start'), text(10, 222, 'entry per page, offset 0.', 'xs d', 'start')]

# list page B
b += [rect(200, 290, 200, 118, 'tl'), text(300, 306, 'PRP list page B', 's h')]
rowsB = [(314, 'slot 0', 'box', 'data page 513'), (336, 'slot 1', 'box', 'data page 514'),
         (358, '...', None, None), (380, 'last slot: data', 'box', 'last data page')]
for y, lab, cls, dp in rowsB:
    if cls:
        b += [rect(206, y, 188, 20, cls, 2), text(300, y + 14, lab, 's')]
    else:
        b += [text(300, y + 14, lab, 's d')]
    if dp:
        b += [arrow(394, y + 10, 560, y + 10, 'lna'), rect(560, y, 190, 20, 'dl', 2), text(655, y + 14, dp, 's')]
b += [text(655, 372, '...', 's d')]

# link arrow
b += [poly_arrow([(394, 240), (470, 240), (470, 298), (400, 298)], 'lnc')]
b += [text(478, 274, 'link to the next list page', 'xs ac', 'start')]

b += [text(10, 326, 'Slot 0 holds the data entry', 'xs d', 'start'), text(10, 340, 'that slot 511 of page A', 'xs d', 'start'),
      text(10, 354, 'would have held.', 'xs d', 'start')]
b += [text(10, 384, 'Final list page: all slots', 'xs d', 'start'), text(10, 398, 'may hold data, no link.', 'xs d', 'start')]

b += [text(380, 430, 'PRP1 may have any byte offset. As a data pointer PRP2 is page aligned; as a list pointer it may have a', 'xs d'),
      text(380, 445, 'qword offset, shortening that first list page. Every other list entry stays page aligned (Base 2.3, 4.3.1).', 'xs d')]
add('prp', 'PRP1, PRP2 and list chaining',
    'The cases by page count, then the 3-or-more case in detail at 4 KiB pages: PRP2 points to a list page of 512 8-byte slots, and when more entries follow, the last slot is a link (blue arrow) to the next list page and the displaced data entry moves to its slot 0.',
    svg(760, 456, 'PRP1 and PRP2 pointing to data pages and to chained PRP list pages', ''.join(b)))

# ------------------------------------------------------------------ fwslots
dy = 16
b = [text(135, 14, 'Host commands', 's h ac'), text(405, 14, 'Controller', 's h cy'), text(653, 14, 'Result', 's h gr')]
b += card(10, 8 + dy, 250, 76, 'tl', '1 Discover: Identify Controller',
          ['FRMW (byte 260): bits 3:1 slot count,', 'bit 0 slot 1 read-only, bit 4 no-reset', 'activation. Also FWUG, MTFA, MDTS.'])
b += card(10, 100 + dy, 250, 84, 'tl', '2 Firmware Image Download (11h)',
          ['NUMD (0s based dwords) + dword offset', 'chunk <= MDTS, offset multiple of FWUG', 'e.g. 4 MiB / 64 KiB = 64 commands,', 'NUMD = 0x3FFF, offsets step 0x4000'])
b += card(10, 204 + dy, 250, 82, 'tl', '3 Firmware Commit (10h)',
          ['CDW10 = (CA << 3) | FS', 'FS bits 2:0 = slot, CA bits 5:3 = action', 'example: slot 2, CA 1 gives 0x0A', 'FS = 0 lets the controller pick'])
b += [arrow(130, 84 + dy, 130, 100 + dy, 'lna'), arrow(130, 184 + dy, 130, 204 + dy, 'lna')]
b += card(10, 302 + dy, 250, 100, 'tl', '5 Verify after the reset',
          ['Firmware Slot log page (03h):', 'AFI bits 2:0 = active slot,', 'bits 6:4 = slot for next reset,', 'then FRS1 to FRS7 (8-byte revs).',
           'Identify Controller FR (bytes 71:64)', 'shows the running revision.'])
b += [arrow(130, 286 + dy, 130, 302 + dy, 'lna')]

# controller column
b += card(300, 100 + dy, 210, 60, 'dl', 'Image buffer', ['downloaded image, staged,', 'not in any slot yet'])
b += [arrow(260, 130 + dy, 300, 130 + dy, 'lna')]
b += [rect(300, 204 + dy, 210, 188, 'dl'), text(405, 222 + dy, 'Firmware slots', 's h'), text(405, 236 + dy, 'count = FRMW bits 3:1', 'xs d')]
b += [rect(306, 246 + dy, 198, 22, 'box', 2), text(405, 261 + dy, 'slot 1 (read-only if FRMW bit 0)', 'xs')]
b += [rect(306, 272 + dy, 198, 22, 'tl', 2), text(405, 287 + dy, 'slot 2 (FS = 2 in the example)', 'xs')]
b += [rect(306, 298 + dy, 198, 22, 'box', 2), text(405, 313 + dy, 'slot 3', 'xs')]
b += [text(405, 335 + dy, '... up to 7 slots', 'xs d')]
b += [text(405, 361 + dy, 'CA 6 and 7 target a Boot', 'xs d'), text(405, 374 + dy, 'Partition (module 12).', 'xs d')]
b += [arrow(405, 160 + dy, 405, 204 + dy, 'lna'), text(413, 186 + dy, 'CA 0, 1, 3: store new image', 'xs ac', 'start')]
b += [arrow(260, 245 + dy, 300, 245 + dy, 'lna'), text(280, 237 + dy, 'FS', 'xs ac')]

# result column
b += card(556, 100 + dy, 194, 64, 'box', 'Rollback', ['keep the old image in', 'another slot, then commit', 'it again with CA 2'])
b += [text(653, 196 + dy, '4 Activate, chosen by CA', 's h')]
b += card(556, 204 + dy, 194, 40, 'box', 'CA 0: store only', ['slot FS is not activated'])
b += card(556, 254 + dy, 194, 64, 'tl', 'CA 1 and CA 2', ['CA 1: store, then activate', 'CA 2: activate slot FS as is', 'both at the next reset'])
b += card(556, 328 + dy, 194, 64, 'pl', 'CA 3: live activation', ['activate now, no reset', 'needs FRMW bit 4 = 1', 'pause up to MTFA (CSTS.PP)'])
b += [arrow(510, 224 + dy, 556, 224 + dy, 'lnd'), arrow(510, 286 + dy, 556, 286 + dy, 'lna'), arrow(510, 360 + dy, 556, 360 + dy, 'lng')]

b += [text(380, 438, 'A Success status on Commit does not prove activation: read the slot log and FR after the reset.', 'xs d')]
add('fwslots', 'Firmware download, commit and activation',
    'Download stages the image, Commit picks the slot (FS) and the action (CA), and only CA 1 and 2 wait for a reset while CA 3 activates live. Verify by reading the Firmware Slot log page and Identify Controller FR.',
    svg(760, 450, 'Firmware update flow: download to image buffer, commit to a slot, activation by CA value, verify', ''.join(b)))

# ------------------------------------------------------------------ nsmodel
b = []
b += [rect(10, 190, 96, 64, 'tl'), text(58, 218, 'Host', 's h'), text(58, 234, 'multipath', 'xs d')]
b += [rect(150, 12, 600, 366, 'grp'), text(162, 30, 'NVM subsystem', 's h', 'start')]
# controllers
b += [rect(190, 78, 140, 64, 'dl'), text(260, 104, 'Controller 0', 's h'), text(260, 122, 'owns its queues', 'xs d')]
b += [rect(190, 232, 140, 64, 'dl'), text(260, 258, 'Controller 1', 's h'), text(260, 276, 'owns its queues', 'xs d')]
# host paths
b += [line(106, 212, 190, 110, 'ln'), line(106, 232, 190, 264, 'ln')]
b += [text(126, 168, 'path 1', 'xs d'), text(126, 268, 'path 2', 'xs d')]
# namespaces
nss = [(58, 'NS A', 'private: 1 controller only', 'dl'), (128, 'NS B', 'shared: NMIC bit 0 = 1', 'pl'),
       (198, 'NS C', 'private: 1 controller only', 'dl'), (268, 'NS D', 'created, attached to none', 'box')]
for y, nm, sub, cls in nss:
    b += [rect(500, y, 230, 46, cls), text(615, y + 20, nm, 's h'), text(615, y + 36, sub, 'xs')]
# attach lines: private = blue, shared = green
b += [line(330, 100, 500, 81, 'lnc'), line(330, 118, 500, 151, 'lng'), line(330, 250, 500, 165, 'lng'), line(330, 270, 500, 221, 'lnc')]
b += [rect(190, 326, 540, 40, 'pl'), text(460, 343, 'Non-volatile media', 's h'), text(460, 358, 'namespaces are logical views of it, not NAND slices', 'xs d')]
b += [text(380, 398, 'Each line is one controller-to-namespace attachment. Private: exactly one line. Shared: two or more.', 'xs d'),
      text(380, 413, 'The host sees NS B through both controllers, so it must report the same NGUID or EUI64 on both.', 'xs d'),
      text(380, 428, 'Attaching a private namespace to a second controller fails: Namespace Is Private (SCT 1, SC 19h).', 'xs d')]
add('nsmodel', 'Subsystem, controllers and namespaces',
    'Namespaces live in the subsystem and are attached to zero or more controllers. Blue lines are private attachments, green lines are the two attachments of a shared namespace.',
    svg(760, 440, 'NVM subsystem with two controllers, private and shared namespaces and attach lines', ''.join(b)))

# ------------------------------------------------------------------ pifmt
b = []
X = 60
CW = 80
for i in range(8):
    b += [text(X + i * CW + CW / 2, 16, 'byte %d' % i, 'xs f')]
fields = [(0, 2, 'Guard', '16 bits', 'dl'), (2, 2, 'Application Tag', '16 bits', 'pl'), (4, 4, 'Reference Tag', '32 bits', 'tl')]
for start, n, nm, sz, cls in fields:
    x = X + start * CW
    b += [rect(x, 24, n * CW, 44, cls), text(x + n * CW / 2, 44, nm, 's h'), text(x + n * CW / 2, 59, sz, 'xs d')]
b += [text(X - 10, 50, 'PI', 's h', 'end')]
dets = [
    (0, 2, ['CRC-16 T10-DIF', 'poly 0x8BB7, initial 0', 'over the block data', 'enabled by PRCHK bit 2']),
    (2, 2, ['host-owned tag', 'compared under mask (LBATM)', '0xFFFF skips the check', 'enabled by PRCHK bit 1']),
    (4, 4, ['type dependent', 'Type 1: low 32 bits of the LBA', 'enabled by PRCHK bit 0']),
]
for start, n, ls in dets:
    x = X + start * CW
    b += [rect(x, 76, n * CW, 66, 'box')]
    for i, t in enumerate(ls):
        b += [text(x + n * CW / 2, 94 + i * 14, t, 'xs')]
b += [text(380, 160, 'All three fields are big-endian, unlike the little-endian SQE and CQE. PI sits in the first or last 8 bytes of the metadata.', 'xs d')]

# where generated and checked
b += [text(380, 192, 'Where the tuple is generated and checked', 's h')]
b += card(10, 204, 190, 76, 'tl', 'Host: generate PI', ['application, block layer', 'or HBA (or the controller', 'itself, with PRACT)'])
b += card(290, 204, 190, 76, 'dl', 'Controller: write', ['verify Guard and tags', 'when PRCHK asks', '(or generate with PRACT)'])
b += card(290, 300, 190, 62, 'dl', 'Controller: read', ['verify Guard and tags', 'when PRCHK asks'])
b += card(10, 300, 190, 62, 'tl', 'Host: verify PI', ['checks what comes back'])
b += [rect(570, 204, 180, 158, 'pl'), text(660, 268, 'Media', 's h'), text(660, 284, 'block data plus', 'xs'), text(660, 297, 'metadata with PI', 'xs')]
b += [arrow(200, 242, 290, 242, 'lna'), text(245, 234, 'PCIe', 'xs d')]
b += [arrow(480, 242, 570, 242, 'lna')]
b += [arrow(570, 331, 480, 331, 'lnc')]
b += [arrow(290, 331, 200, 331, 'lnc'), text(245, 323, 'PCIe', 'xs d')]
b += [text(380, 293, 'write path above, read path below', 'xs d')]
b += [rect(10, 378, 740, 44, 'er'), text(380, 396, 'A mismatch completes with a Guard, Application Tag or Reference Tag Check Error.', 's h'),
      text(380, 412, 'The same tuple travels host to drive and back, so any layer that corrupts the block or its address breaks the match.', 'xs')]
add('pifmt', 'The 8-byte protection information tuple',
    'Guard, Application Tag and Reference Tag make up 8 bytes per LBA. It is generated on the host (or by the controller with PRACT), verified by the controller when PRCHK asks, and verified again by the host on reads.',
    svg(760, 436, 'Layout of the 8-byte PI tuple and the write and read path where it is generated and checked', ''.join(b)))

# ------------------------------------------------------------------ cqestatus
UBW = 22
X0 = 44


def cf(y, h, hi, lo, label, cls, sub=None, narrow_label_above=False):
    x = X0 + (31 - hi) * UBW
    w = (hi - lo + 1) * UBW
    s = [rect(x, y, w, h, cls, 2)]
    bits = sub if sub is not None else ('%d:%d' % (hi, lo) if hi != lo else '%d' % hi)
    if narrow_label_above:
        s += [text(x + w / 2, y - 6, label, 'xs h'), text(x + w / 2, y + h / 2 + 4, bits, 'xs d')]
    elif h >= 44:
        s += [text(x + w / 2, y + 22, label, 's h'), text(x + w / 2, y + 38, bits, 'xs d')]
    else:
        s += [text(x + w / 2, y + h / 2 + 4, label, 'xs')]
    return s


b = [text(X0 + 11, 14, '31', 'xs f'), text(X0 + 32 * UBW - 11, 14, '0', 'xs f')]
ctx = [
    ('DW0', 22, [(31, 0, 'Command specific result', 'box')]),
    ('DW1', 52, [(31, 0, 'Reserved', 'box')]),
    ('DW2', 82, [(31, 16, 'SQ Identifier (SQID)', 'box'), (15, 0, 'SQ Head Pointer (SQHD)', 'box')]),
]
for nm, y, fl in ctx:
    b += [text(6, y + 18, nm, 's h', 'start')]
    for hi, lo, lab, cls in fl:
        b += cf(y, 26, hi, lo, lab, cls)
Y3 = 138
b += [text(6, Y3 + 30, 'DW3', 's h ac', 'start')]
b += cf(Y3, 52, 31, 31, 'DNR', 'er', narrow_label_above=True)
b += cf(Y3, 52, 30, 30, 'M', 'dl', narrow_label_above=True)
b += cf(Y3, 52, 29, 28, 'CRD', 'dl')
b += cf(Y3, 52, 27, 25, 'SCT', 'pl')
b += cf(Y3, 52, 24, 17, 'SC', 'pl')
b += cf(Y3, 52, 16, 16, 'P', 'tl', narrow_label_above=True)
b += cf(Y3, 52, 15, 0, 'CID', 'box')
xs31 = X0
xs16 = X0 + 16 * UBW
b += bracket(xs31, xs16, 208, 'Status field + P: DW3 bits 31:16', 'ac')
b += bracket(xs16, X0 + 32 * UBW, 208, 'Command Identifier: DW3 bits 15:0', '')
legend = [
    ('DNR', '31', 'er', 'Do Not Retry'),
    ('M', '30', 'dl', 'More information is in the Error Information log page'),
    ('CRD', '29:28', 'dl', 'Command Retry Delay: index of a retry delay time, 0 means none'),
    ('SCT', '27:25', 'pl', '0 generic, 1 command specific, 2 media and data integrity, 3 path related, 7 vendor specific'),
    ('SC', '24:17', 'pl', 'Status Code, looked up in the table chosen by SCT'),
    ('P', '16', 'tl', 'Phase Tag, inverts on every pass through the CQ'),
    ('CID', '15:0', 'box', 'Command identifier of the completed command'),
]
ly = 244
for nm, bits, cls, desc in legend:
    b += [rect(10, ly - 10, 14, 14, cls, 2), text(34, ly + 1, nm, 's h', 'start'), text(84, ly + 1, bits, 'xs d', 'start'), text(136, ly + 1, desc, 'xs', 'start')]
    ly += 19
b += [text(380, 392, 'Success is SCT 0 and SC 0. P is 1 on the first pass, so a valid DW3 is never all zero: mask P out before testing.', 'xs d'),
      text(380, 407, 'Linux shifts the status right by 1 (drops P): SC in bits 7:0, SCT 10:8, CRD 12:11, M bit 13, DNR bit 14.', 'xs d'),
      text(380, 422, 'The status field is meaningless until P matches the phase the host expects for that pass of the CQ.', 'xs d')]
add('cqestatus', 'CQE DW3: the status field',
    'The 16-byte CQE ends with DW3. Bits 31:17 are the status field (DNR, M, CRD, SCT, SC), bit 16 is the Phase Tag and bits 15:0 are the command identifier.',
    svg(760, 436, 'Bit layout of the 16-byte CQE with DW3 status field bit positions', ''.join(b)))

dlib.write(os.path.dirname(os.path.abspath(__file__)), 'diagrams_B.js')
