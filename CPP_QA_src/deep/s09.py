DEEP = {

246: D("A template is a blueprint for generating functions, classes, variables or aliases parameterized by types, values or other templates; the compiler instantiates concrete code for each set of arguments used.",
"""Templates are C++'s mechanism for generic programming and compile-time polymorphism: `std::vector<T>`, `std::sort`, `std::max` are all templates. The generated code is as efficient as hand-written type-specific code.

Kinds: function templates, class templates, variable templates (C++14), alias templates (C++11), and C++20 concepts to constrain them. Parameters can be types, non-type values (integers, pointers, and in C++20 floating point and literal class types), or templates.""",
"Expecting templates to be \"compiled once\" like normal functions; each distinct argument set produces separate code, which affects build time and binary size.",
["What kinds of template parameters exist? => Type, non-type (value) and template template parameters.",
 "Are templates resolved at runtime? => No; instantiation and dispatch happen at compile time."]),

247: D("A function template generates functions (`template<class T> T max(T a, T b)`) and its arguments are usually deduced from the call; a class template generates classes (`template<class T> class Stack`) whose arguments are specified or deduced via CTAD.",
"""Function templates can be overloaded with other templates and non-templates, and participate in overload resolution. Class templates can be partially specialized; function templates can't (overload them instead).

Member functions of class templates are instantiated only if used, so a `Stack<T>` whose `print()` requires `operator<<` still works for types without it as long as `print()` isn't called.""",
"Trying to partially specialize a function template; that's not allowed, and full specializations of function templates don't participate in overload resolution the way people expect. Use overloading.",
["Why prefer overloading over specializing function templates? => Specializations don't take part in overload resolution; overloads do, which gives more predictable results.",
 "When are member functions of a class template instantiated? => Only when they're used."]),

248: D("Template argument deduction is the process by which the compiler infers template parameters from the types of function call arguments, following specific rules for references, const and arrays.",
"""Key rules for `template<class T> void f(P param)`:

- `P = T` (by value): references and top-level const are dropped; arrays and functions decay to pointers.
- `P = T&`: const is kept in `T`; arrays keep their size.
- `P = T&&` (forwarding reference): lvalues deduce `T` as `X&`, rvalues as `X`, enabling perfect forwarding.

Deduction fails if parameters conflict (`max(1, 2.0)` deduces `int` and `double` for the same `T`). `auto` variables follow the same rules (except braced initializers).""",
"Calling `std::max(n, 10L)` with an `int` and a `long`: deduction conflicts and compilation fails; use `std::max<long>(n, 10L)`.",
["What is a forwarding reference? => A `T&&` parameter where `T` is deduced; it binds to both lvalues and rvalues.",
 "Why does `auto x = arr;` give a pointer? => `auto` uses by-value deduction rules, under which arrays decay."]),

249: D("Yes: template parameters can have default arguments, e.g. `template<class T, class Alloc = std::allocator<T>> class vector;`, and since C++11 function templates can too.",
"""Defaults are used when arguments aren't specified or deduced. For class templates, defaults must be trailing (like function default arguments); for function templates, a defaulted parameter can come before others if the later ones are deduced.

Defaults are common for allocators, comparators (`std::less<Key>`), hashers and policies, letting typical users write `std::map<K, V>` while experts customize.""",
"Changing a default template argument in a library and breaking ABI, since the default becomes part of every user's instantiated type.",
["Can function templates have default template arguments? => Yes, since C++11.",
 "Where does the STL use defaults heavily? => Allocators, comparators and hash functions in containers."]),

250: D("Template specialization provides a custom implementation of a template for specific template arguments, replacing the generic version for those arguments.",
"""Full specialization: `template<> struct Hash<Device> { ... };` for exactly one argument set. Partial specialization (class templates only): `template<class T> struct IsPointer<T*> : std::true_type {};` for a pattern of arguments.

Uses: optimized implementations (`std::vector<bool>`), traits (`std::hash<MyType>`), and handling special cases. Specializations must be declared before first use that would instantiate the primary template with those arguments.""",
"Declaring a specialization after code has already used (and instantiated) the primary template for those arguments, which is ill-formed, no diagnostic required.",
["How do you make a custom type hashable for unordered containers? => Specialize `std::hash<MyType>` (or pass a hasher).",
 "Can you specialize a member function of a class template? => Yes, a full specialization of a member of a specific instantiation."]),

251: D("A full (explicit) specialization fixes all template arguments (`template<> class Buffer<char>`); a partial specialization fixes only some or matches a pattern (`template<class T> class Buffer<T*>`) and is allowed only for class and variable templates.",
"""The compiler picks the most specialized matching partial specialization; ambiguity between two equally specialized ones is an error.

Function templates can't be partially specialized; instead overload them or dispatch to a class template (tag dispatching, `if constexpr`, or concepts).""",
"Trying to write `template<class T> void f<T*>(T*)`; it's ill-formed. Write an overload `template<class T> void f(T*)` instead.",
["How is the best partial specialization chosen? => By partial ordering: the most specialized match wins.",
 "How do you emulate partial specialization for functions? => Overloading, or forwarding to a partially specialized class template."]),

252: D("A non-type template parameter is a compile-time value (integer, enum, pointer, reference; since C++20 also floating-point and structural class types) used as a template argument, e.g. `std::array<int, 16>`.",
"""Values become part of the type, so `Buffer<256>` and `Buffer<512>` are different types, and the compiler can optimize with the constant (unroll loops, size arrays).

C++17 allows `template<auto N>` to deduce the type; C++20 allows class types with public members (e.g. fixed strings as template arguments). Uses: fixed-size buffers, compile-time register addresses and bit widths in firmware, unit systems.""",
"Using many distinct non-type values (e.g. every buffer size) as template arguments, generating a separate instantiation for each and bloating the binary.",
["What does `template<auto N>` do? => Deduces the type of the non-type parameter from the argument (C++17).",
 "Can a string be a template argument? => In C++20, via a structural class type wrapping a fixed-size char array."]),

253: D("SFINAE (Substitution Failure Is Not An Error) means that if substituting template arguments into a function template's signature produces an invalid type or expression, that overload is silently removed from the candidate set instead of causing a compile error.",
"""It enables constraining templates: `template<class T, std::enable_if_t<std::is_integral_v<T>, int> = 0> void f(T)` only participates for integral types. Only errors in the **immediate context** (the signature) are SFINAE; errors inside the function body are hard errors.

C++20 concepts and `requires` clauses replace most SFINAE with clearer syntax and far better error messages.""",
"Expecting an error inside a function template's body to be SFINAE; body errors are hard errors after the overload is chosen.",
["What is the immediate context? => The function's signature and template parameters, where substitution failures are soft errors.",
 "What replaced SFINAE in modern C++? => Concepts and `requires` clauses (C++20)."]),

254: D("Inside a template, `typename` tells the compiler that a **dependent qualified name** (a name depending on a template parameter, like `T::value_type`) refers to a type.",
"""Without it, the compiler assumes `T::value_type` is a value, so `T::value_type x;` fails to parse. Write `typename T::value_type x;` or use an alias `using V = typename T::value_type;`.

C++20 relaxes the requirement in contexts where only a type can appear (e.g. return types, alias declarations, member types). Similarly, `template` is needed to call a dependent member template: `obj.template get<0>()`.""",
"Omitting `typename` before `T::iterator` in older code or unusual contexts, producing cryptic \"expected primary-expression\" errors.",
["Why can't the compiler figure it out itself? => Until instantiation, `T::name` might be a type or a value, and parsing needs to know which.",
 "When do you need the `template` keyword in a call? => When calling a member template on a dependent object: `x.template f<int>()`."]),

255: D("Variadic templates (C++11) take any number of template arguments through a parameter pack (`template<class... Ts>`), enabling type-safe functions and classes with arbitrary arity.",
"""They power `std::tuple`, `std::variant`, `std::make_unique(args...)`, `std::thread(f, args...)`, `emplace_back(args...)` and `std::format`.

Packs are expanded with `...` (`f(args...)`, `std::forward<Ts>(args)...`), processed recursively (head/tail), with C++17 fold expressions (`(args + ...)`), or with `if constexpr`. `sizeof...(Ts)` gives the pack size. Unlike C varargs (`...` with `va_list`), variadic templates are fully type-checked.""",
"Writing deep recursive instantiations to process packs where a C++17 fold expression would be simpler and compile faster.",
["How do you perfect-forward a pack? => `f(std::forward<Args>(args)...)` with `Args&&... args` parameters.",
 "What does `sizeof...(Args)` return? => The number of elements in the pack."]),

256: D("A template is part of the language, type-checked and scoped, generating code at compile time; a macro is textual substitution by the preprocessor with no types, scopes or evaluation rules.",
"""Templates respect namespaces, access control and overload resolution, evaluate arguments once, can be debugged and stepped through, and give (with concepts) meaningful errors. Macros ignore all of that: `#define MAX(a,b) ((a)>(b)?(a):(b))` evaluates an argument twice (`MAX(i++, j)`), pollutes every scope, and hides errors.

Macros remain useful for conditional compilation, include guards and capturing `__FILE__`/`__LINE__` (partly replaced by `std::source_location`).""",
"Writing a function-like macro for a generic helper (`SWAP`, `MIN`) when a function template is safer and just as fast.",
["Why do macros evaluate arguments multiple times? => Each occurrence of the parameter is textually replaced by the argument expression.",
 "What remains a legitimate use for macros? => Conditional compilation, include guards, and some logging/assert helpers."]),

257: D("Instantiation is the compiler generating a concrete function or class from a template for specific arguments; implicit instantiation happens when the template is used with those arguments in a way that requires its definition.",
"""Using `std::vector<Device>` instantiates the class (its declarations), and each member function is instantiated only when used. Function templates are instantiated when called (or their address taken).

Each translation unit instantiates what it uses; the linker then deduplicates identical instantiations (they're emitted as weak/COMDAT symbols). Explicit instantiation (`template class Foo<int>;`) forces it, and `extern template` suppresses it in other units.""",
"Assuming an error in a member function will appear as soon as the class template is used; it appears only when that member is instantiated.",
["How does the linker handle the same instantiation in many object files? => They're weak/COMDAT symbols, and it keeps one copy.",
 "What does `extern template class Foo<int>;` do? => Tells this translation unit not to instantiate it, relying on an explicit instantiation elsewhere."]),

258: D("Templates must usually be defined in headers because the compiler needs the full definition in every translation unit that instantiates them with new arguments; a separately compiled `.cpp` can't know which instantiations other files will need.",
"""If the definition is only in `foo.cpp`, other files can declare and call `f<int>`, but nothing generates `f<int>`, causing \"undefined reference\" link errors.

Alternatives: explicit instantiation in the `.cpp` for a known set of types (`template void f<int>(int);`), which keeps definitions private and speeds builds; or C++20 modules, which export templates without textual headers.""",
"Moving template definitions into a `.cpp` for tidiness and getting link errors for every new type used.",
["When can template definitions live in a `.cpp`? => When you explicitly instantiate all needed argument combinations there.",
 "How do modules change this? => A module interface can export templates; importers get them without textual inclusion."]),

259: D("`std::enable_if<Cond, T>` has a nested `type` only when `Cond` is true, so using `std::enable_if_t<Cond>` in a template's signature removes that overload via SFINAE when the condition is false.",
"""Typical forms: as a return type (`std::enable_if_t<std::is_integral_v<T>, T> f(T)`), a defaulted template parameter (`std::enable_if_t<cond, int> = 0`), or a function parameter default. It's used to select overloads by type properties or to disable constructors (e.g. perfect-forwarding constructors that would hijack copies).

In C++20 prefer concepts: `template<std::integral T> T f(T)` or `requires std::integral<T>`, which read better and produce better errors.""",
"Putting `enable_if` in a defaulted template type parameter (`typename = enable_if_t<...>`) for two overloads that differ only in that default: they're redeclarations, not overloads.",
["Why use `std::enable_if_t<cond, int> = 0` instead of `typename = ...`? => Non-type parameters make the conditions part of the signature, so overloads differing only in the condition don't clash.",
 "What's the C++20 replacement? => Concepts and `requires` clauses."]),

260: D("A template template parameter is a template parameter that itself accepts a template (not a type), e.g. `template<template<class...> class Container> class Registry` which can be instantiated as `Registry<std::vector>`.",
"""It lets a class decide the element type while the user chooses the container kind: inside `Registry`, `Container<Device>` is used. Declaring it variadic (`template<class...> class C`) makes it accept templates with extra defaulted parameters like allocators.

Many uses can be replaced by passing a fully specified type or by traits/rebinding (as allocators do), which is often simpler.""",
"Declaring `template<template<class> class C>` and then failing to pass `std::vector`, whose template has two parameters (with a default); use `template<class...> class C`.",
["Why use a variadic template template parameter? => To accept templates that have additional (often defaulted) parameters.",
 "What's an alternative to template template parameters? => Passing a concrete type or a metafunction/trait that produces the type."]),

261: D("CTAD (class template argument deduction, C++17) lets the compiler deduce class template arguments from constructor arguments, so you can write `std::pair p{1, 2.5};` or `std::vector v{1, 2, 3};` without spelling out the types.",
"""Deduction uses the constructors (implicit guides) plus user-written **deduction guides**, e.g. `template<class It> Buffer(It, It) -> Buffer<typename std::iterator_traits<It>::value_type>;`.

It simplifies code with lock guards (`std::lock_guard lk(mtx);`) and containers, but beware surprises: `std::vector v{v2};` copies (deduces `vector<int>` from a vector) rather than creating a vector of vectors, and string literals deduce `const char*` rather than `std::string`.""",
"Writing `std::vector v{\"a\", \"b\"};` expecting `vector<std::string>`; CTAD deduces `vector<const char*>`.",
["What is a deduction guide? => A declaration telling CTAD how to deduce template arguments from constructor arguments.",
 "Does CTAD work for aggregates? => Yes, since C++20 aggregates get implicit deduction guides."]),

262: D("C++20 concepts are named compile-time predicates on template arguments (e.g. `std::integral`, `std::ranges::range`) used in `requires` clauses or constrained parameters, replacing SFINAE tricks with readable constraints and clear error messages.",
"""Example: `template<std::floating_point T> T mean(std::span<const T>)`. A custom concept: `template<class D> concept BlockDevice = requires(D d, std::uint64_t lba, std::span<std::byte> buf) { d.read(lba, buf); d.write(lba, buf); };`.

Benefits over SFINAE: constraints are part of the interface and documentation; errors say which requirement failed; overloads can be ordered by subsumption (more constrained wins); and syntax is shorter (`void f(std::integral auto x)`).""",
"Writing concepts that only check syntax (\"has a `read` method\") while ignoring semantics (what `read` must do); concepts can't enforce semantics, so document them.",
["What is subsumption? => When one concept's constraints imply another's, the more constrained overload is preferred.",
 "How do you write a constrained parameter concisely? => `void f(std::integral auto x)` (abbreviated function template)."]),

263: D("Expression SFINAE removes an overload when an **expression** in its signature is invalid for the given types (e.g. `decltype(t.begin())`), whereas classic type SFINAE fails on an invalid **type** (e.g. a missing nested `type`).",
"""Expression SFINAE (fully supported since C++11) lets you test for capabilities directly: `template<class T> auto size(const T& t) -> decltype(t.size())` exists only for types with a `size()` member. `std::void_t<decltype(...)>` builds detection traits on the same idea.

C++20 `requires` expressions express this cleanly: `requires(T t) { t.size(); }`.""",
"Writing a detection trait that checks for a member but uses it in the function body instead of the signature; the check then isn't SFINAE-friendly.",
["What is `std::void_t` used for? => Building detection idioms: it maps any valid types to `void`, failing via SFINAE if an expression is invalid.",
 "How does C++20 express the same check? => A `requires` expression inside a concept or `requires` clause."]),

264: D("Variable templates (C++14) are variables parameterized by template arguments, e.g. `template<class T> constexpr T pi = T(3.14159265358979323846L);`, used as `pi<float>`.",
"""They're the idiom behind the `_v` type-trait helpers (`std::is_integral_v<T>` is `std::is_integral<T>::value`), and useful for per-type constants (maximum register widths, default timeouts per device class).

They can be specialized like class templates and are usually `constexpr` or `inline` to avoid ODR issues.""",
"Defining a non-constexpr, non-inline variable template in a header and running into multiple-definition problems.",
["What are the `_v` helpers? => Variable templates providing a trait's `::value`, e.g. `std::is_same_v<A, B>`.",
 "Can variable templates be specialized? => Yes, fully and partially."]),

265: D("`if constexpr` (C++17) evaluates its condition at compile time and discards the branch not taken, so the discarded code isn't instantiated and may contain code that would be invalid for the current template arguments.",
"""Example: `if constexpr (std::is_integral_v<T>) return x % 2; else return std::fmod(x, 2.0);` compiles for both ints and doubles, whereas a regular `if` would need both branches valid for every `T`.

It replaces many uses of tag dispatch and SFINAE overload sets. The discarding only happens inside templates; in non-template code, both branches must still be well-formed.""",
"Using a regular `if` with a type-trait condition inside a template and getting compile errors from the branch that should never run.",
["Is the discarded branch type-checked? => Only for things independent of template parameters; dependent code isn't instantiated.",
 "Does `if constexpr` discard code outside templates? => No; the discarded statement must still be valid there."]),

266: D("Template metaprogramming computes with types and values through template instantiation (recursive templates, specializations); `constexpr` functions compute values at compile time using ordinary C++ syntax.",
"""TMP was the only compile-time computation tool before C++11: factorials as recursive class templates, type lists and traits. It's powerful for **type** computations but hard to read and slow to compile.

`constexpr` (C++11, greatly expanded in C++14/17/20) handles value computations naturally with loops, variables, and even `std::vector` and `std::string` inside constant evaluation (C++20). `consteval` forces compile-time evaluation. Modern rule: use constexpr for values, templates/traits/concepts for types.""",
"Writing recursive template metaprograms for numeric calculations (lookup tables, CRCs) that a `constexpr` function would express in a few readable lines.",
["What does `consteval` add? => Functions that must be evaluated at compile time (immediate functions).",
 "Can you use `std::vector` in constexpr code? => Yes, since C++20, as long as allocations are freed within the constant evaluation."]),

267: D("A fold expression (C++17) reduces a parameter pack with a binary operator in one expression, e.g. `(args + ...)` or `(std::cout << ... << args)`, replacing recursive template functions.",
"""Forms: unary right `(pack op ...)`, unary left `(... op pack)`, and binary forms with an initial value `(init op ... op pack)`. Empty packs are only allowed for `&&` (true), `||` (false) and `,` (void).

Common idioms: `(f(args), ...)` to call a function for each argument in order; `(std::is_integral_v<Ts> && ...)` for checks; `((sum += args), ...)`.""",
"Using an empty-pack unary fold with `+`, which is ill-formed; add an initial value (`(0 + ... + args)`).",
["How do you call a function for each pack element in order? => A comma fold: `(f(args), ...);`.",
 "Which operators allow empty unary folds? => `&&`, `||` and the comma operator."]),

268: D("Two-phase lookup checks template code twice: non-dependent names are looked up when the template is defined, dependent names (those depending on template parameters) when it's instantiated; this is why `typename` and `template` disambiguators are needed for dependent names.",
"""Consequences:

- Names from a **dependent base class** aren't found by unqualified lookup in phase one; use `this->member` or `Base<T>::member`.
- A dependent qualified name is assumed to be a value unless prefixed with `typename`.
- A dependent member template needs `template` before its name when explicit arguments are given (`obj.template get<0>()`).

MSVC historically deferred all lookup (accepting code other compilers reject); `/permissive-` enables conforming two-phase lookup.""",
"Calling a member of a templated base class without `this->` and getting \"not declared in this scope\" on GCC/Clang while it compiled on old MSVC.",
["Why do you need `this->` for dependent base members? => Unqualified names aren't looked up in dependent bases during the first phase.",
 "What does MSVC's `/permissive-` do here? => Enables standard two-phase lookup, catching code that only non-conforming MSVC accepted."]),

269: D("Template bloat is excessive machine code from instantiating templates for many argument combinations, increasing binary size, instruction-cache pressure and build times.",
"""Mitigations:

- **Thin template / type erasure**: move type-independent code into a non-template base (e.g. a `void*`-based container core with thin typed wrappers).
- **Explicit instantiation** with `extern template` to instantiate common cases once.
- Avoid unnecessary non-type parameters (e.g. buffer sizes as runtime values).
- Linker identical code folding (`--icf=all`, MSVC `/OPT:ICF`) merges identical instantiations.
- Measure with tools like `bloaty` or `nm --size-sort`.

In embedded firmware, flash size makes this especially important.""",
"Making buffer size a template parameter throughout a firmware stack, creating a separate copy of every function for each size used.",
["What is identical code folding? => A linker optimization merging functions with identical machine code.",
 "How does the thin template idiom work? => A non-template base implements the logic on untyped data; templated wrappers only add type safety."]),

270: D("Policy-based design composes behaviour from template parameters (policies) chosen at compile time; runtime polymorphism composes behaviour through virtual interfaces chosen at runtime.",
"""Policies (e.g. `template<class Locking, class Checking> class Buffer`) give zero-overhead customization, inlining and compile-time errors, but every combination is a distinct type (no single container of mixed buffers) and choices can't change at runtime. Popularized by Andrei Alexandrescu's *Modern C++ Design*; the STL's allocators and comparators are policies.

Runtime polymorphism (strategy objects behind interfaces) allows configuration-driven choices and heterogeneous collections, at the cost of indirect calls and allocation.""",
"Using policies for choices that actually come from configuration files at runtime, forcing awkward switch statements to pick among instantiated types.",
["When is policy-based design a good fit? => When behaviour is known at compile time and performance matters, e.g. locking or bounds-checking policies.",
 "Can you store `Buffer<LockPolicy, NoCheck>` and `Buffer<NoLock, Check>` in one container? => Not directly; they're unrelated types without a common base."]),

271: D("C++20 abbreviated function templates let you declare a template using `auto` in parameter types: `auto add(auto a, auto b)` is shorthand for a function template with one invented type parameter per `auto`.",
"""Each `auto` parameter is a separate template parameter, so `add(1, 2.5)` works (int and double). Constrained forms read naturally: `void log(std::integral auto value)` or `void save(const std::ranges::range auto& r)`.

It's the function counterpart of generic lambdas (`[](auto x) {}`, C++14). Because these are templates, their definitions must be visible where they're used (headers).""",
"Assuming `auto add(auto a, auto b)` forces both arguments to the same type; each `auto` is an independent template parameter.",
["Is an abbreviated function template still a template? => Yes; it must be defined where visible and is instantiated per argument types.",
 "How do you constrain an `auto` parameter? => Put a concept before it: `std::integral auto x`."]),

272: D("A type trait is a template that answers a compile-time question about a type (`std::is_integral<T>`, `std::is_trivially_copyable<T>`) or transforms one (`std::remove_cvref<T>`, `std::make_unsigned<T>`), exposing the result as `::value` or `::type`.",
"""Traits are typically implemented with specializations (`is_pointer<T*>` is true) or compiler intrinsics. Helpers `_v` and `_t` shorten usage.

They drive `if constexpr`, `static_assert`, SFINAE and concepts: e.g. using `memcpy` for trivially copyable types, or `static_assert(std::is_standard_layout_v<RegBlock>)` for structs mapped onto hardware registers. You can write your own traits for your types (`is_device_handle<T>`).""",
"Adding specializations to most standard type traits for your own types: it's undefined behaviour for traits the standard says must not be specialized (e.g. `std::is_integral`).",
["What does `std::remove_cvref_t<T>` do? => Removes references and const/volatile qualifiers (C++20).",
 "Why check `std::is_trivially_copyable_v` before `memcpy`? => Byte-copying non-trivially-copyable objects is undefined behaviour."]),

273: D("`std::declval<T>()` produces a (fake) rvalue reference to `T` usable only in unevaluated contexts like `decltype` and `noexcept`, so you can reason about expressions involving `T` even if `T` isn't default-constructible.",
"""Example: `using R = decltype(std::declval<F>()(std::declval<Args>()...));` computes the result type of calling `F` with `Args`, which is how `std::invoke_result` works.

It has no definition; odr-using it (calling it in evaluated code) is a compile error. In C++20, `requires` expressions often express the same idea with declared parameters.""",
"Calling `std::declval<T>()` in normal code; it's only declared, so using it outside `decltype`/`sizeof`/`noexcept` fails.",
["Why not use `T()` in `decltype`? => `T` might not be default-constructible; `declval` works for any type.",
 "Which standard trait relies on `declval`? => `std::invoke_result` (and `std::common_type`, among others)."]),

274: D("The most vexing parse is a C++ grammar rule by which a statement that could be read as a function declaration is treated as one, e.g. `Timer t(Clock());` declares a function `t` instead of an object.",
"""`std::vector<int> v(std::istream_iterator<int>(file), std::istream_iterator<int>());` is the classic example: it declares a function. In generic code this can hide inside templates where arguments are types.

Fixes: brace initialization (`Timer t{Clock{}};`), extra parentheses around arguments, or `auto t = Timer(Clock());`. Compilers warn (`-Wvexing-parse` in Clang).""",
"Writing `Widget w();` to call the default constructor; it declares a function returning `Widget`.",
["How does brace initialization avoid the vexing parse? => Braces can't form a function declaration, so it's always an object definition.",
 "Is `Widget w();` an object? => No, it's a function declaration; use `Widget w;` or `Widget w{};`."]),

275: D("Explicit instantiation (`template class Stack<int>;` or `template void f<int>(int);`) forces the compiler to generate a template's code for specific arguments in one translation unit.",
"""Combined with `extern template class Stack<int>;` in a header, other translation units skip instantiating it and link to the single copy, cutting compile time and object size for heavily used instantiations.

It also lets template definitions live in a `.cpp` (hidden implementation) when the set of supported types is known, e.g. a numeric library supporting `float` and `double` only. The standard library uses it for common cases like `std::basic_string<char>`.""",
"Declaring `extern template` in headers but forgetting the explicit instantiation in exactly one `.cpp`, causing link errors.",
["What does `extern template` do? => Suppresses implicit instantiation in the current translation unit, relying on an explicit instantiation elsewhere.",
 "Where does the standard library use explicit instantiation? => For common specializations like `std::string` (`basic_string<char>`) to reduce compile time."]),
}
