QUESTIONS = [

# =============== 3. STRINGS & TEXT ===============
Q(3, "Easy", "Are strings mutable in Python?",
"""No. `str` is immutable: methods like `upper()` or `replace()` return new strings, and item assignment raises `TypeError`. Build strings from pieces with `''.join()` or `io.StringIO`.""",
r'''
s = "python"
try:
    s[0] = "P"
except TypeError as e:
    print("TypeError:", e)
print(s.capitalize(), s)
'''),

Q(3, "Easy", "How does string slicing work?",
"""`s[start:stop:step]`: start inclusive, stop exclusive, negative indices count from the end, and slices never raise `IndexError`. `s[::-1]` reverses a string.""",
r'''
s = "interview"
print(s[0:5], s[-4:], s[::2], s[::-1], s[100:], repr(s[5:2]))
'''),

Q(3, "Easy", "What are the most-used string methods?",
"""`split`, `join`, `strip/lstrip/rstrip`, `replace`, `find/index`, `startswith/endswith`, `upper/lower/title/casefold`, `count`, `isdigit/isalpha/isalnum`, `zfill`, `center/ljust/rjust`, and 3.9+ `removeprefix/removesuffix`.""",
r'''
line = "  order-42, PAID ,  1299.00  "
parts = [p.strip() for p in line.split(",")]
print(parts)
print(parts[0].removeprefix("order-"), parts[1].lower(), "7".zfill(3), "|" + "hi".center(8) + "|")
print(", ".join(["a", "b", "c"]), "banana".count("an"), "report.pdf".endswith((".pdf", ".doc")))
'''),

Q(3, "Moderate", "`find()` vs `index()`?",
"""Both return the lowest index of a substring. `find()` returns `-1` when not found; `index()` raises `ValueError`. Use `in` if you only need a yes/no answer.""",
r'''
s = "hello world"
print(s.find("world"), s.find("xyz"), "lo w" in s)
try:
    s.index("xyz")
except ValueError as e:
    print("ValueError:", e)
'''),

Q(3, "Moderate", "Why is `''.join(list)` preferred over `+=` in a loop?",
"""Strings are immutable, so `s += piece` may create a new string each time, which is O(n²) in the worst case. `''.join(parts)` computes the total size once and copies each piece once: O(n). (CPython sometimes optimizes `+=` in place, but don't rely on it.)""",
r'''
import timeit
parts = ["x"] * 20000
def concat():
    s = ""
    for p in parts: s = s + p     # forces a new string each time
    return s
def join(): return "".join(parts)
print("concat %.1f ms" % (timeit.timeit(concat, number=20) * 50))
print("join   %.1f ms" % (timeit.timeit(join, number=20) * 50))
'''),

Q(3, "Moderate", "What are the ways to format strings in Python?",
"""- `%` formatting: `"%s is %d" % (name, age)` (old style)
- `str.format()`: `"{} is {}".format(name, age)`
- f-strings (3.6+): `f"{name} is {age}"`, the fastest and most readable
- `string.Template`: `$name` placeholders, safe for user-supplied templates""",
r'''
from string import Template
name, age = "Riya", 31
print("%s is %d" % (name, age))
print("{} is {}".format(name, age), "{0}-{0}".format("ha"))
print(f"{name} is {age}")
print(Template("$name is $age").substitute(name=name, age=age))
'''),

Q(3, "Moderate", "What are raw strings and when are they used?",
"""A raw string `r"..."` treats backslashes literally, so `r"\\n"` is two characters. They are used for regular expressions and Windows paths. A raw string cannot end with an odd number of backslashes.""",
r'''
print(len("\n"), len(r"\n"))
import re
print(re.findall(r"\d+", "order 42 has 3 items"))
print(r"C:\new\table")
'''),

Q(3, "Moderate", "What is the difference between `str()` and `repr()`?",
"""`str()` (`__str__`) is a readable form for end users. `repr()` (`__repr__`) is an unambiguous form for developers, ideally valid Python that recreates the object. Containers show their items' `repr`. f-strings use `!r` for repr.""",
r'''
import datetime
d = datetime.date(2026, 9, 28)
print(str(d), repr(d))
print(str("hi"), repr("hi"), [ "hi" ])
print(f"{d!r}")
'''),

Q(3, "Moderate", "How does Python handle Unicode? What is an encoding?",
"""A `str` holds Unicode code points. An encoding (UTF-8, UTF-16, Latin-1) maps code points to bytes. Decode bytes to text at input, work with `str` internally, encode at output ("Unicode sandwich"). Always pass `encoding="utf-8"` to `open()`.""",
r'''
text = "नमस्ते ₹ 😊"
for enc in ("utf-8", "utf-16"):
    print(enc, len(text.encode(enc)), "bytes")
print(len(text), "code points", [hex(ord(c)) for c in "₹😊"])
try:
    text.encode("ascii")
except UnicodeEncodeError as e:
    print("UnicodeEncodeError:", e.reason)
'''),

Q(3, "Difficult", "Why can `len()` of a string differ from what a user sees as characters?",
"""`len()` counts code points, but one visible character (grapheme) can be several: an emoji with a skin tone modifier, a family emoji joined by zero-width joiners, or a letter plus a combining accent. Use `unicodedata.normalize` for comparisons and a grapheme library (e.g. `regex` with `\\X`) for user-visible length.""",
r'''
import unicodedata
cafe1 = "café"                      # precomposed é
cafe2 = "cafe\u0301"                # e + combining acute accent
print(len(cafe1), len(cafe2), cafe1 == cafe2)
print(unicodedata.normalize("NFC", cafe1) == unicodedata.normalize("NFC", cafe2))
print(len("👍🏽"), len("👨‍👩‍👧"))
'''),

Q(3, "Moderate", "`lower()` vs `casefold()`?",
"""`casefold()` is a more aggressive lowercase for **case-insensitive comparisons** across languages; for example German "ß" casefolds to "ss". Use it (plus normalization) when comparing user text.""",
r'''
print("Straße".lower(), "Straße".casefold(), "STRASSE".casefold() == "Straße".casefold())
'''),

Q(3, "Easy", "How do you check if a string is a palindrome?",
"""Normalize it (keep only alphanumerics, lowercase), then compare with its reverse.""",
r'''
def is_palindrome(s: str) -> bool:
    clean = [c.casefold() for c in s if c.isalnum()]
    return clean == clean[::-1]
print(is_palindrome("A man, a plan, a canal: Panama"), is_palindrome("python"))
'''),

Q(3, "Moderate", "How do you count character or word frequencies?",
"""Use `collections.Counter`: it counts any iterable and has `most_common(n)`.""",
r'''
from collections import Counter
text = "the quick brown fox jumps over the lazy dog the end"
words = Counter(text.split())
print(words.most_common(2))
print(Counter("mississippi").most_common(3))
'''),

Q(3, "Moderate", "What are the most useful `re` functions?",
"""`re.search` (first match anywhere), `re.match` (only at start), `re.fullmatch` (entire string), `re.findall` (all matches as strings/tuples), `re.finditer` (match objects), `re.sub` (replace), `re.split`, `re.compile` (reuse a pattern). Named groups `(?P<name>...)` make matches readable.""",
r'''
import re
log = "2026-09-28 10:15:02 ERROR [payments] timeout after 3000ms"
m = re.search(r"(?P<date>\d{4}-\d\d-\d\d) \S+ (?P<level>[A-Z]+) \[(?P<svc>\w+)\]", log)
print(m.group("level"), m["svc"], m.groupdict())
print(re.sub(r"\d+ms", "<dur>", log))
print(re.match(r"ERROR", log), bool(re.search(r"ERROR", log)))
'''),

Q(3, "Difficult", "What is the difference between greedy and non-greedy regex quantifiers?",
"""`*`, `+`, `?`, `{m,n}` are greedy: they match as much as possible and backtrack. Adding `?` (`*?`, `+?`) makes them lazy: match as little as possible. Greedy patterns over HTML-like text often capture too much.""",
r'''
import re
html = "<b>bold</b> and <i>italic</i>"
print(re.findall(r"<.*>", html))
print(re.findall(r"<.*?>", html))
'''),

Q(3, "Moderate", "How do you split a string on multiple delimiters?",
"""Use `re.split` with a character class or alternation. Note that `str.split()` with no argument splits on any whitespace run and drops empty strings.""",
r'''
import re
print(re.split(r"[,;|\s]+", "a, b;c | d  e"))
print("  a  b\tc\n".split(), "a,,b".split(","))
'''),

Q(3, "Moderate", "How do you reverse the words in a sentence?",
"""Split into words, reverse the list, join back.""",
r'''
s = "Python is fun to learn"
print(" ".join(reversed(s.split())))
print(" ".join(w[::-1] for w in s.split()))   # reverse each word instead
'''),

Q(3, "Moderate", "How do you check if two strings are anagrams?",
"""Compare sorted characters (O(n log n)) or character counts with `Counter` (O(n)). Normalize case and spaces first.""",
r'''
from collections import Counter
def anagram(a, b):
    norm = lambda s: Counter(s.replace(" ", "").lower())
    return norm(a) == norm(b)
print(anagram("Listen", "Silent"), anagram("Dormitory", "dirty room"), anagram("abc", "abd"))
'''),

Q(3, "Difficult", "What is `str.translate` and when is it faster than `replace`?",
"""`str.maketrans` builds a mapping of characters to replacements (or `None` to delete), and `translate` applies it in a single pass. It is faster than chaining many `replace()` calls for character-level substitutions.""",
r'''
table = str.maketrans({"0": "o", "1": "l", "3": "e", "@": "a", "!": None})
print("h3ll0 w0r1d @gain!!".translate(table))
import string
print("Hello, World! 123".translate(str.maketrans("", "", string.punctuation)))
'''),

Q(3, "Moderate", "How do you find the first non-repeating character in a string?",
"""Count characters with `Counter` (dicts keep insertion order), then scan the string for the first count of 1. O(n) time.""",
r'''
from collections import Counter
def first_unique(s):
    counts = Counter(s)
    return next((c for c in s if counts[c] == 1), None)
print(first_unique("swiss"), first_unique("aabb"))
'''),

Q(3, "Easy", "How do you check if a string contains only digits? What's the catch with `isdigit()`?",
"""`isdigit()`, `isnumeric()` and `isdecimal()` accept Unicode digits too (e.g. "²" or Devanagari digits), and none accept "-5" or "3.2". For validation, try `int()`/`float()` inside `try`, or use a regex.""",
r'''
for s in ["123", "²", "१२३", "-5", "3.2"]:
    print(repr(s).ljust(7), s.isdigit(), s.isdecimal())
def is_int(s):
    try: int(s); return True
    except ValueError: return False
print(is_int("-5"), is_int("3.2"))
'''),

# =============== 4. LISTS, TUPLES, DICTS & SETS ===============
Q(4, "Easy", "What is the difference between a list and a tuple?",
"""Lists are mutable and meant for homogeneous, variable-length collections. Tuples are immutable, hashable (if their items are), slightly smaller and faster to create, and meant for fixed-structure records (like a row or coordinate). Tuples can be dict keys; lists cannot.""",
r'''
import sys
lst, tup = [1, 2, 3], (1, 2, 3)
print(sys.getsizeof(lst), sys.getsizeof(tup))
locations = {(12.97, 77.59): "Bengaluru"}
print(locations[(12.97, 77.59)])
'''),

Q(4, "Easy", "`append()` vs `extend()` vs `insert()`?",
"""`append(x)` adds one object at the end (even if it's a list). `extend(iterable)` adds each item. `insert(i, x)` inserts before index `i` (O(n)).""",
r'''
a = [1, 2]; a.append([3, 4]); print(a)
b = [1, 2]; b.extend([3, 4]); print(b)
c = [1, 2]; c.insert(0, 0); print(c)
'''),

Q(4, "Easy", "`remove()` vs `pop()` vs `del`?",
"""`remove(x)` deletes the first item equal to `x` (ValueError if missing). `pop(i=-1)` removes and **returns** the item at index `i`. `del lst[i]` or `del lst[a:b]` deletes by index/slice without returning.""",
r'''
a = [10, 20, 30, 20]
a.remove(20); print(a)
print(a.pop(), a)
del a[0]; print(a)
'''),

Q(4, "Moderate", "`sort()` vs `sorted()`?",
"""`list.sort()` sorts in place and returns `None`. `sorted(iterable)` returns a new list and works on any iterable. Both accept `key=` and `reverse=`, and both are **stable** (Timsort, O(n log n)), so you can sort by multiple keys in passes or with a tuple key.""",
r'''
people = [("riya", 31), ("arjun", 25), ("meera", 31)]
print(sorted(people, key=lambda p: (-p[1], p[0])))
nums = [3, 1, 2]
print(nums.sort(), nums)
'''),

Q(4, "Moderate", "What is the time complexity of common list operations?",
"""- index / assign / `len` / `append` / `pop()` from end: O(1) (append is amortized)
- `insert(0, x)` / `pop(0)` / `del lst[0]`: O(n) (shifts elements)
- `x in lst` / `remove` / `index`: O(n)
- slicing `lst[a:b]`: O(b-a); `sort`: O(n log n)

For fast operations at both ends, use `collections.deque`.""",
r'''
from collections import deque
import timeit
lst, dq = list(range(100_000)), deque(range(100_000))
print("list.pop(0):    %.2f ms" % (timeit.timeit(lambda: (lst.insert(0, 1), lst.pop(0)), number=2000) * 1000))
print("deque.popleft(): %.2f ms" % (timeit.timeit(lambda: (dq.appendleft(1), dq.popleft()), number=2000) * 1000))
'''),

Q(4, "Easy", "How do you remove duplicates from a list while keeping order?",
"""`list(dict.fromkeys(items))`: dicts keep insertion order (3.7+) and keys are unique. `list(set(items))` also removes duplicates but loses order.""",
r'''
items = ["b", "a", "b", "c", "a"]
print(list(dict.fromkeys(items)))
print(sorted(set(items)))
'''),

Q(4, "Easy", "How do dictionaries work and what are their key operations?",
"""A dict maps hashable keys to values using a hash table: average O(1) lookup, insert and delete. Since Python 3.7 dicts preserve insertion order. Key methods: `get`, `setdefault`, `pop`, `update`, `keys/values/items`, `|` merge (3.9+).""",
r'''
stock = {"apple": 10, "pear": 0}
stock["kiwi"] = 5
print(stock.get("mango", 0), stock.pop("pear"), list(stock.items()))
print(stock | {"apple": 99, "fig": 1})
'''),

Q(4, "Moderate", "`dict[key]` vs `dict.get(key)` vs `setdefault` vs `defaultdict`?",
"""`d[k]` raises `KeyError` if missing. `d.get(k, default)` returns a default without inserting. `d.setdefault(k, default)` returns the value, inserting the default if missing. `defaultdict(factory)` inserts `factory()` automatically on missing-key access, ideal for grouping.""",
r'''
from collections import defaultdict
orders = [("riya", "A1"), ("arjun", "B2"), ("riya", "C3")]
groups = defaultdict(list)
for user, oid in orders:
    groups[user].append(oid)
print(dict(groups))
d = {}
d.setdefault("tags", []).append("new")
print(d, d.get("missing", "n/a"))
'''),

Q(4, "Moderate", "How do you merge two dictionaries?",
"""`a | b` (3.9+) returns a new dict; `a |= b` updates in place; `{**a, **b}` works in 3.5+; `a.update(b)`. On duplicate keys, the right-hand dict wins. For nested dicts you need a recursive merge.""",
r'''
defaults = {"timeout": 5, "retries": 3}
user = {"timeout": 10}
print(defaults | user, {**defaults, **user})
'''),

Q(4, "Moderate", "How do you sort a dictionary by value?",
"""Sort its items with a key function and rebuild a dict (dicts keep order).""",
r'''
scores = {"riya": 88, "arjun": 95, "meera": 72}
print(dict(sorted(scores.items(), key=lambda kv: kv[1], reverse=True)))
print(max(scores, key=scores.get))
'''),

Q(4, "Moderate", "What are dictionary views?",
"""`keys()`, `values()` and `items()` return live **views** that reflect later changes to the dict. `keys()` and `items()` views support set operations. Modifying a dict's size while iterating over it raises `RuntimeError`.""",
r'''
d = {"a": 1, "b": 2}
k = d.keys()
d["c"] = 3
print(k, k & {"a", "z"})
try:
    for key in d:
        d["new"] = 0
except RuntimeError as e:
    print("RuntimeError:", e)
'''),

Q(4, "Easy", "What are sets and their operations?",
"""An unordered collection of unique hashable items with O(1) average membership tests. Operations: union `|`, intersection `&`, difference `-`, symmetric difference `^`, subset `<=`. `frozenset` is the immutable, hashable version.""",
r'''
python_devs = {"riya", "arjun", "meera"}
go_devs = {"arjun", "kabir"}
print(python_devs & go_devs, python_devs - go_devs, python_devs ^ go_devs)
print({"riya"} <= python_devs, frozenset({1, 2}) in {frozenset({1, 2})})
'''),

Q(4, "Moderate", "Why is `x in set` much faster than `x in list`?",
"""A set uses a hash table: membership is O(1) on average. A list is scanned linearly: O(n). For repeated lookups, convert to a set once.""",
r'''
import timeit
data = list(range(100_000)); s = set(data)
print("list: %.3f ms" % (timeit.timeit(lambda: 99_999 in data, number=100) * 10))
print("set:  %.5f ms" % (timeit.timeit(lambda: 99_999 in s, number=100) * 10))
'''),

Q(4, "Moderate", "What is a `namedtuple` and when would you use it?",
"""A tuple subclass with named fields: readable (`p.x`), immutable, memory-light, still unpackable and indexable. `typing.NamedTuple` adds type hints. Use for simple records; use `dataclass` when you need mutability, defaults with logic, or methods.""",
r'''
from typing import NamedTuple
class Point(NamedTuple):
    x: float
    y: float = 0.0
p = Point(3, 4)
x, y = p
print(p, p.x, p[1], p._replace(y=9), p._asdict())
'''),

Q(4, "Moderate", "What is `collections.deque` and when do you use it?",
"""A double-ended queue with O(1) `append`/`appendleft`/`pop`/`popleft`. Use it for queues (BFS), sliding windows and "last N items" buffers via `maxlen`.""",
r'''
from collections import deque
recent = deque(maxlen=3)
for event in ["login", "view", "cart", "pay"]:
    recent.append(event)
print(recent)
q = deque([1, 2, 3]); q.rotate(1); print(q, q.popleft())
'''),

Q(4, "Moderate", "What is `Counter` and what can it do beyond counting?",
"""A dict subclass for counting hashable items. It supports `most_common`, arithmetic (`+`, `-`, `&`, `|`), `update`/`subtract`, and `total()` (3.10+). Missing keys return 0 instead of raising.""",
r'''
from collections import Counter
week1 = Counter(apples=3, pears=1)
week2 = Counter(apples=1, kiwis=4)
print(week1 + week2, (week1 + week2).total(), week1["mango"])
print(week2 - week1)
'''),

Q(4, "Moderate", "What is `OrderedDict` still useful for now that dicts are ordered?",
"""`move_to_end()` and `popitem(last=False)` make it easy to build LRU caches, and equality between two `OrderedDict`s is **order-sensitive** (plain dicts compare equal regardless of order).""",
r'''
from collections import OrderedDict
cache = OrderedDict(a=1, b=2, c=3)
cache.move_to_end("a")                 # a was just used
print(cache.popitem(last=False))       # evict least recently used
print(OrderedDict(x=1, y=2) == OrderedDict(y=2, x=1), dict(x=1, y=2) == dict(y=2, x=1))
'''),

Q(4, "Moderate", "How do list slicing assignments work?",
"""Assigning to a slice replaces that range with the items of an iterable, and the list can grow or shrink. `lst[:] = ...` replaces contents in place (all references see it). Extended slices (`lst[::2] = ...`) need the same length.""",
r'''
a = [0, 1, 2, 3, 4]
a[1:3] = ["x", "y", "z"]; print(a)
a[:] = []; print(a)
b = [0, 1, 2, 3]; b[::2] = ["E", "E"]; print(b)
'''),

Q(4, "Difficult", "How is a Python list implemented internally?",
"""A CPython list is a dynamic array of pointers to objects. When full, it over-allocates (about 12.5% extra plus a constant), so `append` is amortized O(1). This is why lists can hold mixed types and why inserting at the front is O(n).""",
r'''
import sys
lst, last = [], None
for i in range(20):
    size = sys.getsizeof(lst)
    if size != last:
        print(f"len={len(lst):2} bytes={size}")
        last = size
    lst.append(i)
'''),

Q(4, "Difficult", "How is a dict implemented internally, and what makes it ordered?",
"""Since 3.6, CPython uses a **compact dict**: a dense entries array (hash, key, value) in insertion order, plus a sparse index table of slots pointing into it. Lookups hash the key, probe the index table (open addressing), then compare. Insertion order falls out of the append-only entries array. It resizes when about 2/3 full."""),

Q(4, "Difficult", "What happens if you mutate an object used as a dict key?",
"""If the hash changes, the dict can no longer find the entry (it's stored in the old slot). That is why built-in mutable types are unhashable. A custom class whose `__hash__` depends on mutable fields causes this silent bug.""",
r'''
class Key:
    def __init__(self, v): self.v = v
    def __hash__(self): return hash(self.v)
    def __eq__(self, o): return self.v == o.v
k = Key(1)
d = {k: "value"}
k.v = 2                                   # mutate the key
print(d.get(k), d.get(Key(1)), len(d))    # lost!
'''),

Q(4, "Moderate", "How do you flatten a nested list?",
"""One level: a nested comprehension or `itertools.chain.from_iterable`. Arbitrary depth: a recursive generator.""",
r'''
from itertools import chain
print(list(chain.from_iterable([[1, 2], [3], [4, 5]])))
def flatten(x):
    for item in x:
        if isinstance(item, list): yield from flatten(item)
        else: yield item
print(list(flatten([1, [2, [3, [4]], 5]])))
'''),

Q(4, "Moderate", "How do you find common elements or differences between two lists?",
"""Convert to sets and use `&`, `-`, `^` (order and duplicates are lost). To keep order, filter one list with a set built from the other.""",
r'''
a, b = [5, 1, 3, 3, 7], [3, 7, 9]
print(set(a) & set(b), set(a) - set(b))
bs = set(b)
print([x for x in a if x in bs])
'''),

Q(4, "Moderate", "What is `bisect` used for?",
"""Binary search on a **sorted** list: `bisect_left`/`bisect_right` find insertion points in O(log n), and `insort` inserts while keeping the list sorted. Useful for grading ranges, time-series lookups and leaderboards.""",
r'''
import bisect
cutoffs, grades = [60, 70, 80, 90], "FDCBA"
print([grades[bisect.bisect(cutoffs, s)] for s in [33, 65, 80, 99]])
scores = [10, 20, 40]; bisect.insort(scores, 25); print(scores)
'''),

Q(4, "Moderate", "What is `heapq` and when would you use it?",
"""A binary min-heap on a plain list: `heappush`/`heappop` in O(log n), smallest item at index 0. Use it for priority queues, schedulers, and top-k problems (`nlargest`/`nsmallest`). For a max-heap, push negated priorities.""",
r'''
import heapq
tasks = []
for prio, name in [(3, "email"), (1, "outage"), (2, "deploy")]:
    heapq.heappush(tasks, (prio, name))
print([heapq.heappop(tasks)[1] for _ in range(3)])
print(heapq.nlargest(2, [5, 1, 9, 7]))
'''),

Q(4, "Difficult", "How would you implement an LRU cache yourself?",
"""Use an `OrderedDict`: on `get`, move the key to the end; on `put`, insert/move to end and evict from the front when over capacity. Both O(1). (In real code, `functools.lru_cache` does this for function results.)""",
r'''
from collections import OrderedDict
class LRU:
    def __init__(self, cap): self.cap, self.d = cap, OrderedDict()
    def get(self, k):
        if k not in self.d: return -1
        self.d.move_to_end(k); return self.d[k]
    def put(self, k, v):
        self.d[k] = v; self.d.move_to_end(k)
        if len(self.d) > self.cap: self.d.popitem(last=False)
c = LRU(2); c.put(1, "a"); c.put(2, "b"); c.get(1); c.put(3, "c")
print(list(c.d.items()), c.get(2))
'''),

Q(4, "Moderate", "How do you group items by a key?",
"""`defaultdict(list)` for unsorted data. `itertools.groupby` groups **consecutive** items with the same key, so sort by that key first.""",
r'''
from itertools import groupby
from operator import itemgetter
rows = [("IN", "riya"), ("US", "sam"), ("IN", "arjun"), ("UK", "amy")]
rows.sort(key=itemgetter(0))
print({k: [n for _, n in g] for k, g in groupby(rows, key=itemgetter(0))})
'''),

Q(4, "Difficult", "What is `array.array` and when is it better than a list?",
"""`array.array` stores numbers of one C type contiguously (not as pointers to Python objects), using far less memory. Use it for large homogeneous numeric data when you don't need NumPy; use NumPy for vectorized math.""",
r'''
import array, tracemalloc
n = 100_000
def measure(make):
    tracemalloc.start(); obj = make(); size = tracemalloc.get_traced_memory()[0]; tracemalloc.stop()
    return size
print(f"list : {measure(lambda: [i * 1000 for i in range(n)]) / 1e6:.2f} MB")
print(f"array: {measure(lambda: array.array('i', (i * 1000 for i in range(n)))) / 1e6:.2f} MB")
'''),

]
