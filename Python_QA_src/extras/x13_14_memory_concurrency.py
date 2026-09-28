EXTRAS = [

X(0, "How does Python manage memory", terms=[
    ("Private heap", "Memory managed by the interpreter; Python code never allocates or frees it directly."),
    ("pymalloc", "CPython's allocator for small objects (up to 512 bytes); larger requests go to the system allocator."),
], pitfall="""Assuming memory use drops when a big structure is released. The process's resident size may stay high because freed memory is kept for reuse or is fragmented.""",
follow=[
    ("How do you see live allocations?", "`tracemalloc.start()` then `tracemalloc.take_snapshot().statistics(\"lineno\")`."),
    ("Does PyPy use reference counting?", "No; it uses a tracing (moving, generational) GC, so objects are not freed immediately."),
]),

X(1, "What is reference counting", terms=[
    ("`sys.getrefcount`", "Returns an object's reference count (one higher than expected, because the argument itself is a reference)."),
    ("Reference cycle", "Objects that refer to each other, so their counts never reach zero on their own."),
], pitfall="""Relying on immediate finalization (e.g. files being closed as soon as a function returns) in code that may run on PyPy or in free-threaded builds with deferred reference counting. Use `with` for deterministic cleanup.""",
follow=[
    ("Why is reference counting a problem for free threading?", "Every refcount change would need atomic operations; free-threaded CPython uses biased and deferred reference counting to reduce that cost."),
    ("What are the advantages of refcounting?", "Deterministic, immediate freeing and low pause times."),
]),

X(2, "How does the cyclic garbage collector work", terms=[
    ("Generations", "Objects surviving collections are promoted to older generations that are scanned less often."),
    ("Unreachable set", "Objects whose references come only from within the scanned group, found by subtracting internal references."),
], pitfall="""Creating cycles in hot code (for example parent/child links, or a closure referencing its own object). Collection is delayed and adds pauses; break cycles with `weakref`.""",
follow=[
    ("What are the default thresholds?", "`gc.get_threshold()`; recent versions return `(2000, 10, 10)`: a young collection after about 2000 net new container allocations, older generations far less often."),
    ("How do you inspect GC activity?", "`gc.get_count()`, `gc.get_stats()`, and `gc.callbacks` for timing each collection."),
]),

X(3, "What is `weakref` and when", terms=[
    ("`WeakValueDictionary`", "Entries disappear when the value object is garbage-collected."),
    ("`WeakKeyDictionary`", "Entries disappear when the key object is collected; useful for per-object metadata."),
], pitfall="""Creating a weak reference to a temporary object (`weakref.ref(Foo())`). The object dies immediately and the ref returns `None`.""",
follow=[
    ("Which objects cannot be weakly referenced?", "Built-ins like `int`, `str`, `tuple`, `list` and `dict` (subclasses of list and dict can), and classes with `__slots__` lacking `__weakref__`."),
    ("How do you weakly reference a bound method?", "`weakref.WeakMethod(obj.method)`."),
]),

X(4, "What causes memory leaks in Python", terms=[
    ("Leak (in Python)", "Memory kept alive by unintended references, not memory lost by the allocator."),
    ("Heap snapshot diff", "Comparing two `tracemalloc` snapshots to find where growth happens."),
], pitfall="""Unbounded module-level caches keyed by request data (user ids, URLs). They grow for the life of the process; bound them with `lru_cache(maxsize=...)` or a TTL cache.""",
follow=[
    ("Which tools help beyond tracemalloc?", "`objgraph` for reference graphs, `memray` for native and Python allocations, `guppy3`/`pympler` for heap summaries."),
    ("How do C extensions leak?", "Missing `Py_DECREF` calls or native allocations never freed; `memray` with native tracking shows them."),
]),

X(5, "What does `sys.getsizeof` measure", terms=[
    ("Shallow size", "The object's own memory, excluding referenced objects."),
    ("Deep size", "Total memory reachable from an object, computed by walking references."),
], pitfall="""Summing `getsizeof` over a nested structure without tracking identity. Shared objects (like small ints and interned strings) are counted many times.""",
follow=[
    ("How do you compute an approximate deep size?", "Walk `gc.get_referents()` recursively with a set of visited `id`s, or use `pympler.asizeof`."),
    ("Does `getsizeof` include GC overhead?", "Yes, it includes the GC header for objects tracked by the collector."),
]),

X(6, "Does `del` free memory", terms=[
    ("Free list", "Per-type cache of freed objects reused for new objects of the same type."),
], pitfall="""Calling `gc.collect()` after `del` to \"free memory\" when there are no cycles. Reference counting already freed the objects; the RSS stays high for allocator reasons.""",
follow=[
    ("How do you truly release memory after a big job?", "Run the job in a subprocess that exits, which returns all its memory to the OS."),
    ("Does `del` on a NumPy array free its buffer?", "Yes, when its refcount reaches zero and no views still reference it."),
]),

X(7, "What is pymalloc", terms=[
    ("Arena", "256 KiB region (1 MiB on 64-bit since 3.10) obtained from the OS."),
    ("Pool", "Arena subdivision serving blocks of one size class."),
], pitfall="""Diagnosing a \"leak\" from RSS alone. A few live objects in each arena keep them all allocated; use `tracemalloc` to see whether Python objects are actually growing.""",
follow=[
    ("How do you disable pymalloc for debugging?", "`PYTHONMALLOC=malloc`, which lets tools like Valgrind or ASan see every allocation."),
    ("Can a different system allocator help?", "Sometimes; jemalloc or mimalloc (used by free-threaded builds) can reduce fragmentation."),
]),

X(8, "How can you reduce memory usage for many objects", terms=[
    ("Columnar layout", "Storing each field in its own array instead of one object per record."),
], pitfall="""Optimizing object layout before measuring. Check with `tracemalloc` which structures dominate; often a single cache or buffer is the real problem.""",
follow=[
    ("How much does `__slots__` save?", "Typically 40-60% per small instance, because there is no per-instance dict."),
    ("When should you move to pandas, polars or NumPy?", "When you hold millions of homogeneous records and process them in bulk."),
]),

X(9, "What are immortal objects", terms=[
    ("Immortal object", "An object whose refcount is fixed and never reaches zero, so it is never freed."),
], pitfall="""Using `sys.getrefcount(None)` in tests or monitoring. Since 3.12 it returns a huge constant, not a real count.""",
follow=[
    ("Why were immortal objects introduced?", "To avoid cache-line contention on shared objects' refcounts, and to enable sharing between subinterpreters and free threading."),
    ("Can user objects become immortal?", "Not through a public API; interned strings and some static objects are made immortal by the runtime."),
]),

X(10, "How can exceptions or closures keep large objects alive", terms=[
    ("Frame locals", "Every frame in a traceback keeps its local variables reachable."),
], pitfall="""Storing caught exceptions in a list for later reporting. Each traceback keeps its frames and their locals alive; store `traceback.format_exception(e)` strings instead, or clear with `e.__traceback__ = None`.""",
follow=[
    ("Why does Python delete `e` at the end of an `except` block?", "To break the cycle frame → traceback → frame that would otherwise keep everything alive until the GC runs."),
    ("How can a lambda keep an object alive?", "It closes over variables; if one of them references a large object, the object lives as long as the lambda."),
]),

X(11, "What does `gc.disable()` do", terms=[
    ("`gc.freeze()`", "Moves all current objects to a permanent generation that is never scanned; helpful before forking workers."),
], pitfall="""Disabling the GC in a long-running process that creates cycles. Cyclic garbage then accumulates without limit.""",
follow=[
    ("Why did Instagram disable or freeze the GC?", "GC touching objects' headers caused copy-on-write page copies in forked workers, increasing memory; `gc.freeze()` was added for this."),
    ("How do you tune rather than disable?", "`gc.set_threshold(...)` to collect less often."),
]),

X(12, "What is the difference between stack and heap in Python", terms=[
    ("Frame object", "Holds a function's locals, value stack and current instruction."),
], pitfall="""Assuming that local variables are cheap \"stack\" values as in C. Every value is a heap object, and locals are just references to them.""",
follow=[
    ("Where are frames stored since 3.11?", "In a contiguous per-thread interpreter stack; full frame objects are created lazily only when needed (tracebacks, `sys._getframe`)."),
    ("What causes `RecursionError` versus a real stack overflow?", "`RecursionError` comes from the Python-level limit; very deep C recursion can still overflow the C stack and crash."),
]),

X(13, "What is the GIL", terms=[
    ("Switch interval", "How often a thread is asked to drop the GIL: `sys.getswitchinterval()`, 5 ms by default."),
], pitfall="""Believing the GIL makes your code thread-safe. It protects the interpreter's internals, not your invariants; `x += 1` and check-then-act sequences still race.""",
follow=[
    ("Which operations release the GIL?", "Blocking I/O, `time.sleep`, and many C extensions (NumPy, zlib, hashlib) during heavy computation."),
    ("Does every Python implementation have a GIL?", "CPython and PyPy have one; Jython and IronPython do not; free-threaded CPython builds remove it."),
]),

X(14, "Threads vs processes vs asyncio", terms=[
    ("I/O-bound", "Waiting on network, disk or other processes dominates."),
    ("CPU-bound", "Computation dominates."),
], pitfall="""Choosing asyncio for a codebase full of blocking libraries (requests, sync DB drivers). Every blocking call freezes the loop; threads may be the better fit.""",
follow=[
    ("How do you mix them?", "Run blocking code from asyncio with `asyncio.to_thread` or `loop.run_in_executor`, and CPU work in a `ProcessPoolExecutor`."),
    ("How do subinterpreters fit in (3.14)?", "`concurrent.interpreters` and `InterpreterPoolExecutor` give per-interpreter GILs: parallelism within one process with isolated state."),
]),

X(15, "Show that threads don't speed up CPU-bound", terms=[
    ("Contention", "Threads waiting for the same lock (here the GIL)."),
], pitfall="""Benchmarking with too little work or with `time.sleep` as \"work\". Sleep releases the GIL and makes CPU-bound threading look faster than it is.""",
follow=[
    ("Would the CPU-bound example scale on a free-threaded build?", "Yes, it can scale close to linearly with cores, if threads do not contend on shared objects."),
    ("How do you measure fairly?", "Use `perf_counter`, repeat runs, and make sure each thread does the same total work."),
]),

X(16, "How do you use multiprocessing for CPU-bound work", terms=[
    ("Pickling", "Serialization used to send functions, arguments and results between processes."),
    ("`chunksize`", "Number of items sent to a worker per task in `map`; larger chunks reduce overhead."),
], pitfall="""Sending large data to workers for small computations. Pickling and copying cost more than the computation; pass file paths or use shared memory.""",
follow=[
    ("Why can't you pass a lambda to a process pool?", "Lambdas cannot be pickled by reference; use module-level functions."),
    ("How many workers should you use?", "Usually `os.process_cpu_count()` (3.13+) or `os.cpu_count()` for CPU-bound work."),
]),

X(17, "What is a race condition", terms=[
    ("Critical section", "Code that must not run in more than one thread at a time."),
    ("Atomic operation", "An operation that completes without being interrupted."),
], pitfall="""Fixing a race by making operations \"look\" atomic (single bytecode). CPython gives no such guarantee across versions or builds; use locks or queues.""",
follow=[
    ("Is `list.append` thread-safe?", "In CPython a single `append` is atomic, but sequences like check-then-append are not."),
    ("How do tests find races?", "Stress tests with many threads, `sys.setswitchinterval` set very low, and ThreadSanitizer for C extensions."),
]),

X(18, "What synchronization primitives does `threading` provide", terms=[
    ("`Condition`", "Lets threads wait until notified, used with a lock."),
    ("`Barrier`", "Blocks until a fixed number of threads arrive."),
], pitfall="""Using `Event.wait()` or `Condition.wait()` without a timeout in shutdown paths. A missed notification then hangs the program forever.""",
follow=[
    ("What is the difference between `Lock` and `RLock`?", "An `RLock` can be acquired again by the thread holding it; a `Lock` would deadlock."),
    ("Why use `BoundedSemaphore`?", "It raises `ValueError` if released more times than acquired, catching bugs."),
]),

X(19, "How do you implement producer-consumer with threads", terms=[
    ("Backpressure", "Slowing producers when consumers fall behind, e.g. with `Queue(maxsize=N)`."),
    ("Poison pill", "A sentinel item telling consumers to stop."),
], pitfall="""Forgetting `task_done()` after `get()`. `queue.join()` then waits forever.""",
follow=[
    ("How do you stop consumers cleanly?", "Put one sentinel per consumer, or call `Queue.shutdown()` (3.13+)."),
    ("What is `SimpleQueue`?", "An unbounded FIFO without `task_done`/`join`, slightly faster."),
]),

X(20, "What is a deadlock and how do you avoid it", terms=[
    ("Lock ordering", "Always acquiring multiple locks in one global order."),
], pitfall="""Calling user callbacks or logging handlers while holding a lock. If the callback takes the same or another lock, you get deadlocks that only happen under load.""",
follow=[
    ("How do you debug a hung Python process?", "`py-spy dump --pid N` or `faulthandler.dump_traceback_later` show every thread's stack."),
    ("How do timeouts help?", "`lock.acquire(timeout=...)` lets you detect and report a probable deadlock instead of hanging."),
]),

X(21, "What is asyncio and how does it work", terms=[
    ("Event loop", "Runs ready callbacks and coroutines, and waits on I/O readiness when nothing is ready."),
    ("Awaitable", "A coroutine, Task or Future, or any object with `__await__`."),
], pitfall="""Calling an `async def` function without `await`. You get a coroutine object that never runs, plus a \"coroutine was never awaited\" warning.""",
follow=[
    ("What does `asyncio.run` do?", "Creates a new event loop, runs the coroutine to completion, then cancels leftover tasks and closes the loop."),
    ("What is uvloop?", "A fast drop-in event loop built on libuv."),
]),

X(22, "What is the difference between a coroutine, a Task", terms=[
    ("Task", "A Future that drives a coroutine on the event loop."),
    ("Future", "A low-level placeholder for a result that will be set later."),
], pitfall="""Creating a task with `asyncio.create_task` and not keeping a reference. The loop only keeps a weak reference, so the task can be garbage-collected mid-execution.""",
follow=[
    ("How do you cancel a task?", "`task.cancel()`; the coroutine receives `CancelledError` at its current `await`."),
    ("When does a coroutine start running?", "When it is awaited or wrapped in a Task; `create_task` schedules it for the next loop iteration."),
]),

X(23, "What happens if you call a blocking function inside async code", terms=[
    ("`asyncio.to_thread`", "Runs a blocking function in the default thread pool and awaits the result."),
], pitfall="""Using `time.sleep` in a coroutine. It blocks the whole loop; use `await asyncio.sleep`.""",
follow=[
    ("How do you detect blocking calls?", "Run with `PYTHONASYNCIODEBUG=1` or `asyncio.run(main(), debug=True)`, which logs slow callbacks (over 100 ms)."),
    ("Is CPU-heavy work in a coroutine also blocking?", "Yes; any long computation between awaits blocks the loop."),
]),

X(24, "What is `asyncio.TaskGroup`", terms=[
    ("Structured concurrency", "Tasks cannot outlive the block that created them."),
], pitfall="""Expecting `TaskGroup` to let other tasks finish after one fails. It cancels the remaining tasks and raises an `ExceptionGroup`.""",
follow=[
    ("How does `gather(return_exceptions=True)` differ?", "It collects exceptions as results and does not cancel siblings."),
    ("How do you handle errors from a TaskGroup?", "`except* SomeError` around the `async with` block."),
]),

X(25, "How do you add a timeout to an async operation", terms=[
    ("Cancellation", "Raising `CancelledError` inside a task at its current `await`."),
], pitfall="""Catching `CancelledError` (or broad `BaseException`) and not re-raising it. Timeouts and shutdown then stop working; clean up and re-raise.""",
follow=[
    ("What exception does a timeout raise?", "`TimeoutError` (the built-in, since 3.11)."),
    ("Can you change a deadline mid-flight?", "Yes, `asyncio.timeout()` returns an object with `reschedule()`."),
]),

X(26, "How do you limit concurrency in asyncio", terms=[
    ("Semaphore", "A counter-based lock allowing up to N holders at once."),
], pitfall="""Creating all tasks at once for a million URLs and using a semaphore only around the request. All the task objects still exist in memory; use a bounded worker pool fed from a queue.""",
follow=[
    ("How do you rate-limit (requests per second) rather than concurrency?", "A token bucket or `aiolimiter`; a semaphore only caps simultaneous requests."),
    ("How do you limit per host?", "One semaphore per host in a dict, or the HTTP client's connection-pool limits."),
]),

X(27, "Is `asyncio` code thread-safe", terms=[
    ("`call_soon_threadsafe`", "Schedules a callback on the loop from another thread, waking it up."),
], pitfall="""Calling `loop.call_soon` or setting a Future's result from another thread. It may never wake the loop or corrupt state; use the `_threadsafe` variants.""",
follow=[
    ("How do you get a result back from `run_coroutine_threadsafe`?", "It returns a `concurrent.futures.Future`; call `.result(timeout)` in the calling thread."),
    ("Can you run several event loops?", "Yes, one per thread."),
]),

X(28, "What is free-threaded Python", terms=[
    ("Free-threaded build", "CPython compiled with `--disable-gil`; its executable is usually named `python3.14t`."),
    ("`sys._is_gil_enabled()`", "Reports whether the GIL is active at runtime."),
], pitfall="""Assuming every package works without the GIL. C extensions must declare support; importing one that does not re-enables the GIL (with a warning) unless `PYTHON_GIL=0` is forced.""",
follow=[
    ("What is the single-threaded cost?", "Roughly 5-10% slower in 3.14, down from larger overheads in 3.13."),
    ("Does free threading remove the need for locks?", "No; it makes races more likely to show up, so shared mutable state needs locks."),
]),

X(29, "What is `concurrent.futures`", terms=[
    ("`as_completed`", "Yields futures as they finish, regardless of submission order."),
    ("`Executor.map`", "Like built-in `map` but parallel; results come back in input order."),
], pitfall="""Not calling `future.result()`. Exceptions raised in workers are stored in the future and never shown.""",
follow=[
    ("How do you cancel pending work at shutdown?", "`executor.shutdown(cancel_futures=True)` (3.9+)."),
    ("What does `Executor.map` do with exceptions?", "Raises the first exception when iteration reaches that result."),
]),

X(30, "How do processes share data", terms=[
    ("`shared_memory`", "Named shared memory blocks (`multiprocessing.shared_memory`) usable with NumPy without copying."),
    ("`Manager`", "Server process holding shared Python objects, accessed through proxies."),
], pitfall="""Forgetting to `close()` and `unlink()` shared memory blocks. They can outlive the processes and leak system memory.""",
follow=[
    ("Why is a `Manager` slow?", "Every operation is an IPC round trip to the manager process."),
    ("How do you share a large read-only dataset?", "Load it before forking (copy-on-write), or memory-map a file."),
]),

X(31, "What is the difference between `fork`, `spawn`", terms=[
    ("Copy-on-write", "Pages are shared after fork until one side writes to them."),
], pitfall="""Relying on the `fork` default on Linux. Python 3.14 changed the default start method on Linux to `forkserver`, so code depending on inherited globals breaks.""",
follow=[
    ("Why is fork unsafe with threads?", "Only the calling thread is copied; locks held by other threads stay locked forever in the child."),
    ("How do you choose a method explicitly?", "`multiprocessing.get_context(\"spawn\")` and create pools from that context."),
]),

X(32, "What are daemon threads", terms=[
    ("Daemon thread", "A thread that does not keep the process alive."),
], pitfall="""Doing writes (files, databases) in daemon threads. At exit they are stopped mid-operation, which can corrupt data.""",
follow=[
    ("How do you shut down non-daemon workers cleanly?", "Signal them with an `Event` or sentinel and `join()` them."),
    ("Are daemon threads allowed in subinterpreters?", "Not by default; isolated subinterpreters disallow them."),
]),

X(33, "Explain `async`/`await` under the hood", terms=[
    ("`__await__`", "Returns an iterator; awaiting an object delegates to it like `yield from`."),
    ("Selector", "The OS mechanism (epoll, kqueue, IOCP) the loop uses to wait for I/O readiness."),
], pitfall="""Thinking `await` itself creates concurrency. Awaiting coroutines one by one runs them sequentially; use tasks, `gather` or `TaskGroup` to overlap them.""",
follow=[
    ("What does a bare `yield` inside `__await__` communicate?", "It yields a Future (or `None`) up to the Task, which suspends until the Future completes."),
    ("How do you write an awaitable class?", "Define `__await__` returning an iterator, often `return some_coroutine().__await__()`."),
]),

X(34, "How do you run periodic or scheduled background work", terms=[
    ("Drift", "Accumulated lateness when the next run is scheduled relative to the end of the previous one."),
], pitfall="""Running scheduled jobs inside every web worker process. With N workers the job runs N times; use a single scheduler (cron, Celery beat, APScheduler with a job store).""",
follow=[
    ("How do you avoid drift?", "Compute the next deadline from a fixed start time with `time.monotonic()`, not `sleep(interval)` after the work."),
    ("What is a common distributed option?", "Celery beat, or cloud schedulers triggering tasks or HTTP endpoints."),
]),
]
