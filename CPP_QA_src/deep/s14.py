DEEP = {

376: D("Smart pointers are RAII class templates that own a dynamically allocated object and automatically release it, encoding ownership in the type: `std::unique_ptr` (exclusive), `std::shared_ptr` (shared, reference counted) and `std::weak_ptr` (non-owning observer).",
"""They replace manual `new`/`delete`, eliminating leaks on early returns and exceptions and making ownership visible in interfaces. `std::auto_ptr` (C++98) was deprecated in C++11 and removed in C++17 because its \"copy\" silently transferred ownership.

Default choice: `unique_ptr`. Use `shared_ptr` only for genuinely shared lifetime; use raw pointers or references for non-owning access.""",
"Using `shared_ptr` everywhere by default, hiding ownership design and paying atomic reference-counting costs unnecessarily.",
["Why was `std::auto_ptr` removed? => Its copy operations transferred ownership, surprising users and breaking containers; `unique_ptr` makes transfer explicit with moves.",
 "Should a function that only uses an object take a smart pointer? => No, take `T&` or `T*`; smart pointer parameters are for ownership changes."]),

377: D("`std::unique_ptr<T>` exclusively owns an object, deletes it when the `unique_ptr` is destroyed or reset, and can be moved but not copied.",
"""It has zero overhead compared to a raw pointer with the default deleter (same size, inlined deletion). It supports custom deleters (part of the type), arrays (`unique_ptr<T[]>`), and conversion to `shared_ptr`.

Idioms: factories return `std::unique_ptr<Base>`; members hold owned sub-objects (pImpl); containers of polymorphic objects use `std::vector<std::unique_ptr<Base>>`. Use `.get()` to pass a non-owning pointer and `.release()` only when handing ownership to legacy code.""",
"Calling `release()` expecting it to delete the object; it only gives up ownership and returns the raw pointer, which you must then manage.",
["Is `unique_ptr` larger than a raw pointer? => Not with the default (stateless) deleter.",
 "`reset()` vs `release()`? => `reset()` deletes the current object; `release()` gives it up without deleting."]),

378: D("`std::shared_ptr<T>` implements shared ownership: multiple `shared_ptr`s can own the same object, which is deleted when the last owner is destroyed or reset.",
"""It uses a separate **control block** holding the strong count, weak count, deleter and allocator. Copying increments the strong count atomically, destruction decrements it.

Uses: objects with genuinely shared or unpredictable lifetimes (caches, graph nodes, async operations where callbacks keep an object alive). Pitfalls: reference cycles, performance overhead, and design obscurity when used as a default.""",
"Keeping `shared_ptr`s in both directions between parent and child objects, creating a cycle that's never freed.",
["When is the managed object destroyed? => When the strong count reaches zero.",
 "When is the control block freed? => When both the strong and weak counts reach zero."]),

379: D("`std::weak_ptr<T>` is a non-owning reference to an object managed by `shared_ptr`; it doesn't keep the object alive, and you must convert it to a `shared_ptr` with `lock()` to use the object safely.",
"""Uses: breaking reference cycles (child-to-parent links), caches that shouldn't keep entries alive, observers that must detect whether the subject still exists, and `enable_shared_from_this`.

`lock()` atomically returns a `shared_ptr` (empty if expired), so the object can't be destroyed while you use it. `expired()` alone is racy in multithreaded code, because the object may die right after the check.""",
"Checking `if (!w.expired()) w.lock()->use();`; between the check and `lock()`, another thread may destroy the object. Use `if (auto sp = w.lock())`.",
["Why isn't `expired()` enough before using the object? => The object can be destroyed between the check and the use; `lock()` is atomic.",
 "Does a `weak_ptr` keep the control block alive? => Yes, through the weak count, even after the object is destroyed."]),

380: D("Use the factory functions `std::make_unique<T>(args...)` (C++14) and `std::make_shared<T>(args...)` (C++11) instead of `new`.",
"""Benefits: no raw `new` in code, exception safety (before C++17, `f(std::shared_ptr<A>(new A), g())` could leak if `g()` threw between allocation and construction of the `shared_ptr`), less repetition of the type name, and for `make_shared` a single allocation.

When you can't use them: custom deleters, adopting a pointer from a C API, private constructors (unless using a passkey), or `make_shared` for objects whose memory should be released while weak pointers remain (see Q381). C++20 adds `make_shared` for arrays and `make_unique_for_overwrite`.""",
"Using `std::shared_ptr<T>(new T)` everywhere out of habit, doubling allocations and risking leaks in complex expressions in older standards.",
["Why was `make_unique` added in C++14 only? => It was an oversight in C++11, fixed in C++14.",
 "What does `make_unique_for_overwrite` do? => Allocates without value-initializing (useful for large buffers that will be filled immediately), C++20."]),

381: D("`std::make_shared` allocates the object and its control block in a single allocation, whereas `std::shared_ptr<T>(new T())` performs two (one for the object, one for the control block).",
"""One allocation means less allocator overhead, better cache locality (count and object adjacent), and less memory fragmentation.

Trade-off: with `make_shared`, the object's memory can't be freed until the control block is freed, i.e. until all `weak_ptr`s are gone too (the object is destroyed when the strong count hits zero, but the storage remains). For large objects with long-lived weak pointers, separate allocation may be preferable.""",
"Using `make_shared` for very large objects observed by long-lived `weak_ptr`s in a cache, keeping big memory blocks allocated after the objects are destroyed.",
["When is the memory of a `make_shared` object released? => When the control block is released, i.e. when the weak count also reaches zero.",
 "Does the destructor run later with `make_shared`? => No, the destructor runs when the strong count hits zero; only the memory release is delayed."]),

382: D("A reference cycle is when objects hold `shared_ptr`s to each other (directly or through a chain), so their strong counts never reach zero and they're never destroyed, even when unreachable from the rest of the program.",
"""Example: a `Device` holds `shared_ptr<Port>`s and each `Port` holds a `shared_ptr<Device>` back to its parent. Dropping all external pointers leaves the counts at 1 forever.

Fix: make back-references non-owning, with `std::weak_ptr` (when the parent may die first) or raw pointers/references (when the child's lifetime is strictly contained). Also avoid lambdas stored in an object that capture a `shared_ptr` to the same object.""",
"Storing a callback in an object that captures `shared_from_this()`, creating a cycle between the object and its own stored lambda.",
["How do you break a parent-child cycle? => Children hold `weak_ptr` (or raw pointer) to the parent; parents own children.",
 "Why can't reference counting collect cycles? => Each object in the cycle keeps the others' counts above zero."]),

383: D("Call `lock()` on the `weak_ptr` to get a `shared_ptr`; if it's non-null the object is alive and stays alive while you hold it, otherwise the object has been destroyed.",
"""Idiom: `if (auto dev = weakDev.lock()) { dev->reset(); } else { /* gone */ }`. Alternatively, constructing `std::shared_ptr<T>(weak)` throws `std::bad_weak_ptr` if expired.

Keep the locked `shared_ptr` only as long as needed, to avoid unintentionally extending lifetimes.""",
"Storing the `shared_ptr` obtained from `lock()` in a long-lived member, turning the observer into an owner and defeating the purpose of `weak_ptr`.",
["What does `shared_ptr<T>(weak)` do if the object expired? => Throws `std::bad_weak_ptr`.",
 "Is `lock()` thread-safe? => Yes, it atomically checks and increments the strong count."]),

384: D("No: `std::unique_ptr` is move-only because copying would create two owners of the same object, and both would delete it.",
"""Its copy constructor and copy assignment are deleted. Transfer ownership explicitly with `std::move`, or create a new object if you need a copy (`std::make_unique<T>(*p)`, or a virtual `clone()` for polymorphic types).

Classes containing a `unique_ptr` member are automatically non-copyable (implicit copy operations deleted) but movable, which is usually the right default for owning classes.""",
"Trying to copy a `std::vector<std::unique_ptr<T>>`; it doesn't compile because elements are move-only. Write an explicit deep-copy function if needed.",
["How do you deep-copy through a `unique_ptr<Base>`? => A virtual `clone()` returning `std::unique_ptr<Base>`.",
 "What happens to a class with a `unique_ptr` member? => It becomes move-only unless you define copy operations yourself."]),

385: D("A custom deleter is a callable that a smart pointer uses instead of `delete` to release the resource, letting smart pointers manage non-memory resources and memory from other allocators.",
"""Examples: `std::unique_ptr<FILE, decltype(&fclose)> f(fopen(path, \"rb\"), &fclose);`, closing file descriptors, releasing device handles from a vendor SDK, freeing `malloc` memory with `free`, or returning objects to a pool.

For `unique_ptr` the deleter is part of the type (a stateless deleter like an empty struct costs nothing; a function pointer adds a pointer's size). For `shared_ptr` the deleter is type-erased in the control block, so `shared_ptr<T>`s with different deleters share one type.""",
"Using a function pointer deleter with `unique_ptr` in a size-critical structure; an empty functor struct keeps the `unique_ptr` the size of a raw pointer.",
["Why is a lambda or empty struct deleter better than a function pointer for `unique_ptr`? => A stateless deleter adds no size; a function pointer doubles the size.",
 "Is the deleter part of `shared_ptr`'s type? => No, it's stored type-erased in the control block."]),

386: D("The reference count is one field inside the control block; the control block is the separately allocated structure that holds the strong count, the weak count, the deleter, the allocator, and (with `make_shared`) the object itself.",
"""Every `shared_ptr` holds two pointers: one to the object (possibly an interior pointer, via aliasing) and one to the control block. All owners of the same object share one control block.

The strong count determines when the object is destroyed; the weak count (plus one while strong owners exist) determines when the control block itself is freed.""",
"Assuming `sizeof(shared_ptr<T>)` equals a raw pointer; it's two pointers, plus the separate control block.",
["Why does `shared_ptr` store two pointers? => One to the managed object (which may differ via aliasing), one to the control block.",
 "What frees the control block? => Both the strong and weak counts reaching zero."]),

387: D("Yes, reference count updates are atomic, so copying and destroying different `shared_ptr` instances that share an object is thread-safe; but concurrent access to the **same** `shared_ptr` instance (one thread assigning while another reads it) is a data race, and the managed object itself isn't protected.",
"""Three levels: control block (thread-safe), a single `shared_ptr` object (not thread-safe for concurrent modification; use `std::atomic<std::shared_ptr<T>>` in C++20), and the pointee (needs its own synchronization).

Atomic increments cost more than plain ones, especially under contention across cores, which is a reason not to copy `shared_ptr`s in hot paths.""",
"Having one thread reassign a global `shared_ptr<Config>` while others read it, believing `shared_ptr` is thread-safe; that's a data race. Use `std::atomic<std::shared_ptr<Config>>`.",
["What does C++20 add for this? => `std::atomic<std::shared_ptr<T>>` for safe concurrent reads and writes of the same pointer.",
 "Does `shared_ptr` make the pointee thread-safe? => No, only the reference counting is synchronized."]),

388: D("Creating two `shared_ptr`s from the same raw pointer creates two independent control blocks, each believing it owns the object, so the object is deleted twice.",
"""Example: `T* raw = new T; std::shared_ptr<T> a(raw); std::shared_ptr<T> b(raw);` leads to a double delete. A subtler version: calling `std::shared_ptr<T>(this)` inside a member function of an object already owned by a `shared_ptr`.

Rules: create the `shared_ptr` once at allocation (`make_shared`), copy `shared_ptr`s rather than raw pointers, and use `enable_shared_from_this` when an object needs a `shared_ptr` to itself.""",
"Writing `return std::shared_ptr<Session>(this);` in a member function to hand a callback a pointer to the session, creating a second control block.",
["How should an object get a `shared_ptr` to itself? => Inherit `std::enable_shared_from_this<T>` and call `shared_from_this()`.",
 "What prevents this bug in general? => Never constructing `shared_ptr` from raw pointers that might already be owned; use `make_shared` at creation."]),

389: D("`std::enable_shared_from_this<T>` is a base class that lets an object already managed by a `shared_ptr` safely obtain additional `shared_ptr`s to itself via `shared_from_this()` (or `weak_from_this()` in C++17).",
"""It stores a `weak_ptr` to the object, set when the first `shared_ptr` takes ownership, so `shared_from_this()` shares the existing control block instead of creating a new one.

Typical use: asynchronous operations (Boost.Asio) where an object passes `shared_from_this()` into a callback to stay alive until the callback runs.""",
"Calling `shared_from_this()` in the constructor; no `shared_ptr` owns the object yet, so it throws `std::bad_weak_ptr` (C++17).",
["Why can't you call `shared_from_this()` in the constructor? => The owning `shared_ptr` doesn't exist until construction completes.",
 "What does `weak_from_this()` return? => A `weak_ptr` to the object (C++17), empty if not owned by a `shared_ptr`."]),

390: D("Calling `shared_from_this()` on an object not owned by any `shared_ptr` throws `std::bad_weak_ptr` since C++17 (it was undefined behaviour before).",
"""This happens with objects on the stack, in `std::unique_ptr`, as members of other objects, or during construction and destruction. The internal `weak_ptr` is empty, so there's nothing to share.

Designs using `enable_shared_from_this` often make constructors private and expose a `static std::shared_ptr<T> create(...)` factory, guaranteeing objects are always `shared_ptr`-owned.""",
"Creating a session object on the stack for a quick test and calling a method that internally uses `shared_from_this()`, which throws.",
["What did C++17 change here? => Calling `shared_from_this()` without an owner throws `bad_weak_ptr` instead of being undefined behaviour.",
 "How do you force objects to be created in a `shared_ptr`? => Private constructor plus a static `create()` factory returning `shared_ptr`."]),

391: D("`std::shared_ptr` costs two pointers per instance, a control block allocation (merged with `make_shared`), atomic increments and decrements on every copy and destruction, and an indirection through the control block for weak operations.",
"""In most code this is negligible. It matters in hot paths: copying `shared_ptr`s in loops or passing them by value to frequently called functions triggers contended atomic operations across cores, which can dominate runtime.

Mitigations: pass by `const&` or raw pointer/reference when not taking ownership, move instead of copy when transferring, use `unique_ptr` when ownership isn't shared, and avoid `shared_ptr` in per-element data structures (use indices or arenas).""",
"Passing `std::shared_ptr<Device>` by value to a function called for every I/O request, performing two atomic operations per call.",
["Why are atomic increments expensive under contention? => The cache line holding the count bounces between cores.",
 "How do you avoid ref-count traffic in a hot function? => Take `const T&` or `T*` instead of `shared_ptr<T>` by value."]),

392: D("`std::unique_ptr<T[]>` is a separate partial specialization for arrays: it calls `delete[]`, provides `operator[]` instead of `*` and `->`, and doesn't support derived-to-base conversions, so it isn't interchangeable with `std::unique_ptr<T>`.",
"""Using `unique_ptr<T>` for memory from `new T[n]` calls `delete` instead of `delete[]` (undefined behaviour). The array version also forbids converting `unique_ptr<Derived[]>` to `unique_ptr<Base[]>`, because pointer arithmetic on base pointers into a derived array is broken.

Prefer `std::vector<T>` for dynamic arrays; use `std::make_unique<T[]>(n)` when you need a fixed heap buffer with minimal overhead (e.g. a DMA staging buffer).""",
"Holding `new char[n]` in `std::unique_ptr<char>`, leading to `delete` on array memory.",
["Why can't `unique_ptr<Derived[]>` convert to `unique_ptr<Base[]>`? => Indexing through a base pointer into a derived array uses the wrong element size.",
 "When prefer `unique_ptr<T[]>` over `vector<T>`? => For a fixed-size buffer where you want no capacity/size bookkeeping and exact allocation."]),

393: D("A `std::unique_ptr` converts to a `std::shared_ptr` by moving it (`std::shared_ptr<T> sp = std::move(up);`), transferring ownership and its deleter; there's no safe conversion from `shared_ptr` back to `unique_ptr`, because other owners may exist.",
"""This is why factories should return `unique_ptr`: callers can keep exclusive ownership or convert to shared ownership as needed, but not the other way around.

`shared_ptr` has no `release()`; once shared, the object's lifetime is governed by the reference count.""",
"Returning `shared_ptr` from factories \"to be flexible\", forcing shared-ownership overhead on every caller when `unique_ptr` would convert on demand.",
["Why can't you release ownership from a `shared_ptr`? => Other owners may still reference the object, so no single owner can take it.",
 "Does the deleter carry over when converting `unique_ptr` to `shared_ptr`? => Yes, it's moved into the control block."]),

394: D("The aliasing constructor `std::shared_ptr<U>(const std::shared_ptr<T>& owner, U* ptr)` creates a `shared_ptr` that shares ownership (the control block) with `owner` but points to a different object, usually a member or sub-object of the owned object.",
"""Example: `std::shared_ptr<Port> port(devicePtr, &devicePtr->ports[2]);` keeps the whole `Device` alive as long as the `port` pointer exists, while giving access only to one port.

It's useful for exposing parts of an object without separate ownership. The pointed-to object must remain valid as long as the owner is alive; the aliasing pointer doesn't manage it independently.""",
"Aliasing a pointer to an object not owned by the source `shared_ptr` (e.g. an unrelated heap object), which can dangle while the count says it's alive.",
["What does the aliasing constructor keep alive? => The object owned by the original `shared_ptr`, not the separately pointed-to object.",
 "What's a typical use? => Handing out `shared_ptr`s to members of an object while keeping the whole object alive."]),

395: D("Pass `shared_ptr` by value only when the function takes (shares) ownership; otherwise pass `const T&`, `T*` or `const std::shared_ptr<T>&`, because by-value passing costs atomic reference-count updates and obscures intent.",
"""Guidelines (C++ Core Guidelines R.30-R.37):

- `void use(const Device&)`: just uses the object; most common.
- `void maybeUse(const Device*)`: optional use.
- `void keep(std::shared_ptr<Device> d)`: stores a copy (shares ownership); caller can `std::move` in.
- `void reseat(std::shared_ptr<Device>& d)`: may change which object the caller's pointer refers to.
- `void inspect(const std::shared_ptr<Device>&)`: rarely needed, only if the function may conditionally copy it.""",
"Taking `std::shared_ptr<Logger>` by value in every function that just logs a message, adding atomic operations to every call.",
["When should a function take `shared_ptr` by value? => When it will store or share ownership of the object.",
 "Why take `const T&` instead of `const shared_ptr<T>&`? => It works for objects owned any way (stack, unique_ptr, shared_ptr) and avoids coupling to shared ownership."]),
}
