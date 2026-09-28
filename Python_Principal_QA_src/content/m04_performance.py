MODULE = dict(id=4, title="Performance Engineering",
              desc="A measurement-first method: profiling, algorithmic fixes, pushing work into C, caching correctly, benchmarking without fooling yourself, startup time and zero-copy binary processing.")

QUESTIONS = [

P("Scenario", "Your test-result parser takes 40 minutes per nightly run and the team wants it under 5. How do you approach it?",
short="""Measure before changing anything: set the target, build a reproducible benchmark on real data, and profile (`cProfile` for call counts, `py-spy`/Scalene for sampling in production-like runs). Fix the biggest hotspot first, usually an algorithmic or I/O issue, re-measure, and stop when the target is met. Only then consider parallelism or compiled code.""",
deep="""A method interviewers look for:

1. **Define success**: 40 to under 5 minutes on the nightly dataset, same output. Save a golden output to guarantee correctness.
2. **Reproduce and time**: a benchmark script with a representative input (a real night's logs, or a scaled sample).
3. **Profile**: `python -m cProfile -o prof.out parser.py` then `pstats` sorted by cumulative time; or `py-spy record -o flame.svg -- python parser.py` for a flame graph with low overhead. Check whether the time is CPU, I/O or waiting.
4. **Fix in this order**, largest wins first: algorithm and data structures (O(n²) membership tests, repeated work); I/O patterns (reading files many times, per-line DB inserts instead of batches); avoiding Python-level loops (use `str` methods, `re`, `collections.Counter`, `sorted` with keys, which run in C); caching repeated computations; parallelism across files; compiled code (Cython, Rust/PyO3) or vectorized libraries for the true hot core.
5. **Re-measure after every change**, keep the benchmark in CI to catch regressions.

In practice, 40 minutes to under 5 is usually one or two quadratic loops or per-row database round trips, not "Python is slow".""",
code=r'''
import cProfile, pstats, io, random

random.seed(1)
known_failures = [f"TC-{i}" for i in range(4000)]
results = [f"TC-{random.randint(0, 20000)}" for _ in range(20000)]

def classify_slow():
    return sum(1 for r in results if r in known_failures)      # list membership: O(n*m)

def classify_fast():
    known = set(known_failures)                                 # O(1) lookups
    return sum(1 for r in results if r in known)

for fn in (classify_slow, classify_fast):
    prof = cProfile.Profile(); prof.enable(); n = fn(); prof.disable()
    buf = io.StringIO()
    stats = pstats.Stats(prof, stream=buf)
    print(f"{fn.__name__}: {n} known failures, total {stats.total_tt:.3f}s")
''',
follow=(
"cProfile says 70% of time is in `json.loads`. Now what? => Check whether you parse the same data multiple times, parse only needed fields, switch to a faster parser (orjson), or change the log format; and check it's not dominated by one huge file you could stream.",
"Why use `py-spy` rather than `cProfile` in production? => It samples from outside the process with low overhead and needs no code changes; cProfile instruments every call and can distort timings of call-heavy code.",
),
pitfall="Rewriting the parser in another language or adding multiprocessing before profiling. That multiplies complexity and often misses the actual quadratic loop.",
signals="You set a target and correctness check first, profile to find evidence, fix algorithmic and I/O issues before micro-optimizing, and lock in the gain with a benchmark.",
),

P("Concept", "Which innocent-looking Python idioms are secretly quadratic or slow?",
short="""`x in list` inside a loop (use a set), building strings with `+=` in a loop (use `''.join`), `list.pop(0)` or `insert(0, x)` in a loop (use `deque`), repeated `sorted()` or `max()` inside a loop, `sum(lists, [])` for flattening, re-compiling or re-reading inside a loop, and per-row database round trips. Each turns O(n) work into O(n²) or adds huge constant costs.""",
deep="""These show up constantly in code reviews of automation and data scripts:

- **Membership in a list**: O(n) per test. Converting once to `set`/`dict` makes it O(1).
- **String accumulation**: `s += part` can copy the string each time; `''.join(parts)` is linear.
- **Queue from a list**: `pop(0)` shifts all elements; `collections.deque.popleft()` is O(1).
- **Flattening with `sum(list_of_lists, [])`**: creates a new list per addition, quadratic; use `itertools.chain.from_iterable`.
- **Sorting inside loops**: keep a heap (`heapq`) or `bisect.insort`, or sort once.
- **N+1 I/O**: one DB query or HTTP call per item; batch them (`executemany`, bulk APIs, `IN (...)` queries).
- **Exceptions as control flow in hot loops**: raising is relatively expensive when failures are common.""",
code=r'''
import timeit, itertools
from collections import deque

n = 20_000
lists = [[i] * 3 for i in range(3000)]
cases = {
    "sum(lists, [])        ": lambda: sum(lists, []),
    "chain.from_iterable   ": lambda: list(itertools.chain.from_iterable(lists)),
    "list.pop(0) drain     ": lambda: (lambda q: [q.pop(0) for _ in range(len(q))])(list(range(n))),
    "deque.popleft() drain ": lambda: (lambda q: [q.popleft() for _ in range(len(q))])(deque(range(n))),
}
for name, fn in cases.items():
    print(f"{name} {min(timeit.repeat(fn, number=3, repeat=3)) / 3 * 1000:8.1f} ms")
''',
follow=(
"How would you catch these automatically? => Code review checklists, Ruff rules (e.g. PERF rules), benchmarks in CI on realistic input sizes, and profiling tests that fail if runtime exceeds a budget.",
"When is a list membership test fine? => When the list is tiny (a handful of items) or the test runs once; building a set has its own cost.",
),
pitfall="Testing with 100 records during development, where quadratic code is instant, then shipping it to data with a million records.",
signals="You list several concrete patterns with the complexity involved and the fix, and mention batching I/O, not just in-memory tricks.",
),

P("Design", "When would you move a hot path out of pure Python, and what are the options?",
short="""Only after profiling shows a CPU-bound core that algorithmic fixes can't solve. Options, from cheapest: use C-implemented stdlib/builtins; vectorize with NumPy/Polars/Arrow; JIT with Numba for numeric loops; compile with Cython or mypyc; write an extension in Rust (PyO3/maturin) or C/C++ (pybind11, nanobind); or run it in a separate native service. Weigh speed-up against build complexity, packaging, debugging and team skills.""",
deep="""Decision factors a Principal should discuss:

- **Shape of the work**: array math (vectorize or Numba); string/byte parsing and state machines (Rust or Cython); calling an existing C/C++ library (bindings via pybind11/nanobind, or `ctypes`/`cffi` for simple C APIs).
- **Boundary cost**: crossing Python/native per element is expensive. Design the API to hand over whole buffers or batches (`bytes`, `memoryview`, NumPy arrays) and do the loop natively.
- **GIL**: native code can release the GIL for true parallelism across threads.
- **Distribution**: native code needs wheels for every platform and Python version (cibuildwheel), which is significant CI work for an internal tool.
- **Maintainability**: who can debug a segfault in the extension at 2 a.m.? Rust reduces memory-safety risks compared to C.
- **Stepping stone**: first make sure you're using C-backed builtins well; a surprising amount of speed comes from `bytes.translate`, `re`, `struct.iter_unpack`, `collections.Counter` and `sorted` with keys.""",
code=r'''
import struct, time, os

# 1 million 16-byte records: (lba: u64, crc: u32, flags: u32), little-endian
raw = os.urandom(16 * 1_000_000)
# Question: how many records have the "error" bit (bit 0 of flags) set?

t = time.perf_counter()
slow = sum(1 for off in range(0, len(raw), 16) if struct.unpack_from("<QII", raw, off)[2] & 1)
t1 = time.perf_counter() - t

t = time.perf_counter()
low_flag_bytes = raw[12::16]                          # strided slice: done in C
odd = bytes(i & 1 for i in range(256))                # lookup table: byte -> 0/1
fast = low_flag_bytes.translate(odd).count(1)         # translate + count: done in C
t2 = time.perf_counter() - t

print(f"per-record Python loop: {t1:.3f}s | C-level slice+translate: {t2:.4f}s | x{t1 / t2:.0f} faster | equal: {slow == fast}")
''',
follow=(
"Why might a Rust extension be slower than expected? => Converting Python objects element by element across the boundary; pass a buffer or batch instead and return compact results.",
"How do you ship a native extension to 40 lab machines with mixed OSes? => Build wheels for each platform/Python combination in CI (cibuildwheel, maturin), publish to an internal package index, pin versions in the framework's lock file.",
),
pitfall="Wrapping a per-item native function and calling it a million times from a Python loop. The call overhead eats most of the gain.",
signals="You start from profiling, pick the option by workload shape, design coarse-grained boundaries, and weigh packaging and maintenance cost.",
),

P("Trap", "What can go wrong with `functools.lru_cache`, especially on methods?",
short="""On a method, the cache keys include `self`, so the cache keeps **every instance alive** for the cache's lifetime (a memory leak) and is shared across all instances. Also: arguments must be hashable, cached mutable return values can be modified by callers, `maxsize=None` grows forever, and the cache ignores changes to external state it depends on.""",
deep="""Details:

- **Method caching leak**: `@lru_cache` on `def get(self, x)` stores `(self, x)` keys in a function-level cache. Instances never get garbage-collected until evicted. Fix: `functools.cached_property` for zero-argument computed attributes, a per-instance cache dict, or `lru_cache` on a module-level function taking only hashable, lightweight arguments.
- **Mutable results**: returning a list from a cached function and letting callers `.append` to it corrupts the cache for everyone. Return tuples/frozen objects or copies.
- **Staleness**: the cache has no notion of time or invalidation beyond `cache_clear()`. For data that changes, use a TTL cache and design explicit invalidation.
- **Unbounded growth**: `@cache` / `maxsize=None` on functions called with many distinct arguments (like per-request IDs) grows forever.
- **Thread safety**: the cache itself is thread-safe, but two threads may compute the same value concurrently on a miss (no single-flight).""",
code=r'''
import gc, functools, weakref

class Device:
    def __init__(self, serial): self.serial = serial
    @functools.lru_cache(maxsize=None)
    def firmware_info(self, field):             # BAD: cache holds `self`
        return f"{self.serial}:{field}"

probes = []
for i in range(1000):
    d = Device(f"SN{i}")
    d.firmware_info("version")
    probes.append(weakref.ref(d))
del d; gc.collect()
print("Device objects still alive:", sum(p() is not None for p in probes), "/ 1000")

@functools.lru_cache
def default_config():
    return {"retries": 3}                       # mutable return value
cfg = default_config(); cfg["retries"] = 99     # a caller mutates it...
print("next caller sees:", default_config())    # ...and poisons everyone else
''',
follow=(
"How would you cache an expensive per-instance computation correctly? => `functools.cached_property` for zero-argument values (stored in the instance, freed with it), or a per-instance dict or `WeakKeyDictionary` keyed by instance.",
"How do you cache results that expire? => A TTL cache (`cachetools.TTLCache` or a small dict of timestamps) with an explicit invalidation path when the source data changes.",
),
pitfall="Adding `@lru_cache` to a method to speed up a test framework and later discovering thousands of device/session objects kept alive for the whole run.",
signals="You explain the `self`-in-key leak and the mutable-return hazard, offer correct alternatives, and consider staleness and growth.",
),

P("Trap", "How do people fool themselves with micro-benchmarks in Python, and how do you benchmark properly?",
short="""Common mistakes: timing a single run, benchmarking unrealistic input sizes, including setup or I/O in the measurement, ignoring warm-up, CPU frequency scaling and noisy machines, comparing results across Python versions, and reporting means instead of minimums/distributions. Use `timeit`/`pyperf` with repeats, realistic data, isolated runs, and confirm with a profile of the real workload.""",
deep="""Guidelines:

- Use `timeit.repeat` (or `pyperf`, which spawns worker processes, calibrates loops and reports mean plus standard deviation). Look at the **minimum** for "how fast can this code be" and the distribution for variance.
- Separate setup from the measured statement (`timeit` `setup=` argument).
- Use realistic sizes: algorithmic differences only show at scale.
- Warm up: the specializing interpreter and CPU caches change timings after the first iterations.
- Control the environment: plugged-in laptop, no other heavy processes, fixed CPU frequency on benchmark machines, same Python build.
- Beware of dead-code effects: if the result is never used, confirm the work actually happens.
- Micro-benchmarks answer narrow questions; always validate with the end-to-end benchmark, since a 3x faster function that is 1% of runtime doesn't matter (Amdahl's law).""",
code=r'''
import timeit, statistics

setup = "data = list(range(10_000))"
stmts = {"loop append": "out = []\nfor x in data: out.append(x * 2)",
         "comprehension": "[x * 2 for x in data]",
         "map + lambda": "list(map(lambda x: x * 2, data))"}
for name, stmt in stmts.items():
    runs = timeit.repeat(stmt, setup=setup, number=200, repeat=7)
    per = [r / 200 * 1e6 for r in runs]
    print(f"{name:14} min {min(per):7.1f} us | median {statistics.median(per):7.1f} us | stdev {statistics.stdev(per):5.1f}")
''',
follow=(
"The comprehension is 20% faster in your benchmark. Should you rewrite 300 loops? => Only in measured hot paths; elsewhere readability wins and the end-to-end gain would be negligible.",
"How do you prevent performance regressions over time? => Keep macro benchmarks on realistic data in CI (pyperf or pytest-benchmark), store results, and alert on significant regressions rather than on noise.",
),
pitfall="Posting a single `time.time()` difference from a laptop in a design discussion as proof one approach is faster.",
signals="You list the traps, use repeats and distributions, separate setup, and connect micro results to end-to-end impact.",
),

P("Design", "A Python CLI in your test framework is invoked 20,000 times per CI run and each invocation takes 1.2 s to start. How do you fix it?",
short="""Measure imports with `python -X importtime`, then remove import-time work: lazy-import heavy modules inside the commands that need them, avoid work at module top level (config loading, network calls, regex compiles of huge tables), and trim dependencies. Structurally, avoid 20,000 processes: run the tool once as a long-lived service or batch mode, or call it as a library from the test process.""",
deep="""Steps:

1. **Measure**: `python -X importtime -c "import mytool.cli" 2> imports.log` shows self and cumulative microseconds per module. Tuna can visualize it.
2. **Common culprits**: importing pandas/NumPy/requests or a large SDK at the top of a CLI that only needs them for one sub-command; plugin discovery scanning all entry points; reading and validating big config files at import; `pkg_resources` (slow, deprecated).
3. **Fixes**: move imports into functions; module-level `__getattr__` (PEP 562) for lazy attributes; cache discovered plugins; use `importlib.metadata` instead of `pkg_resources`; precompile `.pyc` (`compileall`) on read-only installs.
4. **Architecture**: the real win is often not starting Python 20,000 times. Offer a `--batch` mode reading many commands from stdin, a persistent daemon, or a library API the test framework calls directly.

Quantify: 20,000 x 1.2 s = 6.7 hours of CPU per CI run; reducing to 0.15 s saves more than 5.8 hours.""",
code=r'''
import subprocess, sys

def import_cost(module):
    r = subprocess.run([sys.executable, "-X", "importtime", "-c", f"import {module}"],
                       capture_output=True, text=True)
    rows = [l.split("|") for l in r.stderr.splitlines() if l.startswith("import time:") and "|" in l]
    top = [r for r in rows if r[2].strip() == module]
    return int(top[-1][1]) if top else None                     # cumulative microseconds

for m in ("json", "asyncio", "email.mime.multipart", "unittest.mock"):
    print(f"{m:22} {import_cost(m) / 1000:6.1f} ms cumulative import time")
print(f"x 20,000 invocations of asyncio import alone = {import_cost('asyncio') * 20_000 / 1e6 / 60:.1f} CPU-minutes")
''',
follow=(
"How do you stop regressions after you fix it? => A CI check that runs `python -X importtime` on the CLI entry point and fails if cumulative import time exceeds a budget, or a test asserting heavy modules aren't in `sys.modules` after importing the CLI.",
"Is lazy importing always good? => It moves cost to first use and can hide import errors until runtime; keep it for heavy optional dependencies and test those code paths explicitly.",
),
pitfall="Micro-optimizing the CLI's logic when 95% of its runtime is interpreter startup plus imports.",
signals="You measure imports, name typical culprits and fixes, and step back to the architectural fix of not spawning thousands of processes, with a quantified saving.",
),

P("Concept", "How do you process large binary buffers without copying them? Explain `memoryview` and the buffer protocol.",
short="""The buffer protocol lets objects like `bytes`, `bytearray`, `array`, `mmap` and NumPy arrays expose their raw memory. A `memoryview` is a view over that memory: slicing it creates another view, not a copy, and APIs such as `struct.unpack_from`, `socket.recv_into`, `file.readinto` and `hashlib.update` accept it. This avoids megabytes of copies when parsing or checksumming device data.""",
deep="""Why it matters: slicing `bytes` (`data[4096:8192]`) allocates and copies. In a loop over a 1 GB capture that's a gigabyte of extra copying.

Tools:

- `memoryview(buf)[a:b]`: zero-copy slice; `.cast("I")` reinterprets as unsigned ints; `.release()` or a `with` block frees the export so the underlying `bytearray` can be resized again.
- Read directly into preallocated buffers: `f.readinto(buf)`, `sock.recv_into(view)`.
- `struct.unpack_from(fmt, buf, offset)` reads at an offset without slicing.
- `mmap` gives a buffer backed by the file; combine with `memoryview` for random access to huge files.

Caveats: a `bytearray` with active exports can't be resized; views keep the underlying object alive; endianness and alignment are your responsibility.""",
code=r'''
import os, time, zlib

sector = 4096
buf = bytearray(os.urandom(sector * 16_384))      # 64 MiB "disk image"

t = time.perf_counter()
crc_copy = [zlib.crc32(buf[i:i + sector]) for i in range(0, len(buf), sector)]   # copies each slice
t_copy = time.perf_counter() - t

view = memoryview(buf)
t = time.perf_counter()
crc_view = [zlib.crc32(view[i:i + sector]) for i in range(0, len(buf), sector)]  # zero-copy slices
t_view = time.perf_counter() - t

print(f"slicing bytearray: {t_copy:.3f}s | memoryview: {t_view:.3f}s | identical CRCs: {crc_copy == crc_view}")
ints = view[:16].cast("I")
print("first 4 little/native u32 words:", [hex(x) for x in ints])
view.release()
''',
follow=(
"Why might `buf.extend(...)` raise `BufferError` after creating a memoryview? => The bytearray can't be resized while a view exports its memory; release the view first (`view.release()` or `with memoryview(buf) as v:`).",
"How do you read a 1 GB file in 1 MiB blocks without allocating a new bytes object per read? => Preallocate a `bytearray(1 << 20)` and loop with `n = f.readinto(buf)`, processing `memoryview(buf)[:n]`.",
),
pitfall="Assuming `bytes` slicing is free because it \"looks like indexing\". Each slice is a new object and a memory copy.",
signals="You explain the buffer protocol, show zero-copy slicing with measured benefit, and mention readinto/recv_into and the resize caveat.",
),

]
