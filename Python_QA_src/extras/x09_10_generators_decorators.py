EXTRAS = [

X(0, "What is the difference between an iterable and an iterator", terms=[
    ("`iter()` / `next()`", "Built-ins that call `__iter__` and `__next__`."),
    ("Exhaustion", "An iterator that has raised `StopIteration` stays empty forever."),
], pitfall="""Passing an iterator (such as a `map` object or a file) to a function that loops over it twice. The second loop sees nothing and no error is raised.""",
follow=[
    ("How can you tell an iterator from an iterable?", "`iter(x) is x` is True for iterators."),
    ("Is a file object an iterator?", "Yes; iterating it consumes lines, and a second loop needs `f.seek(0)`."),
]),

X(1, "What is a list comprehension", terms=[
    ("Comprehension", "An expression that builds a collection from a `for` clause, optional `if` filters and more `for` clauses."),
], pitfall="""Using a comprehension for side effects (`[print(x) for x in xs]`). It builds a useless list of `None`s; write a `for` loop.""",
follow=[
    ("Why is a comprehension faster than `append` in a loop?", "It avoids the repeated `.append` attribute lookup and method call, using a dedicated `LIST_APPEND` bytecode."),
    ("Where does `if ... else` go?", "Before the `for` as a conditional expression (`[a if c else b for x in xs]`); a filter `if` goes after the `for`."),
]),

X(2, "What are dict and set comprehensions", terms=[
    ("Dict comprehension", "`{key: value for ...}`; later duplicate keys overwrite earlier ones."),
], pitfall="""Inverting a dict with `{v: k for k, v in d.items()}` when values are not unique. Keys collide and entries are silently lost.""",
follow=[
    ("Is there a tuple comprehension?", "No; `(x for x in ...)` is a generator expression. Use `tuple(x for x in ...)`."),
    ("How do you filter a dict by value?", "`{k: v for k, v in d.items() if v > 0}`."),
]),

X(3, "What is a generator?", terms=[
    ("Generator function", "A `def` containing `yield`; calling it returns a generator object and runs no code yet."),
    ("Suspended frame", "The generator keeps its local variables and position between `next()` calls."),
], pitfall="""Putting validation at the top of a generator function. It does not run until the first `next()`, so errors appear far from the call; validate in a normal wrapper function that returns the generator.""",
follow=[
    ("What does `inspect.getgeneratorstate` show?", "One of `GEN_CREATED`, `GEN_RUNNING`, `GEN_SUSPENDED`, `GEN_CLOSED`."),
    ("Can a generator run forever?", "Yes, infinite generators are common; the consumer decides when to stop (e.g. `islice`)."),
]),

X(4, "Generator expression vs list comprehension", terms=[
    ("Generator expression", "`(expr for x in it)`: lazy, one-shot, constant memory."),
], pitfall="""Using a generator expression and then calling `len()` or indexing on it. Generators support neither; use a list if you need them.""",
follow=[
    ("When can you omit the extra parentheses?", "When the generator is the sole argument of a call: `sum(x * x for x in xs)`."),
    ("Is a genexp always faster for `sum`?", "Not always; for small inputs `sum([...])` can be slightly faster. The genexp wins on memory for large inputs."),
]),

X(5, "What does `yield from` do", terms=[
    ("Delegating generator", "A generator that hands control to a sub-generator with `yield from`."),
], pitfall="""Writing `for x in sub(): yield x` when `sub` returns a value or needs `send()`. The loop drops the return value and does not forward `send`/`throw`; use `yield from`.""",
follow=[
    ("How do you write a recursive tree walk with it?", "`def walk(node): yield node; for c in node.children: yield from walk(c)`."),
    ("How did `yield from` relate to early asyncio?", "Before `async`/`await` (3.5), coroutines were generators using `yield from`."),
]),

X(6, "What are `send()`, `throw()`", terms=[
    ("Priming", "Advancing a new generator to its first `yield` with `next(gen)` (or `send(None)`) before sending values."),
    ("`GeneratorExit`", "Raised inside the generator by `close()`; the generator must not yield after catching it."),
], pitfall="""Catching `GeneratorExit` (or a bare `except:`) and yielding again. `close()` then raises `RuntimeError: generator ignored GeneratorExit`.""",
follow=[
    ("What does `send(x)` return?", "The next value the generator yields."),
    ("When is `close()` called automatically?", "When the generator object is garbage-collected while suspended."),
]),

X(7, "What does `enumerate` do", terms=[
    ("`start`", "Keyword argument setting the first index, such as `enumerate(xs, start=1)`."),
], pitfall="""Iterating `for i in range(len(xs)):` and then `xs[i]`. It is slower and less clear, and it does not work for iterables without indexing.""",
follow=[
    ("How do you enumerate in reverse?", "`reversed(list(enumerate(xs)))`, or compute indices with `zip(range(len(xs)-1, -1, -1), reversed(xs))`."),
    ("Is `enumerate` lazy?", "Yes, it returns an iterator."),
]),

X(8, "What does `zip` do", terms=[
    ("`zip_longest`", "From `itertools`; pads shorter inputs with `fillvalue`."),
], pitfall="""Zipping two lists that should have equal length, and silently losing data when one is shorter. Use `strict=True` to fail loudly.""",
follow=[
    ("How do you unzip a list of pairs?", "`a, b = zip(*pairs)` (the results are tuples)."),
    ("How do you iterate over consecutive pairs?", "`itertools.pairwise(xs)` (3.10+)."),
]),

X(9, "Name the most useful `itertools` functions", terms=[
    ("`batched`", "(3.12+) Splits an iterable into tuples of size n; 3.13 adds `strict=True`."),
    ("`accumulate`", "Running totals (or any binary function) over an iterable."),
], pitfall="""Using `itertools.tee` on a large iterator and consuming one copy fully before the other. `tee` buffers every item in between, so memory grows to the whole input.""",
follow=[
    ("How many items does `permutations(range(10))` produce?", "10! = 3,628,800, which is why these functions are lazy."),
    ("What is `product` useful for?", "Nested loops without nesting: `product(xs, ys)` or `product(range(2), repeat=n)` for bit patterns."),
]),

X(10, "What is lazy evaluation", terms=[
    ("Pipeline", "Chained lazy stages (read, filter, transform) that process one item at a time."),
], pitfall="""A lazy pipeline over a file that is closed before the pipeline is consumed (returning a generator from inside a `with` block). Consumption then fails with `ValueError: I/O operation on closed file`.""",
follow=[
    ("Is `range` an iterator?", "No, it is a lazy sequence: it supports `len`, indexing and multiple iterations."),
    ("How do you force evaluation?", "Wrap with `list()`, `tuple()`, or consume in a loop."),
]),

X(11, "Why can a generator only be iterated once", terms=[
    ("Re-iterable", "An object whose `__iter__` returns a fresh iterator each time."),
], pitfall="""Checking whether a generator is empty with `if gen:`. Generator objects are always truthy; use `first = next(gen, sentinel)`.""",
follow=[
    ("How do you peek at the first item without losing it?", "`first = next(it)` then `itertools.chain([first], it)`."),
    ("Is caching all items in a list a valid workaround?", "Yes, when the data fits in memory: `items = list(gen)`."),
]),

X(12, "Do comprehension loop variables leak", terms=[
    ("PEP 709", "Inlined comprehensions (3.12): faster, with the same scoping rules as before."),
], pitfall="""In a class body, a comprehension cannot see class-level names except in the outermost iterable, so `[x * FACTOR for x in data]` inside a class raises `NameError` for `FACTOR`.""",
follow=[
    ("Does a `for` loop variable leak?", "Yes, it stays bound to the last value after the loop."),
    ("Does a walrus in a comprehension leak?", "Yes, `:=` binds in the containing scope by design."),
]),

X(13, "How do you read a huge file efficiently", terms=[
    ("Buffered I/O", "Reading in large blocks internally while handing out lines one at a time."),
    ("`mmap`", "Maps a file into memory so the OS pages it in on demand."),
], pitfall="""Calling `f.read()` or `f.readlines()` on a multi-gigabyte file. Both load the whole file into memory.""",
follow=[
    ("How do you read binary in chunks idiomatically?", "`for chunk in iter(lambda: f.read(1 << 16), b\"\"):`."),
    ("How do you process a huge CSV?", "Stream with `csv.reader`, or use pandas `read_csv(chunksize=...)` or polars' lazy scan."),
]),

X(14, "What happens if a generator has a `return` value", terms=[
    ("`StopIteration.value`", "Attribute carrying a generator's return value."),
], pitfall="""Expecting a `for` loop to give you the return value. The loop swallows `StopIteration`; use `yield from` or call `next()` and catch `StopIteration` yourself.""",
follow=[
    ("Where is this pattern useful?", "Sub-generators that yield progress and return a summary to a delegating generator."),
    ("What is `return` without a value in a generator?", "It ends iteration with `StopIteration` whose value is `None`."),
]),

X(15, "What are `any()` and `all()`", terms=[
    ("Short-circuit", "Stopping evaluation as soon as the result is known."),
], pitfall="""Passing a list comprehension (`any([check(x) for x in xs])`). The list is fully built first, so there is no short-circuit; pass a generator expression.""",
follow=[
    ("What does `all([])` return and why?", "True, because no item is false (vacuous truth)."),
    ("How do you find which item matched?", "`next((x for x in xs if pred(x)), None)`."),
]),

X(16, "What is an async generator", terms=[
    ("`async for`", "Iterates over an async iterator, awaiting `__anext__` for each item."),
    ("`aclose()`", "Async equivalent of `close()`; ensures `finally` blocks run."),
], pitfall="""Breaking out of an `async for` over an async generator without closing it. Cleanup runs later on a GC hook; wrap it with `contextlib.aclosing` for deterministic cleanup.""",
follow=[
    ("Can you use `yield from` in an async generator?", "No; use `async for x in sub(): yield x`."),
    ("Are async comprehensions allowed?", "Yes, `[x async for x in agen()]` inside an `async def`."),
]),

X(17, "How do you implement `range`-like behaviour", terms=[
    ("Accumulated rounding error", "Error that grows when you repeatedly add a float step."),
], pitfall="""Using `while x < stop: x += step`. Rounding errors accumulate, and the loop can produce one extra or one missing value.""",
follow=[
    ("What does NumPy offer?", "`np.arange` (same end-point pitfalls) and `np.linspace(start, stop, num)`, which is safer for floats."),
    ("How do you get exact decimal steps?", "Use `Decimal` or `Fraction` arithmetic."),
]),

X(18, "What does `iter(callable, sentinel)` do", terms=[
    ("Sentinel", "A marker value that signals the end of the data."),
], pitfall="""Using a sentinel that can legitimately occur in the data, such as an empty line when reading from a socket that may send empty lines.""",
follow=[
    ("How do you read a socket until closed?", "`for data in iter(lambda: sock.recv(4096), b\"\"):`."),
    ("Can the callable take arguments?", "No; wrap it with `lambda` or `functools.partial`."),
]),

X(19, "What is the difference between a nested comprehension's loop order", terms=[
    ("Clause order", "`for` clauses are read left to right as outer to inner loops."),
], pitfall="""Writing `[x for x in row for row in matrix]`. `row` is used before it is defined, which raises `NameError` (or silently uses a stale outer `row`).""",
follow=[
    ("How do you transpose a matrix?", "`[list(col) for col in zip(*matrix)]`."),
    ("When should you switch to plain loops?", "When there are more than two `for` clauses or complex conditions."),
]),

X(20, "What is a decorator?", terms=[
    ("`@` syntax", "`@d` above `def f` is shorthand for `f = d(f)` after the definition."),
    ("Wrapper", "The inner function a decorator returns, which calls the original."),
], pitfall="""Returning the wrapper's result from the decorator instead of the wrapper (`return wrapper()` instead of `return wrapper`). The function is then called at decoration time.""",
follow=[
    ("Since 3.9, what can follow `@`?", "Any expression (PEP 614), such as `@buttons[0].on_click`."),
    ("Can you undo a decorator?", "If `functools.wraps` was used, the original is available as `f.__wrapped__`."),
]),

X(21, "Why use `functools.wraps`", terms=[
    ("`__wrapped__`", "Attribute set by `wraps` pointing to the original function."),
], pitfall="""Forgetting `wraps` in a decorator used with pytest fixtures or FastAPI endpoints. They inspect the signature and see `(*args, **kwargs)`, which breaks dependency injection.""",
follow=[
    ("Which attributes does `wraps` copy?", "`__module__`, `__name__`, `__qualname__`, `__doc__`, `__dict__` (merged), `__type_params__` (3.12+), and it sets `__wrapped__`."),
    ("Does `wraps` preserve the signature for type checkers?", "No; use `ParamSpec` in the decorator's annotations for that."),
]),

X(22, "How do you write a decorator that accepts arguments", terms=[
    ("Decorator factory", "A function that takes configuration and returns a decorator."),
], pitfall="""Supporting both `@retry` and `@retry(times=3)` without care. The first passes the function as the first argument; detect it with `if callable(arg)` or require parentheses.""",
follow=[
    ("How many nested functions does this need?", "Three: the factory, the decorator, and the wrapper."),
    ("How do you write it as a class?", "Store the arguments in `__init__`, and make `__call__(self, fn)` return the wrapper."),
]),

X(23, "In what order are stacked decorators", terms=[
    ("Decoration order", "Bottom-up at definition, top-down (outermost first) at call time."),
], pitfall="""Stacking `@staticmethod` or `@classmethod` below another decorator that expects a plain function. Put `@classmethod`/`@staticmethod` outermost (top).""",
follow=[
    ("Where should `@app.route` go relative to `@login_required`?", "`@app.route` on top, so it registers the already-protected function."),
    ("Is `@cache` above or below `@timed` better?", "Depends on intent: `@timed` on top measures cache hits too; below, it times only real computations."),
]),

X(24, "Can you decorate a class", terms=[
    ("Class decorator", "A callable taking a class and returning a class."),
], pitfall="""A class decorator that returns a new wrapper class. `isinstance` checks, pickling and class attributes on the original may break; prefer modifying and returning the same class.""",
follow=[
    ("When is a class decorator better than a metaclass?", "For one-off modifications that do not need to apply to subclasses automatically."),
    ("Do class decorators apply to subclasses?", "No; only to the decorated class itself."),
]),

X(25, "How do you write a class-based decorator", terms=[
    ("`__get__` for methods", "Needed so that decorating a method still binds `self`."),
], pitfall="""Using a class-based decorator on methods without implementing `__get__`. The instance is not passed, and `self` is missing in the call.""",
follow=[
    ("How do you implement `__get__` for it?", "Return `functools.partial(self.__call__, instance)` (or `types.MethodType(self, instance)`) when `instance` is not None."),
    ("How do you apply `wraps` in a class decorator?", "`functools.update_wrapper(self, fn)` in `__init__`."),
]),

X(26, "Give real-world uses of decorators", terms=[
    ("Cross-cutting concern", "Behavior needed in many places (logging, auth, retries) that is not the function's main job."),
], pitfall="""Hiding important control flow (retries, transactions, permission checks) in stacked decorators nobody reads. Keep decorators focused and document their effect.""",
follow=[
    ("What does `@functools.singledispatch` show about decorators?", "Decorators can return objects with extra methods (`.register`), not just wrappers."),
    ("How do you write a registration decorator?", "Add the function to a dict and return it unchanged."),
]),

X(27, "How do you write a timing decorator", terms=[
    ("`perf_counter`", "Highest-resolution monotonic clock, for measuring durations."),
    ("`process_time`", "CPU time of the current process, excluding sleep."),
], pitfall="""Using `time.time()` for durations. It can jump when the system clock is adjusted; use `perf_counter` or `monotonic`.""",
follow=[
    ("How do you time a block rather than a function?", "A context manager with `perf_counter` in `__enter__` and `__exit__`."),
    ("How do you get reliable micro-benchmarks?", "Use `timeit` (or `python -m timeit`), which repeats runs and disables GC during timing."),
]),

X(28, "How do you write a decorator that works on both sync and async", terms=[
    ("`inspect.iscoroutinefunction`", "True for `async def` functions (and, since 3.12, for functions marked with `inspect.markcoroutinefunction`)."),
], pitfall="""Wrapping an async function with a sync wrapper. The wrapper returns the coroutine un-awaited, so timing or error handling applies to creating the coroutine, not running it.""",
follow=[
    ("Why is `asyncio.iscoroutinefunction` discouraged now?", "It is deprecated since 3.14; use `inspect.iscoroutinefunction`."),
    ("How do you handle async generators?", "Check `inspect.isasyncgenfunction` and write an `async def` wrapper that uses `async for ... yield`."),
]),

X(29, "What is a context manager and the `with` statement", terms=[
    ("Context manager protocol", "`__enter__` and `__exit__`."),
    ("RAII-like cleanup", "Tying resource release to leaving a block, as C++ ties it to object scope."),
], pitfall="""Returning a file from inside a `with open(...)` block to use later. The file is already closed when the caller uses it.""",
follow=[
    ("Which stdlib objects are context managers?", "Files, locks, sockets, `decimal.localcontext`, `tempfile.TemporaryDirectory`, `ThreadPoolExecutor`."),
    ("Is `with` required to close files?", "Not strictly (CPython closes on garbage collection), but it guarantees timely closing on every path."),
]),

X(30, "How do you create a context manager with `contextlib.contextmanager`", terms=[
    ("Generator-based context manager", "Setup before `yield`, cleanup after it, typically in `finally`."),
], pitfall="""Forgetting `try/finally` around the `yield`. If the block raises, the exception is thrown into the generator at the `yield` and the cleanup code never runs.""",
follow=[
    ("Can the result be used as a decorator?", "Yes, `@contextmanager` objects inherit `ContextDecorator`, so `@my_cm()` wraps a function call."),
    ("What happens if the generator yields twice?", "`RuntimeError: generator didn't stop`."),
]),

X(31, "Can one `with` statement manage multiple", terms=[
    ("Unwinding order", "Managers exit in reverse order of entry."),
], pitfall="""Assuming a failure in a later `__enter__` also skips cleanup of earlier ones. It does not; earlier managers still exit properly, which is exactly why this form is safe.""",
follow=[
    ("What is the pre-3.10 way to span lines?", "Backslash continuation, or `ExitStack`."),
    ("Can a later manager use an earlier `as` name?", "Yes, `with open(p) as f, Wrapper(f) as w:` works because they are entered in order."),
]),

X(32, "What does `contextlib.suppress` do", terms=[
    ("Expected exception", "An error that is a normal outcome, such as `FileNotFoundError` when deleting an optional file."),
], pitfall="""Wrapping a multi-line block in `suppress`. Execution stops at the first raising line and the remaining lines silently do not run.""",
follow=[
    ("What is the typical example?", "`with suppress(FileNotFoundError): os.remove(path)`."),
    ("Does `suppress` handle exception groups?", "Yes since 3.12: it suppresses matching exceptions within an `ExceptionGroup` and re-raises the rest."),
]),

X(33, "What is `contextlib.ExitStack` used for", terms=[
    ("`enter_context`", "Enters a context manager and registers its exit."),
    ("`pop_all`", "Transfers the registered callbacks to a new stack, used to keep resources open on success."),
], pitfall="""Opening many files in a loop with `ExitStack` and exceeding the OS file-descriptor limit. Process in batches if the number is large.""",
follow=[
    ("How do you register a plain cleanup function?", "`stack.callback(fn, *args)`."),
    ("How does `pop_all` help in constructors?", "Open resources inside a `with ExitStack()`; on success call `pop_all()` to keep them, so failures clean up automatically."),
]),

X(34, "How do async context managers work", terms=[
    ("`asynccontextmanager`", "Decorator turning an async generator into an async context manager."),
], pitfall="""Using `with` instead of `async with` on an async resource. It raises `TypeError` (the object does not support the synchronous protocol), or worse, a library may offer both and the sync path blocks the event loop.""",
follow=[
    ("What is `AsyncExitStack`?", "The async counterpart of `ExitStack`, with `enter_async_context`."),
    ("Can `__aexit__` suppress exceptions?", "Yes, by returning a truthy value, just like `__exit__`."),
]),

X(35, "Can a context manager suppress exceptions", terms=[
    ("`__exit__` return value", "Truthy means the exception is handled; falsy (including `None`) means it propagates."),
], pitfall="""In an `@contextmanager` generator, catching `Exception` around `yield` and not re-raising. Every error inside the `with` block is silently swallowed.""",
follow=[
    ("How do you inspect the exception in `__exit__`?", "The arguments `exc_type`, `exc_value` and `traceback` are `None` when no exception occurred."),
    ("Should `__exit__` re-raise the exception itself?", "No; return a falsy value and Python re-raises it with the original traceback."),
]),

X(36, "What is `contextlib.nullcontext` for", terms=[
    ("Null object pattern", "A do-nothing implementation that removes special-case branches."),
], pitfall="""Writing `with (lock if lock else nullcontext()):` everywhere. Encapsulate the choice once, for example by defaulting the parameter to `nullcontext()`.""",
follow=[
    ("What does `nullcontext(x)` bind with `as`?", "`x` itself."),
    ("Does it support `async with`?", "Yes, since 3.10."),
]),

X(37, "How would you write a decorator that caches results with a time-to-live", terms=[
    ("TTL", "Time to live: how long a cached value stays valid."),
    ("Cache stampede", "Many callers recomputing the same expired value at once."),
], pitfall="""Letting expired entries stay in the dict forever. Without eviction the cache grows without bound; evict on access, cap the size, or use `cachetools.TTLCache`.""",
follow=[
    ("Which clock should a TTL cache use?", "`time.monotonic()`, which never jumps backward."),
    ("How do you make it thread-safe?", "Guard reads and writes with a lock, and consider a per-key lock to avoid duplicate computation."),
]),

X(38, "What is the difference between `@property`", terms=[
    ("Descriptor class", "A class whose instances control attribute access when stored as class attributes."),
], pitfall="""Writing a function-based decorator and expecting it to behave like `@property` (attribute access without calling). Only descriptors can intercept attribute access.""",
follow=[
    ("How does `@x.setter` work?", "`property.setter` returns a new property object copying the getter and adding the setter, which replaces the name `x`."),
    ("Can you write your own property?", "Yes, a class with `__get__`, `__set__` and `__set_name__` reproduces it."),
]),
]
