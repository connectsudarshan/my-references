DEEP = {

171: D("A typical C++ process has a text segment (code), read-only data (constants, string literals), initialized data (`.data`), zero-initialized data (`.bss`), the heap (dynamic allocations) and one stack per thread.",
"""- **Text**: machine code, read-only and shareable between processes.
- **Rodata**: string literals, `const` tables, vtables.
- **Data / BSS**: globals and statics; `.bss` holds zero-initialized ones and takes no space in the executable file.
- **Heap**: memory from `operator new`/`malloc`, managed by the allocator; grows as needed.
- **Stack**: function frames (locals, return addresses, saved registers), fixed size per thread (often 1-8 MB on desktops, a few KB on microcontrollers).

Also present: memory-mapped files, shared libraries and thread-local storage. In firmware, the linker script defines where each section lives (flash vs RAM).""",
"Modifying a string literal through a `char*` cast; it lives in read-only memory and the write crashes or is undefined behaviour.",
["Why does `.bss` not take space in the binary? => It's only recorded as a size; the loader zero-fills it at startup.",
 "Where do vtables live? => Usually in read-only data."]),

172: D("Stack memory holds automatic (local) variables in frames that are pushed and popped with function calls; heap memory holds dynamically allocated objects whose lifetime is controlled explicitly or by owners like smart pointers.",
"""Stack: allocation is just moving the stack pointer (nearly free), memory is cache-hot, lifetime is tied to scope, size is limited and fixed per thread.

Heap: allocation goes through an allocator (locks or thread caches, bookkeeping), objects can outlive the function and be any size, but it risks fragmentation, leaks and use-after-free.

Guideline: prefer stack (or member) objects; use heap allocation for large data, data with dynamic lifetime or size, and polymorphic objects. Containers allocate their elements on the heap even when the container object itself is on the stack.""",
"Placing large arrays (e.g. `char buf[8 * 1024 * 1024];`) on the stack, which overflows threads with small stacks.",
["Why is stack allocation so fast? => It's a pointer adjustment with no bookkeeping, and the memory is usually already in cache.",
 "Where are a `std::vector`'s elements stored if the vector is a local? => On the heap; only the small vector object (pointers) is on the stack."]),

173: D("A memory leak is dynamically allocated memory that is no longer reachable (or no longer needed) but is never freed, so the process's memory usage grows.",
"""Causes: raw `new` without matching `delete` (especially on early returns and exceptions), reference cycles of `shared_ptr`, unbounded caches, containers that keep growing, and callbacks registered and never removed.

Effects matter most for long-running processes (services, test orchestrators, firmware that runs for months): gradual growth leads to out-of-memory failures.

Prevention: RAII and smart pointers, clear ownership, bounded caches; detection with LeakSanitizer, Valgrind, heap profilers (heaptrack, massif), and trend monitoring of process memory.""",
"Calling `new` and then `return` early on an error path before `delete`; RAII avoids having to remember every path.",
["Can a garbage-collected program leak memory? => Yes, when objects remain reachable but unused (unbounded caches, listeners), the same as with `shared_ptr` holding references.",
 "Why do leaks matter less in short-lived tools? => The OS reclaims everything at process exit, though leaks still hide real bugs."]),

174: D("`new T` allocates and constructs one object; `new T[n]` allocates an array of `n` objects, constructing each, and must be released with `delete[]`.",
"""For arrays of types with non-trivial destructors, `new[]` typically stores the element count in a hidden header before the array so `delete[]` knows how many destructors to call.

Modern C++ rarely needs `new[]`: use `std::vector<T>` for dynamic arrays, `std::array` for fixed sizes, and `std::make_unique<T[]>(n)` when you need a heap array with unique ownership.""",
"Using `new T[n]` and releasing with `delete`, or storing it in `std::unique_ptr<T>` instead of `std::unique_ptr<T[]>`.",
["Where does `delete[]` get the element count? => Typically from a hidden cookie stored just before the array by `new[]`.",
 "What's the smart-pointer form for arrays? => `std::unique_ptr<T[]>` created with `std::make_unique<T[]>(n)`."]),

175: D("Using `delete` on memory from `new[]` is undefined behaviour: typically only the first element's destructor runs and the wrong pointer (not the start of the allocation with its count header) is passed to the deallocator, corrupting the heap.",
"""For trivial types it may appear to work on some implementations, which hides the bug until the type gains a destructor or the allocator changes.

Rule: match `new`/`delete`, `new[]`/`delete[]`, `malloc`/`free`. Tools like AddressSanitizer report \"alloc-dealloc-mismatch\". The real fix is to avoid manual arrays altogether.""",
"Assuming the mismatch is harmless because the element type is `char` or `int`; it's still undefined behaviour and tooling will flag it.",
["What does AddressSanitizer report for this bug? => alloc-dealloc-mismatch (operator new[] vs operator delete).",
 "How do you avoid the issue entirely? => Use `std::vector` or `std::unique_ptr<T[]>`."]),

176: D("A dangling pointer refers to an object whose lifetime has ended; you avoid creating one by making ownership and lifetimes explicit so no observer outlives the object it points to.",
"""Common creators: deleting through one pointer while others remain, returning addresses of locals, pointers or iterators into containers that reallocate, `string_view`/`span` of temporaries, lambdas capturing locals by reference that run later.

Avoidance techniques: single owner (`unique_ptr`) with clearly scoped observers; `weak_ptr` for observers of shared objects; indices or handles (generation-checked IDs) instead of raw pointers into pools; don't store views beyond the statement unless the source clearly outlives them; and rely on AddressSanitizer in tests.""",
"Capturing local variables by reference (`[&]`) in a callback or thread that runs after the function returns.",
["What's a generational handle? => An index plus a generation counter; stale handles are detected because the slot's generation changed.",
 "Why are views like `string_view` risky? => They don't own data, so they dangle if the source is destroyed or modified."]),

177: D("RAII (Resource Acquisition Is Initialization) ties a resource's lifetime to an object's lifetime: the constructor acquires the resource and the destructor releases it, so cleanup happens automatically when the object goes out of scope.",
"""Because destructors run on normal scope exit, early returns and exceptions (stack unwinding), RAII gives leak-free and exception-safe code without explicit cleanup paths.

Standard RAII types: `std::unique_ptr`, `std::vector`, `std::fstream`, `std::lock_guard`/`std::scoped_lock`, `std::jthread`. For custom resources (file descriptors, DMA buffers, device handles), write a small move-only wrapper, or use `std::unique_ptr` with a custom deleter.

It's the foundation of modern C++ and the reason C++ doesn't need `finally` blocks.""",
"Manually pairing `lock()`/`unlock()` calls: an exception or early return between them leaves the mutex locked forever. Use `std::lock_guard`.",
["How do you wrap a C handle with RAII quickly? => `std::unique_ptr<FILE, decltype(&fclose)> f(fopen(...), &fclose);` or a small wrapper class.",
 "Why doesn't C++ need `finally`? => Destructors of local RAII objects run during unwinding, providing the same guarantee."]),

178: D("A double free is releasing the same allocation twice; it corrupts the allocator's internal structures and is undefined behaviour, often exploitable as a security vulnerability.",
"""After the first free, the block may be reused; the second free can insert it twice into free lists, so two later allocations receive the same memory, letting an attacker overwrite live objects.

Typical causes: shallow copies of classes owning raw pointers (Rule of Three violations), two `shared_ptr`s created from the same raw pointer, and error paths that free and then fall through to common cleanup.

Detection: AddressSanitizer (\"attempting double-free\"), glibc's `free(): double free detected` abort; prevention via single ownership and smart pointers.""",
"Copying an object that owns a raw buffer with the default copy constructor; both destructors free the same buffer.",
["Why is double free a security issue? => It corrupts allocator metadata, which attackers can turn into arbitrary memory writes.",
 "How can two `shared_ptr` cause a double free? => Constructing both from the same raw pointer creates two independent control blocks."]),

179: D("A memory pool (or custom allocator) pre-allocates a large block and hands out pieces of it itself, avoiding general-purpose heap allocation for specific workloads.",
"""Reasons: deterministic timing (real-time and firmware code can't tolerate `malloc` latency spikes), speed (bump or free-list allocation is a few instructions), reduced fragmentation, better cache locality, and easy bulk release (reset an arena after each frame or request).

Kinds: fixed-size pools (free list of equal blocks), arenas/monotonic buffers (bump pointer, free everything at once), and slab allocators. The standard library offers `std::pmr::monotonic_buffer_resource`, `unsynchronized_pool_resource` and `synchronized_pool_resource` (C++17), usable with `std::pmr::vector` and friends.""",
"Writing a custom allocator before measuring; general-purpose allocators (glibc, jemalloc, mimalloc) are very good, and custom pools add complexity and bugs.",
["What does `std::pmr::monotonic_buffer_resource` do? => Bump-allocates from a buffer and frees everything only when the resource is destroyed.",
 "Why do real-time systems avoid `malloc` at runtime? => Its latency is unbounded and it may lock, so they allocate up front or use pools."]),

180: D("Heap fragmentation is when free memory is split into many small non-contiguous blocks, so a large allocation can fail (or grow the heap) even though enough total memory is free.",
"""External fragmentation comes from interleaving allocations of different sizes and lifetimes; internal fragmentation is wasted space inside allocated blocks due to rounding and alignment.

It hurts long-running and memory-constrained systems (embedded devices, servers running for months): memory usage creeps up without a leak.

Mitigations: allocate up front, use pools for same-sized objects, group allocations with similar lifetimes (arenas), reserve container capacity, and prefer modern allocators (jemalloc, mimalloc, tcmalloc) that segregate size classes.""",
"Diagnosing growing memory as a leak when it's fragmentation; heap profilers show freed but unusable memory, and pooled allocation is the fix rather than hunting leaks.",
["External vs internal fragmentation? => External: free space split into unusable pieces between blocks. Internal: unused space inside allocated blocks.",
 "How do arenas reduce fragmentation? => Objects with the same lifetime are allocated together and freed together."]),

181: D("`malloc(n)` allocates `n` uninitialized bytes; `calloc(count, size)` allocates and zero-fills `count*size` bytes (checking multiplication overflow); `realloc(p, n)` resizes a block, possibly moving it; `free(p)` releases memory from any of them.",
"""All return `void*` and signal failure with null (never throw). They don't run constructors or destructors, so in C++ they're only suitable for trivially copyable data or C interop.

`realloc` pitfalls: on failure it returns null and leaves the original block alive, so `p = realloc(p, n)` leaks on failure; and it copies bytes, which is wrong for non-trivially copyable C++ objects. `std::vector` handles growth correctly with moves.""",
"Writing `p = realloc(p, n);` without keeping the old pointer: if `realloc` fails, the original block leaks.",
["Why is `calloc` safer than `malloc(count * size)`? => It checks for multiplication overflow and zero-initializes memory.",
 "Can you `realloc` memory holding `std::string` objects? => No; byte-wise moves break non-trivially copyable objects."]),

182: D("`malloc`/`free` and `new`/`delete` are different allocation systems: releasing memory with the wrong one is undefined behaviour, and `malloc` never runs constructors while `free` never runs destructors.",
"""`new` may use a different heap, add headers (for arrays), or be replaced by the program; `free` on such memory corrupts heaps. Similarly, `delete` on `malloc` memory calls a destructor on an object that was never constructed.

Keep each allocation's allocate/release pair together, ideally wrapped in RAII (`std::unique_ptr` with a `free` deleter for C-allocated buffers returned by C libraries).""",
"Freeing a buffer returned by a C library with `delete`, or passing `new`-allocated memory to a C function that calls `free` on it.",
["How do you own memory returned by `malloc` from a C API? => `std::unique_ptr<char, decltype(&std::free)> p(ptr, &std::free);`.",
 "Can `operator new` be implemented with `malloc`? => Yes, commonly, but that's an internal detail; you still must release with `delete`."]),

183: D("A stack overflow happens when a thread uses more stack than it was given, typically through deep or unbounded recursion or very large local variables.",
"""Symptoms: segmentation fault or access violation at a seemingly random point, often in a function prologue; on microcontrollers, silent corruption of adjacent memory unless there's a stack guard or MPU region.

Causes: recursion without a proper base case, recursion depth proportional to input size (deep trees, recursive descent on large input), large arrays or structs on the stack, `alloca`/VLAs, and small default stacks for worker threads.

Fixes: iterative algorithms with an explicit container, moving large buffers to the heap or static storage, increasing thread stack size where appropriate, and compiler warnings like `-Wstack-usage=N` / `-Wframe-larger-than=N`.""",
"Recursive tree traversal on a degenerate (linked-list-shaped) tree of a million nodes, which overflows the stack; use an explicit stack.",
["How do you find functions with large stack frames? => GCC's `-fstack-usage` and `-Wframe-larger-than=N`.",
 "How is stack overflow detected on microcontrollers? => Stack canaries/painting, MPU guard regions, or high-water-mark checks."]),

184: D("Automatic storage duration lasts until the end of the enclosing block (locals); dynamic storage duration lasts from `new` until `delete` (or until the owning smart pointer releases it); static storage duration lasts for the whole program (globals, `static` locals and members).",
"""A fourth kind, **thread** storage duration (`thread_local`), lasts for the lifetime of a thread.

Static objects are zero- or constant-initialized before any code runs, then dynamically initialized before `main` (namespace scope) or on first use (function-local statics, thread-safely). They are destroyed after `main` returns, in reverse order of construction.

Storage duration is about when memory exists; object lifetime (between constructor completion and destructor start) is related but narrower.""",
"Global objects whose destructors use other globals from different translation units; destruction order across units is unspecified, so shutdown crashes.",
["When are function-local statics initialized? => The first time control passes through their declaration, thread-safely since C++11.",
 "What is the difference between storage duration and lifetime? => Storage duration is how long the memory exists; lifetime is when a constructed object occupies it."]),

185: D("Common leak-detection tools are LeakSanitizer/AddressSanitizer, Valgrind Memcheck, heap profilers (heaptrack, Massif, Instruments, Visual Studio diagnostics), and the MSVC CRT debug heap.",
"""- **AddressSanitizer + LeakSanitizer** (`-fsanitize=address`): fast (about 2x slowdown), reports leaks at exit with allocation stack traces; ideal in CI.
- **Valgrind Memcheck**: no recompilation needed, very thorough (also uninitialized reads), but 20-50x slower; Linux mainly.
- **Heap profilers**: heaptrack, Massif, jemalloc/tcmalloc profiling show where memory grows over time (\"leaks\" that are still reachable).
- **Windows**: CRT debug heap (`_CrtDumpMemoryLeaks`), Visual Studio diagnostic tools, UMDH.

Complement tools with design: RAII and ownership rules prevent most leaks.""",
"Running leak checks only on short unit tests; many leaks appear only in long-running paths, so also monitor memory trends in soak tests.",
["ASan vs Valgrind? => ASan needs recompilation and is much faster; Valgrind works on existing binaries but is far slower.",
 "How do you find growth that isn't technically a leak? => Heap profilers over time (heaptrack, Massif) to see which call sites keep reachable memory growing."]),

186: D("Regular `new` allocates memory **and** constructs an object; placement new (`new (address) T(args)`) only constructs an object in memory you supply, without allocating.",
"""Use cases: containers that manage capacity separately from elements (`std::vector`), object pools and arenas, fixed buffers in embedded systems without a heap, `std::optional`/`std::variant` implementations that construct in internal storage, and objects in shared or memory-mapped regions.

Requirements: suitable size and alignment, and manual destruction (`p->~T()` or `std::destroy_at(p)`). C++20 `std::construct_at` offers a safer, constexpr-friendly form.""",
"Reusing a placement-new buffer for a new object without destroying the previous one first, skipping its destructor and possibly leaking resources.",
["Does placement new ever throw? => The allocation can't fail, but the constructor can still throw.",
 "Which standard types use placement new internally? => `std::vector`, `std::optional`, `std::variant` and other containers managing raw storage."]),

187: D("Call the destructor explicitly on the object (`p->~T();` or `std::destroy_at(p);`), which ends its lifetime but leaves the memory allocated; you then reuse or free the storage separately.",
"""Typical sequence: `void* mem = pool.allocate(sizeof(T), alignof(T)); T* p = new (mem) T(args); ... p->~T(); pool.deallocate(mem);`.

For ranges use `std::destroy(first, last)` or `std::destroy_n`. Never call `delete` on a placement-new object unless the memory itself came from `new`, and never call the destructor explicitly on automatic objects (they'll be destroyed again).""",
"Calling `delete p` on an object placed in a static buffer; `delete` tries to release memory that was never heap-allocated.",
["What does `std::destroy_at` do? => Calls the object's destructor at the given address (C++17), handling arrays in C++20.",
 "Why is explicitly destroying an automatic object dangerous? => Its destructor runs again at scope exit, causing a double destruction."]),

188: D("Small object optimization stores small values inside the object itself instead of allocating on the heap; for `std::string` (SSO), short strings (typically up to 15 characters in libstdc++ and MSVC, 22 in libc++ on 64-bit) live in an internal buffer.",
"""Benefits: no heap allocation for common short strings, better cache locality, cheaper copies. The same idea appears in `std::function` and `std::any` (small callables stored inline) and in custom `SmallVector` types (LLVM, Boost.Container `small_vector`).

Consequences: moving a short string copies its characters (there's no heap pointer to steal), so moves of SSO strings aren't free; `sizeof(std::string)` is 24-32 bytes; `data()` pointers change when a string moves between SSO and heap mode.""",
"Assuming moving a `std::string` never copies characters; for short (SSO) strings, move copies the inline buffer.",
["Why is `sizeof(std::string)` 32 on some platforms? => It holds a pointer, size, and capacity or an inline SSO buffer.",
 "Which other standard types use small-buffer optimization? => `std::function` and `std::any` for small objects (implementation-dependent)."]),

189: D("A memory leak loses heap memory; a resource leak loses any limited resource (file descriptors, sockets, mutex locks, threads, GPU buffers, device handles) by failing to release it.",
"""Resource leaks often bite sooner than memory leaks: a process may hit the file-descriptor limit (commonly 1024) or leave a device locked long before running out of memory.

RAII solves both the same way: wrap every resource in an object whose destructor releases it (`std::fstream`, `std::lock_guard`, `std::jthread`, custom handles).

Detection: `lsof`/`/proc/<pid>/fd` for descriptors, handle counts on Windows, lock contention monitoring, and tests that check resource counts before and after.""",
"Closing files only on the success path, so each failed parse leaks a descriptor until the tool fails with \"too many open files\".",
["How do you detect file-descriptor leaks on Linux? => Count entries in `/proc/<pid>/fd` or use `lsof` during a long test.",
 "Is a locked-and-never-unlocked mutex a leak? => Yes, a resource leak that typically shows up as a deadlock."]),

190: D("Use-after-free is accessing an object after its memory has been released; it's undefined behaviour and a major security vulnerability because freed memory is soon reused for attacker-influenced data.",
"""Exploitation pattern: an object with a vtable is freed, attacker-controlled data is allocated in the same slot, and a later virtual call through the stale pointer jumps to an attacker-chosen address. A large share of critical browser and OS vulnerabilities are use-after-free bugs.

Prevention: clear ownership (`unique_ptr`), `weak_ptr` for observers, avoiding raw pointers into containers across modifications, and testing with AddressSanitizer. Hardened allocators and memory tagging (ARM MTE) help detect it in production.""",
"Keeping an iterator or pointer to a `std::vector` element across `push_back`, then writing through it after reallocation freed the old buffer.",
["Why is use-after-free exploitable? => Freed memory is reused for other data, so stale pointers read or write attacker-controlled contents.",
 "What hardware feature helps detect it? => Memory tagging, e.g. ARM MTE, which checks pointer tags against memory tags."]),

191: D("Copy-on-write shares one buffer between copies and duplicates it only when one copy is modified; C++11 effectively banned it for `std::string` by requiring that operations like `operator[]` not invalidate references and forbidding reference-counted sharing semantics.",
"""COW made copies cheap but had costs: every potentially mutating access (even non-const `operator[]`) needed a check and possible copy; reference counts needed atomic operations in multithreaded programs; and references/pointers into a string could be invalidated unexpectedly.

C++11's requirements on iterator and reference invalidation, plus move semantics making copies avoidable, led libstdc++ to switch from COW to SSO (with a new ABI, `_GLIBCXX_USE_CXX11_ABI`). COW is still useful in immutable-data designs and some other libraries (Qt's implicitly shared classes).""",
"Mixing libraries built with the old and new libstdc++ string ABI, producing link errors mentioning `std::__cxx11::basic_string`.",
["Why does COW hurt multithreaded code? => Reference counts need atomic updates, and mutation checks add synchronization cost.",
 "What is `_GLIBCXX_USE_CXX11_ABI`? => A libstdc++ macro selecting the new (SSO, non-COW) or old string and list ABI."]),

192: D("The `new` expression (`new T(args)`) calls an allocation function `operator new(sizeof(T))` to get raw memory and then constructs the object; `operator new` itself is just an allocation function, like `malloc` but throwing on failure.",
"""You can call `operator new(size)` directly to get raw memory (no constructor), and replace or overload it globally or per class. You can't change what the `new` expression does as a whole, only the allocation step.

Likewise, the `delete` expression calls the destructor and then `operator delete`. Variants include array forms, `nothrow` forms, aligned forms (`std::align_val_t`, C++17) and sized deallocation.""",
"Overloading `operator new` expecting to control construction; it only controls where memory comes from.",
["Can you call `operator new` directly? => Yes, to get raw uninitialized memory, then construct with placement new.",
 "What did C++17 add for over-aligned types? => Aligned `operator new`/`delete` taking `std::align_val_t`."]),

193: D("Alignment is the requirement that objects of a type start at addresses that are multiples of `alignof(T)`; violating it is undefined behaviour and can crash or slow down memory access.",
"""Many CPUs (and SIMD instructions) fault or split accesses on misaligned addresses; x86 tolerates most misalignment but with a performance penalty, while some ARM cores and DMA engines require strict alignment.

Tools: `alignof(T)`, `alignas(64)` for cache-line or SIMD alignment, `std::aligned_alloc`, `std::align`, and aligned `new` in C++17. Struct padding exists to keep members aligned; reorder members from largest to smallest to reduce padding.

For binary protocols, don't cast byte buffers to struct pointers (alignment and aliasing issues); use `memcpy` into a local or `std::bit_cast`.""",
"`reinterpret_cast<uint32_t*>(buffer + 1)` to read a 32-bit field from a packet buffer: misaligned and an aliasing violation. Use `std::memcpy`.",
["How do you reduce struct padding? => Order members by decreasing alignment, or check with `sizeof` and `offsetof`.",
 "Why align data to 64 bytes? => To match cache-line size, avoiding false sharing and improving SIMD loads."]),

194: D("A buffer overflow writes (or reads) past the end of a buffer, corrupting adjacent memory; it's undefined behaviour and historically one of the most exploited memory-safety bugs in C and C++.",
"""Causes: unchecked `strcpy`/`sprintf`/`memcpy` lengths, off-by-one loop bounds, trusting length fields from input (packets, files), and pointer arithmetic errors.

Stack overflows of this kind can overwrite return addresses (mitigated by stack canaries, ASLR, non-executable stacks and control-flow integrity); heap overflows corrupt allocator metadata or neighbouring objects.

C++ mitigations: `std::string`, `std::vector`, `std::array` with `at()` or hardened library modes (`_GLIBCXX_ASSERTIONS`, libc++ hardening), `std::span` with bounds, `std::format` instead of `sprintf`, and fuzzing with sanitizers for input parsers.""",
"Copying a device-reported length field straight into `memcpy(dst, src, len)` without checking it against the destination size.",
["Which compile flags help catch overflows? => `-fsanitize=address` in testing, `-D_GLIBCXX_ASSERTIONS` / `-D_FORTIFY_SOURCE=2` and stack protectors in builds.",
 "Why is fuzzing effective for parsers? => It generates malformed inputs automatically, and sanitizers turn silent overflows into crashes with stack traces."]),

195: D("In Valgrind's leak summary, \"definitely lost\" means no pointer to the block remains (a true leak), while \"still reachable\" means memory is still pointed to at exit but was never freed.",
"""Categories: **definitely lost** (fix these), **indirectly lost** (reachable only through lost blocks; fixing the definite leak usually fixes them), **possibly lost** (only interior pointers remain; investigate), **still reachable** (often global caches or singletons intentionally not freed at exit).

Still-reachable memory isn't necessarily a bug for a program about to exit, but in long-running services the same pattern (ever-growing reachable caches) is effectively a leak that heap profilers reveal over time.""",
"Ignoring \"still reachable\" growth in a daemon because Valgrind doesn't call it a leak; an unbounded cache will still exhaust memory.",
["What does \"indirectly lost\" mean? => Blocks only reachable from definitely lost blocks, e.g. nodes of a leaked list.",
 "Should you free singletons at exit to silence \"still reachable\"? => Optional; it's usually harmless, but freeing makes leak reports cleaner in CI."]),

196: D("Standard containers take an allocator template parameter (default `std::allocator<T>`) that they use for all element storage; a custom allocator lets you change where and how that memory is obtained without changing container logic.",
"""Containers call the allocator (via `std::allocator_traits`) to allocate raw storage, then construct elements in place. Custom allocators enable memory pools, arenas, shared-memory containers (Boost.Interprocess), tracking allocations per subsystem, and alignment control.

Classic allocators are part of the container's type (`std::vector<int, PoolAlloc<int>>`), which makes interfaces awkward. C++17 **polymorphic allocators** (`std::pmr::vector<int>` with a `std::pmr::memory_resource*`) keep a single container type and choose the resource at runtime.""",
"Writing a stateful classic allocator and forgetting `operator==` or propagation traits, so moving or swapping containers frees memory into the wrong pool.",
["Why were pmr allocators added? => So containers using different memory resources still share one type, e.g. `std::pmr::vector<int>`.",
 "What does `std::allocator_traits` do? => Supplies defaults for optional allocator members so custom allocators only implement the essentials."]),

197: D("Memory ownership means deciding which part of the code is responsible for releasing each resource; modern C++ encodes ownership in types so the compiler helps enforce it.",
"""Conventions: `std::unique_ptr<T>` owns exclusively; `std::shared_ptr<T>` shares ownership; raw pointers and references are non-owning observers; containers own their elements; `std::span`/`std::string_view` are non-owning views.

Function signatures then document intent: taking `unique_ptr<T>` by value transfers ownership in; returning `unique_ptr<T>` transfers ownership out; taking `T&` or `T*` borrows. This removes whole bug classes (leaks, double frees) and makes APIs self-documenting.

The C++ Core Guidelines (R.1-R.37) formalize these rules; tools like clang-tidy check many of them.""",
"APIs that return raw `T*` from factories without documenting who deletes it, so some callers leak and others double-delete.",
["How do you transfer ownership into a function? => Take `std::unique_ptr<T>` by value and call it with `std::move(ptr)`.",
 "Is a raw pointer parameter owning in modern C++? => By convention no; it's an observer (possibly null)."]),

198: D("A moved-from object is left in a **valid but unspecified state**: its invariants still hold, so it can be destroyed, assigned to and have state-independent operations called, but its value shouldn't be relied upon.",
"""For standard library types, the guarantee is exactly that (with some types specifying more: a moved-from `std::unique_ptr` is null; moved-from `std::vector` is in practice empty but not guaranteed by the standard).

For your own types, keep moved-from objects valid (e.g. set pointers to null so the destructor is safe) and document what state they're in. Using a moved-from object's value is a logic bug; clang-tidy's `bugprone-use-after-move` catches many cases.""",
"Reading from a string after `std::move(s)` into a container and assuming it's still the original text (or definitely empty).",
["What operations are safe on a moved-from object? => Destruction, assignment of a new value, and operations without preconditions (like `clear()` or `size()` for containers).",
 "Which moved-from standard type has a specified state? => `std::unique_ptr` (null) and `std::shared_ptr` (empty)."]),

199: D("C++ doesn't mandate garbage collection because it values deterministic destruction, predictable performance and zero-overhead abstractions; RAII, smart pointers and containers fill the role instead.",
"""A tracing GC would make destructor timing unpredictable (bad for locks, files, hardware handles), add pauses (bad for real-time and firmware), and conflict with low-level pointer tricks.

C++11 added minimal \"garbage collection support\" APIs (`std::declare_reachable` etc.) that no major implementation used; they were removed in C++23.

Instead: automatic storage and RAII for most objects, `unique_ptr` for exclusive ownership, `shared_ptr`/`weak_ptr` for shared ownership (reference counting, deterministic), and arenas/pools for bulk lifetime management.""",
"Using `shared_ptr` everywhere to imitate garbage collection, which adds atomic overhead, obscures ownership, and still leaks with reference cycles.",
["What's the downside of reference counting vs tracing GC? => It can't collect cycles on its own and adds counter updates on every copy.",
 "What happened to C++11's GC support APIs? => They were never implemented meaningfully and were removed in C++23."]),

200: D("False sharing is when threads on different cores modify different variables that happen to share a cache line, forcing the line to bounce between cores and severely slowing both, even though no data is actually shared.",
"""Cache coherence works per cache line (typically 64 bytes). Two per-thread counters placed next to each other in a struct or array cause constant invalidations.

Fixes: pad or align per-thread data to cache-line size (`alignas(std::hardware_destructive_interference_size)` in C++17, or `alignas(64)`), keep per-thread data in thread-local storage and combine results at the end, and group data by which thread writes it.

Detection: profilers (`perf c2c` on Linux, Intel VTune) show heavy cache-line contention (HITM events).""",
"An array of per-thread statistics counters (`std::atomic<uint64_t> stats[N]`) updated in a hot loop; adjacent entries share cache lines and scalability collapses.",
["What is `std::hardware_destructive_interference_size`? => A C++17 constant for the minimum offset that avoids false sharing (typically 64).",
 "How do you detect false sharing on Linux? => `perf c2c` reports cache lines with cross-core contention."]),
}
