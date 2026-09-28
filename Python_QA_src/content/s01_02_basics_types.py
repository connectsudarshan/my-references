QUESTIONS = [

# =============== 1. PYTHON BASICS & SYNTAX ===============
Q(1, "Easy", "What is Python and what are its key features?",
"""Python is a high-level, general-purpose, dynamically typed, interpreted language with automatic memory management. Key features: readable indentation-based syntax, multiple paradigms (procedural, OOP, functional), a large standard library ("batteries included"), a huge package ecosystem (PyPI), and portability across operating systems.""",
r'''
import sys, platform
print(sys.version_info[:3], platform.python_implementation())
print("executable:", sys.executable.endswith(("python", "python.exe", "python3")))
'''),

Q(1, "Easy", "Is Python compiled or interpreted?",
"""Both. CPython first **compiles** source code to bytecode (`.pyc` files cached in `__pycache__`), then its virtual machine **interprets** that bytecode. It is usually called interpreted because there is no separate ahead-of-time compile step to machine code. PyPy adds a JIT compiler, and CPython 3.13+ ships an experimental JIT.""",
r'''
import dis
def add(a, b):
    return a + b
dis.dis(add)          # the bytecode CPython actually executes
'''),

Q(1, "Easy", "What is PEP 8?",
"""PEP 8 is Python's official style guide: 4-space indentation, lines around 79 characters (many teams use 88-120), `snake_case` for functions and variables, `PascalCase` for classes, `UPPER_CASE` for constants, two blank lines between top-level definitions, and imports grouped (stdlib, third-party, local). Tools like **Ruff**, flake8 and Black enforce it automatically."""),

Q(1, "Easy", "How does indentation work in Python?",
"""Indentation defines code blocks instead of braces. Every statement in a block must be indented by the same amount (4 spaces by convention). Mixing tabs and spaces inconsistently raises `TabError`, and a wrong level raises `IndentationError`.""",
r'''
code = "if True:\n    x = 1\n      y = 2\n"
try:
    compile(code, "<demo>", "exec")
except IndentationError as e:
    print(type(e).__name__, "-", e.msg, "on line", e.lineno)
'''),

Q(1, "Easy", "What is the difference between `is` and `==`?",
"""`==` compares **values** (calls `__eq__`). `is` compares **identity**: whether both names refer to the very same object (same `id()`). Use `is` only for singletons such as `None`, `True`, `False`; use `==` for everything else.""",
r'''
a = [1, 2, 3]
b = [1, 2, 3]
c = a
print(a == b, a is b)   # equal values, different objects
print(a is c)           # same object
x = None
print(x is None)        # the right way to test for None
'''),

Q(1, "Easy", "What are Python's built-in data types?",
"""- Numeric: `int`, `float`, `complex` (and `bool`, a subclass of `int`)
- Sequences: `str`, `list`, `tuple`, `range`, `bytes`, `bytearray`
- Mapping: `dict`
- Sets: `set`, `frozenset`
- `NoneType` (the single value `None`)""",
r'''
for v in [42, 3.14, 2+3j, True, "hi", [1], (1,), range(3), b"x", {"k": 1}, {1}, frozenset({1}), None]:
    print(f"{v!r:<16} {type(v).__name__}")
'''),

Q(1, "Easy", "What is `None`?",
"""`None` is Python's null value, the only instance of `NoneType`. Functions without a `return` return `None`. It is falsy, and it is a singleton, so compare with `is None`.""",
r'''
def log(msg):
    print(msg)          # no return statement
result = log("hello")
print(result, type(result).__name__, result is None, bool(None))
'''),

Q(1, "Easy", "What does `pass` do? What about `...`?",
"""`pass` is a no-op statement used where syntax requires a statement but nothing should happen (empty function, class or branch). `...` (Ellipsis) is an object; as an expression statement it also does nothing, and it is common in stubs and type-hint protocols.""",
r'''
class Todo:
    pass
def not_yet(): ...
print(Todo(), not_yet(), ... is Ellipsis)
'''),

Q(1, "Easy", "What is the difference between `break`, `continue` and `pass`?",
"""`break` exits the nearest loop immediately. `continue` skips to the next iteration. `pass` does nothing and execution continues normally.""",
r'''
for n in range(10):
    if n == 2: continue      # skip 2
    if n == 5: break         # stop at 5
    if n == 3: pass          # no effect
    print(n, end=" ")
'''),

Q(1, "Moderate", "What does the `else` clause on a `for` or `while` loop do?",
"""The `else` block runs only if the loop finished **without** hitting `break`. It is handy for search loops: "if we never found it, do this".""",
r'''
def find(items, target):
    for i, x in enumerate(items):
        if x == target:
            print("found at", i); break
    else:
        print("not found")
find([4, 7, 9], 7)
find([4, 7, 9], 5)
'''),

Q(1, "Easy", "How do you take input and print output?",
"""`input(prompt)` reads a line from stdin and always returns a `str` (convert with `int()`, `float()`). `print(*objects, sep=' ', end='\\n', file=sys.stdout, flush=False)` writes output.""",
r'''
import io, sys
sys.stdin = io.StringIO("42\n")                 # simulate a user typing 42
age = int(input("Age? "))
print("\nnext year:", age + 1)
print("a", "b", "c", sep="-", end="!\n")
'''),

Q(1, "Easy", "What are f-strings?",
"""Formatted string literals (Python 3.6+), prefixed with `f`. Expressions inside `{}` are evaluated at runtime and support format specs (`:.2f`, `:>10`, `:,`). `{x=}` (3.8+) prints the expression and its value, which is great for debugging.""",
r'''
name, price, qty = "Widget", 1234.5, 3
print(f"{name}: {qty} x {price:,.2f} = {qty * price:>12,.2f}")
print(f"{qty=}, {price * 1.18=:.1f}")
'''),

Q(1, "Easy", "What is the difference between `/`, `//` and `%`?",
"""`/` is true division and always returns a `float`. `//` is floor division (rounds toward negative infinity). `%` is modulo, with the sign of the divisor. They satisfy `a == (a // b) * b + a % b`. `divmod(a, b)` returns both.""",
r'''
print(7 / 2, 7 // 2, 7 % 2)
print(-7 // 2, -7 % 2)       # floor, not truncation
print(divmod(-7, 2))
'''),

Q(1, "Easy", "What does `**` do?",
"""Exponentiation: `2 ** 10` is 1024. It is right-associative (`2 ** 3 ** 2` is `2 ** 9`) and binds tighter than unary minus on its left (`-2 ** 2` is -4). `pow(base, exp, mod)` does fast modular exponentiation.""",
r'''
print(2 ** 10, 2 ** 3 ** 2, -2 ** 2, (-2) ** 2)
print(pow(3, 200, 1_000_007))
'''),

Q(1, "Easy", "What are comments and docstrings?",
"""Comments start with `#` and are ignored. A docstring is a string literal as the first statement of a module, class or function; it is stored in `__doc__` and used by `help()`, IDEs and documentation tools.""",
r'''
def area(r):
    """Return the area of a circle with radius r."""
    # pi approximated for the demo
    return 3.14159 * r * r
print(area.__doc__)
'''),

Q(1, "Moderate", "What is `if __name__ == \"__main__\":` for?",
"""Each module has `__name__`. When a file is run directly it is `"__main__"`; when imported it is the module's name. The guard lets a file be both an importable module and a script, without running script code on import. It is also required with `multiprocessing` on Windows/macOS (spawn start method).""",
r'''
import types
src = 'print("module name is", __name__)\nif __name__ == "__main__":\n    print("running as script")'
exec(src, {"__name__": "__main__"})
exec(src, {"__name__": "mytool"})     # what happens on import
'''),

Q(1, "Easy", "What is the walrus operator `:=`?",
"""The assignment expression (Python 3.8+) assigns and returns a value inside an expression. It avoids repeating a computation in conditions and comprehensions.""",
r'''
data = [3, 18, 7, 42, 11]
if (n := len(data)) > 3:
    print(f"list too long ({n} items)")
print([y for x in data if (y := x * 2) > 20])
'''),

Q(1, "Easy", "How do you swap two variables?",
"""Use tuple packing and unpacking: `a, b = b, a`. The right side is evaluated first into a tuple, then unpacked. No temporary variable is needed.""",
r'''
a, b = 1, 2
a, b = b, a
print(a, b)
'''),

Q(1, "Moderate", "What is extended unpacking with `*`?",
"""A starred target collects the "rest" into a list: `first, *middle, last = seq`. It works in assignments and `for` targets. Only one starred name is allowed per level.""",
r'''
first, *middle, last = [10, 20, 30, 40, 50]
print(first, middle, last)
head, *tail = "abc"
print(head, tail)
for name, *scores in [("riya", 90, 85), ("arjun", 70)]:
    print(name, sum(scores))
'''),

Q(1, "Moderate", "What is the ternary (conditional) expression?",
"""`value_if_true if condition else value_if_false`. It is an expression, so it can be used inside assignments, returns, f-strings and comprehensions.""",
r'''
stock = 0
label = "in stock" if stock > 0 else "sold out"
print(label, [("even" if n % 2 == 0 else "odd") for n in range(4)])
'''),

Q(1, "Moderate", "What is chained comparison?",
"""Python allows `a < b < c`, meaning `a < b and b < c`, with `b` evaluated once. Any comparison operators can be chained, which can surprise people: `1 < 3 > 2` is `True`.""",
r'''
x = 7
print(0 < x < 10, 1 < 3 > 2, 1 == 1.0 == True)
'''),

Q(1, "Moderate", "What does `match` / `case` do (structural pattern matching)?",
"""Python 3.10 added `match`, which matches a value against patterns: literals, sequences, mappings, class patterns with attribute capture, alternatives `|`, guards `if`, and the wildcard `_`. It is more than a switch: it destructures data.""",
r'''
def handle(cmd):
    match cmd.split():
        case ["go", ("north" | "south") as direction]:
            return f"moving {direction}"
        case ["take", item, *rest] if rest:
            return f"taking {item} and {len(rest)} more"
        case ["take", item]:
            return f"taking {item}"
        case _:
            return "unknown command"
for c in ["go north", "take key", "take key map lamp", "dance"]:
    print(c, "->", handle(c))
'''),

Q(1, "Moderate", "What is `del`?",
"""`del` removes a **name binding**, a list item/slice, a dict key or an attribute. It does not directly free memory; the object is reclaimed only when its reference count drops to zero.""",
r'''
a = [0, 1, 2, 3, 4]
del a[1:3]
d = {"x": 1, "y": 2}; del d["x"]
b = a; del a
print(b, d)
try:
    print(a)
except NameError as e:
    print("NameError:", e)
'''),

Q(1, "Difficult", "What are Python's keywords and soft keywords?",
"""Keywords are reserved (`if`, `def`, `class`, `lambda`, `yield`, `async`, `await`, ...) and cannot be used as identifiers. **Soft keywords** (`match`, `case`, `_`, and `type` in 3.12+) are only keywords in specific contexts, so existing code using `match` or `type` as variable names still works.""",
r'''
import keyword
print(len(keyword.kwlist), "keywords, e.g.", keyword.kwlist[:6])
print("soft:", keyword.softkwlist)
match = "still a valid variable name"
print(match)
'''),

# =============== 2. DATA TYPES, VARIABLES & MUTABILITY ===============
Q(2, "Easy", "What are mutable and immutable types?",
"""Mutable objects can change in place: `list`, `dict`, `set`, `bytearray`, most user classes. Immutable objects cannot: `int`, `float`, `bool`, `str`, `tuple`, `frozenset`, `bytes`. "Changing" an immutable value creates a new object.""",
r'''
s = "hi"; before = id(s)
s += "!"
print("str new object:", id(s) != before)
lst = [1]; before = id(lst)
lst += [2]
print("list same object:", id(lst) == before, lst)
'''),

Q(2, "Easy", "How are variables different in Python compared to C/C++?",
"""A Python variable is a **name bound to an object**, not a typed memory box. Assignment never copies; it makes the name point to an object. The type belongs to the object, not the name, so a name can be rebound to any type.""",
r'''
x = 42
y = x              # y refers to the same int object
print(id(x) == id(y))
x = "now a string" # rebinding x does not affect y
print(x, y)
'''),

Q(2, "Easy", "What is dynamic typing? Is Python strongly typed?",
"""Dynamic typing means types are checked at runtime and names aren't declared with types. Python is also **strongly** typed: it won't silently convert unrelated types (`"3" + 4` raises `TypeError`), unlike JavaScript.""",
r'''
try:
    "3" + 4
except TypeError as e:
    print("TypeError:", e)
print("3" + str(4), int("3") + 4)
'''),

Q(2, "Easy", "What values are falsy in Python?",
"""`False`, `None`, zero of any numeric type (`0`, `0.0`, `0j`, `Decimal(0)`), and empty collections (`""`, `[]`, `()`, `{}`, `set()`, `range(0)`). Objects define truthiness via `__bool__` or `__len__`. Everything else is truthy.""",
r'''
from decimal import Decimal
for v in [0, 0.0, "", [], {}, set(), None, Decimal(0), "0", [0], " "]:
    print(repr(v).ljust(12), bool(v))
'''),

Q(2, "Easy", "How do `int` and `float` differ? How big can an `int` be?",
"""`int` has arbitrary precision: it grows as large as memory allows, never overflows. `float` is a 64-bit IEEE-754 double: about 15-17 significant digits, max about 1.8e308, with rounding error.""",
r'''
import sys
print(2 ** 100)
print(sys.float_info.max, sys.float_info.dig)
print(0.1 + 0.2, 0.1 + 0.2 == 0.3)
'''),

Q(2, "Moderate", "Why is `0.1 + 0.2 != 0.3`, and how do you compare floats?",
"""0.1 and 0.2 have no exact binary representation, so their sum is `0.30000000000000004`. Compare with a tolerance using `math.isclose()`, or use `decimal.Decimal` for money and `fractions.Fraction` for exact rationals.""",
r'''
import math
from decimal import Decimal
from fractions import Fraction
print(math.isclose(0.1 + 0.2, 0.3))
print(Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))
print(Fraction(1, 10) + Fraction(2, 10))
'''),

Q(2, "Moderate", "How does `round()` work? Why does `round(2.5)` return 2?",
"""`round()` uses **banker's rounding** (round half to even) to avoid bias, so `round(2.5)` is 2 and `round(3.5)` is 4. Also `round(2.675, 2)` gives 2.67 because 2.675 is stored slightly below. For commercial rounding use `Decimal.quantize(..., ROUND_HALF_UP)`.""",
r'''
from decimal import Decimal, ROUND_HALF_UP
print(round(2.5), round(3.5), round(2.675, 2))
print(Decimal("2.675").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
'''),

Q(2, "Easy", "How do you convert between types?",
"""Use constructors: `int()`, `float()`, `str()`, `list()`, `tuple()`, `set()`, `dict()`, `bool()`. `int()` accepts a base (`int("ff", 16)`). Invalid conversions raise `ValueError`.""",
r'''
print(int("42"), int("ff", 16), int(3.99), float("1e3"), str(3.5))
print(list("abc"), tuple([1, 2]), set([1, 1, 2]), dict([("a", 1)]))
try:
    int("4.2")
except ValueError as e:
    print("ValueError:", e)
'''),

Q(2, "Easy", "What is `bool` in Python, and why does `True + True` equal 2?",
"""`bool` is a subclass of `int`: `True == 1` and `False == 0`. So booleans work in arithmetic, which is handy for counting (`sum(x > 0 for x in xs)`).""",
r'''
print(True + True, isinstance(True, int), sum(x > 2 for x in [1, 5, 3, 0]))
'''),

Q(2, "Moderate", "What is the difference between `type()` and `isinstance()`?",
"""`type(x)` returns the exact class. `isinstance(x, C)` also returns True for subclasses (and for ABC virtual subclasses) and accepts a tuple of classes. Prefer `isinstance` for type checks because it respects inheritance.""",
r'''
class Animal: ...
class Dog(Animal): ...
d = Dog()
print(type(d) is Animal, isinstance(d, Animal), isinstance(3, (int, float)))
print(isinstance(True, int), type(True) is int)
'''),

Q(2, "Moderate", "What happens when you pass a mutable object to a function?",
"""Python passes **object references by value** ("call by sharing"). The function receives a reference to the same object: mutating it is visible to the caller, but rebinding the parameter name is not.""",
r'''
def mutate(lst):  lst.append(99)
def rebind(lst):  lst = [0]
nums = [1, 2]
mutate(nums); rebind(nums)
print(nums)
'''),

Q(2, "Moderate", "Shallow copy vs deep copy?",
"""A shallow copy (`copy.copy`, `list(x)`, `x[:]`, `dict.copy()`) creates a new container holding the **same** inner objects. A deep copy (`copy.deepcopy`) recursively copies inner objects too. Mutating a nested object affects shallow copies.""",
r'''
import copy
orig = [[1, 2], [3, 4]]
shallow, deep = copy.copy(orig), copy.deepcopy(orig)
orig[0].append(99)
print("shallow:", shallow)
print("deep:   ", deep)
'''),

Q(2, "Moderate", "Why does `[[0] * 3] * 3` create a surprising grid?",
"""Multiplying a list repeats **references**. `[[0]*3]*3` contains the same inner list three times, so changing one row changes all. Use a comprehension to create independent rows.""",
r'''
bad = [[0] * 3] * 3
bad[0][0] = 1
print(bad)
good = [[0] * 3 for _ in range(3)]
good[0][0] = 1
print(good)
'''),

Q(2, "Moderate", "Are tuples always immutable?",
"""A tuple's slots can't be reassigned, but if a slot holds a mutable object, that object can still change. Such a tuple is also unhashable. The famous puzzle `t[0] += [1]` both raises `TypeError` and modifies the list.""",
r'''
t = ([1, 2], "x")
t[0].append(3)
print(t)
try:
    t[0] += [4]
except TypeError as e:
    print("TypeError:", e)
print(t)            # the list was extended anyway
try:
    hash(t)
except TypeError as e:
    print("unhashable:", e)
'''),

Q(2, "Moderate", "What is hashability and which objects are hashable?",
"""An object is hashable if it has a `__hash__` that never changes during its lifetime and an `__eq__` consistent with it. Hashable objects can be dict keys and set members. Immutable built-ins (int, str, tuple of hashables, frozenset) are hashable; list, dict and set are not.""",
r'''
for v in [42, "a", (1, 2), frozenset({1}), [1], {"a": 1}, (1, [2])]:
    try:
        hash(v); print(repr(v).ljust(14), "hashable")
    except TypeError:
        print(repr(v).ljust(14), "NOT hashable")
'''),

Q(2, "Easy", "What is `id()`?",
"""`id(obj)` returns an integer unique to the object during its lifetime (in CPython, its memory address). Two objects with non-overlapping lifetimes may get the same id. `a is b` is equivalent to `id(a) == id(b)`."""),

Q(2, "Moderate", "What are augmented assignments (`+=`) and do they behave the same for all types?",
"""`x += y` calls `__iadd__` if defined (in-place, mutable types like list), otherwise `x = x + y` (new object, immutable types). So `+=` mutates a list shared by other names but creates a new string or tuple.""",
r'''
a = [1]; b = a
a += [2]            # in place: b sees it
s = "x"; t = s
s += "y"            # new object: t unchanged
print(b, t)
'''),

Q(2, "Moderate", "What are `bytes` and `bytearray`, and how do they relate to `str`?",
"""`str` is a sequence of Unicode code points. `bytes` is an immutable sequence of 0-255 integers (raw data); `bytearray` is its mutable version. Convert with `str.encode(encoding)` and `bytes.decode(encoding)`.""",
r'''
s = "₹100 café"
b = s.encode("utf-8")
print(len(s), len(b), b)
print(b.decode("utf-8") == s, b[0], list(b[:3]))
ba = bytearray(b"hello"); ba[0] = ord("H"); print(ba)
'''),

Q(2, "Moderate", "What is `complex` and when is it used?",
"""Built-in complex numbers, written with a `j` suffix (`3+4j`). They support arithmetic, `.real`, `.imag`, `abs()` (magnitude), and the `cmath` module. Used in signal processing, electrical engineering and FFTs.""",
r'''
import cmath
z = 3 + 4j
print(z.real, z.imag, abs(z), z.conjugate(), cmath.phase(1j))
'''),

Q(2, "Difficult", "What are `NaN` and `inf`, and why is `nan != nan`?",
"""IEEE-754 floats include `inf`, `-inf` and `nan` (not a number). By the standard, NaN compares unequal to everything, including itself. Use `math.isnan()`. Containers check identity first, so `nan in [nan]` can be True for the same object.""",
r'''
import math
nan, inf = float("nan"), float("inf")
print(nan == nan, math.isnan(nan), inf > 1e308, inf - inf)
print(nan in [nan], float("nan") in [nan])
'''),

Q(2, "Difficult", "Explain integer caching and string interning in CPython.",
"""CPython preallocates ints from -5 to 256, so all references to them share objects. Strings that look like identifiers and compile-time constants are often interned. This is an **implementation detail**: never rely on `is` for numbers or strings. `sys.intern()` interns explicitly.""",
r'''
import sys
a, b = 256, int("256"); c, d = 257, int("257")
print(a is b, c is d)
s1 = "".join(["user", "_id"]); s2 = "user_id"
print(s1 is s2, sys.intern(s1) is sys.intern(s2))
'''),

Q(2, "Difficult", "What is the difference between `==` and `is` for `True`, and why does `1 == True` matter for dict keys?",
"""Because `True == 1` and `hash(True) == hash(1)`, they are the **same dict key**. Mixing them causes one to overwrite the other, a classic bug when keys come from different sources.""",
r'''
d = {1: "one", True: "true", 1.0: "float"}
print(d)
print({0, False, 0.0})
'''),

Q(2, "Moderate", "What are constants in Python?",
"""Python has no true constants. By convention, module-level `UPPER_CASE` names are treated as constants. `typing.Final` marks a name as not-to-be-reassigned for type checkers (mypy), but it is not enforced at runtime.""",
r'''
from typing import Final
MAX_RETRIES: Final = 3
MAX_RETRIES = 4          # allowed at runtime; mypy would report an error
print(MAX_RETRIES)
'''),

]
