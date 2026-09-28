QUESTIONS = [

# =============== 15. STANDARD LIBRARY ESSENTIALS ===============
Q(15, "Easy", "How do you work with dates and times correctly?",
"""Use `datetime` with **timezone-aware** values: `datetime.now(timezone.utc)` for storage and arithmetic, `zoneinfo.ZoneInfo("Asia/Kolkata")` (3.9+) for display. Naive datetimes (no tzinfo) cause bugs around DST and across servers. Parse ISO strings with `fromisoformat`, format with `strftime`.""",
r'''
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
utc = datetime(2026, 9, 28, 4, 30, tzinfo=timezone.utc)
print(utc.astimezone(ZoneInfo("Asia/Kolkata")), utc.astimezone(ZoneInfo("America/New_York")).strftime("%d %b %H:%M %Z"))
print("same instant:", datetime.fromisoformat("2026-09-28T10:00:00+05:30") == utc)
print((utc + timedelta(days=45)).date().isoformat())
'''),

Q(15, "Easy", "How do you work with file paths? `os.path` or `pathlib`?",
"""Prefer `pathlib.Path` (object-oriented, cross-platform): `/` joins paths, and it has `.name`, `.stem`, `.suffix`, `.parent`, `.exists()`, `.glob()`, `.read_text()`, `.write_text()`, `.mkdir(parents=True)`. `os.path` still works but is string-based.""",
r'''
from pathlib import Path
import tempfile
root = Path(tempfile.mkdtemp())
report = root / "reports" / "2026" / "q3_sales.csv"
report.parent.mkdir(parents=True, exist_ok=True)
report.write_text("region,total\nIN,100\n", encoding="utf-8")
print(report.name, report.stem, report.suffix, report.parent.name)
print([p.name for p in root.rglob("*.csv")], report.read_text().splitlines()[1])
'''),

Q(15, "Easy", "How do you read and write JSON?",
"""`json.loads`/`json.dumps` for strings, `json.load`/`json.dump` for files. Useful options: `indent`, `sort_keys`, `ensure_ascii=False`, `default=` for unsupported types (datetime, Decimal). JSON has no tuples (they become lists), and dict keys become strings.""",
r'''
import json
from datetime import date
order = {"id": 42, "items": ("pen", "ink"), "date": date(2026, 9, 28), 1: "one"}
text = json.dumps(order, default=str, indent=None)
print(text)
back = json.loads(text)
print(back["items"], list(back.keys()))
'''),

Q(15, "Easy", "How do you read and write CSV files?",
"""Use the `csv` module with `newline=""` when opening. `csv.DictReader` yields dicts keyed by the header; `csv.DictWriter` writes dicts. It handles quoting and embedded commas correctly, unlike `line.split(",")`.""",
r'''
import csv, io
data = io.StringIO('name,city\n"Sharma, Riya",Pune\nArjun,"Bengaluru"\n')
rows = list(csv.DictReader(data))
print(rows)
out = io.StringIO()
w = csv.DictWriter(out, fieldnames=["name", "city"], lineterminator="\n")
w.writeheader(); w.writerows(rows)
print(out.getvalue())
'''),

Q(15, "Moderate", "What does the `logging` module provide, and how do you configure it?",
"""Named loggers (`getLogger(__name__)`) in a hierarchy, levels (DEBUG, INFO, WARNING, ERROR, CRITICAL), handlers (console, file, rotating file, syslog), formatters and filters. Libraries only create loggers; the application configures handlers once (`basicConfig` or `dictConfig`). Use lazy formatting: `log.info("user %s", uid)`.""",
r'''
import logging, sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format="%(asctime)s %(levelname)-7s %(name)s: %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("shop.payments")
log.debug("hidden: below INFO")
log.info("charged order %s for %.2f", 42, 999.5)
log.warning("retrying gateway call")
'''),

Q(15, "Moderate", "What does `functools` offer besides `lru_cache` and `partial`?",
"""`wraps`, `cache`, `cached_property`, `reduce`, `total_ordering`, `singledispatch` / `singledispatchmethod`, `cmp_to_key`, and `partialmethod`.""",
r'''
from functools import cached_property, cmp_to_key, singledispatch
class Report:
    @cached_property
    def data(self): print("  loading once"); return [3, 1, 2]
r = Report(); r.data; print(sorted(r.data))
print(sorted(["b", "A", "c"], key=cmp_to_key(lambda a, b: (a.lower() > b.lower()) - (a.lower() < b.lower()))))
@singledispatch
def size(x): return len(x)
@size.register
def _(x: int): return x.bit_length()
print(size("hello"), size(1024))
'''),

Q(15, "Moderate", "What does the `operator` module provide?",
"""Function versions of operators (`add`, `mul`, `eq`) and fast accessors: `itemgetter`, `attrgetter` and `methodcaller`, often cleaner and faster than lambdas in `sorted`, `map` and `max`.""",
r'''
from operator import itemgetter, attrgetter, methodcaller
from collections import namedtuple
rows = [("riya", 31, "Pune"), ("arjun", 25, "Delhi")]
print(sorted(rows, key=itemgetter(1)), list(map(itemgetter(0, 2), rows)))
P = namedtuple("P", "name age")
print(max([P("a", 3), P("b", 9)], key=attrgetter("age")))
print(list(map(methodcaller("upper"), ["x", "y"])))
'''),

Q(15, "Moderate", "How do you run external commands safely?",
"""`subprocess.run([...], capture_output=True, text=True, check=True, timeout=...)` with the command as a **list** of arguments. Avoid `shell=True` with user input (shell injection). `check=True` raises `CalledProcessError` on non-zero exit.""",
r'''
import subprocess, sys
r = subprocess.run([sys.executable, "-c", "import sys; print('args:', sys.argv[1:])", "a b", ";rm -rf /"],
                   capture_output=True, text=True, check=True, timeout=10)
print(r.returncode, r.stdout.strip())
try:
    subprocess.run([sys.executable, "-c", "raise SystemExit(3)"], check=True)
except subprocess.CalledProcessError as e:
    print("failed with exit code", e.returncode)
'''),

Q(15, "Moderate", "How do you generate secure random values?",
"""Use `secrets` for anything security-related (tokens, passwords, reset links): `token_urlsafe`, `token_hex`, `choice`, `compare_digest`. The `random` module is a predictable PRNG (Mersenne Twister) meant for simulations, never for security.""",
r'''
import secrets, string
print(len(secrets.token_urlsafe(32)), secrets.token_hex(8).isalnum())
alphabet = string.ascii_letters + string.digits
pwd = "".join(secrets.choice(alphabet) for _ in range(16))
print(len(pwd), secrets.compare_digest("abc", "abc"))
'''),

Q(15, "Moderate", "How do you hash data, and how should passwords be stored?",
"""`hashlib` provides SHA-256, BLAKE2 and more for checksums and fingerprints. Passwords must use a slow, salted KDF: `hashlib.scrypt`, `hashlib.pbkdf2_hmac`, or libraries like argon2-cffi/bcrypt. Never store plain SHA-256 of passwords. Use `hmac` to sign messages.""",
r'''
import hashlib, hmac, os
print(hashlib.sha256(b"invoice-42").hexdigest()[:16])
salt = os.urandom(16)
key = hashlib.scrypt(b"s3cret!", salt=salt, n=2**14, r=8, p=1)
print(len(key), hmac.compare_digest(key, hashlib.scrypt(b"s3cret!", salt=salt, n=2**14, r=8, p=1)))
sig = hmac.new(b"webhook-secret", b'{"paid":true}', "sha256").hexdigest()
print(sig[:16])
'''),

Q(15, "Moderate", "What is `dataclasses` vs `typing.NamedTuple` vs `attrs`/Pydantic?",
"""- `NamedTuple`: immutable, tuple-compatible, lightweight records.
- `dataclass`: flexible classes with generated methods; optional frozen/slots/order.
- `attrs`: the library dataclasses were inspired by, with validators and converters.
- Pydantic: runtime validation and parsing from untrusted input (APIs, config), JSON schema; used by FastAPI.""",
r'''
from dataclasses import dataclass, field
@dataclass(slots=True, kw_only=True)
class Order:
    id: int
    items: list[str] = field(default_factory=list)
    status: str = "PENDING"
    def __post_init__(self):
        if self.id <= 0: raise ValueError("id must be positive")
print(Order(id=7, items=["pen"]))
try:
    Order(id=0)
except ValueError as e:
    print("ValueError:", e)
'''),

Q(15, "Moderate", "How do you work with temporary files and directories?",
"""`tempfile.TemporaryDirectory()` and `NamedTemporaryFile()` create uniquely named, securely created files that are removed automatically when the context manager exits. Don't build temp paths by hand (race conditions, collisions).""",
r'''
import tempfile, pathlib
with tempfile.TemporaryDirectory() as d:
    p = pathlib.Path(d, "scratch.txt"); p.write_text("tmp")
    print(p.exists())
print(p.exists())
'''),

Q(15, "Moderate", "How do you parse command-line arguments?",
"""`argparse` (stdlib): positional and optional arguments, types, defaults, choices, sub-commands and automatic `--help`. Third-party alternatives: `click` and `typer` (type-hint driven).""",
r'''
import argparse
p = argparse.ArgumentParser(prog="export")
p.add_argument("table")
p.add_argument("--format", choices=["csv", "json"], default="csv")
p.add_argument("--limit", type=int, default=100)
p.add_argument("-v", "--verbose", action="store_true")
args = p.parse_args(["orders", "--format", "json", "--limit", "5", "-v"])
print(vars(args))
'''),

Q(15, "Moderate", "What are `collections.ChainMap` and `types.SimpleNamespace` used for?",
"""`ChainMap` searches several dicts in order without merging, perfect for layered config (CLI > env > file > defaults). `SimpleNamespace` is an attribute bag: `ns.x` access over a dict, handy for quick records and test doubles.""",
r'''
from collections import ChainMap
from types import SimpleNamespace
defaults, env, cli = {"port": 80, "debug": False}, {"port": 8080}, {"debug": True}
cfg = ChainMap(cli, env, defaults)
print(cfg["port"], cfg["debug"], dict(cfg))
user = SimpleNamespace(name="riya", role="admin"); user.active = True
print(user)
'''),

Q(15, "Moderate", "How do you measure execution time of a snippet?",
"""`timeit` for micro-benchmarks (runs many times, disables GC by default); `time.perf_counter()` for wall-clock timing of code blocks; `cProfile` for finding where time goes in a whole program.""",
r'''
import timeit
print(f"{timeit.timeit('sum(range(1000))', number=10_000) * 100:.2f} us per call")
best = min(timeit.repeat("'-'.join(map(str, range(100)))", number=10_000, repeat=3))
print(f"join: best of 3 = {best * 100:.2f} us per call")
'''),

Q(15, "Moderate", "What is `decimal.Decimal` and when must you use it?",
"""Exact base-10 arithmetic with configurable precision and rounding. Use it for money, tax and billing, where binary float rounding errors are unacceptable. Construct from strings, not floats.""",
r'''
from decimal import Decimal, ROUND_HALF_UP
print(Decimal(0.1), "|", Decimal("0.1"))
price, qty, gst = Decimal("19.99"), 3, Decimal("0.18")
total = (price * qty * (1 + gst)).quantize(Decimal("0.01"), ROUND_HALF_UP)
print(total, sum([0.1] * 10), sum([Decimal("0.1")] * 10))
'''),

Q(15, "Moderate", "What does `shutil` provide?",
"""High-level file operations: `copy2` (with metadata), `copytree`, `rmtree`, `move`, `make_archive`/`unpack_archive`, `disk_usage`, and `which` (find an executable on PATH).""",
r'''
import shutil, tempfile, pathlib
src = pathlib.Path(tempfile.mkdtemp(), "project"); (src / "pkg").mkdir(parents=True)
(src / "pkg" / "a.py").write_text("x = 1"); (src / "notes.tmp").write_text("scratch")
dst = src.parent / "backup"
shutil.copytree(src, dst, ignore=shutil.ignore_patterns("*.tmp"))
print(sorted(p.relative_to(dst).as_posix() for p in dst.rglob("*")))
shutil.rmtree(dst); print("removed:", not dst.exists())
'''),

Q(15, "Difficult", "How do you use `sqlite3` from Python safely?",
"""Always use **parameterized queries** (`?` placeholders), never f-strings, to prevent SQL injection. Use the connection as a context manager for transactions, set `row_factory = sqlite3.Row` for dict-like rows.""",
r'''
import sqlite3
con = sqlite3.connect(":memory:")
con.row_factory = sqlite3.Row
con.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
with con:
    con.executemany("INSERT INTO users (name) VALUES (?)", [("riya",), ("arjun",)])
evil = "x' OR '1'='1"
print(con.execute("SELECT count(*) FROM users WHERE name = ?", (evil,)).fetchone()[0], "rows (injection blocked)")
row = con.execute("SELECT * FROM users WHERE name = ?", ("riya",)).fetchone()
print(dict(row))
'''),

Q(15, "Moderate", "What does the `statistics` module offer?",
"""Basic statistics without NumPy: `mean`, `fmean`, `median`, `mode`, `stdev`, `pstdev`, `quantiles`, `correlation` and `linear_regression` (3.10+).""",
r'''
import statistics as st
latencies = [120, 95, 101, 3000, 110, 99, 105]
print(st.mean(latencies), st.median(latencies), round(st.stdev(latencies)))
print(st.quantiles(latencies, n=4))
'''),

Q(15, "Difficult", "How do you make HTTP requests with only the stdlib?",
"""`urllib.request` can do it (`urlopen`, `Request` with headers and data), and `http.client` is lower level. In practice most projects use `requests` or `httpx` (sync and async) for sessions, retries and JSON convenience.""",
r'''
import urllib.request, json
req = urllib.request.Request("https://api.example.com/orders", data=json.dumps({"id": 1}).encode(),
                             headers={"Content-Type": "application/json"}, method="POST")
print(req.get_method(), req.full_url, req.headers)
'''),

# =============== 16. TYPE HINTS & MODERN PYTHON ===============
Q(16, "Easy", "What are type hints and are they enforced?",
"""Annotations describing expected types (`def f(x: int) -> str`). CPython does **not** enforce them at runtime; static checkers (mypy, pyright), IDEs and some libraries (Pydantic, FastAPI, dataclasses) use them. They document intent and catch bugs before running.""",
r'''
def total(prices: list[float], tax: float = 0.18) -> float:
    return round(sum(prices) * (1 + tax), 2)
print(total([10.0, 20.0]))
print(total.__annotations__)
'''),

Q(16, "Moderate", "What is the modern syntax for common type hints?",
"""Since 3.9 use built-in generics: `list[int]`, `dict[str, float]`, `tuple[int, ...]`. Since 3.10 use `X | Y` instead of `Union`, and `X | None` instead of `Optional[X]`. `collections.abc.Iterable`, `Callable`, `Mapping` for flexible parameters.""",
r'''
from collections.abc import Callable, Iterable
def apply(fn: Callable[[int], int], values: Iterable[int]) -> list[int]:
    return [fn(v) for v in values]
def find(users: dict[str, int], name: str) -> int | None:
    return users.get(name)
print(apply(lambda v: v * 2, (1, 2, 3)), find({"riya": 1}, "arjun"))
'''),

Q(16, "Moderate", "What are generics and `TypeVar`? What's the 3.12 syntax?",
"""Generics let functions and classes be typed over a type parameter. Before 3.12: `T = TypeVar("T")`. Since 3.12 (PEP 695): `def first[T](xs: list[T]) -> T` and `class Stack[T]:`, plus `type Alias = ...` statements.""",
r'''
def first[T](items: list[T]) -> T:
    return items[0]
class Stack[T]:
    def __init__(self) -> None: self._items: list[T] = []
    def push(self, item: T) -> None: self._items.append(item)
    def pop(self) -> T: return self._items.pop()
type Pair[K] = tuple[K, K]
s = Stack[int](); s.push(5)
print(first(["a", "b"]), s.pop(), Pair.__value__)
'''),

Q(16, "Moderate", "What is `typing.Protocol`?",
"""Structural typing ("static duck typing"): a class matches a Protocol if it has the required methods/attributes, without inheriting from it. Great for describing what a function needs (`SupportsRead`, `HasId`).""",
r'''
from typing import Protocol
class HasArea(Protocol):
    def area(self) -> float: ...
class Square:
    def __init__(self, s: float): self.s = s
    def area(self) -> float: return self.s ** 2
def total_area(shapes: list[HasArea]) -> float:
    return sum(s.area() for s in shapes)
print(total_area([Square(2), Square(3)]))
'''),

Q(16, "Moderate", "What are `TypedDict` and `Literal`?",
"""`TypedDict` types dicts with known string keys (like JSON payloads) for type checkers. `Literal["GET", "POST"]` restricts a value to specific constants. Both are purely static; at runtime a TypedDict is a plain dict.""",
r'''
from typing import TypedDict, Literal, NotRequired
class OrderPayload(TypedDict):
    id: int
    status: Literal["PENDING", "PAID", "SHIPPED"]
    note: NotRequired[str]
p: OrderPayload = {"id": 1, "status": "PAID"}
print(p, type(p).__name__, OrderPayload.__required_keys__)
'''),

Q(16, "Difficult", "How do you type a decorator correctly (`Callable`, `ParamSpec`)?",
"""A naive decorator typed as `Callable[..., Any]` loses the wrapped function's signature. `ParamSpec` (`P`) captures the parameters, so the decorated function keeps its exact signature for type checkers.""",
r'''
import functools
from collections.abc import Callable
def logged[**P, R](fn: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print("calling", fn.__name__)
        return fn(*args, **kwargs)
    return wrapper
@logged
def scale(x: float, *, factor: float = 2.0) -> float: return x * factor
print(scale(3.0, factor=10))
'''),

Q(16, "Moderate", "What does `from __future__ import annotations` do, and what changed in 3.14?",
"""It makes all annotations lazily stored as strings (PEP 563), allowing forward references and avoiding import-time cost. Python 3.14 implements **deferred evaluation** natively (PEP 649/749): annotations are evaluated only when accessed (e.g. via `annotationlib.get_annotations`), so forward references work without the future import.""",
r'''
class Node:
    def link(self, other: Node) -> Node:      # forward reference works in 3.14 without quotes
        return other
import annotationlib
print(annotationlib.get_annotations(Node.link))
'''),

Q(16, "Moderate", "What are `Final`, `ClassVar` and `@override`?",
"""`Final` marks a name that shouldn't be reassigned; `ClassVar` marks a class-level attribute (dataclasses skip it as a field); `typing.override` (3.12+) marks a method that must override a parent method, so checkers flag typos and removed base methods.""",
r'''
from dataclasses import dataclass, fields
from typing import ClassVar, Final, override
MAX: Final = 10
@dataclass
class Item:
    registry: ClassVar[dict] = {}
    name: str
class Base:
    def save(self) -> None: ...
class Child(Base):
    @override
    def save(self) -> None: print("saved")
print([f.name for f in fields(Item)]); Child().save()
'''),

Q(16, "Difficult", "How do you check types at runtime if hints aren't enforced?",
"""Options: explicit `isinstance` checks; Pydantic models or `TypeAdapter` for validating external data; `typeguard`/`beartype` decorators for runtime checking in tests. Keep runtime validation at system boundaries (API input, config files).""",
r'''
from typing import get_type_hints
def validate_call(fn):
    hints = get_type_hints(fn)
    def wrapper(**kwargs):
        for k, v in kwargs.items():
            if k in hints and not isinstance(v, hints[k]):
                raise TypeError(f"{k} must be {hints[k].__name__}, got {type(v).__name__}")
        return fn(**kwargs)
    return wrapper
@validate_call
def create(name: str, age: int): return f"{name} ({age})"
print(create(name="riya", age=31))
try:
    create(name="arjun", age="25")
except TypeError as e:
    print("TypeError:", e)
'''),

Q(16, "Easy", "What major features arrived in Python 3.8 to 3.11?",
"""- 3.8: walrus `:=`, positional-only params `/`, f-string `=` debugging
- 3.9: dict `|` merge, `list[int]` generics, `str.removeprefix`, `zoneinfo`
- 3.10: `match` statement, `X | Y` unions, better error messages, `zip(strict=True)`
- 3.11: 10-60% faster CPython, exception groups and `except*`, `TaskGroup`, `tomllib`, `Self` type, fine-grained error locations"""),

Q(16, "Moderate", "What major features arrived in Python 3.12, 3.13 and 3.14?",
"""- 3.12: PEP 695 generic syntax and `type` aliases, more flexible f-strings (PEP 701), `itertools.batched`, per-interpreter GIL, immortal objects
- 3.13: new interactive REPL, experimental free-threaded build and JIT, `copy.replace`, improved error messages
- 3.14: free-threading officially supported (PEP 779), deferred annotations (PEP 649), template strings `t"..."` (PEP 750), `concurrent.interpreters` (PEP 734), `compression.zstd`, incremental GC, warnings for `return` in `finally`""",
r'''
import sys
print(sys.version.split()[0])
items = ["a", "b"]
print(f"{"-".join(items)}")          # 3.12+: reuse the same quotes inside f-strings
'''),

Q(16, "Difficult", "What are template strings (t-strings) in Python 3.14?",
"""A `t"..."` literal (PEP 750) creates a `string.templatelib.Template` object instead of a `str`, exposing the static parts and the interpolated values separately. Libraries can then process values safely, e.g. escaping HTML or parameterizing SQL, before producing the final string.""",
r'''
from string.templatelib import Template, Interpolation
import html
def render_html(t: Template) -> str:
    return "".join(html.escape(str(p.value)) if isinstance(p, Interpolation) else p for p in t)
user = "<script>alert('x')</script>"
tmpl = t"<p>Hello {user}!</p>"
print(type(tmpl).__name__)
print(render_html(tmpl))
'''),

Q(16, "Moderate", "What is `Self` type and when do you use it?",
"""`typing.Self` (3.11+) annotates methods returning an instance of the current class, including subclasses, e.g. fluent builders or alternate constructors, without writing a `TypeVar` bound to the class.""",
r'''
from typing import Self
class Query:
    def __init__(self): self.parts: list[str] = []
    def where(self, cond: str) -> Self:
        self.parts.append(cond); return self
class UserQuery(Query): pass
q = UserQuery().where("age > 18").where("active")
print(type(q).__name__, q.parts)
'''),

Q(16, "Moderate", "What is `tomllib` and how do you read TOML config?",
"""`tomllib` (3.11+) parses TOML (used by `pyproject.toml`) into dicts. It's read-only; use third-party `tomli-w` to write. Open files in binary mode.""",
r'''
import tomllib
cfg = tomllib.loads("""
[server]
host = "0.0.0.0"
port = 8080
[features]
beta = ["search", "wishlist"]
""")
print(cfg["server"]["port"], cfg["features"]["beta"])
'''),

Q(16, "Difficult", "What is the difference between `mypy` and `pyright`, and how do you adopt typing in an existing codebase?",
"""Both are static type checkers: mypy (the reference implementation, plugin ecosystem) and pyright (fast, powers VS Code's Pylance). Adopt gradually: start with `--check-untyped-defs` or strictness per module, type public APIs and new code first, add stubs (`types-requests`), and enforce in CI with a ratchet so coverage only grows."""),

Q(16, "Moderate", "What does `@dataclass(slots=True, frozen=True)` give you, and what does `kw_only` do?",
"""`slots=True` (3.10+) generates `__slots__` (less memory, no accidental attributes). `frozen=True` makes instances immutable and hashable. `kw_only=True` requires keyword arguments in `__init__`, avoiding argument-order mistakes and allowing defaults before non-defaults.""",
r'''
from dataclasses import dataclass
@dataclass(slots=True, frozen=True, kw_only=True)
class Money:
    currency: str = "INR"
    amount: int
m = Money(amount=500)
print(m, hash(m) == hash(Money(amount=500)), hasattr(m, "__dict__"))
'''),

Q(16, "Moderate", "What are `NewType` and `Annotated`?",
"""`NewType("UserId", int)` creates a distinct type for checkers (so a `UserId` can't be passed where an `OrderId` is expected) with zero runtime cost. `Annotated[T, meta]` attaches metadata used by frameworks, e.g. FastAPI's `Annotated[int, Query(gt=0)]` or Pydantic constraints.""",
r'''
from typing import NewType, Annotated, get_type_hints
UserId = NewType("UserId", int)
def load(uid: UserId) -> str: return f"user {uid}"
print(load(UserId(7)), UserId(7) == 7, type(UserId(7)).__name__)
def price(x: Annotated[float, "must be >= 0"]): ...
print(get_type_hints(price, include_extras=True)["x"].__metadata__)
'''),

]
