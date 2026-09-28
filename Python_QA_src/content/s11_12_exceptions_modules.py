QUESTIONS = [

# =============== 11. EXCEPTIONS & ERROR HANDLING ===============
Q(11, "Easy", "How does `try` / `except` / `else` / `finally` work?",
"""`try` runs code that may fail; `except` handles matching exceptions; `else` runs only if no exception occurred (keep the `try` block minimal and put follow-up code here); `finally` always runs, for cleanup.""",
r'''
def parse(s):
    try:
        n = int(s)
    except ValueError as e:
        print(f"  bad input: {e}")
    else:
        print(f"  parsed {n}")
    finally:
        print("  finally runs either way")
parse("42"); parse("forty-two")
'''),

Q(11, "Easy", "How do you catch multiple exception types?",
"""Use a tuple in one clause, `except (KeyError, IndexError) as e:`, or separate clauses for different handling. Clauses are checked top to bottom, so put specific exceptions before general ones.""",
r'''
def lookup(data, key):
    try:
        return data[key]
    except (KeyError, IndexError) as e:
        return f"missing: {type(e).__name__}"
    except TypeError:
        return "wrong key type"
print(lookup({"a": 1}, "b"), lookup([1], 5), lookup([1], "x"))
'''),

Q(11, "Moderate", "Why is a bare `except:` (or `except Exception: pass`) bad?",
"""A bare `except:` also catches `KeyboardInterrupt` and `SystemExit`, so Ctrl+C and `sys.exit()` stop working. Swallowing errors silently hides bugs. Catch the narrowest exception you can handle, and log or re-raise the rest.""",
r'''
import sys
try:
    sys.exit(3)
except:                       # catches SystemExit too!
    print("exit was swallowed; the program keeps running")
print(issubclass(KeyboardInterrupt, Exception), issubclass(KeyboardInterrupt, BaseException))
'''),

Q(11, "Moderate", "Describe Python's exception hierarchy.",
"""`BaseException` is the root. Directly under it: `SystemExit`, `KeyboardInterrupt`, `GeneratorExit`, `BaseExceptionGroup` and `Exception`. Almost everything else derives from `Exception`: `ArithmeticError` (`ZeroDivisionError`), `LookupError` (`KeyError`, `IndexError`), `OSError` (`FileNotFoundError`, `PermissionError`, `TimeoutError`), `ValueError` (`UnicodeError`), `TypeError`, `AttributeError`, `ImportError` (`ModuleNotFoundError`), `RuntimeError` (`RecursionError`, `NotImplementedError`).""",
r'''
for exc in (ZeroDivisionError, KeyError, FileNotFoundError, ModuleNotFoundError, RecursionError):
    print(exc.__name__.ljust(20), " -> ".join(c.__name__ for c in exc.__mro__[1:-1]))
'''),

Q(11, "Easy", "How do you raise an exception?",
"""`raise ExceptionType("message")`. A bare `raise` inside an `except` block re-raises the current exception with its original traceback.""",
r'''
def withdraw(balance, amount):
    if amount <= 0:
        raise ValueError(f"amount must be positive, got {amount}")
    if amount > balance:
        raise RuntimeError("insufficient funds")
    return balance - amount
try:
    withdraw(100, -5)
except ValueError as e:
    print("ValueError:", e)
'''),

Q(11, "Moderate", "How do you create custom exceptions?",
"""Subclass `Exception` (never `BaseException`). Create a base exception for your library/app and specific subclasses, and attach useful data as attributes. Callers can then catch broadly or narrowly.""",
r'''
class PaymentError(Exception):
    """Base class for payment failures."""
class CardDeclined(PaymentError):
    def __init__(self, code, message="card declined"):
        super().__init__(f"{message} (code {code})")
        self.code = code
try:
    raise CardDeclined("51")
except PaymentError as e:
    print(type(e).__name__, "|", e, "| code:", e.code)
'''),

Q(11, "Moderate", "What is exception chaining (`raise ... from ...`)?",
"""`raise NewError(...) from err` sets `__cause__`, so the traceback shows "The above exception was the direct cause...". Raising inside an `except` without `from` sets `__context__` implicitly. `from None` hides the original, for example to hide implementation details.""",
r'''
class ConfigError(Exception): pass
def load(cfg):
    try:
        return int(cfg["port"])
    except (KeyError, ValueError) as e:
        raise ConfigError("invalid port setting") from e
try:
    load({"port": "eighty"})
except ConfigError as e:
    print(e, "| caused by:", repr(e.__cause__))
'''),

Q(11, "Moderate", "What is the difference between `raise` and `raise e` inside an `except` block?",
"""Bare `raise` re-raises the active exception unchanged. `raise e` re-raises the same object but adds the current line to its traceback. Use bare `raise` to preserve the original traceback cleanly."""),

Q(11, "Moderate", "EAFP vs LBYL: which style does Python prefer?",
"""**EAFP** ("Easier to Ask Forgiveness than Permission"): try the operation and handle the exception. **LBYL** ("Look Before You Leap"): check first. Python favours EAFP: it's often faster when failures are rare and avoids race conditions (a file can disappear between the check and the open).""",
r'''
config = {"host": "db"}
# LBYL
port = config["port"] if "port" in config else 5432
# EAFP
try:
    port2 = config["port"]
except KeyError:
    port2 = 5432
print(port, port2, config.get("port", 5432))
'''),

Q(11, "Moderate", "Does `finally` run if the `try` block returns? What if `finally` also returns?",
"""`finally` always runs, even after `return`, `break` or an exception. If `finally` itself executes `return`, it **overrides** the earlier return value and even swallows an in-flight exception. Python 3.14 warns about `return` in `finally` (PEP 765); avoid it.""",
r'''
import warnings
warnings.simplefilter("ignore", SyntaxWarning)
src = """
def f():
    try:
        return "from try"
    finally:
        print("  finally runs")
def g():
    try:
        1 / 0
    finally:
        return "finally swallowed the exception"
print(f()); print(g())
"""
exec(compile(src, "<demo>", "exec"))
'''),

Q(11, "Moderate", "What does `assert` do and when should you not use it?",
"""`assert cond, msg` raises `AssertionError` if `cond` is false. Asserts are **removed** when Python runs with `-O`, so never use them for input validation, security checks or anything that must always run. Use them for internal invariants and tests.""",
r'''
import subprocess, sys
code = "assert 1 == 2, 'invariant broken'; print('asserts were skipped')"
for flags in ([], ["-O"]):
    r = subprocess.run([sys.executable, *flags, "-c", code], capture_output=True, text=True)
    print(flags or "normal", "->", (r.stdout or r.stderr.strip().splitlines()[-1]).strip())
'''),

Q(11, "Moderate", "How do you log an exception with its traceback?",
"""Inside an `except` block call `logger.exception("message")` (logs at ERROR level with traceback) or pass `exc_info=True` to any log call. `traceback.format_exc()` returns the traceback as a string.""",
r'''
import logging, sys
logging.basicConfig(stream=sys.stdout, format="%(levelname)s %(message)s")
log = logging.getLogger("orders")
try:
    {}["missing"]
except KeyError:
    log.exception("failed to load order")
'''),

Q(11, "Difficult", "What are exception groups and `except*` (Python 3.11+)?",
"""`ExceptionGroup` bundles several exceptions, e.g. from concurrent tasks in `asyncio.TaskGroup`. `except* Type` handles the matching subset while unmatched exceptions continue to propagate. Several `except*` clauses can each run.""",
r'''
def run_all():
    errors = [ValueError("bad sku"), TimeoutError("inventory slow"), ValueError("bad qty")]
    raise ExceptionGroup("checkout failed", errors)
try:
    run_all()
except* ValueError as eg:
    print("validation:", [str(e) for e in eg.exceptions])
except* TimeoutError as eg:
    print("timeouts:", [str(e) for e in eg.exceptions])
'''),

Q(11, "Moderate", "What is `add_note()` on exceptions?",
"""Since 3.11, `exc.add_note(text)` attaches extra context that is printed with the traceback, without wrapping the exception in a new type.""",
r'''
import traceback
try:
    try:
        int("x")
    except ValueError as e:
        e.add_note("while parsing row 17 of orders.csv")
        raise
except ValueError as e:
    print("".join(traceback.format_exception_only(e)).strip())
'''),

Q(11, "Moderate", "How do `warnings` differ from exceptions?",
"""Warnings signal something noteworthy (deprecation, likely mistake) without stopping the program. `warnings.warn(msg, DeprecationWarning, stacklevel=2)` issues one; filters can ignore them, show them once, or turn them into errors (`-W error`), which is useful in tests.""",
r'''
import warnings
def old_api():
    warnings.warn("old_api() is deprecated; use new_api()", DeprecationWarning, stacklevel=2)
    return 1
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    old_api()
print(caught[0].category.__name__, "-", caught[0].message)
'''),

Q(11, "Difficult", "How do you retry an operation on transient errors properly?",
"""Retry only idempotent operations, only on transient errors (timeouts, 503), with a maximum attempt count, exponential backoff and jitter, and re-raise the last error. Libraries like `tenacity` implement this.""",
r'''
import random, time
def with_retry(fn, attempts=4, base=0.01, retry_on=(TimeoutError, ConnectionError)):
    for i in range(1, attempts + 1):
        try:
            return fn()
        except retry_on as e:
            if i == attempts: raise
            sleep = random.uniform(0, base * 2 ** i)
            print(f"attempt {i} failed ({e}); sleeping {sleep * 1000:.0f} ms")
            time.sleep(sleep)
random.seed(3)
results = iter([TimeoutError("slow"), ConnectionError("reset"), "200 OK"])
def call():
    r = next(results)
    if isinstance(r, Exception): raise r
    return r
print(with_retry(call))
'''),

Q(11, "Moderate", "What happens to an exception raised in a `with` block?",
"""The context manager's `__exit__` receives it. If `__exit__` returns a falsy value, the exception propagates after cleanup; files are still closed and locks still released."""),

Q(11, "Difficult", "What is the cost of exceptions in Python?",
"""Entering a `try` block is almost free (zero-cost exceptions since 3.11). Raising and catching is relatively expensive (creating the exception and traceback). So EAFP is fine when failures are rare, but don't use exceptions for common control flow in hot loops.""",
r'''
import timeit
d = {"a": 1}
def eafp_hit():
    try: return d["a"]
    except KeyError: return 0
def eafp_miss():
    try: return d["b"]
    except KeyError: return 0
def lbyl_miss(): return d["b"] if "b" in d else 0
for f in (eafp_hit, eafp_miss, lbyl_miss):
    print(f.__name__.ljust(10), "%.0f ns" % (timeit.timeit(f, number=200_000) / 200_000 * 1e9))
'''),

Q(11, "Moderate", "What does `sys.exit()` actually do?",
"""It raises `SystemExit`, which unwinds the stack (running `finally` blocks and context managers) and exits with the given status code. `os._exit()` exits immediately without cleanup (used in forked children).""",
r'''
import sys
try:
    sys.exit(2)
except SystemExit as e:
    print("caught SystemExit with code", e.code)
'''),

# =============== 12. MODULES, PACKAGES & IMPORTS ===============
Q(12, "Easy", "What is the difference between a module and a package?",
"""A **module** is a single `.py` file (or a compiled extension). A **package** is a directory of modules, usually with an `__init__.py`, imported with dotted names (`package.module`). Without `__init__.py` it's a namespace package.""",
r'''
import json, json.decoder, os
print(json.__file__.endswith("__init__.py"), hasattr(json, "__path__"))
print(json.decoder.__name__, hasattr(os, "__path__"))
'''),

Q(12, "Easy", "What are the different ways to import?",
"""- `import module` then `module.name`
- `import package.module as alias`
- `from module import name1, name2`
- `from package import module`
- relative inside packages: `from . import sibling`, `from ..utils import helper`
- `from module import *` imports public names (those in `__all__` if defined); avoid it outside the REPL.""",
r'''
import math
import collections.abc as cabc
from datetime import date, timedelta
print(math.pi, cabc.Mapping.__name__, date(2026, 9, 28) + timedelta(days=3))
'''),

Q(12, "Moderate", "How does Python find a module when you import it?",
"""It checks `sys.modules` (cache) first. If not found, finders on `sys.meta_path` search built-in modules, frozen modules, then each directory in `sys.path` (the script's directory, `PYTHONPATH`, the standard library, site-packages). The module is executed once and cached.""",
r'''
import sys
print(type(sys.path).__name__, len(sys.path) > 0, "json" in sys.modules)
import json
print("json" in sys.modules, [getattr(f, "__name__", type(f).__name__) for f in sys.meta_path])
'''),

Q(12, "Moderate", "What happens when you import the same module twice?",
"""The module body runs only the first time; later imports return the cached object from `sys.modules`. To re-execute (e.g. during development), use `importlib.reload(module)`.""",
r'''
import sys, types, importlib, tempfile, pathlib
d = pathlib.Path(tempfile.mkdtemp()); sys.path.insert(0, str(d))
(d / "greet.py").write_text('print("  module body executing")\nVALUE = 1\n')
import greet
import greet
print("imported twice, body ran once; VALUE =", greet.VALUE)
(d / "greet.py").write_text('print("  reloaded body")\nVALUE = 2\n')
importlib.invalidate_caches(); importlib.reload(greet)
print("after reload VALUE =", greet.VALUE)
'''),

Q(12, "Moderate", "What is `__init__.py` for?",
"""It marks a directory as a regular package and runs on first import of the package. Use it to expose a clean public API (`from .client import Client`), set `__all__`, or define package-level constants. Keep it light: heavy imports there slow every import of the package."""),

Q(12, "Moderate", "What is `__all__`?",
"""A list of public names in a module. It controls what `from module import *` imports and documents the public API for tools and readers. It doesn't prevent explicit imports of other names.""",
r'''
import sys, types
mod = types.ModuleType("shapes")
exec("__all__ = ['area']\ndef area(): return 1\ndef _helper(): pass\ndef debug(): pass", mod.__dict__)
sys.modules["shapes"] = mod
ns = {}
exec("from shapes import *", ns)
print(sorted(k for k in ns if not k.startswith("__")))
'''),

Q(12, "Difficult", "What causes circular imports, and how do you fix them?",
"""Module A imports B while B imports A. The second import gets a **partially initialized** module, so names defined later aren't there yet and you get `ImportError: cannot import name ...` (older versions add "most likely due to a circular import"). Fixes: move shared code into a third module, import inside the function that needs it, import the module (`import a`) instead of names (`from a import x`), or restructure dependencies.""",
r'''
import sys, tempfile, pathlib, subprocess
d = pathlib.Path(tempfile.mkdtemp())
(d / "orders.py").write_text("from customers import Customer\nclass Order: pass\n")
(d / "customers.py").write_text("from orders import Order\nclass Customer: pass\n")
r = subprocess.run([sys.executable, "-c", "import orders"], cwd=d, capture_output=True, text=True)
print(r.stderr.strip().splitlines()[-1].split(" (")[0])
'''),

Q(12, "Moderate", "Absolute vs relative imports?",
"""Absolute imports use the full path from the project root (`from myapp.utils import slugify`) and are clearer; PEP 8 recommends them. Relative imports (`from .utils import slugify`) work only inside packages and are handy for deep package-internal references. Running a package file directly as a script breaks relative imports; use `python -m package.module`."""),

Q(12, "Moderate", "What is the difference between `python script.py` and `python -m package.module`?",
"""`-m` runs a module found on `sys.path` as `__main__`, with its package context set, so relative imports work and the current directory (not the script's) is on `sys.path`. It's also how you run tools: `python -m pip`, `python -m venv`, `python -m http.server`, `python -m pytest`."""),

Q(12, "Easy", "What is a virtual environment and why use one?",
"""An isolated Python environment with its own `site-packages`, created with `python -m venv .venv`. It keeps project dependencies separate, avoids version conflicts and makes installs reproducible. Tools like `uv`, Poetry and pipenv manage environments and lock files.""",
r'''
import sys
print("in a venv:", sys.prefix != sys.base_prefix)
'''),

Q(12, "Moderate", "How do you manage dependencies in a Python project today?",
"""Declare dependencies in `pyproject.toml` (PEP 621), pin exact versions in a lock file (`uv.lock`, `poetry.lock`, or `pip-tools`' `requirements.txt`), and install into a virtual environment. Separate runtime and dev dependencies, and keep the lock file in version control."""),

Q(12, "Moderate", "What is `pyproject.toml`?",
"""The standard project configuration file (PEPs 518, 517, 621): build-system requirements, project metadata (name, version, dependencies, entry points), and settings for tools such as Ruff, pytest, mypy and Black. It replaces `setup.py` and `setup.cfg` for most projects."""),

Q(12, "Difficult", "How do you import a module dynamically by name?",
"""`importlib.import_module("package.module")` returns the module. Combined with `getattr` it loads classes named in config strings (how Django loads backends from settings).""",
r'''
import importlib
def load_object(path: str):
    module_path, _, attr = path.rpartition(".")
    return getattr(importlib.import_module(module_path), attr)
Decoder = load_object("json.JSONDecoder")
dumps = load_object("json.dumps")
print(Decoder.__name__, dumps({"ok": True}))
'''),

Q(12, "Difficult", "What is `__name__`, `__file__`, `__package__` and `__spec__` in a module?",
"""`__name__`: the module's import name (`"__main__"` when run as a script). `__file__`: path it was loaded from. `__package__`: the package used for relative imports. `__spec__`: the `ModuleSpec` describing how it was found and loaded.""",
r'''
import json.decoder as m
print(m.__name__, m.__package__, m.__spec__.origin.endswith("decoder.py"))
'''),

Q(12, "Moderate", "What are `.pyc` files and `__pycache__`?",
"""Compiled bytecode caches. On import, CPython writes `module.cpython-3XX.pyc` into `__pycache__` and reuses it if the source hasn't changed, which speeds up later imports. They are safe to delete and shouldn't be committed."""),

Q(12, "Difficult", "How can you make an import lazy to speed up startup?",
"""Import heavy modules inside the function that needs them, use a module-level `__getattr__` (PEP 562) to load submodules on first access, or `importlib.util.LazyLoader`. Measure with `python -X importtime`.""",
r'''
import subprocess, sys
r = subprocess.run([sys.executable, "-X", "importtime", "-c", "import json"], capture_output=True, text=True)
lines = [l for l in r.stderr.splitlines() if "json" in l]
print(lines[-1].split("|")[0].strip() if lines else "n/a", "(self us) for json")
def export_excel(rows):
    import csv          # imported only when this rarely-used function runs
    return csv.__name__
print(export_excel([]))
'''),

Q(12, "Moderate", "What is `site-packages` and how does `pip install -e .` work?",
"""`site-packages` is where third-party packages are installed. An editable install (`pip install -e .`) installs a pointer (a `.pth` file or import hook) to your source directory, so code changes take effect without reinstalling."""),

Q(12, "Moderate", "What is a namespace package?",
"""A package without `__init__.py` (PEP 420) that can be split across several directories or distributions, all contributing to one dotted namespace, e.g. `google.cloud.storage` and `google.cloud.bigquery` installed separately.""",
r'''
import sys, tempfile, pathlib
a, b = pathlib.Path(tempfile.mkdtemp()), pathlib.Path(tempfile.mkdtemp())
(a / "acme" / "billing").mkdir(parents=True); (a / "acme" / "billing" / "__init__.py").write_text("NAME='billing'")
(b / "acme" / "shipping").mkdir(parents=True); (b / "acme" / "shipping" / "__init__.py").write_text("NAME='shipping'")
sys.path[:0] = [str(a), str(b)]
import acme.billing, acme.shipping
print(acme.billing.NAME, acme.shipping.NAME, len(list(acme.__path__)), "directories in acme.__path__")
'''),

]
