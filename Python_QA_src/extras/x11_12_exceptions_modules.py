EXTRAS = [

X(0, "How does `try` / `except` / `else` / `finally`", terms=[
    ("`else` clause", "Runs only when the `try` block raised nothing; exceptions inside it are not caught by the preceding `except`."),
    ("`finally` clause", "Runs on every exit path: normal, exception, `return`, `break`, `continue`."),
], pitfall="""Putting too much code in the `try` block. An `except KeyError` then also catches unrelated `KeyError`s from lines you did not mean to protect; move the rest into `else`.""",
follow=[
    ("What order must the clauses appear in?", "`try`, one or more `except`, optional `else`, optional `finally`; or `try`/`finally` alone."),
    ("Is the exception variable available after the `except` block?", "No; `except E as e` deletes `e` at the end of the block to avoid reference cycles with the traceback."),
]),

X(1, "How do you catch multiple exception types", terms=[
    ("Handler order", "The first matching `except` clause wins, so put specific exceptions before general ones."),
], pitfall="""Writing `except KeyError, IndexError:` (Python 2 syntax). In Python 3 that is a `SyntaxError` before 3.14; in 3.14, PEP 758 allows unparenthesized lists only without `as`. Use a tuple for clarity.""",
follow=[
    ("Can you catch an exception by a common base?", "Yes; `except LookupError` catches both `KeyError` and `IndexError`."),
    ("How do you catch everything except system-exit signals?", "`except Exception`, which excludes `KeyboardInterrupt`, `SystemExit` and `GeneratorExit`."),
]),

X(2, "Why is a bare `except:`", terms=[
    ("Swallowing", "Catching an exception and discarding it without logging or re-raising."),
], pitfall="""`except Exception: return None` in a data-access function. Callers cannot tell \"not found\" from \"database is down\", and failures surface much later as confusing `None` errors.""",
follow=[
    ("When is catching broad `Exception` acceptable?", "At a top-level boundary (request handler, worker loop, CLI entry point) where you log it and continue or exit cleanly."),
    ("How do linters flag this?", "Ruff/flake8 rules such as E722 (bare except), BLE001 (blind except) and S110 (try-except-pass)."),
]),

X(3, "Describe Python's exception hierarchy", terms=[
    ("`BaseException`", "Root of all exceptions; direct subclasses other than `Exception` are meant to end the program or generator."),
    ("`OSError` family", "`FileNotFoundError`, `PermissionError`, `TimeoutError`, `ConnectionError` and more, chosen from `errno`."),
], pitfall="""Catching `IOError` or `EnvironmentError` separately from `OSError`. Since 3.3 they are aliases of `OSError`, so separate handlers are redundant.""",
follow=[
    ("Where does `StopIteration` sit?", "Under `Exception`; `StopAsyncIteration` too."),
    ("How do you print the hierarchy?", "Walk `BaseException.__subclasses__()` recursively, or see the tree in the \"Built-in Exceptions\" docs."),
]),

X(4, "How do you raise an exception", terms=[
    ("Re-raise", "A bare `raise` inside an `except` re-raises the exception currently being handled."),
], pitfall="""Raising a class with arguments inconsistently, or `raise \"error\"`. Only `BaseException` instances or subclasses can be raised; strings raise `TypeError`.""",
follow=[
    ("What does `raise ValueError` (no parentheses) do?", "Python instantiates the class with no arguments and raises it."),
    ("What happens with a bare `raise` outside an `except`?", "`RuntimeError: No active exception to reraise`."),
]),

X(5, "How do you create custom exceptions", terms=[
    ("Exception hierarchy per package", "One base class (`MyLibError`) with specific subclasses, so callers can catch at the level they need."),
], pitfall="""Overriding `__init__` with extra required arguments and not calling `super().__init__(message)`. The exception then prints badly and can fail to unpickle when crossing process boundaries.""",
follow=[
    ("Should custom exceptions end in \"Error\"?", "Yes by PEP 8 convention when they signal an error."),
    ("When should you reuse a built-in exception instead?", "When the meaning matches exactly, such as `ValueError` for a bad argument value or `KeyError` for a missing key."),
]),

X(6, "What is exception chaining", terms=[
    ("`__cause__`", "Set by `raise ... from err`; shown as \"direct cause\"."),
    ("`__context__`", "Set automatically when raising inside `except`; shown as \"During handling ... another exception occurred\"."),
], pitfall="""Translating exceptions without `from`, so the traceback suggests a bug in the handler rather than a deliberate translation.""",
follow=[
    ("What does `raise X from None` do?", "Suppresses the context display (`__suppress_context__ = True`); use it when the original is irrelevant to the caller."),
    ("Is the original exception lost with `from None`?", "No; it is still stored in `__context__`, just not printed."),
]),

X(7, "What is the difference between `raise` and `raise e`", terms=[
    ("Traceback", "The chain of frames from where the exception was raised; stored in `e.__traceback__`."),
], pitfall="""Using `raise e` and then being confused by tracebacks that include the re-raise line. Use bare `raise` to re-raise unchanged.""",
follow=[
    ("How do you raise with a specific traceback?", "`raise e.with_traceback(tb)`."),
    ("Does `raise e` lose the original frames?", "No; it appends the current frame to the existing traceback."),
]),

X(8, "EAFP vs LBYL", terms=[
    ("TOCTOU", "Time-of-check to time-of-use race: the state can change between the check and the action."),
], pitfall="""Using EAFP where the exception is the common case in a hot loop. Raising is costly; when failures are frequent, a cheap check (`dict.get`, `in`) is faster.""",
follow=[
    ("Why is `if os.path.exists(p): open(p)` racy?", "The file can be deleted between the check and the open; `try: open(p) except FileNotFoundError` avoids that."),
    ("Is LBYL ever clearer?", "Yes, for input validation and preconditions where failing early with a clear message helps."),
]),

X(9, "Does `finally` run if the `try` block returns", terms=[
    ("Return override", "A `return` in `finally` replaces any pending return value and cancels any exception."),
], pitfall="""`return`, `break` or `continue` inside `finally`, which silently swallows exceptions. Python 3.14 emits a `SyntaxWarning` for it (PEP 765).""",
follow=[
    ("Does `finally` run on `os._exit()`?", "No; `os._exit` terminates immediately without unwinding."),
    ("Does `finally` run when a thread is killed or the process gets SIGKILL?", "No, nothing runs after SIGKILL."),
]),

X(10, "What does `assert` do", terms=[
    ("`__debug__`", "True unless Python runs with `-O`; asserts compile to `if __debug__: ...`."),
], pitfall="""`assert (x > 0, \"msg\")` with parentheses. That asserts a non-empty tuple, which is always true; Python warns about it.""",
follow=[
    ("What are asserts good for?", "Internal invariants and developer assumptions, and test assertions in pytest."),
    ("What should you use for argument validation instead?", "An explicit `if ...: raise ValueError(...)`."),
]),

X(11, "How do you log an exception with its traceback", terms=[
    ("`logger.exception`", "Logs at ERROR level and includes the current exception's traceback."),
    ("`exc_info`", "Argument that attaches exception info to any log call (`exc_info=True` or an exception instance)."),
], pitfall="""Logging and then re-raising at every layer. The same traceback appears many times in the logs; log once at the boundary that handles it.""",
follow=[
    ("How do you get the traceback as a string?", "`traceback.format_exc()`, or `\"\".join(traceback.format_exception(e))`."),
    ("How do you log an exception outside the `except` block?", "Pass the exception object: `logger.error(\"msg\", exc_info=e)`."),
]),

X(12, "What are exception groups", terms=[
    ("`ExceptionGroup`", "An exception holding several exceptions (and nested groups)."),
    ("`except*`", "Handles matching exceptions inside a group; each `except*` clause can run, and unhandled ones re-raise as a group."),
], pitfall="""Using a plain `except ValueError` around `asyncio.TaskGroup` code. Errors arrive wrapped in an `ExceptionGroup`, so the handler does not match; use `except*`.""",
follow=[
    ("Can you mix `except` and `except*` in one `try`?", "No; a `try` statement uses one kind only."),
    ("How do you split a group programmatically?", "`eg.split(ValueError)` returns `(matching, rest)`; `eg.subgroup(...)` returns just the matching part."),
]),

X(13, "What is `add_note()`", terms=[
    ("`__notes__`", "List of strings attached to an exception, printed after the message."),
], pitfall="""Wrapping exceptions in new types only to add context. That changes the type callers catch; `add_note` adds context while keeping the type.""",
follow=[
    ("Where are notes useful?", "Adding the file name, row number or request id while re-raising in a loop or pipeline."),
    ("Does pytest show notes?", "Yes, tracebacks display them, which helps with hypothesis failures too."),
]),

X(14, "How do `warnings` differ from exceptions", terms=[
    ("Warning filter", "Rules (`-W`, `PYTHONWARNINGS`, `warnings.filterwarnings`) that ignore, show once or turn warnings into errors."),
    ("`stacklevel`", "Points the warning at the caller's line instead of the library's line."),
], pitfall="""Emitting `DeprecationWarning` from a library and expecting users to see it. It is hidden by default except in `__main__` and test runners; also document the deprecation.""",
follow=[
    ("How do you turn warnings into errors in tests?", "`python -W error` or pytest's `filterwarnings = error` setting."),
    ("What is `warnings.deprecated`?", "A 3.13 decorator (PEP 702) that marks functions or classes as deprecated for both type checkers and runtime."),
]),

X(15, "How do you retry an operation on transient errors", terms=[
    ("Exponential backoff", "Waiting 1, 2, 4, 8, ... seconds between attempts."),
    ("Jitter", "Randomizing delays so many clients do not retry in lockstep."),
    ("Idempotent", "Safe to repeat: doing it twice has the same effect as once."),
], pitfall="""Retrying at several layers (client library, service code, load balancer). Attempts multiply (3 x 3 x 3 = 27) and amplify an outage; retry at one layer only.""",
follow=[
    ("Which errors should not be retried?", "Validation errors, 4xx client errors (except 429 and sometimes 408), and authentication failures."),
    ("Which library is common for this?", "`tenacity` (decorators with stop, wait and retry conditions), or `stamina` built on it."),
]),

X(16, "What happens to an exception raised in a `with` block", terms=[
    ("Exit arguments", "`__exit__(exc_type, exc_value, traceback)`, all `None` when no exception occurred."),
], pitfall="""An exception raised inside `__exit__` itself replaces the original exception, which then only appears as context. Keep cleanup code defensive.""",
follow=[
    ("Does a lock get released if the block raises?", "Yes; `threading.Lock.__exit__` releases it and returns None so the exception propagates."),
    ("How do you see whether cleanup saw an error?", "Check `exc_type is not None` in `__exit__`."),
]),

X(17, "What is the cost of exceptions", terms=[
    ("Zero-cost exceptions", "Since 3.11, a `try` block adds no instructions on the normal path; handlers are found via a table when raising."),
], pitfall="""Using exceptions for normal control flow in tight loops, such as `try: d[k] except KeyError` when most keys are missing. Raising costs microseconds each time.""",
follow=[
    ("How can you measure it?", "`timeit` a function that raises and catches versus one that returns a sentinel."),
    ("What makes raising expensive?", "Creating the exception object, building the traceback and unwinding frames."),
]),

X(18, "What does `sys.exit()` actually do", terms=[
    ("`SystemExit`", "Exception raised by `sys.exit`; its `code` becomes the process exit status."),
    ("`os._exit`", "Exits immediately without cleanup; used in forked children."),
], pitfall="""Calling `sys.exit()` in a worker thread expecting the program to exit. It only ends that thread.""",
follow=[
    ("What exit status does `sys.exit(\"message\")` produce?", "It prints the message to stderr and exits with status 1."),
    ("How do you run cleanup at interpreter exit?", "`atexit.register(fn)`; it does not run on `os._exit` or fatal signals."),
]),

X(19, "What is the difference between a module and a package", terms=[
    ("Regular package", "A directory with `__init__.py`."),
    ("Extension module", "A compiled `.so`/`.pyd` module written in C, C++ or Rust."),
], pitfall="""Naming your file after a stdlib module (`random.py`, `json.py`). The script directory comes first on `sys.path`, so your file shadows the real module; Python 3.13 warns about this in the error message.""",
follow=[
    ("Is a package also a module?", "Yes; a package is a module object with a `__path__` attribute."),
    ("What is a distribution?", "The installable unit on PyPI (a wheel or sdist), which may contain several top-level packages."),
]),

X(20, "What are the different ways to import", terms=[
    ("Wildcard import", "`from m import *`; imports public names (or `__all__`)."),
], pitfall="""Using `from module import *` in application code. It hides where names come from and can silently overwrite existing names.""",
follow=[
    ("Does `from m import x` see later changes to `m.x`?", "No; it binds `x` to the object at import time. Rebinding `m.x` later is not reflected."),
    ("How does this affect mocking?", "Patch where the name is looked up: `mock.patch(\"mymodule.x\")`, not `\"m.x\"`, if `mymodule` did `from m import x`."),
]),

X(21, "How does Python find a module", terms=[
    ("`sys.path`", "List of directories and zip files searched for imports."),
    ("Finder / loader", "A finder locates a module spec; a loader executes the module code."),
], pitfall="""Running a script from inside a package directory. The script's directory becomes `sys.path[0]`, so absolute imports of the package fail; run it with `python -m package.module` from the project root.""",
follow=[
    ("How do you see where a module was loaded from?", "`module.__file__` or `module.__spec__.origin`."),
    ("How do you add a path at runtime?", "`sys.path.insert(0, path)`, but prefer installing the project (`pip install -e .`)."),
]),

X(22, "What happens when you import the same module twice", terms=[
    ("`sys.modules`", "Dict cache of loaded modules keyed by full dotted name."),
    ("`importlib.reload`", "Re-executes a module's code in the existing module object."),
], pitfall="""Expecting `reload` to update objects already imported elsewhere with `from m import x`, or existing instances of old classes. They still refer to the old objects.""",
follow=[
    ("How can the same file be imported as two modules?", "If it is reachable under two names (e.g. `pkg.mod` and `mod` via different `sys.path` entries); then it runs twice with separate state."),
    ("How do you force a fresh import in a test?", "Delete it from `sys.modules` and import again, or use `importlib.reload`."),
]),

X(23, "What is `__init__.py` for", terms=[
    ("Public API surface", "Names re-exported by `__init__.py` so users can write `from pkg import Client`."),
], pitfall="""Importing heavy submodules eagerly in `__init__.py`. Every `import pkg` pays the cost; use a lazy `__getattr__` for rarely used parts.""",
follow=[
    ("Can `__init__.py` be empty?", "Yes, and it often is."),
    ("What runs when you `import pkg.sub`?", "First `pkg/__init__.py`, then `pkg/sub.py`."),
]),

X(24, "What is `__all__`", terms=[
    ("Public name", "A name without a leading underscore, or one listed in `__all__`."),
], pitfall="""Listing a name in `__all__` that does not exist. `from m import *` then raises `AttributeError`; linters can check this.""",
follow=[
    ("Does `__all__` affect `import m`?", "No, only star imports and tooling such as documentation generators and type checkers."),
    ("What goes in `__all__` of a package's `__init__.py`?", "The re-exported public API, which also tells type checkers these imports are intentional re-exports."),
]),

X(25, "What causes circular imports", terms=[
    ("Partially initialized module", "A module object in `sys.modules` whose code has not finished running."),
], pitfall="""\"Fixing\" a cycle by moving imports around until it happens to work. It breaks again on the next refactor; extract the shared code into a third module.""",
follow=[
    ("How can type hints cause cycles, and how do you avoid it?", "Import only for type checking under `if TYPE_CHECKING:`; with 3.14 lazy annotations, no string quotes are needed."),
    ("Why does `import a` often work where `from a import x` fails?", "`import a` only needs the module object, while `from a import x` needs `x` to already be defined."),
]),

X(26, "Absolute vs relative imports", terms=[
    ("Relative import", "`from . import x` or `from ..pkg import y`, resolved against `__package__`."),
], pitfall="""Running a module with relative imports as a script (`python pkg/mod.py`). It fails with `ImportError: attempted relative import with no known parent package`; use `python -m pkg.mod`.""",
follow=[
    ("Are implicit relative imports allowed in Python 3?", "No; `import sibling` inside a package is an absolute import in Python 3."),
    ("When are relative imports reasonable?", "Inside a package that may be renamed or vendored, to avoid hard-coding its name."),
]),

X(27, "What is the difference between `python script.py` and `python -m", terms=[
    ("`sys.path[0]`", "The script's directory with `python script.py`; the current directory with `-m`."),
], pitfall="""Running tools via a bare command (`pip`, `pytest`) that belongs to a different Python than you think. `python -m pip` guarantees it uses the interpreter you invoke.""",
follow=[
    ("What file runs for `python -m pkg`?", "`pkg/__main__.py`."),
    ("Which stdlib modules are useful with `-m`?", "`http.server`, `venv`, `json.tool`, `timeit`, `cProfile`, `pdb`, `zipfile`."),
]),

X(28, "What is a virtual environment", terms=[
    ("`pyvenv.cfg`", "File at the root of a venv pointing to the base interpreter."),
], pitfall="""Committing the `.venv` folder to git or copying it between machines. Virtual environments contain absolute paths; recreate them from the lock file.""",
follow=[
    ("How do you know you are in a venv?", "`sys.prefix != sys.base_prefix`."),
    ("Do you have to activate a venv?", "No; running `.venv/bin/python` (or `.venv\\Scripts\\python.exe`) directly uses it."),
]),

X(29, "How do you manage dependencies", terms=[
    ("Lock file", "Records exact resolved versions (and hashes) of all transitive dependencies for reproducible installs."),
    ("`uv`", "Fast Rust-based tool that handles venvs, installs, lock files and Python versions."),
], pitfall="""Pinning exact versions in a library's `pyproject.toml`. Libraries should declare compatible ranges; only applications lock exact versions.""",
follow=[
    ("What is a dependency group?", "Named groups of development dependencies (PEP 735 `[dependency-groups]`), such as `test` or `lint`, not published with the package."),
    ("How do you check for known vulnerabilities?", "`pip-audit`, or the audit features of your dependency tool or CI."),
]),

X(30, "What is `pyproject.toml`", terms=[
    ("Build backend", "The tool that builds wheels (setuptools, hatchling, flit-core, uv_build, maturin), named in `[build-system]`."),
    ("`[project.scripts]`", "Declares console entry points that become commands on install."),
], pitfall="""Keeping `setup.py`, `setup.cfg` and `pyproject.toml` with conflicting metadata. Move everything to `pyproject.toml`.""",
follow=[
    ("Where do tool settings go?", "Under `[tool.<name>]`, such as `[tool.ruff]`, `[tool.pytest.ini_options]`, `[tool.mypy]`."),
    ("What is a wheel?", "A built, installable zip archive (`.whl`); installs without running build code."),
]),

X(31, "How do you import a module dynamically", terms=[
    ("Plugin loading", "Importing modules named in config or discovered via entry points at runtime."),
    ("Entry points", "Metadata-declared plugin hooks, read with `importlib.metadata.entry_points(group=...)`."),
], pitfall="""Importing module names that come from user input. Imports execute code, so this becomes remote code execution; use an allow-list.""",
follow=[
    ("How do you import a file by path?", "`importlib.util.spec_from_file_location` then `module_from_spec` and `spec.loader.exec_module(module)`."),
    ("Why not use `__import__`?", "It returns the top-level package for dotted names and is awkward; `import_module` is the documented API."),
]),

X(32, "What is `__name__`, `__file__`", terms=[
    ("Module spec", "`ModuleSpec` object recording how a module was found and loaded."),
], pitfall="""Using `__file__` to find data files. It can be missing (zipapps, frozen apps) or point into a zip; use `importlib.resources.files(__package__)`.""",
follow=[
    ("Does every module have `__file__`?", "No; built-in modules and some frozen modules do not."),
    ("What is `__package__` for a top-level module?", "An empty string."),
]),

X(33, "What are `.pyc` files and `__pycache__`", terms=[
    ("Magic number", "Header bytes identifying the bytecode format version, so different Python versions do not share `.pyc` files."),
], pitfall="""Shipping only `.pyc` files to \"protect\" source code. They are easy to decompile and tied to one Python version.""",
follow=[
    ("How do you disable writing bytecode?", "`PYTHONDONTWRITEBYTECODE=1` or `python -B`."),
    ("How do you precompile a tree?", "`python -m compileall src/`."),
]),

X(34, "How can you make an import lazy", terms=[
    ("Module `__getattr__`", "PEP 562 hook called for missing module attributes."),
    ("`python -X importtime`", "Prints import timing for every module."),
], pitfall="""Hiding imports inside functions everywhere for speed. Import errors then appear only at call time, sometimes in production; lazy-load only measured heavy modules.""",
follow=[
    ("What is `importlib.util.LazyLoader`?", "A loader that defers executing the module until first attribute access."),
    ("Is there a language feature for lazy imports?", "PEP 810 proposes explicit `lazy import` syntax, targeted at Python 3.15; until then use the techniques above."),
]),

X(35, "What is `site-packages`", terms=[
    ("Editable install", "Installs a link to your source tree so code edits take effect without reinstalling."),
], pitfall="""Adding new modules or entry points to an editable project and wondering why they do not appear. Metadata changes (entry points, dependencies) require reinstalling.""",
follow=[
    ("How do you find `site-packages`?", "`python -c \"import site; print(site.getsitepackages())\"` or `sysconfig.get_paths()[\"purelib\"]`."),
    ("What is the user site directory?", "A per-user location used by `pip install --user`; avoid it when using venvs."),
]),

X(36, "What is a namespace package", terms=[
    ("PEP 420", "Implicit namespace packages without `__init__.py`."),
], pitfall="""Forgetting `__init__.py` accidentally. Tools like pytest, mypy or packaging may then treat the folder differently or skip it; add it unless you really want a namespace package.""",
follow=[
    ("What is the typical use case?", "Several separately installed distributions sharing one top-level name, such as company plugins under `acme.*`."),
    ("How do you detect one at runtime?", "It has no `__file__`, and its `__path__` is a `_NamespacePath` that can span several directories."),
]),
]
