#!/usr/bin/env python3
"""Generator for assigned figures: procmem, forkmodel, mutexstate, condvarflow, rwlock, memorder, deadlock."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'study_common'))
import dlib
from dlib import rect, text, line, arrow, poly_arrow, svg, add, bracket, fld

# ============================================================== procmem (1.04)
# Address space layout: main thread stack near top growing down, mmap'd thread
# stacks between heap and main stack, heap growing up, data/text at bottom.
b = []
b += [text(380, 16, 'Every thread shares text/data/heap; only stacks are per-thread.', 's ac')]
# outer container
b += [rect(120, 34, 520, 406, 'box')]
b += [text(650, 52, 'high addresses', 'xs f', 'end'), text(650, 430, 'low addresses', 'xs f', 'end')]
# main stack (top), growing down
b += [rect(180, 50, 200, 60, 'tl'), text(280, 74, 'Main thread stack', 'h'), text(280, 92, 'grows downward', 's d')]
b += [arrow(280, 112, 280, 134, 'lna')]
# mmap region with extra thread stacks
b += [rect(150, 136, 460, 152, 'grp')]
b += [text(380, 154, 'mmap region', 's h')]
b += [rect(180, 168, 150, 50, 'dl'), text(255, 188, 'Thread 2 stack', 's'), text(255, 204, 'mmap-ed', 'xs d')]
b += [rect(360, 168, 150, 50, 'dl'), text(435, 188, 'Thread 3 stack', 's'), text(435, 204, 'mmap-ed', 'xs d')]
b += [rect(270, 230, 150, 46, 'dl'), text(345, 250, 'Thread N stack', 's'), text(345, 266, '... more as created', 'xs d')]
# heap growing up
b += [rect(220, 300, 200, 46, 'pl'), text(320, 320, 'Heap', 'h'), text(320, 336, 'grows upward (malloc)', 's d')]
b += [arrow(320, 300, 320, 288, 'lng')]
# data + text at bottom
b += [rect(180, 356, 200, 34, 'box'), text(280, 377, 'Initialized/BSS data (globals)', 's')]
b += [rect(180, 398, 200, 34, 'box'), text(280, 419, 'Text (code)', 's')]
b += [text(460, 377, 'global_data lives here', 'xs d', 'start')]
b += [text(460, 419, 'main(), worker() code here', 'xs d', 'start')]
add('procmem', 'Thread stacks in the address space',
    'The initial threads stack keeps its usual spot near the top, growing down. Every later pthread_create() gets its own stack mmap-ed into the region between the heap and that main stack, not carved out of it. Heap, data and text stay shared and unmoved.',
    svg(760, 458, 'Multithreaded process address space layout', ''.join(b)))

# ============================================================== forkmodel (2.04, 2.10)
b = []
b += [text(380, 20, 'Before fork(): one process, one address space', 's h')]
b += [rect(280, 34, 200, 40, 'box'), text(380, 58, 'Parent process (2 threads)', 's')]
b += [arrow(380, 74, 380, 96, 'lna')]
b += [text(380, 108, 'fork()', 'h')]
b += [arrow(345, 116, 200, 140, 'lna'), arrow(415, 116, 560, 140, 'lnc')]
# parent side after fork
b += [rect(90, 142, 260, 100, 'tl')]
b += [text(220, 162, 'Parent (after fork)', 'h')]
b += [text(220, 180, 'still 2 threads', 's d')]
b += [rect(110, 194, 100, 34, 'box'), text(160, 216, 'thread A', 'xs')]
b += [rect(240, 194, 90, 34, 'grp'), text(285, 210, 'thread B', 'xs d'), text(285, 224, '(this one forked)', 'xs f')]
# child side after fork
b += [rect(410, 142, 260, 100, 'dl')]
b += [text(540, 162, 'Child (after fork)', 'h')]
b += [text(540, 180, 'only 1 thread (POSIX)', 's d')]
b += [rect(460, 194, 160, 34, 'box'), text(540, 216, 'thread B only (the caller)', 'xs')]
b += [text(540, 236, 'thread A: gone, no cleanup run', 'xs rd')]
# shared physical pages, COW
b += [text(380, 264, 'Immediately after fork: same physical pages, marked read-only + COW', 's h')]
b += [rect(150, 278, 460, 60, 'grp')]
b += [rect(200, 292, 90, 32, 'pl'), text(245, 312, 'page P (RO)', 'xs')]
b += [line(290, 308, 380, 296, 'ln'), line(290, 308, 380, 320, 'ln')]
b += [text(400, 300, 'parent PTE', 'xs d', 'start'), text(400, 320, 'child PTE', 'xs d', 'start')]
b += [text(560, 308, 'both point to the SAME frame', 'xs d', 'start')]
b += [text(380, 356, 'Child writes global_val = 999:', 's h')]
b += [rect(150, 368, 200, 44, 'er'), text(250, 388, 'page fault (write to RO)', 'xs'), text(250, 404, 'kernel copies page', 'xs d')]
b += [arrow(350, 390, 430, 390, 'lnr')]
b += [rect(430, 368, 180, 44, 'dl'), text(520, 388, 'child gets NEW page', 'xs'), text(520, 404, 'parent page untouched', 'xs d')]
b += [text(380, 432, 'Parent still sees global_val=100 at the same virtual address; only the child page changed.', 'xs d')]
add('forkmodel', 'fork(): shared pages, then copy-on-write',
    'Right after fork(), parent and child share the same physical pages read-only. A write triggers a page fault that copies only for the writer. Separately, POSIX gives the child exactly one thread: the caller, with every other thread simply gone.',
    svg(760, 452, 'Copy-on-write fork model and single-thread child', ''.join(b)))

# ============================================================== mutexstate (4.10)
b = []
b += [text(380, 18, 'pthread_mutex_lock() / unlock() timeline', 's h')]
b += [text(60, 38, 'Thread 1 (owner)', 's h', 'start')]
b += [line(150, 30, 150, 186, 'lnd'), line(680, 30, 680, 186, 'lnd')]
# thread1 timeline
b += [rect(150, 50, 140, 32, 'pl'), text(220, 70, 'holds mutex', 'xs')]
b += [rect(290, 50, 220, 32, 'pl'), text(400, 66, 'fast-path unlock:', 'xs'), text(400, 78, 'atomic CAS, no syscall', 'xs')]
b += [arrow(150, 100, 630, 100, 'ln')]
b += [text(630, 112, 'time ->', 'xs f', 'end')]
b += [text(60, 118, 'Thread 2 (contender)', 's h', 'start')]
# thread2 timeline
b += [rect(180, 130, 90, 32, 'tl'), text(225, 150, 'lock(): CAS fails', 'xs')]
b += [arrow(270, 146, 340, 146, 'lnr')]
b += [rect(340, 130, 170, 32, 'er'), text(425, 146, 'futex syscall: sleep', 'xs')]
b += [text(425, 168, '(blocked, off run queue)', 'xs d')]
b += [arrow(510, 146, 570, 146, 'lng')]
b += [rect(570, 130, 90, 32, 'pl'), text(615, 146, 'woken, owns', 'xs'), text(615, 158, 'mutex', 'xs')]
b += [line(150, 194, 680, 194, 'lnd')]
b += [text(380, 214, 'unlock() wakes at most one waiter; POSIX leaves WHICH one to "the scheduling policy" (not FIFO).', 's d')]
b += [text(380, 236, 'Fast path (no contention): pure userspace atomic op. Slow path (contention): futex sleep/wake round trip.', 's d')]
b += [text(380, 258, 'Amber/green = fast-path work and holding, red = blocked/slow-path wait.', 'xs f')]
add('mutexstate', 'Mutex fast path vs. contended slow path',
    'Thread 1 locks and unlocks on the cheap userspace fast path (green/amber). Thread 2 loses the race, so glibc falls back to a futex syscall and the kernel parks it (red) until unlock wakes it. POSIX guarantees the wake but not the wake order.',
    svg(760, 272, 'Mutex fast path and futex-based slow path timeline', ''.join(b)))

# ============================================================== condvarflow (5.13)
b = []
b += [text(380, 18, 'Bounded queue: not_empty side (producer -> consumer)', 's h')]
b += [rect(40, 34, 210, 130, 'tl')]
b += [text(145, 54, 'Producer', 'h')]
b += [text(145, 74, 'q_push():', 's d')]
b += [text(145, 92, 'lock(mtx)', 'xs')]
b += [text(145, 108, 'buf[tail]=val; count++', 'xs')]
b += [text(145, 126, 'cond_signal(not_empty)', 'xs ac')]
b += [text(145, 144, 'unlock(mtx)', 'xs')]
b += [rect(275, 34, 210, 130, 'grp')]
b += [text(380, 54, 'Shared state (1 mutex)', 'h')]
b += [text(380, 76, 'mtx protects:', 's d')]
b += [text(380, 94, 'buf[], head, tail, count', 'xs')]
b += [text(380, 114, 'cond not_empty', 'xs')]
b += [text(380, 132, 'cond not_full', 'xs')]
b += [rect(510, 34, 210, 130, 'dl')]
b += [text(615, 54, 'Consumer', 'h')]
b += [text(615, 74, 'q_pop():', 's d')]
b += [text(615, 92, 'lock(mtx)', 'xs')]
b += [text(615, 110, 'while(count==0 && !done)', 'xs'), text(615, 124, ' cond_wait(not_empty, mtx)', 'xs rd')]
b += [text(615, 142, 're-check predicate, then pop', 'xs')]
b += [arrow(250, 100, 275, 100, 'lna'), arrow(485, 100, 510, 100, 'lna')]
b += [text(380, 176, 'Wake path: producer pushes -> signals not_empty -> ONE blocked consumer wakes,', 's d')]
b += [text(380, 192, 'RE-CHECKS the while() predicate (not just trusts the wake), then proceeds.', 's d')]
b += [rect(120, 214, 520, 70, 'box')]
b += [text(380, 232, 'Shutdown: after joining producers, main sets done_producing=1', 's')]
b += [text(380, 250, 'and cond_broadcast(not_empty) -- EVERY waiting consumer wakes,', 's')]
b += [text(380, 268, 'not just one, so none blocks forever once production has ended.', 's')]
b += [text(380, 300, 'Result: 2 producers, 3 consumers, cap=4, 20 items -> consumed_count=20, sum=210, every run.', 's h')]
add('condvarflow', 'Producer-consumer condition-variable flow',
    'One mutex guards the queue and both condition variables. A push signals not_empty (targeted wake, amber); a waiting consumer wakes, re-checks its while-predicate, then pops. done_producing is broadcast so every consumer, not just one, learns to stop.',
    svg(760, 316, 'Condition-variable signal/wait flow for a bounded queue', ''.join(b)))

# ============================================================== rwlock (6.10)
b = []
b += [text(380, 18, 'rwlock under load: 4 readers spinning, 1 writer waiting', 's h')]
b += [text(60, 40, 'readers (rdlock loop)', 's h', 'start')]
for i in range(4):
    y = 52 + i * 26
    b += [rect(60, y, 130, 20, 'pl'), text(125, y + 14, f'reader {i+1}: rdlock/unlock', 'xs')]
b += [poly_arrow([(190, 62), (230, 62), (230, 150)], 'lng')]
b += [text(235, 100, 'tens of millions', 'xs d', 'start'), text(235, 114, 'of acquisitions', 'xs d', 'start')]
b += [rect(320, 62, 160, 96, 'tl')]
b += [text(400, 82, 'writer', 'h')]
b += [text(400, 100, 'wrlock() -- blocked', 'xs')]
b += [text(400, 116, 'waiting ...', 'xs d')]
b += [text(400, 136, 'measured: 0.068-0.148s', 'xs h')]
b += [arrow(480, 110, 560, 110, 'lna')]
b += [rect(560, 62, 160, 96, 'dl')]
b += [text(640, 82, 'writer', 'h')]
b += [text(640, 100, 'acquired wrlock', 'xs')]
b += [text(640, 118, 'glibc 2.39: got in', 'xs d')]
b += [text(640, 134, 'within ~70-150ms', 'xs d')]
b += [line(60, 176, 720, 176, 'lnd')]
b += [text(380, 198, 'POSIX only says an implementation "may favor writers to avoid starvation" -- a permission, not a guarantee.', 's d')]
b += [text(380, 220, 'This glibc default rwlock kind did not starve the writer here; an older glibc (reader-preferring) plausibly would.', 's d')]
b += [text(380, 242, 'Green = readers freely re-acquiring; amber = writer blocked and waiting; blue = writer finally holds the lock.', 'xs f')]
add('rwlock', 'Reader flood vs. one waiting writer',
    'Four readers repeatedly grab and release the read lock while one writer waits for wrlock(). On this glibc (2.39) the writer still got in within a fraction of a second across three runs, even against millions of reader acquisitions -- not a POSIX guarantee, just this implementation default.',
    svg(760, 262, 'rwlock reader contention against one waiting writer', ''.join(b)))

# ============================================================== memorder (7.06)
b = []
b += [text(380, 18, 'Publish pattern: release-store paired with acquire-load', 's h')]
b += [rect(60, 36, 260, 130, 'tl')]
b += [text(190, 56, 'writer_thread', 'h')]
b += [text(190, 78, 'payload = 42;', 's'), text(190, 94, '(ordinary, non-atomic write)', 'xs d')]
b += [rect(100, 108, 180, 34, 'ac' if False else 'tl'), text(190, 130, 'store_explicit(ready, 1,', 'xs h'), ]
b += [text(190, 143, 'memory_order_release)', 'xs h')]
b += [rect(440, 36, 260, 130, 'dl')]
b += [text(570, 56, 'reader_thread', 'h')]
b += [rect(480, 70, 180, 34, 'dl'), text(570, 89, 'while (load_explicit(ready,', 'xs h'), text(570, 100, 'memory_order_acquire) == 0);', 'xs h')]
b += [text(570, 122, 'spins until it observes 1', 'xs d')]
b += [text(570, 142, 'reads payload -> guaranteed 42', 's h')]
b += [arrow(200, 152, 443, 87, 'lna')]
b += [text(380, 178, '"synchronizes-with" edge: release-store', 's ac')]
b += [text(380, 192, 'the read that OBSERVES value 1 is what makes it happen', 's d')]
b += [rect(60, 214, 640, 90, 'box')]
b += [text(380, 234, 'Guarantee: once the reader\'s acquire-load sees the value the release-store wrote,', 's')]
b += [text(380, 250, 'every ordinary memory write the writer made BEFORE that release (here: payload=42)', 's')]
b += [text(380, 266, 'is visible to the reader AFTER its acquire. Says nothing about a third thread.', 's')]
b += [text(380, 288, 'Result: 50000/50000 runs, reader always saw payload==42. Relaxed order on either side would drop this guarantee.', 'xs d')]
add('memorder', 'Acquire/release publish pattern',
    'The writer stores plain data, then release-stores a ready flag (amber). The reader spins on an acquire-load of that same flag (blue); only once it observes the value 1 does the synchronizes-with edge form, guaranteeing the plain write is visible. 50000/50000 runs saw payload==42.',
    svg(760, 316, 'Release-store to acquire-load synchronizes-with edge', ''.join(b)))

# ============================================================== deadlock (8.04)
b = []
b += [text(380, 18, 'AB-BA deadlock: opposite lock order -> circular wait', 's h')]
b += [rect(60, 40, 230, 110, 'tl')]
b += [text(175, 60, 'thread1', 'h')]
b += [text(175, 80, 'lock(A)  -- OK', 's')]
b += [text(175, 98, 'sleep(200ms)', 's d')]
b += [text(175, 118, 'lock(B)  -- BLOCKS', 's rd')]
b += [rect(470, 40, 230, 110, 'dl')]
b += [text(585, 60, 'thread2', 'h')]
b += [text(585, 80, 'lock(B)  -- OK', 's')]
b += [text(585, 98, 'sleep(200ms)', 's d')]
b += [text(585, 118, 'lock(A)  -- BLOCKS', 's rd')]
# mutex boxes in the middle
b += [rect(320, 190, 60, 40, 'box'), text(350, 214, 'A', 'h')]
b += [rect(380, 190, 60, 40, 'box'), text(410, 214, 'B', 'h')]
# wait-for cycle arrows
b += [arrow(175, 150, 335, 195, 'lng')]
b += [text(178, 142, 't1 holds A', 'xs', 'start')]
b += [arrow(585, 150, 425, 195, 'lnc')]
b += [text(582, 142, 't2 holds B', 'xs', 'end')]
b += [poly_arrow([(320, 210), (270, 210), (270, 75), (300, 60)], 'lnr')]
b += [text(230, 130, 't1 wants B', 'xs rd', 'start')]
b += [poly_arrow([(440, 210), (480, 210), (480, 75), (460, 60)], 'lnr')]
b += [text(465, 130, 't2 wants A', 'xs rd', 'start')]
b += [text(380, 258, 'Circular wait: t1 holds A, wants B; t2 holds B, wants A -- neither can proceed. All four Coffman', 's d')]
b += [text(380, 274, 'conditions hold: mutual exclusion, hold-and-wait, no preemption, circular wait.', 's d')]
b += [rect(180, 292, 400, 40, 'er'), text(380, 310, 'run under timeout 3: process hangs', 'xs h'), text(380, 326, 'shell reports exit code 124', 'xs d')]
add('deadlock', 'AB-BA two-mutex deadlock',
    'thread1 takes A then waits on B; thread2 takes B then waits on A (red arrows = the blocked request each thread cannot satisfy). Every Coffman condition holds at once, so the pair hangs forever; the compiled repro was killed by timeout 3 (exit 124).',
    svg(760, 344, 'Two threads deadlocked on opposite mutex acquisition order', ''.join(b)))

dlib.write(os.path.dirname(os.path.abspath(__file__)), 'diagrams_A.js')
