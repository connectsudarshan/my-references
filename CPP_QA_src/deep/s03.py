DEEP = {

66: D("A constructor is a special member function with the class's name and no return type that initializes a new object and establishes its invariants.",
"""Constructors run automatically when an object is created: for locals at their declaration, for members and bases before the owning constructor's body, and for `new` after memory is allocated. If a constructor completes, the object's lifetime has begun and its destructor will run; if it throws, the object never existed.

Initialize members in the member initializer list, validate arguments, and acquire resources (RAII). Keep constructors cheap and free of virtual calls.""",
"Doing two-phase initialization (`Widget w; w.init();`) out of habit, leaving objects in half-constructed states; initialize fully in the constructor or use a factory function.",
["Does a constructor return a value? => No; failures are reported by throwing, which is why exceptions matter for RAII.",
 "What makes a constructor `constexpr`? => It can be evaluated at compile time for constant arguments, letting objects be compile-time constants."]),

67: D("A destructor (`~ClassName()`) is called automatically when an object's lifetime ends and releases the resources the object owns.",
"""Destructors run at scope exit for locals (in reverse order of construction), on `delete`, when containers destroy elements, and during stack unwinding after an exception. This deterministic timing is what makes **RAII** work: files, locks, sockets and memory are released without explicit cleanup code.

Destructors are implicitly `noexcept`; they should never let exceptions escape. Polymorphic base classes need a virtual destructor. Members are destroyed after the destructor body, in reverse declaration order.""",
"Calling a destructor explicitly on an automatic object (`obj.~T()`); it will be destroyed again at scope exit, which is undefined behaviour. Explicit destructor calls are only for placement-new objects.",
["In what order are members destroyed? => In reverse order of declaration, after the destructor body runs.",
 "When is an explicit destructor call legitimate? => For objects created with placement new in manually managed storage."]),

68: D("A default constructor is one that can be called with no arguments, either because it has no parameters or all have defaults.",
"""The compiler generates one implicitly only if you declare **no** constructors at all; declaring any constructor (including a copy constructor) removes it, which is why `Buffer a;` fails after adding `Buffer(const Buffer&)`. Bring it back with `Widget() = default;`.

The implicit default constructor leaves built-in members (ints, pointers) **uninitialized** in default-initialization. Use default member initializers (`int count = 0;`) so every constructor starts from sane values.

`T()` or `T{}` value-initializes, which zeroes built-in members for classes without a user-provided default constructor; `T t;` does not.""",
"Relying on the implicit default constructor to zero-initialize `int` and pointer members: `Widget w;` leaves them with indeterminate values.",
["Why did adding a copy constructor break `Widget w;`? => Declaring any constructor suppresses the implicit default constructor.",
 "What's the difference between `T t;` and `T t{};`? => The first default-initializes (built-ins may be garbage); the second value-initializes (built-ins zeroed if no user-provided default constructor)."]),

69: D("A parameterized constructor takes arguments used to initialize the object's state at creation.",
"""Parameterized constructors let objects start in a valid, fully specified state (`File f(\"log.txt\", Mode::Append);`) instead of being configured afterwards.

Good practice: mark single-argument constructors `explicit` to prevent implicit conversions; validate arguments and throw on invalid input; take \"sink\" arguments (strings, vectors) by value and `std::move` them into members.

Brace initialization (`Point p{1, 2};`) calls the constructor and forbids narrowing; beware that a constructor taking `std::initializer_list` is preferred by brace syntax.""",
"Declaring a one-argument constructor without `explicit`, allowing `Buffer b = 4096;` or passing an `int` where a `Buffer` is expected.",
["Why take a `std::string` parameter by value in a constructor? => The caller's temporary can be moved in, and lvalues are copied once, then moved into the member.",
 "How does `std::initializer_list` affect brace initialization? => `T{a, b}` prefers an initializer_list constructor if one is viable, e.g. `std::vector<int>{3, 0}` gives two elements, not three zeros."]),

70: D("Yes: a class can have several overloaded constructors with different parameter lists, and the compiler picks one by overload resolution.",
"""Typical set: default constructor, parameterized constructors, copy and move constructors, and perhaps a constructor taking `std::initializer_list`.

Avoid duplicating logic across constructors: use **delegating constructors** (C++11) to route all overloads through one \"master\" constructor, or default member initializers for common defaults.

Too many overloads make calls ambiguous and hard to read; for objects with many optional settings, consider a builder, an options struct with designated initializers (C++20), or named factory functions (`Duration::fromMs(5)`).""",
"Overloads like `Widget(int, double)` and `Widget(double, int)` that are easy to call with arguments swapped; use distinct types or named factories.",
["How do you share code between constructors? => Delegating constructors or default member initializers.",
 "When are named factory functions better than overloaded constructors? => When arguments have the same types but different meanings, e.g. `fromSeconds` vs `fromMilliseconds`."]),

71: D("A copy constructor `T(const T&)` initializes a new object as a copy of an existing object of the same type.",
"""It's used for copy-initialization (`T b = a;`, `T b(a);`), passing and returning by value (unless elided), and when containers copy elements.

The implicit one copies each member. That's correct for members that manage themselves (`std::string`, `std::vector`, `std::unique_ptr` makes the class non-copyable) but wrong for raw owning pointers, where it produces two owners of one buffer.

Declaring a copy constructor suppresses the implicit default constructor and the implicit move operations, so a class with a custom copy constructor falls back to copying when moved.""",
"Taking the parameter by value, `T(T other)`: that would require copying to call the copy constructor, infinite recursion, so it's ill-formed.",
["Why must the copy constructor's parameter be a reference? => Passing by value would itself require a copy, recursively.",
 "What happens to move operations when you declare a copy constructor? => They're not implicitly declared, so rvalues are copied instead."]),

72: D("The copy constructor creates a **new** object from an existing one; copy assignment (`operator=`) replaces the state of an **already existing** object.",
"""`T b = a;` calls the copy constructor (initialization); `b = a;` on an existing `b` calls copy assignment.

Assignment must handle what construction doesn't: releasing the old state, self-assignment (`a = a`), and exception safety. The **copy-and-swap** idiom (`T& operator=(T other) { swap(*this, other); return *this; }`) handles all three and also works as move assignment.

Assignment should return `T&` (so chaining `a = b = c` works) and is typically not virtual.""",
"Writing copy assignment that deletes the old buffer before copying: `a = a` then reads freed memory. Copy first or use copy-and-swap.",
["Which one runs for `T b = a;`? => The copy constructor; the `=` in a declaration is initialization, not assignment.",
 "Why does copy-and-swap give strong exception safety? => The copy happens before `*this` is modified; if it throws, `*this` is unchanged."]),

73: D("The Rule of Three says that if a class needs a user-defined destructor, copy constructor or copy assignment operator, it almost certainly needs all three.",
"""The reason: needing a custom destructor usually means the class owns a raw resource (memory, file handle). The implicit copy operations would then copy the handle, leading to double release or leaks.

Choices: implement all three (deep copy or reference counting), or **delete** the copy operations to make the class non-copyable (`T(const T&) = delete;`). In modern C++ the better answer is usually the Rule of Zero: wrap the resource in a member that already manages it.""",
"Adding a destructor that frees a raw pointer but forgetting copy operations: the first copy leads to a double free.",
["What's the modern replacement for the Rule of Three? => Rule of Five if you manage resources manually, or ideally the Rule of Zero.",
 "When would you delete copy operations? => For unique resources like mutexes, file handles or hardware handles that can't be meaningfully duplicated."]),

74: D("The Rule of Five extends the Rule of Three for C++11: a class that manages a resource should consider all five special members: destructor, copy constructor, copy assignment, move constructor and move assignment.",
"""Declaring a destructor or copy operation suppresses the implicit move operations, so such a class silently copies where it could move. Adding move operations (usually `noexcept`) restores efficient transfers, e.g. when a `std::vector` of these objects reallocates.

Move operations should leave the source in a valid but unspecified state (typically empty), and be `noexcept` so containers use them (`std::move_if_noexcept`).

If you define none of the five and rely on members, you're following the Rule of Zero, which is preferred.""",
"Defining move operations without `noexcept`: `std::vector` then copies elements during reallocation to keep its strong exception guarantee.",
["Why should move constructors be `noexcept`? => Containers only move elements during reallocation if moving can't throw; otherwise they copy.",
 "What state is a moved-from object in? => Valid but unspecified: you can destroy it or assign to it, but shouldn't rely on its value."]),

75: D("The Rule of Zero says classes should not define any of the five special member functions; instead they should hold resources in members (smart pointers, containers, RAII wrappers) that already manage copying, moving and destruction.",
"""Example: a class with `std::vector<std::byte> buffer_` and `std::unique_ptr<Device> dev_` needs no destructor or copy/move code: the compiler-generated ones do the right thing (the class becomes move-only because of the `unique_ptr`).

Only low-level resource-owning classes (a custom RAII wrapper for a file descriptor or DMA buffer) should implement the Rule of Five; everything else composes them.

This reduces bugs, boilerplate, and keeps classes exception-safe by construction.""",
"Writing an empty destructor `~T() {}` \"for completeness\": it suppresses implicit move operations and makes the class copy where it could move. Omit it or write `= default` together with the other special members.",
["How do you make a Rule-of-Zero class non-copyable? => Include a move-only member such as `std::unique_ptr`; the implicit copy operations are then deleted.",
 "When must you break the Rule of Zero? => In the small RAII wrapper that directly owns a raw resource (e.g. a file descriptor)."]),

76: D("A member initializer list (`: a_(x), b_(y)`) initializes members and bases directly before the constructor body runs, instead of default-constructing them and assigning later.",
"""Some members **must** be initialized there: `const` members, references, members without default constructors, and base classes needing arguments.

For class-type members, initializing in the list avoids a default construction followed by assignment, which matters for expensive types. For built-ins it's the only way to avoid a window where they're uninitialized.

Members are initialized in their **declaration order**, not the order of the list; compilers warn (`-Wreorder`) when the list order differs.""",
"Initializing one member from another that is declared later: e.g. `size_(data_.size())` when `size_` is declared before `data_` reads an uninitialized member.",
["Which members must be initialized in the initializer list? => References, `const` members, members without default constructors, and bases needing arguments.",
 "What decides initialization order? => Declaration order in the class, never the order written in the initializer list."]),

77: D("An `explicit` constructor cannot be used for implicit conversions or copy-initialization; it must be called explicitly.",
"""Without `explicit`, `void send(Packet p)` accepts `send(64)` if `Packet(int size)` exists, silently constructing a packet. With `explicit`, that's a compile error and callers must write `send(Packet{64})`.

C++ Core Guidelines: make single-argument constructors `explicit` by default (except for genuine conversions like `std::string` from `const char*`). Since C++11, `explicit` also applies to multi-argument constructors (blocks `T t = {a, b};`) and to conversion operators (`explicit operator bool()` allows `if (obj)` but not `int x = obj;`). C++20 adds conditional `explicit(bool)` for wrapper templates.""",
"Leaving a size-taking constructor implicit so that `Buffer b = 0;` or passing `0` to a `Buffer` parameter compiles unexpectedly.",
["Why is `explicit operator bool()` still usable in `if (p)`? => Contextual conversion to bool (in conditions) is allowed even for explicit operators.",
 "What is `explicit(bool)`? => C++20 conditional explicit, used by wrappers like `std::pair` to be explicit only when the underlying conversion is."]),

78: D("A delegating constructor calls another constructor of the same class in its member initializer list, reusing its initialization logic.",
"""Example: `Connection() : Connection(\"localhost\", 5432) {}`. The target constructor runs completely first, then the delegating constructor's body.

Rules: a delegating constructor's initializer list may contain only the delegation (no other member initializers), and delegation cycles are undefined behaviour (compilers often diagnose them).

Once any constructor completes (including the target), the object is considered constructed, so if the delegating body then throws, the destructor **does** run.""",
"Creating a delegation cycle (A delegates to B, B to A), which is undefined behaviour and usually a stack overflow at runtime.",
["Can a delegating constructor also initialize members? => No; its initializer list may only contain the delegated constructor call.",
 "If the delegating constructor's body throws, does the destructor run? => Yes, because the target constructor already completed."]),

79: D("Construction goes from the base outward: virtual bases, then direct bases in declaration order, then members in declaration order, then the constructor body. Destruction runs in exactly the reverse order.",
"""For `class D : public B { M m; };`: `B()` runs, then `m` is constructed, then `D`'s body. Destruction: `D`'s destructor body, then `~M()`, then `~B()`.

This ordering guarantees that during a class's constructor body, its bases and members are ready, and during its destructor body they still exist. It also explains why virtual calls in constructors don't reach derived overrides: the derived part isn't constructed yet.""",
"Assuming the order in the constructor's initializer list changes construction order; it doesn't, and compilers warn about the mismatch.",
["In what order are multiple bases constructed? => Virtual bases first, then non-virtual bases in the order they're listed in the class definition.",
 "Why are destructors called in reverse order? => Later objects may depend on earlier ones, so they must be destroyed first."]),

80: D("If a constructor throws, the object is never considered constructed: its destructor does not run, but already-constructed members and bases are destroyed in reverse order, and memory from `new` is freed.",
"""This is safe **if** resources are held by members with their own destructors (RAII). It leaks if the constructor acquired a raw resource in its body and then threw before storing it in a managing member.

Example: `buf_ = new char[n]; dev_ = openDevice();` in the body leaks `buf_` if `openDevice` throws, because `~T()` won't run. Holding `buf_` in a `std::unique_ptr<char[]>` fixes it.

Throwing is the idiomatic way to report constructor failure; the alternative (a `valid()` flag or two-phase init) pushes error checking onto every caller.""",
"Allocating several raw resources in the constructor body without RAII members: if a later allocation throws, earlier ones leak because the destructor never runs.",
["Is the destructor called when the constructor throws? => No, but fully constructed members and bases are destroyed.",
 "How do you report constructor failure without exceptions (e.g. `-fno-exceptions` firmware)? => A private constructor plus a static factory returning `std::optional<T>` or `std::expected<T, Error>`."]),

81: D("A destructor can technically throw only if declared `noexcept(false)`, but it should not: destructors are implicitly `noexcept`, so a throw calls `std::terminate`, and throwing during stack unwinding would terminate anyway.",
"""During exception handling, destructors of local objects run; if one of them throws while another exception is active, the program terminates. Standard containers and algorithms also assume destructors don't throw.

Handle failures inside the destructor (log them, swallow them) and offer an explicit `close()` / `flush()` member that can throw, so callers who care about errors can check them before destruction. `std::fstream` follows this pattern.""",
"Letting a flush or close error propagate out of a destructor, which terminates the program as soon as it happens during unwinding.",
["What happens if a destructor throws during stack unwinding? => `std::terminate` is called.",
 "How do you report cleanup errors then? => Provide an explicit `close()` that can throw or return an error, and make the destructor a best-effort fallback."]),

82: D("Making the copy constructor private (the pre-C++11 idiom) prevents copying from outside the class, making the type non-copyable.",
"""Classes that own unique resources (mutexes, file handles, hardware connections, singletons) shouldn't be copied. Before C++11 you declared the copy constructor and copy assignment private and left them undefined (or inherited from `boost::noncopyable`).

Modern C++ uses `= delete`: `T(const T&) = delete; T& operator=(const T&) = delete;`. Deleted functions give clear compile errors at the call site, even for friends and members, whereas private undefined functions only failed at link time inside the class.""",
"Using the old private-and-undefined idiom in new code; `= delete` gives better errors and states intent.",
["Why is `= delete` better than a private copy constructor? => It errors at compile time everywhere (including members and friends) with a clear message.",
 "Can a non-copyable type still be movable? => Yes, e.g. `std::unique_ptr` and `std::thread`: copy deleted, move defined."]),

83: D("`= default` asks the compiler to generate the default implementation of a special member function; `= delete` makes a function unusable, so any call is a compile error.",
"""`= default` is useful to bring back an implicitly suppressed function (a default constructor after adding others), to make a destructor virtual without writing a body (`virtual ~Base() = default;`), or to keep a type trivial (a defaulted function on first declaration can keep triviality; an empty user body `{}` makes it non-trivial).

`= delete` works on any function, not only special members: delete copy operations for unique resources, or delete overloads to block unwanted conversions (`void setSpeed(double) = delete;` next to `void setSpeed(int)`).""",
"Writing `~T() {}` instead of `~T() = default;`: the user-provided destructor makes the type non-trivially destructible and suppresses implicit moves.",
["Can you delete a non-special function? => Yes; deleting overloads prevents calls with unwanted argument types.",
 "Does `= default` on the first declaration keep a type trivial? => Yes, if the defaulted function would be trivial; a user-written empty body does not."]),

84: D("Copy elision is the omission of a copy or move when initializing an object from a temporary or returning a local; since C++17 it is **guaranteed** for prvalues and **optional** (NRVO) for named locals.",
"""Guaranteed (C++17): `T t = T(args);`, `return T(args);`, and passing a prvalue to a by-value parameter construct the object directly in its final place. No copy or move constructor is even required to exist.

Optional: named return value optimization (`T r; ...; return r;`) and some cases with exceptions. When NRVO doesn't happen, returning a local still uses the move constructor automatically.

Consequence: side effects in copy/move constructors (like logging) may not happen, so constructors must not rely on being called for correctness.""",
"Writing `return std::move(local);` to \"help\": it prevents NRVO and forces a move.",
["Can a non-movable type be returned by value? => Yes, since C++17, if the return expression is a prvalue (guaranteed elision).",
 "Why should copy constructors not have required side effects? => Elision may skip them entirely."]),

85: D("Inside a base constructor the object is still of the base type (the derived part doesn't exist yet), so virtual calls dispatch to the base class's version, not the derived override.",
"""The vptr is set to the vtable of the class whose constructor is running. This protects against derived overrides reading derived members that aren't initialized yet. The same logic applies in reverse during destruction.

Calling a pure virtual function this way is undefined behaviour (usually an abort). If derived-specific setup is needed, pass data to the base constructor, use a factory that calls an `init()` after construction, or use CRTP where the type is known statically.""",
"Base constructors calling virtual `configure()` expecting per-device overrides; the base version always runs.",
["What does `typeid(*this)` report inside a base constructor? => The base type, consistent with virtual dispatch at that point.",
 "Is calling a virtual function in a constructor illegal? => No, it's legal and dispatches to the current class; only pure virtual calls are undefined."]),

86: D("A converting constructor is any non-`explicit` constructor callable with a single argument; it lets the compiler implicitly convert that argument type into the class type.",
"""Useful for natural conversions (`std::string s = \"text\";`), dangerous otherwise: with `Timeout(int ms)` non-explicit, a function `wait(Timeout)` accepts `wait(true)` or `wait('A')` because those promote to `int`.

Implicit conversions also participate in overload resolution and operator matching, producing surprising overload choices or ambiguities.

Rule: mark single-argument constructors `explicit` unless the conversion is lossless and obviously intended.""",
"`class Buffer { public: Buffer(std::size_t size); };` lets `buffer = 0;` compile as \"assign a zero-sized buffer\".",
["Do constructors with default arguments count as converting? => Yes, if they can be called with one argument.",
 "How many user-defined conversions can apply implicitly in one conversion sequence? => At most one."]),

87: D("Members are always initialized in the order they are declared in the class, regardless of the order in the initializer list; bases are initialized before members.",
"""The initializer list only supplies values; declaration order controls sequencing, so destruction can run in the exact reverse. Writing the list in a different order is legal but misleading, and `-Wreorder` (part of `-Wall`) warns about it.

The bug appears when one member's initializer uses another member declared **after** it, reading an uninitialized value. Keep the list in declaration order and avoid cross-member dependencies, or compute from constructor parameters instead.""",
"`class Buf { std::size_t cap_; std::vector<char> data_; public: Buf(std::size_t n) : data_(n), cap_(data_.size()) {} };` reads `data_` before it's constructed, because `cap_` is declared (and so initialized) first.",
["Why does C++ use declaration order? => Destruction must be the reverse of construction for every constructor, so the order must be fixed per class.",
 "Which warning catches mismatched initializer order? => `-Wreorder`, enabled by `-Wall` in GCC and Clang."]),

88: D("Without a user-defined destructor, memory allocated with `new` into a raw pointer member is never freed: the implicit destructor destroys the pointer, not the object it points to, so it leaks.",
"""The pointer is a plain value; destroying it does nothing to the pointee. Add a destructor that deletes it, and then (Rule of Three/Five) also handle copy and move, or better, replace the raw pointer with `std::unique_ptr` so the implicit destructor does the right thing.

Tools: AddressSanitizer's leak checker (`-fsanitize=address`), Valgrind, or Visual Studio's CRT debug heap report these leaks.""",
"Fixing the leak by adding only a destructor: copies then double-free. Use `std::unique_ptr` (Rule of Zero) instead.",
["Why doesn't the implicit destructor free the memory? => It destroys each member; destroying a raw pointer is trivial and doesn't touch the pointee.",
 "How do you detect such leaks? => AddressSanitizer / LeakSanitizer, Valgrind, or heap debugging tools."]),

89: D("Yes: private constructors prevent code outside the class from creating objects directly, used by Singleton, named constructors / factory functions, and classes created only by friends.",
"""Patterns relying on private constructors:

- **Singleton**: only `instance()` creates the object.
- **Factory / named constructor**: `static std::optional<Port> open(std::string_view name)` validates and returns nothing on failure, without exceptions.
- **Passkey idiom**: a public constructor taking a private `Key` type, so only friends can call it but `std::make_unique` still works.
- Static-only utility classes (though namespaces are usually better).

Note that `std::make_unique`/`make_shared` can't call private constructors; use the passkey idiom or `std::unique_ptr<T>(new T(...))` inside the class.""",
"Making the constructor private and then trying `std::make_shared<T>()` in a factory: it fails because `make_shared` isn't a friend.",
["What is the passkey idiom? => A public constructor that requires an argument of a private nested type, so only authorized code can construct while `make_unique` still works.",
 "When is a factory with a private constructor better than throwing? => When failure is expected and exceptions are disabled or too costly, e.g. firmware returning `std::optional`."]),

90: D("Placement new (`new (ptr) T(args)`) constructs an object in memory you already own, without allocating; you must later call the destructor explicitly (`p->~T()`) and release the memory yourself.",
"""Uses: memory pools and arenas, containers (`std::vector` constructs elements in raw capacity), embedded systems with static buffers, and objects at fixed addresses (shared memory, DMA regions).

Requirements: the storage must be large enough and suitably aligned (`alignas(T) std::byte buf[sizeof(T)];`). C++17's `std::launder` is sometimes needed when reusing storage for a new object with const or reference members. C++20 adds `std::construct_at` and `std::destroy_at` as safer wrappers.""",
"Placing an object in a `char buffer[sizeof(T)]` without `alignas(T)`: misaligned objects are undefined behaviour and can fault on some architectures.",
["How do you destroy a placement-new object? => Call the destructor explicitly (`p->~T()` or `std::destroy_at(p)`) and then release the storage separately.",
 "What does `std::construct_at` add? => A constexpr-friendly, type-safe wrapper for placement new (C++20)."]),
}
