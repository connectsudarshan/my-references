EXTRAS = [

X(0, "What is the first step when Python code is too slow", terms=[
    ("Profiler", "A tool that measures where time is spent: `cProfile` (deterministic) or py-spy/scalene (sampling)."),
    ("Hot spot", "The small part of the code where most of the time goes."),
], pitfall="""Optimizing code that \"looks slow\" without profiling. Most time is usually in a few places you did not suspect, often I/O or one quadratic loop.""",
follow=[
    ("How do you read `cProfile` output?", "Sort by `cumulative` to find expensive call trees and by `tottime` to find functions that are slow themselves."),
    ("What is Amdahl's law?", "The speedup from optimizing one part is limited by the fraction of total time that part takes."),
]),

X(1, "How do you time a piece of code correctly", terms=[
    ("`timeit.repeat`", "Runs the timing several times so you can take the minimum, which is least affected by noise."),
], pitfall="""Timing code that includes one-time setup (imports, first-call caches, JIT warm-up). Put setup in timeit's `setup=` argument.""",
follow=[
    ("Why take the minimum rather than the mean for micro-benchmarks?", "Noise only adds time, so the minimum is closest to the true cost; for end-to-end timings, report the median and spread."),
    ("How do you benchmark in pytest?", "The pytest-benchmark plugin, or `pytest-codspeed` for CI-stable measurements."),
]),

X(2, "Why are built-in functions and comprehensions usually faster", terms=[
    ("Interpreter overhead", "The cost of dispatching each bytecode instruction, avoided when work happens inside C code."),
], pitfall="""Forcing a clever one-liner (`reduce` with lambdas) believing it is faster. A lambda call per item is often slower than a plain loop.""",
follow=[
    ("Is `map(str, xs)` faster than `[str(x) for x in xs]`?", "Usually slightly, because `str` is a C function called directly without a Python frame."),
    ("Why is `sum(generator)` sometimes slower than `sum(list)`?", "Generator resumption has per-item overhead; the list version pays in memory instead."),
]),

X(3, "Why is `x in set` faster than `x in list`, and when does it matter", terms=[
    ("Amortized construction", "Paying O(n) once to build a set, then O(1) per lookup."),
], pitfall="""Building a set just for one or two lookups. Construction costs more than a single linear scan.""",
follow=[
    ("Is `x in dict` the same speed as `x in set`?", "Yes, both are hash lookups on the keys."),
    ("What about `x in range(n)`?", "O(1) for ints, since `range` computes membership arithmetically."),
]),

X(4, "What are the time complexities of common operations", terms=[
    ("Amortized", "Average cost over a sequence of operations, allowing occasional expensive steps."),
], pitfall="""Assuming `deque` is better than `list` everywhere. Indexing into the middle of a deque is O(n); lists are better for random access.""",
follow=[
    ("What is the cost of `dict.copy()` or `list.copy()`?", "O(n)."),
    ("What is the cost of `set` intersection?", "O(min(len(a), len(b))) on average."),
]),

X(5, "How does `functools.lru_cache` speed up code", terms=[
    ("Cache hit ratio", "Fraction of calls answered from the cache."),
], pitfall="""Caching functions whose results depend on mutable global state or time. The cache returns stale values after the state changes.""",
follow=[
    ("Does `lru_cache` work across processes?", "No, each process has its own cache; use Redis or a disk cache to share."),
    ("Is `lru_cache` thread-safe?", "The cache structure is thread-safe, but a function may be computed more than once concurrently for the same key."),
]),

X(6, "How do generators help performance and memory", terms=[
    ("Early termination", "Stopping a lazy pipeline as soon as the answer is known, skipping the rest of the work."),
], pitfall="""Converting a generator pipeline back to a list at every stage (`list(map(...))`). That removes the memory benefit.""",
follow=[
    ("Are generators always faster?", "No; per-item overhead can make them slower than a list for small data."),
    ("How do you get the first n items lazily?", "`itertools.islice(gen, n)`."),
]),

X(7, "What does `__slots__` do for performance", terms=[
    ("Attribute offset", "Slot attributes are read from a fixed position in the object, avoiding a dict lookup."),
], pitfall="""Adding slots to classes with few instances. The saving is per instance, so it only matters for many (tens of thousands or more) objects.""",
follow=[
    ("How do you measure the saving?", "Compare `tracemalloc` totals for creating many instances with and without slots."),
    ("Does 3.11+ reduce the difference?", "Yes; normal instances got more compact (inline values/lazy dicts), so the gap is smaller than before."),
]),

X(8, "When should you use NumPy instead of Python lists", terms=[
    ("Vectorization", "Expressing a computation as whole-array operations executed in C."),
    ("Broadcasting", "NumPy's rules for combining arrays of different shapes without copying."),
], pitfall="""Looping over NumPy arrays element by element in Python. Each element access creates a Python scalar object, which is slower than a plain list.""",
follow=[
    ("When is NumPy slower than lists?", "For tiny arrays or when you convert back and forth frequently."),
    ("What are alternatives for data frames?", "pandas and polars (the latter is multi-threaded and lazy)."),
]),

X(9, "How do you speed up CPU-bound Python code beyond algorithmic fixes", terms=[
    ("Numba", "JIT compiler for numeric Python functions via LLVM."),
    ("Cython / mypyc", "Compile Python-like code (or type-annotated Python) to C extensions."),
], pitfall="""Rewriting in C or Rust before exhausting simpler options. Better algorithms, vectorization or caching often give bigger gains with far less maintenance.""",
follow=[
    ("How do Rust extensions get built?", "With PyO3 and maturin."),
    ("What about PyPy?", "Often gives large speedups for pure-Python loops, but C-extension compatibility can be an issue."),
]),

X(10, "How do local variables affect speed", terms=[
    ("`LOAD_FAST`", "Bytecode that reads a local variable by index."),
    ("`LOAD_GLOBAL`", "Bytecode that looks up a global, then builtins; specialized and cached since 3.11."),
], pitfall="""Binding globals to locals (`_len = len`) everywhere for micro-speed. Since 3.11 the gain is small and the code gets harder to read; do it only in measured hot loops.""",
follow=[
    ("Why are attribute lookups in a loop costly?", "Each `obj.method` lookup walks the MRO and creates a bound method; hoisting `append = out.append` avoids it."),
    ("How do you see the bytecode?", "`dis.dis(func)`; `dis.dis(func, adaptive=True)` shows specialized instructions."),
]),

X(11, "Why is string building with `+=` in a loop slow", terms=[
    ("`io.StringIO`", "Efficient in-memory text buffer for incremental writes."),
], pitfall="""Relying on CPython's in-place concatenation optimization. It does not apply when the string has other references, or on other implementations.""",
follow=[
    ("What is the cost of `\"\".join` on a list of n pieces?", "O(total length): one pass to size, one to copy."),
    ("What about bytes?", "Use `bytearray` or `b\"\".join(parts)`."),
]),

X(12, "How do you find where memory is being used", terms=[
    ("Snapshot diff", "`snapshot2.compare_to(snapshot1, \"lineno\")` shows allocation growth by source line."),
    ("memray", "Bloomberg's memory profiler, tracking Python and native allocations, with flame graphs."),
], pitfall="""Measuring memory with `tracemalloc` when the growth is in C extensions or NumPy buffers allocated outside Python's allocator hooks. Use memray with native tracking.""",
follow=[
    ("How do you get peak memory?", "`tracemalloc.get_traced_memory()` returns (current, peak); `resource.getrusage` gives max RSS on Unix."),
    ("What is the overhead of tracemalloc?", "Noticeable (often 2x slower and extra memory); enable it only while investigating."),
]),

X(13, "Does multithreading make Python code faster", terms=[
    ("Throughput", "Work completed per unit of time."),
], pitfall="""Using hundreds of threads for I/O. Each thread has a stack and scheduling overhead; use a bounded pool or asyncio for very high concurrency.""",
follow=[
    ("Can threads speed up NumPy code?", "Yes, when the NumPy operations release the GIL; many BLAS routines are already multi-threaded internally."),
    ("What changes with free-threaded Python?", "CPU-bound threads can run in parallel, if the libraries used support it."),
]),

X(14, "What is the cost of function calls and attribute lookups", terms=[
    ("Inline cache", "Per-instruction cache used by the 3.11+ specializing interpreter to speed repeated lookups."),
], pitfall="""Splitting hot inner loops into many tiny functions for readability and then wondering why it is slow. In a measured hot loop, inline the work or vectorize it.""",
follow=[
    ("How much does a Python function call cost?", "Tens of nanoseconds on modern CPUs in 3.11+, more with keyword arguments or decorators."),
    ("Are properties slower than attributes?", "Yes, a property is a function call; still cheap, but measurable in tight loops."),
]),

X(15, "How can you speed up reading and parsing large files", terms=[
    ("Binary mode", "Reading bytes avoids decoding cost when you only need to split or search."),
], pitfall="""Parsing with regexes compiled inside the loop, or `split()` repeatedly on the same line. Compile once and parse each line once.""",
follow=[
    ("How do you parse huge JSON files?", "Use a streaming parser (ijson) or JSON Lines (one object per line)."),
    ("How do you use several cores?", "Split the file into byte ranges aligned to line boundaries and process them in a process pool."),
]),

X(16, "What are CPython 3.11+ performance improvements", terms=[
    ("PEP 659", "Specializing adaptive interpreter: instructions rewrite themselves into type-specific fast versions."),
    ("JIT (3.13+)", "Experimental copy-and-patch JIT, off by default."),
], pitfall="""Upgrading Python and expecting C-extension-heavy workloads to speed up. The gains are in pure-Python execution; NumPy-bound code changes little.""",
follow=[
    ("What made frames cheaper in 3.11?", "Frames are allocated in a contiguous per-thread stack, and full frame objects are created lazily."),
    ("How do you check whether the JIT is enabled?", "`sys._jit.is_enabled()` in 3.14; builds need `--enable-experimental-jit`, and it can be switched with `PYTHON_JIT`."),
]),

X(17, "How do you avoid repeated work inside loops", terms=[
    ("Loop-invariant code motion", "Moving computations that do not change between iterations out of the loop."),
], pitfall="""Querying a database or calling an API inside a loop (the N+1 problem). Batch the requests into one call, then process results in memory.""",
follow=[
    ("How do you cache attribute lookups in a loop?", "Bind them to locals before the loop, such as `add = seen.add`."),
    ("How do you avoid repeated regex compilation?", "Compile once at module level with `re.compile`."),
]),

X(18, "Two Sum", terms=[
    ("Complement", "The value `target - x` that would pair with `x`."),
], pitfall="""Inserting the current number into the dict before checking for its complement. With `target = 2 * x` a single element pairs with itself.""",
follow=[
    ("What if the input is sorted?", "Use two pointers from both ends: O(n) time, O(1) space."),
    ("How do you return all pairs, not just one?", "Collect pairs while scanning; handle duplicates by counting with `Counter`."),
]),

X(19, "Reverse a string, and check whether it is a palindrome", terms=[
    ("Normalization", "Removing case and non-alphanumeric characters before comparing."),
], pitfall="""Using `str.isalnum()` then `lower()` and thinking Unicode is handled. Use `casefold()` for case-insensitive comparison of non-ASCII text.""",
follow=[
    ("How do you do it in O(1) extra space?", "Two indexes moving inward, skipping non-alphanumeric characters."),
    ("How do you check if removing one character can make a palindrome?", "Two pointers; on the first mismatch try skipping either side once."),
]),

X(20, "FizzBuzz", terms=[
    ("Divisibility check", "`n % k == 0`."),
], pitfall="""Checking `% 3` before `% 15` in an `if/elif` chain. Multiples of 15 then print \"Fizz\" only.""",
follow=[
    ("How do you make it easy to add rules (e.g. 7 → Bazz)?", "Loop over an ordered list of `(divisor, word)` pairs and join the matching words."),
    ("Why do interviewers still ask it?", "It quickly shows basic control flow, attention to ordering, and whether you test edge cases."),
]),

X(21, "Find the most frequent element", terms=[
    ("Top-k", "Selecting the k largest items without fully sorting."),
], pitfall="""Assuming a unique answer. Several elements can tie; decide whether to return all of them or the first seen.""",
follow=[
    ("How do you do it for a stream?", "Maintain a `Counter`; for approximate results with little memory, use a count-min sketch or Misra-Gries."),
    ("What does `most_common()` with no argument return?", "All items sorted by count, descending."),
]),

X(22, "Check whether two strings are anagrams", terms=[
    ("Character histogram", "Counts of each character; equal histograms mean anagrams."),
], pitfall="""Using `sorted(a) == sorted(b)` on very long strings in a hot path. It is O(n log n); counting is O(n).""",
follow=[
    ("How do you ignore spaces and case?", "Normalize first: `\"\".join(ch for ch in s.casefold() if not ch.isspace())`."),
    ("How do you find all anagram positions of p in s?", "A sliding window of length `len(p)` with a running count, O(n)."),
]),

X(23, "Valid parentheses", terms=[
    ("Stack", "Last-in, first-out structure; a Python list with `append`/`pop`."),
], pitfall="""Returning True at the end without checking that the stack is empty. Input like `\"((\"` would pass.""",
follow=[
    ("How do you find the longest valid substring?", "A stack of indexes, or two counters in two passes, in O(n)."),
    ("How do you generate all valid combinations of n pairs?", "Backtracking that adds `(` while opens < n and `)` while closes < opens."),
]),

X(24, "Find the first non-repeating character", terms=[
    ("Two passes", "Count first, then scan in the original order."),
], pitfall="""Returning the first character with count 1 from a `set` or unordered structure. Order must come from the string itself.""",
follow=[
    ("What should you return if none exists?", "Agree on a value up front, such as `None` or `-1` for an index."),
    ("How does the stream version work?", "Counts plus a queue of candidates; pop from the front while the front's count exceeds 1."),
]),

X(25, "Longest substring without repeating characters", terms=[
    ("Sliding window", "A range `[left, right]` moved across the input, expanding and shrinking to keep a condition true."),
], pitfall="""Moving `left` backwards when a repeated character's last index is before the window. Use `left = max(left, last[ch] + 1)`.""",
follow=[
    ("What is the complexity?", "O(n) time and O(k) space for the alphabet size k."),
    ("How do you allow at most k distinct characters instead?", "Keep counts in the window and shrink from the left while the number of distinct keys exceeds k."),
]),

X(26, "Merge overlapping intervals", terms=[
    ("Overlap condition", "`start <= last_end` (use `<` if touching intervals should stay separate)."),
], pitfall="""Replacing the end with the new interval's end instead of `max(last_end, end)`. A contained interval would then shrink the merged one.""",
follow=[
    ("How do you insert one new interval into a sorted, merged list?", "Add intervals ending before it, merge overlapping ones, then add the rest: O(n)."),
    ("How do you find free time slots?", "Merge all busy intervals, then report the gaps between consecutive merged intervals."),
]),

X(27, "Group anagrams together", terms=[
    ("Canonical key", "A representation equal for all anagrams, such as the sorted letters."),
], pitfall="""Using a list of counts as the dict key. Lists are unhashable; convert to a tuple.""",
follow=[
    ("Which key is faster for long words?", "A 26-count tuple is O(L) per word; sorting is O(L log L)."),
    ("How do you return groups in first-seen order?", "Dicts keep insertion order, so `list(groups.values())` already does."),
]),

X(28, "Top k frequent elements", terms=[
    ("Bucket sort", "Placing items into buckets indexed by frequency, then reading buckets from the highest."),
], pitfall="""Using a max-heap of all n items and popping k. That is O(n + k log n) and uses O(n) heap space; `nlargest` with a size-k heap is simpler.""",
follow=[
    ("How do you break ties deterministically?", "Sort by `(-count, value)`."),
    ("Which approach is best when k is close to n?", "Just sort: O(n log n) with small constants."),
]),

X(29, "Maximum subarray sum", terms=[
    ("Kadane's algorithm", "Dynamic programming keeping the best sum ending at each position."),
], pitfall="""Initializing the best sum to 0. For an all-negative array the answer should be the largest (least negative) element, not 0.""",
follow=[
    ("How do you return the subarray indices too?", "Track where the current run started and update the best start and end when the best sum improves."),
    ("What about the maximum product subarray?", "Track both max and min products ending here, since a negative can flip the min into the max."),
]),

X(30, "Rotate a list by k positions", terms=[
    ("Reversal algorithm", "Reverse the whole array, then the first k and the remaining parts, for in-place rotation."),
], pitfall="""Forgetting `k %= n` or not handling an empty list. `k` larger than the length, or `n == 0`, gives wrong results or `ZeroDivisionError`.""",
follow=[
    ("Which direction does `deque.rotate(k)` go?", "Right for positive k, left for negative."),
    ("What is the complexity of slicing rotation?", "O(n) time and O(n) extra space."),
]),

X(31, "Flatten an arbitrarily nested list", terms=[
    ("Explicit stack", "Replacing recursion with a list of iterators to avoid the recursion limit."),
], pitfall="""Treating `str` or `bytes` as nested iterables. Each character is itself a string, which causes infinite recursion.""",
follow=[
    ("How do you flatten nested dicts into dotted keys?", "Recursively join parent and child keys: `{\"a.b\": 1}`."),
    ("How do you preserve tuples as leaves?", "Only recurse into `list` instances, not all iterables."),
]),

X(32, "Implement binary search", terms=[
    ("Invariant", "A condition kept true in every iteration, such as \"the answer is in `[lo, hi)`\"."),
], pitfall="""Off-by-one errors from mixing inclusive and exclusive bounds, giving infinite loops. Pick one convention (half-open) and keep it.""",
follow=[
    ("Can Python's midpoint overflow like in Java?", "No, ints are arbitrary precision, so `(lo + hi) // 2` is safe."),
    ("How do you binary search on the answer?", "Search over possible values with a monotonic predicate, such as the minimum capacity that makes a check pass."),
]),

X(33, "Reverse a singly linked list", terms=[
    ("In-place reversal", "Redirecting each node's `next` pointer without allocating new nodes."),
], pitfall="""Losing the rest of the list by overwriting `curr.next` before saving it. Save `nxt = curr.next` first, or use tuple assignment in the right order.""",
follow=[
    ("How do you do it recursively?", "Reverse the rest, then set `head.next.next = head` and `head.next = None`; O(n) stack space."),
    ("How do you reverse only positions m..n?", "Walk to node m-1, reverse the sublist, and reconnect both ends."),
]),

X(34, "Detect a cycle in a linked list", terms=[
    ("Floyd's algorithm", "Tortoise and hare: pointers moving at speeds 1 and 2."),
], pitfall="""Checking `fast.next.next` without first checking `fast and fast.next`. It raises `AttributeError` on lists without a cycle.""",
follow=[
    ("How do you find where the cycle starts?", "After they meet, move one pointer to the head; advance both one step at a time; they meet at the cycle start."),
    ("What is the simpler O(n)-space approach?", "Store visited node ids in a set."),
]),

X(35, "Implement an LRU cache with O(1)", terms=[
    ("Doubly linked list", "Allows O(1) removal of any node given a reference."),
], pitfall="""Evicting before updating an existing key on `put`. Updating a key that is already present should not evict anything.""",
follow=[
    ("How do you make it an LFU cache instead?", "Track frequency buckets (dict of frequency to OrderedDict) and a minimum-frequency pointer."),
    ("How would you add TTL?", "Store expiry times with values and check them on `get`."),
]),

X(36, "Count the number of islands", terms=[
    ("Flood fill", "BFS or DFS marking all connected cells."),
    ("Union-find", "Disjoint-set structure, useful when cells are added one at a time."),
], pitfall="""Recursive DFS on a large grid. It exceeds the recursion limit; use an explicit stack or BFS with a deque.""",
follow=[
    ("How do you count islands as land is added dynamically?", "Union-find with path compression: each addition is nearly O(1)."),
    ("Should you mutate the input grid?", "Ask first; otherwise keep a separate visited set."),
]),

X(37, "Climbing stairs / Fibonacci", terms=[
    ("Dynamic programming", "Solving a problem from overlapping subproblems, computed once each."),
], pitfall="""Naive recursion without memoization. It is exponential and times out around n = 35-40.""",
follow=[
    ("How do you get O(1) space?", "Keep only the last two values."),
    ("How do you compute it in O(log n)?", "Matrix exponentiation or fast doubling."),
]),

X(38, "Given a list of meeting times, find the minimum number of rooms", terms=[
    ("Sweep line", "Processing sorted start and end events and tracking the count in between."),
], pitfall="""Treating a meeting that starts exactly when another ends as overlapping (or not) inconsistently. Decide the rule; with `heap[0] <= start` a room is reused.""",
follow=[
    ("What is the sweep-line alternative?", "Sort starts and ends separately and walk both with two pointers."),
    ("How do you also assign room numbers?", "Keep a heap of `(end_time, room_id)` and reuse the freed room id."),
]),

X(39, "Implement a function that returns all permutations", terms=[
    ("Backtracking", "Building candidates incrementally and undoing the last choice to try the next."),
], pitfall="""Appending the current path list itself to results (`res.append(path)`). All entries share one list that is later emptied; append a copy.""",
follow=[
    ("How do you avoid duplicate permutations with repeated items?", "Sort first and skip an item equal to the previous one when the previous was not used at this depth."),
    ("How many subsets does a list of n items have?", "2**n, including the empty set."),
]),

X(40, "Parse a log file and report the count of each error code", terms=[
    ("Streaming", "Processing input line by line so memory stays constant."),
], pitfall="""Assuming every line matches the pattern. Malformed lines then raise `AttributeError` on `None.group`; skip or count them separately.""",
follow=[
    ("How do you handle gzip-compressed logs?", "`gzip.open(path, \"rt\")` streams them transparently."),
    ("How would you scale this to many files?", "Process files in parallel with a pool and merge the `Counter`s (`sum` or `update`)."),
]),

X(41, "Find the k-th largest element", terms=[
    ("Quickselect", "Partition-based selection with average O(n) time."),
], pitfall="""Using quickselect with a fixed pivot on sorted input. It degrades to O(n²); choose a random pivot.""",
follow=[
    ("What is the k-th largest in a stream?", "Keep a size-k min-heap; its root is the answer."),
    ("How does `statistics.median` relate?", "It sorts, O(n log n); quickselect finds the median in O(n) average."),
]),

X(42, "Shortest path in an unweighted graph", terms=[
    ("Relaxation", "Updating a node's distance when a shorter path is found."),
    ("Lazy deletion", "Skipping stale heap entries whose distance is larger than the recorded best."),
], pitfall="""Running Dijkstra with negative edge weights. It can return wrong answers; use Bellman-Ford.""",
follow=[
    ("How do you reconstruct the path?", "Store each node's predecessor when relaxing, then walk back from the target."),
    ("What does A* add?", "A heuristic estimate of remaining distance that guides the search toward the goal."),
]),

X(43, "Topological sort", terms=[
    ("DAG", "Directed acyclic graph; only DAGs have a topological order."),
    ("`graphlib.TopologicalSorter`", "Stdlib implementation (3.9+), with support for parallel processing of ready nodes."),
], pitfall="""Not detecting cycles. Kahn's algorithm must check that all nodes were output; otherwise a cycle exists.""",
follow=[
    ("How does `graphlib` report cycles?", "It raises `graphlib.CycleError` with the cycle's nodes."),
    ("How do you run independent tasks in parallel?", "Use `get_ready()` and `done()` on a `TopologicalSorter` to dispatch nodes whose dependencies are finished."),
]),

X(44, "Design a rate limiter", terms=[
    ("Token bucket", "Tokens refill at a steady rate; each request consumes one; allows short bursts."),
    ("Sliding window log", "Keeps each request timestamp; exact but memory grows with the limit."),
], pitfall="""Implementing it in process memory when the service runs on several instances. Each instance has its own counters; use a shared store such as Redis with atomic operations.""",
follow=[
    ("What does a fixed window counter get wrong?", "Bursts at the boundary: up to 2N requests across two adjacent windows."),
    ("How do you tell clients to back off?", "Return HTTP 429 with a `Retry-After` header."),
]),

X(45, "Implement a Trie", terms=[
    ("Prefix tree", "Tree where each edge is a character and paths spell stored words."),
], pitfall="""Marking a word's end by the absence of children. Words that are prefixes of other words (\"car\" and \"cart\") then cannot be found; use an explicit end flag.""",
follow=[
    ("How do you return the top suggestions for a prefix?", "Store counts at end nodes and keep a small heap per node, or search the subtree for the best k."),
    ("How do you reduce memory?", "Compress chains of single children (radix tree), or use a sorted list with `bisect` for prefix ranges."),
]),

X(46, "Word frequency over a very large file", terms=[
    ("External sort / partitioning", "Splitting data into disk-backed partitions that each fit in memory."),
    ("MapReduce", "Map to key-value pairs, shuffle by key, reduce per key."),
], pitfall="""Loading the whole file (`read().split()`). Stream line by line; memory then depends only on the number of distinct words.""",
follow=[
    ("How do you partition words so each fits in memory?", "Hash each word to one of N files; the same word always goes to the same file."),
    ("How do approximate methods help?", "Count-min sketch or HyperLogLog give frequency or cardinality estimates in fixed memory."),
]),

X(47, "Remove duplicates from a sorted list in place", terms=[
    ("Write pointer", "Index of the next position to write a kept value."),
], pitfall="""Deleting items with `del lst[i]` while scanning. Each deletion shifts the tail, making it O(n²).""",
follow=[
    ("How do you allow each value at most twice?", "Compare with the element two positions before the write pointer."),
    ("What if the list is not sorted?", "Use a seen set, or `dict.fromkeys` to keep order."),
]),

X(48, "Given a matrix, return it rotated 90 degrees", terms=[
    ("Transpose", "Swapping rows and columns: `m[i][j]` becomes `m[j][i]`."),
], pitfall="""Rotating in place by swapping cells without a temporary pattern. You overwrite values before moving them; do four-way swaps per layer, or transpose then reverse rows.""",
follow=[
    ("How do you rotate counter-clockwise?", "`list(zip(*m))[::-1]`, or transpose then reverse the row order."),
    ("Does it work for non-square matrices?", "The `zip` version does; the in-place version needs a square matrix."),
]),

X(49, "Convert a Roman numeral to an integer", terms=[
    ("Subtractive notation", "A smaller symbol before a larger one is subtracted: IV, IX, XL, XC, CD, CM."),
], pitfall="""Accepting invalid numerals such as \"IIII\" or \"IC\" silently. If validation matters, convert back and compare, or use a strict regex.""",
follow=[
    ("How do you convert an integer to Roman?", "Greedy over value-symbol pairs from 1000 (\"M\") down to 1 (\"I\"), including the subtractive pairs."),
    ("What is the maximum standard value?", "3999 (MMMCMXCIX) without special notation."),
]),

X(50, "Implement a simple thread-safe counter", terms=[
    ("Lock", "Mutual exclusion around the read-modify-write."),
], pitfall="""Protecting `increment` with a lock but reading the value without one while computing derived state. Every compound operation on shared state needs the lock.""",
follow=[
    ("Is `itertools.count()` a thread-safe counter?", "`next()` on it happens to be atomic in CPython with the GIL, but that is an implementation detail; use a lock."),
    ("How do you count across processes?", "`multiprocessing.Value` with its lock, or aggregate per-process counts at the end."),
]),
]
