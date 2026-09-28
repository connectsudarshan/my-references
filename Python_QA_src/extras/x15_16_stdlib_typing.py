EXTRAS = [

X(0, "How do you work with dates and times correctly", terms=[
    ("Aware vs naive", "An aware datetime has `tzinfo`; a naive one does not and is ambiguous."),
    ("`zoneinfo`", "(3.9+) IANA time-zone database support, e.g. `ZoneInfo(\"Europe/Berlin\")`."),
], pitfall="""Using `datetime.utcnow()`. It returns a naive datetime that many functions treat as local time, and it is deprecated since 3.12; use `datetime.now(timezone.utc)`.""",
follow=[
    ("Why is adding `timedelta(days=1)` across a DST change tricky?", "Arithmetic on aware datetimes is wall-clock based within one tzinfo, so \"one day later\" may be 23 or 25 real hours; convert to UTC for elapsed-time math."),
    ("How do you parse ISO 8601 strings?", "`datetime.fromisoformat()`, which accepts most ISO 8601 formats since 3.11."),
]),

X(1, "How do you work with file paths", terms=[
    ("`PurePath`", "Path manipulation without filesystem access; `PureWindowsPath` works on any OS."),
], pitfall="""Building paths with string concatenation (`dir + \"/\" + name`). It breaks on Windows edge cases and doubles or loses separators; use `Path(dir) / name`.""",
follow=[
    ("How do you list files recursively?", "`Path(root).rglob(\"*.py\")`, or `Path.walk()` (3.12+) for an `os.walk`-style traversal."),
    ("What are `read_text` / `write_text`?", "One-call helpers to read or write a whole file; pass `encoding=\"utf-8\"`."),
]),

X(2, "How do you read and write JSON", terms=[
    ("`default=`", "A function `json.dumps` calls for objects it cannot serialize."),
    ("`object_hook`", "A function `json.loads` calls on every decoded dict, to build custom objects."),
], pitfall="""Assuming a round trip preserves types. Tuples become lists, int dict keys become strings, and `datetime` or `Decimal` fail unless you add `default=`.""",
follow=[
    ("How do you parse JSON floats as `Decimal`?", "`json.loads(s, parse_float=Decimal)`."),
    ("What is faster than the stdlib `json`?", "`orjson` or `msgspec`, both implemented in compiled code."),
]),

X(3, "How do you read and write CSV files", terms=[
    ("Dialect", "Delimiter, quoting and line-terminator settings; `csv.Sniffer` can guess them."),
], pitfall="""Opening CSV files without `newline=\"\"`. On Windows the writer then produces blank lines between rows, and quoted fields containing newlines are misread.""",
follow=[
    ("Why is `split(\",\")` wrong for CSV?", "Fields can be quoted and contain commas or newlines."),
    ("When should you use pandas or polars instead?", "For large files, type inference and analysis; `csv` is fine for streaming simple rows."),
]),

X(4, "What does the `logging` module provide", terms=[
    ("Handler", "Sends records somewhere (stream, file, syslog)."),
    ("Propagation", "Records bubble up to ancestor loggers' handlers."),
], pitfall="""Calling `logging.basicConfig()` or adding handlers inside a library. Libraries should only create loggers (and at most add a `NullHandler`); the application configures output.""",
follow=[
    ("How do you configure logging from a dict?", "`logging.config.dictConfig({...})`, often loaded from YAML or TOML."),
    ("How do you avoid blocking on slow handlers?", "`QueueHandler` plus `QueueListener`, so log I/O happens on a background thread."),
]),

X(5, "What does `functools` offer besides", terms=[
    ("`cached_property`", "Computes an attribute once per instance and stores it."),
    ("`cmp_to_key`", "Converts an old-style comparison function into a key function."),
], pitfall="""Using `lru_cache` on functions with unhashable arguments (lists, dicts). The call raises `TypeError`; convert arguments to tuples or frozensets.""",
follow=[
    ("What is `functools.reduce` best replaced with?", "Built-ins where possible: `sum`, `math.prod`, `max`, `any`, `\"\".join`."),
    ("What does `singledispatchmethod` do?", "Type-based dispatch on the first non-self argument of a method."),
]),

X(6, "What does the `operator` module provide", terms=[
    ("`itemgetter(1)`", "Callable returning `obj[1]`; with several indexes it returns a tuple."),
    ("`methodcaller(\"strip\")`", "Callable that calls `obj.strip()`."),
], pitfall="""Expecting `itemgetter(0)` with a single argument to return a tuple. Only multiple arguments produce a tuple, which surprises code that expects consistent shapes.""",
follow=[
    ("Why is `itemgetter` faster than a lambda?", "It is implemented in C and avoids a Python-level function call."),
    ("What does `attrgetter(\"a.b\")` do?", "Follows dotted attributes, returning `obj.a.b`."),
]),

X(7, "How do you run external commands safely", terms=[
    ("`shell=True`", "Runs the command through a shell, which interprets metacharacters."),
    ("`check=True`", "Raises `CalledProcessError` on non-zero exit status."),
], pitfall="""Passing untrusted input with `shell=True`. A filename like `x; rm -rf ~` becomes a command injection; pass an argument list without a shell.""",
follow=[
    ("How do you stream output line by line?", "Use `subprocess.Popen(..., stdout=PIPE, text=True)` and iterate over `proc.stdout`."),
    ("How do you avoid deadlocks with pipes?", "Use `communicate()` or `run()` instead of reading one pipe while the other fills."),
]),

X(8, "How do you generate secure random values", terms=[
    ("CSPRNG", "Cryptographically secure pseudo-random number generator, backed by the OS (`os.urandom`)."),
], pitfall="""Using `random` for tokens, passwords or IDs. It is a Mersenne Twister whose state can be recovered from outputs; use `secrets`.""",
follow=[
    ("What is `secrets.compare_digest` for?", "Constant-time comparison of secrets to prevent timing attacks."),
    ("How do you seed `random` for reproducible tests?", "`random.seed(42)`, or use a separate `random.Random(42)` instance."),
]),

X(9, "How do you hash data, and how should passwords be stored", terms=[
    ("Salt", "Random per-password value stored with the hash so identical passwords hash differently."),
    ("KDF", "Key derivation function designed to be slow: Argon2, scrypt, bcrypt, PBKDF2."),
], pitfall="""Storing passwords as SHA-256 hashes, even salted. General-purpose hashes are fast, so GPUs can try billions per second; use Argon2id (argon2-cffi), bcrypt or `hashlib.scrypt`.""",
follow=[
    ("Is MD5 still acceptable for anything?", "Only for non-security checksums; use `usedforsecurity=False` to document that."),
    ("What does `hashlib.file_digest` do?", "(3.11+) Hashes a file object efficiently without reading it all into memory."),
]),

X(10, "What is `dataclasses` vs `typing.NamedTuple`", terms=[
    ("Validation", "Checking and converting input data at runtime; pydantic does it, dataclasses do not."),
    ("`msgspec.Struct`", "A fast, typed record with built-in JSON/MessagePack encoding and validation."),
], pitfall="""Using pydantic models everywhere, including hot internal code. Validation has a cost; validate at boundaries and use dataclasses inside.""",
follow=[
    ("What do `attrs` offer over dataclasses?", "Validators, converters and more options; dataclasses were modeled on attrs."),
    ("When is `NamedTuple` preferable?", "For small immutable records that must also behave like tuples (unpacking, CSV rows)."),
]),

X(11, "How do you work with temporary files and directories", terms=[
    ("`delete_on_close`", "(3.12+) `NamedTemporaryFile(delete_on_close=False)` keeps the file until the context exits, which fixes reopening on Windows."),
], pitfall="""Using `tempfile.mktemp()`. It returns a name without creating the file, which is a race condition and a security risk; use `mkstemp` or `NamedTemporaryFile`.""",
follow=[
    ("How do you get a temp directory in pytest?", "The `tmp_path` fixture gives a unique `pathlib.Path` per test."),
    ("Where are temp files created?", "In `tempfile.gettempdir()`, controlled by `TMPDIR`, `TEMP` or `TMP`."),
]),

X(12, "How do you parse command-line arguments", terms=[
    ("Subcommand", "A verb-style command (`git commit`), created with `add_subparsers()`."),
], pitfall="""Parsing `sys.argv` by hand. Quoting, `--help`, error messages and type conversion all end up half-implemented; use argparse, click or typer.""",
follow=[
    ("How do you make an argument a boolean flag?", "`action=\"store_true\"`, or `argparse.BooleanOptionalAction` for `--flag/--no-flag`."),
    ("What does typer add?", "Builds the CLI from function signatures and type hints, on top of click."),
]),

X(13, "What are `collections.ChainMap` and `types.SimpleNamespace`", terms=[
    ("Layered lookup", "Searching several mappings in priority order without merging."),
], pitfall="""Writing to a `ChainMap` expecting to update the layer where the key was found. Writes and deletes always go to the first mapping.""",
follow=[
    ("How do you add a new scope?", "`cm.new_child()` returns a ChainMap with a fresh dict in front; `.parents` drops it."),
    ("How does `SimpleNamespace` differ from a dict?", "It uses attribute access and has a readable repr; convert with `vars(ns)`."),
]),

X(14, "How do you measure execution time of a snippet", terms=[
    ("Warm-up", "Initial runs affected by caching or JIT specialization, which benchmarks should exclude."),
], pitfall="""Timing a single run with `time.time()` and comparing two versions. Noise dominates; repeat many times and compare minimums or medians.""",
follow=[
    ("What is `pyperf`?", "A benchmarking tool that spawns worker processes, calibrates loops and reports statistics; used for CPython's own benchmarks."),
    ("How do you time in IPython or Jupyter?", "`%timeit expr` and `%%timeit` for a whole cell."),
]),

X(15, "What is `decimal.Decimal`", terms=[
    ("Context", "Precision, rounding mode and traps for Decimal operations (`decimal.getcontext()`, `localcontext()`)."),
    ("`quantize`", "Rounds to a fixed exponent, such as two decimal places."),
], pitfall="""Mixing `Decimal` and `float` in arithmetic. It raises `TypeError`, and converting floats with `Decimal(0.1)` imports binary error; build from strings.""",
follow=[
    ("What does precision mean for Decimal?", "Significant digits (default 28), not decimal places."),
    ("How do you store money in a database?", "Use a DECIMAL/NUMERIC column, or integer minor units (cents)."),
]),

X(16, "What does `shutil` provide", terms=[
    ("`copy2`", "Copies a file with its metadata (timestamps)."),
], pitfall="""Calling `shutil.rmtree` on a path built from user input or an unchecked variable. An empty or wrong value can delete far more than intended; validate the path first.""",
follow=[
    ("How do you find an executable on PATH?", "`shutil.which(\"git\")`."),
    ("What does `copytree(dirs_exist_ok=True)` do?", "(3.8+) Copies into an existing destination instead of raising."),
]),

X(17, "How do you use `sqlite3` from Python safely", terms=[
    ("Parameterized query", "SQL with placeholders whose values are sent separately, so they cannot change the query structure."),
    ("`autocommit`", "(3.12+) connection attribute that selects PEP 249-compliant transaction control."),
], pitfall="""Using the connection as a context manager and expecting it to close. `with conn:` commits or rolls back a transaction but does not close the connection.""",
follow=[
    ("How do you get rows as dicts?", "`conn.row_factory = sqlite3.Row`, then access by column name."),
    ("How do you use SQLite from multiple threads?", "One connection per thread, or `check_same_thread=False` with your own locking; enable WAL mode for concurrent readers."),
]),

X(18, "What does the `statistics` module offer", terms=[
    ("`pstdev` vs `stdev`", "Population versus sample standard deviation."),
], pitfall="""Using `statistics` on millions of values in a hot path. It is written for correctness with exact arithmetic, not speed; use NumPy for large arrays.""",
follow=[
    ("What does `statistics.quantiles` return?", "n-1 cut points dividing the data into n intervals (quartiles by default)."),
    ("What is `NormalDist` for?", "Normal-distribution math: `cdf`, `inv_cdf`, `overlap`, and building one from samples."),
]),

X(19, "How do you make HTTP requests with only the stdlib", terms=[
    ("`urllib.request.Request`", "Object carrying URL, method, headers and body."),
], pitfall="""Calling `urlopen` without a timeout. The default is to wait forever on an unresponsive server; always pass `timeout=`.""",
follow=[
    ("Why prefer `httpx` or `requests`?", "Connection pooling, simpler JSON handling, sessions, retries, and in httpx's case async and HTTP/2."),
    ("How do you send JSON with urllib?", "Encode it with `json.dumps(...).encode()` and set `Content-Type: application/json`."),
]),

X(20, "What are type hints and are they enforced", terms=[
    ("Static type checker", "A tool that analyzes code without running it: mypy, pyright, pyrefly, ty."),
], pitfall="""Adding type hints but never running a type checker in CI. The hints drift out of date and give readers false confidence.""",
follow=[
    ("Do type hints make code faster?", "Not in CPython; compilers like mypyc and Cython can use them for speed."),
    ("What does `Any` mean?", "An escape hatch that disables checking for that value in both directions."),
]),

X(21, "What is the modern syntax for common type hints", terms=[
    ("`X | None`", "Modern spelling of `Optional[X]` (3.10+)."),
    ("`collections.abc` types", "Preferred for parameter types: `Iterable`, `Sequence`, `Mapping`, `Callable`."),
], pitfall="""Annotating parameters as `list[str]` when any iterable works. Callers then cannot pass tuples or generators; accept `Iterable[str]` and return concrete types.""",
follow=[
    ("What does `tuple[int, ...]` mean?", "A tuple of any length whose items are ints; `tuple[int, str]` is exactly two items."),
    ("How do you annotate a callable?", "`Callable[[int, str], bool]`, or a Protocol with `__call__` for keyword arguments."),
]),

X(22, "What are generics and `TypeVar`", terms=[
    ("Type parameter", "A placeholder type, such as `T` in `def first[T](xs: list[T]) -> T`."),
    ("Bound / constraints", "`T: Number` restricts `T` to subtypes; `T: (int, str)` restricts it to listed types."),
], pitfall="""Using a TypeVar only once in a signature (`def f(x: T) -> None`). It adds nothing; a TypeVar is meaningful only when it links two or more positions.""",
follow=[
    ("What does the `type` statement do?", "Declares a (lazily evaluated) type alias: `type Pair[T] = tuple[T, T]` (3.12+)."),
    ("What is variance?", "Whether `Box[Cat]` is a subtype of `Box[Animal]`; the 3.12 syntax infers it automatically."),
]),

X(23, "What is `typing.Protocol`?", terms=[
    ("Structural typing", "A type matches by shape rather than by declared inheritance."),
], pitfall="""Defining huge protocols with many methods. Keep them small (one or two methods), like `SupportsRead` or `Sized`, so many types satisfy them.""",
follow=[
    ("Can a protocol include attributes?", "Yes, declare them with annotations in the protocol body."),
    ("What stdlib protocols exist?", "`typing.SupportsInt`, `SupportsAbs`, `collections.abc.Iterable`, `Sized`, `Hashable`, and others."),
]),

X(24, "What are `TypedDict` and `Literal`", terms=[
    ("`Required` / `NotRequired`", "Mark individual TypedDict keys as required or optional."),
    ("`ReadOnly`", "(3.13+) Marks TypedDict keys as not to be modified."),
], pitfall="""Expecting `TypedDict` to validate JSON at runtime. At runtime it is a plain dict; use pydantic's `TypeAdapter` or msgspec to validate.""",
follow=[
    ("How do you narrow a `Literal` type?", "Compare with `==` or use `match`; checkers narrow the type in each branch."),
    ("How do you type `**kwargs` with specific keys?", "`**kwargs: Unpack[MyTypedDict]` (PEP 692)."),
]),

X(25, "How do you type a decorator correctly", terms=[
    ("`ParamSpec`", "Captures a callable's parameter list so a wrapper can expose the same signature."),
    ("`Concatenate`", "Adds or removes leading parameters from a `ParamSpec`."),
], pitfall="""Typing a decorator's return as `Callable[..., Any]`. Every decorated function loses its argument checking, which silently weakens type coverage across the codebase.""",
follow=[
    ("What is the 3.12 syntax?", "`def deco[**P, R](fn: Callable[P, R]) -> Callable[P, R]:`."),
    ("How do you type a decorator that injects the first argument?", "Accept `Callable[Concatenate[Session, P], R]` and return `Callable[P, R]`."),
]),

X(26, "What does `from __future__ import annotations` do", terms=[
    ("PEP 649/749", "Deferred evaluation of annotations, the default in 3.14."),
    ("Forward reference", "A reference to a name defined later in the file."),
], pitfall="""Keeping `from __future__ import annotations` and runtime-annotation libraries together. String annotations can fail to resolve in libraries like pydantic when names are only imported under `TYPE_CHECKING`.""",
follow=[
    ("How do you read annotations safely in 3.14?", "`annotationlib.get_annotations(obj, format=Format.FORWARDREF)` tolerates undefined names."),
    ("Will the `__future__` import be removed?", "It is expected to be deprecated eventually, but it still works in 3.14."),
]),

X(27, "What are `Final`, `ClassVar` and `@override`", terms=[
    ("`ClassVar`", "Marks a class-level attribute that instances should not set."),
], pitfall="""Writing `x: Final[int] = 3` in a dataclass and expecting a class constant. Type checkers treat it like a class-level constant, but `@dataclass` still makes it an instance field with a default. Use `ClassVar` (or a module-level constant) for real constants.""",
follow=[
    ("What does `@override` catch?", "A method marked `@override` that does not actually override anything, such as after a base-class rename."),
    ("Is `@override` enforced at runtime?", "No; it only sets `__override__ = True` for introspection."),
]),

X(28, "How do you check types at runtime", terms=[
    ("`typeguard` / `beartype`", "Libraries that check annotations when functions are called."),
    ("`TypeIs` / `TypeGuard`", "Return annotations for user-defined narrowing functions."),
], pitfall="""Adding runtime type checking to every internal function. It slows code down; validate at trust boundaries (API input, config, files).""",
follow=[
    ("Can `isinstance` check `list[int]`?", "No; `isinstance(x, list[int])` raises `TypeError`. Check the container and elements separately."),
    ("What is `TypeIs` (3.13)?", "Like `TypeGuard` but narrows in both the true and false branches."),
]),

X(29, "What major features arrived in Python 3.8 to 3.11", terms=[
    ("Faster CPython", "The 3.11 project that added the specializing adaptive interpreter, making code 10-60% faster."),
], pitfall="""Using new syntax in a library that still supports older Pythons. Check `requires-python` and test on the oldest supported version in CI.""",
follow=[
    ("What were the key 3.11 additions?", "Exception groups and `except*`, `TaskGroup`, `tomllib`, `Self`, better error locations, and the big speedup."),
    ("How do you find which Python versions are still supported?", "The devguide's status page; each release gets about five years of support."),
]),

X(30, "What major features arrived in Python 3.12, 3.13 and 3.14", terms=[
    ("PEP 695", "Type-parameter syntax and the `type` statement (3.12)."),
    ("PEP 779", "Made the free-threaded build officially supported in 3.14."),
], pitfall="""Assuming the 3.13 experimental JIT makes code faster. It is off by default and gives small gains so far; measure before relying on it.""",
follow=[
    ("What did 3.13 change in the REPL?", "A new interactive shell with color, multi-line editing and paste mode."),
    ("What is new for debugging in 3.14?", "Safe external debugger attach (PEP 768) and the `python -m pdb -p PID` option."),
]),

X(31, "What are template strings (t-strings)", terms=[
    ("`Template`", "Object holding static string parts and `Interpolation` objects, iterable in order."),
    ("`Interpolation`", "Holds `value`, `expression`, `conversion` and `format_spec` for one `{...}` field."),
], pitfall="""Expecting a t-string to be a string. `t\"...\"` has no `str` methods and does not format itself; a processing function must render it.""",
follow=[
    ("What are t-strings good for?", "Safe SQL, HTML escaping, structured logging and shell commands, where each value needs processing."),
    ("Can you convert a Template to a plain string?", "Yes, by writing a renderer that joins the strings and formatted values; there is no built-in `str()` rendering."),
]),

X(32, "What is `Self` type", terms=[
    ("`Self`", "Refers to the type of the current instance, including subclasses."),
], pitfall="""Annotating fluent methods with the class name (`-> Builder`). Subclasses calling them then lose their own type; use `Self`.""",
follow=[
    ("How was this done before 3.11?", "With a bound TypeVar: `T = TypeVar(\"T\", bound=\"Builder\")` and `def m(self: T) -> T`."),
    ("Can `Self` be used in classmethods?", "Yes, for alternate constructors: `def from_json(cls, s: str) -> Self`."),
]),

X(33, "What is `tomllib`", terms=[
    ("TOML", "Tom's Obvious Minimal Language: a config format with typed values and tables."),
], pitfall="""Opening the TOML file in text mode for `tomllib.load`. It requires binary mode (`\"rb\"`) and raises `TypeError` otherwise.""",
follow=[
    ("How do you parse a TOML string?", "`tomllib.loads(text)`."),
    ("Which TOML types map to Python?", "Tables become dicts, arrays lists, and date/time values become `datetime`, `date` or `time` objects."),
]),

X(34, "What is the difference between `mypy` and `pyright`", terms=[
    ("Strict mode", "A set of stricter checks (no implicit `Any`, full annotations)."),
    ("Baseline", "Recording existing errors so CI fails only on new ones."),
], pitfall="""Turning on strict mode for a large untyped codebase in one step. Thousands of errors get suppressed with `# type: ignore`; adopt per module, strictest on new code.""",
follow=[
    ("What are newer Rust-based checkers?", "Astral's `ty` and Meta's `pyrefly`, which aim for much faster checking."),
    ("How do you type third-party libraries without hints?", "Install stub packages (`types-requests`) or write `.pyi` stubs."),
]),

X(35, "What does `@dataclass(slots=True, frozen=True)`", terms=[
    ("`kw_only`", "Makes fields keyword-only; `KW_ONLY` sentinel makes only later fields keyword-only."),
], pitfall="""Using `slots=True` with a zero-argument `super()` in methods on 3.10-3.13. The decorator creates a new class, breaking the `__class__` cell; it works on 3.14.""",
follow=[
    ("Does `frozen=True` make instances hashable?", "Yes, with `eq=True` (the default) it generates `__hash__`."),
    ("How do you set a field in `__post_init__` of a frozen dataclass?", "`object.__setattr__(self, \"field\", value)`."),
]),

X(36, "What are `NewType` and `Annotated`", terms=[
    ("`NewType`", "Creates a distinct type for checkers; at runtime it is an identity function returning the value."),
    ("`Annotated`", "Attaches metadata to a type, such as `Annotated[int, Gt(0)]`, used by pydantic and FastAPI."),
], pitfall="""Subclassing a `NewType` or using it in `isinstance`. Neither works; it is not a real class. Use a real subclass if you need runtime distinction.""",
follow=[
    ("What do type checkers do with `Annotated` metadata?", "They ignore it; only libraries that read it at runtime use it."),
    ("How does FastAPI use `Annotated`?", "`Annotated[str, Query(max_length=50)]` declares parameter source and validation."),
]),
]
