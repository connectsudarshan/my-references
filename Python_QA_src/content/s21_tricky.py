QUESTIONS = [

# =============== 21. TRICKY QUESTIONS & GOTCHAS ===============
Q(21, "Moderate", "What does this print? `def f(x, lst=[]): lst.append(x); return lst` called as `f(1)`, `f(2)`",
"""`[1, 2]` for the second call (and the first call's result is the same list). The default list is created once when `def` runs and shared by every call that doesn't pass `lst`. Use `lst=None` and create the list inside.""",
r'''
def f(x, lst=[]):
    lst.append(x)
    return lst
a = f(1); b = f(2)
print(a, b, a is b)
'''),

Q(21, "Moderate", "What does `[lambda: i for i in range(3)]` return when each lambda is called?",
"""`[2, 2, 2]`. Closures capture the variable `i`, not its value at creation time (late binding); by the time they run, `i` is 2. Bind the value with a default argument: `lambda i=i: i`.""",
r'''
fs = [lambda: i for i in range(3)]
print([f() for f in fs], [g() for g in [lambda i=i: i for i in range(3)]])
'''),

Q(21, "Moderate", "Why does `0.1 + 0.2 == 0.3` return False?",
"""Binary floating point can't represent 0.1, 0.2 or 0.3 exactly; the sum is `0.30000000000000004`. Compare with `math.isclose`, or use `Decimal` for money.""",
r'''
import math
print(0.1 + 0.2, 0.1 + 0.2 == 0.3, math.isclose(0.1 + 0.2, 0.3))
'''),

Q(21, "Moderate", "What is `[[0] * 3] * 3` and why does changing one cell change a whole column?",
"""The outer `* 3` copies the **reference** to the same inner list three times, so all rows are one object. Build rows independently: `[[0] * 3 for _ in range(3)]`.""",
r'''
grid = [[0] * 3] * 3
grid[0][0] = 9
print(grid, grid[0] is grid[1])
'''),

Q(21, "Difficult", "`t = ([1], 2)`; what happens with `t[0] += [3]`?",
"""Both: it raises `TypeError` **and** the list is modified. `+=` first calls `list.__iadd__` (mutating the list in place, succeeds), then tries to assign the result back to `t[0]` (tuple item assignment, fails).""",
r'''
t = ([1], 2)
try:
    t[0] += [3]
except TypeError as e:
    print("TypeError:", e)
print(t)
'''),

Q(21, "Moderate", "Why does `a = 256; b = 256; a is b` give True but the same with 257 can give False?",
"""CPython caches small integers from -5 to 256, so all references to 256 share one object. 257 created at runtime is a new object (though constants in the same code block may be merged by the compiler). Never use `is` to compare numbers; use `==`.""",
r'''
a, b = 256, int("256")
c, d = 257, int("257")
print(a is b, c is d, c == d)
'''),

Q(21, "Moderate", "What does `print(True + True + True)` and `{1: 'a', True: 'b'}` give?",
"""`3`, and `{1: 'b'}`. `bool` is a subclass of `int` (`True == 1`, same hash), so `True` and `1` are the same dict key: the key object stays `1` and the value is overwritten.""",
r'''
print(True + True + True, {1: "a", True: "b"}, isinstance(True, int))
'''),

Q(21, "Moderate", "Why can `x = x + [1]` and `x += [1]` behave differently?",
"""`x += [1]` mutates the list in place (other names referring to it see the change); `x = x + [1]` creates a new list and rebinds only `x`.""",
r'''
a = [0]; alias = a
a += [1]
b = [0]; alias_b = b
b = b + [1]
print(alias, alias_b)
'''),

Q(21, "Moderate", "What happens if you modify a list while iterating over it?",
"""Elements get skipped (removing) or the loop runs forever (appending), because iteration uses an index. Iterate over a copy (`for x in lst[:]`) or build a new list with a comprehension. Dicts and sets raise `RuntimeError` if their size changes during iteration.""",
r'''
nums = [1, 2, 2, 3, 2, 4]
for n in nums:
    if n == 2: nums.remove(n)
print("buggy:", nums)
nums = [1, 2, 2, 3, 2, 4]
print("fixed:", [n for n in nums if n != 2])
'''),

Q(21, "Moderate", "Why does this raise `UnboundLocalError`? `count = 0; def inc(): count += 1`",
"""Because `count` is assigned inside `inc`, the compiler makes it local to the whole function; `count += 1` reads the local before it has a value. Use `global count` (or better, pass and return values, or use a class).""",
r'''
count = 0
def inc():
    count += 1
try:
    inc()
except UnboundLocalError as e:
    print("UnboundLocalError:", e)
'''),

Q(21, "Moderate", "What does `print(round(2.5), round(3.5), round(0.5))` print?",
"""`2 4 0`. Python uses banker's rounding (round half to even) to avoid systematic bias. Use `Decimal.quantize(..., ROUND_HALF_UP)` for "school" rounding.""",
r'''
print(round(2.5), round(3.5), round(0.5), round(-1.5))
'''),

Q(21, "Moderate", "What is the result of `-7 // 2` and `-7 % 2`, and why?",
"""`-4` and `1`. Floor division rounds toward negative infinity (not toward zero like C), and `%` takes the sign of the divisor so that `(a // b) * b + a % b == a` holds. `math.fmod` and `int(a / b)` truncate toward zero instead.""",
r'''
import math
print(-7 // 2, -7 % 2, int(-7 / 2), math.fmod(-7, 2))
'''),

Q(21, "Difficult", "What does `try: return 1 finally: return 2` return?",
"""`2`. A `return` in `finally` overrides the earlier return and even discards an in-flight exception. Python 3.14 emits a `SyntaxWarning` for `return`/`break`/`continue` in `finally` (PEP 765); avoid it.""",
r'''
import warnings
warnings.simplefilter("ignore", SyntaxWarning)
exec(compile("def f():\n    try:\n        return 1\n    finally:\n        return 2\nprint(f())", "<t>", "exec"))
'''),

Q(21, "Moderate", "Is `a == b` for two lists with the same elements always equal to `a is b`?",
"""No. `==` compares contents, `is` compares identity. `[1, 2] == [1, 2]` is True but they're different objects, so `is` is False. Use `is` only for singletons like `None`.""",
r'''
a, b = [1, 2], [1, 2]
print(a == b, a is b, None is None)
'''),

Q(21, "Moderate", "What does `print('a' 'b')` and `x = 'hello', ` produce?",
"""`'a' 'b'` is implicit string concatenation at compile time: `ab`. A trailing comma creates a tuple: `x` is `('hello',)`. Both cause subtle bugs, e.g. a missing comma in a list of strings silently merges two items.""",
r'''
print('a' 'b')
x = 'hello',
servers = ["db1", "db2" "db3"]      # missing comma!
print(x, type(x).__name__, servers, len(servers))
'''),

Q(21, "Moderate", "What does `bool('False')`, `bool([])` and `bool([0])` give?",
"""`True`, `False`, `True`. Any non-empty string is truthy (including `'False'` and `'0'`), empty containers are falsy, and a list containing a falsy value is still non-empty. Parse strings explicitly for config flags.""",
r'''
print(bool("False"), bool([]), bool([0]), bool("0"), bool(0.0))
def parse_flag(s): return s.strip().lower() in {"1", "true", "yes", "on"}
print(parse_flag("False"), parse_flag(" YES "))
'''),

Q(21, "Moderate", "Why does `a = []; b = a; b.append(1)` change `a`?",
"""Assignment binds another name to the same object; it never copies. Use `a.copy()`, `list(a)`, `a[:]` (shallow) or `copy.deepcopy(a)` when you need an independent copy.""",
r'''
a = []; b = a; b.append(1)
c = a.copy(); c.append(2)
print(a, b, c)
'''),

Q(21, "Difficult", "Why doesn't a shallow copy protect nested data?",
"""A shallow copy creates a new outer container but reuses the inner objects. Mutating a nested list through the copy changes the original too. `copy.deepcopy` copies recursively.""",
r'''
import copy
config = {"retries": 3, "hosts": ["a", "b"]}
shallow = config.copy(); deep = copy.deepcopy(config)
shallow["hosts"].append("c")
print(config["hosts"], deep["hosts"])
'''),

Q(21, "Moderate", "What does `dict.fromkeys(['a', 'b'], [])` do that surprises people?",
"""All keys share the **same** list object, so appending to one key's value appears under every key. Use a comprehension: `{k: [] for k in keys}` or `defaultdict(list)`.""",
r'''
d = dict.fromkeys(["a", "b"], [])
d["a"].append(1)
print(d, {k: [] for k in "ab"})
'''),

Q(21, "Moderate", "Why is `is not` different from `not ... is`, and what does `not x == y` mean?",
"""`x is not y` is a single operator (identity inequality). `not x == y` parses as `not (x == y)` because comparisons bind tighter than `not`. They're equivalent to what they look like, but `x == not y` is a syntax error; write `x == (not y)`."""),

Q(21, "Difficult", "What is printed? `x = 10` then `def f(): print(x); x = 5`, calling `f()`",
"""`UnboundLocalError`, not `10`. The assignment `x = 5` anywhere in the function makes `x` local for the whole function body, so the earlier `print(x)` reads an unassigned local.""",
r'''
x = 10
def f():
    print(x)
    x = 5
try:
    f()
except UnboundLocalError as e:
    print("UnboundLocalError:", e)
'''),

Q(21, "Moderate", "Why does `sorted(['b', 'A', 'c'])` put 'A' first, and how do you sort case-insensitively?",
"""Strings compare by Unicode code point, and uppercase letters come before lowercase. Use `key=str.casefold` (or `str.lower`).""",
r'''
words = ["banana", "apple", "Cherry"]
print(sorted(words), sorted(words, key=str.casefold))
'''),

Q(21, "Moderate", "What does `sorted` do with mixed types like `[1, 'a']` in Python 3?",
"""It raises `TypeError` because `<` isn't defined between `int` and `str`. Python 2 allowed arbitrary cross-type ordering; Python 3 removed it. Provide a `key` that maps everything to comparable values.""",
r'''
try:
    sorted([3, "a", 1])
except TypeError as e:
    print("TypeError:", e)
print(sorted([3, "a", 1], key=str))
'''),

Q(21, "Moderate", "What does `print(1 < 2 < 3, 3 > 2 > 1, 1 < 3 > 2)` print?",
"""`True True True`. Comparisons chain: `a < b < c` means `a < b and b < c`. So `1 < 3 > 2` is `1 < 3 and 3 > 2`, which is True, although it reads strangely.""",
r'''
print(1 < 2 < 3, 3 > 2 > 1, 1 < 3 > 2, (1 < 3) > 2)
'''),

Q(21, "Difficult", "Why is `nan` in a list found by `in` but not equal to itself?",
"""`float('nan') != float('nan')` by IEEE 754 rules, but container membership checks **identity first** (`x is item or x == item`). The same NaN object is found; a different NaN object is not.""",
r'''
nan = float("nan")
print(nan == nan, nan in [nan], float("nan") in [nan])
'''),

Q(21, "Moderate", "What does `len({1, 1.0, True})` return?",
"""`1`. `1`, `1.0` and `True` are equal and have the same hash, so the set keeps only the first one.""",
r'''
s = {1, 1.0, True}
print(len(s), s)
'''),

Q(21, "Moderate", "Why does a generator produce nothing the second time you loop over it?",
"""A generator is an iterator: it's exhausted after one pass and stays empty. Recreate it, store results in a list, or wrap the logic in an iterable class whose `__iter__` makes a new generator.""",
r'''
g = (x * x for x in range(3))
print(list(g), list(g))
'''),

Q(21, "Moderate", "What does `print(type(()), type((1)), type((1,)))` show?",
"""`<class 'tuple'> <class 'int'> <class 'tuple'>`. Parentheses alone don't make a tuple; the **comma** does. `(1)` is just the integer 1.""",
r'''
print(type(()), type((1)), type((1,)), type(1,))
'''),

Q(21, "Difficult", "Class attribute trap: why do all instances share this list?",
"""`items = []` in the class body is a **class** attribute, created once and shared by all instances. `self.items.append(...)` mutates that shared list. Initialize mutable state in `__init__` (or `field(default_factory=list)` in dataclasses).""",
r'''
class Cart:
    items = []
    def add(self, x): self.items.append(x)
a, b = Cart(), Cart()
a.add("pen")
print(b.items, Cart.items)
'''),

Q(21, "Moderate", "What does `\"abc\" * -1` and `[1, 2][5:10]` return?",
"""An empty string and an empty list. Multiplying a sequence by zero or a negative number gives an empty sequence, and slicing never raises `IndexError` for out-of-range bounds (indexing does).""",
r'''
print(repr("abc" * -1), [1, 2][5:10])
try:
    [1, 2][5]
except IndexError as e:
    print("IndexError:", e)
'''),

Q(21, "Moderate", "Does `except Exception` catch `KeyboardInterrupt` and `SystemExit`?",
"""No. Both inherit from `BaseException`, not `Exception`, precisely so that generic handlers don't block Ctrl+C or `sys.exit()`. A bare `except:` does catch them, which is why it's discouraged.""",
r'''
print(issubclass(KeyboardInterrupt, Exception), issubclass(SystemExit, BaseException))
'''),

Q(21, "Difficult", "Why can't you use a list as a dict key, but you can use a tuple (sometimes)?",
"""Dict keys must be hashable, and a hash must not change while the key is in the dict. Lists are mutable, so they're unhashable. Tuples are hashable only if all their items are hashable: `(1, 2)` works, `(1, [2])` doesn't.""",
r'''
d = {(1, 2): "ok"}
for key in ([1, 2], (1, [2])):
    try:
        d[key] = "x"
    except TypeError as e:
        print(type(key).__name__, "->", e)
'''),

Q(21, "Moderate", "What's the output of `print(\"%s\" % (1, 2))`?",
"""`TypeError: not all arguments converted during string formatting`. A tuple on the right of `%` is treated as the argument list. To print a tuple with one `%s`, wrap it: `"%s" % ((1, 2),)`, or use f-strings.""",
r'''
try:
    print("%s" % (1, 2))
except TypeError as e:
    print("TypeError:", e)
t = (1, 2)
print("%s" % (t,), f"{t}")
'''),

Q(21, "Difficult", "Why does `x = x.sort()` leave `x` as None?",
"""In-place methods (`list.sort`, `list.append`, `list.reverse`, `dict.update`, `random.shuffle`) return `None` by convention, to make clear they mutate rather than return a new object. Use `sorted(x)` for a new list, or call `x.sort()` without assigning.""",
r'''
x = [3, 1, 2]
x = x.sort()
print(x)
y = [3, 1, 2]
print(sorted(y), y)
'''),

Q(21, "Moderate", "Does `is` work for comparing strings?",
"""Not reliably. Short identifier-like strings and compile-time constants are often interned (same object), so `is` may appear to work, but strings built at runtime usually aren't. Always use `==` for string comparison.""",
r'''
a = "nvme"
b = "".join(["nv", "me"])
print(a == b, a is b)
'''),

Q(21, "Difficult", "What does `print(any([]), all([]))` print, and why?",
"""`False True`. `any` asks "is at least one item true?" (none exist, so False); `all` asks "is there any item that is false?" (none exist, so it's vacuously True). This matters for validations like `all(check(x) for x in results)` on an empty results list.""",
r'''
print(any([]), all([]))
results = []
print("all tests passed?", all(r == "PASS" for r in results), "<- vacuous truth: guard for empty input")
'''),

Q(21, "Moderate", "What is the output of `print(list(zip([1, 2, 3], 'ab')))`?",
"""`[(1, 'a'), (2, 'b')]`. `zip` stops at the shortest input silently, which can hide data loss. Use `zip(..., strict=True)` (3.10+) to raise on mismatched lengths, or `itertools.zip_longest` to pad.""",
r'''
print(list(zip([1, 2, 3], "ab")))
try:
    list(zip([1, 2, 3], "ab", strict=True))
except ValueError as e:
    print("ValueError:", e)
'''),

Q(21, "Difficult", "Why does `json.loads(json.dumps({1: (2, 3)}))` not round-trip?",
"""JSON object keys are always strings and JSON has no tuple type, so `{1: (2, 3)}` comes back as `{'1': [2, 3]}`. Serialize and deserialize with explicit schemas or conversion when types matter.""",
r'''
import json
original = {1: (2, 3)}
back = json.loads(json.dumps(original))
print(back, back == original)
'''),

Q(21, "Moderate", "What does `datetime.now()` get wrong in distributed systems?",
"""It returns a **naive** local time with no timezone. Comparing or storing naive datetimes from servers in different zones (or across DST changes) gives wrong results. Use `datetime.now(timezone.utc)` for storage and convert for display.""",
r'''
from datetime import datetime, timezone
naive, aware = datetime.now(), datetime.now(timezone.utc)
print(naive.tzinfo, aware.tzinfo)
try:
    naive < aware
except TypeError as e:
    print("TypeError:", e)
'''),

]
