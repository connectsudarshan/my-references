QUESTIONS = [

# =============== 7. INHERITANCE, MRO & POLYMORPHISM ===============
Q(7, "Easy", "How does inheritance work in Python?",
"""`class Child(Parent)` inherits attributes and methods; the child can add or override them. Every class ultimately inherits from `object`. Use `super()` to call the parent's version of a method.""",
r'''
class Employee:
    def __init__(self, name, salary): self.name, self.salary = name, salary
    def pay(self): return self.salary
class Manager(Employee):
    def __init__(self, name, salary, bonus):
        super().__init__(name, salary); self.bonus = bonus
    def pay(self): return super().pay() + self.bonus
print(Manager("riya", 100, 25).pay(), Manager.__bases__, issubclass(Manager, object))
'''),

Q(7, "Moderate", "What does `super()` actually do?",
"""`super()` returns a proxy that delegates to the **next class in the MRO** of the instance's type, not necessarily the direct parent. That is what makes cooperative multiple inheritance work. Zero-argument `super()` works inside methods thanks to the `__class__` cell.""",
r'''
class A:
    def hi(self): return "A"
class B(A):
    def hi(self): return "B>" + super().hi()
class C(A):
    def hi(self): return "C>" + super().hi()
class D(B, C):
    def hi(self): return "D>" + super().hi()
print(D().hi())          # B's super() goes to C, not A
'''),

Q(7, "Moderate", "What is the MRO (Method Resolution Order)?",
"""The order Python searches classes for an attribute, computed with the **C3 linearization**: a class comes before its parents, parents keep the order they're listed in, and each class appears once. View it with `Cls.__mro__` or `Cls.mro()`.""",
r'''
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass
print([k.__name__ for k in D.__mro__])
'''),

Q(7, "Difficult", "What is the diamond problem and how does Python solve it?",
"""With `D(B, C)` where both B and C inherit from A, naive lookup could visit A twice or before C. Python's C3 MRO visits A once, after both B and C, and cooperative `super()` calls let each class's method run exactly once.""",
r'''
class Base:
    def __init__(self): print("Base init")
class Left(Base):
    def __init__(self): print("Left init"); super().__init__()
class Right(Base):
    def __init__(self): print("Right init"); super().__init__()
class Child(Left, Right):
    def __init__(self): print("Child init"); super().__init__()
Child()
'''),

Q(7, "Difficult", "When does Python refuse to create a class because of the MRO?",
"""If the base orders are contradictory, C3 can't produce a consistent linearization and Python raises `TypeError` at class creation.""",
r'''
class X: pass
class Y: pass
class A(X, Y): pass
class B(Y, X): pass
try:
    class C(A, B): pass
except TypeError as e:
    print("TypeError:", e)
'''),

Q(7, "Easy", "What is method overriding?",
"""A subclass defines a method with the same name as the parent's; calls on subclass instances use the subclass version. Call the parent explicitly with `super().method()` when extending rather than replacing.""",
r'''
class Notifier:
    def send(self, msg): return f"log: {msg}"
class SmsNotifier(Notifier):
    def send(self, msg): return f"sms: {msg[:20]}"
for n in (Notifier(), SmsNotifier()):
    print(n.send("Your order has been shipped today"))
'''),

Q(7, "Moderate", "Does Python support method overloading?",
"""Not by signature: a second `def` with the same name replaces the first. Use default arguments, `*args`, or `functools.singledispatch` / `singledispatchmethod` to dispatch on the type of the first argument. `typing.overload` only informs type checkers.""",
r'''
from functools import singledispatchmethod
class Printer:
    @singledispatchmethod
    def show(self, arg): return f"object: {arg!r}"
    @show.register
    def _(self, arg: int): return f"int with {arg.bit_length()} bits"
    @show.register
    def _(self, arg: list): return f"list of {len(arg)}"
p = Printer()
print(p.show(255), "|", p.show([1, 2]), "|", p.show("x"))
'''),

Q(7, "Moderate", "What is polymorphism in Python?",
"""The same operation works on different types, each with its own behaviour: `len()` on str/list/dict, `+` on numbers/strings/lists, or a `draw()` method on different shape classes. Python's duck typing means objects needn't share a base class.""",
r'''
class Circle:
    def area(self): return 3.14159 * 2 ** 2
class Square:
    def area(self): return 3 ** 2
print([round(s.area(), 1) for s in (Circle(), Square())])
print(len("abc"), len([1, 2]), len({"a": 1}), 1 + 2, "a" + "b", [1] + [2])
'''),

Q(7, "Moderate", "What is a mixin?",
"""A small class providing one reusable capability, combined via multiple inheritance: `class View(LoginRequiredMixin, TemplateView)`. Mixins are listed before the main base, avoid their own `__init__` state, and use cooperative `super()`.""",
r'''
import json
class JsonMixin:
    def to_json(self): return json.dumps(self.__dict__)
class ReprMixin:
    def __repr__(self): return f"{type(self).__name__}({self.__dict__})"
class User(JsonMixin, ReprMixin):
    def __init__(self, name): self.name = name
u = User("riya"); print(u.to_json(), u)
'''),

Q(7, "Moderate", "How do `isinstance` and `issubclass` work with ABCs and `register`?",
"""They check the class hierarchy, and also consult `__subclasshook__` and virtual subclasses registered with `ABC.register()`. That's why `isinstance([], collections.abc.Sequence)` is True even though `list` doesn't inherit from it.""",
r'''
from collections.abc import Sequence, Iterable, Sized
print(isinstance([], Sequence), isinstance({}, Sequence), issubclass(list, Iterable))
class Box:
    def __len__(self): return 3
print(isinstance(Box(), Sized))              # structural check via __subclasshook__
class Legacy: pass
Sequence.register(Legacy)
print(issubclass(Legacy, Sequence))
'''),

Q(7, "Difficult", "How should `__init__` be written in cooperative multiple inheritance?",
"""Every class calls `super().__init__(**kwargs)`, consuming only the keyword arguments it needs and passing the rest along, so each `__init__` in the MRO runs once in order and `object.__init__` receives no leftovers.""",
r'''
class Timestamped:
    def __init__(self, *, created="2026-09-28", **kw):
        super().__init__(**kw); self.created = created
class Owned:
    def __init__(self, *, owner, **kw):
        super().__init__(**kw); self.owner = owner
class Document(Timestamped, Owned):
    def __init__(self, *, title, **kw):
        super().__init__(**kw); self.title = title
d = Document(title="Q3", owner="riya")
print(vars(d))
'''),

Q(7, "Moderate", "What is the difference between inheriting from `list` and from `collections.UserList` (or `abc.MutableSequence`)?",
"""Built-in methods of `list`/`dict` are implemented in C and often **don't call your overrides** (e.g. `dict.update` ignores your `__setitem__`). `UserDict`/`UserList` or the `collections.abc` bases route everything through your methods.""",
r'''
from collections import UserDict
class UpperDict(dict):
    def __setitem__(self, k, v): super().__setitem__(k.upper(), v)
class UpperUserDict(UserDict):
    def __setitem__(self, k, v): super().__setitem__(k.upper(), v)
a = UpperDict(); a.update(x=1); a["y"] = 2
b = UpperUserDict(); b.update(x=1); b["y"] = 2
print(dict(a), dict(b))
'''),

Q(7, "Moderate", "Can you call a parent method that the child has overridden?",
"""Yes: `super().method()` from inside the child, or explicitly `Parent.method(self)` (bypasses the MRO; avoid with multiple inheritance). From outside, `super(Child, obj).method()`.""",
r'''
class Parent:
    def greet(self): return "parent"
class Child(Parent):
    def greet(self): return "child"
c = Child()
print(c.greet(), super(Child, c).greet(), Parent.greet(c))
'''),

Q(7, "Difficult", "What is `typing.Protocol` and how is it different from ABC inheritance?",
"""A `Protocol` defines an interface **structurally**: any class with matching methods satisfies it for type checkers, without inheriting. With `@runtime_checkable`, `isinstance` checks that the methods exist (not their signatures). ABCs are nominal: classes must inherit or register.""",
r'''
from typing import Protocol, runtime_checkable
@runtime_checkable
class SupportsClose(Protocol):
    def close(self) -> None: ...
class Socketish:
    def close(self): print("closed")
def shutdown(r: SupportsClose): r.close()
shutdown(Socketish())
print(isinstance(Socketish(), SupportsClose), isinstance(42, SupportsClose))
'''),

Q(7, "Moderate", "What is `object` and what does every class inherit from it?",
"""`object` is the root of all classes. It provides default `__init__`, `__new__`, `__repr__`, `__str__`, `__eq__` (identity), `__hash__` (id-based), `__getattribute__`, `__setattr__`, `__dir__`, `__init_subclass__`, `__class__` and more.""",
r'''
class Empty: pass
e = Empty()
print(repr(e)[:22], e == e, e == Empty(), hash(e) == hash(e))
print(len(dir(object)), "attributes on object")
'''),

Q(7, "Difficult", "Why is deep inheritance often discouraged, and what's the alternative?",
"""Deep hierarchies couple subclasses to base-class internals (fragile base class problem), make behaviour hard to trace across files, and multiply MRO surprises. Alternatives: composition, small mixins, protocols, and passing strategies/functions in."""),

Q(7, "Moderate", "How do you prevent a class from being subclassed or a method from being overridden?",
"""There's no runtime enforcement by default. `typing.final` / `@final` marks classes or methods for type checkers. At runtime you can raise in `__init_subclass__`.""",
r'''
from typing import final
class Sealed:
    def __init_subclass__(cls, **kw):
        raise TypeError(f"{cls.__name__}: Sealed cannot be subclassed")
try:
    class Hack(Sealed): pass
except TypeError as e:
    print(e)
@final
class Config: ...        # mypy/pyright will flag subclasses
'''),

Q(7, "Difficult", "What does `super()` do in a classmethod or `__new__`?",
"""Zero-arg `super()` works in any method defined in the class body, including classmethods and `__new__`, delegating along the MRO of `cls`. It's needed for correct alternate constructors and immutable subclasses.""",
r'''
class Upper(str):
    def __new__(cls, value):
        return super().__new__(cls, value.upper())
class Base:
    @classmethod
    def create(cls): return f"created {cls.__name__}"
class Sub(Base):
    @classmethod
    def create(cls): return super().create() + " via Sub"
print(Upper("hello"), isinstance(Upper("x"), str), Sub.create())
'''),

# =============== 8. DUNDER METHODS & THE DATA MODEL ===============
Q(8, "Easy", "What are dunder (magic) methods?",
"""Methods with double underscores (`__init__`, `__len__`, `__add__`, ...) that Python calls implicitly to implement built-in behaviour: operators, `len()`, iteration, `with`, attribute access, printing. Implementing them makes your objects feel built-in.""",
r'''
class Vector:
    def __init__(self, x, y): self.x, self.y = x, y
    def __add__(self, o): return Vector(self.x + o.x, self.y + o.y)
    def __mul__(self, k): return Vector(self.x * k, self.y * k)
    def __abs__(self): return (self.x ** 2 + self.y ** 2) ** 0.5
    def __eq__(self, o): return (self.x, self.y) == (o.x, o.y)
    def __repr__(self): return f"Vector({self.x}, {self.y})"
v = Vector(3, 4)
print(v + Vector(1, 1), v * 2, abs(v), v == Vector(3, 4))
'''),

Q(8, "Moderate", "What are reflected operators like `__radd__`?",
"""For `a + b`, Python calls `a.__add__(b)`; if that returns `NotImplemented`, it tries `b.__radd__(a)`. Implementing `__radd__` lets `sum()` work (it starts with `0 + first`) and lets `3 * v` work via `__rmul__`.""",
r'''
class Money:
    def __init__(self, c): self.c = c
    def __add__(self, o):
        if isinstance(o, Money): return Money(self.c + o.c)
        if o == 0: return self
        return NotImplemented
    __radd__ = __add__
    def __repr__(self): return f"Money({self.c})"
print(sum([Money(5), Money(7), Money(1)]))
'''),

Q(8, "Moderate", "Why return `NotImplemented` instead of raising `NotImplementedError`?",
"""`NotImplemented` is a special value telling Python "I don't support this operand; try the other side's reflected method". If both return it, Python raises `TypeError`. `NotImplementedError` is an exception for abstract methods that subclasses must override."""),

Q(8, "Moderate", "How do you make objects comparable and sortable?",
"""Implement `__eq__` and `__lt__` (sorting only needs `__lt__`), and add `@functools.total_ordering` to derive `<=`, `>`, `>=`. Or use `@dataclass(order=True)`.""",
r'''
from functools import total_ordering
@total_ordering
class Version:
    def __init__(self, s): self.parts = tuple(map(int, s.split(".")))
    def __eq__(self, o): return self.parts == o.parts
    def __lt__(self, o): return self.parts < o.parts
    def __repr__(self): return ".".join(map(str, self.parts))
vs = [Version("1.10.0"), Version("1.2.3"), Version("1.9")]
print(sorted(vs), Version("2.0") >= Version("1.99"))
'''),

Q(8, "Moderate", "What does `__call__` do?",
"""It makes instances callable like functions. Useful for stateful functions, configurable callbacks and class-based decorators.""",
r'''
class RateLimiter:
    def __init__(self, limit): self.limit, self.calls = limit, 0
    def __call__(self, user):
        self.calls += 1
        return "ok" if self.calls <= self.limit else "429"
check = RateLimiter(2)
print([check("riya") for _ in range(3)], callable(check))
'''),

Q(8, "Moderate", "How do `__getitem__`, `__setitem__`, `__len__` and `__contains__` work?",
"""They implement indexing `obj[k]`, assignment `obj[k] = v`, `len(obj)` and `x in obj`. `__getitem__` receives a `slice` object for `obj[a:b]`. A class with only `__getitem__` (accepting 0, 1, 2...) is even iterable via the old sequence protocol.""",
r'''
class Timeline:
    def __init__(self, events): self._e = list(events)
    def __getitem__(self, i):
        if isinstance(i, slice): return Timeline(self._e[i])
        return self._e[i]
    def __len__(self): return len(self._e)
    def __repr__(self): return f"Timeline({self._e})"
t = Timeline(["boot", "login", "pay", "logout"])
print(t[1], t[1:3], len(t), "pay" in t, list(t))
'''),

Q(8, "Moderate", "What is `__bool__` and how does truthiness fall back?",
"""`bool(obj)` calls `__bool__`; if absent, it uses `__len__` (0 is False); if neither exists, the object is truthy.""",
r'''
class Basket:
    def __init__(self, items): self.items = items
    def __len__(self): return len(self.items)
class Result:
    def __init__(self, ok): self.ok = ok
    def __bool__(self): return self.ok
print(bool(Basket([])), bool(Basket([1])), bool(Result(False)), bool(object()))
'''),

Q(8, "Moderate", "What do `__enter__` and `__exit__` do?",
"""They implement the context manager protocol for `with`. `__enter__`'s return value is bound by `as`; `__exit__(exc_type, exc, tb)` always runs and can suppress exceptions by returning True.""",
r'''
class Suppress:
    def __init__(self, *exc): self.exc = exc
    def __enter__(self): return self
    def __exit__(self, et, e, tb):
        if et and issubclass(et, self.exc):
            print("suppressed", et.__name__); return True
with Suppress(ZeroDivisionError):
    1 / 0
print("continues")
'''),

Q(8, "Moderate", "What is `__hash__` and what is the rule connecting it to `__eq__`?",
"""`hash(obj)` calls `__hash__`. Rule: objects that compare equal **must** have equal hashes. If you define `__eq__` without `__hash__`, Python sets `__hash__ = None` (unhashable), protecting you from breaking dicts and sets. Hash only immutable fields."""),

Q(8, "Difficult", "What is `__getattribute__` vs `__getattr__` vs `__setattr__` vs `__delattr__`?",
"""`__getattribute__` runs on **every** attribute access (default implements normal lookup). `__getattr__` runs only when normal lookup fails. `__setattr__` runs on every assignment, `__delattr__` on every `del obj.x`. Inside them, call `object.__...__` / `super()` to avoid infinite recursion.""",
r'''
class Audited:
    def __init__(self): self.x = 1
    def __setattr__(self, name, value):
        print(f"set {name}={value!r}")
        super().__setattr__(name, value)
    def __getattr__(self, name):
        return f"<missing {name}>"
a = Audited(); a.y = 2
print(a.x, a.nope)
'''),

Q(8, "Moderate", "What is `__len__` vs `__length_hint__`?",
"""`__len__` must return the exact size (used by `len()`). `__length_hint__` returns an estimate used by `operator.length_hint` to pre-allocate, for iterators whose length isn't known exactly.""",
r'''
import operator
it = iter(range(10)); next(it)
print(operator.length_hint(it), operator.length_hint(iter([1, 2, 3])))
'''),

Q(8, "Difficult", "What is `__format__` and how do custom format specs work?",
"""`format(obj, spec)` and f-strings `{obj:spec}` call `obj.__format__(spec)`, so a class can define its own mini-language. `datetime` uses this for `f"{d:%Y-%m-%d}"`.""",
r'''
from datetime import date
class Money:
    def __init__(self, amt): self.amt = amt
    def __format__(self, spec):
        if spec == "inr": return f"₹{self.amt:,.2f}"
        return format(self.amt, spec)
m = Money(1234567.5)
print(f"{m:inr} | {m:.1f} | {date(2026, 9, 28):%d %b %Y}")
'''),

Q(8, "Difficult", "What are `__iter__` / `__next__` / `__reversed__` / `__contains__` used for?",
"""`__iter__` returns an iterator (used by `for`); iterators implement `__next__` and raise `StopIteration`. `reversed()` uses `__reversed__` (or `__len__` + `__getitem__`). `in` uses `__contains__`, falling back to iterating.""",
r'''
class Countdown:
    def __init__(self, n): self.n = n
    def __iter__(self): return iter(range(self.n, 0, -1))
    def __reversed__(self): return iter(range(1, self.n + 1))
    def __contains__(self, x): return 1 <= x <= self.n
c = Countdown(3)
print(list(c), list(reversed(c)), 2 in c, 9 in c)
'''),

Q(8, "Difficult", "What is `__class_getitem__`?",
"""It lets a class support subscription like `MyList[int]` for generic type hints, returning a `types.GenericAlias`. Built-ins support it since 3.9 (`list[int]`), which is why you no longer need `typing.List`.""",
r'''
class Registry:
    def __class_getitem__(cls, item): return f"Registry of {item.__name__}"
print(Registry[int], list[int], dict[str, list[int]])
'''),

Q(8, "Moderate", "What is `__del__` and why should you avoid relying on it?",
"""A finalizer called when an object is about to be destroyed. Timing is not guaranteed (reference cycles, interpreter shutdown, other implementations like PyPy), and exceptions inside it are ignored. Use context managers or `weakref.finalize` for cleanup.""",
r'''
import weakref
class Resource:
    def __init__(self, name):
        self.name = name
        weakref.finalize(self, print, f"finalize: released {name}")
r = Resource("tmpfile")
del r
print("after del")
'''),

Q(8, "Difficult", "What are `__copy__` and `__deepcopy__`?",
"""Hooks used by `copy.copy` and `copy.deepcopy` to customize cloning, for example to avoid copying a cache or a live connection. `__deepcopy__(self, memo)` must pass `memo` to nested deepcopies to handle cycles.""",
r'''
import copy
class Model:
    def __init__(self): self.weights, self.cache = [1, 2], {"big": "..."}
    def __deepcopy__(self, memo):
        new = Model.__new__(Model)
        new.weights = copy.deepcopy(self.weights, memo)
        new.cache = {}                         # don't clone the cache
        return new
m2 = copy.deepcopy(Model())
print(m2.weights, m2.cache)
'''),

Q(8, "Difficult", "What are `__set_name__` and descriptors' role in the data model?",
"""`__set_name__(self, owner, name)` is called on class attributes when the class is created, telling a descriptor which attribute name it was assigned to. It removes the need to repeat the name, e.g. `email = Validated()` instead of `Validated("email")`.""",
r'''
class NonEmpty:
    def __set_name__(self, owner, name): self.name = "_" + name
    def __get__(self, obj, objtype=None): return getattr(obj, self.name)
    def __set__(self, obj, value):
        if not value: raise ValueError(f"{self.name[1:]} must not be empty")
        setattr(obj, self.name, value)
class User:
    email = NonEmpty()
    def __init__(self, email): self.email = email
print(User("a@x.com").email)
try:
    User("")
except ValueError as e:
    print("ValueError:", e)
'''),

Q(8, "Moderate", "Why does `len(obj)` work but `obj.__len__` lookups on the instance are ignored?",
"""Implicit special-method lookup goes to the **type**, not the instance. Setting `obj.__len__ = ...` on an instance has no effect on `len(obj)`. This keeps built-in operations fast and consistent.""",
r'''
class C:
    def __len__(self): return 1
c = C()
c.__len__ = lambda: 99
print(len(c), c.__len__())
'''),

Q(8, "Difficult", "How do you implement a container that supports `+=` in place?",
"""Implement `__iadd__` returning `self` after mutating. If `__iadd__` is missing, Python falls back to `__add__` and rebinds the name to a new object.""",
r'''
class Bag:
    def __init__(self): self.items = []
    def __iadd__(self, other):
        self.items.extend(other); return self
b = Bag(); ref = b
b += ["pen", "book"]
print(b.items, b is ref)
'''),

Q(8, "Moderate", "What is `__missing__`?",
"""A dict subclass hook called by `dict.__getitem__` when a key isn't found. `defaultdict` is built on it. Note it's not used by `get()`.""",
r'''
class Defaulting(dict):
    def __missing__(self, key): return f"<no {key}>"
d = Defaulting(a=1)
print(d["a"], d["zzz"], d.get("zzz"))
'''),

]
