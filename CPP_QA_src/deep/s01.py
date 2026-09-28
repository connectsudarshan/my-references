DEEP = {

1: D("C++ is a statically typed, compiled, multi-paradigm language that extends C with classes, templates, exceptions, RAII and a standard library, while keeping C's low-level control.",
"""C++ keeps C's memory model, pointers and near-zero-overhead abstractions, and adds tools for building large systems: classes with constructors and destructors (enabling RAII), templates for generic code, exceptions, namespaces, references, operator overloading and the STL.

The guiding principle is the **zero-overhead principle**: you don't pay for features you don't use, and what you do use is as efficient as hand-written code. That's why C++ is common in firmware tools, drivers' user-space layers, game engines, databases and trading systems.

C++ is *mostly* but not fully compatible with C: implicit `void*` conversion, some keywords (`class`, `new`), and designated initializer rules differ. Use `extern "C"` to share functions between the two.""",
"Saying \"C++ is a superset of C\". Valid C such as `int* p = malloc(4);` (implicit conversion from `void*`) does not compile as C++.",
["What is the zero-overhead principle? => Abstractions should cost nothing if unused and be as cheap as hand-written code when used (e.g. templates and inline functions compile to direct code).",
 "Why is `extern \"C\"` needed? => It disables C++ name mangling so C code (or a C ABI) can link to the function by its plain name."]),

2: D("The fundamental types are the built-in arithmetic types (`bool`, character types, integer types, floating-point types) plus `void` and `std::nullptr_t`; their exact sizes are implementation-defined within minimum ranges.",
"""The standard fixes minimums, not exact sizes: `char` is at least 8 bits, `short` and `int` at least 16, `long` at least 32, `long long` at least 64; `sizeof(char)` is always 1. On typical 64-bit Linux (LP64) `long` is 8 bytes, while on 64-bit Windows (LLP64) it is 4.

Character types: `char`, `signed char`, `unsigned char`, `wchar_t`, `char8_t` (C++20), `char16_t`, `char32_t`. Whether plain `char` is signed is implementation-defined.

For hardware registers, binary formats and protocols, use the fixed-width types from `<cstdint>` (`uint8_t`, `int32_t`, `uint64_t`) so layouts don't change between compilers.""",
"Assuming `long` is 64 bits everywhere, or that plain `char` is signed; both differ between Linux and Windows or between x86 and ARM.",
["Why use `uint32_t` instead of `unsigned int` for a register? => Its width is guaranteed; `unsigned int` is only guaranteed to be at least 16 bits.",
 "What is `std::size_t`? => An unsigned type large enough to hold the size of any object; the result type of `sizeof` and the index type of standard containers."]),

3: D("`=` assigns a value (and returns a reference to the left operand); `==` compares two values and returns `bool`.",
"""Because assignment is an expression, `if (x = 5)` compiles: it assigns 5 and then tests the result (non-zero, so true). This is a classic bug that silently changes `x`.

Defences: compile with warnings (`-Wall` gives "suggest parentheses around assignment used as truth value"), and in C++17 use `if (auto v = f(); v == 5)` to separate declaration from the condition. The old "Yoda condition" (`if (5 == x)`) is unnecessary with warnings enabled.

For classes, `operator=` and `operator==` are separate functions; since C++20, `operator==` can be defaulted (`bool operator==(const T&) const = default;`).""",
"Writing `if (status = ERROR)` in error handling: it overwrites `status` and the branch is always taken.",
["Why does `if (x = 0)` never execute its body? => The assignment yields 0, which converts to `false`.",
 "What does C++20 `= default` for `operator==` do? => Generates member-wise equality comparison; `!=` is then synthesized automatically."]),

4: D("A header is a file of declarations (and inline or template definitions) that is textually included into source files so many translation units share the same interface.",
"""`#include` is a literal copy-paste by the preprocessor. Headers let each `.cpp` see the declarations it needs while definitions live in exactly one `.cpp`, which is what makes separate compilation and linking work.

Every header needs an **include guard** (`#ifndef X_H / #define X_H / #endif`) or `#pragma once` so double inclusion doesn't cause redefinitions.

Good practice: include what you use, prefer forward declarations in headers to reduce rebuilds, never put `using namespace std;` in a header (it leaks into every includer), and only put definitions in headers when they are `inline`, templates or `constexpr`. C++20 **modules** (`import`) aim to replace textual inclusion.""",
"Defining a non-inline function or global variable in a header: every `.cpp` that includes it gets its own definition, causing multiple-definition link errors (an ODR violation).",
["Include guard or `#pragma once`? => `#pragma once` is simpler and supported by all major compilers but non-standard; guards are standard and work everywhere.",
 "What problem do C++20 modules solve? => Faster builds and isolation: a module is compiled once, and macros and internal names don't leak into importers."]),

5: D("`::` names a member of a namespace, class or enumeration (`std::vector`, `Class::member`), and with nothing on its left refers to the global namespace (`::x`).",
"""Uses of the scope resolution operator:

- Namespace members: `std::cout`, `math::square(4)`.
- Class static members and nested types: `Config::instance()`, `std::vector<int>::iterator`.
- Defining member functions outside the class: `void Widget::draw() { ... }`.
- Calling a base-class version of an overridden function: `Base::print();`.
- Scoped enumerators: `Color::Red`.
- The global namespace: `::x` bypasses a local or class member of the same name; `::operator new` calls the global allocator.""",
"Relying on `::x` to reach a global shadowed by a local makes code hard to read; rename instead of shadowing.",
["How do you call the base-class implementation from an override? => Qualify it: `Base::method();` inside the derived method.",
 "What does `::operator new(n)` do? => Calls the global allocation function directly, allocating raw memory without constructing an object."]),

6: D("`struct` and `class` define the same kind of type; the only differences are the default member access and default inheritance access (`public` for `struct`, `private` for `class`).",
"""Both can have constructors, virtual functions, templates, access specifiers and inheritance. By convention, `struct` is used for simple data aggregates with public members (plain data, protocol headers), and `class` for types with invariants protected by private members.

Default inheritance: `struct D : B` means public inheritance, `class D : B` means private inheritance, a frequent surprise.

Aggregate initialization (`Point p{1, 2};`) works only for types with no user-declared constructors, no private or protected non-static members and no virtual functions, whichever keyword you use.""",
"Writing `class Derived : Base {}` and expecting public inheritance; it is private, so `Base` members become inaccessible to users of `Derived`.",
["When would you use `struct`? => For passive data with no invariants, like a packed protocol header or a configuration record.",
 "Can a struct have private members and virtual functions? => Yes; only the default access differs."]),

7: D("Storage-class and duration specifiers decide how long an object lives and which translation units can see its name.",
"""Storage duration kinds: **automatic** (block-scope locals, destroyed at the end of the block), **static** (namespace-scope objects and `static` locals, alive for the whole program), **thread** (`thread_local`, one per thread), and **dynamic** (created with `new`, lifetime controlled manually or by smart pointers).

Linkage: `static` at namespace scope (or an unnamed namespace) gives internal linkage, visible only in its translation unit; `extern` declares a name defined elsewhere.

`static` locals are initialized once, on first execution of their declaration, and that initialization is thread-safe since C++11 (\"magic statics\").""",
"Using `static` globals across translation units that depend on each other at startup; their initialization order is unspecified (the \"static initialization order fiasco\").",
["How do you avoid the static initialization order fiasco? => Wrap the object in a function returning a reference to a function-local static (constructed on first use).",
 "What is `thread_local` useful for? => Per-thread state without locking, such as per-thread buffers, random generators or error contexts."]),

8: D("`static` at namespace scope gives a name internal linkage (private to its translation unit); `extern` declares that a name with external linkage is defined somewhere else.",
"""`extern int count;` in a header plus `int count = 0;` in exactly one `.cpp` is the classic way to share a global variable. Functions have external linkage by default, so `extern` on a function declaration is redundant.

`static` has several meanings depending on context: at namespace scope it restricts linkage; on a local variable it gives static storage duration; in a class it creates a member shared by all instances. Modern code prefers an **unnamed namespace** over `static` for internal linkage of types and functions.

C++17 `inline` variables let you define a global in a header once without `extern` gymnastics: `inline int count = 0;`.""",
"Writing `extern int count = 0;` in a header: the initializer turns it into a definition in every translation unit, causing multiple-definition link errors.",
["What does an unnamed namespace do? => Gives everything inside it internal linkage, like `static`, but it also works for types.",
 "What are C++17 inline variables? => Variables that may be defined in several translation units (e.g. in a header) and are merged into one entity by the linker."]),

9: D("A namespace is a named scope that groups declarations so the same identifier can exist in different libraries without collisions.",
"""Namespaces can be reopened across files, nested (`namespace a::b { }` since C++17), aliased (`namespace fs = std::filesystem;`) and anonymous (internal linkage).

**Argument-dependent lookup (ADL)** means an unqualified call like `swap(a, b)` also searches the namespaces of the arguments' types, which is why `std::cout << x` finds `std::operator<<`.

`inline namespace` is used for library versioning: members of `namespace lib { inline namespace v2 { } }` are accessible as `lib::name` while the ABI can distinguish versions.""",
"`using namespace std;` in headers or at global scope: it pulls hundreds of names into every includer and causes ambiguous calls (e.g. a user function named `count` or `distance`).",
["What is argument-dependent lookup? => Unqualified function names are also looked up in the namespaces associated with the argument types.",
 "What is a namespace alias? => A shorter name for a long namespace: `namespace chrono = std::chrono;`."]),

10: D("`#define` is textual substitution by the preprocessor with no type or scope; `const` (and `constexpr`) declares a typed, scoped object the compiler understands.",
"""Macros are replaced before compilation, so errors show up in expanded code, they ignore namespaces, they can't be inspected in a debugger, and function-like macros evaluate arguments multiple times (`#define SQ(x) x*x` breaks for `SQ(a+1)` and `SQ(i++)`).

Prefer `constexpr` for compile-time constants (`constexpr int kQueueDepth = 64;`), `enum class` for related constants, and `inline`/`constexpr` functions or templates instead of function-like macros.

Macros are still legitimate for include guards, conditional compilation (`#ifdef DEBUG`), and cases needing `__FILE__`/`__LINE__` (though C++20 `std::source_location` covers the latter).""",
"`#define MAX(a, b) a > b ? a : b` without parentheses: `MAX(x, y) * 2` expands to `x > y ? x : y * 2`.",
["`const` vs `constexpr`? => `const` means read-only after initialization (possibly at runtime); `constexpr` requires a compile-time constant usable in array sizes and templates.",
 "How does C++20 `std::source_location` replace macros? => It captures file, line and function name as a default argument, without `__FILE__` / `__LINE__` macros."]),

11: D("`inline` is primarily a linkage rule: an inline function (or variable) may be defined in multiple translation units, as long as all definitions are identical; inlining the code is only a hint.",
"""Modern compilers decide what to inline based on their own heuristics, regardless of the keyword. The keyword's real job is allowing definitions in headers without violating the One Definition Rule.

Implicitly inline: functions defined inside a class body, `constexpr` functions, and function templates (effectively).

To force or prevent inlining use compiler attributes (`[[gnu::always_inline]]`, `__forceinline`, `[[gnu::noinline]]`), and only after profiling. Excessive inlining increases code size and instruction-cache pressure, which can make code slower.""",
"Marking large functions `inline` expecting a speed-up: the compiler usually ignores the hint, and if it does inline, code bloat can hurt performance.",
["Why can an inline function be defined in a header without link errors? => The ODR explicitly allows one identical definition per translation unit for inline functions; the linker merges them.",
 "Are member functions defined inside the class body inline? => Yes, implicitly."]),

12: D("By value copies the argument; by pointer passes an address that may be null; by reference passes an alias that must refer to a valid object.",
"""Guidelines (C++ Core Guidelines F.15-F.18):

- Cheap-to-copy types (built-ins, small structs, `std::string_view`, `std::span`): pass by value.
- Read-only access to larger objects: `const T&`.
- Output or in-out parameters: `T&` (or better, return the value).
- Optional arguments where \"no object\" is valid: pointer (`T*`, possibly null) or `std::optional`.
- \"Sink\" parameters the function keeps: pass by value and `std::move` into place.

References can't be reseated or null, which makes interfaces clearer; pointers make optionality explicit.""",
"Passing `std::vector<T>` or `std::string` by value in hot paths, causing a full copy on each call when a `const&` would do.",
["When is pass-by-value better than `const&`? => For small types and for sink parameters that will be moved into storage anyway.",
 "How do you express an optional in-parameter in modern C++? => `const T*` (nullable) or `std::optional<T>`; never a reference that might be \"invalid\"."]),

13: D("Function overloading is declaring several functions with the same name in the same scope that differ in their parameter types, count or qualifiers; the compiler picks one by overload resolution.",
"""Overload resolution ranks candidates by conversion quality: exact match beats promotion (e.g. `char` to `int`), which beats standard conversion, which beats user-defined conversion; ambiguity is a compile error.

What distinguishes overloads: parameter types and count, `const`/`volatile` and ref-qualifiers on member functions (`void f() &` vs `void f() &&`). What doesn't: return type alone, or top-level `const` on by-value parameters (`void f(int)` and `void f(const int)` are the same function).

Overloads are resolved at compile time (static polymorphism), unlike virtual functions.""",
"Overloading `f(int)` and `f(double)` then calling `f(5L)`: `long` converts equally well to both, so the call is ambiguous.",
["Can two functions differ only by return type? => No, calls couldn't be resolved; it's a redeclaration error.",
 "What is the difference between overloading and overriding? => Overloading: same name, different parameters, resolved at compile time. Overriding: same signature in a derived class, resolved at runtime through virtual dispatch."]),

14: D("A default argument is a value the compiler substitutes at the call site when the caller omits trailing arguments.",
"""Rules: defaults must be trailing parameters; they are specified once (usually in the header declaration, not repeated in the definition); and they are evaluated at each call.

Because defaults are inserted at the **call site**, changing a default in a library header requires recompiling callers.

With virtual functions, default arguments are bound by the **static type** of the expression, while the function body is chosen by the dynamic type, so a call through a base pointer uses the base's default even if the derived override declares a different one. Prefer overloads or non-virtual wrappers for virtual functions with defaults.""",
"Declaring different default arguments on a base virtual function and its override: calls through base pointers use the base default with the derived body.",
["Where should default arguments be declared? => Once, in the declaration visible to callers (the header), not again in the definition.",
 "Why are defaults on virtual functions risky? => Defaults come from the static type, bodies from the dynamic type, so behaviour depends on the pointer type used."]),

15: D("`new`/`delete` allocate memory **and** construct/destroy objects, returning typed pointers; `malloc`/`free` only allocate raw bytes from the C heap.",
"""`new T(args)` calls `operator new` then the constructor; on failure it throws `std::bad_alloc` (or returns null with `new (std::nothrow)`). `malloc` returns `void*` and signals failure with null; it never runs constructors.

Pairs must match: `new`/`delete`, `new[]`/`delete[]`, `malloc`/`free`. Mixing them is undefined behaviour.

In modern C++ you rarely call either directly: use `std::make_unique`, `std::make_shared` and containers. `malloc` still appears when interfacing with C APIs; objects placed in such memory need placement `new` (or C++20 implicit object creation rules for trivial types).""",
"Allocating with `new[]` and releasing with `delete` (without `[]`), which is undefined behaviour and may skip destructors or corrupt the heap.",
["What is placement new? => `new (address) T(args)` constructs an object in pre-allocated memory without allocating, used by pools and containers.",
 "Why prefer `std::make_unique` over `new`? => Exception safety and automatic cleanup: ownership is captured immediately, and no `delete` is needed."]),

16: D("`const` expresses that something must not be modified through a given name: a variable, the object a pointer points to, the pointer itself, or `*this` inside a member function.",
"""Read declarations right to left: `const int* p` is a pointer to const int (can't change `*p`); `int* const p` is a const pointer to int (can't reseat `p`); `const int* const p` is both.

A `const` member function (`int size() const;`) promises not to modify observable state and is the only kind callable on const objects; `mutable` members are the exception for caches and mutexes.

Const correctness propagates: taking parameters as `const T&` documents intent, enables calls with temporaries, and lets the compiler catch accidental writes. Casting away const with `const_cast` and then modifying an object that was originally const is undefined behaviour.""",
"Forgetting `const` on member functions that don't modify state: the class then can't be used through `const&` parameters, forcing const to be removed everywhere else.",
["What is the difference between `const int*` and `int* const`? => The first protects the pointee, the second protects the pointer itself.",
 "Why do mutexes in classes often need `mutable`? => Const member functions still need to lock them, and locking modifies the mutex."]),

17: D("A reference is an alias for an existing object; it must be initialized, cannot be reseated to another object, and a valid program can never have a null reference.",
"""Under the hood a reference is usually implemented as a pointer, but the language guarantees it refers to an object, which is why functions taking `T&` don't need null checks.

A **dangling** reference is possible, though: returning a reference to a local variable, or keeping a reference into a `std::vector` element after the vector reallocates.

`const T&` can bind to temporaries and extends the temporary's lifetime to that of the reference (only for references bound directly in a local declaration). Rvalue references (`T&&`) bind to temporaries and enable move semantics.""",
"Returning `const std::string&` to a local string or to a temporary: the reference dangles as soon as the function returns.",
["How can a reference end up \"null\"? => Only through undefined behaviour, such as dereferencing a null pointer to initialize it; a valid program never has one.",
 "What is lifetime extension? => A temporary bound directly to a `const T&` (or `T&&`) local lives as long as that reference."]),

18: D("Name mangling is the compiler's encoding of a function's name, namespace, class and parameter types into a unique linker symbol, which makes overloading possible.",
"""Example with the Itanium ABI (GCC/Clang): `void ns::f(int)` becomes `_ZN2ns1fEi`. MSVC uses a different scheme (`?f@ns@@YAXH@Z`), which is one reason C++ libraries built by different compilers usually can't be linked together.

Consequences: link errors show mangled names (use `c++filt` or `-C` in `nm` to demangle); C code can't call mangled symbols, hence `extern \"C\"`; and exported symbols in shared libraries form part of the ABI.""",
"Declaring a C library's functions without `extern \"C\"` in C++: the linker looks for mangled names and reports undefined references.",
["How do you demangle a symbol? => `c++filt _ZN2ns1fEi` or `nm -C lib.a`.",
 "Why can't you overload `extern \"C\"` functions? => C linkage uses the plain name, so two overloads would produce the same symbol."]),

19: D("A declaration introduces a name and its type; a definition is a declaration that also creates the entity (allocates storage for variables or provides the body of a function or the members of a class).",
"""Examples: `extern int x;` and `void f(int);` and `class Widget;` are declarations; `int x = 0;`, `void f(int) { }` and `class Widget { ... };` are definitions.

A name can be declared many times but (with exceptions for inline entities, templates and classes across translation units) defined only once: the One Definition Rule.

Forward declarations (`class Widget;`) let headers refer to pointers and references to a type without including its full definition, which cuts compile times and breaks include cycles.""",
"Using a forward-declared (incomplete) type by value or calling its members in a header; the compiler needs the full definition for size and member access.",
["When is a forward declaration enough? => When you only use pointers or references to the type, or declare functions taking or returning it.",
 "Is `class Widget;` a declaration or definition? => A declaration (it introduces an incomplete type)."]),

20: D("A translation unit is one source file after preprocessing (all includes expanded and macros replaced); it is the unit the compiler turns into one object file.",
"""Each `.cpp` becomes an independent translation unit; the compiler sees nothing from other `.cpp` files except what headers declare. The linker then combines object files and resolves external symbols.

This model explains many rules: internal linkage (`static`, unnamed namespaces) is per translation unit; templates must usually be defined in headers because each unit instantiates them; and inline functions may be defined once per unit.

Large headers included by hundreds of units dominate build time; precompiled headers, forward declarations, pImpl and C++20 modules reduce that cost.""",
"Putting non-inline definitions in headers: each translation unit that includes them defines the entity again, and the link fails.",
["Why must templates usually be defined in headers? => Each translation unit instantiates templates for the types it uses, so it needs the full definition.",
 "What does unity (jumbo) build mean? => Concatenating many `.cpp` files into one translation unit to reduce repeated header parsing."]),

21: D("Building C++ is four stages: preprocessing (includes, macros), compilation (to assembly/IR), assembly (to object files) and linking (combining objects and libraries into an executable or library).",
"""1. **Preprocess**: `g++ -E` shows the expanded source; includes and macros vanish here.
2. **Compile**: parsing, semantic analysis, template instantiation and optimization produce assembly (`-S`).
3. **Assemble**: machine code into an object file with a symbol table (`-c`).
4. **Link**: resolves symbols across object files and static libraries; with shared libraries some resolution happens at load time.

Link-time optimization (`-flto`) lets the optimizer see across translation units. Knowing which stage failed speeds up debugging: a missing header is a preprocessor error, a type error is compilation, \"undefined reference\" is linking.""",
"Treating \"undefined reference to foo\" as a compiler problem; it's the linker: a definition wasn't compiled, a library wasn't linked, or link order/mangling is wrong.",
["How do you see the preprocessed output? => `g++ -E file.cpp`.",
 "What does LTO do? => Delays optimization to link time so the compiler can inline and optimize across translation units."]),

22: D("`.h` and `.hpp` are only naming conventions; the compiler treats included files identically regardless of extension.",
"""Teams use `.hpp` to signal a C++-only header (classes, templates, namespaces) and `.h` for headers usable from C or shared C/C++ interfaces. Some projects use `.hxx`, `.hh` or `.inl` (inline/template implementation files included from the header).

What matters is consistency within a codebase and the content: headers meant to be consumed by C must avoid C++ features and wrap declarations in `extern \"C\"` guarded by `#ifdef __cplusplus`.""",
"Including a C++-only header (templates, namespaces) from a `.c` file because it is named `.h`.",
["How do you write a header usable from both C and C++? => Use only C constructs and wrap declarations in `#ifdef __cplusplus extern \"C\" { #endif ... }`.",
 "What is an `.inl` or `.tpp` file? => A file holding inline or template definitions, included at the end of the header to keep the interface readable."]),

23: D("The One Definition Rule requires that every non-inline function and variable has exactly one definition in the whole program, and that inline entities, classes and templates defined in several translation units have identical definitions.",
"""Two flavours: within a translation unit, nothing may be defined twice; across the program, non-inline functions and variables are defined once, while classes, inline functions, templates and inline variables may appear in several translation units if the token sequences (and meanings) are identical.

ODR violations across translation units are often **not diagnosed**: two different `struct Config` definitions in different `.cpp` files can link fine and then crash at runtime, because the linker silently picks one inline member function. Tools: `-fsanitize=address` with ODR detection, `-Wodr` with LTO, and unique namespaces.""",
"Defining two different helper classes with the same name (e.g. `Helper`) at global scope in two `.cpp` files: an undiagnosed ODR violation. Put them in unnamed namespaces.",
["Why is an ODR violation dangerous? => The program can link without error and behave incorrectly, since the linker keeps only one of the differing inline definitions.",
 "How do unnamed namespaces prevent ODR problems? => They give internal linkage, so identically named entities in different translation units are distinct."]),

24: D("A shallow copy copies member values as they are (so pointers share the same pointee); a deep copy duplicates the owned resources so each object owns its own.",
"""The implicitly generated copy constructor and assignment copy each member. For a raw owning pointer that means two objects point to the same buffer, and both destructors free it: a double free.

Solutions, in order of preference: don't own raw resources (use `std::vector`, `std::string`, `std::unique_ptr`, which copy correctly or are move-only); if you must, implement the **Rule of Three/Five** (destructor, copy constructor, copy assignment, and move operations), typically with copy-and-swap.

`std::shared_ptr` members give shared ownership, which is a deliberate shallow copy, not a deep one.""",
"Writing a destructor that deletes a raw pointer member but relying on the default copy constructor: copies share the pointer and the program double-frees.",
["What is the Rule of Zero? => Design classes so they need none of the special member functions, by holding resources in RAII members.",
 "What is copy-and-swap? => Implement assignment by copying the argument (by value) and swapping it with `*this`, giving strong exception safety."]),

25: D("Every expression has a value category: an **lvalue** designates an object with identity (you can take its address), a **prvalue** is a pure temporary value, and an **xvalue** is an expiring object (e.g. the result of `std::move`).",
"""Rough test: if you can take its address with `&`, it's an lvalue (`x`, `*p`, `arr[i]`, a function returning `T&`). Literals and expressions like `x + 1` or `f()` returning by value are prvalues. `std::move(x)` yields an xvalue: it still refers to `x`, but marks it as movable.

**glvalue** = lvalue or xvalue (has identity); **rvalue** = prvalue or xvalue (can be moved from).

Why it matters: overload resolution uses value categories. `T&` binds to lvalues, `T&&` to rvalues, `const T&` to both. That's how move constructors are chosen for temporaries and copy constructors for named objects.""",
"Believing a named rvalue reference is an rvalue: inside `void f(Widget&& w)`, `w` is an lvalue, so passing it on requires `std::move(w)` (or `std::forward` in templates).",
["Is `std::move` a move? => No, it's a cast to an xvalue (`static_cast<T&&>`); the actual move happens when a move constructor or assignment is selected.",
 "What category is a string literal? => An lvalue (an array of const char with static storage); other literals like `42` are prvalues."]),

26: D("Undefined behaviour is program behaviour for which the C++ standard imposes no requirements, so the compiler may assume it never happens and the result can be anything.",
"""Common sources: out-of-bounds access, dereferencing null or dangling pointers, use after free, signed integer overflow, data races, reading uninitialized variables, violating strict aliasing, and modifying an object through a pointer after casting away its original `const`.

Optimizers exploit the \"UB never happens\" assumption: a null check after a dereference can be deleted, and a loop with signed overflow can be turned into an infinite loop. So UB can appear to work in debug builds and break in release builds.

Tools: `-fsanitize=address,undefined`, `-fsanitize=thread` for races, compiler warnings (`-Wall -Wextra`), static analysers, and `constexpr` evaluation (UB in constant expressions is a compile error).""",
"Testing that code \"works\" instead of proving it has no UB: behaviour can change with compiler version, optimization level or unrelated edits.",
["How is UB different from unspecified behaviour? => Unspecified behaviour picks one of several valid outcomes (e.g. argument evaluation order); UB imposes no requirements at all.",
 "How do you catch UB at runtime? => Build tests with sanitizers: `-fsanitize=address,undefined` (and `thread` for races)."]),

27: D("The four named casts separate intentions: `static_cast` for well-defined conversions, `dynamic_cast` for checked polymorphic downcasts, `const_cast` to add or remove const/volatile, and `reinterpret_cast` to reinterpret bits between unrelated types.",
"""- `static_cast`: numeric conversions, `void*` to typed pointer, up/down casts in a hierarchy without runtime checks (downcasting to the wrong type is UB).
- `dynamic_cast`: requires a polymorphic base (a virtual function); returns `nullptr` for pointers or throws `std::bad_cast` for references on failure; has runtime cost (RTTI).
- `const_cast`: for calling legacy APIs that aren't const-correct; modifying an originally const object is UB.
- `reinterpret_cast`: pointer to integer, unrelated pointer types; almost always implementation-specific, and accessing an object through an incompatible type violates strict aliasing. For type punning use `std::memcpy` or C++20 `std::bit_cast`.

Avoid C-style casts `(T)x`: they silently try all of the above, including the dangerous ones.""",
"Using `reinterpret_cast<float*>(&some_int)` to read the bits of an int as a float: undefined behaviour under strict aliasing; use `std::bit_cast<float>(some_int)`.",
["Why are named casts better than C-style casts? => They state intent, are searchable, and the compiler rejects casts that don't fit that intent.",
 "What does `dynamic_cast` need to work? => A polymorphic type (at least one virtual function) and RTTI enabled."]),

28: D("Header-only libraries place all definitions in headers (inline or templates), while compiled libraries keep declarations in headers and definitions in `.cpp` files built into object code.",
"""Header-only: easy to integrate (just include), required for templates anyway, allows inlining across the boundary. Costs: longer compile times (every translation unit parses everything) and every change rebuilds all users.

Separate `.h`/`.cpp`: faster incremental builds, implementation hidden, stable ABI possible with techniques like pImpl, but consumers must link the library and ABI compatibility matters.

Many libraries mix both: templates in headers, heavy non-template code compiled (Boost offers both modes for some libraries; fmt and spdlog can be header-only or compiled).""",
"Making a large non-template library header-only for convenience, then paying for it with minutes of extra compile time across hundreds of files.",
["Why are template libraries usually header-only? => Templates are instantiated per translation unit and need their full definition there (unless explicitly instantiated).",
 "What is explicit instantiation used for? => Compiling a template once for known types in a `.cpp` (`template class Foo<int>;`) to cut compile times and keep definitions out of headers."]),

29: D("RVO (return value optimization) constructs a returned temporary directly in the caller's storage; NRVO does the same for a named local variable; both remove the copy or move.",
"""Since C++17, eliding the copy for a **prvalue** return (`return Widget{...};`) is guaranteed, so it works even for types that aren't copyable or movable. NRVO (`Widget w; ...; return w;`) is still an optimization the compiler may skip, for example when different branches return different named objects.

When elision doesn't happen, returning a local by value still moves automatically (implicit move), so there's no need to write `return std::move(w);`, and doing so actually **prevents** NRVO.

This is why returning large objects by value (vectors, strings) is the idiomatic, efficient choice.""",
"Writing `return std::move(local);`: it disables NRVO and forces a move where no operation would have been needed.",
["Is RVO guaranteed? => For prvalues since C++17, yes (mandatory copy elision); NRVO remains optional.",
 "What happens if NRVO doesn't apply? => The returned local is treated as an rvalue and moved (or copied if it has no move constructor)."]),

30: D("C++ is statically typed (types are checked at compile time) and fairly strongly typed, but it allows several implicit conversions inherited from C, so it is weaker than languages like Rust or Haskell.",
"""Static vs dynamic typing is about **when** types are checked (compile time vs runtime); strong vs weak is about how freely the language converts between types.

C++ weak spots: implicit numeric conversions and narrowing (`int i = 3.7;`), integer promotions, array-to-pointer decay, implicit bool conversions, and user-defined implicit conversions.

Ways to strengthen it: brace initialization (narrowing becomes an error), `explicit` constructors and conversion operators, `enum class`, strong typedefs (wrapper types like `struct Lba { uint64_t v; };`), and warnings such as `-Wconversion`.""",
"Declaring single-argument constructors without `explicit`, allowing surprising implicit conversions like passing `42` where a `Buffer` was expected.",
["How does brace initialization help type safety? => Narrowing conversions (like double to int) inside `{}` are compile errors.",
 "What is a strong typedef? => A small wrapper type (e.g. `struct Lba`) so values with different meanings can't be mixed accidentally, at zero runtime cost."]),
}
