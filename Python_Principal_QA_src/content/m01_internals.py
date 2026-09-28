MODULE = dict(id=1, title="CPython Internals & Execution Model",
              desc="What really happens between source and result: compilation, the eval loop, the specializing interpreter, the GIL, free-threading and subinterpreters.")

QUESTIONS = [

P("Concept", "Walk me through what CPython does when you run `python app.py`.",
short="""The source is tokenized and parsed (PEG parser) into an AST, a symbol table decides which names are local, global or closure cells, and the compiler emits **bytecode** in code objects. The interpreter's eval loop then executes that bytecode frame by frame. Imported modules go through the same steps once, and their bytecode is cached as `.pyc` in `__pycache__`.""",
deep="""The pipeline has five stages, and knowing them explains many everyday behaviours:

1. **Tokenize and parse**: the PEG parser (3.9+) builds an AST. Syntax errors come from here, which is why they are raised before any code runs.
2. **Symbol table**: for each scope the compiler decides whether a name is local, global, free (closure) or cell. That is why assigning to a name *anywhere* in a function makes it local everywhere in that function (the classic `UnboundLocalError`).
3. **Compile**: the AST becomes code objects (`co_code`, `co_consts`, `co_varnames`, ...). Constant folding happens here (`24 * 60 * 60` becomes `86400`).
4. **Execute**: the eval loop (`_PyEval_EvalFrameDefault`) runs instructions on a per-call **frame**. Since 3.11 frames are lightweight and allocated on a per-thread data stack; full frame objects are only materialized when something (a traceback, `sys._getframe`) needs them.
5. **Import caching**: `import x` compiles `x.py` once, writes `__pycache__/x.cpython-314.pyc`, and later runs reuse it when the source timestamp or hash still matches. The main script itself is never cached.

At Principal level, connect this to consequences: startup time is dominated by imports; per-call overhead is frame setup; and CPython 3.11+ got 10-60% faster largely by making frames cheaper and specializing bytecode.""",
code=r'''
import ast, dis

src = "def area(r):\n    seconds = 24 * 60 * 60\n    return 3.14159 * r * r\n"
tree = ast.parse(src)
print("AST root:", type(tree).__name__, "->", type(tree.body[0]).__name__)

code = compile(tree, "<demo>", "exec")
fn_code = code.co_consts[0]
print("function code object:", fn_code.co_name, "| locals:", fn_code.co_varnames)
print("constants (note folding of 24*60*60):", fn_code.co_consts)
dis.dis(fn_code)
''',
follow=(
"Why is a syntax error in one branch of a function reported even if that branch never runs? => Because parsing and compilation happen for the whole module before execution starts; the eval loop never sees invalid code.",
"What invalidates a `.pyc`? => By default the source file's mtime and size recorded in the `.pyc` header; with hash-based pycs (PEP 552, used for reproducible builds) the source hash. Different Python versions use different file names (`cpython-314`), so they never collide.",
"Where does time go when a CLI takes 2 seconds to print `--help`? => Almost always imports: module execution at import time plus disk I/O. Measure with `python -X importtime` before optimizing anything else.",
),
pitfall="Saying Python is \"interpreted, not compiled\". CPython compiles to bytecode every time; the distinction that matters is ahead-of-time machine code (no) versus bytecode run by a VM (yes), with an experimental JIT since 3.13.",
signals="You describe the stages in order, tie at least one of them to a practical consequence (UnboundLocalError, import-time cost, constant folding), and know which version introduced the relevant change.",
),

P("Concept", "What is the specializing adaptive interpreter (PEP 659), and how can code make it faster or slower?",
short="""Since 3.11, CPython rewrites hot bytecode instructions in place into **specialized** versions for the types it actually observes (e.g. `BINARY_OP` becomes `BINARY_OP_ADD_INT`, `LOAD_ATTR` becomes `LOAD_ATTR_INSTANCE_VALUE`), using inline caches. If the assumption breaks, the instruction de-optimizes. Type-stable ("monomorphic") code benefits most.""",
deep="""After an instruction runs a few times ("warm-up"), the interpreter replaces it with a specialized variant that skips generic dispatch: integer addition without the full number protocol, attribute loads that jump straight to a known slot, global loads guarded by a dict version, calls to Python functions without building a new C frame.

Each specialized instruction has **guards**. When a guard fails repeatedly (a different type shows up), the instruction goes back to the adaptive form and may re-specialize later.

What this means in practice:

- Keep hot loops **type-stable**: mixing `int` and `float`, or passing many different classes through the same line, reduces specialization.
- Avoid changing class attributes or module globals inside hot paths; version tags invalidate caches.
- Consistent object shapes (set all attributes in `__init__`, or use `__slots__`) help attribute specialization.
- This is also the foundation the experimental JIT (3.13+, `PYTHON_JIT=1` builds) compiles from.

Tooling: `dis.dis(fn, adaptive=True)` shows the specialized instructions after warm-up.""",
code=r'''
import dis

def total(values):
    s = 0
    for v in values:
        s = s + v
    return s

for _ in range(50):                    # warm up with ints only
    total(list(range(100)))

ops = [i.opname for i in dis.get_instructions(total, adaptive=True)]
print("specialized:", sorted({o for o in ops if "_" in o and o.startswith(("BINARY_OP", "FOR_ITER", "LOAD_FAST", "STORE_FAST"))}))
''',
follow=(
"Why might a function slow down after refactoring to accept both `int` and `Decimal`? => The same `BINARY_OP` now sees two types; specialization for `int` fails its guard and the instruction de-optimizes to the generic path.",
"Does this make Python as fast as a JIT-compiled language? => No. It removes dispatch overhead per instruction (roughly 1.25x average on pyperformance for 3.11), but values are still boxed objects. For numeric hot loops, vectorize (NumPy) or move to compiled code.",
),
pitfall="Micro-optimizing by hand (caching methods in locals, etc.) based on advice written for Python 3.7. Many of those tricks matter much less now; always measure on the version you run.",
signals="You can name concrete specialized instructions, explain guards and de-optimization, and translate that into coding guidance (type stability, consistent object shapes) rather than folklore.",
),

P("Concept", "How does the GIL actually hand control between threads, and which work truly runs in parallel?",
short="""A thread holding the GIL runs until it blocks on I/O or until another thread has waited for the **switch interval** (5 ms by default, `sys.getswitchinterval()`); the waiting thread sets an "eval breaker" flag and the running thread drops the GIL at the next check. C code that releases the GIL (I/O, `hashlib` on large buffers, `zlib`, NumPy kernels) runs truly in parallel.""",
deep="""Mechanics (since the "new GIL" in 3.2):

- A thread that wants the GIL waits on a condition variable with a timeout equal to the switch interval.
- On timeout it sets a **drop request**; the running thread checks the eval breaker between bytecode instructions (at specific points like backward jumps and calls) and releases the GIL.
- The OS decides which waiting thread wins next, so fairness is not guaranteed.

Consequences you should mention:

- Pure-Python CPU work gets no speed-up from threads, and can even slow down because of lock hand-offs (the "convoy effect" when an I/O thread must reacquire the GIL behind a CPU thread).
- Blocking I/O releases the GIL, so threads are fine for sockets, files and subprocess waits.
- C extensions that wrap long computations in `Py_BEGIN_ALLOW_THREADS` run in parallel: `hashlib` releases the GIL for data larger than about 2 KiB, `zlib` for compression, and NumPy for most kernels. Many "Python is slow at X" arguments disappear when the heavy lifting is in such code.
- `sys.setswitchinterval()` trades latency for throughput, but it's rarely the right knob.""",
code=r'''
import hashlib, os, sys, time
from concurrent.futures import ThreadPoolExecutor

print("switch interval:", sys.getswitchinterval(), "s")
blocks = [os.urandom(40 * 1024 * 1024) for _ in range(4)]          # 4 x 40 MB

def digest(b): return hashlib.sha256(b).hexdigest()[:8]
def py_work(b): return sum(i * i for i in range(1_500_000))       # pure Python loop, holds the GIL

for name, fn in (("hashlib (releases GIL)", digest), ("pure Python", py_work)):
    t = time.perf_counter(); [fn(b) for b in blocks]; serial = time.perf_counter() - t
    t = time.perf_counter()
    with ThreadPoolExecutor(4) as ex: list(ex.map(fn, blocks))
    par = time.perf_counter() - t
    print(f"{name:24} serial {serial:.2f}s  4 threads {par:.2f}s  speed-up x{serial / par:.1f}")
''',
follow=(
"A service has one CPU-heavy thread and many I/O threads, and I/O latency is terrible. Why? => Convoy effect: every time an I/O thread wakes it must wait up to a switch interval for the CPU thread to drop the GIL. Move the CPU work to a process pool or a GIL-releasing library.",
"How would you check whether a C extension releases the GIL? => Read its source for `Py_BEGIN_ALLOW_THREADS`, or measure: run the call in N threads and compare wall time with serial, as in the example.",
),
pitfall="Claiming \"threads are useless in Python\". They are the right tool for blocking I/O and for C-level work that releases the GIL; they are only useless for pure-Python CPU loops.",
signals="You explain the drop-request mechanism, give examples of GIL-releasing libraries, and back the claim with a measurement instead of an assertion.",
),

P("Design", "Python 3.14 officially supports the free-threaded (no-GIL) build. Would you move your organization's test infrastructure to it? How?",
short="""Not wholesale. I'd adopt it where there's a measured benefit: CPU-bound work that is currently forced into multiprocessing because of the GIL. First verify that every C extension we use supports free-threading, accept about 5-10% single-thread overhead, fix code that relied on the GIL for correctness, and roll out behind a separate interpreter build in CI before production.""",
deep="""**Why it could help**: tasks like verifying data patterns, parsing large logs or computing statistics across devices could use threads instead of processes, avoiding pickling costs and memory duplication.

**Costs and risks to evaluate:**

- **Single-thread performance**: the free-threaded build is slower for single-threaded code (the 3.14 target is roughly 5-10% overhead) because of biased reference counting and per-object locks.
- **C extensions**: a module must declare support (`Py_mod_gil`); importing one that doesn't **re-enables the GIL** for the process (with a warning), silently removing the benefit. Check `sys._is_gil_enabled()` at startup.
- **Hidden races**: built-in containers stay internally consistent (per-object locks), but compound operations like `d[k] = d.get(k, 0) + 1` or check-then-act were never atomic; the GIL just made races rare. Expect latent bugs to surface.
- **Tooling**: profilers, debuggers and some pip wheels (`cp314t` tags) may lag.

**Rollout plan:**

1. Inventory dependencies and their free-threading status; build a compatibility matrix.
2. Add a CI job on `python3.14t` running the framework's unit tests with thread-sanitizing stress tests.
3. Pick one CPU-bound workload, benchmark GIL vs no-GIL vs multiprocessing on real data.
4. Ship it for that workload only, with `sys._is_gil_enabled()` asserted and metrics on throughput.
5. Expand based on data; keep the default build for everything else.""",
code=r'''
import sys, sysconfig

free_threaded_build = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))
gil_active = sys._is_gil_enabled() if hasattr(sys, "_is_gil_enabled") else True
print(f"free-threaded build: {free_threaded_build} | GIL currently enabled: {gil_active}")

# A check-then-act that is NOT atomic even though dict operations are thread-safe:
counts = {}
def record(key):
    counts[key] = counts.get(key, 0) + 1      # read + write: two operations, can race
# Safe alternatives: a threading.Lock around it, collections.Counter per thread merged later,
# or queue-based aggregation in a single consumer thread.
print("record() is only safe under a lock or single-writer design")
''',
follow=(
"How do you guarantee the GIL didn't silently come back in production? => Log and assert `sys._is_gil_enabled()` after all imports at startup, and export it as a metric; also run with `-X gil=0` / `PYTHON_GIL=0` only after confirming extensions are compatible.",
"Wouldn't subinterpreters be a safer route to parallelism? => For isolated tasks, yes: `concurrent.interpreters` (3.14) gives each interpreter its own GIL with no shared objects, so existing code has fewer race risks, at the cost of explicit data passing.",
),
pitfall="Assuming code is thread-safe because \"it worked under the GIL\". The GIL protected interpreter internals, never your application's invariants.",
signals="You balance benefit against measured costs, mention extension compatibility and the silent GIL re-enable, and give a staged rollout with a success metric.",
),

P("Trap", "Is `counter += 1` thread-safe in CPython? Is `list.append`? Prove it.",
short="""`list.append(x)` is a single C-level operation, so it's atomic with the GIL (and protected by a per-object lock in free-threaded builds). `counter += 1` compiles to separate load, add and store instructions, so a thread switch between them loses updates. Never rely on it; use a `Lock` or a single-writer design.""",
deep="""`dis` makes the difference visible: `counter += 1` on a global is `LOAD_GLOBAL`, `LOAD_SMALL_INT`/`LOAD_CONST`, `BINARY_OP (+=)`, `STORE_GLOBAL`. The GIL can be dropped between any two of those.

Operations that are effectively atomic today (single bytecode calling one C function on a built-in type): `list.append`, `list.pop`, `dict[k] = v`, `dict.setdefault`, `deque.append/popleft`. Operations that are not: `+=` on anything shared, `if k not in d: d[k] = ...`, `lst[i] = lst[i] + 1`, iterating a dict while another thread mutates it.

Even the "atomic" list is only a documented implementation property of CPython, not a language guarantee. A Principal answer: design so correctness doesn't depend on it (locks, `queue.Queue`, per-thread accumulation then merge).""",
code=r'''
import dis, threading, time

counter = 0
def unsafe_inc():
    global counter
    counter += 1

print([i.opname for i in dis.get_instructions(unsafe_inc) if i.opname not in ("RESUME", "RETURN_CONST", "RETURN_VALUE", "LOAD_CONST")])

# Force the race to show up by yielding between read and write
counter = 0
def worker():
    global counter
    for _ in range(2000):
        tmp = counter
        time.sleep(0)            # a thread switch here is always possible
        counter = tmp + 1
ts = [threading.Thread(target=worker) for _ in range(4)]
[t.start() for t in ts]; [t.join() for t in ts]
print("counter:", counter, "expected 8000")

items = []
def appender():
    for i in range(20000): items.append(i)
ts = [threading.Thread(target=appender) for _ in range(4)]
[t.start() for t in ts]; [t.join() for t in ts]
print("list.append items:", len(items), "expected 80000")
''',
follow=(
"Is `x = y` (a simple assignment) atomic? => Rebinding a name is a single store, so readers see either the old or new object, never a torn value. But the combination read-modify-write still isn't.",
"How do you aggregate counters from many threads without a lock per increment? => Give each thread its own `Counter` and merge at the end, or send events through a `queue.Queue` to a single aggregator thread.",
),
pitfall="Answering \"yes, because of the GIL\". The GIL makes individual bytecodes atomic, not Python statements.",
signals="You show the bytecode, distinguish single C calls from compound statements, and propose designs that don't depend on implementation details.",
),

P("Concept", "Why is local variable access faster than global access, and does that still matter?",
short="""Locals live in a fixed array in the frame and are read with `LOAD_FAST` (an index). Globals and builtins need dictionary lookups (`LOAD_GLOBAL`), although 3.11+ caches them with dict version guards. In modern CPython the gap is small; it only matters in very hot loops, and algorithmic changes matter far more.""",
deep="""The compiler knows every local name at compile time, so it assigns each a slot index (`co_varnames`). `LOAD_FAST 3` is one array read. Names not local are resolved at runtime: first the module globals dict, then builtins. Since 3.11 the specializing interpreter turns `LOAD_GLOBAL` into `LOAD_GLOBAL_MODULE`/`LOAD_GLOBAL_BUILTIN`, which checks a dict **version tag** and reads a cached index, so repeated global access is much cheaper than it used to be.

Closures use **cell** objects: `co_cellvars` in the outer function and `co_freevars` in the inner one, accessed with `LOAD_DEREF`, which adds one indirection.

Practical guidance: aliasing a global function to a local (`append = out.append`) used to give 10-30% in tight loops; on 3.12+ it's often in the single digits. Mention it only as a last-mile optimization after profiling.""",
code=r'''
import math, timeit

def use_global(n=200_000):
    s = 0.0
    for i in range(n):
        s += math.sqrt(i)
    return s

def use_local(n=200_000):
    s, sqrt = 0.0, math.sqrt
    for i in range(n):
        s += sqrt(i)
    return s

for f in (use_global, use_local):
    print(f"{f.__name__:10} {min(timeit.repeat(f, number=5, repeat=5)) / 5 * 1000:.1f} ms")
print("locals:", use_local.__code__.co_varnames)
''',
follow=(
"What does `LOAD_DEREF` indicate in `dis` output? => A read of a closure variable through a cell object: the variable is shared between an outer function and an inner function.",
"Why can't you add a local variable with `locals()['x'] = 1` inside a function? => Locals are array slots fixed at compile time; `locals()` returns a snapshot (3.13's PEP 667 made its semantics well-defined), so writes don't create new fast locals.",
),
pitfall="Presenting local-aliasing as a key optimization. On current CPython the benefit is small; profiling usually points to I/O, algorithms or data structures instead.",
signals="You explain slots vs dict lookups, know that 3.11+ specialization narrowed the gap, and quantify with a measurement.",
),

P("Concept", "Compare threads, processes and subinterpreters (PEP 734) for parallel work in Python 3.14.",
short="""Threads share everything and are limited by the GIL for Python code. Processes have separate memory and GILs, true parallelism, but pay for pickling and memory duplication. **Subinterpreters** (`concurrent.interpreters`, `InterpreterPoolExecutor` in 3.14) run in one process, each with its own GIL and isolated objects: parallel like processes, cheaper to start, but data must be passed explicitly and extension modules must support them.""",
deep="""Comparison:

- **Isolation**: threads share all objects (races possible); processes and subinterpreters share nothing by default.
- **Parallel Python bytecode**: threads no (unless free-threaded build); processes yes; subinterpreters yes (per-interpreter GIL since 3.12).
- **Startup and memory**: threads cheapest; subinterpreters much cheaper than spawning processes; processes most expensive (a whole interpreter plus imports per worker).
- **Data exchange**: threads by reference; processes by pickling over pipes; subinterpreters by pickling or through shareable types and `concurrent.interpreters` queues.
- **Compatibility**: subinterpreters need extension modules that support multi-phase init and per-interpreter state; many popular C extensions are still catching up.

Rule of thumb for a Principal answer: I/O-bound, use threads or asyncio; CPU-bound with heavy dependencies, use processes; CPU-bound pure-Python or stdlib work with strict isolation, consider subinterpreters and benchmark.""",
code=r'''
from concurrent.futures import InterpreterPoolExecutor, ProcessPoolExecutor, ThreadPoolExecutor
import time

JOBS = [range(40_000_000)] * 8          # sum(range) runs in C but HOLDS the GIL

def bench(executor_cls):
    t = time.perf_counter()
    with executor_cls(max_workers=4) as ex:
        results = list(ex.map(sum, JOBS))
    return time.perf_counter() - t

if __name__ == "__main__":
    t = time.perf_counter(); [sum(r) for r in JOBS]
    print(f"{'serial':24} {(time.perf_counter() - t) * 1000:5.0f} ms")
    for cls in (ThreadPoolExecutor, InterpreterPoolExecutor, ProcessPoolExecutor):
        print(f"{cls.__name__:24} {bench(cls) * 1000:5.0f} ms  (4 workers, includes startup)")
''',
follow=(
"When would subinterpreters beat processes? => Many short-lived isolated tasks where process startup and memory per worker dominate, and the libraries involved support subinterpreters.",
"Why can't you just pass a live database connection to another interpreter? => Objects are not shared between interpreters; you pass data (pickled or shareable types) and each interpreter opens its own resources.",
),
pitfall="Treating subinterpreters as a drop-in replacement for threads. They isolate state, so code that relies on shared module-level objects must be redesigned.",
signals="You compare isolation, parallelism, startup cost, data passing and compatibility, and end with a clear decision rule plus \"benchmark it\".",
),

]
