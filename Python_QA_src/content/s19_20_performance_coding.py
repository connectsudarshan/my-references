QUESTIONS = [

# =============== 19. PERFORMANCE & OPTIMIZATION ===============
Q(19, "Easy", "What is the first step when Python code is too slow?",
"""**Measure** before changing anything: time the whole program, then profile to find where time actually goes (`cProfile`, `py-spy`). Most programs spend most of their time in a small part of the code, and intuition about which part is often wrong. Then fix the algorithm or data structure first, micro-optimizations last.""",
r'''
import cProfile, pstats, io
def slow_unique(items):
    out = []
    for x in items:
        if x not in out: out.append(x)        # O(n) membership -> O(n^2) overall
    return out
data = list(range(3000)) * 2
prof = cProfile.Profile(); prof.enable(); slow_unique(data); prof.disable()
stats = pstats.Stats(prof).sort_stats("cumulative")
for (file, line, name), (cc, nc, tt, ct, callers) in stats.stats.items():
    if name == "slow_unique":
        print(f"{name}: {nc} call(s), {ct * 1000:.1f} ms cumulative -> the hotspot")
'''),

Q(19, "Easy", "How do you time a piece of code correctly?",
"""Use `time.perf_counter()` for wall-clock timing of a block (monotonic, high resolution), and `timeit` for small snippets (it repeats the code many times and disables GC by default). Report the best of several repeats; single measurements are noisy.""",
r'''
import time, timeit
t = time.perf_counter(); sum(range(1_000_000)); print(f"block: {(time.perf_counter() - t) * 1000:.1f} ms")
best = min(timeit.repeat("sum(range(1000))", number=1000, repeat=5))
print(f"snippet: {best / 1000 * 1e6:.2f} us per call (best of 5)")
'''),

Q(19, "Moderate", "Why are built-in functions and comprehensions usually faster than explicit loops?",
"""Built-ins like `sum`, `min`, `sorted`, `map`, `str.join` and `collections.Counter` run their loops in C. A comprehension avoids repeated attribute lookups of `append` and uses a specialized bytecode. The less work done per item in the Python interpreter, the faster the code.""",
r'''
import timeit
data = list(range(10_000))
def loop():
    total = 0
    for x in data: total += x
    return total
print("for loop :", round(min(timeit.repeat(loop, number=200, repeat=3)) * 5, 2), "ms")
print("sum()    :", round(min(timeit.repeat(lambda: sum(data), number=200, repeat=3)) * 5, 2), "ms")
'''),

Q(19, "Moderate", "Why is `x in set` faster than `x in list`, and when does it matter?",
"""A set is a hash table: membership is O(1) on average. A list is scanned item by item: O(n). It matters when you test membership many times, for example inside a loop over another collection; converting the list to a set once turns O(n*m) into O(n+m).""",
r'''
import timeit
ids = list(range(50_000)); ids_set = set(ids)
lookups = list(range(49_000, 50_000))
print("list:", round(timeit.timeit(lambda: [x in ids for x in lookups], number=3), 3), "s")
print(f"set : {timeit.timeit(lambda: [x in ids_set for x in lookups], number=3):.5f} s")
'''),

Q(19, "Moderate", "What are the time complexities of common operations on list, dict, set and deque?",
"""- list: index O(1), append O(1) amortized, pop() O(1), insert/pop at front O(n), `in` O(n), sort O(n log n)
- dict/set: get, set, delete, `in` O(1) average (O(n) worst case with pathological hashes)
- deque: append/pop at both ends O(1), index in the middle O(n)
- str concatenation in a loop: O(n^2) worst case; `''.join` is O(n)"""),

Q(19, "Moderate", "How does `functools.lru_cache` speed up code, and what are the risks?",
"""It stores results keyed by the arguments, so repeated calls with the same arguments return instantly (memoization). Risks: arguments must be hashable, unbounded caches (`maxsize=None`) grow forever, cached mutable results can be modified by callers, and on methods the cache keeps `self` alive.""",
r'''
from functools import lru_cache
import time
@lru_cache(maxsize=None)
def paths(r, c):                     # number of grid paths: exponential without caching
    return 1 if r == 0 or c == 0 else paths(r - 1, c) + paths(r, c - 1)
t = time.perf_counter(); n = paths(16, 16); dt = time.perf_counter() - t
print(n, f"in {dt * 1000:.2f} ms", paths.cache_info())
'''),

Q(19, "Moderate", "How do generators help performance and memory?",
"""They produce items one at a time instead of building a whole list, so memory stays constant and work can stop early. Aggregations like `sum(x for x in ...)` and pipelines over files benefit most. They're not faster per item, but they avoid allocating huge intermediate lists.""",
r'''
import sys
squares_list = [x * x for x in range(1_000_000)]
squares_gen = (x * x for x in range(1_000_000))
print("list:", sys.getsizeof(squares_list) // 1024, "KiB | generator:", sys.getsizeof(squares_gen), "bytes")
print(next(x for x in squares_gen if x > 10_000))   # stops early
'''),

Q(19, "Moderate", "What does `__slots__` do for performance?",
"""It removes the per-instance `__dict__`, storing attributes in fixed slots. That reduces memory per object noticeably and makes attribute access slightly faster. Useful when creating very many small objects; the trade-off is no dynamic attributes.""",
r'''
import tracemalloc
class P:
    def __init__(self, x, y): self.x, self.y = x, y
class S:
    __slots__ = ("x", "y")
    def __init__(self, x, y): self.x, self.y = x, y
for cls in (P, S):
    tracemalloc.start(); objs = [cls(i, i) for i in range(100_000)]
    print(cls.__name__, f"{tracemalloc.get_traced_memory()[0] / 1e6:.1f} MB"); tracemalloc.stop()
'''),

Q(19, "Moderate", "When should you use NumPy instead of Python lists?",
"""For large numeric arrays and element-wise math. NumPy stores numbers unboxed in contiguous memory and runs operations in compiled loops (vectorization), typically 10-100x faster than Python loops and using far less memory. For small data or mixed types, lists are fine."""),

Q(19, "Difficult", "How do you speed up CPU-bound Python code beyond algorithmic fixes?",
"""Options in rough order of effort: use C-backed builtins and libraries better; vectorize with NumPy/pandas/Polars; parallelize across processes (`ProcessPoolExecutor`) since threads don't help pure-Python CPU work under the GIL; JIT with Numba for numeric loops; compile with Cython/mypyc; or write the hot core in Rust (PyO3) or C++. Upgrading Python itself (3.11+ is much faster) is often free speed."""),

Q(19, "Moderate", "How do local variables affect speed?",
"""Local variables are accessed by index (`LOAD_FAST`); globals and builtins need dictionary lookups (cached in 3.11+). In very hot loops, binding a frequently used global or method to a local can help a little. It's a last-mile optimization after profiling.""",
r'''
import math, timeit
def g():
    return [math.sqrt(i) for i in range(20_000)]
def l(sqrt=math.sqrt):
    return [sqrt(i) for i in range(20_000)]
print("global lookup:", round(min(timeit.repeat(g, number=50, repeat=3)) * 20, 2), "ms")
print("local alias  :", round(min(timeit.repeat(l, number=50, repeat=3)) * 20, 2), "ms")
'''),

Q(19, "Moderate", "Why is string building with `+=` in a loop slow, and what should you use?",
"""Strings are immutable, so each `+=` can create a new string and copy everything so far, giving quadratic time for long outputs. Collect pieces in a list and `''.join()` them once, or write to `io.StringIO`.""",
r'''
import timeit
parts = [str(i) for i in range(20_000)]
def concat():
    s = ""
    for p in parts: s = s + p
    return s
print("+ in loop:", round(min(timeit.repeat(concat, number=5, repeat=3)) * 200, 2), "ms")
print("join     :", round(min(timeit.repeat(lambda: "".join(parts), number=5, repeat=3)) * 200, 2), "ms")
'''),

Q(19, "Difficult", "How do you find where memory is being used?",
"""`tracemalloc` (stdlib) snapshots allocations with tracebacks and can diff two snapshots to find growth. `sys.getsizeof` measures one object shallowly. Third-party tools: memray (flame graphs, native allocations), pympler, objgraph for reference chains.""",
r'''
import tracemalloc
tracemalloc.start()
cache = {i: str(i) * 20 for i in range(50_000)}
snap = tracemalloc.take_snapshot()
top = snap.statistics("lineno")[0]
print(f"{top.size / 1e6:.1f} MB allocated at line {top.traceback[0].lineno} ({top.count} blocks)")
'''),

Q(19, "Moderate", "Does multithreading make Python code faster?",
"""For I/O-bound work (network calls, disk, subprocesses) yes: threads overlap their waiting because blocking I/O releases the GIL. For pure-Python CPU-bound work, no: the GIL lets only one thread run bytecode at a time. Use processes, or the free-threaded build (3.13t+), for CPU parallelism."""),

Q(19, "Moderate", "What is the cost of function calls and attribute lookups in Python?",
"""Every call creates a frame and binds arguments; every `obj.attr` goes through the attribute lookup protocol. Both are much cheaper since 3.11, but in tight loops of millions of iterations they still dominate. Inlining trivial helpers or hoisting lookups out of loops can help after profiling shows the loop is hot."""),

Q(19, "Moderate", "How can you speed up reading and parsing large files?",
"""Iterate the file object (buffered line reading), avoid reading everything with `read()`/`readlines()`, parse only needed fields (`str.split(maxsplit=...)`, a precompiled regex), use the `csv` module rather than manual splitting, process in binary mode when decoding isn't needed, and parallelize by file with processes. For repeated analytics, convert to a columnar format once.""",
r'''
import re, io
log = io.StringIO("".join(f"2026-09-28 10:00:{i % 60:02d} {'ERROR' if i % 50 == 0 else 'INFO'} req={i}\n" for i in range(100_000)))
pattern = re.compile(r" ERROR ")                      # compiled once, reused per line
print("errors:", sum(1 for line in log if pattern.search(line)))
'''),

Q(19, "Difficult", "What are CPython 3.11+ performance improvements and why do they matter?",
"""3.11 introduced the specializing adaptive interpreter (PEP 659), cheaper frames, zero-cost exception handling (try blocks cost nothing unless raised) and faster startup, making typical code 10-60% faster (about 25% on average). 3.12-3.14 continued with more specializations, an experimental JIT (3.13+), and an optional free-threaded build. Upgrading Python is often the cheapest optimization."""),

Q(19, "Moderate", "How do you avoid repeated work inside loops?",
"""Hoist invariant computations out of the loop (compile regexes, compute constants, look up attributes once), cache results of expensive pure functions, and avoid re-sorting or re-scanning inside the loop.""",
r'''
import timeit, re
lines = [f"id={i} status={'ok' if i % 3 else 'fail'}" for i in range(20_000)]
def inside():  return sum(1 for l in lines if re.compile(r"status=fail").search(l))
PAT = re.compile(r"status=fail")
def hoisted(): return sum(1 for l in lines if PAT.search(l))
print("compile inside loop:", round(min(timeit.repeat(inside, number=5, repeat=3)) * 200, 1), "ms")
print("compiled once      :", round(min(timeit.repeat(hoisted, number=5, repeat=3)) * 200, 1), "ms")
'''),

# =============== 20. CODING PROBLEMS (INTERVIEW-ROUND STYLE) ===============
Q(20, "Easy", "Two Sum: return indices of two numbers that add up to a target.",
"""Use a dict mapping value to index while scanning once: for each number, check whether `target - n` was seen. O(n) time, O(n) space, instead of the O(n^2) double loop.""",
r'''
def two_sum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return seen[target - n], i
        seen[n] = i
    return None
print(two_sum([2, 7, 11, 15], 9), two_sum([3, 2, 4], 6), two_sum([1, 2], 7))
'''),

Q(20, "Easy", "Reverse a string, and check whether it is a palindrome ignoring case and punctuation.",
"""Slicing with a step of -1 reverses (`s[::-1]`). For the palindrome check, keep only alphanumeric characters, casefold, and compare with the reverse; a two-pointer loop avoids the extra copy.""",
r'''
def is_palindrome(s):
    i, j = 0, len(s) - 1
    while i < j:
        if not s[i].isalnum(): i += 1
        elif not s[j].isalnum(): j -= 1
        elif s[i].casefold() != s[j].casefold(): return False
        else: i, j = i + 1, j - 1
    return True
print("python"[::-1], is_palindrome("A man, a plan, a canal: Panama"), is_palindrome("race a car"))
'''),

Q(20, "Easy", "FizzBuzz: print numbers 1..n with multiples of 3 as Fizz, 5 as Buzz, both as FizzBuzz.",
"""Check divisibility by 15 first (or build the string from parts), otherwise print the number.""",
r'''
def fizzbuzz(n):
    return [("Fizz" * (i % 3 == 0) + "Buzz" * (i % 5 == 0)) or str(i) for i in range(1, n + 1)]
print(" ".join(fizzbuzz(15)))
'''),

Q(20, "Easy", "Find the most frequent element (and the top k) in a list.",
"""`collections.Counter` counts in O(n); `most_common(k)` returns the top k (it uses a heap for small k).""",
r'''
from collections import Counter
words = "the cat and the hat and the bat".split()
c = Counter(words)
print(c.most_common(1)[0], c.most_common(2))
'''),

Q(20, "Easy", "Check whether two strings are anagrams.",
"""Compare character counts: `Counter(a) == Counter(b)` is O(n); sorting both is O(n log n). Normalize case and spaces first if required.""",
r'''
from collections import Counter
def anagram(a, b): return Counter(a.replace(" ", "").lower()) == Counter(b.replace(" ", "").lower())
print(anagram("Listen", "Silent"), anagram("Dormitory", "Dirty room"), anagram("abc", "abd"))
'''),

Q(20, "Moderate", "Valid parentheses: check that brackets `()[]{}` are balanced and properly nested.",
"""Use a stack: push opening brackets, and on a closing bracket pop and check it matches. At the end the stack must be empty. O(n).""",
r'''
def valid(s):
    pairs, stack = {")": "(", "]": "[", "}": "{"}, []
    for ch in s:
        if ch in "([{": stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]: return False
    return not stack
print([valid(s) for s in ["()[]{}", "([{}])", "(]", "([)]", "(("]])
'''),

Q(20, "Moderate", "Find the first non-repeating character in a string.",
"""Count characters with `Counter` (insertion-ordered), then return the first with count 1. Two passes, O(n).""",
r'''
from collections import Counter
def first_unique(s):
    counts = Counter(s)
    return next((i for i, ch in enumerate(s) if counts[ch] == 1), -1)
print(first_unique("leetcode"), first_unique("loveleetcode"), first_unique("aabb"))
'''),

Q(20, "Moderate", "Longest substring without repeating characters.",
"""Sliding window: keep the last index of each character; when a repeat appears inside the window, move the window start past its previous position. O(n).""",
r'''
def longest_unique(s):
    last, start, best = {}, 0, 0
    for i, ch in enumerate(s):
        if last.get(ch, -1) >= start:
            start = last[ch] + 1
        last[ch] = i
        best = max(best, i - start + 1)
    return best
print(longest_unique("abcabcbb"), longest_unique("bbbbb"), longest_unique("pwwkew"), longest_unique(""))
'''),

Q(20, "Moderate", "Merge overlapping intervals.",
"""Sort by start, then walk through: if the current interval overlaps the last merged one, extend it; otherwise start a new one. O(n log n).""",
r'''
def merge(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out
print(merge([[1, 3], [2, 6], [8, 10], [15, 18]]), merge([[1, 4], [4, 5]]))
'''),

Q(20, "Moderate", "Group anagrams together from a list of words.",
"""Use a dict keyed by a canonical form of each word (its sorted letters, or a letter-count tuple), collecting words per key.""",
r'''
from collections import defaultdict
def group_anagrams(words):
    groups = defaultdict(list)
    for w in words:
        groups["".join(sorted(w))].append(w)
    return list(groups.values())
print(group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))
'''),

Q(20, "Moderate", "Top k frequent elements in better than O(n log n).",
"""Count with `Counter`, then use `heapq.nlargest(k, ...)` (O(n log k)) or bucket sort by frequency (O(n)).""",
r'''
from collections import Counter
import heapq
def top_k(nums, k):
    counts = Counter(nums)
    return heapq.nlargest(k, counts, key=counts.get)
def top_k_bucket(nums, k):
    counts, buckets = Counter(nums), [[] for _ in range(len(nums) + 1)]
    for n, c in counts.items(): buckets[c].append(n)
    return [n for b in reversed(buckets) for n in b][:k]
print(top_k([1, 1, 1, 2, 2, 3], 2), top_k_bucket([4, 4, 5, 5, 5, 6], 2))
'''),

Q(20, "Moderate", "Maximum subarray sum (Kadane's algorithm).",
"""Track the best sum ending at the current position (either extend the previous run or start fresh) and the best overall. O(n), O(1) space.""",
r'''
def max_subarray(nums):
    best = cur = nums[0]
    for n in nums[1:]:
        cur = max(n, cur + n)
        best = max(best, cur)
    return best
print(max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]), max_subarray([-3, -1, -2]))
'''),

Q(20, "Moderate", "Rotate a list by k positions.",
"""Normalize `k %= len(lst)` and use slicing (new list), or `collections.deque.rotate` (in place, O(k)). The in-place array method uses three reversals.""",
r'''
from collections import deque
def rotate(lst, k):
    if not lst: return lst
    k %= len(lst)
    return lst[-k:] + lst[:-k]
d = deque([1, 2, 3, 4, 5]); d.rotate(2)
print(rotate([1, 2, 3, 4, 5], 2), rotate([1, 2, 3], 7), list(d))
'''),

Q(20, "Moderate", "Flatten an arbitrarily nested list.",
"""A recursive generator with `yield from`, checking for lists (or iterables that aren't strings). For very deep nesting use an explicit stack to avoid the recursion limit.""",
r'''
def flatten(items):
    stack = [iter(items)]
    while stack:
        for x in stack[-1]:
            if isinstance(x, (list, tuple)):
                stack.append(iter(x)); break
            yield x
        else:
            stack.pop()
print(list(flatten([1, [2, [3, [4, (5, 6)]]], 7])))
'''),

Q(20, "Moderate", "Implement binary search, and find the insertion position of a value.",
"""Keep a half-open range `[lo, hi)` and halve it each step: O(log n). The standard library's `bisect` module does this in C.""",
r'''
import bisect
def binary_search(a, x):
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x: lo = mid + 1
        else: hi = mid
    return lo if lo < len(a) and a[lo] == x else -1
a = [1, 3, 5, 7, 9, 11]
print(binary_search(a, 7), binary_search(a, 4), bisect.bisect_left(a, 4))
'''),

Q(20, "Moderate", "Reverse a singly linked list.",
"""Iterate with three pointers (previous, current, next), reversing each link. O(n) time, O(1) space.""",
r'''
class Node:
    def __init__(self, val, nxt=None): self.val, self.next = val, nxt
def reverse(head):
    prev = None
    while head:
        head.next, prev, head = prev, head, head.next
    return prev
def to_list(n):
    out = []
    while n: out.append(n.val); n = n.next
    return out
head = Node(1, Node(2, Node(3, Node(4))))
print(to_list(reverse(head)))
'''),

Q(20, "Moderate", "Detect a cycle in a linked list.",
"""Floyd's tortoise and hare: a slow pointer moves one step, a fast pointer two steps; if they ever meet there is a cycle. O(n) time, O(1) space.""",
r'''
class Node:
    def __init__(self, v): self.v, self.next = v, None
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast: return True
    return False
a, b, c = Node(1), Node(2), Node(3); a.next, b.next = b, c
print(has_cycle(a)); c.next = a; print(has_cycle(a))
'''),

Q(20, "Moderate", "Implement an LRU cache with O(1) get and put.",
"""`OrderedDict` gives O(1) `move_to_end` and `popitem(last=False)`. (From scratch: a dict plus a doubly linked list.)""",
r'''
from collections import OrderedDict
class LRUCache:
    def __init__(self, capacity): self.cap, self.d = capacity, OrderedDict()
    def get(self, key):
        if key not in self.d: return -1
        self.d.move_to_end(key); return self.d[key]
    def put(self, key, value):
        self.d[key] = value; self.d.move_to_end(key)
        if len(self.d) > self.cap: self.d.popitem(last=False)
c = LRUCache(2); c.put(1, 1); c.put(2, 2); r1 = c.get(1); c.put(3, 3)
print(r1, c.get(2), c.get(3), list(c.d))
'''),

Q(20, "Moderate", "Count the number of islands in a grid of '1' (land) and '0' (water).",
"""Scan the grid; for each unvisited land cell start a BFS/DFS that marks the whole island visited, and count how many times you start. O(rows x cols). Use an explicit queue to avoid recursion limits.""",
r'''
from collections import deque
def islands(grid):
    rows, cols, seen, count = len(grid), len(grid[0]), set(), 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in seen:
                count += 1; q = deque([(r, c)]); seen.add((r, c))
                while q:
                    y, x = q.popleft()
                    for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                        if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] == "1" and (ny, nx) not in seen:
                            seen.add((ny, nx)); q.append((ny, nx))
    return count
g = ["11000", "11000", "00100", "00011"]
print(islands(g))
'''),

Q(20, "Moderate", "Climbing stairs / Fibonacci: in how many ways can you climb n stairs taking 1 or 2 steps?",
"""The count follows Fibonacci: ways(n) = ways(n-1) + ways(n-2). Iterate bottom-up with two variables: O(n) time, O(1) space. Naive recursion is exponential.""",
r'''
def climb(n):
    a, b = 1, 1
    for _ in range(n): a, b = b, a + b
    return a
print([climb(n) for n in range(1, 11)], climb(90))
'''),

Q(20, "Moderate", "Given a list of meeting times, find the minimum number of rooms required.",
"""Sort meetings by start; keep a min-heap of end times of ongoing meetings. For each meeting, free a room if the earliest ending meeting finished, then add the current end. The heap's maximum size is the answer. O(n log n).""",
r'''
import heapq
def min_rooms(meetings):
    ends = []
    for start, end in sorted(meetings):
        if ends and ends[0] <= start:
            heapq.heapreplace(ends, end)
        else:
            heapq.heappush(ends, end)
    return len(ends)
print(min_rooms([(0, 30), (5, 10), (15, 20)]), min_rooms([(7, 10), (2, 4)]))
'''),

Q(20, "Moderate", "Implement a function that returns all permutations / subsets of a list.",
"""`itertools.permutations` and `itertools.combinations` in practice; in interviews show backtracking: choose, recurse, un-choose.""",
r'''
from itertools import permutations
def subsets(nums):
    out = [[]]
    for n in nums:
        out += [s + [n] for s in out]
    return out
def perms(nums):
    if len(nums) <= 1: return [nums[:]]
    return [[n] + p for i, n in enumerate(nums) for p in perms(nums[:i] + nums[i + 1:])]
print(subsets([1, 2, 3]))
print(perms([1, 2, 3]) == [list(p) for p in permutations([1, 2, 3])])
'''),

Q(20, "Moderate", "Parse a log file and report the count of each error code, sorted by frequency.",
"""Stream lines, extract the field with a precompiled regex (or split), count with `Counter`, and print `most_common()`. Handle malformed lines by skipping and counting them.""",
r'''
import re, io
from collections import Counter
log = io.StringIO("""10:00:01 ERROR E1023 read timeout
10:00:02 INFO ok
10:00:03 ERROR E2001 crc mismatch
10:00:04 ERROR E1023 read timeout
garbage line
10:00:05 WARN W300 slow
10:00:06 ERROR E1023 read timeout
""")
pat = re.compile(r"^\S+ ERROR (E\d+)")
counts, bad = Counter(), 0
for line in log:
    if m := pat.match(line): counts[m[1]] += 1
    elif not re.match(r"^\d\d:\d\d:\d\d ", line): bad += 1
for code, n in counts.most_common(): print(code, n)
print("malformed lines:", bad)
'''),

Q(20, "Difficult", "Find the k-th largest element in an unsorted list.",
"""Keep a min-heap of size k (`heapq.nlargest(k, nums)[-1]`): O(n log k). Quickselect gives O(n) average. Sorting is O(n log n) and fine for small inputs.""",
r'''
import heapq, random
def kth_largest(nums, k):
    heap = nums[:k]; heapq.heapify(heap)
    for n in nums[k:]:
        if n > heap[0]: heapq.heapreplace(heap, n)
    return heap[0]
def quickselect(nums, k):
    pivot = random.choice(nums)
    hi = [x for x in nums if x > pivot]; eq = [x for x in nums if x == pivot]
    if k <= len(hi): return quickselect(hi, k)
    if k <= len(hi) + len(eq): return pivot
    return quickselect([x for x in nums if x < pivot], k - len(hi) - len(eq))
data = [3, 2, 1, 5, 6, 4]
print(kth_largest(data, 2), quickselect(data, 2), sorted(data)[-2])
'''),

Q(20, "Difficult", "Shortest path in an unweighted graph, and with weights (Dijkstra).",
"""Unweighted: BFS from the source gives shortest hop counts. Non-negative weights: Dijkstra with a min-heap of (distance, node): O((V + E) log V).""",
r'''
import heapq
def dijkstra(graph, src):
    dist, heap = {src: 0}, [(0, src)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]: continue
        for v, w in graph.get(u, []):
            if d + w < dist.get(v, float("inf")):
                dist[v] = d + w; heapq.heappush(heap, (d + w, v))
    return dist
g = {"A": [("B", 4), ("C", 1)], "C": [("B", 2), ("D", 7)], "B": [("D", 1)]}
print(dijkstra(g, "A"))
'''),

Q(20, "Difficult", "Topological sort: order build tasks so dependencies come first, and detect cycles.",
"""Kahn's algorithm: count incoming edges, repeatedly take nodes with zero in-degree. If not all nodes are output, there is a cycle. The stdlib has `graphlib.TopologicalSorter` (3.9+).""",
r'''
from graphlib import TopologicalSorter, CycleError
deps = {"test": {"build"}, "build": {"fetch", "configure"}, "configure": {"fetch"}, "package": {"test"}}
print(list(TopologicalSorter(deps).static_order()))
try:
    list(TopologicalSorter({"a": {"b"}, "b": {"a"}}).static_order())
except CycleError as e:
    print("cycle:", e.args[1])
'''),

Q(20, "Difficult", "Design a rate limiter that allows N requests per time window per user.",
"""Sliding window log: store timestamps per user in a deque, drop those older than the window, allow if fewer than N remain. O(1) amortized per request. A token bucket is an alternative with smoother bursts.""",
r'''
from collections import defaultdict, deque
class RateLimiter:
    def __init__(self, limit, window): self.limit, self.window, self.log = limit, window, defaultdict(deque)
    def allow(self, user, now):
        q = self.log[user]
        while q and q[0] <= now - self.window: q.popleft()
        if len(q) < self.limit:
            q.append(now); return True
        return False
rl = RateLimiter(limit=3, window=10)
print([rl.allow("riya", t) for t in (0, 1, 2, 3, 11, 12)])
'''),

Q(20, "Difficult", "Implement a Trie supporting insert, search and prefix queries (autocomplete).",
"""Each node is a dict of children plus an end flag. Insert and search are O(length of word); autocomplete walks to the prefix node, then collects words below it.""",
r'''
class Trie:
    def __init__(self): self.root = {}
    def insert(self, word):
        node = self.root
        for ch in word: node = node.setdefault(ch, {})
        node["$"] = True
    def starts_with(self, prefix):
        node = self.root
        for ch in prefix:
            if ch not in node: return []
            node = node[ch]
        out, stack = [], [(node, prefix)]
        while stack:
            n, p = stack.pop()
            if "$" in n: out.append(p)
            stack.extend((child, p + ch) for ch, child in n.items() if ch != "$")
        return sorted(out)
t = Trie()
for w in ["nvme", "nvmeof", "nand", "namespace", "sata"]: t.insert(w)
print(t.starts_with("nv"), t.starts_with("na"), t.starts_with("x"))
'''),

Q(20, "Difficult", "Word frequency over a very large file that doesn't fit in memory.",
"""Stream line by line and update a `Counter`. If even the distinct words don't fit, partition words into files by hash (map), count each partition separately (reduce), and merge the top results; or use an approximate structure (Count-Min Sketch) for heavy hitters.""",
r'''
import io, re
from collections import Counter
big_file = io.StringIO("error on device\n" * 3 + "timeout on device\n" * 5 + "ok\n" * 2)
word = re.compile(r"[a-z]+")
counts = Counter()
for line in big_file:                            # one line in memory at a time
    counts.update(word.findall(line.lower()))
print(counts.most_common(3))
'''),

Q(20, "Moderate", "Remove duplicates from a sorted list in place and return the new length.",
"""Two pointers: a write index advances only when a new value appears. O(n) time, O(1) extra space.""",
r'''
def dedupe_sorted(a):
    if not a: return 0
    w = 1
    for r in range(1, len(a)):
        if a[r] != a[w - 1]:
            a[w] = a[r]; w += 1
    del a[w:]
    return w
nums = [1, 1, 2, 3, 3, 3, 4]
print(dedupe_sorted(nums), nums)
'''),

Q(20, "Moderate", "Given a matrix, return it rotated 90 degrees clockwise.",
"""Transpose then reverse each row; in Python, `list(zip(*m[::-1]))` does it in one line (returns tuples).""",
r'''
m = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print([list(r) for r in zip(*m[::-1])])
'''),

Q(20, "Moderate", "Convert a Roman numeral to an integer.",
"""Add each symbol's value, but subtract it if a larger value follows (IV = 4, IX = 9).""",
r'''
def roman_to_int(s):
    v = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for i, ch in enumerate(s):
        total += -v[ch] if i + 1 < len(s) and v[ch] < v[s[i + 1]] else v[ch]
    return total
print(roman_to_int("III"), roman_to_int("LVIII"), roman_to_int("MCMXCIV"))
'''),

Q(20, "Moderate", "Implement a simple thread-safe counter and a producer/consumer queue.",
"""Protect read-modify-write with a `Lock`. For producer/consumer, use `queue.Queue`, which is already thread-safe and supports blocking, `task_done` and `join`.""",
r'''
import threading, queue
class Counter:
    def __init__(self): self.n, self.lock = 0, threading.Lock()
    def inc(self):
        with self.lock: self.n += 1
c, q = Counter(), queue.Queue()
def producer():
    for i in range(1000): q.put(i)
def consumer():
    while (item := q.get()) is not None: c.inc()
cs = [threading.Thread(target=consumer) for _ in range(4)]
[t.start() for t in cs]; producer()
for _ in cs: q.put(None)
[t.join() for t in cs]
print(c.n)
'''),

]
