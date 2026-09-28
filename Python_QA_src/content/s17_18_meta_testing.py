QUESTIONS = [

# =============== 17. METAPROGRAMMING ===============
Q(17, "Moderate", "What is a descriptor?",
"""An object defining `__get__`, and optionally `__set__`/`__delete__`, stored as a **class** attribute. Attribute access on instances is routed through it. `property`, `classmethod`, `staticmethod`, bound methods and ORM fields (Django, SQLAlchemy) are all descriptors.""",
r'''
class Positive:
    def __set_name__(self, owner, name): self.attr = "_" + name
    def __get__(self, obj, objtype=None):
        if obj is None: return self            # accessed on the class
        return getattr(obj, self.attr)
    def __set__(self, obj, value):
        if value <= 0: raise ValueError(f"{self.attr[1:]} must be > 0")
        setattr(obj, self.attr, value)
class Product:
    price = Positive(); qty = Positive()
    def __init__(self, price, qty): self.price, self.qty = price, qty
p = Product(99.0, 2); print(p.price * p.qty)
try:
    p.qty = 0
except ValueError as e:
    print("ValueError:", e)
'''),

Q(17, "Difficult", "Data vs non-data descriptors: what's the lookup precedence?",
"""A **data descriptor** defines `__set__` or `__delete__`; a **non-data descriptor** only `__get__`. Lookup order for `obj.x`: data descriptors on the type win over the instance `__dict__`, which wins over non-data descriptors and plain class attributes. That's why `cached_property` (non-data) can store its result in the instance dict and be found there next time.""",
r'''
class Data:
    def __get__(self, o, t=None): return "data descriptor"
    def __set__(self, o, v): pass
class NonData:
    def __get__(self, o, t=None): return "non-data descriptor"
class C:
    d = Data(); n = NonData()
c = C()
c.__dict__["d"] = "instance value"; c.__dict__["n"] = "instance value"
print(c.d, "|", c.n)
'''),

Q(17, "Moderate", "How is `property` implemented using descriptors?",
"""`property` is a data descriptor class storing `fget`, `fset`, `fdel`. Its `__get__` calls `fget(obj)`, `__set__` calls `fset(obj, value)` or raises `AttributeError` if read-only. `@x.setter` returns a new property copy with `fset` added.""",
r'''
class MyProperty:
    def __init__(self, fget, fset=None): self.fget, self.fset = fget, fset
    def __get__(self, obj, objtype=None): return self if obj is None else self.fget(obj)
    def __set__(self, obj, value):
        if self.fset is None: raise AttributeError("read-only")
        self.fset(obj, value)
    def setter(self, fset): return MyProperty(self.fget, fset)
class Circle:
    def __init__(self, r): self._r = r
    @MyProperty
    def area(self): return round(3.14159 * self._r ** 2, 2)
c = Circle(2); print(c.area)
try:
    c.area = 5
except AttributeError as e:
    print("AttributeError:", e)
'''),

Q(17, "Moderate", "What is a metaclass?",
"""The class of a class. Classes are created by calling their metaclass (default `type`) with name, bases and namespace. Custom metaclasses (subclassing `type`) can modify or validate classes at creation time. "Metaclasses are deeper magic than 99% of users should ever worry about" (Tim Peters): prefer decorators or `__init_subclass__` first.""",
r'''
class Meta(type):
    def __new__(mcls, name, bases, ns):
        ns.setdefault("table", name.lower() + "s")
        return super().__new__(mcls, name, bases, ns)
class Model(metaclass=Meta): pass
class Order(Model): pass
print(type(Order).__name__, Order.table, type(type).__name__)
'''),

Q(17, "Difficult", "How can you create a class dynamically with `type()`?",
"""`type(name, bases, namespace)` builds a class at runtime, the same thing the `class` statement does. Useful for generating classes from schemas or configuration.""",
r'''
def greet(self): return f"hello from {type(self).__name__}"
Dog = type("Dog", (object,), {"sound": "woof", "greet": greet})
d = Dog()
print(d.greet(), d.sound, Dog.__mro__)
fields = {"id": int, "name": str}
Row = type("Row", (), {"__annotations__": fields, "__slots__": tuple(fields)})
print(Row.__slots__)
'''),

Q(17, "Difficult", "What real-world problems do metaclasses solve?",
"""Frameworks that need to transform class bodies: Django models (collecting `Field` attributes into `_meta`), SQLAlchemy declarative models, enum's `EnumType`, ABCMeta (abstract method tracking), and registries/validation of every subclass. Many of these could now use `__init_subclass__` and `__set_name__`."""),

Q(17, "Difficult", "What is the order of operations when a class statement runs?",
"""1) Resolve the metaclass. 2) Call `metaclass.__prepare__` to get the namespace mapping. 3) Execute the class body in that namespace. 4) Call `metaclass(name, bases, namespace)`, which runs `__new__` and `__init__`; during `type.__new__`, `__set_name__` is called on descriptors and the parent's `__init_subclass__` runs. 5) Apply class decorators.""",
r'''
class Meta(type):
    @classmethod
    def __prepare__(mcls, name, bases): print("1 __prepare__"); return {}
    def __new__(mcls, name, bases, ns): print("3 metaclass __new__"); return super().__new__(mcls, name, bases, ns)
class Desc:
    def __set_name__(self, owner, name): print("4 __set_name__", name)
class Base(metaclass=Meta):
    def __init_subclass__(cls): print("5 __init_subclass__", cls.__name__)
def deco(cls): print("6 class decorator"); return cls
print("-- defining Child --")
@deco
class Child(Base):
    print("2 class body runs")
    field = Desc()
'''),

Q(17, "Moderate", "What does `__slots__` do and what are its limitations?",
"""It declares a fixed set of instance attributes stored in slots instead of a per-instance `__dict__`, saving memory and speeding attribute access. Limitations: no new attributes, no `__weakref__` unless listed, `cached_property` needs a `__dict__`, and every class in the hierarchy must define slots to fully avoid `__dict__`.""",
r'''
class Point:
    __slots__ = ("x", "y")
    def __init__(self, x, y): self.x, self.y = x, y
class Point3D(Point):          # forgot __slots__: gets a __dict__ again
    pass
p, q = Point(1, 2), Point3D(1, 2)
print(hasattr(p, "__dict__"), hasattr(q, "__dict__"), Point.x)
'''),

Q(17, "Moderate", "What is monkey patching?",
"""Changing classes, modules or functions at runtime, e.g. replacing `time.sleep` in a test or patching a library bug. It's powerful but hidden and fragile; in tests, use `unittest.mock.patch` or pytest's `monkeypatch`, which undo the change automatically.""",
r'''
import math
original = math.sqrt
math.sqrt = lambda x: "patched!"
print(math.sqrt(16))
math.sqrt = original
print(math.sqrt(16))
'''),

Q(17, "Moderate", "What does `inspect` let you do?",
"""Introspect live objects: signatures, source code, members, class hierarchy, call stack frames, whether something is a coroutine function or generator. Frameworks use it for dependency injection, CLI generation and documentation.""",
r'''
import inspect
def create(name: str, *, admin: bool = False) -> dict: return {}
print(inspect.signature(create), inspect.isfunction(create))
print([n for n, _ in inspect.getmembers(dict, inspect.ismethoddescriptor)][:5])
print(inspect.currentframe().f_code.co_name)
'''),

Q(17, "Difficult", "How do `eval`, `exec` and `compile` differ, and what are the risks?",
"""`eval` evaluates a single expression and returns its value; `exec` executes statements; `compile` turns source into a code object for either. Running untrusted input through them allows arbitrary code execution: restricting globals does not make them safe. Use `ast.literal_eval` for literals or a real parser.""",
r'''
import ast
print(eval("2 * 21"))
ns = {}; exec("def f(x):\n    return x + 1", ns); print(ns["f"](9))
code = compile("a + b", "<expr>", "eval"); print(eval(code, {"a": 1, "b": 2}))
print(ast.literal_eval("[1, {'k': (2, 3)}]"))
try:
    ast.literal_eval("__import__('os').getcwd()")
except ValueError as e:
    print("literal_eval refused:", type(e).__name__)
'''),

Q(17, "Difficult", "What is the `ast` module used for?",
"""It parses Python source into an abstract syntax tree you can inspect, transform (`NodeTransformer`) and compile back. Linters (pylint, Bandit), formatters, codemods, coverage tools and pytest's assertion rewriting are built on it.""",
r'''
import ast
tree = ast.parse("total = price * qty + tax")
print(ast.dump(tree.body[0].value, indent=None)[:80] + "...")
names = sorted({n.id for n in ast.walk(tree) if isinstance(n, ast.Name)})
print(names, ast.unparse(tree))
'''),

Q(17, "Moderate", "How can you add methods or attributes to a class after it's defined?",
"""Assign to the class: `Cls.method = function`; all instances (existing and new) see it because lookups go through the class. Assigning to one instance only affects that instance, and a function assigned to an instance is not bound automatically (use `types.MethodType`).""",
r'''
import types
class User:
    def __init__(self, name): self.name = name
u = User("riya")
User.shout = lambda self: self.name.upper()
print(u.shout())
u.whisper = types.MethodType(lambda self: self.name.lower() + "...", u)
print(u.whisper())
'''),

Q(17, "Difficult", "How do Django/SQLAlchemy model fields know their own names?",
"""Each field is a descriptor-like object in the class body. When the class is created, `__set_name__` (or a metaclass that scans the namespace) tells each field its attribute name and owner, so it can map to a column and build the model's metadata without you repeating names."""),

# =============== 18. TESTING, DEBUGGING & LOGGING ===============
Q(18, "Easy", "What testing frameworks are common in Python?",
"""`unittest` (stdlib, xUnit style classes) and **pytest** (the de facto standard: plain `assert`, fixtures, parametrization, plugins). Also `doctest` for examples in docstrings, `hypothesis` for property-based testing, `tox`/`nox` for multi-environment runs, `coverage.py` for coverage."""),

Q(18, "Easy", "Write a basic unittest test case.",
"""Subclass `unittest.TestCase`, write `test_*` methods, use assertion methods, and use `setUp`/`tearDown` for fixtures.""",
r'''
import unittest
def apply_discount(price, pct):
    if not 0 <= pct <= 100: raise ValueError("pct out of range")
    return round(price * (1 - pct / 100), 2)
class DiscountTests(unittest.TestCase):
    def test_basic(self): self.assertEqual(apply_discount(200, 10), 180)
    def test_zero(self): self.assertEqual(apply_discount(99.99, 0), 99.99)
    def test_invalid(self):
        with self.assertRaises(ValueError): apply_discount(10, 150)
suite = unittest.defaultTestLoader.loadTestsFromTestCase(DiscountTests)
result = unittest.TextTestRunner(verbosity=0, stream=open("nul" if __import__("os").name == "nt" else "/dev/null", "w")).run(suite)
print("ran", result.testsRun, "failures", len(result.failures), "errors", len(result.errors))
'''),

Q(18, "Moderate", "Why is pytest preferred, and what does a pytest test look like?",
"""Tests are plain functions with plain `assert` (pytest rewrites asserts to show detailed diffs), fixtures are injected by argument name, `@pytest.mark.parametrize` runs one test over many inputs, and a huge plugin ecosystem exists (pytest-django, pytest-asyncio, pytest-cov, pytest-xdist).""",
r'''
# test_pricing.py -- run with:  pytest -q
import pytest

def apply_discount(price, pct): return round(price * (1 - pct / 100), 2)

@pytest.fixture
def cart():
    return {"items": [("pen", 50.0), ("book", 450.0)]}

def test_total(cart):
    assert sum(p for _, p in cart["items"]) == 500

@pytest.mark.parametrize("price,pct,expected", [(200, 10, 180), (100, 0, 100), (80, 25, 60)])
def test_discount(price, pct, expected):
    assert apply_discount(price, pct) == expected
''', run=False),

Q(18, "Moderate", "What are pytest fixtures and scopes?",
"""Functions decorated with `@pytest.fixture` that provide setup (and teardown after `yield`) to tests that name them as parameters. Scopes: `function` (default), `class`, `module`, `package`, `session`, so expensive resources (DB, server) can be shared. `conftest.py` shares fixtures across files.""",
r'''
# conftest.py
import pytest, sqlite3

@pytest.fixture(scope="session")
def db():
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE users (name TEXT)")
    yield con                      # tests run here
    con.close()                    # teardown after the whole session

@pytest.fixture
def user(db):                      # fixtures can use fixtures
    db.execute("INSERT INTO users VALUES ('riya')")
    yield "riya"
    db.execute("DELETE FROM users")
''', run=False),

Q(18, "Moderate", "How do you mock a dependency in tests?",
"""`unittest.mock.patch` replaces an object where it's **looked up** for the duration of a test, and `Mock`/`MagicMock` record calls so you can assert on them (`assert_called_once_with`). Better still, design for dependency injection and pass fakes directly.""",
r'''
from unittest import mock
import json, urllib.request
def get_rate(cur):
    with urllib.request.urlopen(f"https://api.example.com/rates/{cur}") as r:
        return json.load(r)["rate"]
fake_resp = mock.MagicMock()
fake_resp.__enter__.return_value = fake_resp
fake_resp.read.return_value = b'{"rate": 83.1}'
with mock.patch("urllib.request.urlopen", return_value=fake_resp) as m:
    print(get_rate("USD"))
    m.assert_called_once_with("https://api.example.com/rates/USD")
print("no real network call was made")
'''),

Q(18, "Difficult", "Why does `mock.patch` sometimes not work? (Patch where it's used)",
"""`patch("module.name")` replaces the attribute in **that module's namespace**. If your code did `from requests import get`, it holds its own reference in `myapp.client.get`; patching `requests.get` won't affect it. Patch the name in the module under test: `patch("myapp.client.get")`.""",
r'''
import sys, types
from unittest import mock
lib = types.ModuleType("lib"); exec("def now(): return 'real time'", lib.__dict__); sys.modules["lib"] = lib
app = types.ModuleType("app"); exec("from lib import now\ndef stamp(): return now()", app.__dict__); sys.modules["app"] = app
with mock.patch("lib.now", return_value="fake"):
    print("patched lib.now ->", app.stamp())
with mock.patch("app.now", return_value="fake"):
    print("patched app.now ->", app.stamp())
'''),

Q(18, "Moderate", "What is `MagicMock` vs `Mock`, and what does `spec`/`autospec` add?",
"""`MagicMock` also supports magic methods (`len`, iteration, context managers). `spec=`/`autospec=True` restrict the mock to the real object's attributes and signatures, so typos and wrong arguments fail instead of silently passing.""",
r'''
from unittest import mock
class Gateway:
    def charge(self, amount: float, currency: str) -> str: ...
loose = mock.Mock()
loose.chrage(10)                                  # typo passes silently!
strict = mock.create_autospec(Gateway, instance=True)
try:
    strict.chrage(10)
except AttributeError as e:
    print("AttributeError:", e)
try:
    strict.charge(10)
except TypeError as e:
    print("TypeError:", e)
'''),

Q(18, "Moderate", "How do you test code that raises exceptions or logs messages?",
"""`pytest.raises(Exc, match="regex")` or `self.assertRaises` for exceptions; pytest's `caplog` fixture or `self.assertLogs` for log records; `capsys` to capture printed output.""",
r'''
import logging, unittest
log = logging.getLogger("billing")
def refund(amount):
    if amount > 1000:
        log.warning("large refund %s", amount)
    return amount
class T(unittest.TestCase):
    def test_logs(self):
        with self.assertLogs("billing", level="WARNING") as cm:
            refund(5000)
        self.assertIn("large refund 5000", cm.output[0])
        print("captured:", cm.output)
unittest.main(argv=["x"], exit=False, verbosity=0)
'''),

Q(18, "Moderate", "What is property-based testing?",
"""Instead of hand-picked examples, you state properties that must hold for all inputs, and a library (Hypothesis) generates many inputs, including edge cases, and shrinks failures to a minimal example. Great for parsers, serializers and math.""",
r'''
# pip install hypothesis ; run with pytest
from hypothesis import given, strategies as st

def encode(s: str) -> bytes: return s.encode("utf-8")
def decode(b: bytes) -> str: return b.decode("utf-8")

@given(st.text())
def test_roundtrip(s):
    assert decode(encode(s)) == s          # property: decode(encode(x)) == x

@given(st.lists(st.integers()))
def test_sort_is_idempotent(xs):
    assert sorted(sorted(xs)) == sorted(xs)
''', run=False),

Q(18, "Easy", "How do you debug Python code?",
"""- `breakpoint()` (3.7+) drops into `pdb` at that line: `n` next, `s` step, `c` continue, `p expr`, `l` list, `w` where, `u`/`d` up/down the stack
- `python -m pdb script.py`, or post-mortem after a crash with `pdb.pm()`
- IDE debuggers (VS Code, PyCharm)
- structured logging and `traceback`; `faulthandler` for hard crashes"""),

Q(18, "Moderate", "How do you read a Python traceback?",
"""Read from the **bottom**: the last line is the exception type and message; the lines above show the call stack from outermost (top) to where it failed (bottom), with file, line and code. Since 3.11, `^^^^` markers point to the exact failing expression. For chained exceptions, read each block.""",
r'''
import traceback
def load(cfg): return cfg["db"]["port"]
try:
    load({"db": None})
except TypeError:
    print(traceback.format_exc().strip())
'''),

Q(18, "Moderate", "What is code coverage and what does it not tell you?",
"""Coverage (`coverage.py`, `pytest --cov`) measures which lines/branches ran during tests. It finds untested code but doesn't prove tests check the right things: 100% coverage with weak asserts can still miss bugs. Aim for meaningful coverage of critical logic, and consider branch coverage and mutation testing."""),

Q(18, "Moderate", "How do you test async code?",
"""Use `pytest-asyncio` (`@pytest.mark.asyncio` / auto mode) or `unittest.IsolatedAsyncioTestCase`, and `AsyncMock` for awaited dependencies.""",
r'''
import asyncio, unittest
from unittest.mock import AsyncMock
async def get_user(client, uid):
    data = await client.fetch(f"/users/{uid}")
    return data["name"].title()
class T(unittest.IsolatedAsyncioTestCase):
    async def test_get_user(self):
        client = AsyncMock(); client.fetch.return_value = {"name": "riya sharma"}
        self.assertEqual(await get_user(client, 7), "Riya Sharma")
        client.fetch.assert_awaited_once_with("/users/7")
        print("async test passed")
unittest.main(argv=["x"], exit=False, verbosity=0)
'''),

Q(18, "Moderate", "What's the difference between unit, integration and end-to-end tests?",
"""**Unit** tests check one function/class in isolation (fast, many). **Integration** tests check components together with real dependencies (DB, message queue), often via containers. **End-to-end** tests exercise the whole system like a user (slow, few). The test pyramid suggests many unit tests, fewer integration, very few E2E."""),

Q(18, "Moderate", "How do you freeze time or control randomness in tests?",
"""Inject a clock/RNG (best), or patch: `freezegun`/`time-machine` for dates, `random.seed()` or a dedicated `random.Random(seed)` instance for reproducible randomness.""",
r'''
import random
from datetime import datetime, timezone
class Service:
    def __init__(self, clock=lambda: datetime.now(timezone.utc), rng=random.Random()):
        self.clock, self.rng = clock, rng
    def token(self): return f"{self.clock():%Y%m%d}-{self.rng.randint(1000, 9999)}"
s = Service(clock=lambda: datetime(2026, 9, 28, tzinfo=timezone.utc), rng=random.Random(42))
print(s.token(), s.token())
'''),

Q(18, "Moderate", "What is logging best practice in applications vs libraries?",
"""Libraries: `log = logging.getLogger(__name__)`, never configure handlers (at most add `NullHandler`). Applications: configure once at startup (`dictConfig`), use structured/JSON logs in production, include request IDs, log exceptions with `log.exception`, and use lazy `%s` formatting. Don't use `print` in services."""),

Q(18, "Difficult", "How do you find where a slow or hanging Python process is stuck?",
"""`py-spy dump --pid <pid>` shows every thread's stack without stopping it; `py-spy top`/`record` profiles live. `faulthandler.dump_traceback_later(timeout)` dumps stacks if a run hangs; `python -X faulthandler` shows stacks on crashes; `sys._current_frames()` in-process.""",
r'''
import sys, threading, time, traceback
def worker(): time.sleep(0.2)
t = threading.Thread(target=worker, name="slow-worker"); t.start()
time.sleep(0.05)
for tid, frame in sys._current_frames().items():
    name = next((th.name for th in threading.enumerate() if th.ident == tid), "?")
    if name == "slow-worker":
        print(name, "is at:", traceback.extract_stack(frame)[-1].line)
t.join()
'''),

Q(18, "Moderate", "What are doctests?",
"""Examples in docstrings written as interactive sessions (`>>> expr` then expected output). `python -m doctest module.py` or `doctest.testmod()` runs them, keeping documentation examples correct.""",
r'''
import doctest
def slugify(text):
    """Turn a title into a URL slug.
    >>> slugify("Hello World")
    'hello-world'
    >>> slugify("  Python  Tips ")
    'python-tips'
    """
    return "-".join(text.lower().split())
print(doctest.testmod(verbose=False))
'''),

Q(18, "Moderate", "How do you structure tests in a project?",
"""A `tests/` directory mirroring the package layout, `test_*.py` files, shared fixtures in `conftest.py`, test configuration in `pyproject.toml` (`[tool.pytest.ini_options]`), markers for slow/integration tests, and CI running `pytest -q --cov` on every pull request, often parallelized with `pytest-xdist`."""),

]
