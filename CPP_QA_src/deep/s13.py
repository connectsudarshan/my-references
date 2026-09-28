DEEP = {

356: D("An rvalue reference (`T&&`) is a reference that binds to rvalues (temporaries and objects cast with `std::move`), identifying objects whose resources may be taken because they're about to expire.",
"""Before C++11, a function couldn't tell whether its argument was a temporary, so it had to copy. With overloads `f(const T&)` (lvalues) and `f(T&&)` (rvalues), code can copy from named objects and steal from temporaries.

Note: `T&&` in a template with deduced `T` (or `auto&&`) is a **forwarding reference**, not an rvalue reference; it binds to both. And a named rvalue reference variable is itself an lvalue.""",
"Assuming every `&&` in a signature means \"rvalue only\"; in deduced contexts it's a forwarding reference that also binds lvalues.",
["Can an rvalue reference bind to an lvalue? => Not without a cast; `std::move` produces the needed xvalue.",
 "What does an rvalue reference extend? => A temporary bound directly to it lives as long as the reference."]),

357: D("Move semantics lets an object transfer its resources (heap buffers, handles) to another object instead of copying them, when the source is a temporary or explicitly marked as movable.",
"""Problem solved: before C++11, returning or inserting large objects (vectors, strings) copied their contents, even when the source was about to be destroyed. A move is typically O(1): copy a few pointers and null out the source.

This made value semantics cheap: returning `std::vector` by value, storing move-only types like `std::unique_ptr` and `std::thread` in containers, and reallocating vectors without deep copies. The source stays valid but unspecified.""",
"Expecting moves to be free for every type; types without heap resources (like `std::array` or SSO strings) still copy their data when moved.",
["Why is moving a `std::vector` O(1)? => It transfers the pointer to the heap buffer and leaves the source empty.",
 "Which types can be moved but not copied? => Move-only types like `std::unique_ptr`, `std::thread`, `std::fstream`."]),

358: D("A move constructor `T(T&& other) noexcept` constructs a new object by taking over `other`'s resources and leaving `other` in a valid, typically empty, state.",
"""Typical implementation: copy the pointer members, then set the source's pointers to null so its destructor releases nothing: `Buffer(Buffer&& o) noexcept : data_(std::exchange(o.data_, nullptr)), size_(std::exchange(o.size_, 0)) {}`.

It's implicitly generated (member-wise move) if you declare no copy operations, move assignment or destructor. Mark it `noexcept` so containers use it during reallocation.""",
"Forgetting to reset the source's pointer in a hand-written move constructor: both objects' destructors free the same buffer.",
["What does `std::exchange` do in move constructors? => Sets a member to a new value and returns the old one in one expression.",
 "When is the move constructor implicitly generated? => When no copy operations, move assignment or destructor are user-declared."]),

359: D("`std::move` is an unconditional cast to an rvalue reference (`static_cast<std::remove_reference_t<T>&&>`); it doesn't move anything itself but makes the argument eligible to bind to move constructors and move assignment.",
"""Whether a move actually happens depends on overload resolution: if the type has a move constructor, it's selected; otherwise the copy constructor is used (const lvalue references bind rvalues). `std::move` of a const object yields `const T&&`, which binds to the copy constructor.

Use it to transfer ownership from named objects you no longer need: `v.push_back(std::move(buffer));`. Don't use it on return statements of local variables (it prevents copy elision).""",
"`return std::move(localVector);`, which disables NRVO and forces a move where no operation at all would have been needed.",
["Does `std::move` generate any code? => No, it's a compile-time cast.",
 "What happens if a type has no move constructor? => The copy constructor is used instead."]),

360: D("After `std::move(obj)` is passed to a move operation, `obj` is in a valid but unspecified state, so reading its value (expecting the original contents) is a logic bug; you may only destroy it, assign to it, or call operations without preconditions.",
"""For many standard types the moved-from state is empty in practice, but it's not guaranteed (except for some, like `std::unique_ptr`). Code that relies on the old value, or on emptiness, may break with another implementation or a different string length (SSO strings may keep their characters).

Static analysis catches it: clang-tidy `bugprone-use-after-move`, and some compilers warn. If you need the object again, assign it a new value first (e.g. `s.clear()` or `s = {}`).""",
"Moving a string into a container and then logging it: `names.push_back(std::move(name)); log(name);` prints an unspecified (often empty) string.",
["What's safe to do with a moved-from `std::vector`? => Destroy it, assign to it, or call `clear()` and reuse it.",
 "Which tool detects use-after-move? => clang-tidy's `bugprone-use-after-move` check."]),

361: D("A move assignment operator `T& operator=(T&& other) noexcept` replaces the current object's state by taking over `other`'s resources, after releasing its own.",
"""Implementation outline: release current resources, steal `other`'s, reset `other`, return `*this`; handle self-move-assignment (`x = std::move(x)`) at least without leaking or crashing. A common shortcut is the move-and-swap idiom or implementing both assignments with a by-value parameter (copy-and-swap).

Mark it `noexcept`, like the move constructor.""",
"Releasing the current buffer and then reading from `other` without checking for self-move-assignment, leaving the object with a dangling pointer.",
["Is self-move-assignment required to preserve the value? => No, only to leave the object in a valid state; but it must not crash or leak.",
 "Can one function serve as both copy and move assignment? => Yes, a by-value `operator=(T other)` with swap handles both."]),

362: D("Move operations should be `noexcept` because standard containers (and `std::move_if_noexcept`) only use them when they can't throw; otherwise they fall back to copying to keep the strong exception guarantee.",
"""During `std::vector` reallocation, if a move threw halfway, some elements would be moved-from and the original couldn't be restored. So if the move constructor isn't `noexcept` and the type is copyable, `vector` copies, which can be dramatically slower.

Moves that just transfer pointers genuinely can't throw, so marking them `noexcept` is accurate. The implicitly generated move operations are `noexcept` when all members' moves are. Verify with `static_assert(std::is_nothrow_move_constructible_v<T>);`.""",
"A hand-written move constructor without `noexcept`, silently turning every vector growth into a deep copy of all elements.",
["Which standard facility decides between move and copy? => `std::move_if_noexcept`, used by containers during reallocation.",
 "Are implicitly generated moves noexcept? => Yes, if all members' and bases' move operations are noexcept."]),

363: D("Perfect forwarding passes arguments from a function template to another function while preserving their value category (lvalue or rvalue) and constness, using forwarding references (`T&&`) and `std::forward<T>`.",
"""Without it, a wrapper like `make_unique` would either copy everything (taking by value or const reference) or fail for lvalues (taking `T&&`). With `template<class... Args> auto make(Args&&... args) { return T(std::forward<Args>(args)...); }`, lvalues stay lvalues (copied) and rvalues stay rvalues (moved).

Used throughout the standard library: `std::make_unique`, `std::make_shared`, `emplace_back`, `std::thread`, `std::invoke`.""",
"Writing `std::forward<Args>(args)` twice for the same argument (e.g. logging then passing it on); the first forward may move from it.",
["What two ingredients enable perfect forwarding? => Forwarding references (`T&&` with deduced `T`) and `std::forward<T>`.",
 "Which standard functions rely on perfect forwarding? => `make_unique`, `make_shared`, `emplace_back`, `std::thread`'s constructor and more."]),

364: D("A forwarding (\"universal\") reference is a `T&&` parameter where `T` is deduced from the argument (or `auto&&`); it binds to both lvalues and rvalues. A normal rvalue reference has a known type (e.g. `std::string&&` or `T&&` where `T` is a class template parameter already fixed).",
"""Tests: `template<class T> void f(T&& x)` is forwarding; `void f(Widget&& x)` is rvalue; inside `template<class T> class Box { void set(T&& v); }`, `T` isn't deduced at the call, so `set` takes an rvalue reference; `const T&&` is never forwarding.

Reference collapsing makes it work: an lvalue `Widget` deduces `T = Widget&`, and `Widget& &&` collapses to `Widget&`.""",
"Assuming a member function `void push(T&& v)` of `template<class T> class Queue` accepts lvalues; `T` is fixed by the class, so it only takes rvalues.",
["What is reference collapsing? => `& &`, `& &&` and `&& &` collapse to `&`; only `&& &&` collapses to `&&`.",
 "Is `auto&&` a forwarding reference? => Yes, it binds to lvalues and rvalues (used in generic range-for loops)."]),

365: D("The implicit generation rules are asymmetric: declaring a move operation deletes the implicit copy operations, while declaring a copy operation or destructor suppresses the implicit move operations (which then fall back to copying).",
"""So the question's premise is inverted, as its answer notes: defining only a move constructor makes the class **move-only** (copy constructor and copy assignment are defined as deleted). Defining only a copy constructor or destructor means the class is copied even when moved from (no implicit move constructor is declared, so rvalues use the copy constructor).

These rules exist to avoid silently generating wrong operations for classes with custom resource management. The Rule of Five (or Rule of Zero) avoids surprises: declare all five explicitly (`= default` or `= delete` where appropriate) or none.""",
"Adding `~Widget() = default;` \"for completeness\" to a class; it suppresses implicit move operations, so moves become copies.",
["What happens to copy operations if you declare a move constructor? => They're implicitly deleted.",
 "What happens to move operations if you declare a destructor? => They aren't implicitly declared, so moving falls back to copying."]),

366: D("A named rvalue reference is an lvalue because it has a name and can be used multiple times; treating it as an rvalue would let the first use silently move from it and break later uses.",
"""Inside `void add(std::string&& s)`, `s` is an lvalue expression of type `std::string`. `names.push_back(s)` copies; `names.push_back(std::move(s))` moves. The rule \"if it has a name, it's an lvalue\" makes moves explicit and safe.

In generic code with forwarding references, use `std::forward<T>(x)` instead of `std::move`, so lvalue arguments aren't moved from.""",
"Writing `member_ = param;` in a constructor taking `std::string&& param`, which copies instead of moving; use `member_(std::move(param))`.",
["Why isn't a named `T&&` treated as an rvalue? => It could be used again later; implicit moving would leave later uses with moved-from state.",
 "What's the value category of `std::move(s)`? => xvalue (an rvalue)."]),

367: D("`std::forward<T>(x)` conditionally casts `x` to an rvalue only if the original argument was an rvalue (encoded in the deduced `T`), preserving value category; `std::move` always casts to an rvalue.",
"""In `template<class T> void wrapper(T&& x) { target(std::forward<T>(x)); }`, calling `wrapper(name)` deduces `T = std::string&` and forwards an lvalue (copy); calling `wrapper(std::string{\"x\"})` deduces `T = std::string` and forwards an rvalue (move).

Using `std::move` there would move from the caller's lvalue `name`, a nasty surprise. Rule: `std::move` for rvalue references, `std::forward` for forwarding references.""",
"Using `std::move` on a forwarding reference parameter, which silently moves from callers' lvalues.",
["Why does `std::forward` need the template argument `T`? => `T` encodes whether the original argument was an lvalue or rvalue.",
 "When should you use `std::move` vs `std::forward`? => `move` for rvalue references, `forward` for forwarding references."]),

368: D("Moving a `std::unique_ptr` transfers ownership of the managed object to the destination; the source becomes null, and no object is copied or destroyed.",
"""`auto p2 = std::move(p1);` leaves `p1 == nullptr`. This is how ownership passes into functions (`void take(std::unique_ptr<Device> d)` called with `take(std::move(dev))`), out of factories (return by value), and into containers.

Unlike most types, `unique_ptr`'s moved-from state is specified: it's guaranteed to be null.""",
"Dereferencing the source `unique_ptr` after moving it into a container or function; it's null.",
["Is a moved-from `unique_ptr` guaranteed to be null? => Yes.",
 "How do you transfer a `unique_ptr` into a function? => Take it by value and call with `std::move(ptr)`."]),

369: D("Returning a local by value doesn't need `std::move` because the compiler either elides the copy entirely (NRVO) or, if it can't, automatically treats the returned local as an rvalue (implicit move); adding `std::move` actually prevents NRVO.",
"""`return std::move(local);` changes the return expression from a plain name (eligible for elision) to a function call result, so NRVO no longer applies and a move constructor call is forced.

C++20 and C++23 extended implicit move to more cases (e.g. returning rvalue reference parameters and some conversions). Compilers warn: `-Wpessimizing-move` and `-Wredundant-move`.""",
"Adding `std::move` to every return statement \"for performance\", which pessimizes by blocking copy elision.",
["Which warning catches this? => `-Wpessimizing-move` (and `-Wredundant-move`) in GCC and Clang.",
 "When is `return std::move(x)` still useful? => When returning a member or a sub-object, which aren't implicitly moved."]),

370: D("A move-only type can be moved but not copied (copy operations deleted), used for objects representing unique ownership of a resource, such as `std::unique_ptr`, `std::thread`, `std::fstream` or a device handle.",
"""Copying a file handle, thread or hardware lock doesn't make sense (two owners would both close it), but transferring it (returning from a factory, storing in a container) does.

Design: delete copy constructor and copy assignment, implement (or default) `noexcept` move operations, and define the moved-from state (e.g. an invalid handle the destructor ignores). Containers support move-only elements, though you can't copy such containers.""",
"Making a resource type copyable with a shallow copy, so two objects close the same file descriptor or release the same device lock.",
["Can `std::vector` hold move-only types? => Yes, but the vector itself then can't be copied.",
 "Why is `std::thread` move-only? => A thread of execution can have only one owner responsible for joining it."]),

371: D("Containers use moves during reallocation only if they can't throw (or if the type isn't copyable); otherwise they copy, so that a failure midway leaves the original elements intact and the strong exception guarantee holds.",
"""This is `std::move_if_noexcept` in action. For a type with a throwing (or non-noexcept) move constructor and a copy constructor, `push_back` reallocation copies every element: correct but slow.

If a type is move-only with a potentially throwing move, `vector` moves anyway and gives only the basic guarantee for that operation. Declaring moves `noexcept` gets both speed and strong safety.""",
"Leaving move constructors unmarked and profiling a slow `push_back` loop without realizing every reallocation deep-copies elements.",
["What guarantee does `vector::push_back` give for move-only types with throwing moves? => Only the basic guarantee.",
 "How do you confirm reallocation will move? => `static_assert(std::is_nothrow_move_constructible_v<T>)`."]),

372: D("Moving a heap-allocated (long) `std::string` just transfers the buffer pointer (O(1)), while moving a short string stored in its small-string buffer must copy the characters, since there's no heap buffer to steal.",
"""With SSO (typically up to 15 or 22 characters), the characters live inside the string object. The move constructor copies them into the destination and usually sets the source to empty (not guaranteed). It's still cheap, a small fixed-size copy, but not pointer-stealing.

Consequence: pointers from `data()` of a short string don't survive moving the string, while for long strings they usually point into the transferred buffer (still not something to rely on).""",
"Keeping a `const char*` from `s.c_str()` and expecting it to remain valid after moving `s` into a container; for SSO strings the characters move with the object.",
["Is moving an SSO string expensive? => No, it copies a small fixed buffer, but it isn't a pointer steal.",
 "Is the moved-from string guaranteed empty? => No, only valid but unspecified (in practice usually empty)."]),

373: D("C++17 guaranteed copy elision means that initializing an object from a prvalue of the same type constructs it directly in place, with no copy or move at all, so it works even for non-movable types; move semantics is about cheaply transferring resources when an actual move does happen.",
"""Since C++17, a prvalue is \"a recipe\" for creating an object, materialized only where needed. `T x = T(args);` and `return T(args);` create exactly one object. Before C++17, this was an allowed optimization and the move constructor still had to be accessible.

Elision vs move: elision removes the operation; moves make the remaining necessary transfers cheap (e.g. returning a named local when NRVO isn't possible, or inserting into containers).""",
"Believing a class must be movable to be returned by value; since C++17 a prvalue return works for non-movable types too.",
["Can you return a `std::mutex` by value in C++17? => Yes, from a prvalue: `return std::mutex{};` works due to guaranteed elision.",
 "Is NRVO guaranteed by C++17? => No, only prvalue elision is guaranteed."]),

374: D("A `const` object can't be moved from because moving modifies the source (e.g. nulling its pointer), and `std::move` on a const object produces `const T&&`, which can't bind to the move constructor's `T&&` parameter, so the copy constructor is chosen.",
"""The call compiles silently and copies, which is a performance bug rather than a compile error. It happens with `const` locals (`const std::vector v = ...; return std::move(v);`), const members, and `const auto&` loop variables.

Avoid declaring objects `const` when you intend to move from them later; clang-tidy (`performance-move-const-arg`) flags `std::move` on const objects.""",
"Declaring a large local `const` for safety and later calling `consume(std::move(it))`, silently copying.",
["Why does `std::move` on a const object compile? => `const T&&` binds to `const T&`, selecting the copy constructor.",
 "Which clang-tidy check catches this? => `performance-move-const-arg`."]),

375: D("Move semantics doesn't propagate automatically into members when you write your own move operations: inside a move constructor, named members are lvalues, so you must `std::move` each member (or use `= default`), otherwise they're copied.",
"""Example: `Widget(Widget&& o) : name_(o.name_), data_(o.data_) {}` copies both members, because `o.name_` is an lvalue. Correct: `name_(std::move(o.name_)), data_(std::move(o.data_))`.

The simplest correct approach is `Widget(Widget&&) noexcept = default;` (or the Rule of Zero), which moves member-wise automatically. The same applies when forwarding a `T&&` parameter into a member (`member_(std::move(param))`).""",
"Hand-writing a move constructor that initializes members from `other.member` without `std::move`, so the \"move\" deep-copies everything.",
["Why are members of an rvalue-referenced object lvalues? => `o` is a named reference (an lvalue), so `o.member` is an lvalue too.",
 "What's the simplest way to get correct member-wise moves? => `= default` for the move operations, or no user-declared special members at all."]),
}
