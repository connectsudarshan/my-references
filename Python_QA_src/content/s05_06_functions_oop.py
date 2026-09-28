QUESTIONS = [

# =============== 5. FUNCTIONS, ARGUMENTS & SCOPE ===============
Q(5, "Easy", "What are `*args` and `**kwargs`?",
"""`*args` collects extra positional arguments into a tuple; `**kwargs` collects extra keyword arguments into a dict. The names are conventions; the `*` and `**` matter. At a call site, `*` and `**` unpack a sequence or mapping into arguments.""",
r'''
def report(title, *args, **kwargs):
    print(title, args, kwargs)
report("sales", 10, 20, region="IN", year=2026)
nums, opts = [1, 2], {"region": "US"}
report("unpacked", *nums, **opts)
'''),

Q(5, "Moderate", "What is the mutable default argument trap?",
"""Default values are evaluated **once**, when the `def` runs, and shared across calls. A mutable default (list, dict) accumulates state between calls. Use `None` as the default and create the object inside.""",
r'''
def add_bad(item, bucket=[]):
    bucket.append(item); return bucket
print(add_bad(1), add_bad(2))          # same list both times!
def add_good(item, bucket=None):
    if bucket is None: bucket = []
    bucket.append(item); return bucket
print(add_good(1), add_good(2))
print(add_bad.__defaults__)
'''),

Q(5, "Moderate", "What are positional-only and keyword-only parameters?",
"""Parameters before `/` are positional-only (3.8+); parameters after `*` (or `*args`) are keyword-only. This lets APIs rename positional params freely and forces clarity for flags like `sort(key=..., reverse=True)`.""",
r'''
def transfer(src, dst, /, amount, *, currency="INR", dry_run=False):
    return f"{src}->{dst} {amount} {currency} dry={dry_run}"
print(transfer("A", "B", 100, dry_run=True))
try:
    transfer(src="A", dst="B", amount=1)
except TypeError as e:
    print("TypeError:", e)
try:
    transfer("A", "B", 1, "USD")
except TypeError as e:
    print("TypeError:", e)
'''),

Q(5, "Easy", "What is the LEGB rule?",
"""Name lookup order: **L**ocal (current function), **E**nclosing (outer functions), **G**lobal (module), **B**uilt-in. The first match wins.""",
r'''
x = "global"
def outer():
    x = "enclosing"
    def inner():
        x = "local"
        print(x, len)          # local x, built-in len
    inner(); print(x)
outer(); print(x)
'''),

Q(5, "Moderate", "What do `global` and `nonlocal` do?",
"""Assigning to a name inside a function makes it local by default. `global x` rebinds the module-level `x`; `nonlocal x` rebinds `x` in the nearest enclosing function. Reading doesn't need either; only rebinding does.""",
r'''
count = 0
def bump():
    global count
    count += 1
def make_counter():
    n = 0
    def inc():
        nonlocal n
        n += 1; return n
    return inc
bump(); bump()
c = make_counter(); c(); print(count, c())
'''),

Q(5, "Moderate", "Why does this raise `UnboundLocalError`?",
"""Because the function assigns to `total` somewhere, Python treats `total` as **local for the whole function** (decided at compile time). Reading it before the local assignment fails even though a global exists.""",
r'''
total = 10
def add(n):
    total = total + n        # 'total' is local here -> read before assignment
    return total
try:
    add(5)
except UnboundLocalError as e:
    print("UnboundLocalError:", e)
''', ),

Q(5, "Moderate", "What is a closure?",
"""A nested function that remembers variables from its enclosing scope even after the outer function has returned. The captured variables live in "cells" (`fn.__closure__`). Closures power decorators, factories and callbacks.""",
r'''
def make_multiplier(k):
    def mul(x):
        return x * k
    return mul
triple = make_multiplier(3)
print(triple(7), triple.__closure__[0].cell_contents)
'''),

Q(5, "Difficult", "Why do closures created in a loop all return the same value?",
"""Closures capture **variables**, not values (late binding). All lambdas below refer to the same `i`, which is 2 when they run. Fix with a default argument (`i=i`) or `functools.partial`.""",
r'''
fns = [lambda: i for i in range(3)]
print([f() for f in fns])
fixed = [lambda i=i: i for i in range(3)]
print([f() for f in fixed])
'''),

Q(5, "Easy", "What is a lambda function?",
"""An anonymous function limited to a single expression: `lambda args: expr`. Common as short `key=` functions or callbacks. For anything longer, or anything you'd name, use `def` (better tracebacks and docs).""",
r'''
pairs = [(1, "b"), (3, "a"), (2, "c")]
print(sorted(pairs, key=lambda p: p[1]))
square = lambda x: x * x
print(square(9), square.__name__)
'''),

Q(5, "Moderate", "What does it mean that functions are first-class objects?",
"""Functions can be assigned to variables, stored in data structures, passed as arguments, returned from functions, and have attributes. This enables higher-order functions, callbacks, decorators and dispatch tables.""",
r'''
import operator
OPS = {"+": operator.add, "-": operator.sub, "*": operator.mul}
def calc(a, op, b): return OPS[op](a, b)
print(calc(6, "*", 7), calc(10, "-", 3))
def shout(s): return s.upper()
shout.version = 2
print(shout.__name__, shout.version, list(map(shout, ["a", "b"])))
'''),

Q(5, "Moderate", "What are `map`, `filter` and `functools.reduce`?",
"""`map(f, it)` applies `f` lazily to each item; `filter(pred, it)` keeps items where pred is truthy; `reduce(f, it, init)` folds items into one value. Comprehensions are usually more readable than `map`/`filter` with lambdas.""",
r'''
from functools import reduce
nums = [1, 2, 3, 4, 5]
print(list(map(lambda x: x * x, nums)), list(filter(lambda x: x % 2, nums)))
print(reduce(lambda acc, x: acc * x, nums, 1))
print([x * x for x in nums if x % 2])      # usually preferred
'''),

Q(5, "Moderate", "What is `functools.partial`?",
"""It creates a new callable with some arguments pre-filled. Useful for callbacks and adapting functions to an expected signature.""",
r'''
from functools import partial
def power(base, exp): return base ** exp
square, cube = partial(power, exp=2), partial(power, exp=3)
print(square(5), cube(2))
parse_hex = partial(int, base=16)
print(parse_hex("ff"))
'''),

Q(5, "Easy", "What does a function return if it has no `return` statement?",
"""`None`. A bare `return` also returns `None`. To return several values, return a tuple (the parentheses are optional) and unpack it.""",
r'''
def stats(nums):
    return min(nums), max(nums), sum(nums) / len(nums)
lo, hi, avg = stats([3, 9, 6])
def nothing(): pass
print(lo, hi, avg, nothing())
'''),

Q(5, "Moderate", "What is recursion, and what is Python's recursion limit?",
"""A function calling itself, with a base case to stop. CPython limits depth (default 1000, `sys.getrecursionlimit()`) and raises `RecursionError` beyond it. Python has **no tail-call optimization**, so deep recursion should be rewritten iteratively.""",
r'''
import sys
def fact(n): return 1 if n <= 1 else n * fact(n - 1)
print(fact(10), sys.getrecursionlimit())
try:
    fact(100_000)
except RecursionError as e:
    print("RecursionError:", e)
'''),

Q(5, "Moderate", "How do you memoize a recursive function?",
"""Decorate it with `functools.cache` (unbounded, 3.9+) or `lru_cache(maxsize=N)`. Arguments must be hashable. It turns exponential recursive Fibonacci into linear time.""",
r'''
from functools import cache
import time
@cache
def fib(n): return n if n < 2 else fib(n - 1) + fib(n - 2)
t = time.perf_counter()
print(fib(300), f"{(time.perf_counter() - t) * 1000:.2f} ms")
print(fib.cache_info())
'''),

Q(5, "Moderate", "How are arguments passed in Python: by value or by reference?",
"""Neither exactly: "pass by object reference" (call by sharing). The parameter is a new name bound to the same object. Mutations to mutable objects are visible to the caller; rebinding the parameter isn't."""),

Q(5, "Moderate", "What are function annotations?",
"""Optional hints on parameters and return values (`def f(x: int) -> str`), stored in `__annotations__`. Python doesn't enforce them at runtime; type checkers (mypy, pyright) and tools like FastAPI and Pydantic use them.""",
r'''
def greet(name: str, times: int = 1) -> str:
    return " ".join([f"hi {name}"] * times)
print(greet.__annotations__)
print(greet(42))            # no runtime check
'''),

Q(5, "Moderate", "How do you inspect a function's signature?",
"""`inspect.signature(fn)` returns parameters with kinds, defaults and annotations. Frameworks (pytest fixtures, FastAPI, click) use it to wire arguments automatically.""",
r'''
import inspect
def create_user(name: str, /, age: int = 18, *, admin: bool = False, **extra): ...
sig = inspect.signature(create_user)
for p in sig.parameters.values():
    print(f"{p.name:6} {p.kind.name:22} default={'-' if p.default is p.empty else repr(p.default)}")
'''),

Q(5, "Difficult", "What is the difference between a function and a method, and what is a bound method?",
"""A function defined in a class becomes a **method** when accessed through an instance: Python creates a bound method object that carries `__self__` and passes the instance as the first argument. Accessed on the class, it's the plain function.""",
r'''
class Greeter:
    def hello(self, name): return f"hello {name} from {self.__class__.__name__}"
g = Greeter()
m = g.hello
print(type(m).__name__, m.__self__ is g, m.__func__ is Greeter.hello)
print(m("riya"), Greeter.hello(g, "arjun"))
'''),

Q(5, "Moderate", "What is a higher-order function? Give examples from the stdlib.",
"""A function that takes and/or returns functions. Examples: `sorted(key=)`, `map`, `filter`, `functools.reduce`, `functools.partial`, `functools.wraps`, `itertools.starmap`, and every decorator.""",
r'''
def compose(*fns):
    def run(x):
        for f in reversed(fns): x = f(x)
        return x
    return run
slugify = compose(lambda s: s.replace(" ", "-"), str.lower, str.strip)
print(slugify("  Python Interview Prep "))
'''),

Q(5, "Difficult", "How do default argument values and `__defaults__` / `__kwdefaults__` work?",
"""Defaults are stored on the function object: positional defaults in `__defaults__` (tuple), keyword-only defaults in `__kwdefaults__` (dict). They are evaluated once at definition time, which explains the mutable-default trap.""",
r'''
import time
def stamp(ts=time.time(), *, tz="UTC"): return ts, tz
print(stamp.__defaults__ == (stamp()[0],), stamp.__kwdefaults__)
time.sleep(0.01)
print(stamp()[0] == stamp()[0])     # same frozen timestamp every call
'''),

Q(5, "Moderate", "How would you write a function that accepts any number of arguments and returns their average?",
"""Use `*args`, guard against zero arguments, and use `statistics.fmean` or `sum/len`.""",
r'''
def average(*nums: float) -> float:
    if not nums:
        raise ValueError("need at least one number")
    return sum(nums) / len(nums)
print(average(4, 8, 15, 16, 23, 42))
'''),

# =============== 6. OBJECT-ORIENTED PROGRAMMING ===============
Q(6, "Easy", "What are classes and objects in Python?",
"""A class is a blueprint defining attributes and methods; an object (instance) is created by calling the class. In Python everything is an object, including classes themselves (instances of `type`).""",
r'''
class Account:
    bank = "PyBank"                         # class attribute (shared)
    def __init__(self, owner, balance=0):
        self.owner, self.balance = owner, balance   # instance attributes
    def deposit(self, amt):
        self.balance += amt; return self.balance
a = Account("riya")
print(a.deposit(500), a.bank, type(a).__name__, type(Account))
'''),

Q(6, "Easy", "What is `self`?",
"""`self` is the conventional name for the first parameter of an instance method: the instance the method was called on. `obj.method(x)` is effectively `Class.method(obj, x)`. It is explicit in Python rather than a hidden `this`."""),

Q(6, "Easy", "What is `__init__`? Is it the constructor?",
"""`__init__` is the **initializer**: it sets up an already-created instance and must return `None`. The actual constructor is `__new__`, which creates and returns the instance. You rarely override `__new__` (immutable subclasses, singletons, caching).""",
r'''
class Point:
    def __new__(cls, *args):
        print("__new__ creates the object")
        return super().__new__(cls)
    def __init__(self, x, y):
        print("__init__ initializes it")
        self.x, self.y = x, y
p = Point(1, 2)
'''),

Q(6, "Moderate", "Class attributes vs instance attributes?",
"""Class attributes live on the class and are shared by all instances; instance attributes live in each object's `__dict__`. Lookup checks the instance first, then the class. Assigning via the instance creates an instance attribute that shadows the class one. A **mutable** class attribute is shared, a common bug.""",
r'''
class Cart:
    items = []                  # BUG: shared by every cart
    tax = 0.18
a, b = Cart(), Cart()
a.items.append("pen")
b.tax = 0.05                    # shadows only for b
print(b.items, a.tax, b.tax, Cart.tax, a.__dict__, b.__dict__)
'''),

Q(6, "Moderate", "What are instance methods, class methods and static methods?",
"""- Instance method: receives `self`; works with instance state.
- `@classmethod`: receives `cls`; used for alternate constructors and class-level state; respects subclasses.
- `@staticmethod`: receives neither; a plain function namespaced in the class.""",
r'''
from datetime import date
class Person:
    def __init__(self, name, born): self.name, self.born = name, born
    def age(self, today=date(2026, 9, 28)): return today.year - self.born
    @classmethod
    def from_csv(cls, line):
        name, born = line.split(","); return cls(name, int(born))
    @staticmethod
    def is_adult(age): return age >= 18
p = Person.from_csv("riya,1995")
print(p.name, p.age(), Person.is_adult(p.age()))
'''),

Q(6, "Moderate", "What is encapsulation in Python? Are there private members?",
"""Python has no enforced access control. Convention: `_name` means internal (don't touch from outside). `__name` triggers **name mangling** to `_ClassName__name`, which avoids accidental clashes in subclasses but isn't real privacy. Use properties to control access.""",
r'''
class Account:
    def __init__(self): self._balance = 100; self.__pin = 1234
a = Account()
print(a._balance)
try:
    print(a.__pin)
except AttributeError as e:
    print("AttributeError:", e)
print(a._Account__pin, [k for k in vars(a)])
'''),

Q(6, "Moderate", "What is `@property` and why use it?",
"""It turns a method into a managed attribute with optional setter and deleter. You can start with a plain attribute and later add validation or computation without changing callers (`obj.x` stays `obj.x`).""",
r'''
class Temperature:
    def __init__(self, celsius): self.celsius = celsius
    @property
    def celsius(self): return self._c
    @celsius.setter
    def celsius(self, v):
        if v < -273.15: raise ValueError("below absolute zero")
        self._c = v
    @property
    def fahrenheit(self): return self._c * 9 / 5 + 32
t = Temperature(25); print(t.fahrenheit)
try:
    t.celsius = -300
except ValueError as e:
    print("ValueError:", e)
'''),

Q(6, "Easy", "What are the four pillars of OOP and how does Python support them?",
"""- **Encapsulation**: bundling data and methods; `_` convention and properties.
- **Abstraction**: exposing what, hiding how; abstract base classes (`abc`).
- **Inheritance**: `class Child(Parent)`, multiple inheritance with MRO.
- **Polymorphism**: duck typing, method overriding, operator overloading via dunder methods."""),

Q(6, "Moderate", "What are abstract base classes (ABCs)?",
"""Classes inheriting from `abc.ABC` with `@abstractmethod` methods can't be instantiated until subclasses implement all abstract methods. They define interfaces and catch missing implementations early.""",
r'''
from abc import ABC, abstractmethod
class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...
    def describe(self): return f"{type(self).__name__} with area {self.area():.1f}"
class Circle(Shape):
    def __init__(self, r): self.r = r
    def area(self): return 3.14159 * self.r ** 2
print(Circle(2).describe())
try:
    Shape()
except TypeError as e:
    print("TypeError:", e)
'''),

Q(6, "Moderate", "What is duck typing?",
""""If it walks like a duck and quacks like a duck, it's a duck." Python cares whether an object has the needed methods, not its declared type. Any object with `read()` works where a file is expected. `typing.Protocol` lets type checkers express this structurally.""",
r'''
import io
class FakeFile:
    def read(self): return "data from anywhere"
def load(f): return f.read().upper()
print(load(io.StringIO("from memory")), "|", load(FakeFile()))
'''),

Q(6, "Moderate", "What are dataclasses?",
"""`@dataclass` (3.7+) generates `__init__`, `__repr__` and `__eq__` from annotated fields, with options for `order=True`, `frozen=True` (immutable and hashable), `slots=True` (3.10+), `kw_only=True`, and `field(default_factory=list)` for mutable defaults.""",
r'''
from dataclasses import dataclass, field, asdict
@dataclass(order=True, frozen=True)
class Version:
    major: int
    minor: int = 0
    tags: tuple = field(default=(), compare=False)
v = [Version(1, 10), Version(1, 2), Version(0, 9)]
print(sorted(v)[0], Version(1) == Version(1, 0), asdict(v[0]))
try:
    v[0].major = 2
except Exception as e:
    print(type(e).__name__, e)
'''),

Q(6, "Moderate", "Composition vs inheritance: which should you prefer?",
"""Prefer **composition** ("has-a"): build objects from collaborators you can swap. Use inheritance ("is-a") for true specialization or framework extension points. Composition avoids fragile base classes and deep hierarchies.""",
r'''
class Engine:
    def start(self): return "vroom"
class ElectricMotor:
    def start(self): return "hum"
class Car:
    def __init__(self, engine): self.engine = engine     # has-a
    def drive(self): return f"car goes {self.engine.start()}"
print(Car(Engine()).drive(), "|", Car(ElectricMotor()).drive())
'''),

Q(6, "Moderate", "How do you compare objects for equality and make them usable in sets/dicts?",
"""Define `__eq__` for equality and `__hash__` consistent with it (equal objects must have equal hashes). Defining `__eq__` alone sets `__hash__` to `None`, making instances unhashable. A frozen dataclass does both for you.""",
r'''
class Sku:
    def __init__(self, code): self.code = code.upper()
    def __eq__(self, other): return isinstance(other, Sku) and self.code == other.code
    def __hash__(self): return hash(self.code)
print(Sku("ab1") == Sku("AB1"), len({Sku("ab1"), Sku("AB1")}))
class NoHash:
    def __eq__(self, o): return True
print(NoHash.__hash__)
'''),

Q(6, "Moderate", "What is `__dict__` on an object?",
"""A dict holding an instance's writable attributes (and, on a class, its namespace as a read-only `mappingproxy`). `vars(obj)` returns it. Classes using `__slots__` don't have one.""",
r'''
class User:
    role = "member"
    def __init__(self, name): self.name = name
u = User("riya"); u.active = True
print(vars(u), type(User.__dict__).__name__, "role" in User.__dict__)
'''),

Q(6, "Difficult", "How do `getattr`, `setattr`, `hasattr` and `delattr` work, and what is `__getattr__`?",
"""They access attributes by name at runtime. `hasattr` calls `getattr` and catches `AttributeError`. A class-level `__getattr__` is called only when normal lookup fails, useful for proxies and lazy attributes; `__getattribute__` intercepts every access (use with care).""",
r'''
class Config:
    def __init__(self, **kw): self._data = kw
    def __getattr__(self, name):
        try: return self._data[name]
        except KeyError: raise AttributeError(name) from None
c = Config(db="postgres", debug=False)
print(c.db, getattr(c, "debug"), hasattr(c, "port"), getattr(c, "port", 5432))
setattr(c, "extra", 1); print(c.extra)
'''),

Q(6, "Difficult", "What is the difference between `__str__` and `__repr__`, and which is used when?",
"""`print()`, `str()` and `format()` use `__str__`, falling back to `__repr__`. The REPL, `repr()`, containers and debuggers use `__repr__`. Always implement `__repr__`; add `__str__` only if a user-facing form differs.""",
r'''
class Money:
    def __init__(self, amt, cur): self.amt, self.cur = amt, cur
    def __repr__(self): return f"Money({self.amt!r}, {self.cur!r})"
    def __str__(self): return f"{self.cur} {self.amt:,.2f}"
m = Money(1234.5, "INR")
print(m, [m], f"{m}", f"{m!r}")
'''),

Q(6, "Moderate", "How do you make a class iterable?",
"""Implement `__iter__` returning an iterator (a generator method is easiest). Optionally `__len__`, `__contains__` and `__getitem__`.""",
r'''
class Playlist:
    def __init__(self, *songs): self.songs = list(songs)
    def __iter__(self): yield from self.songs
    def __len__(self): return len(self.songs)
    def __contains__(self, s): return s in self.songs
p = Playlist("Intro", "Theme", "Outro")
print(list(p), len(p), "Theme" in p, [s.upper() for s in p])
'''),

Q(6, "Difficult", "What is `__init_subclass__`?",
"""A hook on a base class called whenever a subclass is defined (PEP 487). It can validate subclasses or register them in a plugin registry, without a metaclass. It receives keyword arguments from the class statement.""",
r'''
class Handler:
    registry = {}
    def __init_subclass__(cls, *, event, **kw):
        super().__init_subclass__(**kw)
        Handler.registry[event] = cls
class OnSignup(Handler, event="signup"): pass
class OnPayment(Handler, event="payment"): pass
print(Handler.registry)
'''),

Q(6, "Difficult", "What are class-level `__slots__` and what do they change?",
"""`__slots__ = ("x", "y")` replaces the per-instance `__dict__` with fixed slots: less memory, faster attribute access, and assigning undeclared attributes raises `AttributeError`. Trade-offs: no dynamic attributes, and multiple inheritance with slots needs care.""",
r'''
import sys
class P:
    def __init__(self): self.x, self.y = 1, 2
class S:
    __slots__ = ("x", "y")
    def __init__(self): self.x, self.y = 1, 2
p, s = P(), S()
print(sys.getsizeof(p) + sys.getsizeof(p.__dict__), sys.getsizeof(s))
try:
    s.z = 3
except AttributeError as e:
    print("AttributeError:", e)
'''),

Q(6, "Moderate", "How do you implement a singleton or shared state in Python?",
"""Simplest: a module-level instance (modules are cached singletons). Otherwise override `__new__` or use a metaclass or a caching decorator. Many teams prefer dependency injection over singletons for testability. See the Design Patterns page for full examples.""",
r'''
class Settings:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.values = {"debug": False}
        return cls._instance
print(Settings() is Settings(), Settings().values)
'''),

Q(6, "Moderate", "What is the difference between `copy.copy` of an object and creating a new instance?",
"""`copy.copy(obj)` creates a new instance **without calling `__init__`**, copying the instance `__dict__` (shallow). Customize with `__copy__` / `__deepcopy__`. A new instance via the constructor runs `__init__` with its validation and side effects.""",
r'''
import copy
class Conn:
    def __init__(self, dsn): print("__init__ called"); self.dsn = dsn
c = Conn("db://x")
c2 = copy.copy(c)
print(c2.dsn, c2 is not c)
'''),

Q(6, "Moderate", "What is an enum and why use it?",
"""`enum.Enum` defines a set of named constant members. Members are singletons, compared by identity, iterable, and prevent magic strings. `IntEnum`/`StrEnum` (3.11+) also behave like ints/strings; `Flag` supports bitwise combinations; `auto()` assigns values.""",
r'''
from enum import Enum, StrEnum, Flag, auto
class Status(StrEnum):
    PENDING = auto(); PAID = auto()
class Perm(Flag):
    READ = auto(); WRITE = auto(); EXEC = auto()
print(Status.PAID, Status.PAID == "paid", list(Status))
rw = Perm.READ | Perm.WRITE
print(rw, Perm.WRITE in rw, Perm.EXEC in rw)
'''),

]
