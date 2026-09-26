#!/usr/bin/env python3
"""Generates diagrams_B.js for cadv module figures: diningphil, scheduling,
ipcmodel, vmpaging, isrflow, threadpool."""
import sys, math, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'study_common'))
import dlib
from dlib import rect, text, line, arrow, poly_arrow, svg, add, bracket, fld

ROOT = os.path.dirname(os.path.abspath(__file__))


def edge(cx1, cy1, cx2, cy2, r):
    dx, dy = cx2 - cx1, cy2 - cy1
    L = math.hypot(dx, dy)
    return cx1 + dx / L * r, cy1 + dy / L * r


def circle(cx, cy, r, cls='box'):
    return f'<circle class="{cls}" cx="{cx}" cy="{cy}" r="{r}"/>'


# ================================================================ diningphil
cx, cy, R = 300, 233, 150
names = ['P0', 'P1', 'P2', 'P3', 'P4', 'F0', 'F1', 'F2', 'F3', 'F4']
centers = {}
for k in range(10):
    ang = math.radians(-90 + 36 * k)
    x, y = cx + R * math.cos(ang), cy + R * math.sin(ang)
    idx = k // 2
    if k % 2 == 0:
        centers['P%d' % idx] = (x, y)
    else:
        centers['F%d' % idx] = (x, y)

PR, FR = 25, 15
b = []
for i in range(5):
    x, y = centers['P%d' % i]
    b += [circle(x, y, PR, 'box'), text(x, y + 5, 'P%d' % i, 'h')]
for i in range(5):
    x, y = centers['F%d' % i]
    b += [circle(x, y, FR, 'dl'), text(x, y + 4, 'F%d' % i, 'xs h')]

# fixed rule: P_i grabs fork min(i,(i+1)%5) first. For i=0..3 that's Fi (green).
for i in range(4):
    ax, ay = centers['P%d' % i]
    bx, by = centers['F%d' % i]
    s1 = edge(ax, ay, bx, by, PR)
    s2 = edge(bx, by, ax, ay, FR)
    b += [arrow(s1[0], s1[1], s2[0], s2[1], 'lng')]
# P4: first grab is F0 (min(4,0)=0), not F4 -- this is the fix.
ax, ay = centers['P4']
bx, by = centers['F0']
s1 = edge(ax, ay, bx, by, PR)
s2 = edge(bx, by, ax, ay, FR)
b += [poly_arrow([(s1[0], s1[1]), ((s1[0] + s2[0]) / 2 - 10, (s1[1] + s2[1]) / 2 - 60), (s2[0], s2[1])], 'lng')]

# naive rule (9.12): P4 grabs F4 first (its "left") -> completes the 5-cycle -> deadlock.
bx2, by2 = centers['F4']
s1n = edge(ax, ay, bx2, by2, PR)
s2n = edge(bx2, by2, ax, ay, FR)
b += [arrow(s1n[0], s1n[1], s2n[0], s2n[1], 'lnr')]
midx, midy = (s1n[0] + s2n[0]) / 2, (s1n[1] + s2n[1]) / 2
b += [line(midx - 7, midy - 7, midx + 7, midy + 7, 'lnr'), line(midx - 7, midy + 7, midx + 7, midy - 7, 'lnr')]

b += [text(cx, 30, 'Dining philosophers: lowest-numbered-fork-first breaks the cycle (9.13)', 's h')]
b += [text(centers['F0'][0] + 40, centers['F0'][1] - 15, 'P0 and P4 both reach for F0 first now', 'xs d', 'start')]
b += [text(centers['F4'][0] + 15, centers['F4'][1] + 28, 'naive (9.12): P4 grabbed its', 'xs rd', 'start'),
      text(centers['F4'][0] + 15, centers['F4'][1] + 40, 'left fork F4 first -> 5-cycle', 'xs rd', 'start')]
b += [text(20, 410, 'green = fixed rule: each Pi grabs min(left,right) fork first.', 'xs d', 'start')]
b += [text(20, 424, 'red X = the naive left-first grab (9.12) that closed the ring.', 'xs d', 'start')]
b += [text(20, 438, 'Only P4 (neighbors F4, F0) switches; everyone else grabs the same fork first either way, so the ring never re-closes.', 'xs d', 'start')]
add('diningphil', 'Dining philosophers: breaking the cycle', 'Under lowest-fork-first, philosophers 0-3 grab the same fork they always did, but P4 now reaches for F0 first (contending with P0) instead of F4, so the 5-cycle from 9.12 never forms.',
    svg(760, 460, 'Dining philosophers resource ordering fix', ''.join(b)))

# ================================================================ scheduling
b = []
# Running (top) directly above Ready (bottom-left); Blocked bottom-right.
# Every arrow is orthogonal (own x- or y-band) so no label ever sits on a line.
b += [rect(290, 30, 180, 56, 'pl'), text(380, 56, 'Running', 'h'), text(380, 72, 'on a CPU right now', 'xs d')]
b += [rect(60, 210, 180, 56, 'tl'), text(150, 236, 'Ready', 'h'), text(150, 252, 'runnable, waiting for a CPU', 'xs d')]
b += [rect(520, 210, 200, 56, 'dl'), text(620, 236, 'Blocked', 'h'), text(620, 252, 'waiting on I/O, lock, cond var, signal', 'xs d')]

# dispatch: Ready -> Running, lane x=110 (left of Ready's own column)
b += [arrow(110, 210, 110, 86, 'lng')]
b += [text(98, 150, 'scheduler', 'xs d', 'end'), text(98, 164, 'dispatch', 'xs d', 'end')]
# preempt: Running -> Ready, lane x=190
b += [arrow(190, 86, 190, 210, 'lna')]
b += [text(202, 130, 'preempted: timer tick, or a', 'xs d', 'start'), text(202, 144, 'higher-priority thread ready', 'xs d', 'start')]

# blocks: Running -> Blocked, routed along the top then down (own y/x band)
b += [poly_arrow([(470, 58), (650, 58), (650, 210)], 'lnc')]
b += [text(662, 120, 'blocks: I/O wait,', 'xs d', 'start'), text(662, 134, 'mutex/cond wait,', 'xs d', 'start'), text(662, 148, 'signal wait', 'xs d', 'start')]

# event ready: Blocked -> Ready, horizontal band below both boxes
b += [arrow(520, 280, 240, 280, 'lng')]
b += [text(380, 306, 'event ready: I/O done, mutex unlocked + woken,', 'xs d'), text(380, 320, 'signal delivered, or timer expires -- back to Ready, not straight to Running', 'xs d')]

b += [circle(30, 238, 22, 'box'), text(30, 234, 'new', 'xs d'), text(30, 246, 'thread', 'xs d'),
      arrow(52, 238, 58, 238, 'lnd')]
b += [circle(30, 58, 22, 'box'), text(30, 54, 'thread', 'xs d'), text(30, 66, 'exits', 'xs d'),
      arrow(288, 58, 54, 58, 'lnd')]
b += [text(20, 20, 'Only one thread per CPU can be Running; many can be Ready or Blocked at once.', 'xs d', 'start')]
b += [text(20, 420, 'Preemption needs no cooperation from the running', 'xs d', 'start'), text(20, 434, 'thread: the kernel can take the CPU away at essentially any point.', 'xs d', 'start')]
add('scheduling', 'Thread states under preemptive scheduling', 'The kernel, not the thread, decides when Running gives up the CPU. A CPU-bound thread that never blocks is still moved to Ready by a timer tick or a higher-priority thread becoming ready.',
    svg(760, 460, 'Thread state diagram: running, ready, blocked', ''.join(b)))

# ================================================================ ipcmodel
b = []
b += [rect(20, 20, 160, 400, 'box'), text(100, 46, 'Process A', 'h')]
b += [rect(580, 20, 160, 400, 'box'), text(660, 46, 'Process B', 'h')]

# Row 1: pipe / FIFO -- byte stream, no boundaries
y = 90
b += [text(30, y - 14, 'pipe() / mkfifo(): byte stream, no message boundaries', 's h', 'start')]
b += [arrow(180, y + 14, 580, y + 14, 'lna')]
b += [text(380, y + 34, 'anonymous pipe: only fork() descendants.  named FIFO: any process opening that pathname.', 'xs d')]

# Row 2: message queue -- discrete, priority-ordered
y = 168
b += [text(30, y - 14, 'POSIX message queue: discrete, priority-ordered messages', 's h', 'start')]
mx = 260
for i, p in enumerate(['pri 3', 'pri 1', 'pri 1']):
    b += [rect(mx + i * 60, y, 50, 26, 'dl', 3), text(mx + i * 60 + 25, y + 17, p, 'xs')]
b += [arrow(180, y + 13, mx - 6, y + 13, 'lna'), arrow(mx + 3 * 60 + 6, y + 13, 580, y + 13, 'lnc')]
b += [text(380, y + 44, 'kernel copies each message; mq_receive() drains highest priority first', 'xs d')]

# Row 3: shared memory -- direct, no built-in sync
y = 246
b += [text(30, y - 14, 'shm_open()+mmap(): same physical memory, no copy', 's h', 'start')]
b += [rect(300, y, 160, 46, 'er'), text(380, y + 20, 'shared pages', 'h'), text(380, y + 36, 'no transfer step at all', 'xs d')]
b += [line(180, y + 23, 300, y + 23, 'lnr'), line(460, y + 23, 580, y + 23, 'lnr')]
b += [text(380, y + 68, 'both processes see the same bytes instantly -- but nothing serializes who wrote what when:', 'xs rd'),
      text(380, y + 82, 'a mutex or semaphore placed inside the segment (PTHREAD_PROCESS_SHARED) is mandatory, not optional', 'xs rd')]

# Row 4: signal -- one bit, not data transfer
y = 356
b += [text(30, y - 14, 'signal: one bit of information, not a data-transfer mechanism', 's h', 'start')]
b += [line(180, y + 13, 580, y + 13, 'lnd'), text(380, y + 6, 'e.g. SIGUSR1', 'xs d')]
b += [text(20, 436, 'Pipes and queues: the kernel serializes its own buffer, so no extra lock is needed for the transfer itself.', 'xs d', 'start')]
add('ipcmodel', 'POSIX IPC mechanisms at a glance', 'Pipes move an unstructured byte stream; message queues move discrete, priority-ordered messages; shared memory gives direct access to the same physical pages with no built-in synchronization at all; a signal only carries one bit of information.',
    svg(760, 460, 'Four POSIX IPC mechanisms between two processes', ''.join(b)))

# ================================================================ vmpaging
b = []
b += [text(150, 20, 'CPU / MMU', 's h'), text(610, 20, 'Kernel fault handler', 's h'), line(150, 34, 150, 430), line(610, 34, 610, 430)]


def step(y, n, label, direction, cls, sub=None):
    s = []
    if direction == '>':
        s += [arrow(150, y, 610, y + 8, cls)]
    elif direction == '<':
        s += [arrow(610, y, 150, y + 8, cls)]
    s += [text(380, y - 6, label, 's')]
    if sub:
        s += [text(380, y + 20, sub, 'xs d')]
    s += [text(6, y + 4, str(n), 's ac', 'start')]
    return s


b += [rect(160, 50, 220, 26, 'box'), text(270, 67, 'load/store to virtual addr V', 'xs d'), text(6, 66, '1', 's ac', 'start')]
b += [rect(160, 84, 220, 26, 'box'), text(270, 101, 'TLB miss -> walk page table', 'xs d'), text(6, 100, '2', 's ac', 'start')]
b += step(148, 3, 'no valid / permission-matching PTE', '>', 'lnr', 'CPU raises page-fault exception')
b += step(198, 4, 'fault handler looks up the VMA covering V', '<', 'lnc', 'is this address legitimate, and for what access?')
b += [rect(160, 232, 450, 26, 'pl'), text(385, 249, 'legitimate: allocate/zero a frame, or read it in from disk (major fault)', 'xs')]
b += step(288, 5, 'install new page table entry, refresh TLB', '<', 'lna')
b += step(338, 6, 'return to user mode, re-execute the instruction', '<', 'lng', 'now succeeds')
b += [rect(160, 372, 450, 30, 'er'), text(385, 391, 'illegitimate: not covered by any VMA, or wrong access type', 'xs')]
b += [poly_arrow([(610, 226), (680, 226), (680, 386), (610, 386)], 'lnr')]
b += [text(385, 416, 'delivered: SIGSEGV (bad address), or SIGBUS for the mmap.3p whole-page-beyond-object case', 'xs rd')]
b += [text(20, 436, 'Minor fault: no disk I/O (zero/allocate a frame). Major fault: page is read in from disk, orders of magnitude slower.', 'xs d', 'start')]
add('vmpaging', 'Anatomy of a page fault', 'MMU miss to exception to VMA lookup to frame install to resume -- the deliberate mechanism behind lazy allocation and demand paging. Only an address outside every VMA, or a disallowed access, turns into SIGSEGV/SIGBUS.',
    svg(830, 452, 'Sequence of a hardware page fault handled by the kernel', ''.join(b)))

# ================================================================ isrflow
b = []
b += [text(20, 24, 'Task context', 's h', 'start'), text(20, 200, 'Interrupt context (ISR = top half)', 's h', 'start'), text(20, 340, 'Bottom half (worker, normal context)', 's h', 'start')]

# task lane: running, interrupted gap, resumes
b += [rect(60, 40, 300, 50, 'pl'), text(210, 70, 'thread runs normally', 's h')]
b += [rect(360, 40, 60, 50, 'box', 3, 'stroke-dasharray="4,3"'), text(390, 70, 'paused', 'xs d')]
b += [rect(420, 40, 300, 50, 'pl'), text(570, 70, 'thread resumes exactly here', 's h')]
b += [line(390, 90, 390, 130, 'lnd')]

# interrupt fires
b += [poly_arrow([(390, 15), (390, 40)], 'lnr')]
b += [text(390, 12, 'IRQ fires', 'xs rd')]
b += [rect(345, 216, 130, 56, 'tl'), text(410, 238, 'ISR (top half)', 's h'), text(410, 254, 'ack hw + copy fixed', 'xs d'), text(410, 266, 'record -- bounded, no block', 'xs d')]
b += [poly_arrow([(390, 90), (390, 216)], 'lnr'), text(300, 148, 'preempts the thread,', 'xs d', 'end'), text(300, 160, 'no scheduler slot of its own', 'xs d', 'end')]
b += [poly_arrow([(410, 272), (410, 290), (390, 130)], 'lng')]
b += [text(430, 300, 'returns; interrupted thread resumes', 'xs d', 'start')]

# ring buffer between ISR and bottom half
b += [text(540, 210, 'SPSC ring buffer (14.16)', 's h')]
for i in range(6):
    b += [rect(520 + i * 35, 224, 30, 30, 'dl' if i in (1, 2, 3) else 'box', 2)]
b += [text(520, 268, 'tail (consumer)', 'xs d', 'start'), text(730, 268, 'head (producer)', 'xs d', 'end')]
b += [arrow(475, 244, 520, 244, 'lna'), text(700, 244, '', 'xs')]

b += [rect(300, 356, 220, 56, 'box'), text(410, 378, 'worker task', 'h'), text(410, 394, 'dequeue record, do the real', 'xs d'), text(410, 406, 'processing -- free to block/alloc', 'xs d')]
b += [poly_arrow([(600, 260), (665, 260), (665, 384), (520, 384)], 'lnc')]
b += [text(668, 320, 'consumed later,', 'xs d', 'end'), text(668, 332, 'in normal context', 'xs d', 'end')]

b += [text(20, 448, 'Only the amber box runs in interrupt context; everything else (including the worker) can safely block, allocate, and take as long as it needs.', 'xs d', 'start')]
add('isrflow', 'Top half / bottom half split', 'The ISR does the minimum, bounded, non-blocking work and hands a fixed-size record to a lock-free SPSC ring buffer; the interrupted thread resumes right after, and a separate worker drains the ring later in ordinary schedulable context.',
    svg(760, 460, 'ISR top half handing off to a bottom-half worker via a ring buffer', ''.join(b)))

# ================================================================ threadpool
b = []
b += [rect(300, 170, 160, 110, 'tl'), text(380, 194, 'shared queue', 'h'), text(380, 210, 'qhead/qtail/qcount', 'xs d')]
for i in range(4):
    b += [rect(316 + i * 34, 224, 30, 40, 'box' if i > 0 else 'dl', 2)]
b += [text(380, 278, 'circular buffer, size NTASKS', 'xs d')]
b += [text(380, 300, 'protected by: qlock (mutex) + qnotempty (cond var)', 'xs h')]

b += [rect(70, 60, 160, 56, 'box'), text(150, 84, 'main: submit(id)', 'h'), text(150, 100, 'lock, enqueue, signal, unlock', 'xs d')]
b += [arrow(230, 100, 300, 190, 'lna')]

for i in range(4):
    y = 60 + i * 90
    b += [rect(560, y, 180, 60, 'pl'), text(650, y + 20, f'worker {i}', 'h'),
          text(650, y + 36, 'lock; while(empty && !down)', 'xs d'), text(650, y + 50, 'cond_wait; dequeue; unlock; work', 'xs d')]
    b += [poly_arrow([(560, y + 30), (460, 225)], 'lnc')]

b += [rect(70, 380, 200, 60, 'er'), text(170, 402, 'shutdown', 'h'), text(170, 418, 'lock; shutdown=1;', 'xs d'), text(170, 432, 'broadcast(qnotempty); unlock', 'xs d')]
b += [poly_arrow([(270, 410), (560, 405), (560, 380)], 'lnr')]
b += [text(20, 350, 'broadcast (not signal): every worker may be waiting and must wake to notice', 'xs rd', 'start')]
b += [text(20, 362, 'shutdown_flag and exit -- a single signal() would leave some workers asleep forever', 'xs rd', 'start')]
b += [text(20, 30, 'One mutex + one cond var guard the queue; each worker rechecks its predicate in a loop before touching queue state (module 5 rule).', 'xs d', 'start')]
add('threadpool', 'Fixed-size thread pool with a shared queue', 'A mutex and condition variable guard a circular task queue; N workers loop wait/dequeue/work, and a shutdown flag plus a broadcast (never a single signal) wakes every worker to exit cleanly before they are joined.',
    svg(760, 460, 'Thread pool with shared work queue and shutdown broadcast', ''.join(b)))

dlib.write(ROOT, 'diagrams_B.js')
