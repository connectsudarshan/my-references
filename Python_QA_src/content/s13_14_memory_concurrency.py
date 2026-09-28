QUESTIONS = [

# =============== 13. MEMORY MANAGEMENT & GARBAGE COLLECTION ===============
Q(13, "Moderate", "How does Python manage memory?",
"""CPython uses a private heap. Every object has a **reference count**; when it drops to zero the object is freed immediately. A **cyclic garbage collector** finds groups of objects that reference each other but are unreachable. Small objects (up to 512 bytes) come from the **pymalloc** allocator's pools for speed.""",
r'''
import sys
x = []
print(sys.getrefcount(x) - 1, "reference (getrefcount adds one for its own argument)")
y = x; z = [x]
print(sys.getrefcount(x) - 1, "references")
'''),

Q(13, "Moderate", "What is reference counting and what are its limitations?",
"""Each object tracks how many references point to it; `del`, rebinding or leaving scope decrements it, and at zero the object is freed deterministically. Limitation: **reference cycles** (A -> B -> A) never reach zero, so a separate cycle collector is needed. Refcount updates also cost time and complicate removing the GIL.""",
r'''
import gc, weakref
class Node:
    def __init__(self, name): self.name, self.other = name, None
a, b = Node("a"), Node("b")
a.other, b.other = b, a                    # cycle
probe = weakref.ref(a)
del a, b
print("alive after del:", probe() is not None)
gc.collect()
print("alive after gc.collect():", probe() is not None)
'''),

Q(13, "Difficult", "How does the cyclic garbage collector work?",
"""It tracks container objects (lists, dicts, class instances) in generations. Newly created objects start young; survivors are promoted. A collection subtracts internal references within the tracked set: objects whose count doesn't drop to zero from external references are reachable; the rest are garbage and get freed. Python 3.14 switched to an **incremental** collector (young + old generations) to reduce pause times. Tune with `gc.set_threshold`, inspect with `gc.get_count()`, `gc.get_stats()`.""",
r'''
import gc
print("enabled:", gc.isenabled(), "thresholds:", gc.get_threshold())
print("collected objects:", gc.collect())
'''),

Q(13, "Moderate", "What is `weakref` and when do you need it?",
"""A weak reference refers to an object without increasing its refcount, so it doesn't keep the object alive. Use it for caches (`WeakValueDictionary`), observer lists, and parent back-references to avoid cycles and leaks.""",
r'''
import weakref
class Image:
    def __init__(self, name): self.name = name
cache = weakref.WeakValueDictionary()
img = Image("logo.png")
cache["logo"] = img
print(list(cache.keys()))
del img
print(list(cache.keys()))            # entry disappeared with the object
'''),

Q(13, "Moderate", "What causes memory leaks in Python, and how do you find them?",
"""Common causes: growing global caches or lists, unbounded `lru_cache`, observers/callbacks never unregistered, reference cycles through objects with `__del__` in old versions, C-extension leaks, and holding large objects in long-lived closures or exceptions (tracebacks keep frames alive). Tools: `tracemalloc` snapshots and diffs, `gc.get_objects()`, objgraph, memray, and RSS monitoring.""",
r'''
import tracemalloc
tracemalloc.start()
leaky_cache = []
snap1 = tracemalloc.take_snapshot()
for i in range(10_000):
    leaky_cache.append("request-" + str(i) * 10)   # never cleared
snap2 = tracemalloc.take_snapshot()
top = snap2.compare_to(snap1, "lineno")[0]
print(f"+{top.size_diff / 1024:.0f} KiB at line {top.traceback[0].lineno}: {top.count_diff} new blocks")
'''),

Q(13, "Moderate", "What does `sys.getsizeof` measure, and what doesn't it?",
"""It returns the size of the object itself in bytes, **not** the objects it references. A list's size covers its pointer array, not its elements. For deep sizes, walk references or use `tracemalloc`/`pympler`.""",
r'''
import sys
small, big = [1, 2, 3], ["x" * 10_000] * 3
print(sys.getsizeof(small), sys.getsizeof(big))          # nearly the same
print(sys.getsizeof("x" * 10_000))
'''),

Q(13, "Moderate", "Does `del` free memory?",
"""`del name` removes a reference. Memory is freed only when the object's refcount reaches zero (and cycles are collected). Even then, CPython may keep freed memory in its pools for reuse instead of returning it to the OS, so process RSS may not shrink."""),

Q(13, "Difficult", "What is pymalloc and why might a Python process not return memory to the OS?",
"""pymalloc manages small objects in 256 KiB **arenas** divided into pools of fixed-size blocks. An arena can only be released to the OS when **every** block in it is free, so a few surviving objects can pin whole arenas. Fragmentation from long-running processes is common; restarting workers periodically (e.g. gunicorn `max_requests`) is a practical mitigation."""),

Q(13, "Moderate", "How can you reduce memory usage for many objects?",
"""- `__slots__` to drop per-instance `__dict__`
- tuples / `NamedTuple` instead of small classes
- generators instead of lists
- `array`, NumPy or pandas for numeric data; categorical dtypes for repeated strings
- `sys.intern` or flyweights for repeated strings
- stream data instead of loading it whole""",
r'''
import tracemalloc
class Plain:
    def __init__(self, x, y): self.x, self.y = x, y
class Slotted:
    __slots__ = ("x", "y")
    def __init__(self, x, y): self.x, self.y = x, y
for cls in (Plain, Slotted, tuple):
    tracemalloc.start()
    objs = [cls((i, i)) if cls is tuple else cls(i, i) for i in range(100_000)]
    print(f"{cls.__name__:8} {tracemalloc.get_traced_memory()[0] / 1e6:.1f} MB")
    tracemalloc.stop(); del objs
'''),

Q(13, "Difficult", "What are immortal objects (PEP 683)?",
"""Since Python 3.12, some objects (`None`, `True`, small ints, interned strings, and others) are **immortal**: their refcount is set to a special value and never changes. This avoids cache-line writes when many threads/processes touch them, helps copy-on-write after `fork`, and supports the free-threaded build.""",
r'''
import sys
print(sys.getrefcount(None) > 1_000_000_000, sys.getrefcount(42) > 1_000_000_000)
'''),

Q(13, "Difficult", "How can exceptions or closures keep large objects alive?",
"""An exception's `__traceback__` references frames, which reference all their local variables. Storing an exception (e.g. in a list of errors) keeps those locals alive. Python deletes the `as e` name at the end of the `except` block for this reason. Closures likewise keep captured variables alive.""",
r'''
import weakref
class BigData: pass
errors = []
def process():
    data = BigData(); process.ref = weakref.ref(data)
    try:
        raise ValueError("boom")
    except ValueError as e:
        errors.append(e)                  # keeps the frame and `data` alive
process()
print("BigData alive:", process.ref() is not None)
errors.clear()
print("after clearing errors:", process.ref() is not None)
'''),

Q(13, "Moderate", "What does `gc.disable()` do and when is it used?",
"""It turns off automatic cyclic collection (reference counting still runs). Some high-throughput services disable or tune it, or call `gc.freeze()` after startup (moving existing objects to a permanent generation) to reduce pauses and improve copy-on-write sharing in pre-fork servers. Instagram famously did this with Django."""),

Q(13, "Easy", "What is the difference between stack and heap in Python?",
"""All Python objects live on the heap. The C call stack holds interpreter frames' bookkeeping; Python frame objects and local variable references point into the heap. So "stack variables" in Python are just references to heap objects."""),

# =============== 14. CONCURRENCY: GIL, THREADS, PROCESSES & ASYNCIO ===============
Q(14, "Moderate", "What is the GIL (Global Interpreter Lock)?",
"""A mutex in CPython that lets only one thread execute Python bytecode at a time. It simplifies memory management (refcounts) and C extensions, but prevents CPU-bound Python threads from running in parallel. It's released during blocking I/O and by many C extensions (NumPy, hashlib, zlib), so I/O-bound threads still scale.""",
r'''
import sys
print("GIL enabled:", getattr(sys, "_is_gil_enabled", lambda: True)())
'''),

Q(14, "Moderate", "Threads vs processes vs asyncio: when do you use each?",
"""- **Threads** (`threading`, `ThreadPoolExecutor`): I/O-bound work with blocking libraries (HTTP calls, DB drivers, file I/O).
- **Processes** (`multiprocessing`, `ProcessPoolExecutor`): CPU-bound work in pure Python; each process has its own interpreter and GIL.
- **asyncio**: very many concurrent I/O operations (thousands of sockets) with async-aware libraries; single-threaded cooperative multitasking."""),

Q(14, "Moderate", "Show that threads don't speed up CPU-bound Python code but do help I/O-bound code.",
"""With the GIL, CPU-bound threads take turns, so total time stays about the same. I/O-bound threads overlap their waiting, so total time drops.""",
r'''
import time
from concurrent.futures import ThreadPoolExecutor
def cpu(n=2_000_000): return sum(i * i for i in range(n))
def io(_=None): time.sleep(0.2)
for name, fn in (("CPU-bound", cpu), ("I/O-bound", io)):
    t = time.perf_counter(); [fn() for _ in range(4)]; serial = time.perf_counter() - t
    t = time.perf_counter()
    with ThreadPoolExecutor(4) as ex: list(ex.map(lambda _: fn(), range(4)))
    threaded = time.perf_counter() - t
    print(f"{name}: serial {serial:.2f}s, 4 threads {threaded:.2f}s")
'''),

Q(14, "Moderate", "How do you use multiprocessing for CPU-bound work?",
"""`ProcessPoolExecutor` (or `multiprocessing.Pool`) runs functions in worker processes, each with its own GIL. Functions and arguments must be picklable, and the entry point must be guarded by `if __name__ == "__main__":` on spawn platforms (Windows, macOS).""",
r'''
import time
from concurrent.futures import ProcessPoolExecutor
def cpu(n): return sum(i * i for i in range(n))
if __name__ == "__main__":
    jobs = [3_000_000] * 4
    t = time.perf_counter(); [cpu(n) for n in jobs]; serial = time.perf_counter() - t
    t = time.perf_counter()
    with ProcessPoolExecutor(4) as ex: list(ex.map(cpu, jobs))
    print(f"serial {serial:.2f}s vs 4 processes {time.perf_counter() - t:.2f}s")
'''),

Q(14, "Moderate", "What is a race condition? Show one and fix it.",
"""When the result depends on thread timing. `counter += 1` is a read-modify-write, so threads can interleave and lose updates. Protect shared state with a `threading.Lock` (or avoid sharing: use queues, or per-thread results merged at the end).""",
r'''
import threading, time
counter = 0
lock = threading.Lock()
def unsafe():
    global counter
    for _ in range(1_000):
        tmp = counter          # read
        time.sleep(0)          # another thread runs here (as it can at any bytecode)
        counter = tmp + 1      # write back a stale value -> lost update
def safe():
    global counter
    for _ in range(1_000):
        with lock:
            tmp = counter; time.sleep(0); counter = tmp + 1
for fn in (unsafe, safe):
    counter = 0
    ts = [threading.Thread(target=fn) for _ in range(4)]
    for t in ts: t.start()
    for t in ts: t.join()
    print(f"{fn.__name__}: {counter} (expected 4000)")
'''),

Q(14, "Moderate", "What synchronization primitives does `threading` provide?",
"""- `Lock` / `RLock` (re-entrant by the same thread)
- `Semaphore` / `BoundedSemaphore` (limit concurrency, e.g. max 5 DB calls)
- `Event` (one thread signals others)
- `Condition` (wait for a state change)
- `Barrier` (N threads wait for each other)
- `queue.Queue` (thread-safe producer/consumer, usually the best choice)""",
r'''
import threading, time
limit = threading.Semaphore(2)
active, peak = 0, 0
guard = threading.Lock()
def call_api(i):
    global active, peak
    with limit:
        with guard: active += 1; peak = max(peak, active)
        time.sleep(0.02)
        with guard: active -= 1
ts = [threading.Thread(target=call_api, args=(i,)) for i in range(8)]
for t in ts: t.start()
for t in ts: t.join()
print("max concurrent calls:", peak)
'''),

Q(14, "Moderate", "How do you implement producer-consumer with threads?",
"""Use `queue.Queue`: producers `put()`, consumers `get()` and call `task_done()`; `join()` waits until all items are processed. A sentinel (`None`) per consumer tells workers to stop. `maxsize` provides back-pressure.""",
r'''
import queue, threading
q = queue.Queue(maxsize=5)
results = []
def consumer():
    while (item := q.get()) is not None:
        results.append(item * 2); q.task_done()
    q.task_done()
workers = [threading.Thread(target=consumer) for _ in range(3)]
for w in workers: w.start()
for i in range(10): q.put(i)
for _ in workers: q.put(None)
q.join()
print(sorted(results))
'''),

Q(14, "Moderate", "What is a deadlock and how do you avoid it?",
"""Two or more threads each hold a lock the other needs, waiting forever. Avoid by acquiring locks in a **consistent global order**, holding locks briefly, using timeouts (`lock.acquire(timeout=...)`), using a single lock, or preferring message passing (queues)."""),

Q(14, "Moderate", "What is asyncio and how does it work?",
"""asyncio runs coroutines on a single-threaded **event loop**. `async def` defines a coroutine; `await` suspends it until the awaited operation (I/O, sleep, another coroutine) completes, letting the loop run other tasks meanwhile. Concurrency comes from overlapping waits, not parallel CPU execution.""",
r'''
import asyncio, time
async def fetch(name, delay):
    await asyncio.sleep(delay)            # pretend network I/O
    return f"{name} done"
async def main():
    t = time.perf_counter()
    results = await asyncio.gather(fetch("users", 0.3), fetch("orders", 0.2), fetch("stock", 0.1))
    print(results, f"in {time.perf_counter() - t:.2f}s (not 0.6s)")
asyncio.run(main())
'''),

Q(14, "Moderate", "What is the difference between a coroutine, a Task and a Future?",
"""A **coroutine** is what `async def` returns when called; it does nothing until awaited or scheduled. A **Task** wraps a coroutine and schedules it on the event loop to run concurrently (`asyncio.create_task`). A **Future** is a low-level placeholder for a result that will be set later; `Task` is a subclass of `Future`.""",
r'''
import asyncio
async def work(): await asyncio.sleep(0.01); return 42
async def main():
    coro = work()
    print(type(coro).__name__)
    task = asyncio.create_task(coro)          # starts running soon
    print(type(task).__name__, isinstance(task, asyncio.Future), task.done())
    print(await task, task.done())
asyncio.run(main())
'''),

Q(14, "Difficult", "What happens if you call a blocking function inside async code?",
"""It blocks the whole event loop: no other coroutine runs until it returns. Use async libraries (httpx, aiohttp, asyncpg), or offload blocking calls with `await asyncio.to_thread(fn, ...)` (threads) or `loop.run_in_executor` (process pool for CPU-bound work).""",
r'''
import asyncio, time
async def heartbeat():
    for _ in range(3):
        print("  tick", round(time.perf_counter() - T0, 2)); await asyncio.sleep(0.1)
async def main(blocking):
    hb = asyncio.create_task(heartbeat())
    if blocking: time.sleep(0.3)                       # freezes the loop
    else: await asyncio.to_thread(time.sleep, 0.3)     # loop keeps running
    await hb
for blocking in (True, False):
    print("blocking" if blocking else "to_thread")
    T0 = time.perf_counter(); asyncio.run(main(blocking))
'''),

Q(14, "Moderate", "What is `asyncio.TaskGroup` (3.11+) and why is it better than `gather`?",
"""`TaskGroup` provides **structured concurrency**: tasks created in an `async with` block are awaited at the end, and if one fails, the others are cancelled and errors are raised together as an `ExceptionGroup`. `gather` by default lets the others keep running when one fails.""",
r'''
import asyncio
async def job(name, delay, fail=False):
    try:
        await asyncio.sleep(delay)
        if fail: raise ValueError(f"{name} failed")
        print("finished", name)
    except asyncio.CancelledError:
        print("cancelled", name); raise
async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(job("fast", 0.01))
            tg.create_task(job("broken", 0.02, fail=True))
            tg.create_task(job("slow", 1.0))
    except* ValueError as eg:
        print("errors:", [str(e) for e in eg.exceptions])
asyncio.run(main())
'''),

Q(14, "Moderate", "How do you add a timeout to an async operation?",
"""`async with asyncio.timeout(seconds):` (3.11+) or `await asyncio.wait_for(coro, seconds)`. On timeout the inner task is cancelled and `TimeoutError` is raised.""",
r'''
import asyncio
async def slow_service(): await asyncio.sleep(2); return "data"
async def main():
    try:
        async with asyncio.timeout(0.1):
            await slow_service()
    except TimeoutError:
        print("gave up after 100 ms")
asyncio.run(main())
'''),

Q(14, "Difficult", "How do you limit concurrency in asyncio (e.g. at most 5 requests at once)?",
"""Use an `asyncio.Semaphore`: each task does `async with sem:` around the I/O. Alternatively, a fixed number of worker tasks pulling from an `asyncio.Queue`.""",
r'''
import asyncio
async def fetch(i, sem, stats):
    async with sem:
        stats["now"] += 1; stats["peak"] = max(stats["peak"], stats["now"])
        await asyncio.sleep(0.02)
        stats["now"] -= 1
        return i
async def main():
    sem, stats = asyncio.Semaphore(5), {"now": 0, "peak": 0}
    res = await asyncio.gather(*(fetch(i, sem, stats) for i in range(50)))
    print(len(res), "requests, peak concurrency", stats["peak"])
asyncio.run(main())
'''),

Q(14, "Difficult", "Is `asyncio` code thread-safe?",
"""No. asyncio objects must be used from the thread running the loop. To schedule work on the loop from another thread use `asyncio.run_coroutine_threadsafe(coro, loop)` or `loop.call_soon_threadsafe(cb)`. Within one loop, there's no preemption between `await` points, so plain statements between awaits don't race."""),

Q(14, "Difficult", "What is free-threaded Python (PEP 703)?",
"""An optional CPython build without the GIL (`python3.13t`, officially supported from 3.14 under PEP 779), where threads run Python bytecode in parallel on multiple cores. It uses biased reference counting, per-object locks and immortal objects. C extensions must be updated to be thread-safe; single-threaded code is slightly slower. Check with `sys._is_gil_enabled()`."""),

Q(14, "Moderate", "What is `concurrent.futures` and why is it convenient?",
"""A high-level API with `ThreadPoolExecutor` and `ProcessPoolExecutor` sharing the same interface: `submit()` returns a `Future`, `map()` preserves order, and `as_completed()` yields futures as they finish. Switching threads for processes is a one-word change.""",
r'''
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
def download(name, secs): time.sleep(secs); return name
with ThreadPoolExecutor(max_workers=3) as ex:
    futures = [ex.submit(download, n, s) for n, s in [("big", 0.3), ("small", 0.1), ("mid", 0.2)]]
    print("completion order:", [f.result() for f in as_completed(futures)])
'''),

Q(14, "Difficult", "How do processes share data?",
"""They don't share memory by default. Options: pass data as (pickled) arguments and return values, `multiprocessing.Queue`/`Pipe`, `multiprocessing.shared_memory` or `Value`/`Array` for raw shared buffers, a `Manager` (proxy objects, slower), or external stores (Redis, DB, files). Minimize data transfer: pickling large objects is often the bottleneck.""",
r'''
from multiprocessing import Process, Queue
def worker(q, n): q.put((n, n * n))
if __name__ == "__main__":
    q = Queue()
    ps = [Process(target=worker, args=(q, i)) for i in range(4)]
    for p in ps: p.start()
    results = sorted(q.get() for _ in ps)
    for p in ps: p.join()
    print(results)
'''),

Q(14, "Difficult", "What is the difference between `fork`, `spawn` and `forkserver` start methods?",
"""`fork` copies the parent process (fast, inherits memory via copy-on-write, but unsafe with threads). `spawn` starts a fresh interpreter and re-imports the main module (safe, slower; default on Windows and macOS). `forkserver` forks from a clean server process. Python 3.14 changed the Linux default from `fork` to `forkserver`.""",
r'''
import multiprocessing as mp
print("default start method here:", mp.get_start_method(), "| available:", mp.get_all_start_methods())
'''),

Q(14, "Moderate", "What are daemon threads?",
"""Threads with `daemon=True` don't prevent the program from exiting; they're killed abruptly at interpreter shutdown (no `finally`, no flush). Use them for background helpers that can be dropped, never for work that must complete."""),

Q(14, "Difficult", "Explain `async`/`await` under the hood.",
"""Coroutines are built on generators: `await` delegates to an awaitable (like `yield from`) until it yields a Future to the event loop. The loop registers the Future's I/O with the OS selector (epoll/kqueue/IOCP), runs other ready callbacks, and resumes the coroutine by calling `send()` when the Future completes."""),

Q(14, "Moderate", "How do you run periodic or scheduled background work in Python services?",
"""Within a process: an asyncio task with `while True: ...; await asyncio.sleep(interval)`, or `threading.Timer`/`sched`. Across a deployment: Celery beat, APScheduler, cron/Kubernetes CronJobs, or cloud schedulers, so jobs survive restarts and don't run twice across replicas."""),

]
