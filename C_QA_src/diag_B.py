#!/usr/bin/env python3
"""Generator for diagrams_B.js: vtable, buildpipeline, linkedlist, mmio, ringbuffer."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'study_common'))
import dlib
from dlib import rect, text, line, arrow, poly_arrow, svg, add, bracket

ROOT = os.path.dirname(os.path.abspath(__file__))

# =================================================================== vtable
b = []
b += [rect(250, 14, 260, 50, 'tl'), text(380, 36, 'calling code (same call site)', 's h'),
      text(380, 54, 'ops.read(ctx)  /  ops.write(ctx, v)', 'xs d')]
b += [poly_arrow([(310, 64), (170, 112)], 'lnd'), poly_arrow([(450, 64), (610, 112)], 'lnd')]
b += [text(200, 100, 'ops = mem_vt', 'xs d'), text(560, 100, 'ops = log_vt', 'xs d')]

b += [rect(40, 112, 260, 62, 'dl'), text(170, 132, 'mem_vt : device_ops_t', 's h'),
      text(170, 150, 'read  = mem_read', 'xs'), text(170, 164, 'write = mem_write', 'xs')]
b += [rect(460, 112, 260, 62, 'dl'), text(590, 132, 'log_vt : device_ops_t', 's h'),
      text(590, 150, 'read  = log_read', 'xs'), text(590, 164, 'write = log_write', 'xs')]

b += [arrow(170, 174, 170, 206, 'lnd'), text(184, 194, 'ctx', 'xs d', 'start')]
b += [arrow(590, 174, 590, 206, 'lnd'), text(604, 194, 'ctx', 'xs d', 'start')]

b += [rect(40, 208, 260, 48, 'box'), text(170, 228, 'mem_dev_t', 's h'), text(170, 244, '{ int value; }', 'xs d')]
b += [rect(460, 208, 260, 48, 'box'), text(590, 228, 'log_dev_t', 's h'), text(590, 244, '{ int calls; }', 'xs d')]

b += [text(170, 280, 'mem_vt.write(&mem, 42);', 'xs'), text(170, 293, 'mem_vt.read(&mem) -> 42', 'xs h')]
b += [text(590, 280, 'log_vt.write(&log,7); log_vt.write(&log,8);', 'xs'),
      text(590, 293, 'log_vt.read(&log) -> calls=2, last=8', 'xs h')]

b += [text(20, 330, 'Same struct type (device_ops_t) and the same call site in both cases; which function actually', 's d', 'start'),
      text(20, 346, 'runs depends only on which instance ops refers to -- this is C-style virtual dispatch by hand.', 's d', 'start'),
      text(20, 366, 'ctx plays the role of "this": each concrete function casts it back to its own real struct type; nothing', 'xs d', 'start'),
      text(20, 380, 'in the language ties a given ctx to the vtable it is used with (mem_vt.write(&log,7) would compile).', 'xs d', 'start')]

add('vtable', 'A struct of function pointers as a vtable',
    'device_ops_t is the interface; mem_vt and log_vt are two instances filling it with different concrete functions. Calling code invokes ops.read/ops.write without knowing which one it holds.',
    svg(760, 400, 'Struct of function pointers emulating a vtable, two instances dispatching to different implementations', ''.join(b)))

# =============================================================== buildpipeline
b = []
nodes = [(20, 100, 'box', 'hello.c', 'source text'),
         (150, 90, 'box', 'hello.i', 'preprocessed text'),
         (290, 90, 'box', 'hello.s', 'assembly text'),
         (420, 90, 'dl', 'hello.o', 'object + symbols'),
         (560, 90, 'pl', 'hello', 'runnable image')]
cy = 70
for x, w, cls, nm, sub in nodes:
    b += [rect(x, cy, w, 46, cls), text(x + w / 2, cy + 20, nm, 's h'), text(x + w / 2, cy + 36, sub, 'xs d')]
stages = [(110, 150, 'Preprocess', '-E'), (240, 290, 'Compile', '-S'), (380, 420, 'Assemble', '-c'), (510, 560, 'Link', '(no flag)')]
for xa, xb, nm, flag in stages:
    b += [arrow(xa, cy + 23, xb, cy + 23), text((xa + xb) / 2, cy - 6, nm, 'xs h'), text((xa + xb) / 2, cy + 34 + 46, flag, 'xs d')]

b += [line(390, cy + 46, 390, 160), line(390, 160, 330, 160), rect(200, 160, 130, 70, 'box'),
      text(265, 178, 'nm hello.o', 's h'),
      text(265, 194, 'D gvar   T main', 'xs'),
      text(265, 208, 'U printf', 'xs'),
      text(265, 222, '(U: linker must resolve)', 'xs d')]

b += bracket(20, 510, 262, '"compiling" = phases 1-3  (gcc -c hello.c runs all three internally)', 'd')
b += bracket(520, 650, 262, '"linking" = separate step', 'd')

b += [text(20, 300, 'gvar is D (not B/bss) because int gvar = 42; has a nonzero initializer; only zero/uninitialized', 's d', 'start'),
      text(20, 316, 'file-scope objects go in .bss. printf stays U until the linker pulls it in from libc.', 's d', 'start'),
      text(20, 336, 'A clean compile only proves phases 1-3 worked; linking can still fail on an unresolved symbol.', 's d', 'start')]

add('buildpipeline', 'The four translation phases',
    'Preprocess, compile, and assemble turn hello.c into hello.o (an object file with a symbol table); link resolves external references like printf against libc to produce the runnable image.',
    svg(760, 350, 'Four phases from hello.c to executable, with an nm symbol table aside', ''.join(b)))

# =================================================================== linkedlist
b = []
b += [text(20, 18, 'amber solid = link rewired this step   grey dashed = already reversed (settled)   plain = original, not yet processed', 'xs d', 'start')]

AX, BX, CX = 140, 330, 520
NW, NH = 90, 36
NULLX = 690

def nodebox(x, yy, label):
    return [rect(x, yy, NW, NH, 'dl'), text(x + NW / 2, yy + 23, label, 'h')]

frames = [
    (50, 'start', {'A_next': 'fwd', 'B_next': 'fwd', 'C_next': 'fwd'}, 'A', None),
    (140, 'step 1', {'A_next': 'nullA_new', 'B_next': 'fwd', 'C_next': 'fwd'}, 'B', 'A'),
    (230, 'step 2', {'A_next': 'nullA_settled', 'B_next': 'toA_new', 'C_next': 'fwd'}, 'C', 'B'),
    (320, 'step 3 (done)', {'A_next': 'nullA_settled', 'B_next': 'toA_settled', 'C_next': 'toB_new'}, None, 'C'),
]

for yy, label, links, curnode, prevnode in frames:
    midy = yy + NH / 2
    b += [text(20, midy + 4, label, 's h', 'start')]
    b += nodebox(AX, yy, 'A') + nodebox(BX, yy, 'B') + nodebox(CX, yy, 'C')

    a_next = links['A_next']
    if a_next == 'fwd':
        b += [arrow(AX + NW, midy, BX, midy, 'ln')]
    elif a_next == 'nullA_new':
        b += [arrow(AX, midy - 6, 70, midy - 6, 'lna'), text(70, midy - 12, 'NULL', 'xs d', 'end')]
        b += [arrow(BX + NW, midy, CX, midy, 'ln')]
    elif a_next == 'nullA_settled':
        b += [arrow(AX, midy - 6, 70, midy - 6, 'lnd'), text(70, midy - 12, 'NULL', 'xs f', 'end')]

    b_next = links['B_next']
    if b_next == 'toA_new':
        b += [arrow(BX, midy + 8, AX + NW, midy + 8, 'lna')]
        b += [arrow(CX + NW, midy, NULLX, midy, 'ln'), text(NULLX + 8, midy + 4, 'NULL', 'xs d', 'start')]
    elif b_next == 'toA_settled':
        b += [arrow(BX, midy + 8, AX + NW, midy + 8, 'lnd')]

    c_next = links['C_next']
    if c_next == 'fwd' and links['A_next'] != 'fwd' and links['B_next'] not in ('toA_new', 'toA_settled'):
        # only used in the "start" frame's own tail is handled below explicitly; guard unused
        pass
    if links['A_next'] == 'fwd' and links['B_next'] == 'fwd':
        b += [arrow(CX + NW, midy, NULLX, midy, 'ln'), text(NULLX + 8, midy + 4, 'NULL', 'xs d', 'start')]
    if c_next == 'toB_new':
        b += [arrow(CX, midy + 8, BX + NW, midy + 8, 'lna')]

    if curnode:
        cx = {'A': AX, 'B': BX, 'C': CX}[curnode] + NW / 2
        b += [text(cx, yy - 18, 'cur', 'xs ac'), arrow(cx, yy - 12, cx, yy - 2, 'lna')]
    else:
        b += [text(NULLX + 8, midy - 14, 'cur = NULL', 'xs ac', 'start')]
    if prevnode:
        px = {'A': AX, 'B': BX, 'C': CX}[prevnode] + NW / 2
        b += [text(px, yy + NH + 26, 'prev', 'xs cy'), arrow(px, yy + NH + 20, px, yy + NH + 4, 'lnc')]
    else:
        b += [text(20, midy + 20, 'prev = NULL', 'xs d', 'start')]

b += [text(590, 320 + NH + 26, '<- new head (returned)', 'xs h', 'start')]

add('linkedlist', 'Reversing a singly linked list, one step at a time',
    'reverse_iter walks once with prev/cur/next. Each step saves cur->next, rewires cur->next to point at prev (amber), then advances both pointers; when cur reaches NULL, prev (now C) is the new head.',
    svg(760, 440, 'Four frames showing prev, cur, and next as a 3-node list A->B->C is reversed to C->B->A', ''.join(b)))

# ======================================================================= mmio
b = []
b += [text(190, 18, 'non-volatile: for (i=0;i<3;i++) *p=1;', 's rd'), text(570, 18, 'volatile: for (i=0;i<3;i++) *p=1;', 's gr')]
b += [text(190, 32, 'uint32_t *p = &reg;', 'xs d'), text(570, 32, 'volatile uint32_t *p = &reg;', 'xs d')]

left_mx = [120, 190, 260]
right_mx = [500, 570, 640]
for i, mx in enumerate(left_mx):
    cls = 'grp' if i < 2 else 'tl'
    b += [rect(mx - 8, 52, 16, 16, cls, 3), text(mx, 46, f'i={i}', 'xs d')]
    if i < 2:
        b += [text(mx, 78, 'elim.', 'xs rd')]
for i, mx in enumerate(right_mx):
    b += [rect(mx - 8, 52, 16, 16, 'pl', 3), text(mx, 46, f'i={i}', 'xs d')]
    b += [arrow(mx, 68, 570, 100, 'lng')]

b += [arrow(left_mx[2], 68, 190, 100, 'lna'), text(190, 96, 'kept: movl $1,(reg)', 'xs h', anchor='middle')]

b += [rect(110, 100, 160, 40, 'dl'), text(190, 118, 'reg (in memory)', 's h'), text(190, 133, 'never read again', 'xs f')]
b += [rect(490, 100, 160, 40, 'dl'), text(570, 118, 'reg (in memory)', 's h'), text(570, 133, 'written 3 times', 'xs f')]

b += [poly_arrow([(260, 68), (320, 68), (320, 190), (250, 190)], 'lnd'),
      text(324, 130, 'constant reused,', 'xs d', 'start'), text(324, 144, 'no reload', 'xs d', 'start')]
b += [arrow(570, 140, 570, 178, 'lng'), text(584, 160, 'real reload', 'xs h', 'start')]

b += [rect(90, 190, 200, 40, 'box'), text(190, 208, 'return (int)*p;', 's h'), text(190, 224, 'mov $1,%eax', 'xs d')]
b += [rect(470, 190, 200, 40, 'box'), text(570, 208, 'return (int)*p;', 's h'), text(570, 224, 'mov 0x2fac(%rip),%eax', 'xs d')]

b += [rect(20, 250, 340, 40, 'er'), text(190, 268, '-O2 result: 1 store total', 's h'), text(190, 283, '(dead-store elimination)', 'xs d')]
b += [rect(400, 250, 340, 40, 'pl'), text(570, 268, '-O2 result: 3 stores + 1 reload', 's h'), text(570, 283, '(all preserved, in order)', 'xs d')]

b += [text(20, 318, 'C11 6.7.3p7: an access to a volatile object must happen exactly as the abstract machine specifies.', 's d', 'start'),
      text(20, 334, 'Without volatile the compiler proves the first two stores are dead and the final read is just the', 's d', 'start'),
      text(20, 350, 'constant it already stored -- both eliminated at -O2, which is invisible at -O0.', 's d', 'start')]

add('mmio', 'volatile vs. non-volatile: what -O2 actually emits',
    'Same three-store loop compiled twice. Without volatile the compiler collapses it to one store and answers the read from a constant (red = wrong for a real register). With volatile every store and the final reload survive as separate instructions (green = correct).',
    svg(760, 370, 'Disassembly comparison of a volatile and non-volatile memory-mapped register write loop', ''.join(b)))

# ================================================================== ringbuffer
b = []
b += [text(20, 18, 'SPSC ring, CAPACITY=8 (power of two): array index = counter & (CAPACITY-1); head/tail only ever increase.', 'xs d', 'start')]

SX0, SW, GAP = 60, 78, 8
slot_x = [SX0 + i * (SW + GAP) for i in range(8)]
values = [100, 101, 102, 3, 4, 5, 6, 7]
fresh = {0, 1, 2}
SY = 130
for i, x in enumerate(slot_x):
    cls = 'pl' if i in fresh else 'dl'
    b += [rect(x, SY, SW, 46, cls), text(x + SW / 2, SY + 29, str(values[i]), 'h'), text(x + SW / 2, SY + 62, f'[{i}]', 'xs d')]

s3 = slot_x[3]
b += [text(s3 - 6, 78, 'tail = 3', 'xs cy', 'end'), arrow(s3 - 4, 84, s3 + SW / 2 - 10, SY - 2, 'lnc')]
b += [text(s3 + SW + 6, 96, 'head = 11', 'xs ac', 'start'), arrow(s3 + SW + 4, 102, s3 + SW / 2 + 10, SY - 2, 'lna')]

b += [rect(30, 210, 700, 56, 'box'),
      text(380, 230, 'Both mask to the same slot: 11 & 7 == 3 & 7 == 3', 's h'),
      text(380, 248, 'but head - tail = 11 - 3 = 8 = CAPACITY, so rb_full() (not equal masked indices) says FULL, not empty.', 'xs d')]

b += [text(20, 290, 'push (producer, owns head): buf[head & 7] = v; head++', 's ac', 'start'),
      text(20, 306, 'pop  (consumer, owns tail):  v = buf[tail & 7]; tail++', 's cy', 'start')]

b += [text(20, 336, 'Slots [0..2] (green) were just refilled by the wrap-around pushes of 100,101,102 after 0,1,2 were popped;', 'xs d', 'start'),
      text(20, 352, 'slots [3..7] (blue) still hold the original values 3..7, waiting to be popped in order.', 'xs d', 'start')]

add('ringbuffer', 'SPSC ring buffer: masking and the full/empty ambiguity',
    'Capacity-8 ring after filling, popping 3, and pushing 3 more (wrap-around). head=11 and tail=3 both mask to slot 3, which is why fullness must be checked with head-tail, not by comparing masked indices.',
    svg(760, 380, 'Ring buffer array with head and tail pointers wrapping via bitwise AND', ''.join(b)))

dlib.write(ROOT, 'diagrams_B.js')
