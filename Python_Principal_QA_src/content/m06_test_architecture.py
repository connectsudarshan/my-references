MODULE = dict(id=6, title="Test Framework Architecture",
              desc="Designing pytest-based validation frameworks for hardware: fixtures and device lifecycle, plugins and hooks, parallel runs across device pools, flaky-test management, reproducibility and testing the framework itself.")

QUESTIONS = [

P("Design", "Design a pytest-based validation framework for SSD firmware that runs on lab racks and in CI with simulated devices.",
short="""Build on pytest rather than inventing a runner. Model the device lifecycle as **fixtures** with the right scope (session: lab connection; module: device reserved and preconditioned; function: clean namespace), select hardware via **markers** and CLI options, parametrize over firmware/configuration matrices, collect logs on failure with a **plugin hook**, and publish structured results to a database. A HAL interface lets the same tests run against a simulator in CI.""",
deep="""Architecture:

- **HAL**: a `BlockDevice`/`NvmeController` protocol with a real implementation (nvme-cli, ioctl or vendor SDK) and a simulated one. Tests only see the protocol.
- **Fixtures**: `lab` (session), `device` (module scope: reserve from a pool, format, check health, release in teardown), `namespace` (function scope). Fixture finalizers must always release hardware, even on failures.
- **Selection**: markers such as `@pytest.mark.requires(feature="zns", min_fw="2.1")`; a `pytest_collection_modifyitems` hook deselects or skips tests the attached device can't run, with a clear reason.
- **Matrices**: `pytest.mark.parametrize` or `pytest_generate_tests` for queue depths, block sizes and power-loss points; keep IDs readable (`ids=`).
- **Evidence on failure**: a `pytest_runtest_makereport` hookwrapper that, on failure, grabs SMART logs, firmware logs, the serial console buffer and the command history, and attaches them to the result.
- **Results**: every test emits a structured record (run ID, device serial, firmware, config, verdict, duration, artifacts) to a results service, not only JUnit XML.
- **Timeouts and watchdogs**: per-test timeout with stack dumps, device health checks between tests, automatic quarantine of devices that fail health checks.
- **Reproducibility**: record seeds, firmware versions, framework commit and resolved config per run.""",
code=r'''
# conftest.py (sketch of the key extension points; requires pytest)
import pytest

def pytest_addoption(parser):
    parser.addoption("--device", default="sim", help="device pool name or 'sim'")

@pytest.fixture(scope="session")
def lab(request):
    pool = connect_pool(request.config.getoption("--device"))   # real rack or simulator
    yield pool
    pool.close()

@pytest.fixture(scope="module")
def device(lab):
    dev = lab.reserve(timeout_s=600)
    dev.format(); assert dev.health().critical_warning == 0
    yield dev
    lab.release(dev)                                         # always runs, even on failure

def pytest_collection_modifyitems(config, items):
    caps = current_device_capabilities(config)
    for item in items:
        for m in item.iter_markers("requires"):
            if not caps.supports(**m.kwargs):
                item.add_marker(pytest.mark.skip(reason=f"device lacks {m.kwargs}"))

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed and "device" in item.funcargs:
        dev = item.funcargs["device"]
        report.sections.append(("smart-log", dev.smart_log_text()))
        report.sections.append(("console", dev.console_tail(200)))
''', run=False,
follow=(
"Why not write your own test runner? => pytest already solves discovery, fixtures, parametrization, reporting, parallelism (xdist) and has a large plugin ecosystem; a custom runner becomes a second product to maintain. Extend pytest through hooks instead.",
"How do you keep hardware fixtures from leaking devices when a test crashes the process? => Reservations with leases/heartbeats in the pool service, so a dead runner's devices expire and are reclaimed; plus finalizers for normal failures.",
),
pitfall="Putting device setup inside each test body. It duplicates code, is skipped on early failures, and makes cleanup unreliable. Use fixtures with finalizers.",
signals="You separate HAL from tests, use fixture scopes deliberately, select tests by capability, collect evidence automatically on failure, and store structured results with reproducibility metadata.",
),

P("Scenario", "Your 10,000-test nightly suite has a 4% flaky failure rate and engineers have stopped trusting it. What do you do?",
short="""Treat flakiness as a measurable defect: record every result with its history, compute a per-test flake rate (fails, then passes on unchanged code and firmware), quarantine the worst offenders out of the gating set (visible, owned, with deadlines), fix root causes by category (timing assumptions, order dependence, shared state, environment and hardware issues), and only allow automatic retries if every retry is recorded.""",
deep="""Steps:

1. **Measure**: store results per (test, commit, firmware, device). A test is flaky if it both passed and failed for the same inputs. Rank by flake rate x runtime x number of teams affected.
2. **Restore trust quickly**: move the top flaky tests to a non-gating "quarantine" job. Each quarantined test gets an owner and a ticket; quarantine is time-limited.
3. **Fix root causes** by category (listed below).
4. **Tooling**: run tests in random order (`pytest-randomly`), re-run the same test many times (`pytest --count` / a stress job), capture complete evidence on first failure.
5. **Policy**: retries are allowed only when the retry and first failure are both reported, so intermittent product bugs remain visible.
6. **Track the trend** weekly: flake rate, quarantine size, mean time to fix.

Root-cause categories in hardware validation:

- fixed `sleep()` instead of polling for a condition with a timeout
- order dependence and shared state (global caches, a device left in a non-default state)
- resource contention (two tests on one device, thermal throttling, lab network)
- nondeterministic data (unseeded random workloads)
- real intermittent firmware bugs, which must not be hidden by retries""",
code=r'''
from collections import defaultdict

# (test, firmware, commit, verdict) history from the results database
history = [
    ("test_trim_basic", "2.1.7", "a1f", "PASS"), ("test_trim_basic", "2.1.7", "a1f", "FAIL"),
    ("test_trim_basic", "2.1.7", "a1f", "PASS"), ("test_pwr_loss_qd32", "2.1.7", "a1f", "FAIL"),
    ("test_pwr_loss_qd32", "2.1.7", "a1f", "FAIL"), ("test_smart_temp", "2.1.7", "a1f", "PASS"),
    ("test_smart_temp", "2.1.7", "b22", "PASS"), ("test_fw_download", "2.1.7", "a1f", "PASS"),
    ("test_fw_download", "2.1.7", "a1f", "FAIL"), ("test_fw_download", "2.1.7", "a1f", "PASS"),
    ("test_fw_download", "2.1.7", "a1f", "PASS"),
]
groups = defaultdict(list)
for test, fw, commit, verdict in history:
    groups[(test, fw, commit)].append(verdict)

report = defaultdict(lambda: [0, 0])                  # test -> [flaky groups, total runs]
for (test, *_), verdicts in groups.items():
    report[test][1] += len(verdicts)
    if len(set(verdicts)) > 1:                        # same inputs, different outcomes
        report[test][0] += 1
for test, (flaky, runs) in sorted(report.items(), key=lambda kv: -kv[1][0]):
    label = "FLAKY -> quarantine + owner" if flaky else ("consistent" if runs else "")
    print(f"{test:22} runs={runs}  {label}")
print("note: test_pwr_loss_qd32 fails consistently: a real bug, not flakiness")
''',
follow=(
"A team wants `--reruns 3` on everything to make the dashboard green. How do you respond? => Reruns hide intermittent firmware bugs, which are exactly what validation exists to find. Allow reruns only with full reporting of first failures and a flake budget, and never on tests whose failures could be product defects without triage.",
"How do you replace `time.sleep(5)` waits for the device? => Poll the actual condition (controller ready bit, namespace visible, log entry present) with a timeout and backoff, and report what was observed when the timeout expires.",
),
pitfall="Blanket automatic retries. They turn a 4% flake rate into a green dashboard that hides real intermittent firmware defects.",
signals="You quantify flakiness with history, restore trust with an owned quarantine, fix by root-cause category, distinguish flaky tests from intermittent product bugs, and set a retry policy that preserves evidence.",
),

P("Design", "How do you run a hardware test suite in parallel across a pool of 64 devices?",
short="""Use a scheduler that treats devices as leased resources: workers (pytest-xdist or a custom dispatcher) acquire a device matching the test's requirements from a pool service with leases and heartbeats, run the test, return the device after health checks, and quarantine devices that fail them. Group tests by required capability and duration to keep devices busy, and make results traceable to the exact device serial.""",
deep="""Considerations:

- **Allocation**: a central pool (a small service or DB table with atomic reservation) rather than each worker guessing. Leases expire if a worker dies, so devices never stay locked forever. Locally, file locks (`O_CREAT|O_EXCL`) work for a single host.
- **Worker model**: `pytest -n 64 --dist loadgroup` with an `xdist_group` per device class, or a dispatcher that sends test IDs to per-device workers. Each worker's session fixture binds to one device (`worker_id` from xdist).
- **Scheduling**: longest tests first reduces the tail; tests with rare capability requirements shouldn't wait behind common ones; don't co-schedule tests that share a host bus if they interfere.
- **Isolation**: reset state between tests (format, reset controller, verify default feature settings); health check before handing to the next test.
- **Failure handling**: a device that fails health checks is quarantined, not retried endlessly; the test is marked "BLOCKED: infrastructure", not FAIL.
- **Observability**: pool utilization, queue wait per capability, device health trends.""",
code=r'''
import os, tempfile, threading, time, random, contextlib

class DevicePool:
    """Single-host pool using atomic lock files (O_EXCL) as leases."""
    def __init__(self, serials, lock_dir):
        self.serials, self.lock_dir = serials, lock_dir
    @contextlib.contextmanager
    def lease(self, timeout=5.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            for sn in self.serials:
                path = os.path.join(self.lock_dir, sn + ".lock")
                try:
                    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)   # atomic claim
                except FileExistsError:
                    continue
                os.write(fd, str(os.getpid()).encode()); os.close(fd)
                try:
                    yield sn
                finally:
                    os.remove(path)                                            # release
                return
            time.sleep(0.005)
        raise TimeoutError("no device available")

pool = DevicePool([f"SN{i:03}" for i in range(4)], tempfile.mkdtemp())
usage, lock, active, peak = {}, threading.Lock(), [0], [0]
def run_test(name):
    with pool.lease() as sn:
        with lock: active[0] += 1; peak[0] = max(peak[0], active[0]); usage.setdefault(sn, []).append(name)
        time.sleep(random.uniform(0.01, 0.03))
        with lock: active[0] -= 1

random.seed(0)
threads = [threading.Thread(target=run_test, args=(f"t{i}",)) for i in range(20)]
[t.start() for t in threads]; [t.join() for t in threads]
print("tests per device:", {sn: len(v) for sn, v in sorted(usage.items())}, "| peak concurrent:", peak[0], "(4 devices)")
''',
follow=(
"How do you make the pool work across 10 lab hosts? => Move reservation to a shared service or database with an atomic `UPDATE ... WHERE state='free'` or Redis `SET NX PX`, leases with expiry, and heartbeats from the worker.",
"How do you reduce total wall time when test durations vary from 1 minute to 6 hours? => Schedule longest-first, split very long tests into checkpointed phases if possible, and track historical durations to predict the critical path.",
),
pitfall="Letting each test pick a device by index (`devices[worker_id]`). One dead device then fails every test assigned to that worker, and nothing is rebalanced.",
signals="You treat devices as leased resources with expiry, match capabilities, schedule for utilization, isolate state between tests, and distinguish infrastructure failures from test failures.",
),

P("Debug", "A test passes when run alone but fails when run as part of the full suite. How do you find the cause?",
short="""It's test pollution: some earlier test leaves state behind. Find the polluter by bisection (run the victim with halves of the preceding tests until one culprit remains; tools like `detect-test-pollution` automate it), then look for shared state: module-level caches, globals patched and not restored, environment variables, current directory, singletons, leftover device configuration, or fixtures with too-wide scope.""",
deep="""Procedure:

1. Reproduce deterministically: note the exact order (`pytest -p no:randomly` or the seed used), then confirm the victim passes alone.
2. **Bisect** the tests that ran before it: run `[first half] + victim`; if it fails, the polluter is in that half; repeat. That's log2(N) runs.
3. Inspect the polluter for shared state (list below).
4. Fix at the source: use `monkeypatch`, context managers, fresh objects per test, and teardown that restores device defaults. Then run the suite in random order in CI to prevent regressions.

Typical polluters:

- mutation of module globals or class attributes (`Config.retries = 0`)
- `unittest.mock.patch` started with `.start()` but never stopped
- `os.environ` / `os.chdir` / `sys.path` changes
- caches (`lru_cache`) holding state across tests
- fixtures with `scope="module"`/`"session"` whose object is mutated by a test
- on hardware: device features (write cache, power state, namespace layout) left non-default""",
code=r'''
import unittest, functools

class DeviceSettings:                    # module-level shared state (the hazard)
    write_cache = True

@functools.lru_cache
def default_timeout(): return 30

class TestA(unittest.TestCase):
    def test_disable_cache(self):
        DeviceSettings.write_cache = False           # polluter: never restored
        self.assertFalse(DeviceSettings.write_cache)

class TestB(unittest.TestCase):
    def test_perf_expects_cache_on(self):
        self.assertTrue(DeviceSettings.write_cache, "write cache unexpectedly disabled")

def run(*cases):
    suite = unittest.TestSuite(cases)
    r = unittest.TestResult(); suite.run(r)
    return "PASS" if r.wasSuccessful() else "FAIL"

victim = TestB("test_perf_expects_cache_on")
print("victim alone     :", run(TestB("test_perf_expects_cache_on")))
DeviceSettings.write_cache = True
print("after TestA      :", run(TestA("test_disable_cache"), victim))
DeviceSettings.write_cache = True

class TestAFixed(unittest.TestCase):
    def test_disable_cache(self):
        self.addCleanup(setattr, DeviceSettings, "write_cache", DeviceSettings.write_cache)   # restore
        DeviceSettings.write_cache = False
print("after fixed TestA:", run(TestAFixed("test_disable_cache"), TestB("test_perf_expects_cache_on")))
''',
follow=(
"How do you prevent this class of bug across a big suite? => Random test ordering in CI, a fixture that snapshots and verifies global state (env, cwd, key module attributes) before and after each test, and banning module-level mutable state in test code via review and linters.",
"What's the hardware equivalent? => A post-test fixture that checks and restores device defaults (features, power state, namespaces) and fails loudly naming the test that changed them.",
),
pitfall="Marking the victim test as flaky or reordering tests so it runs first. The polluter keeps corrupting other tests silently.",
signals="You recognise pollution, bisect systematically, list concrete shared-state sources including hardware state, and prevent recurrence with random ordering and state guards.",
),

P("Concept", "How do you make randomized stress tests reproducible?",
short="""Generate all randomness from an explicit seed that is recorded with the result: use a dedicated `random.Random(seed)` instance (not the global module state), derive per-device or per-thread seeds deterministically from a master seed, log the seed on failure, and provide a replay command. For data patterns, make them a pure function of (seed, LBA) so any block can be regenerated and verified independently.""",
deep="""Why a dedicated instance: the global `random` module is shared by every library in the process; any extra call shifts the sequence and breaks replay. `random.Random(seed)` isolates it.

Deriving seeds: `master_seed` for the run, then `hash((master_seed, device_serial, iteration))` via a stable hash (e.g. `hashlib.blake2b`), because Python's built-in `hash()` of strings is randomized per process (PYTHONHASHSEED).

Data patterns: a pattern function `block(seed, lba)` lets the verifier recompute expected data without storing what was written, which scales to terabytes. Embedding the LBA and a write sequence number in each block also detects misdirected or stale writes.

Workflow: every failure report shows `--seed=...` and the exact configuration, so an engineer can replay the same sequence on the bench. Property-based testing (Hypothesis) complements this by shrinking failing inputs to minimal cases.""",
code=r'''
import hashlib, random

def derive_seed(master, *parts):
    h = hashlib.blake2b(repr((master,) + parts).encode(), digest_size=8)
    return int.from_bytes(h.digest(), "little")          # stable across processes and machines

def workload(master, serial, n=5):
    rng = random.Random(derive_seed(master, serial))       # isolated generator
    return [(rng.choice(["read", "write", "trim"]), rng.randrange(0, 1 << 20), rng.choice([4096, 131072])) for _ in range(n)]

def block(seed, lba, size=16):                            # data = pure function of (seed, lba)
    return hashlib.blake2b(f"{seed}:{lba}".encode(), digest_size=size).digest()

MASTER = 20260928
first = workload(MASTER, "SN001")
replay = workload(MASTER, "SN001")
print("replay identical:", first == replay)
print("per-device streams differ:", workload(MASTER, "SN001") != workload(MASTER, "SN002"))
print(first[:2])
written = block(MASTER, 4096)
print("verify without storing expected data:", block(MASTER, 4096) == written)
print(f"on failure print: pytest tests/stress --seed={MASTER} --device=SN001")
''',
follow=(
"Why not use `hash((seed, serial))` to derive seeds? => String hashing is randomized per process (PYTHONHASHSEED), so the derived seed changes between runs; use a stable hash like BLAKE2 or SHA-256.",
"How do you reproduce a failure that depends on thread timing, not just random data? => Record the operation log with timestamps and ordering, replay it deterministically in a single thread first, and use stress runs with many seeds to reproduce timing issues statistically.",
),
pitfall="Calling `random.seed(42)` at the top of a test and assuming reproducibility, while other code (libraries, fixtures) also consumes the global generator.",
signals="You isolate generators, derive seeds stably, record them for replay, and use seed-derived data patterns for scalable verification.",
),

P("Scenario", "How do you test the test framework itself?",
short="""Treat it as production software: unit tests for framework logic with **simulated devices** (fast, run on every PR), contract tests proving the simulator and real drivers behave the same for the HAL interface, integration tests on a small real hardware pool before release, and staged rollout of framework versions (canary rack first). Also test that failures are detected: inject faults and confirm tests fail.""",
deep="""Layers:

- **Unit tests** of scheduling, result parsing, config handling and fixtures, using an in-memory simulator implementing the HAL protocol. Seconds, on every PR.
- **Contract tests**: one test suite parameterized over implementations (simulator, real driver). If the simulator drifts from reality, the contract suite catches it on hardware nightly.
- **Fault injection**: the simulator can corrupt data, time out, drop commands or report critical warnings. The framework must turn each into the correct verdict. This tests the test ("does it detect the bug it exists for?").
- **Mutation-style checks**: deliberately break a verifier and confirm tests fail (a verifier that always passes is the most dangerous bug in validation).
- **Release process**: version the framework, run the canary rack on the new version alongside the old, compare verdict distributions, then roll out.
- **Metrics**: framework-caused failures ("infrastructure" category) tracked separately from product failures.""",
code=r'''
import zlib

class SimulatedDrive:
    def __init__(self, fault=None): self.blocks, self.fault = {}, fault
    def write(self, lba, data): self.blocks[lba] = data
    def read(self, lba):
        data = self.blocks[lba]
        if self.fault == "bitflip" and lba == 7:
            data = bytes([data[0] ^ 0x01]) + data[1:]           # injected corruption
        if self.fault == "stale" and lba == 3:
            return b"\0" * len(data)                              # injected lost write
        return data

def verify_test(drive, lbas=range(10)):
    for lba in lbas:
        drive.write(lba, lba.to_bytes(4, "little") * 128)
    bad = [lba for lba in lbas if zlib.crc32(drive.read(lba)) != zlib.crc32(lba.to_bytes(4, "little") * 128)]
    return ("FAIL", bad) if bad else ("PASS", [])

for fault in (None, "bitflip", "stale"):
    print(f"fault={fault!s:8} -> verdict {verify_test(SimulatedDrive(fault))}")
''',
follow=(
"How do you keep the simulator honest? => Run the same contract suite against the simulator and real devices; any divergence is a simulator bug. Record real device traces and replay them into the simulator.",
"What's the risk of relying on a simulator? => It encodes your assumptions; timing, error recovery and firmware quirks may be missing. Use it for framework logic and fast feedback, never as a substitute for hardware validation of the product.",
),
pitfall="A verifier that silently passes (for example comparing a buffer with itself). Without fault injection, nobody notices until a customer finds the data corruption.",
signals="You test the framework with simulators, contract tests and fault injection, prove verifiers can fail, and release framework changes gradually with verdict comparisons.",
),

P("Concept", "How do pytest fixtures, scopes and finalization work under the hood, and what goes wrong at scale?",
short="""pytest builds a dependency graph from fixture names in test signatures, instantiates each fixture once per scope (function, class, module, package, session), and caches it for that scope. Generator fixtures run setup before `yield` and teardown after, in reverse dependency order, even when tests fail. At scale, problems come from too-broad scopes sharing mutated state, expensive autouse fixtures, and teardown that can itself fail or hang.""",
deep="""Mechanics:

- Resolution by **name**: `def test_x(device, tmp_path)` requests fixtures; fixtures can request other fixtures. `conftest.py` files provide fixtures to their directory tree; closer definitions override farther ones.
- **Caching per scope**: a module-scoped fixture is created once per test module and shared by its tests. Parametrized fixtures create one instance per parameter.
- **Teardown order**: last set up, first torn down. If setup fails, teardown of already-created fixtures still runs; the test is reported as an error, not a failure.
- `request.addfinalizer` registers extra cleanup; `yield` fixtures are the modern form.

Pitfalls at scale:

- **Scope creep**: making `device` session-scoped for speed means tests share device state; pair broad scopes with explicit reset fixtures.
- **autouse** fixtures run for every test, often invisibly; keep them cheap.
- **Teardown failures** mask original failures or leave hardware reserved; make teardown idempotent, time-limited and logged.
- **xdist**: each worker has its own session, so "session" fixtures run once per worker, not once globally; use locks or an external service for truly global setup.""",
code=r'''
# Equivalent semantics demonstrated without pytest: scoped caching + reverse-order teardown
from contextlib import ExitStack, contextmanager

@contextmanager
def lab():
    print("setup lab (session)"); yield "lab"; print("teardown lab")
@contextmanager
def device(lab):
    print(f"  setup device on {lab} (module)"); yield "nvme0"; print("  teardown device")
@contextmanager
def namespace(dev):
    print(f"    setup namespace on {dev} (function)"); yield "ns1"; print("    teardown namespace")

tests = {"test_write": lambda ns: None, "test_trim": lambda ns: 1 / 0}
with ExitStack() as session:
    lab_obj = session.enter_context(lab())
    with ExitStack() as module:
        dev = module.enter_context(device(lab_obj))
        for name, body in tests.items():
            with ExitStack() as fn:
                ns = fn.enter_context(namespace(dev))
                try:
                    body(ns); print(f"    {name}: PASS")
                except Exception as e:
                    print(f"    {name}: FAIL ({type(e).__name__}) -> teardown still runs")
''',
follow=(
"How do you do one-time global setup (e.g. flash firmware on all devices) when running with pytest-xdist? => Use a file lock or an external coordination service inside the session fixture so only the first worker performs it and others wait, or do it in a separate pipeline step before pytest starts.",
"A session fixture's teardown hangs. What happens and how do you protect against it? => The run never finishes and hardware stays reserved; wrap teardown steps in timeouts, log each step, and rely on pool leases that expire.",
),
pitfall="Widening fixture scope to save setup time without adding state reset, then chasing order-dependent failures for weeks.",
signals="You explain name-based resolution, per-scope caching and teardown order, and connect them to scaling problems: shared state, autouse cost, xdist semantics and robust teardown.",
),

]
