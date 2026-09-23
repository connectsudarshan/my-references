#!/usr/bin/env python3
"""NVMe study page diagrams, part A: nvmearch, regmap, ctrlinit, sqcq, sqecqe."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'study_common'))
import dlib
from dlib import rect, text, line, arrow, poly_arrow, svg, add, bracket, fld

# ---------------------------------------------------------------- nvmearch (1.01)
b = []
# host group
b += [rect(14, 8, 732, 160, 'grp', 8), text(24, 22, 'HOST (software, memory)', 'xs f', 'start')]
xs = [30, 206, 382, 558]
labs = [('Application', 'read(), io_uring'), ('Filesystem', 'ext4, XFS, raw device'), ('Block layer', 'blk-mq on Linux'), ('NVMe driver', 'queues, doorbells, IRQs')]
for x, (a, s_) in zip(xs, labs):
    b += [rect(x, 32, 160, 42, 'tl'), text(x + 80, 50, a, 's h'), text(x + 80, 65, s_, 'xs d')]
for x in xs[:3]:
    b += [arrow(x + 160, 53, x + 176, 53, 'lna')]
b += [arrow(638, 74, 638, 100, 'lna'), text(646, 92, 'builds 64 B SQEs', 'xs d', 'start')]
b += [rect(382, 100, 336, 58, 'tl'), text(550, 115, 'Host memory', 's h')]
for i, lab in enumerate(['SQs: 64 B SQEs', 'CQs: 16 B CQEs', 'data buffers']):
    b += [rect(392 + i * 106, 122, 100, 26, 'box', 3), text(442 + i * 106, 139, lab, 'xs')]
for i, t in enumerate(['The driver owns the queue memory,', 'the doorbell writes and the', 'interrupt handlers. Everything', 'above it is ordinary OS code.']):
    b += [text(30, 112 + i * 14, t, 'xs d', 'start')]
# transport band
cells = [(30, 'MMIO writes', 'doorbells'), (198, 'DMA by controller', 'SQE, data, CQE'), (366, 'MSI-X writes', 'interrupts')]
for x, a, s_ in cells:
    b += [rect(x, 192, 154, 40, 'box'), text(x + 77, 209, a, 's h'), text(x + 77, 223, s_, 'xs d')]
b += [rect(536, 192, 194, 40, 'grp', 6), text(633, 209, 'PCIe transport', 's h'), text(633, 223, 'Fabrics: RDMA, TCP or FC', 'xs d')]
b += [arrow(107, 168, 107, 192, 'lna'), arrow(266, 168, 266, 192, 'lnc'), arrow(288, 192, 288, 168, 'lnc'), arrow(443, 192, 443, 168, 'lnc')]
b += [arrow(107, 232, 107, 262, 'lna'), arrow(266, 262, 266, 232, 'lnc'), arrow(288, 232, 288, 262, 'lnc'), arrow(443, 262, 443, 232, 'lnc')]
# NVM subsystem group
b += [rect(14, 240, 732, 214, 'grp', 8), text(738, 254, 'NVM SUBSYSTEM: the whole device as the host sees it', 'xs f', 'end')]
b += [rect(30, 262, 490, 88, 'dl'), text(275, 279, 'Controller (a logical entity, BAR0 registers)', 's h')]
inner = [('Registers', 'BAR0, doorbells'), ('Admin QP', 'exactly one'), ('I/O QPs', 'up to thousands'), ('Engine', 'runs commands')]
for i, (a, s_) in enumerate(inner):
    x = 36 + i * 122
    b += [rect(x, 288, 112, 50, 'box', 4), text(x + 56, 309, a, 's h'), text(x + 56, 325, s_, 'xs d')]
b += [rect(536, 262, 194, 88, 'dl'), text(633, 279, 'Namespaces', 's h')]
for i, n in enumerate(['NS 1', 'NS 2', 'NS n']):
    b += [rect(548 + i * 60, 288, 52, 24, 'box', 3), text(574 + i * 60, 304, n, 'xs h')]
b += [text(633, 328, 'LBA address spaces,', 'xs d'), text(633, 341, 'mapped to NAND by the FTL', 'xs d')]
b += [line(30, 370, 730, 370, 'lnd'), text(730, 365, 'NVMe stops above this line: the host-to-controller interface', 'xs f', 'end')]
b += [rect(30, 378, 700, 30, 'dl'), text(380, 397, 'Firmware: FTL, garbage collection, wear leveling, ECC (internal, not defined by NVMe)', 's')]
b += [rect(30, 416, 700, 30, 'pl'), text(380, 435, 'NAND flash media', 's h')]
add('nvmearch', 'NVMe architecture, application to NAND',
    'Amber is host software and memory, blue is the NVM subsystem (controller, namespaces, firmware), green is the media. PCIe carries doorbell writes down, controller DMA both ways, and interrupts up. The dashed line is where the specification stops.',
    svg(760, 460, 'NVMe stack from application through host driver, PCIe, controller and namespaces to NAND', ''.join(b)))

# ---------------------------------------------------------------- regmap (2.01)
b = [text(20, 16, 'BAR0 offsets, not to scale', 's h', 'start'), text(20, 30, 'first 4 KB = registers, doorbells from 1000h', 'xs d', 'start')]
LX, LW = 76, 294
rows = [
    ('00h', 'CAP', 'capabilities (read-only)', '8 B', 'dl', 32),
    ('08h', 'VS', 'version (read-only)', '4 B', 'dl', 24),
    ('0Ch', 'INTMS', 'mask set, pin/MSI', '4 B', 'tl', 24),
    ('10h', 'INTMC', 'mask clear, pin/MSI', '4 B', 'tl', 24),
    ('14h', 'CC', 'controller configuration', '4 B', 'tl', 24),
    ('18h', '', 'reserved', '', 'grp', 24),
    ('1Ch', 'CSTS', 'status: RDY, CFS, SHST, NSSRO, PP, ST', '4 B', 'dl', 24),
    ('20h', 'NSSR', 'subsystem reset trigger', '4 B', 'tl', 24),
    ('24h', 'AQA', 'admin queue sizes', '4 B', 'tl', 24),
    ('28h', 'ASQ', 'admin SQ base address', '8 B', 'tl', 32),
    ('30h', 'ACQ', 'admin CQ base address', '8 B', 'tl', 32),
    ('38h', 'CMBLOC', 'CMB location', '4 B', 'box', 24),
    ('3Ch', 'CMBSZ', 'CMB size', '4 B', 'box', 24),
]
y = 38
for off, nm, role, sz, cls, h in rows:
    b += [rect(LX, y, LW, h, cls, 3), text(LX - 8, y + h / 2 + 4, off, 's h', 'end')]
    if nm:
        b += [text(LX + 10, y + h / 2 + 4, nm, 's h', 'start')]
    b += [text(LX + 72 if nm else LX + 10, y + h / 2 + 4, role, 'xs d', 'start'), text(LX + LW - 8, y + h / 2 + 4, sz, 'xs d', 'end')]
    y += h + 2
lend = y
b += [text(LX + LW / 2, lend + 12, 'continues at 40h', 'xs f')]
RX, RW = 452, 288
b += [text(RX + RW / 2, 30, 'continued', 'xs f')]
y = 38
def rrow(off, nm, role, sz, cls, h):
    global b, y
    b += [rect(RX, y, RW, h, cls, 3), text(RX - 8, y + 16, off, 's h', 'end'), text(RX + 10, y + h / 2 + 4, nm, 's h', 'start')]
    b += [text(RX + 72, y + h / 2 + 4, role, 'xs d', 'start')]
    if sz:
        b += [text(RX + RW - 8, y + h / 2 + 4, sz, 'xs d', 'end')]
    y += h + 2
rrow('40h', 'BPINFO', 'boot partition info', '4 B', 'box', 24)
rrow('44h', 'BPRSEL', 'boot partition read select', '4 B', 'box', 24)
rrow('48h', 'BPMBL', 'BP memory buffer location', '8 B', 'box', 32)
b += [rect(RX, y, RW, 52, 'box', 3), text(RX - 8, y + 16, '50h', 's h', 'end'), text(RX + RW / 2, y + 20, 'CMBMSC CMBSTS CMBEBS', 's h'),
      text(RX + RW / 2, y + 34, 'CMBSWTP NSSD CRTO', 's h'), text(RX + RW / 2, y + 47, 'newer CMB controls, shutdown, timeouts', 'xs d'), text(RX - 8, y + 48, 'to 68h', 'xs d', 'end')]
y += 54
b += [rect(RX, y, RW, 22, 'grp', 3), text(RX + RW / 2, y + 15, 'reserved gap: never write', 'xs d')]
y += 24
b += [rect(RX, y, RW, 52, 'box', 3), text(RX - 8, y + 16, 'E00h', 's h', 'end'), text(RX + RW / 2, y + 18, 'PMR block: PMRCAP PMRCTL', 's h'),
      text(RX + RW / 2, y + 32, 'PMRSTS PMREBS PMRSWTP', 's h'), text(RX + RW / 2, y + 46, 'PMRMSCL PMRMSCU', 's h'), text(RX - 8, y + 34, 'to E18h', 'xs d', 'end')]
y += 54
b += [rect(RX, y, RW, 22, 'grp', 3), text(RX + RW / 2, y + 15, 'reserved gap', 'xs d')]
y += 24
b += [rect(RX, y, RW, 74, 'tl', 3), text(RX - 8, y + 16, '1000h', 's h', 'end'), text(RX + RW / 2, y + 18, 'Doorbells, 4 B each, write-only', 's h'),
      text(RX + RW / 2, y + 34, 'SQ y tail = 1000h + (2y) x stride', 'xs'), text(RX + RW / 2, y + 48, 'CQ y head = 1000h + (2y+1) x stride', 'xs'),
      text(RX + RW / 2, y + 63, 'stride = 4 << CAP.DSTRD bytes', 'xs d')]
y += 76
b += [text(RX, y + 14, '64-bit registers: CAP, ASQ, ACQ, BPMBL, CMBMSC.', 'xs d', 'start'), text(RX, y + 28, 'All others are 32-bit. Gaps are reserved.', 'xs d', 'start')]
ly = max(lend, y) + 44
b += [rect(20, ly - 10, 14, 12, 'tl', 2), text(40, ly, 'host writes (controls, doorbells)', 'xs d', 'start'),
      rect(280, ly - 10, 14, 12, 'dl', 2), text(300, ly, 'device reports (read-only, status)', 'xs d', 'start'),
      rect(540, ly - 10, 14, 12, 'box', 2), text(560, ly, 'optional blocks: CMB, BP, PMR', 'xs d', 'start')]
add('regmap', 'BAR0 controller register map',
    'Amber registers are the host controls, blue ones tell the host what the device is and what state it is in. CC is at 14h and CSTS at 1Ch, with 18h reserved between them. Doorbells start at 1000h and are spaced by the CAP.DSTRD stride.',
    svg(760, ly + 14, 'Register offsets in BAR0 from CAP at 00h to the doorbells at 1000h', ''.join(b)))

# ---------------------------------------------------------------- ctrlinit (2.03)
b = []
BX, BW = 20, 380
steps = [
    (14, 40, 'tl', '0', 'PCIe is up', 'memory space and bus master on, BAR0 mapped, admin MSI-X ready'),
    (74, 40, 'tl', '1', 'Quiesce', 'if CC.EN = 1, write CC.EN = 0. Wait until CSTS.RDY = 0'),
    (134, 40, 'tl', '2', 'Admin queues', 'write AQA, ASQ, ACQ (sizes and base addresses)'),
    (194, 40, 'tl', '3', 'Configure', 'write CC: MPS, CSS, AMS, IOSQES=6, IOCQES=4 (EN still 0)'),
    (254, 40, 'tl', '4', 'Enable', 'write CC.EN = 1'),
    (314, 40, 'dl', '5', 'Wait for ready', 'poll CSTS.RDY until it reads 1'),
]
for y0, h, cls, n, a, s_ in steps:
    b += [rect(BX, y0, BW, h, cls), text(BX + 14, y0 + 25, n, 's ac'), text(BX + BW / 2 + 8, y0 + 18, a, 's h'), text(BX + BW / 2 + 8, y0 + 32, s_, 'xs d')]
for y0 in (14, 74, 134, 194, 254):
    b += [arrow(BX + BW / 2, y0 + 40, BX + BW / 2, y0 + 60, 'lna')]
b += [arrow(BX + BW / 2, 354, BX + BW / 2, 374, 'lng'), text(BX + BW / 2 + 10, 368, 'RDY = 1', 'xs gr', 'start')]
b += [rect(BX, 374, BW, 58, 'pl'), text(BX + 14, 407, '6', 's ac'), text(BX + BW / 2 + 8, 392, 'Admin commands on queue 0', 's h'),
      text(BX + BW / 2 + 8, 406, 'Identify, Set Features (Number of Queues), MSI-X setup,', 'xs d'),
      text(BX + BW / 2 + 8, 420, 'Create I/O CQ, Create I/O SQ, Identify namespaces, AERs', 'xs d')]
# right column
NX = 432
b += [text(NX, 30, 'why this order', 's h', 'start')]
b += [text(NX, 92, 'A reset that is still running must', 'xs d', 'start'), text(NX, 106, 'finish before you write config.', 'xs d', 'start')]
b += [text(NX, 152, 'Write these before EN: the controller may fetch', 'xs d', 'start'), text(NX, 166, 'from them once RDY = 1 (a Controller Reset keeps them).', 'xs d', 'start')]
b += [text(NX, 212, 'Some drivers do this and step 4 in one', 'xs d', 'start'), text(NX, 226, 'CC write.', 'xs d', 'start')]
b += [arrow(BX + BW, 334, 424, 334, 'lnr'), text(420, 322, 'no', 'xs rd', 'end')]
b += [rect(432, 310, 308, 48, 'er'), text(586, 329, 'Timeout after CAP.TO x 500 ms', 's h'), text(586, 345, 'treat the controller as failed', 'xs d')]
b += [text(NX, 396, 'CQ before SQ: Create I/O SQ names the', 'xs d', 'start'), text(NX, 410, 'CQ it completes into, so the CQ must exist.', 'xs d', 'start')]
add('ctrlinit', 'Controller enable and initialization',
    'Amber steps are host register writes, blue is the controller answering through CSTS.RDY, green is normal operation over the admin queue. The red branch is the bounded wait: if RDY never rises within CAP.TO x 500 ms the controller is treated as failed.',
    svg(760, 444, 'Flow chart from PCIe up, through quiesce, admin queue setup, CC configure and enable, to waiting for RDY and admin commands', ''.join(b)))

# ---------------------------------------------------------------- sqcq (3.01)
b = []
CX0, CW, CS = 154, 55, 57


def cx(i):
    return CX0 + i * CS + CW / 2


def tri_down(x, y, cls):
    return f'<polygon class="{cls}" points="{x},{y + 9} {x - 6},{y} {x + 6},{y}"/>'


def tri_up(x, y, cls):
    return f'<polygon class="{cls}" points="{x},{y} {x - 6},{y + 9} {x + 6},{y + 9}"/>'


def ring(y0, kind):
    s = []
    top = y0 + 44
    if kind == 'sq':
        s += [text(CX0, y0 + 10, 'Submission queue (SQ): 64 B entries', 's h', 'start')]
    else:
        s += [text(CX0, y0 + 10, 'Completion queue (CQ): 16 B entries', 's h', 'start')]
    s += [text(CX0 + 8 * CS - 2, y0 + 10, '8 slots shown, slot 7 wraps to 0', 'xs f', 'end')]
    for i in range(8):
        x = CX0 + i * CS
        if kind == 'sq':
            full = i in (2, 3, 4)
            cls = 'tl' if full else 'box'
            main, sub = ('SQE', 'posted') if full else ('free', '')
        else:
            if i == 0:
                cls, main, sub = 'box', 'CQE', 'P=1 seen'
            elif i in (1, 2, 3):
                cls, main, sub = 'dl', 'CQE', 'P=1 new'
            else:
                cls, main, sub = 'box', 'empty', 'P=0'
        s += [rect(x, top, CW, 46, cls, 3), text(x + CW / 2, top + 12, str(i), 'xs f'), text(x + CW / 2, top + 28, main, 's h' if cls != 'box' or main == 'CQE' else 's d')]
        if sub:
            s += [text(x + CW / 2, top + 41, sub, 'xs d')]
    if kind == 'sq':
        s += [tri_down(cx(5), top - 11, 'ah'), text(cx(5) + 14, top - 16, 'TAIL: host writes here, then rings SQ tail doorbell', 'xs ac', 'end')]
        s += [tri_up(cx(2), top + 48, 'ahc'), text(cx(2) - 14, top + 66, 'HEAD: controller fetches here, reports it in CQE SQHD', 'xs cy', 'start')]
        hl, hr = ('Host', 'produces SQEs'), ('Controller', 'consumes SQEs')
        s += [arrow(104, top + 23, 150, top + 23, 'lna'), arrow(612, top + 23, 650, top + 23, 'lnc')]
    else:
        s += [tri_down(cx(4), top - 11, 'ahc'), text(cx(4) + 14, top - 16, 'TAIL: controller writes here, phase tag marks it new', 'xs cy', 'end')]
        s += [tri_up(cx(1), top + 48, 'ah'), text(cx(1) - 14, top + 66, 'HEAD: host reads here, then rings CQ head doorbell', 'xs ac', 'start')]
        hl, hr = ('Host', 'consumes CQEs'), ('Controller', 'produces CQEs')
        s += [arrow(150, top + 23, 104, top + 23, 'lna'), arrow(650, top + 23, 612, top + 23, 'lnc')]
    s += [rect(14, top - 4, 90, 54, 'tl'), text(59, top + 20, hl[0], 's h'), text(59, top + 36, hl[1], 'xs d')]
    s += [rect(656, top - 4, 90, 54, 'dl'), text(701, top + 20, hr[0], 's h'), text(701, top + 36, hr[1], 'xs d')]
    return s


b += ring(4, 'sq') + ring(142, 'cq')
b += [line(20, 292, 740, 292, 'ln')]
b += [text(20, 312, 'pointer', 'xs f', 'start'), text(130, 312, 'written by', 'xs f', 'start'), text(250, 312, 'how the other side learns it', 'xs f', 'start')]
tab = [('SQ tail', 'host', 'ac', 'SQ tail doorbell write (MMIO)'), ('SQ head', 'controller', 'cy', 'SQ Head Pointer (SQHD) field in every CQE'),
       ('CQ tail', 'controller', 'cy', 'phase tag in the new CQE, plus an interrupt if enabled'), ('CQ head', 'host', 'ac', 'CQ head doorbell write (MMIO)')]
for i, (p, w, c, how) in enumerate(tab):
    yy = 332 + i * 20
    b += [text(20, yy, p, 's h', 'start'), text(130, yy, w, 's ' + c, 'start'), text(250, yy, how, 's', 'start')]
b += [text(20, 424, 'Phase tag: the host zeroes the CQ first and expects P=1 on the first pass. The controller writes P=1,', 'xs d', 'start'),
      text(20, 440, 'then inverts it each time its tail wraps. The host treats a slot as new only when its P equals the', 'xs d', 'start'),
      text(20, 456, 'expected phase, so slot 4 (P=0) is not new yet. Neither side reads the other side pointer register.', 'xs d', 'start')]
add('sqcq', 'Submission and completion rings',
    'Amber is the host and blue is the controller. Each side owns one pointer per ring: the host produces SQ entries and consumes CQ entries, the controller does the opposite. Doorbells, the SQHD field and the phase tag carry the pointers across.',
    svg(760, 472, 'Submission and completion queues as ring buffers with head and tail pointers and the phase tag', ''.join(b)))

# ---------------------------------------------------------------- sqecqe (3.03)
b = [text(20, 14, 'SQE: 64 bytes = 16 dwords (host writes it into the SQ)', 's h', 'start')]
LBL = dlib.X0 - 12
b += [text(LBL, 46, 'DW0', 's h', 'end')]
b += fld(22, 31, 16, 'CID', 'pl', sub='31:16') + fld(22, 15, 14, 'PSDT', 'tl', sub='15:14') + fld(22, 13, 10, 'Rsvd', 'box', sub='13:10') + \
    fld(22, 9, 8, 'FUSE', 'tl', sub='9:8') + fld(22, 7, 0, 'Opcode', 'tl', sub='7:0')
b += [text(LBL, 90, 'DW1', 's h', 'end')] + fld(66, 31, 0, 'NSID', 'tl', sub='31:0')
X0, W = dlib.X0, 640


def block(y, h, dws, cls, main, sub=None):
    s = [rect(X0, y, W, h, cls, 2), text(LBL, y + h / 2 + 4, dws, 's h', 'end')]
    if sub:
        s += [text(X0 + W / 2, y + h / 2 - 2, main, 's h'), text(X0 + W / 2, y + h / 2 + 11, sub, 'xs d')]
    else:
        s += [text(X0 + W / 2, y + h / 2 + 4, main, 's h')]
    return s


b += block(110, 22, 'DW2-3', 'box', 'Reserved by the base layout (some commands use them)')
b += block(136, 22, 'DW4-5', 'tl', 'MPTR: metadata pointer (8 B)')
b += block(162, 38, 'DW6-9', 'tl', 'DPTR: PRP1 + PRP2, or one 16 B SGL descriptor', 'PSDT in DW0 selects which')
b += block(204, 38, 'DW10-15', 'tl', 'CDW10 to CDW15: command specific', '6 dwords, meaning depends on the opcode')
b += [text(20, 264, 'CQE: 16 bytes = 4 dwords (controller writes it into the CQ)', 's h', 'start')]
b += block(272, 22, 'DW0', 'dl', 'Command-specific result (e.g. granted queue counts)')
b += block(298, 22, 'DW1', 'box', 'Reserved (some commands return a 64-bit result across DW0-1)')
b += [text(LBL, 348, 'DW2', 's h', 'end')] + fld(324, 31, 16, 'SQ Identifier', 'dl', sub='31:16') + fld(324, 15, 0, 'SQ Head Pointer', 'dl', sub='15:0')
b += [text(LBL, 392, 'DW3', 's h', 'end')]
b += fld(368, 31, 31, 'DNR', 'dl', sub='31') + fld(368, 30, 30, 'M', 'dl', sub='30') + fld(368, 29, 28, 'CRD', 'dl', sub='29:28') + fld(368, 27, 25, 'SCT', 'dl', sub='27:25') + \
    fld(368, 24, 17, 'SC', 'dl', sub='24:17') + fld(368, 16, 16, 'P', 'dl', sub='16') + fld(368, 15, 0, 'CID', 'pl', sub='15:0')
b += [text(20, 430, 'Status field = DW3 bits 31:17 (SC, SCT, CRD, M, DNR: 15 bits). P is the phase tag, bit 16, just below it.', 'xs d', 'start'),
      text(20, 446, 'SQID + CID identify the command. PSDT 00b: DPTR holds PRPs. 01b or 10b: SGL.', 'xs d', 'start'),
      text(20, 462, 'Amber = host-written, blue = controller-written, green CID = echoed from SQE to CQE.', 'xs d', 'start')]
add('sqecqe', 'SQE and CQE dword layout',
    'The 64-byte SQE is built by the host, the 16-byte CQE by the controller. The command identifier in SQE DW0 comes back in CQE DW3, and DW3 bit 16 is the phase tag the host polls.',
    svg(760, 472, 'Dword layout of the 64-byte submission queue entry and the 16-byte completion queue entry', ''.join(b)))

dlib.write(os.path.dirname(os.path.abspath(__file__)), 'diagrams_A.js')
