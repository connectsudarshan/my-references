MODULE = dict(id=8, title="Reliability, Errors & Observability",
              desc="Error-handling strategy for long-running systems, context-rich structured logging, deadlines, graceful shutdown, crash forensics, metrics, and resumable campaigns with atomic writes.")

QUESTIONS = [

P("Design", "Define an error-handling strategy for a long-running test orchestrator that runs for days.",
short="""Classify errors, don't just catch them: **product failures** (the device misbehaved: record FAIL with evidence), **infrastructure errors** (tool crash, lab network, device unreachable: mark BLOCKED, retry or quarantine), and **framework bugs** (our code is wrong: fail loudly, alert the team). Use a small exception hierarchy that encodes this, catch at clear boundaries (per test, per device), attach context to exceptions, retry only transient infrastructure errors, and never swallow exceptions silently.""",
deep="""Why classification matters: the verdict must be trustworthy. Reporting an infrastructure hiccup as a firmware FAIL wastes developer time; reporting a firmware bug as BLOCKED hides it.

Design:

- **Hierarchy**: `FrameworkError` (base); `ProductFailure(FrameworkError)`, `InfraError(FrameworkError)` with `TransientInfraError`; unexpected exceptions (`KeyError`, `TypeError`) are framework bugs by definition.
- **Boundaries**: the per-test runner catches everything, converts it to a verdict, collects evidence, and continues with the next test; the orchestrator catches per device; only the top level decides to abort the campaign (for example when more than 20% of devices are BLOCKED, which signals a lab problem).
- **Context**: `raise InfraError("smart-log failed") from exc` keeps the cause; `exc.add_note(f"device={sn} test={name}")` (3.11+) adds context without new types.
- **Retries**: bounded, with backoff, only for transient infrastructure errors; log each attempt; never retry product failures.
- **No silent swallowing**: every broad `except` logs with traceback and converts to a verdict or re-raises.
- **Fail-fast config**: validate configuration and environment at startup, not after 10 hours.""",
code=r'''
import time, traceback

class FrameworkError(Exception): """Base for expected, classified failures."""
class ProductFailure(FrameworkError): """Device behaved incorrectly -> FAIL."""
class InfraError(FrameworkError): """Lab/tooling problem -> BLOCKED."""
class TransientInfraError(InfraError): """Worth retrying."""

def with_retry(fn, attempts=3, delay=0.01):
    for i in range(1, attempts + 1):
        try:
            return fn()
        except TransientInfraError as e:
            if i == attempts: raise
            e.add_note(f"attempt {i} failed"); time.sleep(delay * 2 ** i)

def run_test(name, body, device):
    try:
        with_retry(body)
        return "PASS", ""
    except ProductFailure as e:
        return "FAIL", f"{e} (evidence collected from {device})"
    except InfraError as e:
        return "BLOCKED", f"{e}; notes={getattr(e, '__notes__', [])}"
    except Exception as e:                                   # a bug in OUR code
        return "FRAMEWORK_ERROR", traceback.format_exception_only(e)[0].strip()

flaky = iter([TransientInfraError("ssh timeout"), None])
def t_ok(): pass
def t_fw(): raise ProductFailure("read returned stale data at LBA 0x1f40")
def t_lab(): raise InfraError("power relay unreachable")
def t_retry():
    err = next(flaky)
    if err: raise err
def t_bug(): return {"a": 1}["b"]
for name, fn in [("wrv", t_ok), ("trim", t_fw), ("pwr_cycle", t_lab), ("smart", t_retry), ("report", t_bug)]:
    verdict, detail = run_test(name, fn, "SN001")
    print(f"{name:10} {verdict:16} {detail}")
''',
follow=(
"When should the whole campaign abort instead of continuing? => When failures indicate a shared cause (most devices BLOCKED at once, the results database down, disk full), because continuing only produces garbage; define explicit abort thresholds.",
"How do you stop engineers from writing `except Exception: pass`? => Linters (Ruff `S110`, `BLE001`), review guidelines, and making the framework's per-test boundary the only place broad catches are allowed.",
),
pitfall="Treating every exception the same way: either retrying product failures (hiding bugs) or failing the product on lab issues (wasting firmware engineers' time).",
signals="You classify failures by who must act, encode that in an exception hierarchy, define catch boundaries and retry policy, preserve context, and set campaign-level abort rules.",
),

P("Concept", "How do you add correlation context (run ID, device serial, test name) to every log line across threads and asyncio tasks?",
short="""Store the context in `contextvars.ContextVar`s and inject it with a `logging.Filter` (or a custom `LogRecord` factory), and emit structured logs (JSON). Context variables are per-thread and per-asyncio-task automatically (each task copies the context when created), so concurrent device tasks don't mix up their IDs. Avoid passing IDs manually through every function or using thread-local storage with asyncio.""",
deep="""Why `contextvars`: asyncio runs many tasks on one thread, so `threading.local` would share one value across all tasks. `ContextVar` values are captured when a task is created (and `asyncio.to_thread` copies the context into the worker thread), so each device task keeps its own values.

Implementation:

- `run_id = ContextVar("run_id", default="-")`, set at the top of each task: `token = device.set(sn)` ... `device.reset(token)`.
- A `logging.Filter` subclass reads the vars and sets attributes on the record; the formatter includes them. Filters on handlers apply to all loggers, including libraries.
- JSON logs (one object per line) make searching in ELK/Loki trivial: `device="SN007" AND level=ERROR`.
- Also stamp results, metrics and artifacts with the same IDs so logs, dashboards and raw data join up.

Threads created with `threading.Thread` do **not** inherit the context by default; use `contextvars.copy_context().run(...)` or executors that copy it (asyncio's `to_thread` does).""",
code=r'''
import asyncio, contextvars, json, logging, sys

run_id = contextvars.ContextVar("run_id", default="-")
device = contextvars.ContextVar("device", default="-")

class ContextFilter(logging.Filter):
    def filter(self, record):
        record.run_id, record.device = run_id.get(), device.get()
        return True

class JsonFormatter(logging.Formatter):
    def format(self, r):
        return json.dumps({"lvl": r.levelname, "run": r.run_id, "dev": r.device, "msg": r.getMessage()})

h = logging.StreamHandler(sys.stdout); h.addFilter(ContextFilter()); h.setFormatter(JsonFormatter())
log = logging.getLogger("orchestrator"); log.addHandler(h); log.setLevel(logging.INFO)

async def test_device(sn, delay):
    device.set(sn)                                  # visible only inside this task
    log.info("start write-read-verify")
    await asyncio.sleep(delay)                      # tasks interleave here
    await asyncio.to_thread(lambda: log.info("CRC check in worker thread"))
    log.info("done")

async def main():
    run_id.set("nightly-2026-09-28")
    await asyncio.gather(test_device("SN001", 0.02), test_device("SN002", 0.01))
asyncio.run(main())
''',
follow=(
"Why not add the device serial to every log message by hand? => It's forgotten in some calls, isn't applied to library logs, and makes messages inconsistent; context injection guarantees every record is tagged.",
"How do you propagate the run ID to a subprocess or another service? => Pass it explicitly (environment variable, CLI flag, HTTP header such as W3C `traceparent`), and have the other side set its own context variable from it.",
),
pitfall="Using `threading.local()` for request/device context in asyncio code: all tasks on the loop thread share and overwrite it.",
signals="You pick contextvars and explain why thread-locals fail with asyncio, inject via filters, use structured logs, and extend correlation to results, metrics and subprocesses.",
),

P("Design", "How do you implement timeouts correctly across nested operations (deadline propagation)?",
short="""Give each top-level operation a **deadline** (an absolute monotonic time), pass it down, and let each nested call use `min(its own default, time remaining)`. That guarantees the whole operation finishes on time, avoids nested timeouts that add up beyond the budget, and lets deep code fail fast when there's no time left. In asyncio, `asyncio.timeout()` blocks nest naturally; in threads and subprocess calls, compute remaining time explicitly.""",
deep="""The problem with independent timeouts: a test step allows 60 s, calls three operations each with its own 30 s timeout, and each retries twice: worst case 3 x 3 x 30 s = 270 s, far over the 60 s budget. Hung tests then block racks for hours.

Deadline pattern:

- `Deadline(seconds)` stores `time.monotonic() + seconds` (never wall-clock time, which can jump).
- `remaining()` returns seconds left; `check()` raises if expired.
- Every blocking call takes `timeout=deadline.remaining()`: `subprocess.run`, `queue.get`, `lock.acquire`, socket operations, HTTP clients.
- Retries loop `while deadline.remaining() > backoff`.
- Report which step exhausted the budget.

asyncio: `async with asyncio.timeout(60):` at the top; inner `asyncio.timeout(10)` blocks can only shorten it; the innermost expiring timeout raises. `asyncio.timeout_at(loop.time() + x)` expresses absolute deadlines.""",
code=r'''
import subprocess, sys, time

class Deadline:
    def __init__(self, seconds): self.end = time.monotonic() + seconds
    def remaining(self): return max(0.0, self.end - time.monotonic())
    def budget(self, default): return min(default, self.remaining())
    def check(self, step):
        if self.remaining() <= 0: raise TimeoutError(f"deadline exceeded before {step}")

def cli(seconds_it_takes, dl, step):
    dl.check(step)
    t = dl.budget(default=2.0)
    try:
        subprocess.run([sys.executable, "-c", f"import time; time.sleep({seconds_it_takes})"], timeout=t, check=True)
        print(f"  {step:12} ok   (budget {t:.2f}s)")
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"{step} exceeded its budget of {t:.2f}s") from None

def test_step(total_budget):
    dl = Deadline(total_budget)
    for step, secs in [("identify", 0.2), ("smart-log", 0.3), ("self-test", 0.9), ("error-log", 0.1)]:
        cli(secs, dl, step)

for budget in (3.0, 1.0):
    print(f"step budget {budget}s:")
    t = time.monotonic()
    try:
        test_step(budget)
    except TimeoutError as e:
        print("  TIMEOUT:", e)
    print(f"  finished after {time.monotonic() - t:.2f}s (never more than the budget)")
''',
follow=(
"Why `time.monotonic()` instead of `time.time()`? => Wall-clock time can jump (NTP corrections, DST, manual changes); monotonic time only moves forward, so timeouts stay correct.",
"How do deadlines cross service boundaries? => Send the remaining time with the request (gRPC deadlines do this automatically; for HTTP use a header), and have the callee set its own deadline from it minus a safety margin.",
),
pitfall="Setting generous independent timeouts at every layer \"to be safe\"; they multiply, and a hung device blocks a rack for hours.",
signals="You explain why nested timeouts compound, implement deadline propagation with monotonic time, apply it to every blocking call and retry loop, and know the asyncio equivalent.",
),

P("Scenario", "How do you shut down a long-running Python service or test orchestrator gracefully?",
short="""On a stop signal (SIGTERM/SIGINT, or Ctrl+C / a stop API), stop accepting new work, let in-flight work finish or reach a safe checkpoint within a drain timeout, flush results and logs, release hardware reservations, close resources in reverse order, and exit with a meaningful code. Implement it with a stop `Event` checked by workers, `try/finally` and context managers for cleanup, and a hard deadline after which you exit anyway.""",
deep="""Steps:

1. **Signal handling**: `signal.signal(SIGTERM, handler)` in the main thread (POSIX); in asyncio, `loop.add_signal_handler` (not supported on Windows, where you rely on `KeyboardInterrupt` or a control API). The handler only sets a stop event; no heavy work in signal handlers.
2. **Stop intake**: the scheduler stops dispatching new tests.
3. **Drain**: running tests either finish or reach a checkpoint; cancel them after a drain timeout (Kubernetes gives 30 s by default before SIGKILL, so size accordingly).
4. **Cleanup in reverse order**: release device leases, power devices to a safe state, flush results to the database, close log handlers (`logging.shutdown()` runs at exit), close connection pools.
5. **Exit code**: distinguish clean shutdown, interrupted run and crash so CI and supervisors react correctly.
6. **Resumability**: persist progress so a restarted orchestrator continues instead of starting over.

`atexit` handlers run on normal interpreter exit and `sys.exit`, but not on `os._exit`, SIGKILL or hard crashes, so don't rely on them for critical state; persist incrementally.""",
code=r'''
import threading, time, queue, contextlib

stop = threading.Event()
results, released = [], []

@contextlib.contextmanager
def device_lease(sn):
    try: yield sn
    finally: released.append(sn)                 # always released, even when interrupted

def worker(sn, tasks):
    with device_lease(sn):
        while not stop.is_set():
            try:
                test = tasks.get(timeout=0.05)
            except queue.Empty:
                continue
            for step in range(5):                # long test with safe checkpoints
                if stop.is_set():
                    results.append((sn, test, f"INTERRUPTED at step {step}")); return
                time.sleep(0.02)
            results.append((sn, test, "PASS"))

tasks = queue.Queue()
for i in range(20): tasks.put(f"test{i}")
workers = [threading.Thread(target=worker, args=(f"SN00{i}", tasks)) for i in range(3)]
[w.start() for w in workers]
time.sleep(0.35)
print("SIGTERM received -> stop intake, drain in-flight work")
stop.set()                                         # in production: set from the signal handler
for w in workers: w.join(timeout=2.0)              # drain deadline
print("completed:", sum(r[2] == "PASS" for r in results), "| interrupted:", [r[:2] for r in results if r[2] != "PASS"])
print("leases released:", sorted(released), "| not started (resume later):", tasks.qsize())
''',
follow=(
"Why must the signal handler only set a flag? => Signal handlers run between bytecodes in the main thread and can interrupt anything (including logging or lock-holding code); doing real work there risks deadlocks and inconsistent state.",
"How do you guarantee devices end in a safe state if the orchestrator is SIGKILLed? => You can't from inside the process; use lease expiry in the device pool and a separate reaper/watchdog service that resets devices whose leases expired.",
),
pitfall="Relying on `atexit` or `__del__` to release hardware and save results. Neither runs on SIGKILL, OOM kills or hard crashes.",
signals="You cover signal handling correctly, drain with a deadline, cleanup ordering, exit codes, resumability, and an external safety net for hard kills.",
),

P("Debug", "A Python process running native libraries crashes with no Python traceback (segfault or access violation). How do you investigate?",
short="""Enable `faulthandler` (`python -X faulthandler` or `PYTHONFAULTHANDLER=1`) so Python prints the traceback of every thread on fatal signals; that usually points at the call into the native library. Then reproduce with `python -X dev`, collect a core dump and inspect it with gdb (CPython's `py-bt` extension) or WinDbg, check native library versions and ABI compatibility, and isolate the risky library in a subprocess so a crash can't take down the orchestrator.""",
deep="""Typical causes: bugs in C extensions or vendor SDKs, ctypes misuse (wrong argtypes/restype, buffers freed too early, wrong struct layout), using a library across threads that isn't thread-safe, mismatched ABI (extension built for a different Python or dependency version), and stack overflows from deep recursion in C.

Investigation steps:

1. **faulthandler** on by default in lab runs: it's cheap and prints Python-level stacks for all threads on SIGSEGV/SIGABRT (or access violations on Windows).
2. **Core dumps**: enable (`ulimit -c unlimited` / systemd-coredump / Windows Error Reporting LocalDumps), then `gdb python core` with `py-bt` to see Python frames next to C frames.
3. **Narrow down**: reproduce with minimal inputs; run the suspicious call in a subprocess with the same arguments; try `PYTHONMALLOC=debug` and `-X dev` to catch memory misuse earlier.
4. **ctypes review**: every foreign function needs `argtypes` and `restype`; 64-bit pointers returned as default `c_int` get truncated and crash later. On Windows, ctypes wraps calls in structured exception handling, so some access violations surface as `OSError: exception: access violation` instead of killing the process; don't mistake that for a recoverable error, since memory may already be corrupted.
5. **Containment**: run vendor SDK calls in a helper process (multiprocessing or a small RPC server) so a crash becomes a recoverable `BrokenProcessPool`/exit code with the device marked BLOCKED.""",
code=r'''
import subprocess, sys

# faulthandler._sigsegv() is CPython's test helper that triggers a real native crash,
# standing in for a buggy C extension or vendor SDK call.
crash_code = "import faulthandler\ndef read_register():\n    faulthandler._sigsegv()\nread_register()\n"
for flags in ([], ["-X", "faulthandler"]):
    r = subprocess.run([sys.executable, *flags, "-c", crash_code], capture_output=True, text=True)
    lines = [l for l in r.stderr.splitlines() if l.strip()]
    print(f"flags={flags or 'none'}: exit code {r.returncode}, stderr lines: {len(lines)}")
    for l in lines[:6]:
        print("   ", l.strip()[:90])
''',
follow=(
"Why isolate a crashing vendor SDK in a subprocess instead of fixing it? => You often can't fix vendor code quickly; isolation turns a process-wide crash into a handled error for one device while you work with the vendor.",
"What is the most common ctypes crash you have seen? => Missing `restype` on functions returning pointers: ctypes assumes `int`, truncates a 64-bit pointer, and a later access crashes far from the real bug.",
),
pitfall="Wrapping the native call in `try/except`. A segfault is not a Python exception; nothing is caught and the process dies.",
signals="You enable faulthandler proactively, know core-dump workflows, list typical native causes including ctypes mistakes, and contain risky native code with process isolation.",
),

P("Design", "How do you make a multi-day test campaign resumable and its results trustworthy after crashes?",
short="""Persist progress incrementally and atomically: record each completed unit (test x device x iteration) as it finishes, in a transactional store (SQLite/Postgres) or with **atomic file writes** (write to a temp file in the same directory, `flush` + `os.fsync`, then `os.replace`). Make units idempotent, keyed by a stable ID, so a restart skips completed work and re-runs only in-flight units. Record the campaign manifest (config, versions, seeds) at start.""",
deep="""Failure scenarios: orchestrator crash, host reboot, power loss in the lab, disk full.

Principles:

- **Unit of work** with a stable key, e.g. `(campaign_id, device_sn, test, iteration)`. State machine per unit: PENDING, RUNNING (with lease/heartbeat), DONE, FAILED.
- **Atomic writes**: `os.replace()` is atomic on POSIX and Windows when source and target are on the same filesystem. Without it, a crash mid-write leaves a truncated JSON file that breaks the next run. `fsync` makes it durable across power loss.
- **Transactions**: SQLite in WAL mode handles concurrent readers and crash safety well for single-host orchestrators.
- **Idempotency**: a unit that ran twice must not double-count; upserts keyed by unit ID.
- **Resume logic**: on start, units in RUNNING whose lease expired become PENDING again (the device may need re-preconditioning).
- **Integrity**: store the manifest (framework commit, firmware versions, config hash, seeds) so resumed results are provably from the same campaign.""",
code=r'''
import json, os, tempfile, pathlib

def atomic_write_json(path: pathlib.Path, data) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)                          # atomic swap on the same filesystem
    except BaseException:
        os.unlink(tmp); raise

class Campaign:
    def __init__(self, state_file, units):
        self.path = state_file
        self.state = json.loads(state_file.read_text()) if state_file.exists() else {"done": {}}
        self.units = units
    def run(self, execute, crash_after=None):
        for n, unit in enumerate(u for u in self.units if u not in self.state["done"]):
            if crash_after is not None and n == crash_after:
                raise SystemExit("host rebooted!")
            self.state["done"][unit] = execute(unit)
            atomic_write_json(self.path, self.state)    # progress persisted per unit

state = pathlib.Path(tempfile.mkdtemp()) / "campaign.json"
units = [f"SN{d}:wrv:iter{i}" for d in range(2) for i in range(4)]
executed = []
def execute(u): executed.append(u); return "PASS"
try:
    Campaign(state, units).run(execute, crash_after=5)
except SystemExit as e:
    print("crash:", e, "| units done before crash:", len(executed))
Campaign(state, units).run(execute)
print("after resume:", len(json.loads(state.read_text())["done"]), "of", len(units), "done | total executions:", len(executed), "(no unit ran twice)")
''',
follow=(
"Why write the temp file in the same directory as the target? => `os.replace` is only atomic within one filesystem; a temp file in `/tmp` may be on a different mount, turning the rename into a non-atomic copy.",
"SQLite or files for campaign state? => SQLite for anything beyond a small JSON state: transactions, concurrent readers, queries for dashboards, and crash safety with WAL; files are fine for tiny single-writer state.",
),
pitfall="`json.dump(state, open(path, 'w'))` after each test: a crash during the write leaves a truncated file, and the campaign can't even restart.",
signals="You define stable idempotent work units, persist atomically and durably, handle in-flight units on restart, and record a manifest for trustworthy results.",
),

P("Concept", "What would you measure and alert on for a fleet of lab test machines running Python orchestrators?",
short="""Use the RED/USE ideas adapted to test infrastructure: **throughput** (tests completed per hour), **errors** split by class (FAIL vs BLOCKED vs framework error), **durations** (p50/p95 per test type, queue wait for devices), and **saturation** (device pool utilization, CPU, memory, disk of hosts). Alert on symptoms that need a human (BLOCKED rate spike, no heartbeat, pool exhausted, disk nearly full), not on every failing test. Use histograms, and keep label cardinality low.""",
deep="""Metric design:

- **Counters**: `tests_total{result, test_suite}`; `commands_total{tool, outcome}`.
- **Histograms**: test duration and device command latency; percentiles from histogram buckets (Prometheus) rather than averages.
- **Gauges**: devices free/leased/quarantined, orchestrator heartbeat timestamp, queue depth.
- **Cardinality**: labels like `suite` and `result` are fine; `device_serial` for 5,000 devices times many metrics can explode storage; put per-device detail in logs and results DB instead.

Alerts (actionable only):

- No heartbeat from an orchestrator for 10 minutes (dead-man's switch).
- BLOCKED ratio over 10% for 30 minutes (lab problem).
- Device pool wait p95 over 1 hour (capacity).
- Host disk over 90%, or memory growth trend (leak).
- Nightly run didn't start or didn't publish results (the silent failure that is otherwise noticed a week later).

Dashboards per audience: firmware teams see failure trends by build; lab ops see pool health and infrastructure errors.""",
code=r'''
import random, statistics, collections

random.seed(4)
durations = [random.lognormvariate(4.0, 0.6) for _ in range(2000)]     # seconds per test
outcomes = collections.Counter(random.choices(["PASS", "FAIL", "BLOCKED"], weights=[90, 3, 7], k=2000))

q = statistics.quantiles(durations, n=100)
print(f"tests: {sum(outcomes.values())} | {dict(outcomes)}")
print(f"duration p50 {q[49]:.0f}s  p95 {q[94]:.0f}s  p99 {q[98]:.0f}s  mean {statistics.fmean(durations):.0f}s")
blocked_ratio = outcomes["BLOCKED"] / sum(outcomes.values())
print(f"BLOCKED ratio {blocked_ratio:.1%} ->", "ALERT lab ops" if blocked_ratio > 0.05 else "ok")
buckets = [30, 60, 120, 300, 600, float("inf")]                          # Prometheus-style histogram
counts = [sum(d <= b for d in durations) for b in buckets]
print("cumulative histogram:", dict(zip([str(b) for b in buckets], counts)))
''',
follow=(
"Why are averages misleading for test durations? => Durations are skewed (lognormal-like); a few very long or hung tests move the mean a lot while telling you nothing about the typical case; use p50/p95/p99.",
"How do you detect a nightly run that silently didn't happen? => A dead-man's switch: the run pushes a \"completed\" timestamp metric, and an alert fires if it's older than 26 hours.",
),
pitfall="Alerting on every FAIL (alert fatigue) while having no alert for \"the nightly run never started\".",
signals="You separate product failures from infrastructure health, choose metric types and percentiles, manage cardinality, and define a few actionable alerts including a dead-man's switch.",
),

]
