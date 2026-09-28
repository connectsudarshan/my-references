EXTRAS = [

X(0, "Are strings mutable", terms=[
    ("Immutable string", "A `str` object never changes after creation; every \"modifying\" method returns a new string."),
    ("`io.StringIO`", "An in-memory text buffer you can write to piece by piece, like a file."),
], pitfall="""Expecting `s.replace(\"a\", \"b\")` or `s.strip()` to change `s`. The result must be assigned: `s = s.strip()`.""",
follow=[
    ("How do you change one character of a string?", "Build a new one: `s[:i] + c + s[i+1:]`, or convert to a list, edit, and `\"\".join()` it."),
    ("Why are strings immutable?", "It makes them hashable (usable as dict keys), safe to share between threads and callers, and allows caching of their hash."),
]),

X(1, "How does string slicing work", terms=[
    ("Half-open interval", "`[start, stop)`: includes start, excludes stop, so `len(s[a:b]) == b - a` when both are in range."),
    ("`slice` object", "What `a:b:c` creates internally; you can name one: `HEADER = slice(0, 4)` then `data[HEADER]`."),
], pitfall="""Using `s[::-1]` on user-visible text containing combining characters or emoji sequences. It reverses code points, which can split graphemes and produce garbled output.""",
follow=[
    ("What does `s[5:2]` return?", "An empty string; slices with start past stop (and a positive step) are empty, never an error."),
    ("Does slicing copy?", "For `str`, `list`, `tuple` and `bytes`, yes, it creates a new object. `memoryview` and NumPy slices are views that do not copy."),
]),

X(2, "What are the most-used string methods", terms=[
    ("`removeprefix` / `removesuffix`", "3.9+ methods that remove an exact prefix or suffix once, unlike `strip`, which removes a set of characters."),
], pitfall="""Using `s.strip(\"abc\")` or `s.lstrip(\"https://\")` to remove a word. The argument is a set of characters, so `\"https://sample.com\".lstrip(\"https://\")` also eats the leading \"s\" of \"sample\". Use `removeprefix`.""",
follow=[
    ("What is the difference between `split()` and `split(\" \")`?", "`split()` splits on runs of any whitespace and drops empty strings; `split(\" \")` splits on each single space and keeps empty strings."),
    ("How do you split only once from the right?", "`s.rsplit(sep, 1)`, or `s.rpartition(sep)` which always returns a 3-tuple."),
]),

X(3, "`find()` vs `index()`", terms=[
    ("`rfind` / `rindex`", "The same searches starting from the right, returning the highest index."),
], pitfall="""Writing `if s.find(x):`. `find` returns 0 for a match at the start (falsy) and -1 (truthy) for no match, so the test is backwards. Use `if x in s:`.""",
follow=[
    ("Do lists have `find()`?", "No. Lists have `index()` (raises `ValueError`) and `count()`, but no `find()`."),
    ("How do you find all occurrences?", "Loop with `find(x, start)`, or use `[m.start() for m in re.finditer(re.escape(x), s)]`."),
]),

X(4, "Why is `''.join(list)`", terms=[
    ("Quadratic behavior", "Total work grows with the square of the input size, because each step copies everything built so far."),
], pitfall="""Passing non-strings to `join`: `\",\".join([1, 2])` raises `TypeError`. Convert first: `\",\".join(map(str, items))`.""",
follow=[
    ("Why does `s += x` sometimes appear fast in CPython?", "If `s` has no other references, CPython can resize it in place. This is an implementation detail and breaks as soon as another reference exists."),
    ("Is `join` better with a list or a generator?", "A list is slightly faster; `join` materializes a generator into a list anyway because it needs two passes."),
]),

X(5, "What are the ways to format strings", terms=[
    ("`string.Template`", "Simple `$name` substitution, suitable for user-provided templates because it cannot evaluate expressions or access attributes."),
    ("t-strings", "Template string literals (`t\"...\"`, Python 3.14, PEP 750) that produce a `Template` object for safe, custom processing instead of a `str`."),
], pitfall="""Passing a user-controlled format string to `str.format`. `\"{0.__class__.__init__.__globals__}\".format(obj)` can leak internals; use `Template` for untrusted templates.""",
follow=[
    ("Why do logging calls use `%`-style arguments instead of f-strings?", "`log.debug(\"x=%s\", x)` defers formatting until the record is actually emitted, so disabled levels cost almost nothing, and aggregators can group by the template."),
    ("How do you put a literal brace in an f-string?", "Double it: `f\"{{{x}}}\"` prints the value of `x` inside braces."),
]),

X(6, "What are raw strings", terms=[
    ("Escape sequence", "A backslash combination such as `\\n` or `\\t` that stands for a special character."),
], pitfall="""Writing a regex without `r` and getting a `SyntaxWarning: invalid escape sequence` (3.12+), or silently wrong patterns like `\"\\b\"`, which is a backspace character, not a word boundary.""",
follow=[
    ("Why can a raw string not end with a single backslash?", "The backslash still escapes the closing quote for tokenizing, so `r\"C:\\\"` is unterminated. Use `\"C:\\\\\"` or `pathlib`."),
    ("Are raw strings a different type?", "No. `r\"...\"` only changes how the literal is parsed; the result is an ordinary `str`."),
]),

X(7, "What is the difference between `str()` and `repr()`", terms=[
    ("`__repr__`", "Developer-facing representation; used by the REPL, debuggers, containers and `!r`."),
    ("`__str__`", "User-facing text; falls back to `__repr__` if not defined."),
], pitfall="""Defining only `__str__` on a class. Lists and log lines containing the object then show the unhelpful default `<Foo object at 0x...>`, because containers use `repr` for their items.""",
follow=[
    ("Which should you define if you only define one?", "`__repr__`; `str()` falls back to it."),
    ("What does `reprlib.repr` do?", "Produces a size-limited repr, useful for logging huge containers."),
]),

X(8, "How does Python handle Unicode", terms=[
    ("Code point", "A number identifying one Unicode character, written like U+00E9."),
    ("UTF-8", "Variable-length encoding using 1-4 bytes per code point; ASCII-compatible and the de facto standard."),
], pitfall="""Opening files without `encoding=`. The default depends on the OS locale (often cp1252 on Windows), so the same program reads files differently on different machines.""",
follow=[
    ("What is the \"Unicode sandwich\"?", "Decode bytes to `str` at the input boundary, process only `str`, and encode back to bytes at the output boundary."),
    ("What is a BOM and how do you handle it?", "A byte order mark at the start of a file; read UTF-8 files that may contain one with `encoding=\"utf-8-sig\"`."),
]),

X(9, "Why can `len()` of a string differ", terms=[
    ("Grapheme cluster", "What a user perceives as one character, possibly several code points."),
    ("Normalization (NFC/NFD)", "Canonical composed or decomposed forms, applied with `unicodedata.normalize`."),
], pitfall="""Truncating user text with `s[:N]` for a UI or database column. It can cut an emoji or accent sequence in half; truncate by graphemes (third-party `grapheme`/`regex` modules) or by encoded byte length where storage requires it.""",
follow=[
    ("Why can two visually identical strings compare unequal?", "One may use a precomposed character (é, U+00E9) and the other `e` + combining accent (U+0301). Normalize both to NFC before comparing."),
    ("How do you count bytes for a storage limit?", "`len(s.encode(\"utf-8\"))`."),
]),

X(10, "`lower()` vs `casefold()`", terms=[
    ("Case folding", "A Unicode-defined mapping designed for caseless matching, more complete than lowercasing."),
], pitfall="""Using `lower()` for case-insensitive username or email-local-part comparisons with international text. Use `casefold()` together with NFKC normalization.""",
follow=[
    ("Is `casefold()` suitable for display?", "No, it is only for comparison; \"ß\" becomes \"ss\", which changes the displayed word."),
    ("What does the Turkish dotted/dotless i problem show?", "Case mapping can be locale-dependent; Python's `lower`/`casefold` are locale-independent, so Turkish needs special handling."),
]),

X(11, "How do you check if a string is a palindrome", terms=[
    ("Two-pointer technique", "Compare characters from both ends moving inward; O(1) extra memory."),
], pitfall="""Forgetting normalization, so \"A man, a plan, a canal: Panama\" fails because of case, spaces and punctuation.""",
follow=[
    ("How do you check it without building a reversed copy?", "Two pointers `i`, `j` that skip non-alphanumeric characters and compare `casefold()`ed characters."),
    ("How would you find the longest palindromic substring?", "Expand around each center (O(n²)); Manacher's algorithm gives O(n)."),
]),

X(12, "How do you count character or word frequencies", terms=[
    ("`Counter.most_common`", "Returns `(item, count)` pairs sorted by count descending; ties keep first-seen order."),
], pitfall="""Counting words with `text.split()` and getting separate counts for \"Word\", \"word,\" and \"word.\". Normalize case and strip punctuation, for example `re.findall(r\"\\w+\", text.lower())`.""",
follow=[
    ("How do you get the least common items?", "`c.most_common()[:-n-1:-1]`, or `heapq.nsmallest(n, c.items(), key=lambda kv: kv[1])`."),
    ("Can you count items in a huge file without loading it?", "Yes, update a `Counter` line by line: `c.update(line.split())`."),
]),

X(13, "What are the most useful `re` functions", terms=[
    ("`re.compile`", "Pre-compiles a pattern into a reusable object; the module also caches recently used patterns."),
    ("Match object", "Result of a successful match, with `group()`, `groups()`, `groupdict()`, `start()`, `end()` and `span()`."),
], pitfall="""Using `re.match` to validate a whole string. It anchors only at the start, so `re.match(r\"\\d+\", \"123abc\")` succeeds; use `re.fullmatch`.""",
follow=[
    ("What do named groups look like?", "`(?P<year>\\d{4})`, read with `m[\"year\"]` or `m.group(\"year\")`."),
    ("Why might `findall` return tuples?", "If the pattern has more than one group, each match is a tuple of groups; use `(?:...)` for non-capturing groups."),
]),

X(14, "What is the difference between greedy", terms=[
    ("Backtracking", "The regex engine undoing earlier choices to try alternatives."),
    ("Catastrophic backtracking (ReDoS)", "Exponential matching time caused by nested quantifiers such as `(a+)+$`."),
], pitfall="""Parsing HTML or nested structures with `.*?` regexes. It works on examples and fails on real input; use a parser.""",
follow=[
    ("How do possessive quantifiers and atomic groups help?", "`*+`, `++` and `(?>...)` (supported by `re` since 3.11) never give back characters, which prevents catastrophic backtracking."),
    ("What does `re.DOTALL` change?", "It makes `.` also match newlines."),
]),

X(15, "How do you split a string on multiple delimiters", terms=[
    ("Character class", "`[,;\\s]` matches any single character in the set."),
], pitfall="""Using a capturing group in `re.split`, as in `re.split(r\"(,|;)\", s)`. The delimiters are then included in the result list; use `(?:...)` if you do not want them.""",
follow=[
    ("How do you drop empty strings from the result?", "`[p for p in re.split(pattern, s) if p]`, or use `re.findall` for the tokens instead."),
    ("How do you split CSV correctly?", "Use the `csv` module; quoted fields may contain the delimiter."),
]),

X(16, "How do you reverse the words", terms=[
    ("`reversed()`", "Returns a reverse iterator without copying the list."),
], pitfall="""Using `s.split(\" \")` and then being surprised by empty strings from double spaces. `split()` with no argument handles runs of whitespace.""",
follow=[
    ("How do you reverse words in place in a character array?", "Reverse the whole array, then reverse each word; O(n) time, O(1) space."),
    ("How do you preserve the original spacing?", "Split with `re.split(r\"(\\s+)\", s)` to keep separators, then reverse only the word tokens."),
]),

X(17, "How do you check if two strings are anagrams", terms=[
    ("Multiset", "A set that allows repeated items; `Counter` is Python's multiset."),
], pitfall="""Comparing `set(a) == set(b)`. It ignores counts, so \"aab\" and \"abb\" wrongly look like anagrams.""",
follow=[
    ("How do you group a list of words into anagram groups?", "`defaultdict(list)` keyed by `\"\".join(sorted(w))` (or a tuple of 26 counts)."),
    ("What is the fastest check for lowercase ASCII only?", "A fixed 26-slot count array, incrementing for one string and decrementing for the other."),
]),

X(18, "What is `str.translate`", terms=[
    ("Translation table", "A dict mapping code points (ints) to strings, code points or `None`; build it with `str.maketrans`."),
], pitfall="""Passing a table keyed by characters (`{\"a\": \"b\"}`) directly to `translate`. It needs integer keys; use `str.maketrans(d)` to convert.""",
follow=[
    ("How do you delete all punctuation?", "`s.translate(str.maketrans(\"\", \"\", string.punctuation))`."),
    ("Does `translate` work on `bytes`?", "Yes, `bytes.translate` takes a 256-byte table from `bytes.maketrans` and an optional `delete` argument."),
]),

X(19, "How do you find the first non-repeating character", terms=[
    ("Two-pass counting", "One pass to count, a second pass in original order to find the answer."),
], pitfall="""Iterating over the `Counter` instead of the string in the second pass. It works in 3.7+ because of insertion order, but iterating the string states the intent and does not rely on it.""",
follow=[
    ("How would you do it for a stream of characters?", "Keep counts plus an `OrderedDict` (or deque) of candidates; drop a candidate from the front when its count exceeds 1."),
    ("What is the complexity?", "O(n) time and O(k) space, where k is the alphabet size."),
]),

X(20, "How do you check if a string contains only digits", terms=[
    ("`isdecimal` / `isdigit` / `isnumeric`", "Increasingly broad: decimal digits only; plus superscripts and similar digits; plus numeric characters like \"½\" and Roman numerals."),
], pitfall="""Validating numbers with `isdigit()` and then calling `int()`. \"²\" passes `isdigit()` but `int(\"²\")` raises `ValueError`. Use `try: int(s)` or `s.isascii() and s.isdecimal()`.""",
follow=[
    ("How do you validate a signed integer string?", "`re.fullmatch(r\"[+-]?\\d+\", s, re.ASCII)`, or just `try: int(s) except ValueError`."),
    ("Does `int()` accept Unicode digits?", "Yes, `int(\"٣\")` (Arabic-Indic three) returns 3, since it accepts any Unicode decimal digit."),
]),

X(21, "What is the difference between a list and a tuple", terms=[
    ("Heterogeneous record", "A fixed-shape group of different-typed fields, the typical use of a tuple (`(name, age)`)."),
], pitfall="""Writing `t = (1)` and expecting a tuple. It is just the int 1; the comma makes a tuple: `(1,)`.""",
follow=[
    ("Why is a tuple slightly faster to create?", "Constant tuples are built once at compile time and reused; tuples also have no over-allocation."),
    ("When must you use a tuple?", "When you need a hashable sequence: dict keys, set members, `functools.cache` arguments."),
]),

X(22, "`append()` vs `extend()`", terms=[
    ("Amortized O(1)", "Individual appends are occasionally slow (resize) but average constant time."),
], pitfall="""`lst.extend(\"abc\")` adds three characters, and `lst.append([1, 2])` adds one nested list. Pick the method by whether you want one item or many.""",
follow=[
    ("What is `lst += \"ab\"`?", "Equivalent to `extend`, so it adds `\"a\"` and `\"b\"`; `lst = lst + \"ab\"` raises `TypeError` instead."),
    ("What does `insert` do with an index beyond the end?", "It appends; out-of-range indexes are clamped, not errors."),
]),

X(23, "`remove()` vs `pop()`", terms=[
    ("`pop` from a dict", "`d.pop(k, default)` removes and returns a value, with an optional default instead of `KeyError`."),
], pitfall="""Removing items from a list while iterating over it (`for x in lst: if bad(x): lst.remove(x)`). It skips elements; build a new list with a comprehension.""",
follow=[
    ("How do you remove all occurrences of a value?", "`lst[:] = [x for x in lst if x != v]` (in place) or a new list."),
    ("What is the complexity of `pop(0)`?", "O(n), because everything shifts; use `collections.deque.popleft()` for O(1)."),
]),

X(24, "`sort()` vs `sorted()`", terms=[
    ("Stable sort", "Equal elements keep their original relative order, which enables multi-pass sorting by secondary then primary key."),
    ("Timsort / Powersort", "CPython's adaptive merge sort; since 3.11 it uses the Powersort merge policy. It is O(n) on already sorted runs."),
], pitfall="""Writing `lst = lst.sort()`. `sort()` returns `None`, so `lst` becomes `None`.""",
follow=[
    ("How do you sort by several keys, one descending?", "Use a tuple key with negation for numbers (`key=lambda r: (-r.score, r.name)`), or sort twice relying on stability."),
    ("What replaced `cmp=` in Python 3?", "`key=functools.cmp_to_key(cmp_func)`."),
]),

X(25, "What is the time complexity of common list operations", terms=[
    ("Big-O", "How cost grows with input size, ignoring constant factors."),
], pitfall="""Hiding O(n) operations in a loop: `x in lst`, `lst.index(x)`, `lst.pop(0)` or `lst.insert(0, x)` inside a loop makes the whole thing O(n²).""",
follow=[
    ("What is the complexity of slicing `lst[a:b]`?", "O(b - a), since it copies that many references."),
    ("What is the complexity of `lst.sort()`?", "O(n log n) worst case, O(n) for already sorted or reverse-sorted input."),
]),

X(26, "How do you remove duplicates from a list", terms=[
    ("`dict.fromkeys`", "Builds a dict from an iterable of keys, all mapped to one value (default `None`)."),
], pitfall="""Deduplicating unhashable items such as dicts or lists. `dict.fromkeys` raises `TypeError`; key by a hashable projection (`tuple(sorted(d.items()))`) or fall back to an O(n²) scan.""",
follow=[
    ("How do you deduplicate by a key while keeping the first occurrence?", "Track seen keys in a set: `seen = set(); [x for x in xs if not (k := key(x)) in seen and not seen.add(k)]`, or a plain loop for readability."),
    ("How do you keep the last occurrence instead?", "`list({key(x): x for x in xs}.values())` keeps the last value, in the position where its key first appeared."),
]),

X(27, "How do dictionaries work", terms=[
    ("Hash table", "An array indexed by (a function of) each key's hash, giving average O(1) access."),
    ("Insertion order", "Guaranteed by the language since 3.7: iteration follows the order keys were first added."),
], pitfall="""Changing a dict's size while iterating over it raises `RuntimeError: dictionary changed size during iteration`. Iterate over `list(d)` if you must delete.""",
follow=[
    ("Does updating an existing key change its position?", "No; only deleting and re-inserting moves it to the end."),
    ("What is the worst case for dict lookups?", "O(n), if many keys collide; CPython randomizes `str`/`bytes` hashes per process to make deliberate collisions hard."),
]),

X(28, "`dict[key]` vs `dict.get(key)`", terms=[
    ("`__missing__`", "Hook a dict subclass can define; called by `d[k]` when the key is absent. `defaultdict` and `Counter` use it."),
], pitfall="""`d.setdefault(k, expensive())` evaluates `expensive()` every time, even when the key exists. Use `defaultdict` or an explicit `if k not in d`.""",
follow=[
    ("Does `defaultdict.get(k)` create the key?", "No. Only `d[k]` triggers `default_factory`; `get` and `in` do not insert."),
    ("How do you build a nested auto-vivifying dict?", "`tree = lambda: defaultdict(tree)`; then `t = tree(); t[\"a\"][\"b\"] = 1`."),
]),

X(29, "How do you merge two dictionaries", terms=[
    ("`ChainMap`", "A view that searches several dicts in order without copying them; writes go to the first mapping."),
], pitfall="""Expecting `a | b` or `update` to merge nested dicts. They replace the whole inner value; write a recursive merge for nested configs.""",
follow=[
    ("Does `{**a, **b}` work with non-string keys?", "Yes, in a dict display it accepts any hashable keys; only `dict(**b)` as a function call requires string keys."),
    ("What is the difference between `a | b` and `a.update(b)`?", "`|` returns a new dict; `update` mutates `a` and returns `None`."),
]),

X(30, "How do you sort a dictionary by value", terms=[
    ("`operator.itemgetter`", "Fast, picklable alternative to `lambda kv: kv[1]`."),
], pitfall="""Expecting the dict to stay sorted after new insertions. It keeps insertion order, not sorted order; re-sort or use a sorted container.""",
follow=[
    ("How do you get only the top 3 entries?", "`heapq.nlargest(3, d.items(), key=itemgetter(1))` or `Counter(d).most_common(3)`."),
    ("Is there a sorted dict in the standard library?", "No; use the third-party `sortedcontainers.SortedDict`, or keep a separate sorted key list with `bisect`."),
]),

X(31, "What are dictionary views", terms=[
    ("Live view", "An object reflecting the current state of the dict, not a copy."),
], pitfall="""Iterating `d.keys()` and deleting keys inside the loop. Snapshot first: `for k in list(d):`.""",
follow=[
    ("Why does `values()` not support set operations?", "Values need not be hashable or unique, so set semantics are not defined for them."),
    ("How do you find keys common to two dicts?", "`a.keys() & b.keys()`."),
]),

X(32, "What are sets and their operations", terms=[
    ("Symmetric difference", "Items in exactly one of the two sets: `a ^ b`."),
    ("Subset / superset", "`a <= b` / `a >= b`; `<` and `>` are proper subset/superset."),
], pitfall="""Creating an empty set with `{}`. That is an empty dict; use `set()`.""",
follow=[
    ("What is the difference between `a | b` and `a.union(b)`?", "The operator requires both sides to be sets; the method accepts any iterable."),
    ("Is set iteration order predictable?", "No; it depends on hashes and insertion history, and string hashes change between runs."),
]),

X(33, "Why is `x in set` much faster", terms=[
    ("Average vs worst case", "Hash lookups are O(1) on average, degrading only with pathological collisions."),
], pitfall="""Converting a list to a set inside a loop (`if x in set(big_list)`). Building the set is O(n) each time, which is worse than the list scan; build it once outside the loop.""",
follow=[
    ("When can a list membership test be faster?", "For very small lists (a few items) the linear scan can beat hashing, and when elements are unhashable a set is impossible."),
    ("How do you speed up `x in` for a sorted list?", "Binary search with `bisect`: O(log n)."),
]),

X(34, "What is a `namedtuple`", terms=[
    ("`_replace`", "Returns a copy with some fields changed, since namedtuples are immutable."),
    ("`typing.NamedTuple`", "Class syntax for namedtuples with type annotations and defaults."),
], pitfall="""Namedtuples compare equal to plain tuples and to other namedtuples with the same values: `Point(1, 2) == Color(1, 2) == (1, 2)`. Use a dataclass if type-aware equality matters.""",
follow=[
    ("How do you convert one to a dict?", "`p._asdict()`."),
    ("When is a dataclass better?", "When you need mutability, methods with defaults, validation in `__post_init__`, or equality that respects the type."),
]),

X(35, "What is `collections.deque`", terms=[
    ("`maxlen`", "Bounded deque; adding past the limit silently discards from the opposite end."),
    ("`rotate(n)`", "Rotates items n steps to the right (negative for left)."),
], pitfall="""Indexing into the middle of a large deque (`dq[i]`) in a loop. Middle access is O(n); deques are for the ends.""",
follow=[
    ("Is `deque` thread-safe?", "`append`, `appendleft`, `pop` and `popleft` are atomic in CPython, but for producer/consumer with blocking use `queue.Queue`."),
    ("How do you keep the last 5 lines of a file?", "`deque(open(path), maxlen=5)`."),
]),

X(36, "What is `Counter`", terms=[
    ("Multiset arithmetic", "`+` adds counts, `-` subtracts and drops non-positive counts, `&` is min, `|` is max."),
], pitfall="""Expecting `c1 - c2` to keep negative counts. It drops zero and negative results; use `c1.subtract(c2)` to keep them.""",
follow=[
    ("What does `c[\"missing\"]` return?", "0, without inserting the key."),
    ("How do you remove zero and negative counts?", "`+c` (unary plus) returns a new Counter with only positive counts."),
]),

X(37, "What is `OrderedDict` still useful for", terms=[
    ("`move_to_end(key, last=True)`", "Moves a key to either end in O(1)."),
], pitfall="""Assuming `OrderedDict` and `dict` are interchangeable in equality checks. `OrderedDict(a=1, b=2) == OrderedDict(b=2, a=1)` is False, but comparing either with a plain dict ignores order.""",
follow=[
    ("Does a plain dict support `popitem(last=False)`?", "No; `dict.popitem()` always removes the last item (LIFO)."),
    ("Is `OrderedDict` bigger than a dict?", "Yes, it maintains an extra doubly linked list, so it uses more memory."),
]),

X(38, "How do list slicing assignments work", terms=[
    ("Extended slice assignment", "Assigning to a slice with a step; the right side must have exactly the same length."),
], pitfall="""Writing `lst = new_items` inside a function expecting the caller's list to change. Rebinding does nothing to the caller; `lst[:] = new_items` replaces the contents in place.""",
follow=[
    ("How do you insert several items at index i?", "`lst[i:i] = items`."),
    ("What does `lst[::2] = [0]` do for a 4-item list?", "Raises `ValueError`, because the extended slice has 2 slots and the right side has 1 item."),
]),

X(39, "How is a Python list implemented", terms=[
    ("Over-allocation", "Reserving extra capacity so most appends do not need to reallocate."),
    ("Pointer array", "The list stores references (`PyObject *`), not the values themselves."),
], pitfall="""Assuming a list of a million floats is compact. Each item is a separate 24-byte float object plus an 8-byte pointer; use `array` or NumPy for dense numbers.""",
follow=[
    ("Does a list shrink when you remove items?", "Yes, it may reallocate smaller when the size drops below half the allocated capacity."),
    ("How do you inspect the allocated size?", "`sys.getsizeof(lst)` includes the capacity of the pointer array (not the items)."),
]),

X(40, "How is a dict implemented internally", terms=[
    ("Open addressing", "Collisions are resolved by probing other slots in the same table, not by chaining linked lists."),
    ("Key-sharing dict", "Instances of one class can share a single key table for their `__dict__`, saving memory."),
], pitfall="""Deleting most keys from a huge dict and expecting memory to drop. The table does not shrink on deletion; copy it (`d = dict(d)`) to compact.""",
follow=[
    ("Why did the compact layout make dicts ordered?", "Entries are appended to a dense array in insertion order, and iteration walks that array."),
    ("What triggers a resize?", "The table grows when it becomes about two thirds full."),
]),

X(41, "What happens if you mutate an object used as a dict key", terms=[
    ("Hash invariance", "An object's hash must not change while it is stored in a hash-based container."),
], pitfall="""A dataclass with `eq=True, unsafe_hash=True` whose fields are mutated after being used as a key. The entry becomes unreachable by lookup but is still listed in iteration.""",
follow=[
    ("How do you make a safe hashable dataclass?", "`@dataclass(frozen=True)` generates `__hash__` from immutable fields."),
    ("Can you recover the \"lost\" entry?", "Only by iterating the dict; or rebuild the dict so every key is re-hashed."),
]),

X(42, "How do you flatten a nested list", terms=[
    ("`chain.from_iterable`", "Lazily concatenates the iterables produced by one outer iterable."),
], pitfall="""Writing a recursive flattener that treats strings as iterables. A string's items are strings, so recursion never terminates; special-case `str` and `bytes`.""",
follow=[
    ("Why not use `sum(lists, [])`?", "It creates a new list at every step, which is O(n²)."),
    ("How do you flatten very deep nesting without hitting the recursion limit?", "Use an explicit stack of iterators instead of recursion."),
]),

X(43, "How do you find common elements", terms=[
    ("Order-preserving filter", "`[x for x in a if x in set_b]` keeps `a`'s order and duplicates."),
], pitfall="""Using set operations when duplicates matter, for example matching order lines. Use `Counter(a) & Counter(b)` for multiset intersection.""",
follow=[
    ("How do you compare two lists ignoring order but respecting counts?", "`Counter(a) == Counter(b)`."),
    ("How do you find items in `a` but not in `b` with duplicates preserved?", "`list((Counter(a) - Counter(b)).elements())`, or a filter with a set if duplicates of `a` should all be kept."),
]),

X(44, "What is `bisect` used for", terms=[
    ("`bisect_left` vs `bisect_right`", "Insertion point before or after any existing equal items."),
], pitfall="""Using `insort` in a loop for large inputs. The search is O(log n) but the insertion shifts items, so each insert is O(n); sort once at the end if you do not need the order in between.""",
follow=[
    ("How do you map scores to grades with `bisect`?", "`\"FDCBA\"[bisect([60, 70, 80, 90], score)]`."),
    ("Does `bisect` support a key function?", "Yes, since 3.10: `bisect(a, x, key=...)`; `x` is compared to `key(item)`."),
]),

X(45, "What is `heapq` and when", terms=[
    ("Heap invariant", "`a[k] <= a[2k+1]` and `a[k] <= a[2k+2]`; only the minimum is guaranteed to be at the front."),
    ("`heapify`", "Turns a list into a heap in O(n)."),
], pitfall="""Pushing `(priority, obj)` tuples where priorities tie and `obj` is not comparable. Python compares `obj` and raises `TypeError`; add a counter: `(priority, count, obj)`.""",
follow=[
    ("How do you build a max-heap?", "Push negated keys. Python 3.14 also adds public max-heap functions such as `heapq.heappush_max`."),
    ("When is `nlargest` better than `sorted(...)[:k]`?", "For small k relative to n: O(n log k) versus O(n log n); for k near n, sorting wins."),
]),

X(46, "How would you implement an LRU cache", terms=[
    ("LRU", "Least Recently Used: evict the entry that has gone longest without access."),
], pitfall="""Forgetting to mark an entry as recently used on reads. Only updating order on writes gives FIFO eviction, not LRU.""",
follow=[
    ("How would you do it without `OrderedDict`?", "A dict mapping keys to nodes of a doubly linked list; move nodes to the head on access and pop from the tail."),
    ("How do you make it thread-safe?", "Guard `get` and `put` with a `threading.Lock`, since the read and reorder must happen together."),
]),

X(47, "How do you group items by a key", terms=[
    ("`groupby`", "Yields `(key, iterator)` pairs for runs of consecutive items with equal keys."),
], pitfall="""Keeping `groupby`'s group iterators for later. Each group iterator is invalidated when you advance to the next group; convert to a list immediately.""",
follow=[
    ("How do you count items per group?", "`Counter(key(x) for x in items)`."),
    ("How do you group in pandas?", "`df.groupby(\"col\")` followed by an aggregation such as `.sum()` or `.agg(...)`."),
]),

X(48, "What is `array.array`", terms=[
    ("Type code", "A letter such as `\"i\"`, `\"d\"` or `\"B\"` that fixes the C element type."),
    ("Buffer protocol", "Lets `array`, `bytes`, NumPy arrays and `memoryview` share raw memory without copying."),
], pitfall="""Storing values out of range for the type code, such as 300 in a `\"B\"` array, raises `OverflowError`; floats are stored as C doubles, so there is no arbitrary precision.""",
follow=[
    ("When should you use NumPy instead?", "Whenever you need vectorized math, multidimensional data or broadcasting; `array` only stores."),
    ("How do you write an array to a file quickly?", "`arr.tofile(f)` and read back with `arr.fromfile(f, n)`."),
]),
]
