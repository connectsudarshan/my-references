MODULE = dict(id=2, title="Memory & the Object Model",
              desc="Object layout, reference counting and cycles, allocator behaviour, leak hunting in long-running services, and choosing the right data representation for millions of records.")

QUESTIONS = [

P("Debug", "A long-running Python service (or test orchestrator) grows from 300 MB to 6 GB over three days. How do you find the cause?",
short="""First decide whether it's a **leak** (live objects accumulating) or **fragmentation/allocator retention** (freed memory not returned to the OS). Compare RSS with the Python heap from `tracemalloc`; if the traced heap grows, take periodic snapshots and diff them by traceback to find the allocation site; if it doesn't, suspect C extensions or fragmentation, and use memray or native tools. Then fix the root cause and add a memory metric with an alert.""",
deep="""A structured approach an interviewer wants to hear:

1. **Characterize**: steady linear growth suggests an unbounded cache or list; step growth suggests specific requests or test types; sawtooth that never returns to baseline suggests fragmentation. Correlate with workload metrics.
2. **Python heap vs process**: `tracemalloc.get_traced_memory()` shows memory allocated through Python's allocators. If RSS grows but traced memory is flat, the growth is in C extensions, native libraries or allocator retention.
3. **Snapshot diffing**: enable `tracemalloc.start(25)` (frames of traceback), take a snapshot at t0 and t1, and use `snapshot.compare_to(old, "traceback")`. The top entries show which lines keep allocating memory that stays alive.
4. **Who holds the objects?**: `gc.get_referrers(obj)`, `objgraph.show_backrefs`, or memray's flame graphs. Typical culprits: module-level dicts used as caches, `lru_cache` on methods (keeps `self` alive), listeners never unsubscribed, exceptions stored with tracebacks (keeping frames and locals), growing `logging` handlers, per-request data stored on long-lived objects.
5. **Fix and guard**: bound caches (`maxsize`, TTL), weak references, explicit cleanup; add an RSS and heap metric; for fragmentation, recycle workers (`max_requests` in gunicorn, `maxtasksperchild` in multiprocessing).

In production, tracemalloc has overhead (roughly 2x memory for tracking and noticeable CPU), so enable it on one canary instance or on demand via a signal/endpoint.""",
code=r'''
import tracemalloc, gc

class ResultCache:                                  # the "leak": unbounded, never evicted
    _store = {}
    @classmethod
    def remember(cls, run_id, payload): cls._store[run_id] = payload

def handle_test_run(run_id):
    log_lines = [f"{run_id}: step {i} OK" for i in range(200)]
    ResultCache.remember(run_id, log_lines)         # keeps every run's logs forever

tracemalloc.start(10)
for i in range(200): handle_test_run(f"warmup-{i}")
before = tracemalloc.take_snapshot()
for i in range(2000): handle_test_run(f"run-{i}")
after = tracemalloc.take_snapshot()

top = after.compare_to(before, "lineno")
for stat in top[:2]:
    frame = stat.traceback[0]
    print(f"+{stat.size_diff / 1024:8.0f} KiB  +{stat.count_diff:6} blocks  line {frame.lineno}")
cur, peak = tracemalloc.get_traced_memory()
print(f"traced now {cur / 1e6:.1f} MB, peak {peak / 1e6:.1f} MB, cached runs: {len(ResultCache._store)}")
''',
follow=(
"RSS keeps growing but `tracemalloc` shows a flat heap. What next? => The growth is outside Python's allocators: a C extension leak, native library buffers, or allocator fragmentation. Use memray with native tracking, compare `malloc` stats, test with a different allocator (jemalloc), and consider worker recycling as mitigation.",
"How would you enable this safely in production? => Only on one canary instance or behind an admin trigger that starts tracemalloc for a limited window, dumps snapshots to storage, and stops it; never globally, because of the overhead.",
"Why can storing exceptions leak memory? => `exc.__traceback__` references frames, which reference every local variable in them. Keep formatted strings, or call `traceback.clear_frames(tb)`.",
),
pitfall="Adding `gc.collect()` calls or raising memory limits without identifying who holds the objects. That hides the symptom and the service still dies, only later.",
signals="You separate leak from fragmentation, name the exact tools and their overhead, show how to find the allocation site and the holder, and finish with a guardrail (metric, alert, bounded cache).",
),

P("Concept", "How big is a Python object really? Estimate the memory for a list of 10 million integers.",
short="""Each object carries a header (reference count and type pointer, 16 bytes on 64-bit) plus its payload: a small `int` is 28 bytes, a float 24, an empty dict about 64 plus more. A list stores 8-byte pointers. So 10 million distinct ints cost roughly 80 MB of pointers plus about 320 MB of int objects (28 bytes, rounded up to 32 by the allocator): around 400 MB, versus 80 MB in an `array('q')` or NumPy int64 array.""",
deep="""Every CPython object starts with `ob_refcnt` and `ob_type` (16 bytes). On top of that:

- `int`: variable-length digits; values below 2**30 need one digit, so 28 bytes.
- `float`: 24 bytes. `str`: roughly 40-50 bytes of header (version dependent) plus one byte per ASCII character; non-Latin text uses 2 or 4 bytes per character.
- `tuple`: about 40-48 bytes + 8 per item. `list`: 56 bytes + 8 per slot, over-allocated for growth.
- Instances of plain classes: the object plus a `__dict__` (or, since 3.11/3.12, inline values that avoid a separate dict until needed); `__slots__` objects are much smaller.

Allocation rounding: pymalloc rounds requests up to multiples of 16 bytes, so real usage is slightly higher than `sys.getsizeof`.

The Principal-level point: "one Python object per record" is often the wrong representation for large numeric data. Columnar storage (`array`, NumPy, Arrow) stores raw values contiguously, uses 5-10x less memory and enables vectorized processing.""",
code=r'''
import array, sys, tracemalloc

for v in (0, 2**30, 2**100, 1.5, "a", "é", (), [], {}):
    print(f"{v!r:>35}  {sys.getsizeof(v):4} bytes")

def measure(make):
    tracemalloc.start(); obj = make(); cur = tracemalloc.get_traced_memory()[0]; tracemalloc.stop()
    return cur / 1e6

n = 1_000_000
print(f"list of {n:,} ints : {measure(lambda: [i * 7 for i in range(n)]):6.1f} MB")
print(f"array('q')         : {measure(lambda: array.array('q', (i * 7 for i in range(n)))):6.1f} MB")
''',
follow=(
"Why does `sys.getsizeof([big_object])` look tiny? => It reports only the list's own memory (header and pointer array), not the objects it references.",
"Why do small ints in the list above cost nothing extra for values below 257? => CPython caches ints from -5 to 256 as shared immortal objects; multiplying by 7 was used to avoid that.",
),
pitfall="Quoting `sys.getsizeof` of a container as its total memory. Use `tracemalloc` or recursive measurement for real footprints.",
signals="You know the per-object overhead numbers roughly, do the arithmetic out loud, and propose a columnar representation with the expected saving.",
),

P("Trap", "You delete a 2 GB list, `tracemalloc` shows it freed, but the process RSS barely drops. Is that a leak?",
short="""Not necessarily. CPython's small-object allocator (pymalloc) keeps memory in 1 MiB arenas (256 KiB before 3.10) and can return an arena to the OS only when every block in it is free, and the C `malloc` may also keep freed memory for reuse. Freed memory is usually reused by the same process later. It's a leak only if memory keeps growing across repeated identical workloads.""",
deep="""Layers involved:

- **pymalloc** handles objects up to 512 bytes, carving arenas into pools of fixed-size blocks. A single surviving object in an arena pins the whole arena.
- **Free lists** for some types (floats, tuples, frames) keep recently freed objects for fast reuse.
- **libc malloc** (glibc, the Windows heap) may not return freed pages to the OS immediately; glibc's `malloc_trim(0)` can sometimes release them.

How to reason about it in an interview:

1. Run the workload twice. If RSS returns to the same plateau (not higher), the memory is being reused: not a leak.
2. If RSS ratchets up each cycle while traced heap is flat, it's fragmentation or native memory.
3. Mitigations: process large batches in a **child process** that exits (memory fully returned), recycle workers periodically, reduce long-lived small objects mixed with short-lived ones, or try a different allocator (jemalloc/mimalloc; the free-threaded build uses mimalloc).""",
code=r'''
import tracemalloc, gc
tracemalloc.start()
def peak_cycle():
    data = [str(i) * 3 for i in range(300_000)]     # many small objects -> pymalloc arenas
    size = tracemalloc.get_traced_memory()[0]
    del data; gc.collect()
    return size
for cycle in range(3):
    in_use = peak_cycle()
    print(f"cycle {cycle}: traced while alive {in_use / 1e6:5.1f} MB -> after del {tracemalloc.get_traced_memory()[0] / 1e6:4.1f} MB")
print("traced heap returns to ~0 each cycle: memory is freed and reusable, even if RSS stays higher")
''',
follow=(
"How do you make sure a memory-hungry batch step gives memory back to the OS? => Run it in a separate process (`multiprocessing` or a subprocess) that exits when done; the OS reclaims everything.",
"What does `gc.collect()` do for this problem? => Nothing unless there are reference cycles; plain reference counting already freed the objects. It doesn't defragment arenas.",
),
pitfall="Reporting a \"leak\" from a single RSS reading after `del`. Leak detection needs repeated identical cycles and a trend.",
signals="You explain arenas, free lists and libc behaviour, propose the repeated-cycle test, and give practical mitigations like child processes and worker recycling.",
),

P("Design", "You must analyse 50 GB of device test logs on a machine with 16 GB of RAM, daily. Design the approach.",
short="""Never load it all. Stream line by line (or use `mmap` for random access) through a generator pipeline, keep only aggregates in memory, and parallelize by file or shard with a process pool, merging partial results. If the analysis is columnar and repeated, convert logs once to a compact format (Parquet with Arrow/Polars, or SQLite) and query that instead.""",
deep="""Clarify first: is it one pass for aggregate stats, or ad-hoc queries? Do we need exact counts or percentiles? How fresh must results be?

Design options:

1. **Streaming aggregation** (default): read files with buffered iteration, parse only needed fields (regex compiled once, or `str.split` with maxsplit), update counters/histograms. Memory is O(number of distinct keys), not O(data).
2. **Parallel by shard**: logs are usually many files; a `ProcessPoolExecutor` per file returns small partial aggregates (`Counter`s) that are merged. Avoid sending lines between processes: send file paths.
3. **mmap for binary or indexed access**: `mmap` + `re.finditer` or `memoryview` lets you scan or jump to offsets without copying the file into Python objects.
4. **Convert once, query many**: if engineers keep asking new questions, ingest into Parquet/DuckDB/SQLite with a schema; queries then run in seconds using columnar engines.
5. **Percentiles without storing everything**: use t-digest/HDR histograms or fixed buckets.

Operational concerns: make the job resumable (checkpoint processed files), validate malformed lines (count and sample them instead of crashing), and record input manifest and code version for reproducibility.""",
code=r'''
import mmap, os, re, tempfile, collections, itertools
from concurrent.futures import ProcessPoolExecutor

LINE = re.compile(rb"dev=(?P<dev>\w+) .*?status=(?P<st>\w+) lat_us=(?P<lat>\d+)")

def make_log(path, n, seed):
    with open(path, "wb") as f:
        for i in range(n):
            st = b"FAIL" if (i * seed) % 97 == 0 else b"PASS"
            f.write(b"2026-09-28T10:00:%02d dev=nvme%d op=write status=%s lat_us=%d\n" % (i % 60, i % 4, st, 80 + i % 900))

def summarize(path):
    counts, slow = collections.Counter(), 0
    with open(path, "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
        for m in LINE.finditer(mm):                  # scans the mapped file, no full read()
            counts[(m["dev"].decode(), m["st"].decode())] += 1
            slow += int(m["lat"]) > 900
    return counts, slow

if __name__ == "__main__":
    d = tempfile.mkdtemp()
    paths = [os.path.join(d, f"run{i}.log") for i in range(4)]
    for i, p in enumerate(paths): make_log(p, 50_000, i + 3)
    total, slow_total = collections.Counter(), 0
    with ProcessPoolExecutor(4) as ex:
        for counts, slow in ex.map(summarize, paths):   # send paths, receive small aggregates
            total.update(counts); slow_total += slow
    fails = {dev: n for (dev, st), n in sorted(total.items()) if st == "FAIL"}
    print("lines:", sum(total.values()), "| FAIL per device:", fails, "| slow ops:", slow_total)
''',
follow=(
"Why send file paths to workers instead of lines? => Pickling millions of lines through pipes costs more than the parsing itself; workers should read their own input and return small results.",
"How would you compute the p99 latency across 50 GB without storing every value? => Mergeable sketches (t-digest, HDR histogram) or fixed log-scale buckets per worker, merged at the end; exact p99 would need an external sort or a columnar engine.",
),
pitfall="Calling `f.read()` or `readlines()` \"because it's faster\", or building a pandas DataFrame of the whole dataset. Both blow past RAM long before 50 GB.",
signals="You clarify requirements, choose streaming plus sharded parallelism with small partial results, mention sketches for percentiles, and cover resumability and bad-input handling.",
),

P("Concept", "When is \"one Python object per record\" the wrong model, and what do you use instead?",
short="""When you have millions of homogeneous records processed in bulk. Per-object overhead (headers, dicts, pointers) dominates and every operation runs through the interpreter. Switch to `__slots__`/tuples for moderate counts, and to columnar storage (`array`, NumPy, Arrow/Polars) or a database for large ones.""",
deep="""Options in increasing efficiency:

- **dict per record**: flexible but the heaviest (hash table per record).
- **class with `__dict__`**: slightly better since 3.11+ (inline values), still heavy.
- **`__slots__` class / `dataclass(slots=True)`**: fixed fields, no per-instance dict; good middle ground with methods and type hints.
- **tuple / NamedTuple**: compact, immutable.
- **struct-of-arrays (columnar)**: one `array('d')` per field or a NumPy/Arrow table. Values are unboxed; memory drops 5-10x and aggregations run in C.

Choose based on access pattern: object-oriented access to a few records at a time favours classes; analytics over all records favours columns. A good design often uses both: columnar storage for the bulk, with a small view class that wraps one row on demand.""",
code=r'''
import tracemalloc, array
from dataclasses import dataclass
from typing import NamedTuple

N = 200_000
@dataclass
class Plain: lba: int; latency: float; ok: bool
@dataclass(slots=True)
class Slotted: lba: int; latency: float; ok: bool
class Row(NamedTuple): lba: int; latency: float; ok: bool

def mem(build):
    tracemalloc.start(); keep = build(); used = tracemalloc.get_traced_memory()[0]; tracemalloc.stop()
    return used / 1e6

print(f"dict per record   {mem(lambda: [{'lba': i, 'latency': i * 0.5, 'ok': True} for i in range(N)]):6.1f} MB")
print(f"dataclass         {mem(lambda: [Plain(i, i * 0.5, True) for i in range(N)]):6.1f} MB")
print(f"dataclass(slots)  {mem(lambda: [Slotted(i, i * 0.5, True) for i in range(N)]):6.1f} MB")
print(f"NamedTuple        {mem(lambda: [Row(i, i * 0.5, True) for i in range(N)]):6.1f} MB")
print(f"columnar arrays   {mem(lambda: (array.array('q', range(N)), array.array('d', (i * 0.5 for i in range(N))), bytearray(b'\x01') * N)):6.1f} MB")
''',
follow=(
"How do you keep an object-oriented API over columnar storage? => A lightweight view class (or a `NamedTuple` built on demand) that indexes into the columns for one row, while bulk operations work on whole columns.",
"What changed in 3.11-3.13 that made plain classes cheaper? => Instance attribute values can be stored inline in the object (no separate dict until you touch `__dict__` or add unusual attributes), which cuts per-instance memory.",
),
pitfall="Optimizing with `__slots__` for 5,000 objects. The saving is irrelevant there; pick representations based on record counts and access patterns.",
signals="You list the representation ladder with rough numbers, tie the choice to access patterns, and suggest hybrid designs.",
),

P("Trap", "Your event bus keeps a list of callbacks. Why does registering `self.on_event` cause a memory leak, and how do you fix it?",
short="""A bound method holds a strong reference to its instance (`method.__self__`). A long-lived bus holding bound methods keeps every subscriber object alive forever, even after the rest of the program dropped it. Fix with explicit unsubscribe (returning a handle, or a context manager) or store `weakref.WeakMethod` references that die with the object.""",
deep="""This leak pattern appears in GUI frameworks, test harnesses (per-test listeners registered on a session-wide bus), and plugin systems.

Fix options:

- **Explicit lifecycle**: `subscribe()` returns an unsubscribe callable; wrap in a context manager so tests always clean up.
- **Weak references**: `weakref.WeakMethod(obj.method)` for bound methods, `weakref.ref` for functions; the bus skips and prunes dead references. `weakref.WeakSet` works for objects implementing a known method.
- **Frameworks**: Django signals store receivers weakly by default (`weak=True`); Blinker supports weak references too.

Also watch for closures and lambdas capturing `self`: `bus.subscribe(lambda e: self.handle(e))` creates a strong reference via the closure and can't be made weak (the lambda itself would be collected immediately).""",
code=r'''
import gc, weakref

class Bus:
    def __init__(self, weak): self.weak, self.subs = weak, []
    def subscribe(self, cb):
        self.subs.append(weakref.WeakMethod(cb) if self.weak else cb)
    def publish(self, event):
        alive = []
        for s in self.subs:
            fn = s() if self.weak else s
            if fn is None: continue            # subscriber is gone: prune it
            fn(event); alive.append(s)
        self.subs = alive

class TestMonitor:
    def __init__(self, bus): self.seen = []; bus.subscribe(self.on_event)
    def on_event(self, e): self.seen.append(e)

for weak in (False, True):
    bus = Bus(weak)
    for _ in range(1000):
        TestMonitor(bus)                     # created per test, then dropped by the test
    gc.collect()
    alive = sum(isinstance(o, TestMonitor) for o in gc.get_objects())
    bus.publish("tick")
    print(f"weak={weak!s:5} TestMonitor objects still alive: {alive:4} | subscribers after publish: {len(bus.subs)}")
''',
follow=(
"Why can't you store a lambda with `weakref.ref`? => The only strong reference to the lambda is the one you're about to make weak, so it would be collected immediately; store the owner object weakly instead, or require explicit unsubscribe.",
"How do you catch this class of leak in CI? => A test that creates and drops N subscribers, runs `gc.collect()`, and asserts the count of those objects returns to baseline (or uses `weakref.ref` probes).",
),
pitfall="Using `WeakMethod` but forgetting to prune dead references, so the list itself grows with dead weakrefs and publish gets slower over time.",
signals="You explain `__self__` holding the instance, give both lifecycle and weakref fixes, mention the lambda trap, and propose a regression test.",
),

P("Concept", "Why do pre-fork servers and forked test workers lose copy-on-write memory sharing in Python, and what helps?",
short="""After `fork`, parent and child share memory pages until either writes to them. In CPython, merely **reading** an object updates its reference count, and the garbage collector writes to object headers, so shared pages get copied. Immortal objects (3.12+) help for core singletons, and `gc.freeze()` after preloading moves existing objects out of GC scans, reducing copies.""",
deep="""Pattern: a server (gunicorn with `--preload`, uWSGI) or a test runner loads a large model or dataset once, then forks workers expecting them to share that memory. In practice worker RSS climbs towards the full size because:

- Reference count increments/decrements touch every object that is used.
- The cyclic GC walks tracked objects and writes to their headers (the GC links).

Mitigations:

- `gc.freeze()` right before forking (and `gc.disable()` in the parent during preload) so the collector ignores those objects; Instagram reported large memory savings with this approach.
- Immortalization (PEP 683) makes objects like `None`, small ints and interned strings never change refcount.
- Store big read-only data outside Python objects: `mmap`-ed files, NumPy arrays, Arrow buffers, or shared memory; their pages aren't touched by refcounting.
- On Windows and macOS, `spawn` is the default, so there is no copy-on-write sharing at all; each worker loads its own copy.""",
code=r'''
import gc
gc.disable()                                   # preload phase: avoid GC touching everything
model = {f"feature_{i}": [i] * 8 for i in range(50_000)}   # big read-only structure
gc.freeze()                                    # move all current objects to the permanent generation
print("objects frozen:", gc.get_freeze_count() > 50_000)
gc.enable()
# ... here a pre-fork server would os.fork() workers that only READ `model` ...
print("gen counts after freeze:", gc.get_count())
''',
follow=(
"Does `gc.freeze()` stop reference counting writes? => No; it only stops the cyclic collector from traversing those objects. Refcount writes on objects you actually use still copy pages.",
"What's the most robust way to share a 2 GB read-only lookup table between 16 workers? => Put it in a memory-mapped file or shared-memory array (NumPy/Arrow) so pages are shared by the OS and never modified by Python's bookkeeping.",
),
pitfall="Assuming `--preload` automatically shares memory across workers. Without GC freezing or out-of-object storage, much of it gets copied within minutes.",
signals="You identify refcount and GC writes as the cause, cite `gc.freeze()` and immortal objects, and propose storing bulk data outside Python objects.",
),

]
