MODULE = dict(id=3, title="Concurrency Architecture",
              desc="Choosing and combining asyncio, threads and processes for real systems: orchestration of many devices, cancellation, backpressure, deadlock diagnosis and rate-limited I/O.")

QUESTIONS = [

P("Design", "Design the concurrency model for an orchestrator that runs tests on 64 SSDs at once. Each test mostly waits on CLI tools and serial consoles, then verifies data (CPU heavy).",
short="""Use **asyncio** as the orchestrator: one task per device, `asyncio.create_subprocess_exec` for CLI tools, stream readers for consoles, a semaphore for shared resources and `asyncio.timeout` on every step. Push the CPU-heavy verification to a `ProcessPoolExecutor` via `loop.run_in_executor` so it doesn't block the event loop. Wrap each device in its own error boundary so one bad drive can't take down the run.""",
deep="""Clarify: How long do tests run (minutes or days)? Do devices share hosts, power supplies or buses? Must results stream to a database live?

**Why asyncio for orchestration**: 64 devices x several concurrent waits (CLI, console, power relay) is hundreds of mostly idle operations. Coroutines are cheap, cancellation and timeouts are first-class, and there's one thread to reason about.

**Structure:**

- `asyncio.TaskGroup` (or a supervisor that collects results) with one `run_device(dev)` task per device. Use a per-device try/except so one failure is recorded, not propagated to all.
- Subprocesses: `create_subprocess_exec` (never shell), read stdout/stderr concurrently, kill on timeout.
- Shared resources (a power controller that accepts one command at a time, a lab network with bandwidth limits): `asyncio.Semaphore` / `Lock`.
- CPU work (CRC checks on gigabytes): `await loop.run_in_executor(process_pool, verify, path)`. Pass file paths, not data.
- Blocking libraries without async support (vendor SDKs): `asyncio.to_thread`.
- Observability: per-device structured logs with a device ID in `contextvars`, heartbeat metrics, and a watchdog task that flags devices with no progress.

**Alternatives**: a thread per device works for smaller counts and blocking SDKs, but timeouts and cancellation are harder. A process per device gives strong isolation (useful if drivers can crash the interpreter) at higher memory cost.""",
code=r'''
import asyncio, sys, time

CLI = [sys.executable, "-c", "import sys, time, random; random.seed(int(sys.argv[1])); time.sleep(random.uniform(0.05, 0.3)); print('{\"temp_c\": %d}' % (35 + int(sys.argv[1]) % 20))"]

async def run_cli(dev_id, timeout):
    proc = await asyncio.create_subprocess_exec(*CLI, str(dev_id), stdout=asyncio.subprocess.PIPE)
    try:
        async with asyncio.timeout(timeout):
            out, _ = await proc.communicate()
        return out.decode().strip()
    except TimeoutError:
        proc.kill(); await proc.wait()
        raise

def verify(dev_id):                      # CPU-heavy step: runs in a process pool in the real design
    return sum(i * dev_id for i in range(200_000)) % 97

async def run_device(dev_id, power_lock, pool):
    try:
        async with power_lock:           # shared power controller: one command at a time
            await asyncio.sleep(0.005)
        health = await run_cli(dev_id, timeout=0.25)
        crc = await asyncio.get_running_loop().run_in_executor(pool, verify, dev_id)
        return dev_id, "PASS", health, crc
    except TimeoutError:
        return dev_id, "TIMEOUT", None, None

async def main():
    from concurrent.futures import ThreadPoolExecutor   # ProcessPoolExecutor in production
    power_lock = asyncio.Lock()
    t = time.perf_counter()
    with ThreadPoolExecutor(4) as pool:
        results = await asyncio.gather(*(run_device(d, power_lock, pool) for d in range(16)))
    passed = sum(r[1] == "PASS" for r in results)
    print(f"{len(results)} devices in {time.perf_counter() - t:.2f}s: {passed} PASS, {len(results) - passed} TIMEOUT")
    print("sample:", results[:2])

asyncio.run(main())
''',
follow=(
"One vendor SDK is blocking and not thread-safe. How do you integrate it? => Give it a dedicated single-thread executor (`ThreadPoolExecutor(max_workers=1)`) and call it with `run_in_executor`, so calls are serialized but the loop stays responsive; or isolate it in a helper process.",
"How do you stop a hung device test without killing the whole run? => Per-device timeouts with cancellation, kill the child process group, mark the device TIMEOUT, collect logs, and optionally power-cycle it via the relay before continuing.",
"How do you know the orchestrator itself is healthy during a 48-hour run? => A heartbeat task updating a metric/file every N seconds, per-device last-progress timestamps, and an external watchdog alert when heartbeats stop.",
),
pitfall="Running the CPU-bound verification directly inside a coroutine. It blocks the event loop, so console readers miss data and every timeout fires late.",
signals="You pick asyncio for orchestration and explain why, isolate CPU and blocking work in executors, add per-device error boundaries, timeouts and shared-resource limits, and cover observability.",
),

P("Concept", "How does cancellation work in asyncio, and what are the rules for writing cancellation-safe code?",
short="""`task.cancel()` raises `CancelledError` inside the task at its current `await`. Since 3.8 it subclasses `BaseException`, so `except Exception` doesn't swallow it. Rules: clean up in `finally` or `async with`, re-raise `CancelledError` if you catch it, don't `await` long operations during cleanup without a timeout, and use `asyncio.shield` only for work that must finish (like committing a result).""",
deep="""Cancellation is **cooperative**: a task is only interrupted at `await` points. CPU loops without awaits can't be cancelled.

Sources of cancellation: explicit `task.cancel()`, `asyncio.timeout()`/`wait_for`, a failing sibling in a `TaskGroup`, and `asyncio.run` shutting down.

Rules:

- Put cleanup in `finally` / context managers so it runs on cancel.
- If you catch `CancelledError` (for logging), **re-raise** it. Swallowing it makes timeouts and TaskGroups hang or misbehave. (3.11 added `Task.uncancel()` for the rare cases where a library must suppress it deliberately.)
- `asyncio.shield(coro)` protects an inner operation from the outer cancellation, but the outer `await` still raises; use it for short, must-complete work like writing a final result.
- Beware of cleanup that itself awaits a hung resource; wrap it in a timeout.
- Blocking calls in threads (`to_thread`) cannot be interrupted; cancellation abandons the await, but the thread keeps running.""",
code=r'''
import asyncio

async def save_result(name):
    await asyncio.sleep(0.05)
    print(f"  result for {name} committed")

async def device_test(name):
    try:
        print(f"  {name}: running")
        await asyncio.sleep(10)                  # long I/O wait
    except asyncio.CancelledError:
        print(f"  {name}: cancelled, cleaning up")
        await asyncio.shield(save_result(name))  # must-complete step
        raise                                    # ALWAYS re-raise
    finally:
        print(f"  {name}: finally ran")

async def main():
    try:
        async with asyncio.timeout(0.1):
            await device_test("nvme3")
    except TimeoutError:
        print("timeout surfaced to caller as TimeoutError")
    print("CancelledError is an Exception subclass?", issubclass(asyncio.CancelledError, Exception))

asyncio.run(main())
''',
follow=(
"Why did Python 3.8 move `CancelledError` under `BaseException`? => Because code with `except Exception:` (logging and retry wrappers) was accidentally swallowing cancellations, breaking timeouts and shutdown.",
"A task doing `while True: compute()` ignores cancel. Why, and how do you fix it? => There's no `await` to deliver the exception. Add `await asyncio.sleep(0)` periodically, or better, move the CPU work to an executor.",
),
pitfall="`except Exception: pass` style wrappers written before 3.8 still exist in libraries; and `except BaseException` or bare `except:` in your own retry helpers will swallow cancellation.",
signals="You state cooperative semantics, the BaseException change, the re-raise rule, correct use of shield, and the limitation with threads.",
),

P("Design", "A producer generates work faster than consumers can process it. How do you design backpressure in Python?",
short="""Bound every queue. With `asyncio.Queue(maxsize=N)` or `queue.Queue(maxsize=N)`, `put()` blocks when full, which naturally slows the producer to the consumers' speed. Decide the overflow policy explicitly (block, drop oldest, drop newest, reject with an error or 429), size N from latency targets, and expose queue depth as a metric.""",
deep="""Unbounded queues turn a throughput problem into a memory and latency problem: the queue grows until the process dies, and every item waits longer.

Options:

- **Block** the producer (default for bounded queues). Correct when the producer can slow down (a log reader, a crawler).
- **Shed load**: when full, drop or reject new work (`put_nowait` + `QueueFull`), returning 429 or recording a skip. Correct for live telemetry where old data is worthless.
- **Drop oldest**: `collections.deque(maxlen=N)` as a ring buffer for "latest N samples".
- **Scale consumers** dynamically based on queue depth, within limits of downstream capacity.

Sizing: queue length ~ (acceptable delay) x (consumer throughput). Monitor depth and wait time; alert on sustained saturation. Propagate backpressure end to end: a bounded queue in front of a database writer is useless if an unbounded one sits upstream.""",
code=r'''
import asyncio, time

async def producer(q, n, stats):
    for i in range(n):
        t = time.perf_counter()
        await q.put(i)                               # blocks while the queue is full
        stats["blocked"] += time.perf_counter() - t
    for _ in range(2): await q.put(None)

async def consumer(q, name, done):
    while (item := await q.get()) is not None:
        await asyncio.sleep(0.01)                     # slow downstream, e.g. DB insert
        done.append(item)

async def main():
    stats, done = {"blocked": 0.0}, []
    q = asyncio.Queue(maxsize=5)
    t = time.perf_counter()
    await asyncio.gather(producer(q, 60, stats), consumer(q, "c1", done), consumer(q, "c2", done))
    print(f"processed {len(done)} items in {time.perf_counter() - t:.2f}s")
    print(f"producer spent {stats['blocked']:.2f}s waiting: that is backpressure working")
    print(f"max memory held: {q.maxsize} queued items, not 60")

asyncio.run(main())
''',
follow=(
"What do you do if the producer can't be slowed down (for example, telemetry arriving from hardware)? => Shed load deliberately: sample, aggregate at the source, or drop oldest from a ring buffer, and count what was dropped so it's visible.",
"How do you pick `maxsize`? => From the latency budget: if consumers process 200 items/s and 2 seconds of queueing is acceptable, about 400. Then validate with load tests and watch queue-depth metrics.",
),
pitfall="Using `asyncio.Queue()` or `queue.Queue()` without `maxsize` (the default is unbounded) in any pipeline that reads from a faster source.",
signals="You bound queues, choose an explicit overflow policy for the use case, size from latency, and make depth observable.",
),

P("Debug", "A threaded test harness hangs randomly once a night. How do you diagnose and prevent deadlocks?",
short="""Capture every thread's stack while it's hung: `py-spy dump --pid`, `faulthandler.dump_traceback_later(timeout)` or `sys._current_frames()`. Look for threads waiting on locks acquired in different orders, or waiting on a queue/event that nobody will set. Prevent with a global lock order, lock timeouts that log and fail loudly, smaller critical sections, and message passing instead of shared locks.""",
deep="""Diagnosis steps:

1. **Get stacks without stopping the process**: `py-spy dump --pid <pid>` (works on hung processes, shows all threads). In-process: `faulthandler.dump_traceback_later(3600, exit=False)` as a watchdog, or an admin signal/endpoint that prints `sys._current_frames()`.
2. **Match the signature** (see the list below).
3. **Reproduce**: stress the suspected section with many threads and `sys.setswitchinterval(1e-6)` to force interleavings.

Classic hang signatures:

- Two threads each in `lock.acquire()` for a lock the other holds: lock-order inversion.
- A thread in `queue.get()` with no producers left: a lost sentinel or a crashed producer.
- `thread.join()` on a thread that waits for the joiner: circular wait.
- Holding a lock while calling out (callbacks, logging handlers, I/O) that re-enters the same code.

Prevention: define lock hierarchy (always acquire `device_lock` before `results_lock`), use `lock.acquire(timeout=...)` with an error that includes the owner, avoid calling unknown code while holding a lock, prefer `queue.Queue` ownership handoff, and add a watchdog that dumps stacks when progress stops.""",
code=r'''
import sys, threading, time, traceback

device_lock, results_lock = threading.Lock(), threading.Lock()

def run_test():                                  # acquires device -> results
    with device_lock:
        time.sleep(0.05)
        if results_lock.acquire(timeout=0.5): results_lock.release()
        else: print("run_test: gave up waiting for results_lock")

def flush_results():                              # acquires results -> device (inverted order!)
    with results_lock:
        time.sleep(0.05)
        if device_lock.acquire(timeout=0.5): device_lock.release()
        else: print("flush_results: gave up waiting for device_lock")

threads = [threading.Thread(target=run_test, name="runner"), threading.Thread(target=flush_results, name="flusher")]
for t in threads: t.start()
time.sleep(0.2)                                   # both are now stuck: dump their stacks
names = {t.ident: t.name for t in threads}
for tid, frame in sys._current_frames().items():
    if tid in names:
        where = traceback.extract_stack(frame)[-1]      # innermost Python frame
        print(f"[{names[tid]}] waiting at line {where.lineno}: {where.line}")
for t in threads: t.join()
''',
follow=(
"How do you add a permanent safety net in CI? => `faulthandler.dump_traceback_later(timeout, repeat=False)` per test (pytest-timeout does this with its `thread` method) so a hang produces stack traces and fails instead of blocking the pipeline for hours.",
"What does `RLock` fix and what doesn't it fix? => It lets the same thread re-acquire a lock it holds (re-entrancy), fixing self-deadlock; it doesn't fix lock-order inversion between two threads.",
),
pitfall="Adding `time.sleep()` or retries around the hang. That changes timing so the deadlock happens less often, and it becomes harder to catch.",
signals="You get evidence first (stack dumps of all threads), recognise common deadlock signatures, and prevent them structurally with lock ordering, timeouts, message passing and watchdogs.",
),

P("Trap", "How do you safely call asyncio code from a regular thread (and the reverse)?",
short="""From another thread, never call loop methods or `await` directly: use `asyncio.run_coroutine_threadsafe(coro, loop)` (returns a `concurrent.futures.Future`) or `loop.call_soon_threadsafe(fn)`. From async code, run blocking functions with `await asyncio.to_thread(fn)` or `loop.run_in_executor`. asyncio objects (Queues, Events, Futures) are not thread-safe.""",
deep="""Common real-world case: a hardware callback or vendor SDK invokes your function on its own thread, and you want to push an event into an asyncio-based orchestrator.

- `asyncio.run_coroutine_threadsafe(queue.put(item), loop)` schedules the put on the loop's thread and returns a future you can wait on (with a timeout) from the calling thread.
- `loop.call_soon_threadsafe(queue.put_nowait, item)` is cheaper for fire-and-forget; it also wakes the loop immediately.
- Keep a reference to the running loop captured at startup (`asyncio.get_running_loop()`), because `get_event_loop()` in a non-loop thread won't give you the right one.
- The reverse: blocking code inside coroutines must go through `to_thread`/executors. The default executor has a limited number of workers (`min(32, cpu_count + 4)`), so many long blocking calls can queue up; give heavy users their own executor.""",
code=r'''
import asyncio, threading, time

def hardware_callback_thread(loop, queue):
    """Simulates a vendor SDK firing events on its own thread."""
    for i in range(3):
        time.sleep(0.02)
        fut = asyncio.run_coroutine_threadsafe(queue.put(f"interrupt-{i}"), loop)
        fut.result(timeout=1)                     # wait until the loop accepted it
    loop.call_soon_threadsafe(queue.put_nowait, None)

def blocking_sdk_call():
    time.sleep(0.05); return "firmware version 2.1.7"

async def main():
    loop, queue = asyncio.get_running_loop(), asyncio.Queue()
    threading.Thread(target=hardware_callback_thread, args=(loop, queue), daemon=True).start()
    version = await asyncio.to_thread(blocking_sdk_call)        # loop stays responsive
    print("from blocking SDK:", version)
    while (event := await queue.get()) is not None:
        print("event from SDK thread:", event)

asyncio.run(main())
''',
follow=(
"What goes wrong if the SDK thread calls `queue.put_nowait(item)` directly? => It touches loop-owned state from the wrong thread: it may appear to work, but the loop isn't woken, waiters can stall, and internal state can be corrupted.",
"How do you run an asyncio orchestrator from synchronous code (like a pytest test without plugins)? => `asyncio.run(main())` once at the top level; for long-lived integration, run the loop in a dedicated thread and submit work with `run_coroutine_threadsafe`.",
),
pitfall="Calling `asyncio.run()` inside a function that is already running on an event loop (it raises `RuntimeError`), or creating a new loop per call, which breaks shared resources like connection pools.",
signals="You know the thread-safe entry points, explain why asyncio objects aren't thread-safe, and mention default executor limits.",
),

P("Concept", "What are the performance pitfalls of `multiprocessing` at scale, and how do you tune it?",
short="""The main costs are **process startup** (spawn re-imports your modules), **pickling** arguments and results through pipes, and **per-task overhead** for tiny tasks. Tune with `chunksize` in `map`, an `initializer` to load expensive state once per worker, sending references (paths, IDs) instead of data, `max_tasks_per_child` to bound memory growth, and shared memory for large read-only arrays.""",
deep="""Checklist:

- **Task granularity**: each task costs a pickle round-trip (tens of microseconds or more). With 100,000 tiny tasks, set `chunksize` (e.g. 500) so workers receive batches.
- **Worker initialization**: loading a model, opening a DB connection or compiling regexes per task is wasteful; do it once with `initializer=`/`initargs=`, storing state in a module global of the worker.
- **Data transfer**: pass file paths or DB keys; results should be small aggregates. For large numeric buffers, use `multiprocessing.shared_memory` or memory-mapped files.
- **Start method**: `spawn` (Windows/macOS default, and `forkserver` on Linux in 3.14) re-imports the main module, so keep top-level code import-safe and guarded by `if __name__ == "__main__"`.
- **Memory growth and leaky libraries**: `max_tasks_per_child` (3.11+ for `ProcessPoolExecutor`) recycles workers.
- **Failure handling**: a worker crash raises `BrokenProcessPool`; make tasks idempotent and resubmit.""",
code=r'''
import time, re
from concurrent.futures import ProcessPoolExecutor

_PATTERN = None
def init_worker():
    global _PATTERN
    _PATTERN = re.compile(r"ERR(\d+)")           # expensive setup done ONCE per worker

def parse(line):
    m = _PATTERN.search(line)
    return int(m.group(1)) if m else 0

if __name__ == "__main__":
    lines = [f"2026-09-28 dev{i % 8} ERR{i % 50} lba={i}" for i in range(10_000)]
    with ProcessPoolExecutor(4, initializer=init_worker) as ex:
        for chunk in (1, 1000):
            t = time.perf_counter()
            total = sum(ex.map(parse, lines, chunksize=chunk))
            print(f"chunksize={chunk:5}: {time.perf_counter() - t:.2f}s (sum={total})")
    t = time.perf_counter(); init_worker(); total = sum(map(parse, lines))
    print(f"single process   : {time.perf_counter() - t:.2f}s  <- tiny tasks may not be worth parallelizing at all")
''',
follow=(
"Why is the single-process version competitive here? => Each task is microseconds of work; pickling and IPC dominate. Parallelize coarser units (whole files or big chunks) instead.",
"A worker process segfaults inside a C library. What happens and how do you recover? => The pool raises `BrokenProcessPool` for pending futures; recreate the pool, resubmit idempotent tasks, and quarantine inputs that reproducibly crash.",
),
pitfall="Parallelizing at the wrong granularity (per line or per record) and concluding \"multiprocessing is slow\". Measure against the single-process baseline and batch the work.",
signals="You name the cost components, tune granularity, initialization and data movement, and always compare with a serial baseline.",
),

P("Scenario", "You must make 10,000 calls to a lab management API limited to 20 requests per second and 10 concurrent connections. How do you implement it?",
short="""Use asyncio with two limits: a `Semaphore(10)` for concurrency and a token bucket (or leaky bucket) for 20 req/s. Add timeouts, retries with exponential backoff and jitter on 429/5xx (respecting `Retry-After`), idempotency for writes, and progress checkpointing so a crash resumes instead of repeating 10,000 calls.""",
deep="""Concurrency limit and rate limit are different constraints: 10 slow requests can respect the concurrency cap and still exceed the rate cap if they're fast, or the reverse. Enforce both.

Components:

- **Token bucket**: refills at 20 tokens/s up to a burst capacity; each request awaits a token. With asyncio, a single lock-protected bucket works because there's one thread.
- **Semaphore(10)** around the HTTP call.
- **Session reuse**: one `httpx.AsyncClient`/`aiohttp.ClientSession` with connection pooling.
- **Retries**: only on retryable statuses (429, 502-504, timeouts), exponential backoff with full jitter, cap attempts, honour `Retry-After`.
- **Idempotency**: GETs are safe; for POSTs, use idempotency keys or check-before-create.
- **Checkpointing**: record completed IDs (file or DB) so reruns skip them.
- **Observability**: rate achieved, error counts by status, and latency percentiles.

At 20 req/s the run takes about 500 s minimum, which is worth stating: parallelism can't beat the provider's limit.""",
code=r'''
import asyncio, time

class TokenBucket:
    def __init__(self, rate, burst):
        self.rate, self.capacity, self.tokens, self.t = rate, burst, burst, time.monotonic()
        self.lock = asyncio.Lock()
    async def acquire(self):
        async with self.lock:
            while True:
                now = time.monotonic()
                self.tokens = min(self.capacity, self.tokens + (now - self.t) * self.rate); self.t = now
                if self.tokens >= 1:
                    self.tokens -= 1; return
                await asyncio.sleep((1 - self.tokens) / self.rate)

async def call_api(i, bucket, sem, stats):
    await bucket.acquire()
    async with sem:
        stats["inflight"] += 1; stats["peak"] = max(stats["peak"], stats["inflight"])
        await asyncio.sleep(0.03)                 # network latency
        stats["inflight"] -= 1
        return i

async def main():
    # rate scaled up 10x (200/s) so the demo finishes quickly; production value would be 20
    bucket, sem, stats = TokenBucket(rate=200, burst=5), asyncio.Semaphore(10), {"inflight": 0, "peak": 0}
    n, t = 300, time.perf_counter()
    await asyncio.gather(*(call_api(i, bucket, sem, stats) for i in range(n)))
    dt = time.perf_counter() - t
    print(f"{n} calls in {dt:.2f}s -> {n / dt:.0f} req/s (limit 200), peak concurrency {stats['peak']} (limit 10)")

asyncio.run(main())
''',
follow=(
"How would you enforce the limit across 5 worker machines? => A shared limiter (Redis with an atomic Lua token bucket, or the API gateway's quota), or split the budget statically (4 req/s each) with some safety margin.",
"The API starts returning 429 even though you're under 20 req/s. What do you do? => Honour `Retry-After`, back off adaptively (reduce the rate, AIMD-style), and confirm how the provider counts (per token, per IP, sliding window).",
),
pitfall="Using only a semaphore and assuming it limits requests per second, or retrying immediately on 429, which makes the throttling worse.",
signals="You separate concurrency from rate, implement both, include retry policy with jitter and Retry-After, idempotency and resumability, and do the back-of-envelope runtime estimate.",
),

]
