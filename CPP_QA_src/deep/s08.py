DEEP = {

201: D("The STL's main components are containers (store data), iterators (traverse it), algorithms (operate on ranges), and function objects (customize behaviour), plus adaptors and allocators.",
"""The key design idea is that **algorithms work on iterator ranges, not on containers**: `std::sort`, `std::find`, `std::transform` don't know which container they operate on. So N algorithms times M containers needs N + M implementations, not N x M.

Containers: sequence (`vector`, `deque`, `list`, `forward_list`, `array`), associative (`set`, `map`, multi variants), unordered (hash-based), and adaptors (`stack`, `queue`, `priority_queue`). C++20 ranges build on the same ideas with composable views.""",
"Writing hand-rolled loops for tasks the algorithms already express (find, count, transform, partition), which is longer and more error-prone.",
["Why do algorithms take iterators instead of containers? => To decouple them, so one algorithm works with every container and even raw arrays.",
 "What do C++20 ranges add? => Algorithms taking whole ranges, projections, and lazy composable views."]),

202: D("A container is a class template that owns a collection of elements and manages their storage, offering a standard interface (iterators, `size()`, `empty()`, insertion and removal).",
"""Categories and when to use them:

- **Sequence containers**: `vector` (default choice, contiguous), `array` (fixed size), `deque` (fast at both ends), `list`/`forward_list` (stable iterators, cheap splicing).
- **Ordered associative**: `set`, `map` and multi versions (red-black trees, sorted, O(log n)).
- **Unordered associative**: `unordered_set`, `unordered_map` (hash tables, average O(1)).
- **Adaptors**: `stack`, `queue`, `priority_queue` restrict an underlying container's interface.
- C++23 adds flat containers (`std::flat_map`, `std::flat_set`) backed by sorted vectors.""",
"Choosing `std::list` for performance by Big-O reasoning; `std::vector` is usually faster in practice because of cache locality.",
["What should be your default container? => `std::vector`, unless measurements or requirements say otherwise.",
 "What are C++23 flat containers? => Sorted-vector-backed maps and sets: faster lookup and iteration, slower insertion."]),

203: D("`std::vector` is a dynamic array whose size can change at runtime and whose elements live on the heap; `std::array<T, N>` is a fixed-size array whose size is part of the type and whose elements live inside the object.",
"""`std::array` has no allocation, can live on the stack or in static memory, is an aggregate (`std::array<int, 3> a{1, 2, 3};`), works in `constexpr` code and doesn't decay to a pointer. It's ideal for small fixed tables, e.g. register maps or lookup tables in firmware.

`std::vector` grows dynamically with amortized O(1) `push_back`, can be moved in O(1) (pointer steal), and is the default for variable-length data. Moving a `std::array` moves each element (O(N)).""",
"Using `std::vector` for small fixed-size data in hot paths (like a 4-element coordinate) and paying for a heap allocation each time.",
["Can `std::array` be used in constexpr code? => Yes, it's a literal type usable at compile time.",
 "Why is moving a `std::vector` O(1) but moving a `std::array` O(N)? => The vector swaps its heap pointer; the array must move each element stored inline."]),

204: D("`std::pair<A, B>` holds exactly two values (`first`, `second`); `std::tuple<Ts...>` holds a fixed number of values of possibly different types, accessed with `std::get<I>` or `std::get<T>`.",
"""Both support comparison (lexicographic), `std::make_pair`/`std::make_tuple`, class template argument deduction (`std::pair p{1, 2.0};`), and C++17 structured bindings (`auto [key, value] = *it;`).

`std::tie` creates a tuple of references, handy for multiple assignment and lexicographic comparisons in `operator<`.

For public APIs prefer a small named struct over tuples: `result.lba` is clearer than `std::get<2>(result)`.""",
"Returning `std::tuple<int, int, bool>` from public functions; callers mix up which element means what. Use a named struct.",
["How do structured bindings work with pairs? => `auto [a, b] = pair;` introduces names bound to `first` and `second`.",
 "What does `std::tie` return? => A tuple of lvalue references to its arguments."]),

205: D("An iterator is an object that points to an element in a range and supports moving to the next element and accessing the current one; it generalizes a pointer.",
"""Every container provides `begin()`/`end()` (end is one past the last element), and algorithms take iterator pairs. Iterator capabilities differ by category (input, forward, bidirectional, random access, contiguous), and algorithms require minimum categories.

Iterators can be invalidated by container modifications; each container documents when. C++20 ranges add **sentinels** (end markers of a different type) and range-based algorithms that accept whole containers.""",
"Dereferencing `end()` or using an iterator after the container was modified in a way that invalidates it.",
["Why is `end()` one past the last element? => Half-open ranges make empty ranges (`begin == end`) and length (`end - begin`) natural.",
 "What is a sentinel in C++20 ranges? => An end marker whose type may differ from the iterator, e.g. for null-terminated strings."]),

206: D("`std::vector` stores elements contiguously with fast random access and cache-friendly iteration; `std::list` is a doubly linked list with O(1) insertion and removal anywhere given an iterator, and stable iterators, but no random access.",
"""In practice `vector` wins most workloads, even with middle insertions, because traversal of contiguous memory is far faster than pointer chasing and each list node is a separate allocation (with two pointers of overhead).

Choose `list` when: you need iterators and references that stay valid across insertions and removals, you frequently splice sublists between lists (O(1)), or elements are very expensive or impossible to move.""",
"Picking `std::list` because \"insertion is O(1)\" while the code first searches linearly for the position, making the operation O(n) with poor locality anyway.",
["What does `std::list::splice` do? => Moves nodes between lists in O(1) without copying or reallocating.",
 "Why is vector faster for middle insertion than theory suggests? => Shifting contiguous memory is very fast, and finding the position in a list is slow."]),

207: D("`std::map` is an ordered associative container implemented as a balanced binary search tree (O(log n) operations, keys sorted); `std::unordered_map` is a hash table (average O(1), worst case O(n), no ordering).",
"""Choose `map` when you need sorted iteration, range queries (`lower_bound`, `upper_bound`), stable performance without hashing, or keys that are easy to compare but hard to hash. Choose `unordered_map` for fast lookups by key when order doesn't matter.

Both allocate a node per element; `unordered_map` also has a bucket array. For small maps, a sorted `std::vector` or C++23 `std::flat_map` can outperform both.""",
"Using `unordered_map` with a poor hash function (or attacker-controlled keys), degrading to O(n) lookups.",
["When is `std::map` better than `unordered_map`? => When you need ordering, range queries, or predictable worst-case performance.",
 "What's a faster alternative for small, rarely modified maps? => A sorted `std::vector` of pairs or `std::flat_map`."]),

208: D("`std::set` stores unique keys in sorted order; `std::multiset` allows duplicate keys, keeping equal keys adjacent.",
"""With `multiset`, `insert` always succeeds, `count(k)` may exceed 1, `equal_range(k)` returns all equal elements, and `erase(k)` removes **all** of them (use `erase(it)` to remove one).

Both are ordered by a strict weak ordering (default `std::less<Key>`); elements are const through iterators because modifying them would break the ordering. C++17 `extract` lets you take a node out, modify it, and reinsert without reallocation.""",
"Calling `ms.erase(value)` on a multiset to remove one occurrence, which removes every equal element.",
["How do you remove a single element from a multiset? => `ms.erase(ms.find(value))` (after checking it isn't `end()`).",
 "How can you modify a key in a set without reallocation? => C++17 `extract` the node, change it, and `insert` it back."]),

209: D("`std::vector::push_back` is **amortized** O(1): usually constant time, but occasionally O(n) when capacity runs out and all elements are moved to a larger buffer.",
"""Capacity grows geometrically (by a factor of 1.5 or 2 depending on the implementation), so the total cost of n pushes is O(n), averaging O(1) each.

If elements have a `noexcept` move constructor, reallocation moves them; otherwise it copies (to preserve the strong exception guarantee). Use `reserve(n)` when the final size is known to avoid reallocations entirely, which also keeps pointers and iterators valid.""",
"Pushing millions of elements without `reserve` in a latency-sensitive path, causing multiple large reallocations and copies at unpredictable moments.",
["Why must the growth be geometric? => Growing by a constant amount would make n pushes cost O(n²).",
 "What decides whether reallocation moves or copies elements? => Whether the move constructor is `noexcept` (`std::move_if_noexcept`)."]),

210: D("`size()` is the number of elements currently in the vector; `capacity()` is how many elements fit in the allocated storage before a reallocation is needed.",
"""`capacity() >= size()` always. Growing past capacity triggers reallocation (and iterator invalidation). `clear()` and `erase()` reduce size but not capacity; `shrink_to_fit()` is a non-binding request to release excess capacity; the swap trick (`std::vector<T>(v).swap(v)`) forces it.

Understanding the difference matters for memory usage: a vector that once held a million elements keeps that capacity after `clear()`.""",
"Expecting `v.clear()` to free the vector's memory; capacity stays the same until `shrink_to_fit()` or destruction.",
["Is `shrink_to_fit` guaranteed to free memory? => No, it's a non-binding request, though major implementations honour it.",
 "Does `reserve` change `size()`? => No, only capacity; `resize` changes size."]),

211: D("`reserve(n)` ensures the vector's capacity is at least `n` without changing its size, pre-allocating storage to avoid repeated reallocations.",
"""Benefits: fewer allocations and element moves, predictable performance, and pointers/iterators that stay valid while pushing up to `n` elements.

`reserve` vs `resize`: `resize(n)` creates `n` elements (default-constructed or copies), `reserve(n)` only allocates. Calling `reserve` repeatedly with small increments (e.g. `reserve(size() + 1)` in a loop) defeats geometric growth and makes insertion quadratic.""",
"Calling `v.reserve(n)` and then assigning `v[i] = x` for `i < n`; the elements don't exist yet (size is still 0). Use `push_back` or `resize`.",
["What's the danger of `reserve(size() + 1)` before each push? => It prevents geometric growth, making the loop O(n²).",
 "Does `reserve` construct elements? => No, only `resize` or insertion does."]),

212: D("When a `std::vector` reallocates, all iterators, pointers and references to its elements are invalidated, because the elements move to new storage.",
"""Reallocation happens when an insertion exceeds `capacity()` (`push_back`, `emplace_back`, `insert`, `resize`, `reserve` above capacity). Without reallocation, insertions still invalidate iterators at and after the insertion point.

Safe patterns: use indices instead of iterators or pointers during insertion loops, `reserve` enough capacity up front, or re-obtain iterators after modifications. Debug modes (`_GLIBCXX_DEBUG`, MSVC iterator debugging) and AddressSanitizer catch many of these bugs.""",
"`for (auto& x : v) if (cond(x)) v.push_back(transform(x));`, where the range-for iterators dangle after the first reallocation.",
["Does `push_back` without reallocation invalidate existing iterators? => No, only the `end()` iterator is invalidated.",
 "How do you catch invalidated-iterator bugs? => Debug STL modes (`_GLIBCXX_DEBUG`, MSVC checked iterators) and sanitizers."]),

213: D("`std::deque` is a double-ended queue with O(1) insertion and removal at both ends, implemented as a sequence of fixed-size blocks; `std::vector` is one contiguous block with fast insertion only at the back.",
"""Deque advantages: `push_front` is O(1), growing never moves existing elements (references to elements stay valid on push at either end, though iterators are invalidated), and no huge contiguous reallocations.

Disadvantages: elements are not contiguous (no `data()`, can't pass to C APIs), slightly slower indexing (two-level lookup), and more memory overhead for small sizes. `std::queue` uses `deque` by default.""",
"Passing `&dq[0]` to an API expecting contiguous memory; deque storage is split into blocks.",
["Does `deque::push_back` invalidate references to existing elements? => No, references stay valid (iterators are invalidated).",
 "What's the default underlying container of `std::queue` and `std::stack`? => `std::deque`."]),

214: D("The classic iterator categories are input, output, forward, bidirectional and random access; C++20 adds contiguous iterators as a refinement of random access.",
"""- **Input**: single-pass read (`istream_iterator`).
- **Output**: single-pass write (`back_insert_iterator`, `ostream_iterator`).
- **Forward**: multi-pass read/write (`forward_list`, unordered containers).
- **Bidirectional**: plus `--` (`list`, `set`, `map`).
- **Random access**: plus `+ n`, `[]`, `<` (`deque`).
- **Contiguous** (C++20): elements adjacent in memory (`vector`, `array`, `string`, raw pointers).

Algorithms state requirements: `std::sort` needs random access (so `std::list` has its own `sort`), `std::reverse` needs bidirectional. C++20 expresses them as concepts (`std::random_access_iterator`).""",
"Calling `std::sort` on `std::list` iterators, which fails to compile with a long error because list iterators are only bidirectional.",
["Why can't `std::sort` work on `std::list`? => It needs random-access iterators for efficient partitioning; lists provide only bidirectional.",
 "Which category do `std::vector` iterators belong to? => Contiguous (and therefore random access)."]),

215: D("`std::find` does a linear search on any input range and returns an iterator to the element (O(n)); `std::binary_search` requires a sorted range and only returns `bool` (O(log n) comparisons).",
"""To locate the element in a sorted range use `std::lower_bound` (first element not less than the value), `upper_bound`, or `equal_range`. `binary_search` alone doesn't tell you where the element is.

On a non-sorted range, `binary_search` gives meaningless results (undefined behaviour in terms of correctness). For associative containers use their member `find`, which is O(log n) or O(1).""",
"Calling `std::binary_search` on unsorted data, or using `std::find` on a `std::set` instead of `set::find` (O(n) instead of O(log n)).",
["How do you get the position of a value in a sorted vector? => `std::lower_bound`, then check the element equals the value.",
 "Why prefer `set.find(x)` over `std::find(set.begin(), set.end(), x)`? => The member function uses the tree (O(log n)); the algorithm scans linearly."]),

216: D("`std::map` guarantees elements are iterated in ascending key order (by its comparator); `std::unordered_map` guarantees no particular order, and the order can change after insertions that trigger rehashing.",
"""Code that prints or serializes an `unordered_map` directly produces nondeterministic output across runs, platforms or library versions, which breaks golden-file tests and reproducible builds.

If you need deterministic output from an unordered container, copy the keys into a vector and sort them before iterating, or use `std::map` from the start.""",
"Writing test reports by iterating an `unordered_map`, then seeing different line orders between Linux and Windows runs.",
["Can iteration order of `unordered_map` change without modifying elements' values? => Yes, after inserts that trigger rehashing.",
 "How do you print an unordered_map deterministically? => Collect and sort the keys, then iterate in sorted order."]),

217: D("A functor is an object of a class that overloads `operator()`, so it can be called like a function while carrying state; STL algorithms and containers accept functors to customize behaviour.",
"""Examples: comparators (`std::greater<>`), hash functions, predicates for `std::count_if`, and stateful callables (a counter or a threshold). Because the functor type is a template parameter, calls can be inlined, which often makes functors faster than function pointers.

Lambdas are the concise way to write functors; the standard library provides many (`std::plus`, `std::less`, `std::equal_to`), and transparent ones (`std::less<>`) that enable heterogeneous lookup.""",
"Relying on a functor's internal state being shared across calls in algorithms that may copy it (e.g. `std::for_each` returns the final copy; others don't).",
["What is a transparent comparator? => One like `std::less<>` that can compare different types, enabling `set.find(\"key\")` without creating a `std::string`.",
 "How do you share functor state with algorithms that copy it? => Keep state outside and capture it by reference, or use `std::ref`."]),

218: D("`std::stack`, `std::queue` and `std::priority_queue` are container **adaptors**: they wrap an underlying container (by default `deque`, `deque` and `vector`) and expose only a restricted interface (LIFO, FIFO, or highest-priority-first).",
"""Adaptors provide no iterators, so you can't traverse or search them; they enforce the intended access pattern. You can change the underlying container (`std::stack<int, std::vector<int>>`).

If you need both queue behaviour and iteration or random access, use `std::deque` directly.""",
"Trying to iterate over a `std::queue` to print it; adaptors deliberately don't provide iterators.",
["Why don't adaptors have iterators? => They restrict access to their semantic operations (push/pop/top/front).",
 "What's the underlying container of `std::priority_queue`? => `std::vector` by default, organized as a binary heap."]),

219: D("Use the erase-remove idiom (`v.erase(std::remove_if(v.begin(), v.end(), pred), v.end());`) or C++20 `std::erase_if(v, pred)`; if you must erase in a loop, use the iterator returned by `erase`.",
"""`std::remove_if` moves the kept elements to the front and returns the new logical end; `erase` then truncates. This is O(n) overall, versus O(n²) for erasing elements one by one.

Manual loop form: `for (auto it = v.begin(); it != v.end(); ) { if (pred(*it)) it = v.erase(it); else ++it; }`. Never increment an iterator after erasing it.

C++20 `std::erase(v, value)` and `std::erase_if` work for all standard containers.""",
"Calling `v.erase(it)` inside a range-for loop, or incrementing `it` after erasing it, which uses an invalidated iterator.",
["Why is erase-remove O(n) while erasing in a loop is O(n²)? => `remove_if` shifts each element once; repeated `erase` shifts the tail each time.",
 "What does `std::remove_if` return? => An iterator to the new logical end; elements after it are in a valid but unspecified state."]),

220: D("`std::string` is a class managing a dynamically sized, null-terminated sequence of characters with automatic memory management; a C-style string is a `char` array or pointer terminated by `'\\0'`, with manual memory and length handling.",
"""`std::string` knows its length (O(1) `size()`), grows automatically, can contain embedded null characters, copies and compares by value, and cleans up automatically. `c_str()` provides a null-terminated `const char*` for C APIs.

C strings require manual buffer sizing (source of overflows), `strlen` is O(n), and ownership is unclear. Use `std::string_view` for read-only non-owning parameters.""",
"Keeping the pointer from `s.c_str()` after modifying or destroying `s`; it dangles.",
["Can `std::string` contain `'\\0'` characters? => Yes; its length is tracked separately, though `c_str()` users will stop at the first null.",
 "When should a parameter be `std::string_view`? => For read-only access to string data without needing ownership or null termination."]),

221: D("`push_back` takes an existing object (copying or moving it into the container); `emplace_back` constructs the element in place from constructor arguments, avoiding a temporary.",
"""`v.emplace_back(\"dev\", 4096)` constructs `Device(\"dev\", 4096)` directly in the vector's storage. With an existing object, `push_back(std::move(x))` and `emplace_back(std::move(x))` are equivalent.

Caveat: `emplace_back` can call **explicit** constructors, so `std::vector<std::unique_ptr<T>> v; v.emplace_back(rawPtr);` compiles and takes ownership silently, whereas `push_back(rawPtr)` wouldn't compile. Since C++17, `emplace_back` returns a reference to the new element.""",
"Using `emplace_back` everywhere by habit; it can invoke explicit constructors unexpectedly. Use `push_back` for existing objects and `emplace_back` when constructing.",
["When does `emplace_back` give a real benefit? => When constructing from arguments, avoiding a temporary that would then be moved.",
 "What does `emplace_back` return since C++17? => A reference to the inserted element."]),

222: D("`std::priority_queue` is a container adaptor that always gives access to the largest element (by default, using `std::less` and a max-heap over a `std::vector`).",
"""`push` and `pop` are O(log n), `top` is O(1). For a min-heap use `std::priority_queue<T, std::vector<T>, std::greater<T>>` or a custom comparator.

It doesn't support decrease-key or iteration; for algorithms like Dijkstra, push duplicates and skip stale entries, or use `std::set` as an updatable priority queue. The heap algorithms (`std::make_heap`, `push_heap`, `pop_heap`) work directly on vectors if you need more control.""",
"Expecting the smallest element on top with the default comparator; the default is a max-heap.",
["How do you make a min-heap? => Use `std::greater<T>` as the comparator.",
 "How do you handle decrease-key in Dijkstra with `priority_queue`? => Push a new entry and ignore outdated ones when they're popped."]),

223: D("`std::unordered_map` needs a hash function to choose a bucket for each key and `operator==` (or a key-equality predicate) to distinguish different keys within the same bucket.",
"""Hash collisions are unavoidable, so equality decides whether a key already exists. The two must be consistent: keys that compare equal must produce equal hashes, otherwise duplicates appear and lookups fail.

For custom keys, specialize `std::hash<Key>` or pass a hasher type, and combine member hashes well (e.g. boost-style `hash_combine`). Hash quality matters: poor hashes cluster keys in few buckets, degrading to O(n).""",
"Defining `operator==` on some fields but hashing all fields (or vice versa), breaking the equal-keys-equal-hashes contract.",
["What happens if equal keys have different hashes? => They land in different buckets, so lookups miss and duplicates are inserted.",
 "How do you hash a struct with several fields? => Combine field hashes with a mixing function (like `hash_combine`), or hash a tuple of the fields."]),

224: D("Iterator invalidation means iterators, pointers or references become unusable after a container modification; the rules depend on how each container stores elements.",
"""Summary:

- `vector`/`string`: reallocation invalidates everything; insert/erase invalidates at and after the position.
- `deque`: insertion in the middle invalidates everything; at the ends invalidates iterators but not references.
- `list`/`forward_list`/`set`/`map`: only erased elements' iterators are invalidated (node-based).
- `unordered_*`: rehashing invalidates iterators but not references or pointers to elements; erase invalidates only the erased element.

Consult cppreference's invalidation table when writing loops that modify containers.""",
"Holding a pointer to an `unordered_map` value and assuming iterators stay valid after inserts; rehashing invalidates iterators (though pointers to elements survive).",
["Which containers keep references valid across insertion? => Node-based ones (`list`, `set`, `map`, unordered containers for references).",
 "Does erasing from a `std::map` invalidate other iterators? => No, only the erased element's iterators."]),

225: D("`std::map::find` is O(log n) (tree search); `std::unordered_map::find` is O(1) on average but O(n) in the worst case (many keys in one bucket).",
"""Average vs worst case matters when keys come from untrusted input: crafted keys can collide deliberately (hash flooding), making lookups linear. Randomized or keyed hashes mitigate this.

Constant factors also matter: hashing a long string key may cost more than a few comparisons in a small map, and tree nodes vs hash buckets both involve pointer chasing. Benchmark with real data.""",
"Assuming `unordered_map` is always faster; for small maps or expensive hashes, `map` or a sorted vector can be quicker.",
["What is hash flooding? => An attack using keys that collide in the same bucket to force O(n) lookups.",
 "When can `std::map` beat `unordered_map`? => Small sizes, expensive hashing, or when ordered iteration is also needed."]),

226: D("`std::move` doesn't move anything: it's a cast to an rvalue reference (`static_cast<T&&>`) that makes an object eligible for a move constructor or move assignment, which do the actual transfer.",
"""If the type has no move constructor, `std::move` results in a copy (the rvalue binds to `const T&`). Moving a `const` object also copies, since `const T&&` can't bind to the move constructor's `T&&`.

The real move (stealing a heap buffer, nulling the source pointer) is implemented by the class's move operations. After a move, the source is in a valid but unspecified state.""",
"Writing `std::move(constObj)` and expecting a cheap move; const objects are copied.",
["Why does moving a const object copy? => `const T&&` can't bind to `T&&`, so overload resolution chooses the copy constructor.",
 "Is `std::move` free at runtime? => Yes, it's just a cast; the cost is in the move constructor or assignment that follows."]),

227: D("`std::span<T>` (C++20) is a non-owning view over a contiguous sequence of elements (pointer plus length), usable for arrays, vectors, `std::array` and raw buffers alike.",
"""It replaces `(T* data, size_t n)` parameter pairs: `void checksum(std::span<const std::byte> data)` accepts any contiguous buffer, knows its size, and offers `subspan`, `first`, `last` without copying.

Spans can have a static extent (`std::span<int, 4>`) or dynamic extent. They don't own data, so they must not outlive the buffer; like other views, they're cheap to pass by value. Note `std::span::operator[]` doesn't check bounds (C++26 adds `at()`).""",
"Returning a `std::span` into a local vector, or keeping a span after the vector reallocates.",
["Why pass a span by value? => It's two words (pointer and size), cheap to copy, like `string_view`.",
 "How do you view a struct as bytes? => `std::as_bytes(std::span{&obj, 1})` gives `std::span<const std::byte>`."]),

228: D("`std::sort` guarantees O(n log n) comparisons (since C++11) and is typically implemented as **introsort**: quicksort, switching to heapsort if recursion gets too deep, and insertion sort for small partitions.",
"""Quicksort is fast on average but O(n²) in the worst case; tracking recursion depth and falling back to heapsort bounds the worst case at O(n log n). Insertion sort finishes small subranges efficiently. libc++ and libstdc++ both use variations; some newer implementations use pattern-defeating quicksort (pdqsort) ideas.

`std::sort` is not stable and requires random-access iterators and a strict weak ordering comparator.""",
"Passing a comparator that isn't a strict weak ordering (e.g. using `<=`), which can make `std::sort` read out of bounds and crash.",
["Why does introsort switch to heapsort? => To guarantee O(n log n) when quicksort's partitioning degenerates.",
 "Is `std::sort` stable? => No; use `std::stable_sort` if equal elements must keep their order."]),

229: D("`std::stable_sort` preserves the relative order of equal elements; `std::sort` doesn't.",
"""Stability matters when sorting by one key after another (sort by name, then stable-sort by department to get departments with names ordered within), or when equal elements carry other data whose order is meaningful (timestamps of log entries with equal priority).

`stable_sort` is typically a merge sort: O(n log n) with extra O(n) memory, or O(n log² n) if memory can't be allocated. It's usually somewhat slower than `std::sort`.""",
"Sorting records by a secondary key and then by a primary key with `std::sort`, losing the secondary order.",
["How does `stable_sort` behave without extra memory? => It falls back to an in-place algorithm with O(n log² n) complexity.",
 "How do you sort by multiple keys in one pass? => Use a comparator that compares tuples of keys (`std::tie`)."]),

230: D("`std::vector<bool>` is a space-optimized specialization that packs bits (1 bit per element) instead of storing `bool` objects, so it isn't a real container of `bool`.",
"""Consequences: `operator[]` returns a proxy object, not `bool&`; you can't take `&v[0]` or get a `bool*`; `auto x = v[0];` captures a proxy; generic code expecting `T&` breaks; and concurrent writes to different elements race because they may share a byte.

Alternatives: `std::vector<char>` or `std::vector<std::uint8_t>` for a real container, `std::bitset<N>` for fixed-size bit sets, or `boost::dynamic_bitset` for dynamic ones.""",
"Writing a template that takes `std::vector<T>&` and returns `T&` from it; it fails for `T = bool`, whose `operator[]` returns a proxy.",
["Why can't two threads safely write different elements of `vector<bool>`? => Elements share storage words, so writes are read-modify-write of the same memory.",
 "What should you use instead? => `std::vector<char>`, `std::bitset`, or `boost::dynamic_bitset`."]),

231: D("`std::initializer_list<T>` is a lightweight view over a compiler-created array of const elements, used for brace-initialization like `std::vector<int> v{1, 2, 3};`; brace initialization strongly prefers constructors taking an `initializer_list`.",
"""The famous surprise: `std::vector<int> a(3, 0);` creates three zeros, but `std::vector<int> b{3, 0};` creates two elements, 3 and 0, because the `initializer_list` constructor wins overload resolution whenever it's viable.

Elements are const and copied into the container (can't move from them, so `std::vector<std::unique_ptr<T>>{...}` with `initializer_list` doesn't compile). The underlying array lives only as long as the `initializer_list` object in most contexts, so don't store it.""",
"Writing `std::vector<int> v{n}` expecting `n` elements; you get one element with value `n`.",
["Why doesn't `vector<unique_ptr<T>>{make_unique<T>()}` compile? => `initializer_list` elements are const, so they can only be copied, and `unique_ptr` isn't copyable.",
 "How do you choose the non-initializer-list constructor? => Use parentheses: `std::vector<int>(3, 0)`."]),

232: D("`std::multimap<K, V>` stores each key-value pair as a separate node with duplicate keys allowed; `std::map<K, std::vector<V>>` stores one node per key with all values grouped in a vector.",
"""`map<K, vector<V>>` is usually more convenient and faster to iterate per key (values contiguous, one tree node per key) and makes \"all values for key\" a direct lookup. `multimap` keeps insertion order among equal keys, supports erasing individual pairs by iterator cheaply, and avoids a vector per key when most keys have one value.

Choose based on access pattern; for grouping and batch processing, map-of-vectors typically wins.""",
"Using `multimap` and then repeatedly calling `equal_range` to process groups, when a map of vectors would give direct access and better locality.",
["How do you get all values for a key in a multimap? => `equal_range(key)` returns the range of matching pairs.",
 "Does multimap keep insertion order among equal keys? => Yes, since C++11 equal keys keep insertion order."]),

233: D("The standard specifies complexity guarantees for algorithms (usually as a maximum number of operations such as comparisons or applications of a function), and algorithms like `std::for_each` and `std::transform` apply their function exactly once per element in the range.",
"""Examples: `std::sort` O(n log n) comparisons; `std::find` at most n comparisons; `std::nth_element` O(n) on average; `std::for_each` exactly n applications. These guarantees make performance predictable across implementations.

`std::for_each` guarantees in-order application (it returns the function object); `std::transform` doesn't guarantee order of application (so functions shouldn't rely on sequencing side effects). The parallel overloads (C++17 execution policies) relax ordering further.""",
"Passing a stateful function with side effects to `std::transform` and relying on the order of application.",
["Does `std::transform` guarantee left-to-right application? => No; only `std::for_each` (sequential) guarantees order.",
 "What complexity does `std::nth_element` have? => Linear on average."]),

234: D("`std::any` (C++17) holds a single value of **any** copyable type, checked at runtime with `std::any_cast`; `std::variant<Ts...>` holds a value of one of a **fixed set** of types, checked at compile time and accessed with `std::visit`, `std::get` or `std::get_if`.",
"""`variant` is a type-safe union: no heap allocation, size equals the largest alternative plus a discriminator, and `std::visit` enforces handling of every alternative. It's ideal for closed sets (messages, AST nodes, results).

`any` is a type-erased container: flexible (plugin data, heterogeneous property bags), but requires knowing the type to extract, may allocate for large types, and errors surface only at runtime (`std::bad_any_cast`).""",
"Using `std::any` where the set of types is known; `std::variant` gives compile-time checking and better performance.",
["What happens when `std::get<T>` is used on a variant holding another type? => It throws `std::bad_variant_access`.",
 "Does `std::any` allocate? => Possibly; implementations use a small-buffer optimization for small types and allocate for larger ones."]),

235: D("`std::optional<T>` (C++17) represents a value that may or may not be present, storing it inline without heap allocation, instead of using sentinel values, null pointers or out-parameters.",
"""Typical use: return types for lookups or parsing that can fail (`std::optional<int> parsePort(std::string_view)`). Access with `has_value()` / `if (opt)`, `*opt` (unchecked), `value()` (throws `std::bad_optional_access`), or `value_or(default)`. C++23 adds monadic operations `and_then`, `transform`, `or_else`.

For failures that need a reason, C++23's `std::expected<T, E>` carries either a value or an error.""",
"Dereferencing an empty optional with `*opt` (undefined behaviour) instead of checking or using `value_or`.",
["When would you use `std::expected` instead of `std::optional`? => When callers need to know why the operation failed.",
 "Does `std::optional` allocate memory? => No, the value is stored inside the optional object."]),

236: D("`erase` removes the specified elements and `clear` removes all elements; neither reduces `capacity()`, so the allocated memory stays until `shrink_to_fit()`, a swap, or destruction.",
"""This is intentional: keeping capacity makes refilling the vector cheap. Destructors of the removed elements do run.

To actually free memory: `v.clear(); v.shrink_to_fit();` (non-binding but honoured by major implementations) or `std::vector<T>().swap(v);` (guaranteed).""",
"Clearing a large buffer vector in a long-running process and assuming memory usage drops.",
["Does `clear()` call element destructors? => Yes, it destroys all elements but keeps the storage.",
 "How do you guarantee releasing a vector's memory? => Swap it with an empty temporary: `std::vector<T>().swap(v);`."]),

237: D("`std::list::sort` is a member function because the generic `std::sort` requires random-access iterators, which linked lists can't provide efficiently; the member version sorts by relinking nodes (typically merge sort) in O(n log n).",
"""Relinking nodes also means no elements are copied or moved and iterators and references remain valid, which a generic algorithm couldn't guarantee.

The same reasoning applies to `list::merge`, `list::remove`, `list::unique` and `list::reverse`: members exploit the node structure. For associative containers, member `find`, `count` and `lower_bound` exist for the same reason.""",
"Copying a list into a vector to sort it and back, when `lst.sort()` sorts in place without moving elements.",
["Does `list::sort` invalidate iterators? => No; nodes are relinked, so iterators and references stay valid.",
 "Why do associative containers have member `find`? => It uses the tree or hash structure (O(log n) or O(1)) instead of a linear scan."]),

238: D("A hint iterator passed to `std::map::insert(hint, value)` (or `emplace_hint`) tells the container where the new element probably belongs; if correct, insertion is amortized O(1) instead of O(log n).",
"""The hint should be the position just after where the element will go (C++11 semantics). The classic use is inserting already-sorted data: pass `end()` (or the iterator returned by the previous insert) so each insertion is constant time.

A wrong hint is harmless for correctness; the container falls back to a normal search.""",
"Passing `begin()` as the hint while inserting ascending keys; the hint is wrong every time, so there's no speedup.",
["What hint should you use when inserting sorted keys in ascending order? => `end()` (or the result of the previous insert).",
 "What happens with a bad hint? => Insertion still works correctly, just at normal O(log n) cost."]),

239: D("The bucket count is the number of hash buckets; the load factor is the average number of elements per bucket (`size() / bucket_count()`); when it would exceed `max_load_factor()` (default 1.0), the container rehashes into more buckets.",
"""Rehashing costs O(n) and invalidates iterators (not references). Lower load factors mean fewer collisions and faster lookups but more memory.

Tune with `reserve(n)` (enough buckets for n elements without rehashing), `rehash(buckets)`, and `max_load_factor(f)`. Reserving up front avoids repeated rehashing when bulk-loading a map.""",
"Bulk-inserting millions of entries into an `unordered_map` without `reserve`, causing many O(n) rehashes along the way.",
["What does `unordered_map::reserve(n)` do? => Sets the bucket count so `n` elements fit without exceeding the max load factor.",
 "What does rehashing invalidate? => Iterators, but not pointers or references to elements."]),

240: D("C++20 ranges provide algorithms that take whole ranges (`std::ranges::sort(v)`), support projections, use concepts for clearer errors, and add lazy, composable **views** (`std::views::filter`, `transform`, `take`) combined with `|`.",
"""Example: `for (int x : readings | std::views::filter(isValid) | std::views::transform(toCelsius) | std::views::take(10))` processes lazily without temporary vectors.

Projections: `std::ranges::sort(devices, {}, &Device::temperature)` sorts by a member without writing a comparator lambda. Algorithms return richer results (e.g. iterator plus sentinel), and sentinels allow ranges without a real end iterator.

C++23 adds more views (`zip`, `enumerate`, `chunk`, `slide`) and `std::ranges::to` to materialize views into containers.""",
"Storing a view that refers to a temporary container (`auto v = getVec() | views::filter(f);`), which dangles.",
["What is a projection? => A function applied to each element before the comparison or predicate, e.g. sorting by a member.",
 "How do you turn a view into a vector in C++23? => `std::ranges::to<std::vector>()`."]),

241: D("`std::unique` removes **consecutive** duplicate elements by shifting later unique elements forward and returns the new logical end; it only removes all duplicates if equal elements are adjacent, which sorting guarantees.",
"""Pattern: `std::sort(v.begin(), v.end()); v.erase(std::unique(v.begin(), v.end()), v.end());`. Like `remove`, `unique` doesn't change the container's size; you must `erase` the tail.

If order must be preserved, use a seen-set approach or `std::unordered_set` to filter while keeping the first occurrence.""",
"Calling `std::unique` without sorting and without `erase`, then being surprised that duplicates remain and the vector size is unchanged.",
["Why doesn't `std::unique` shrink the vector? => Algorithms work on iterators and can't change a container's size; use `erase`.",
 "How do you dedupe while keeping original order? => Track seen values in a set and keep only first occurrences."]),

242: D("`std::accumulate` folds a range into a single value using an initial value and a binary operation (default `+`), expressing sums, products, concatenations and other reductions generically.",
"""Pitfalls: the result type is the type of the **initial value**, so `std::accumulate(v.begin(), v.end(), 0)` on doubles truncates to int; use `0.0`. It's strictly left-to-right and sequential.

`std::reduce` (C++17) allows reordering and parallel execution (with an associative, commutative operation), and `std::transform_reduce` combines mapping and reduction. C++23 adds `std::ranges::fold_left`.""",
"Summing doubles with an initial value of `0` (an int), silently truncating the result.",
["What decides `accumulate`'s result type? => The type of the initial value argument.",
 "How does `std::reduce` differ? => It may reorder operations and run in parallel, so the operation should be associative and commutative."]),

243: D("Inserting into the middle of a `std::vector` is O(n) because all elements after the position must shift by one (and a reallocation may copy everything); inserting at the end is amortized O(1) because nothing needs to shift.",
"""Middle insertion calls move assignments or moves for each subsequent element; for large vectors of expensive-to-move elements, this dominates. Still, contiguous shifting is fast in practice (memmove-like for trivially copyable types), so vectors often beat linked lists even with some middle insertions.

If you insert many elements in the middle, batch them: append then `std::sort`, or build a new vector, rather than inserting one by one.""",
"Inserting elements one by one at the front of a large vector in a loop, turning the whole operation into O(n²).",
["How do you insert many elements efficiently? => Insert a whole range at once (`v.insert(pos, first, last)`) or append and sort.",
 "Why can vector still beat list for middle insertions? => Shifting contiguous memory is cache-friendly, while finding a position in a list is slow."]),

244: D("`std::forward_list` (C++11) is a singly linked list with minimal overhead (one pointer per node, no size member), while `std::list` is doubly linked with bidirectional iteration and O(1) `size()`.",
"""Because nodes only know their successor, `forward_list` operations are expressed \"after\" a position: `insert_after`, `erase_after`, `emplace_after`, and `before_begin()` for inserting at the front. It has no `push_back` or `size()`.

It's meant to match a hand-written C singly linked list in space and speed. Use it only when the memory savings matter; otherwise `std::vector` (or `list` for stable iterators) is simpler.""",
"Trying to erase the current element of a `forward_list` while iterating with a single iterator; you must track the previous position and use `erase_after`.",
["Why doesn't `forward_list` have `size()`? => Maintaining a size would add space and time overhead that the container is designed to avoid.",
 "What is `before_begin()` for? => A position before the first element, allowing `insert_after` and `erase_after` at the front."]),

245: D("Separating algorithms from containers through iterators lets each algorithm be written once and work with every container (and arrays, streams, custom types), reducing N x M implementations to N + M.",
"""This is **generic programming** as designed by Alexander Stepanov: algorithms specify requirements on iterators (concepts), containers provide iterators meeting them, and the compiler generates efficient specialized code through templates.

Benefits: reuse, consistency, and zero abstraction cost. Your own containers gain the whole algorithm library by providing standard-conforming iterators. C++20 concepts and ranges make the requirements explicit and errors readable.""",
"Implementing custom containers without standard iterators, forcing users to write manual loops instead of using `std::` algorithms.",
["What must a custom container provide to use STL algorithms? => Iterators meeting the relevant category requirements, via `begin()` and `end()`.",
 "Who designed the STL's generic approach? => Alexander Stepanov (with Meng Lee), based on generic programming principles."]),
}
