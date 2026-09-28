QUESTIONS = [

# =============== 9. ITERATORS, GENERATORS & COMPREHENSIONS ===============
Q(9, "Easy", "What is the difference between an iterable and an iterator?",
"""An **iterable** can produce an iterator via `iter()` (it has `__iter__`): lists, dicts, strings, files. An **iterator** has `__next__`, remembers its position, and is exhausted after one pass; its `__iter__` returns itself.""",
r'''
nums = [1, 2, 3]
it = iter(nums)
print(next(it), next(it), list(it), list(it))    # exhausted
print(list(nums), list(nums))                     # iterable: fresh iterator each time
'''),

Q(9, "Easy", "What is a list comprehension?",
"""A concise expression that builds a list: `[expr for x in iterable if condition]`. It is usually faster and clearer than an equivalent loop with `append`. Comprehensions have their own scope, so the loop variable doesn't leak.""",
r'''
prices = [120, 45, 300, 80]
with_tax = [round(p * 1.18, 1) for p in prices if p > 50]
print(with_tax)
matrix = [[r * 3 + c for c in range(3)] for r in range(3)]
print(matrix, [row[i] for i, row in enumerate(matrix)])
'''),

Q(9, "Easy", "What are dict and set comprehensions?",
"""Same syntax with braces: `{k: v for ...}` builds a dict, `{x for ...}` builds a set.""",
r'''
words = ["apple", "Banana", "cherry", "avocado"]
print({w: len(w) for w in words})
print({w[0].lower() for w in words})
inventory = {"pen": 0, "ink": 5, "pad": 2}
print({k: v for k, v in inventory.items() if v})
'''),

Q(9, "Moderate", "What is a generator?",
"""A function containing `yield`. Calling it returns a generator object (an iterator) without running the body; each `next()` runs until the next `yield`, pausing with local state intact. Generators are lazy and memory-efficient.""",
r'''
def countdown(n):
    print("start")
    while n > 0:
        yield n
        n -= 1
    print("done")
g = countdown(3)
print(type(g).__name__)
print(next(g)); print(list(g))
'''),

Q(9, "Moderate", "Generator expression vs list comprehension?",
"""`(x for x in ...)` is lazy: it produces items on demand and uses constant memory. `[x for x in ...]` builds the whole list immediately. Use generator expressions for aggregations (`sum`, `any`, `max`) or one-pass streaming.""",
r'''
import sys
lst = [x * x for x in range(1_000_000)]
gen = (x * x for x in range(1_000_000))
print(sys.getsizeof(lst), sys.getsizeof(gen))
print(sum(x * x for x in range(1_000_000)))
'''),

Q(9, "Moderate", "What does `yield from` do?",
"""It delegates to a sub-iterator: yields all its values (and forwards `send()`/`throw()`), and evaluates to the sub-generator's return value. It simplifies recursive generators and generator composition.""",
r'''
def read_files(*files):
    for f in files:
        yield from f.splitlines()
def walk(tree):
    yield tree["name"]
    for child in tree.get("children", []):
        yield from walk(child)
print(list(read_files("a\nb", "c")))
print(list(walk({"name": "root", "children": [{"name": "x", "children": [{"name": "y"}]}, {"name": "z"}]})))
'''),

Q(9, "Difficult", "What are `send()`, `throw()` and `close()` on generators?",
"""`gen.send(value)` resumes the generator and makes the paused `yield` expression evaluate to `value` (first call must be `send(None)` or `next`). `throw(exc)` raises inside the generator at the `yield`. `close()` raises `GeneratorExit` so `finally` blocks run.""",
r'''
def running_avg():
    total = count = 0
    avg = None
    try:
        while True:
            value = yield avg
            total += value; count += 1
            avg = total / count
    finally:
        print("cleanup")
g = running_avg(); next(g)
print(g.send(10), g.send(20), g.send(60))
g.close()
'''),

Q(9, "Moderate", "What does `enumerate` do?",
"""Wraps an iterable to yield `(index, item)` pairs, with an optional `start`. It replaces `range(len(x))` loops.""",
r'''
for i, name in enumerate(["riya", "arjun", "meera"], start=1):
    print(f"{i}. {name}")
'''),

Q(9, "Moderate", "What does `zip` do, and what happens with unequal lengths?",
"""`zip` pairs items from several iterables and stops at the **shortest**. `strict=True` (3.10+) raises `ValueError` on mismatch; `itertools.zip_longest` pads instead. `zip(*rows)` transposes.""",
r'''
from itertools import zip_longest
names, scores = ["a", "b", "c"], [90, 80]
print(list(zip(names, scores)), list(zip_longest(names, scores, fillvalue=0)))
print(list(zip(*[(1, 2, 3), (4, 5, 6)])))
try:
    list(zip(names, scores, strict=True))
except ValueError as e:
    print("ValueError:", e)
'''),

Q(9, "Moderate", "Name the most useful `itertools` functions.",
"""- Infinite: `count`, `cycle`, `repeat`
- Slicing/filtering: `islice`, `takewhile`, `dropwhile`, `filterfalse`, `compress`
- Combining: `chain`, `zip_longest`, `product`, `pairwise` (3.10), `batched` (3.12)
- Grouping/aggregating: `groupby`, `accumulate`, `tee`
- Combinatorics: `permutations`, `combinations`, `combinations_with_replacement`""",
r'''
from itertools import accumulate, pairwise, product, combinations, islice, count, batched
print(list(accumulate([5, 3, 8])), list(pairwise("abcd")))
print(list(product("AB", [1, 2])), list(combinations("abc", 2)))
print(list(islice(count(10, 5), 4)), list(batched(range(7), 3)))
'''),

Q(9, "Moderate", "What is lazy evaluation and why does it matter?",
"""Values are computed only when needed. Generators, `range`, `map`, `filter`, `zip`, dict views and file iteration are lazy. It saves memory, allows infinite sequences, and lets pipelines stop early.""",
r'''
from itertools import count
def expensive(n):
    print(f"computing {n}"); return n * n
first_big = next(x for x in map(expensive, count(1)) if x > 10)
print("result:", first_big)
'''),

Q(9, "Difficult", "Why can a generator only be iterated once, and how do you work around it?",
"""A generator is an iterator: once exhausted it stays empty. Wrap it in a class whose `__iter__` creates a new generator each time (an iterable), materialize it into a list, or use `itertools.tee` (which buffers).""",
r'''
gen = (x for x in range(3))
print(sum(gen), sum(gen))
class Squares:
    def __init__(self, n): self.n = n
    def __iter__(self): return (x * x for x in range(self.n))
s = Squares(3)
print(sum(s), sum(s))
'''),

Q(9, "Moderate", "Do comprehension loop variables leak into the enclosing scope?",
"""No (in Python 3). Comprehensions run in their own scope, so the loop variable doesn't overwrite an outer name. A plain `for` loop variable **does** remain after the loop.""",
r'''
x = "outer"
squares = [x * x for x in range(3)]
print(x)
for y in range(3): pass
print(y)
'''),

Q(9, "Moderate", "How do you read a huge file efficiently?",
"""Iterate over the file object: it yields one line at a time with buffered I/O, using constant memory. For binary data, read fixed-size chunks with `iter(lambda: f.read(size), b"")`.""",
r'''
import tempfile, os
path = os.path.join(tempfile.mkdtemp(), "big.log")
with open(path, "w") as f:
    f.writelines(f"line {i} {'ERROR' if i % 1000 == 0 else 'ok'}\n" for i in range(100_000))
with open(path) as f:
    errors = sum(1 for line in f if "ERROR" in line)
print("errors:", errors)
with open(path, "rb") as f:
    chunks = sum(1 for _ in iter(lambda: f.read(64 * 1024), b""))
print("64KB chunks:", chunks)
'''),

Q(9, "Difficult", "What happens if a generator has a `return` value?",
"""`return value` in a generator raises `StopIteration(value)`. `yield from` captures it as the expression's result; a plain `for` loop ignores it.""",
r'''
def worker():
    yield 1; yield 2
    return "summary: 2 items"
def supervisor():
    result = yield from worker()
    print("got", result)
print(list(supervisor()))
'''),

Q(9, "Moderate", "What are `any()` and `all()`, and do they short-circuit?",
"""`any(it)` is True if any item is truthy; `all(it)` is True if all are (and True for empty input). Both stop as soon as the answer is known, so pass a generator expression to avoid computing everything.""",
r'''
def check(n):
    print("checking", n); return n > 2
print(any(check(n) for n in [1, 5, 9]))
print(all([]), any([]))
'''),

Q(9, "Difficult", "What is an async generator?",
"""An `async def` function with `yield`, consumed with `async for`. It can `await` between yields, ideal for streaming paginated APIs or websocket messages.""",
r'''
import asyncio
async def fetch_pages():
    for page in range(1, 4):
        await asyncio.sleep(0.01)            # pretend network call
        yield [f"item{page}-{i}" for i in range(2)]
async def main():
    async for items in fetch_pages():
        print(items)
asyncio.run(main())
'''),

Q(9, "Moderate", "How do you implement `range`-like behaviour with a generator for floats?",
"""`range` only supports integers. Write a generator computing `start + i * step` (multiplication avoids accumulated floating-point error), or use `numpy.arange`/`linspace`.""",
r'''
def frange(start, stop, step):
    n = 0
    while (value := start + n * step) < stop:
        yield round(value, 10)
        n += 1
print(list(frange(0, 1, 0.25)), list(frange(0.1, 0.5, 0.1)))
'''),

Q(9, "Moderate", "What does `iter(callable, sentinel)` do?",
"""The two-argument form calls `callable()` repeatedly and yields results until it returns `sentinel`. Common for reading chunks until EOF or polling until a stop value.""",
r'''
import io
f = io.BytesIO(b"abcdefgh")
print(list(iter(lambda: f.read(3), b"")))
'''),

Q(9, "Difficult", "What is the difference between a nested comprehension's loop order and nested for loops?",
"""The `for` clauses appear in the **same order** as nested loops would be written (outer first). The expression comes first. Reading left to right after the expression matches the indentation order of the equivalent loops.""",
r'''
pairs = [(x, y) for x in range(2) for y in "ab" if y != "b" or x]
out = []
for x in range(2):
    for y in "ab":
        if y != "b" or x: out.append((x, y))
print(pairs, pairs == out)
'''),

# =============== 10. DECORATORS & CONTEXT MANAGERS ===============
Q(10, "Easy", "What is a decorator?",
"""A callable that takes a function (or class) and returns a replacement, usually a wrapper adding behaviour before/after the original call. `@decorator` above a `def` is shorthand for `func = decorator(func)`.""",
r'''
import functools
def log_calls(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"calling {fn.__name__}{args}")
        return fn(*args, **kwargs)
    return wrapper
@log_calls
def add(a, b): return a + b
print(add(2, 3))
'''),

Q(10, "Moderate", "Why use `functools.wraps` in decorators?",
"""Without it, the wrapper replaces the original's `__name__`, `__doc__`, `__module__`, `__qualname__` and signature. That breaks logging, documentation, debugging, pytest and frameworks that key routes by function name. `wraps` copies them and sets `__wrapped__`.""",
r'''
import functools
def plain(fn):
    def wrapper(*a, **k): return fn(*a, **k)
    return wrapper
def proper(fn):
    @functools.wraps(fn)
    def wrapper(*a, **k): return fn(*a, **k)
    return wrapper
@plain
def f():
    """Docs for f."""
@proper
def g():
    """Docs for g."""
print(f.__name__, f.__doc__, "|", g.__name__, g.__doc__, "| __wrapped__:", g.__wrapped__.__name__)
'''),

Q(10, "Moderate", "How do you write a decorator that accepts arguments?",
"""Add another layer: an outer function takes the arguments and returns the actual decorator, which takes the function and returns the wrapper.""",
r'''
import functools, time
def retry(times=3, delay=0.0, exceptions=(Exception,)):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    print(f"attempt {attempt}: {e}")
                    if attempt == times: raise
                    time.sleep(delay)
        return wrapper
    return decorator
calls = iter([ConnectionError("timeout"), ConnectionError("reset"), "OK"])
@retry(times=3, exceptions=(ConnectionError,))
def fetch():
    r = next(calls)
    if isinstance(r, Exception): raise r
    return r
print(fetch())
'''),

Q(10, "Moderate", "In what order are stacked decorators applied?",
"""Bottom-up at definition time: `@a @b def f` means `f = a(b(f))`. At call time the outermost wrapper (`a`) runs first.""",
r'''
def tag(name):
    def deco(fn):
        def wrapper(): return f"<{name}>{fn()}</{name}>"
        return wrapper
    return deco
@tag("b")
@tag("i")
def hello(): return "hi"
print(hello())
'''),

Q(10, "Moderate", "Can you decorate a class? Give an example.",
"""Yes: a class decorator receives the class and returns it (modified) or a replacement. `@dataclass`, `@functools.total_ordering` and registration decorators work this way.""",
r'''
REGISTRY = {}
def register(cls):
    REGISTRY[cls.__name__.lower()] = cls
    cls.registered = True
    return cls
@register
class CsvExporter: pass
print(REGISTRY, CsvExporter.registered)
'''),

Q(10, "Difficult", "How do you write a class-based decorator, and when is it useful?",
"""A class with `__init__(self, fn)` and `__call__`. Useful when the decorator keeps state (call counts, caches). Use `functools.update_wrapper(self, fn)` to preserve metadata. Note it won't bind as a method unless you also implement `__get__`.""",
r'''
import functools
class CountCalls:
    def __init__(self, fn):
        functools.update_wrapper(self, fn)
        self.fn, self.calls = fn, 0
    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.fn(*args, **kwargs)
@CountCalls
def ping(): return "pong"
ping(); ping()
print(ping.calls, ping.__name__)
'''),

Q(10, "Moderate", "Give real-world uses of decorators.",
"""- Frameworks: `@app.route` (Flask), `@app.get` (FastAPI), `@login_required`, `@csrf_exempt`
- Caching: `@functools.cache`, `@lru_cache`, Django `@cache_page`
- Resilience: `@retry` (tenacity), rate limiting, timeouts
- Observability: timing, logging, tracing spans
- Testing: `@pytest.fixture`, `@pytest.mark.parametrize`, `@unittest.mock.patch`
- Language: `@property`, `@staticmethod`, `@classmethod`, `@dataclass`, `@contextmanager`, `@abstractmethod`"""),

Q(10, "Moderate", "How do you write a timing decorator?",
"""Wrap the call with `time.perf_counter()` (monotonic, high resolution) and report in a `finally` block so failures are timed too.""",
r'''
import functools, time
def timed(fn):
    @functools.wraps(fn)
    def wrapper(*a, **k):
        start = time.perf_counter()
        try:
            return fn(*a, **k)
        finally:
            print(f"{fn.__name__} took {(time.perf_counter() - start) * 1000:.1f} ms")
    return wrapper
@timed
def slow_sum(n): return sum(range(n))
slow_sum(2_000_000)
'''),

Q(10, "Difficult", "How do you write a decorator that works on both sync and async functions?",
"""Check `inspect.iscoroutinefunction(fn)` and return an `async def` wrapper for coroutines (which `await`s the call) or a normal wrapper otherwise.""",
r'''
import asyncio, functools, inspect, time
def timed(fn):
    if inspect.iscoroutinefunction(fn):
        @functools.wraps(fn)
        async def awrapper(*a, **k):
            t = time.perf_counter(); r = await fn(*a, **k)
            print(f"async {fn.__name__}: {(time.perf_counter() - t) * 1000:.0f} ms"); return r
        return awrapper
    @functools.wraps(fn)
    def wrapper(*a, **k):
        t = time.perf_counter(); r = fn(*a, **k)
        print(f"sync {fn.__name__}: {(time.perf_counter() - t) * 1000:.0f} ms"); return r
    return wrapper
@timed
async def fetch(): await asyncio.sleep(0.05); return "data"
@timed
def compute(): time.sleep(0.02); return 42
print(asyncio.run(fetch()), compute())
'''),

Q(10, "Easy", "What is a context manager and the `with` statement?",
"""An object that sets something up on entry and guarantees cleanup on exit, even if an exception occurs. `with open(path) as f:` closes the file automatically. It implements `__enter__` and `__exit__`.""",
r'''
import os, tempfile
path = os.path.join(tempfile.mkdtemp(), "notes.txt")
with open(path, "w", encoding="utf-8") as f:
    f.write("hello")
print(f.closed)
'''),

Q(10, "Moderate", "How do you create a context manager with `contextlib.contextmanager`?",
"""Write a generator that does setup, `yield`s exactly once (the yielded value is bound by `as`), and does cleanup after. Wrap the `yield` in `try/finally` so cleanup runs if the block raises.""",
r'''
from contextlib import contextmanager
import os, tempfile
@contextmanager
def working_dir(path):
    old = os.getcwd()
    os.chdir(path)
    try:
        yield path
    finally:
        os.chdir(old)
tmp = tempfile.mkdtemp()
with working_dir(tmp):
    print(os.getcwd() == os.path.realpath(tmp) or os.getcwd() == tmp)
print(os.getcwd() != tmp)
'''),

Q(10, "Moderate", "Can one `with` statement manage multiple context managers?",
"""Yes: `with A() as a, B() as b:`. Since 3.10 you can wrap them in parentheses across lines. They're entered left to right and exited in reverse order. For a dynamic number, use `contextlib.ExitStack`.""",
r'''
from contextlib import contextmanager
@contextmanager
def res(name):
    print("open", name); yield name; print("close", name)
with (
    res("db") as db,
    res("cache") as cache,
):
    print("using", db, cache)
'''),

Q(10, "Moderate", "What does `contextlib.suppress` do?",
"""It suppresses the listed exceptions inside the block, a readable alternative to `try/except: pass` for expected, ignorable errors.""",
r'''
import contextlib, os
with contextlib.suppress(FileNotFoundError):
    os.remove("/definitely/not/here.tmp")
print("no crash")
'''),

Q(10, "Difficult", "What is `contextlib.ExitStack` used for?",
"""It manages an arbitrary, runtime-determined number of context managers and callbacks, unwinding them in reverse order. Also useful to conditionally enter a context manager or to transfer cleanup responsibility (`pop_all()`).""",
r'''
from contextlib import ExitStack, contextmanager
@contextmanager
def conn(n):
    print(f"connect {n}"); yield n; print(f"disconnect {n}")
shards = [1, 2, 3]
with ExitStack() as stack:
    conns = [stack.enter_context(conn(s)) for s in shards]
    stack.callback(print, "flush metrics")
    print("query all:", conns)
'''),

Q(10, "Difficult", "How do async context managers work?",
"""They implement `__aenter__`/`__aexit__` (or use `@contextlib.asynccontextmanager`) and are used with `async with`. Typical: DB transactions, HTTP sessions (`aiohttp.ClientSession`), locks in asyncio.""",
r'''
import asyncio
from contextlib import asynccontextmanager
@asynccontextmanager
async def transaction(name):
    print("BEGIN", name); await asyncio.sleep(0)
    try:
        yield name
        print("COMMIT", name)
    except Exception:
        print("ROLLBACK", name); raise
async def main():
    async with transaction("tx1"):
        pass
    try:
        async with transaction("tx2"):
            raise ValueError("bad row")
    except ValueError:
        pass
asyncio.run(main())
'''),

Q(10, "Moderate", "Can a context manager suppress exceptions? How?",
"""Yes: if `__exit__` returns a truthy value, the exception is swallowed. In `@contextmanager` generators, catching the exception around `yield` and not re-raising suppresses it. Suppressing should be deliberate and narrow."""),

Q(10, "Difficult", "What is `contextlib.nullcontext` for?",
"""A context manager that does nothing, optionally returning a value. It lets code use one `with` statement whether or not a real resource (lock, transaction, file) is provided.""",
r'''
import contextlib, sys
def write_report(text, path=None):
    cm = open(path, "w") if path else contextlib.nullcontext(sys.stdout)
    with cm as out:
        out.write(text + "\n")
write_report("printed to stdout because no path was given")
'''),

Q(10, "Difficult", "How would you write a decorator that caches results with a time-to-live (TTL)?",
"""Store `(timestamp, value)` keyed by arguments, and recompute when the entry is older than the TTL. Arguments must be hashable. (Libraries like `cachetools.TTLCache` provide this.)""",
r'''
import functools, time
def ttl_cache(seconds):
    def deco(fn):
        store = {}
        @functools.wraps(fn)
        def wrapper(*args):
            now = time.monotonic()
            if args in store and now - store[args][0] < seconds:
                return store[args][1]
            value = fn(*args); store[args] = (now, value); return value
        return wrapper
    return deco
@ttl_cache(0.05)
def rate(cur):
    print("  fetching", cur); return 83.1
rate("USD"); rate("USD"); time.sleep(0.06); rate("USD")
'''),

Q(10, "Moderate", "What is the difference between `@property` and a decorator you write yourself?",
"""`property` is a built-in **descriptor** class; used as a decorator it wraps the getter in a descriptor object that intercepts attribute access. Your own decorators usually return a wrapper function. Both use the same `@` syntax because both are callables applied to the function."""),

]
