EXTRAS = [

X(0, "What does this print? `def f(x, lst=[])", terms=[
    ("Default evaluated once", "The default list is created when `def` runs and stored in `f.__defaults__`."),
], pitfall="""Fixing it with `lst=lst or []`. That also replaces an empty list the caller passed on purpose; test `if lst is None`.""",
follow=[
    ("What does `f(3, [])` return after `f(1)` and `f(2)`?", "`[3]`, because an explicit list bypasses the shared default."),
    ("Does the same happen with a default `dict` or `set`?", "Yes, any mutable default is shared."),
]),

X(1, "What does `[lambda: i for i in range(3)]` return", terms=[
    ("Late binding", "Free variables are looked up when the function runs."),
], pitfall="""Assuming a generator expression fixes it. `(lambda: i for i in range(3))` consumed lazily can give 0, 1, 2 if each lambda is called before the next is created, which makes the behavior depend on consumption order.""",
follow=[
    ("What does `[lambda i=i: i for i in range(3)]` return when called?", "`[0, 1, 2]`, because each default captures the current value."),
    ("Does a nested function in a `for` loop behave the same?", "Yes, closures in loops share the loop variable."),
]),

X(2, "Why does `0.1 + 0.2 == 0.3`", terms=[
    ("ULP", "Unit in the last place: the gap between adjacent floats; `math.ulp(x)` returns it."),
], pitfall="""Using a fixed absolute tolerance like `1e-9` for all magnitudes. For large values it is too strict, for tiny values too loose; use relative tolerance.""",
follow=[
    ("What does `sum([0.1] * 10) == 1.0` give?", "False; `math.fsum([0.1] * 10) == 1.0` gives True."),
    ("What does `0.1 + 0.2 == 0.3` give with `Decimal(\"0.1\")` etc.?", "True, since those decimals are exact."),
]),

X(3, "What is `[[0] * 3] * 3`", terms=[
    ("Shared reference", "Several slots pointing to one object."),
], pitfall="""\"Fixing\" it with `[[0] * 3 for _ in range(3)]` but then creating each row with `row = [[]] * 3` for nested buckets. The same sharing bug reappears one level down.""",
follow=[
    ("How do you verify the rows are distinct?", "`len({id(r) for r in grid}) == 3`."),
    ("Does `copy.deepcopy([[0]*3]*3)` fix the sharing?", "No; deepcopy preserves sharing (via its memo), so the copy's rows are still one list."),
]),

X(4, "`t = ([1], 2)`; what happens with `t[0] += [3]`", terms=[
    ("Augmented assignment on a subscript", "Evaluates `t[0]`, calls `__iadd__`, then assigns the result back to `t[0]`."),
], pitfall="""Concluding from the `TypeError` that nothing changed. The list was already extended before the item assignment failed.""",
follow=[
    ("How do you extend the inner list without the error?", "`t[0].extend([3])` or `t[0].append(3)`; no tuple assignment happens."),
    ("How can you see the two steps?", "`dis.dis(\"t[0] += [3]\")` shows `BINARY_OP (+=)` followed by `STORE_SUBSCR`."),
]),

X(5, "Why does `a = 256; b = 256; a is b`", terms=[
    ("Constant folding / merging", "The compiler may reuse one constant object for equal literals in the same code object."),
], pitfall="""Testing this in a script and getting True for 257. Both literals in one compiled module share a constant, so the result differs between the REPL and a file.""",
follow=[
    ("What does `int(\"257\") is int(\"257\")` give?", "False in CPython, since each call creates a new object."),
    ("Why does this matter in real code?", "It does not, as long as you use `==` for values."),
]),

X(6, "What does `print(True + True + True)`", terms=[
    ("Hash equality", "`hash(True) == hash(1) == hash(1.0)`."),
], pitfall="""Using a dict keyed by mixed JSON values (1, 1.0, true). They collapse into one key, overwriting each other.""",
follow=[
    ("What does `{True: \"a\", 1: \"b\"}` print?", "`{True: 'b'}`: the first key object is kept, the last value wins."),
    ("What does `True == 1.0` give?", "True."),
]),

X(7, "Why can `x = x + [1]` and `x += [1]`", terms=[
    ("In-place vs new object", "`+=` on lists mutates; `+` builds a new list."),
], pitfall="""Using `+=` on a list parameter to build a result, which mutates the caller's list.""",
follow=[
    ("What does `x += (1,)` do if `x` is a list?", "Extends it; `+=` accepts any iterable, while `x + (1,)` raises `TypeError`."),
    ("And for a tuple `x`?", "Creates a new tuple and rebinds `x`, since tuples have no `__iadd__`."),
]),

X(8, "What happens if you modify a list while iterating", terms=[
    ("Internal index", "The list iterator keeps a position that does not adjust for removals."),
], pitfall="""Iterating over `d.items()` and deleting keys. Dicts detect the size change and raise `RuntimeError`, unlike lists, which silently skip items.""",
follow=[
    ("How do you safely remove items while iterating?", "Iterate over a copy (`for x in lst[:]`) or build a new list."),
    ("How do you iterate backwards to delete by index?", "`for i in range(len(lst) - 1, -1, -1): if bad(lst[i]): del lst[i]`."),
]),

X(9, "Why does this raise `UnboundLocalError`? `count = 0", terms=[
    ("Local by assignment", "Any assignment in a function body (including `+=`) makes the name local."),
], pitfall="""\"Fixing\" it with `global count` in library code. Shared global counters break with threads and tests; use a class or `itertools.count`.""",
follow=[
    ("What if `count` is a list and you do `count.append(1)`?", "It works; that mutates the global object without assigning the name."),
    ("What is the fix inside nested functions?", "`nonlocal count`."),
]),

X(10, "What does `print(round(2.5), round(3.5)", terms=[
    ("Round half to even", "Ties round to the nearest even integer."),
], pitfall="""Assuming `round(2.675, 2)` gives 2.68. The float is actually 2.67499..., so it gives 2.67.""",
follow=[
    ("How do you round half up for display?", "`Decimal(s).quantize(Decimal(\"1\"), rounding=ROUND_HALF_UP)`."),
    ("What does `round(-2.5)` give?", "-2."),
]),

X(11, "What is the result of `-7 // 2`", terms=[
    ("Floor division identity", "`a == (a // b) * b + a % b` always holds."),
], pitfall="""Computing \"last digit\" or \"hours on a clock\" with negative numbers and expecting C results. Python's `%` returns non-negative results for positive divisors, which is usually what you want.""",
follow=[
    ("What does `7 // -2` give?", "-4, with `7 % -2 == -1`."),
    ("How do you get truncation toward zero for ints?", "`int(a / b)` for moderate values (float precision limits it); exactly: `q = abs(a) // abs(b)`, then negate if the signs differ."),
]),

X(12, "What does `try: return 1 finally: return 2`", terms=[
    ("PEP 765", "Python 3.14 warns about `return`/`break`/`continue` in `finally`."),
], pitfall="""A `finally: return` in cleanup code that swallows a real exception, so a failure turns into a normal return value.""",
follow=[
    ("What if the `try` raises and `finally` has no return?", "The exception propagates after `finally` runs."),
    ("What does `break` in `finally` inside a loop do to an exception?", "Discards it, just like `return`."),
]),

X(13, "Is `a == b` for two lists", terms=[
    ("Structural equality", "Comparing contents element by element."),
], pitfall="""Checking `if result is []:`. It is always False because a new empty list is a new object; use `if not result:` or `== []`.""",
follow=[
    ("What does `[] is []` give?", "False."),
    ("And `() is ()`?", "True in CPython, since the empty tuple is a singleton (an implementation detail)."),
]),

X(14, "What does `print('a' 'b')`", terms=[
    ("Implicit concatenation", "Adjacent string literals are joined at compile time."),
], pitfall="""A missing comma in a list of strings: `[\"a\", \"b\" \"c\"]` gives two items, `\"a\"` and `\"bc\"`. Linters (Ruff ISC rules) flag it.""",
follow=[
    ("What does `return 1,` return?", "The tuple `(1,)`."),
    ("Does implicit concatenation work with f-strings?", "Yes, `f\"{a}\" \"b\"` is fine."),
]),

X(15, "What does `bool('False')`", terms=[
    ("Truthiness of strings", "Only the empty string is falsy."),
], pitfall="""Parsing boolean environment variables with `bool(os.environ[\"DEBUG\"])`. Any non-empty value, including \"0\" and \"false\", is True; compare against an allowed set.""",
follow=[
    ("What does `bool(\" \")` give?", "True, since a space is a non-empty string."),
    ("How do you parse \"yes/no\" safely?", "`value.strip().lower() in {\"1\", \"true\", \"yes\", \"on\"}`."),
]),

X(16, "Why does `a = []; b = a; b.append(1)`", terms=[
    ("Aliasing", "Two names for one object."),
], pitfall="""Returning an internal list from a class (`return self._items`). Callers can mutate your internal state; return a copy or a tuple.""",
follow=[
    ("Does `b = a[:]` copy nested lists?", "No, it is a shallow copy."),
    ("How do you check whether two names alias?", "`a is b`."),
]),

X(17, "Why doesn't a shallow copy protect nested data", terms=[
    ("Shallow copy", "New container, same element objects."),
], pitfall="""Copying a config dict with `.copy()` and then modifying a nested section for a test. The original config changes too.""",
follow=[
    ("What is cheaper than deepcopy for JSON-like data?", "`json.loads(json.dumps(d))` or a hand-written copy; measure, since deepcopy is slow."),
    ("How do immutable structures avoid the issue?", "If nested values are tuples or frozen dataclasses, sharing them is safe."),
]),

X(18, "What does `dict.fromkeys(['a', 'b'], [])`", terms=[
    ("Single default object", "`fromkeys` stores the very same value object under every key."),
], pitfall="""The same happens with `defaultdict(lambda: shared_list)`. The factory must create a new object each call.""",
follow=[
    ("What is the correct way?", "`{k: [] for k in keys}` or `defaultdict(list)`."),
    ("Is `dict.fromkeys(keys, 0)` safe?", "Yes, ints are immutable."),
]),

X(19, "Why is `is not` different from `not ... is`", terms=[
    ("Operator precedence", "`not` binds looser than comparisons."),
], pitfall="""Writing `if not x in items` and misreading it. It works (`not (x in items)`), but `if x not in items` is the idiomatic, clearer form.""",
follow=[
    ("What does `not 1 == 2` evaluate to?", "True, as `not (1 == 2)`."),
    ("What does `x is (not None)` mean?", "`x is True`, since `not None` is True; a common mistake when people mean `x is not None`."),
]),

X(20, "What is printed? `x = 10` then `def f(): print(x); x = 5`", terms=[
    ("Compile-time scope decision", "Locals are determined when the function is compiled, not as lines run."),
], pitfall="""Adding a local assignment far down in a long function that shadows a global used earlier. Code that worked starts raising `UnboundLocalError`; linters catch this.""",
follow=[
    ("What if `x = 5` is inside an `if False:` block?", "`x` is still local, and `print(x)` still raises."),
    ("How do you read the global anyway?", "`globals()[\"x\"]`, but renaming the local is better."),
]),

X(21, "Why does `sorted(['b', 'A', 'c'])` put 'A' first", terms=[
    ("Code-point order", "Default string ordering by Unicode code point values."),
    ("Locale-aware sorting", "`locale.strxfrm` or PyICU for language-correct order."),
], pitfall="""Sorting names with `key=str.lower` for international users. Accented letters and other scripts still sort by code point; use `casefold` or locale-aware collation.""",
follow=[
    ("How do you sort case-insensitively but stably break ties?", "`key=lambda s: (s.casefold(), s)`."),
    ("How do you sort \"file2\" before \"file10\"?", "Natural sort: split digits with `re.split(r\"(\\d+)\", s)` and convert them to ints in the key."),
]),

X(22, "What does `sorted` do with mixed types", terms=[
    ("Total ordering", "Every pair of values is comparable; mixed-type Python values are not."),
], pitfall="""Sorting data with `None` values mixed in (e.g. missing dates). It raises `TypeError`; use a key like `(x is None, x)` to put `None` last.""",
follow=[
    ("How do you sort mixed types deterministically anyway?", "Key by `(type(x).__name__, x)`, or convert everything to strings."),
    ("What does `max([1, \"a\"])` do?", "Also raises `TypeError`."),
]),

X(23, "What does `print(1 < 2 < 3, 3 > 2 > 1", terms=[
    ("Comparison chaining", "`a op b op c` means `a op b and b op c`."),
], pitfall="""Porting `(a < b) < c` from another language. In Python `a < b < c` chains, while `(a < b) < c` compares a bool with `c`.""",
follow=[
    ("What does `(1 < 2) < 3` give?", "True, because `True < 3` is `1 < 3`."),
    ("What does `1 == 1 in [1]` give?", "True: `(1 == 1) and (1 in [1])`."),
]),

X(24, "Why is `nan` in a list found by `in`", terms=[
    ("Identity shortcut", "Containers check `x is item` before `x == item`."),
], pitfall="""Counting NaNs with `lst.count(float(\"nan\"))`. A new NaN object is never identical or equal, so the count is 0; use `sum(math.isnan(v) for v in lst)`.""",
follow=[
    ("What does `float(\"nan\") in [float(\"nan\")]` give?", "False, because they are different objects."),
    ("How does pandas treat NaN?", "It uses NaN (or `pd.NA`) as missing; use `isna()` rather than equality."),
]),

X(25, "What does `len({1, 1.0, True})` return", terms=[
    ("Set deduplication", "Items that are equal and have the same hash are stored once."),
], pitfall="""Deduplicating mixed numeric data read from different sources. `1`, `1.0` and `True` collapse into one element, which may be wrong for your domain.""",
follow=[
    ("Which object is kept?", "The first inserted: `{1, 1.0, True}` prints `{1}`."),
    ("What about `{0, 0.0, False, -0.0}`?", "Also one element, `{0}`."),
]),

X(26, "Why does a generator produce nothing the second time", terms=[
    ("One-shot iterator", "Consumed items cannot be read again."),
], pitfall="""Passing a generator to `len`, `sorted` for a check, and then iterating it. The check consumed it; the loop then sees nothing.""",
follow=[
    ("How do you iterate twice cheaply?", "Materialize to a list, or recreate the generator by calling the generator function again."),
    ("Is `range` affected?", "No, `range` is a re-iterable sequence."),
]),

X(27, "What does `print(type(()), type((1))", terms=[
    ("Tuple display", "Commas create tuples; parentheses only group, except for the empty tuple `()`."),
], pitfall="""A stray trailing comma: `x = compute(),` makes `x` a one-element tuple, which later fails with confusing errors.""",
follow=[
    ("What is `type((1,),)`?", "`tuple`; the trailing comma in a call is just argument syntax."),
    ("How do you write a one-element tuple in a return?", "`return (value,)` or `return value,`."),
]),

X(28, "Class attribute trap", terms=[
    ("Class attribute", "Defined in the class body and shared by all instances."),
], pitfall="""The dataclass version: `items: list = []` raises `ValueError` at class creation, which is Python protecting you; use `field(default_factory=list)`.""",
follow=[
    ("How do you detect the sharing?", "`a.items is b.items` returns True."),
    ("Is a class-level constant like `MAX = 10` fine?", "Yes, immutable class attributes are safe to share."),
]),

X(29, "What does `\"abc\" * -1`", terms=[
    ("Lenient slicing", "Out-of-range slice bounds are clipped, never raising `IndexError`."),
], pitfall="""Relying on slices to detect short input. `data[5:10]` silently returns fewer items; check `len` explicitly if you need exactly 5.""",
follow=[
    ("What does `[1, 2][5]` do?", "Raises `IndexError`; only indexing is strict, slicing is not."),
    ("What does `[0] * 2.0` do?", "Raises `TypeError`; the repeat count must be an int."),
]),

X(30, "Does `except Exception` catch `KeyboardInterrupt`", terms=[
    ("`BaseException`-only exceptions", "`KeyboardInterrupt`, `SystemExit`, `GeneratorExit`, and `BaseExceptionGroup` of those."),
], pitfall="""Catching `BaseException` in a retry loop. Ctrl+C and `sys.exit()` are then retried instead of stopping the program.""",
follow=[
    ("Is `asyncio.CancelledError` an `Exception`?", "No, since 3.8 it inherits from `BaseException`, so `except Exception` does not swallow cancellation."),
    ("How do you run cleanup on Ctrl+C?", "Use `try/finally` or a context manager; they run for `KeyboardInterrupt` too."),
]),

X(31, "Why can't you use a list as a dict key", terms=[
    ("Hashable", "Has a hash that never changes and a consistent `__eq__`."),
], pitfall="""Using a tuple of lists as a key after \"checking it is a tuple\". It still raises `TypeError: unhashable type: 'list'`.""",
follow=[
    ("How do you key a dict by a set of items?", "Use `frozenset(items)`."),
    ("How do you key by a dict?", "`frozenset(d.items())` if the values are hashable, or a sorted tuple of items."),
]),

X(32, "What's the output of `print(\"%s\" % (1, 2))`", terms=[
    ("`%` argument tuple", "A tuple on the right side is treated as the full argument list."),
], pitfall="""Formatting a variable that might be a tuple with `\"%s\" % value`. It fails or formats only part; wrap it: `\"%s\" % (value,)`, or use f-strings.""",
follow=[
    ("What does `\"%s\" % [1, 2]` print?", "`[1, 2]`; lists are not unpacked."),
    ("Why does logging use `%` style then?", "Deferred formatting; pass arguments separately (`log.info(\"%s\", value)`), which avoids this tuple trap."),
]),

X(33, "Why does `x = x.sort()` leave `x` as None", terms=[
    ("Command-query separation", "Methods that mutate return `None` to signal they changed the object in place."),
], pitfall="""Chaining in-place methods: `lst.append(1).append(2)` raises `AttributeError: 'NoneType' object has no attribute 'append'`.""",
follow=[
    ("Which similar functions return a new object?", "`sorted()`, `reversed()` (an iterator), and string methods, since strings are immutable."),
    ("Does `random.shuffle` return the list?", "No, it returns `None`; use `random.sample(lst, len(lst))` for a shuffled copy."),
]),

X(34, "Does `is` work for comparing strings", terms=[
    ("Interning", "Reusing one object for equal strings."),
], pitfall="""Code that compares user input with `is` passing tests with literals and failing in production with strings built at runtime (read from files or networks).""",
follow=[
    ("What warning does Python give?", "`SyntaxWarning: \"is\" with 'str' literal. Did you mean \"==\"?`"),
    ("When is `is` correct with strings?", "Only when checking for a specific sentinel object you created yourself."),
]),

X(35, "What does `print(any([]), all([]))`", terms=[
    ("Vacuous truth", "A statement about all members of an empty set is true."),
], pitfall="""Validating \"all items pass\" with `all(...)` on data that might be empty. An empty input passes; also check that there is at least one item if required.""",
follow=[
    ("What does `all([[]])` return?", "False, because the single item, an empty list, is falsy."),
    ("What does `any([0, \"\", None])` return?", "False, since every item is falsy."),
]),

X(36, "What is the output of `print(list(zip([1, 2, 3], 'ab')))`", terms=[
    ("`strict=True`", "Makes `zip` raise `ValueError` when inputs differ in length (3.10+)."),
], pitfall="""Zipping keys and values from two sources to build a dict. A length mismatch silently drops data; use `strict=True`.""",
follow=[
    ("How do you keep the extra items?", "`itertools.zip_longest([1, 2, 3], \"ab\", fillvalue=None)`."),
    ("What does `zip()` with no arguments return?", "An empty iterator."),
]),

X(37, "Why does `json.loads(json.dumps({1: (2, 3)}))`", terms=[
    ("JSON data model", "Objects with string keys, arrays, strings, numbers, booleans and null."),
], pitfall="""Caching Python objects as JSON and expecting the same types back. Int keys, tuples, sets, datetimes and Decimals all change or fail; use a schema-aware serializer (pydantic, msgspec) to restore types.""",
follow=[
    ("What does `json.dumps({(1, 2): 3})` do?", "Raises `TypeError`; tuple keys are not allowed (use `skipkeys=True` to drop them)."),
    ("What does `json.dumps(float(\"nan\"))` produce?", "`NaN`, which is not valid JSON; pass `allow_nan=False` to raise instead."),
]),

X(38, "What does `datetime.now()` get wrong", terms=[
    ("Naive datetime", "No time zone attached, so its meaning depends on context."),
    ("Monotonic clock", "A clock that never goes backward; use it for durations."),
], pitfall="""Measuring durations with `datetime.now()` differences. NTP adjustments or DST changes can make them negative or wrong; use `time.monotonic()`.""",
follow=[
    ("How do you store timestamps in databases?", "As UTC in a timezone-aware column (e.g. `timestamptz`), converting to local time only for display."),
    ("How do you compare an aware and a naive datetime?", "You cannot: ordering comparisons raise `TypeError`, and `==` returns False, so make both aware first."),
]),
]
