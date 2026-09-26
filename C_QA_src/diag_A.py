#!/usr/bin/env python3
"""Diagram generator, part A: ptrmodel, strlayout, structpad, memmap, bitops, endian."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'study_common'))
import dlib
from dlib import rect, text, line, arrow, poly_arrow, svg, add, bracket

ROOT = os.path.dirname(os.path.abspath(__file__))

# ============================================================== ptrmodel (4.06)
b = []
b += [text(190, 22, 'int *p[4]  --  array of 4 pointers', 'h', 'middle')]
b += [text(190, 38, 'each slot points anywhere, independently', 's d', 'middle')]
for i in range(4):
    y = 55 + i * 45
    b += [rect(40, y, 70, 32, 'dl'), text(75, y + 21, 'p[%d]' % i, 's h')]
targets = [(260, 60, 'a'), (300, 150, 'b'), (240, 230, 'c'), (320, 290, 'd')]
for i, (tx, ty, nm) in enumerate(targets):
    y = 55 + i * 45 + 16
    b += [arrow(110, y, tx, ty + 14, 'lna')]
    b += [rect(tx, ty, 46, 28, 'pl'), text(tx + 23, ty + 19, nm, 's h')]
b += [text(190, 350, 'scattered ints, unrelated addresses', 'xs d', 'middle')]

b += [line(380, 10, 380, 400, 'lnd')]

b += [text(570, 22, 'int (*prow)[4]  --  one pointer to an int[4]', 'h', 'middle')]
b += [text(570, 38, 'arithmetic unit = whole row (16 bytes)', 's d', 'middle')]
mx, my, cw, ch = 430, 60, 60, 34
rows_vals = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
for r in range(3):
    ry = my + r * ch
    for c in range(4):
        cls = 'dl' if r == 0 else 'box'
        b += [rect(mx + c * cw, ry, cw, ch, cls), text(mx + c * cw + cw / 2, ry + 22, str(rows_vals[r][c]), 's')]
    b += [text(mx - 8, ry + 22, 'row%d' % r, 'xs d', 'end')]
addr0 = my + 3 * ch + 18
b += [arrow(410, my + 17, mx - 4, my + 17, 'lna'), text(400, my + 12, 'prow', 's h ac', 'end')]
b += [arrow(410, my + ch + 17, mx - 4, my + ch + 17, 'lnc')]
b += [text(680, my + ch + 12, 'prow++', 's cy', 'start'), text(680, my + ch + 26, '+16 bytes', 'xs d', 'start')]
b += [text(570, my + 3 * ch + 40, 'matrix[3][4] laid out row-major, contiguous', 's d', 'middle')]
b += [text(570, my + 3 * ch + 56, 'prow[1][2] = 7 ; after prow++, prow[0][0] = 5', 'xs d', 'middle')]

add('ptrmodel', 'int *p[4]  vs  int (*p)[4]',
    'Left: an array of pointers, each slot free to point anywhere. Right: a single pointer whose step size is an entire int[4] row, which is exactly what a 2D array decays to.',
    svg(760, 400, 'int star p bracket 4 versus int paren star p paren bracket 4', ''.join(b)))

# ============================================================== strlayout (5.04)
b = []
b += [text(20, 24, 'char *lit1 = "hello";  char *lit2 = "hello";', 's', 'start')]
b += [text(20, 40, 'char arr[] = "hello";', 's', 'start')]

b += [rect(60, 70, 90, 30, 'dl'), text(105, 90, 'lit1', 's h')]
b += [rect(60, 112, 90, 30, 'dl'), text(105, 132, 'lit2', 's h')]
b += [rect(60, 220, 90, 30, 'pl'), text(105, 240, 'arr', 's h')]

b += [arrow(150, 85, 330, 85, 'lna'), arrow(150, 127, 330, 100, 'lna')]
b += [rect(330, 60, 200, 55, 'er'), text(430, 82, '.rodata (read-only)', 's h'),
      text(430, 100, '"hello" + NUL -- shared object', 'xs d')]
b += [text(430, 130, 'lit1 == lit2 : 1 on this toolchain (folded)', 'xs d', 'middle')]
b += [line(535, 87, 585, 87, 'lnr'), text(592, 91, "lit1[0]='H';", 's rd', 'start'), text(592, 107, 'UB: crashes here', 'xs rd', 'start')]

b += [arrow(150, 235, 330, 235, 'lng')]
b += [rect(330, 210, 200, 55, 'pl'), text(430, 232, 'arr : own writable storage', 's h'),
      text(430, 250, '"hello" + NUL -- private copy', 'xs d')]
b += [line(535, 237, 585, 237, 'lng'), text(592, 231, "arr[0]='H';", 's gr', 'start'), text(592, 247, 'fine: owns its bytes', 'xs d', 'start')]

b += [text(20, 320, 'A string literal has static duration and may be placed read-only and shared', 's d', 'start')]
b += [text(20, 336, 'between identical literals (C11 6.4.5p6-7). Writing through any pointer to it is UB.', 's d', 'start')]
b += [text(20, 356, 'char arr[] copies the literal bytes into a fresh, writable object at init time.', 's d', 'start')]

add('strlayout', 'Where a string literal lives',
    'lit1 and lit2 may both point at one shared read-only object; writing through either is undefined behavior. char arr[] instead owns a private, writable copy made at initialization.',
    svg(760, 380, 'String literal storage versus a writable array copy', ''.join(b)))

# ============================================================== structpad (6.03)
b = []
fields = [('opcode', 1, 'dl'), ('pad', 1, 'grp'), ('nsid', 2, 'pl'), ('cdw2', 4, 'tl'), ('flags', 1, 'dl'), ('pad', 3, 'grp')]
bw = 50
x0, y0 = 40, 130
x = x0
for name, n, cls in fields:
    w = n * bw
    b += [rect(x, y0, w, 56, cls)]
    lbl = name if name != 'pad' else 'pad'
    b += [text(x + w / 2, y0 + 30, lbl, 's h' if name != 'pad' else 'xs d')]
    if name != 'pad':
        b += [text(x + w / 2, y0 + 46, ('%d byte' % n) if n == 1 else ('%d bytes' % n), 'xs d')]
    for i in range(n):
        b += [line(x + i * bw, y0, x + i * bw, y0 + 56, 'ln')]
        b += [text(x + i * bw + bw / 2, y0 + 70, str((x - x0) // bw + i), 'xs f')]
    x += w
b += [line(x, y0, x, y0 + 56, 'ln')]

marks = [('opcode', 0, 'dl'), ('nsid', 2, 'pl'), ('cdw2', 4, 'tl'), ('flags', 8, 'dl')]
for nm, off, cls in marks:
    bx = x0 + off * bw
    b += [line(bx, y0 - 10, bx, y0, 'lnd')]
    b += [text(bx, y0 - 16, 'offsetof=%d' % off, 'xs h', 'start' if off < 8 else 'end')]

b += [text(20, 24, 'struct cmd_header { uint8_t opcode; uint16_t nsid; uint32_t cdw2; uint8_t flags; }', 's h', 'start')]
b += [text(20, 42, 'nsid needs 2-byte alignment, cdw2 needs 4-byte alignment; struct size is rounded up', 's d', 'start')]
b += [text(20, 58, 'to a multiple of its strictest member alignment (4), so total sizeof = 12.', 's d', 'start')]

b += bracket(x0, x0 + 12 * bw, y0 + 100, 'sizeof(struct cmd_header) = 12 bytes', 'h')
b += [text(20, 270, 'dashed cells = padding: 1 byte before nsid (offset 1),', 's d', 'start')]
b += [text(20, 286, '3 trailing bytes after flags (offsets 9-11) to round size up to 12.', 's d', 'start')]

add('structpad', 'struct cmd_header layout',
    'Byte-by-byte layout on a typical ABI: opcode at 0, one pad byte before nsid (needs 2-byte alignment), cdw2 at 4 with no gap, flags at 8, then 3 trailing pad bytes so sizeof is 12, a multiple of 4.',
    svg(760, 310, 'struct cmd_header byte layout with padding', ''.join(b)))

# ============================================================== memmap (8.06)
b = []
ax = 130
b += [line(ax, 20, ax, 390, 'ln')]
b += [arrow(ax, 390, ax, 400, 'lna'), text(ax, 412, 'low address', 'xs d', 'middle')]
b += [text(ax, 14, 'high address', 'xs d', 'middle')]

regions = [
    ('stack', 20, 90, 'er', 'locals, return addrs -- grows DOWN as calls nest'),
    ('gap', 110, 60, None, None),
    ('heap', 170, 90, 'pl', 'malloc()/realloc() -- grows UP as you allocate'),
    ('bss', 260, 40, 'dl', 'uninitialized globals (zeroed)'),
    ('data', 300, 40, 'dl', 'initialized globals'),
    ('text', 340, 50, 'tl', 'compiled code (main, functions)'),
]
for name, y, h, cls, note in regions:
    if cls is None:
        b += [text(ax + 40, y + h / 2 + 4, '(large unmapped gap)', 'xs f', 'start')]
        b += [line(ax - 5, y, ax + 5, y, 'ln'), line(ax - 5, y + h, ax + 5, y + h, 'ln')]
        continue
    b += [rect(ax + 20, y, 230, h, cls), text(ax + 135, y + h / 2 + 5, name, 's h')]
    b += [text(ax + 265, y + h / 2 + 4, note, 's d', 'start')]

b += [poly_arrow([(ax + 60, 108), (ax + 60, 92)], 'lnr'), text(ax + 12, 95, 'grows', 'xs rd', 'start')]
b += [poly_arrow([(ax + 60, 182), (ax + 60, 198)], 'lng'), text(ax + 12, 205, 'grows', 'xs gr', 'start')]

b += [text(20, 434, 'text < data < bss < heap, stack far above -- one common run, x86-64 Linux, ASLR off.', 's d', 'start')]
b += [text(20, 450, 'This is an OS/ABI convention, not a C11 rule -- the standard defines only storage durations (6.2.4).', 's d', 'start')]

add('memmap', 'A process address space',
    'The classic flat layout: code and globals sit low, the heap grows upward from allocations, the stack grows downward from call frames near the top. Real addresses and gaps vary with the OS and ASLR, but this relative order is the common mental model.',
    svg(760, 460, 'Process memory map: text, data, bss, heap, stack', ''.join(b)))

# ============================================================== bitops (11.02)
b = []
bits_a = '10110100'
bits_b = '00101111'
def bits_of(s): return [int(c) for c in s]
va, vb = bits_of(bits_a), bits_of(bits_b)
vand = [x & y for x, y in zip(va, vb)]
vor = [x | y for x, y in zip(va, vb)]
vxor = [x ^ y for x, y in zip(va, vb)]
vshl = bits_of('11010000')
vshr = bits_of('00101101')
rows = [('a = 0xB4', va, 'dl', 40), ('b = 0x2F', vb, 'dl', 78), ('a & b = 0x24', vand, 'pl', 116), ('a | b = 0xBF', vor, 'tl', 154), ('a ^ b = 0x9B', vxor, 'er', 192),
        ('a<<2 = 0xD0', vshl, 'dl', 262), ('a>>2 = 0x2D', vshr, 'dl', 300)]
cw, ch = 36, 30
gx, gy = 190, 40
for j in range(8):
    b += [text(gx + j * cw + cw / 2, gy - 8, str(7 - j), 'xs f')]
for label, vals, cls, ry in rows:
    b += [text(gx - 12, ry + ch / 2 + 4, label, 's h', 'end')]
    for j, v in enumerate(vals):
        c = cls if v else 'box'
        b += [rect(gx + j * cw, ry, cw - 4, ch, c)]
        if not v:
            b += [text(gx + j * cw + (cw - 4) / 2, ry + ch / 2 + 4, '0', 'xs f')]
b += [text(gx + 4 * cw, 228, 'filled = bit 1, outline = bit 0. columns are independent: no carry between bit positions.', 'xs d', 'middle')]
b += [line(gx - 20, 244, gx + 8 * cw, 244, 'lnd')]

endy = 360
b += [text(20, endy, 'Shifting slides every bit two places and fills the vacated end with 0 (unsigned char', 's d', 'start')]
b += [text(20, endy + 16, 'promotes to a nonnegative int, so this is a logical shift with no sign extension).', 's d', 'start')]

add('bitops', 'AND / OR / XOR / shift, bit by bit',
    'a=0xB4, b=0x2F. AND/OR/XOR act on each bit column independently, with no carrying between positions, unlike addition. The shift rows show the same 8 bits after sliding left/right 2 places with zero-fill.',
    svg(760, endy + 34, 'Bitwise AND OR XOR and shift worked example', ''.join(b)))

# ============================================================== endian (11.09)
b = []
b += [text(20, 24, 'uint32_t x = 0x01020304;  unsigned char *p = (unsigned char *)&x;', 's', 'start')]

def byte_row(x0, y0, addr0, vals, hi_cls):
    r = []
    cw = 90
    for i, v in enumerate(vals):
        r += [rect(x0 + i * cw, y0, cw - 10, 46, hi_cls if i == 0 else 'box')]
        r += [text(x0 + i * cw + (cw - 10) / 2, y0 + 20, '0x%02X' % v, 's h')]
        r += [text(x0 + i * cw + (cw - 10) / 2, y0 + 36, 'p[%d]' % i, 'xs d')]
        r += [text(x0 + i * cw + (cw - 10) / 2, y0 - 8, '&x+%d' % i, 'xs f')]
    return r

b += [text(20, 72, 'little-endian (this host, x86-64):', 's h ac', 'start')]
b += byte_row(60, 104, 0, [0x04, 0x03, 0x02, 0x01], 'pl')
b += [text(440, 127, 'p[0]==0x04 : least-significant byte first', 's d', 'start')]
b += [text(440, 143, '-> "little-endian"', 's gr', 'start')]

b += [text(20, 200, 'big-endian (hypothetical other platform):', 's h', 'start')]
b += byte_row(60, 232, 0, [0x01, 0x02, 0x03, 0x04], 'tl')
b += [text(440, 255, 'p[0]==0x01 : most-significant byte first', 's d', 'start')]
b += [text(440, 271, '-> "big-endian"', 's ac', 'start')]

b += [text(20, 322, 'Byte order is implementation-defined (C11 6.2.6.1p2), so it must be checked at', 's d', 'start')]
b += [text(20, 338, 'runtime, not assumed. Accessing through unsigned char * is the well-defined,', 's d', 'start')]
b += [text(20, 354, 'strict-aliasing-safe way in (6.5p7); a same-size int-pointer cast would not be.', 's d', 'start')]

add('endian', 'Runtime endianness check',
    'Storing 0x01020304 and reading its first byte through an unsigned char pointer reveals byte order directly: 0x04 first means little-endian, 0x01 first means big-endian. This must be checked, never assumed from the dev machine.',
    svg(760, 378, 'Determining endianness at runtime by inspecting bytes', ''.join(b)))

dlib.write(ROOT, 'diagrams_A.js')
