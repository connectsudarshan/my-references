DEEP = {

326: D("`auto` (C++11) lets the compiler deduce a variable's type from its initializer, removing verbose or unknowable type names.",
"""It shines for iterator types (`auto it = m.find(k);`), lambdas (whose types can't be written), and template-heavy expressions. It also prevents accidental conversions: `auto n = v.size();` keeps `size_t` rather than truncating to `int`, and forces initialization.

Deduction follows template rules: top-level const and references are dropped (`auto x = cref;` copies); use `auto&`, `const auto&` or `auto&&` to keep references. `decltype(auto)` preserves exactly. Style: use `auto` where the type is obvious or irrelevant; spell it out where it documents intent.""",
"`for (auto x : bigObjects)` copies every element; use `const auto&` (or `auto&` to modify).",
["What does `auto` drop during deduction? => Top-level const/volatile and references; arrays decay to pointers.",
 "What's the pitfall with `auto` and proxy types? => `auto b = vecBool[0];` stores a proxy, not a `bool`."]),

327: D("A lambda expression creates an anonymous function object inline: `[captures](params) -> ret { body }`, typically used for callbacks, predicates and short algorithms.",
"""The compiler generates a unique closure class with captured variables as members and `operator()` as the body. Lambdas are easily inlined, so `std::sort(v.begin(), v.end(), [](auto& a, auto& b){ return a.lat < b.lat; })` is as fast as a hand-written comparator.

Evolution: generic lambdas (C++14), init-captures (`[p = std::move(ptr)]`, C++14), `constexpr` lambdas (C++17), template lambdas and captures of structured bindings (C++20), and deducing `this` (C++23) for recursive lambdas. Captureless lambdas convert to function pointers.""",
"Capturing by reference (`[&]`) in a lambda that is stored and called later (thread, callback), after the captured locals are gone.",
["Can a lambda convert to a function pointer? => Yes, if it captures nothing.",
 "What is an init-capture? => A capture that initializes a new member, e.g. `[buf = std::move(buffer)]`, allowing move-only captures."]),

328: D("`nullptr` (C++11) is a null pointer literal of type `std::nullptr_t` that converts to any pointer type but not to integers, unlike `NULL` (often `0` or `0L`) and `0`.",
"""With overloads `void f(int)` and `void f(Device*)`, `f(NULL)` calls the `int` version (or is ambiguous), while `f(nullptr)` calls the pointer version. In templates, `NULL` deduces as an integer type, breaking forwarding (`std::make_unique<T>(NULL)` passes an int).

Always use `nullptr` in C++ code; tools like clang-tidy's `modernize-use-nullptr` convert old code automatically.""",
"Passing `NULL` through a perfect-forwarding factory to a constructor expecting a pointer; it arrives as an `int` and fails to compile (or picks a wrong overload).",
["What is the type of `nullptr`? => `std::nullptr_t`.",
 "Why does `NULL` break perfect forwarding? => It deduces as an integer type, which can't convert to a pointer inside the forwarded call."]),

329: D("The range-based for loop (`for (auto& x : range)`) iterates over every element of a container, array or any type with `begin()`/`end()`, without explicit iterators or indices.",
"""It's rewritten by the compiler into iterator code. Choose the element form deliberately: `auto` (copy), `auto&` (modify), `const auto&` (read, no copy), `auto&&` (generic code, binds to proxies).

C++20 allows an init-statement (`for (auto list = getList(); auto& x : list)`), which also fixes the classic lifetime bug where `for (auto& x : getObj().items())` iterated over a member of a destroyed temporary (C++23 extends temporary lifetimes in range-for).

You can't safely add or remove elements of the container inside the loop (iterator invalidation).""",
"Calling `v.push_back()` inside `for (auto& x : v)`; reallocation invalidates the loop's hidden iterators.",
["How do you get an index in a range-for? => Keep a counter, or use C++23 `std::views::enumerate`.",
 "What did C++23 fix for range-for? => Temporaries in the range expression now live until the end of the loop."]),

330: D("`constexpr` marks variables and functions that can be evaluated at compile time: a `constexpr` variable must be a compile-time constant, and a `constexpr` function can run at compile time when given constant arguments (and at runtime otherwise).",
"""Uses: compile-time lookup tables (CRC tables, register bit masks), array sizes, template arguments, and `static_assert` checks, moving work from runtime to build time with zero runtime cost.

Each standard expanded it: C++14 allowed loops and variables, C++17 `if constexpr` and constexpr lambdas, C++20 allowed `std::vector`/`std::string` usage, virtual functions and `try` blocks in constant evaluation. `consteval` (C++20) requires compile-time evaluation; `constinit` requires static initialization. Undefined behaviour inside constant evaluation is a compile error, a nice correctness bonus.""",
"Assuming a `constexpr` function always runs at compile time; it only does in constant-expression contexts (use `consteval` or assign to a `constexpr` variable to force it).",
["What's the difference between `constexpr` and `consteval` functions? => `consteval` must be evaluated at compile time; `constexpr` may run at either.",
 "Why is UB caught in constexpr evaluation? => The compiler must diagnose undefined behaviour in constant expressions."]),

331: D("Captures specify which outer variables a lambda can use and how: `[=]` copies everything used, `[&]` references everything used, `[this]` captures the object pointer, and explicit captures name each variable (`[x, &y]`).",
"""Guidance: prefer explicit captures in code that outlives the current scope, so lifetimes are visible. `[=]` in a member function captures `this` implicitly (deprecated since C++20); use `[this]` or `[*this]` (C++17, copies the object) explicitly.

Init-captures (`[conn = std::move(connection)]`) move resources into the lambda. By-copy captures are const inside the lambda unless it's declared `mutable`.""",
"Using `[=]` in a member function and storing the lambda asynchronously, believing everything was copied, while it actually captured `this` and dangles after the object dies.",
["What does `[*this]` do? => Copies the entire object into the lambda (C++17), avoiding dangling `this`.",
 "Why must some lambdas be `mutable`? => By-copy captures are const by default; `mutable` allows modifying the lambda's own copies."]),

332: D("A generic lambda (C++14) has `auto` parameters, making its `operator()` a template: `[](const auto& a, const auto& b) { return a < b; }` works for any comparable types.",
"""Each `auto` parameter becomes an independent template parameter. C++20 adds explicit template parameter lists for lambdas (`[]<class T>(const std::vector<T>& v) { ... }`), useful when you need the type name or to constrain several parameters to the same type, and concepts (`[](std::integral auto x) {}`).

Generic lambdas combined with `std::visit` and the \"overloaded\" idiom make type-safe variant handling concise.""",
"Expecting `[](auto a, auto b)` to require both arguments to have the same type; each `auto` is independent.",
["How do you get the type name inside a generic lambda? => Use `decltype(param)` or a C++20 template lambda `[]<class T>(T x) {}`.",
 "What is the overloaded idiom? => A struct inheriting from several lambdas' `operator()`s, used with `std::visit` to handle each variant alternative."]),

333: D("`decltype(expr)` yields the exact declared type of an expression (including references and const), while `auto` deduces a type from an initializer using template deduction rules (dropping references and top-level const).",
"""Rules: `decltype(name)` gives the declared type of the variable; `decltype((name))` or other lvalue expressions give `T&`. `decltype(auto)` (C++14) deduces like `auto` but applies decltype rules, used to return exactly what a forwarded call returns.

Uses: trailing return types (`auto f(T t) -> decltype(t.size())`), type aliases for expression results, and SFINAE/detection in generic code.""",
"Writing `decltype(auto) f() { int x = 1; return (x); }`: the parentheses make it `int&` to a local, a dangling reference.",
["What's the difference between `decltype(x)` and `decltype((x))`? => The first is the declared type of `x`; the second treats it as an lvalue expression and yields a reference.",
 "When is `decltype(auto)` useful? => For forwarding functions that must return exactly what the wrapped call returns, including references."]),

334: D("Structured bindings (C++17) declare several names bound to the elements of a tuple-like object, struct or array in one statement: `auto [key, value] = *it;`.",
"""They work with `std::pair`, `std::tuple`, `std::array`, C arrays, and structs with public non-static members (in declaration order), and custom types that implement the tuple protocol.

The names are aliases into a hidden object: `auto [a, b] = s;` copies `s`; `auto& [a, b] = s;` binds to `s` itself. Perfect for map iteration (`for (const auto& [sn, dev] : devices)`) and returning multiple values from functions. C++20 allows capturing them in lambdas and `static`/`thread_local` bindings.""",
"Writing `auto [a, b] = bigStruct;` in a loop and copying the whole struct each time; use `const auto&` or `auto&`.",
["Can structured bindings be used with private members? => No, only public non-static data members (or types implementing the tuple protocol).",
 "Are structured bindings copies or references? => They refer into a hidden object which is a copy or a reference depending on `auto` vs `auto&`."]),

335: D("`std::string_view` (C++17) is a non-owning, read-only view of a character sequence (pointer + length) that can refer to `std::string`, string literals or any char buffer without copying.",
"""As a parameter type, `std::string_view` accepts literals without constructing a temporary `std::string` (which `const std::string&` requires), accepts substrings cheaply (`sv.substr` doesn't allocate), and works with buffers from C APIs or packet data.

Caveats: it doesn't own data (never return a view into a local string, never store views of temporaries), and it's **not null-terminated**, so don't pass `sv.data()` to C functions expecting a C string. Pass it by value (two words).""",
"`std::string_view name = getName();` where `getName()` returns `std::string` by value: the view dangles immediately.",
["Why can't you pass `sv.data()` to `printf(\"%s\")` safely? => The view isn't necessarily null-terminated.",
 "Why pass `string_view` by value? => It's two words, cheap to copy, and avoids an extra indirection."]),

336: D("Uniform (brace) initialization (C++11) uses `{}` to initialize objects of any kind (aggregates, classes, containers, built-ins) with consistent syntax, and forbids narrowing conversions.",
"""Benefits: `int x{3.7};` is a compile error (narrowing), `T obj{};` value-initializes (zeros built-ins), and braces avoid the most vexing parse (`Widget w{};` is always an object).

Caveats: brace initialization prefers `std::initializer_list` constructors (`std::vector<int>{3, 1}` has two elements), and `auto x{1};` deduces `int` in C++17 (it was `initializer_list<int>` before).""",
"Writing `std::vector<int> v{100};` expecting 100 elements; it creates one element with value 100.",
["What is narrowing, and why is it an error in braces? => An implicit conversion that may lose information (double to int, large int to char); braces reject it for safety.",
 "What does `T t{};` do for an aggregate with int members? => Value-initializes, setting them to zero."]),

337: D("Variadic templates take a type-safe parameter pack of any length (`template<class... Args> void log(Args&&... args)`); C-style variadic functions (`...` with `va_list`) accept arguments without type information and rely on the caller and callee agreeing on types.",
"""C varargs (`printf`) can't know argument types at compile time: passing a `std::string` to `%s` is undefined behaviour, and non-trivial types can't be passed at all. Variadic templates know every type, can forward arguments perfectly, and generate specialized code.

Modern replacements for printf-style functions: `std::format` / `std::print` (C++20/23), which are type-safe and checked at compile time.""",
"Passing a `std::string` to `printf(\"%s\")` instead of `.c_str()`; with C varargs, it compiles (maybe with a warning) and is undefined behaviour.",
["How does `std::format` check format strings? => The format string is checked at compile time against the argument types (C++20).",
 "Why can't C varargs handle `std::string` safely? => Only trivially copyable types can be passed, and no type information is available to the callee."]),

338: D("`std::function<R(Args...)>` is a type-erased, copyable wrapper that can hold any callable with a compatible signature (function pointers, lambdas with captures, functors, bound member functions).",
"""Use it when you need to **store** heterogeneous callables with state, e.g. callback registries or event handlers. A raw function pointer can't hold capturing lambdas.

Costs: possible heap allocation for large callables (small-buffer optimization for small ones), an indirect call that usually can't be inlined, and copyability requirements. For callbacks passed and called immediately, prefer a template parameter; for move-only callables use C++23 `std::move_only_function`; for non-owning callback parameters C++26 adds `std::function_ref`.""",
"Using `std::function` as a parameter in a hot, inlinable path (like a comparator in a sort), preventing inlining and costing allocations.",
["When is a template parameter better than `std::function`? => When the callable is used immediately and performance matters; it can be inlined.",
 "What does `std::move_only_function` add? => Holding move-only callables, like lambdas capturing `unique_ptr` (C++23)."]),

339: D("A plain `enum` leaks its enumerators into the enclosing scope and converts implicitly to `int`; `enum class` (scoped enum, C++11) keeps enumerators scoped (`Color::Red`), prevents implicit integer conversion, and allows specifying the underlying type.",
"""Plain enums cause name clashes (`Red` in two enums) and bugs like comparing unrelated enums or passing an enum where an `int` count was expected. Scoped enums require `static_cast<int>(e)` (or C++23 `std::to_underlying(e)`) for conversions.

Specify the underlying type for binary layouts and forward declarations: `enum class Opcode : std::uint8_t { Read = 0x02, Write = 0x01 };` (NVMe opcodes fit a byte). C++20's `using enum Opcode;` imports enumerators into a scope when convenient.""",
"Using plain enums for NVMe status codes and command opcodes, then accidentally comparing a status to an opcode because both convert to int.",
["How do you convert a scoped enum to its integer value in C++23? => `std::to_underlying(e)`.",
 "Can you forward-declare an enum? => Yes, if its underlying type is specified (always the case for `enum class`, default `int`)."]),

340: D("C++14 lets functions declare `auto` as the return type, and the compiler deduces it from the `return` statements (all of which must deduce the same type).",
"""Useful for templates whose return type is complex, for returning lambdas, and for short helper functions. `decltype(auto)` preserves references and const of the returned expression.

Limits: the function body must be visible where the return type is needed (so declarations in headers need the definition), recursive functions need a return before the recursive call, and overuse makes interfaces harder to read (callers must read the body to know the type).""",
"Using `auto` return types on public API functions declared in headers and defined in `.cpp` files; callers can't deduce the type without the definition.",
["Can two return statements deduce different types with `auto`? => No; they must deduce the same type or it's an error.",
 "When would you use `decltype(auto)` as a return type? => When forwarding a call whose result may be a reference that must be preserved."]),

341: D("`std::filesystem` (C++17) is a portable library for working with paths, files and directories: path manipulation, existence and status checks, directory iteration, copying, renaming, removing and space queries.",
"""Key types: `std::filesystem::path` (handles separators and encodings per platform), `directory_iterator` and `recursive_directory_iterator`, `file_status`, and functions like `exists`, `create_directories`, `copy_file`, `remove_all`, `file_size`, `last_write_time`, `space`.

Functions throw `filesystem_error` or take an `std::error_code&` parameter for non-throwing use. It replaces platform-specific APIs (POSIX `opendir`, Win32 `FindFirstFile`) and Boost.Filesystem, on which it was based.""",
"Checking `exists(p)` and then opening the file in two steps; the file can change in between (TOCTOU race). Just open it and handle the failure.",
["How do you avoid exceptions from filesystem calls? => Use the overloads taking a `std::error_code&` argument.",
 "What is `path::operator/` for? => Joining path components with the correct platform separator."]),

342: D("Attributes are standardized annotations in `[[...]]` that give the compiler extra information: e.g. `[[nodiscard]]` warns if a return value is ignored, `[[maybe_unused]]` silences unused warnings, `[[deprecated(\"msg\")]]` warns on use.",
"""Others: `[[noreturn]]` (C++11), `[[fallthrough]]` (intentional switch fallthrough, C++17), `[[likely]]`/`[[unlikely]]` (branch hints, C++20), `[[no_unique_address]]` (empty-member optimization, C++20), `[[assume(expr)]]` (C++23).

`[[nodiscard]]` is especially valuable for error codes and `std::expected`-style results: ignoring a device command's status becomes a compiler warning. It can be applied to types (every function returning that type) and, since C++20, carry a reason string.""",
"Returning error codes from driver functions without `[[nodiscard]]`, so callers silently ignore failures.",
["What does `[[nodiscard]]` on a class do? => Every function returning that type by value warns if the result is ignored.",
 "What is `[[fallthrough]]` for? => Marking intentional fallthrough in a switch so the compiler doesn't warn."]),

343: D("With brace initialization, if a class has a constructor taking `std::initializer_list` and the braced arguments can convert to its element type, that constructor is strongly preferred over all others, even better matches.",
"""Surprises: `std::vector<int> v{10, 0};` makes two elements (10 and 0) instead of ten zeros; `std::string s{65, 'a'};` makes \"Aa\" (65 converts to 'A'); adding an `initializer_list` constructor to an existing class can silently change meaning of existing brace-initializations.

Empty braces `T{}` call the default constructor, not the `initializer_list` constructor. To call other constructors use parentheses. Library designers should add `initializer_list` constructors carefully.""",
"Adding an `initializer_list` constructor to a widely used class, which changes the behaviour of existing `T{a, b}` initializations in client code.",
["What does `std::vector<int>{}` call? => The default constructor, not the initializer_list constructor.",
 "Why does `std::string s{65, 'a'}` produce \"Aa\"? => Brace initialization picks the `initializer_list<char>` constructor, converting 65 to 'A'."]),

344: D("C++20 concepts are named compile-time requirements on template arguments that participate in overload resolution and produce targeted errors; `static_assert` only checks inside an already-selected template and produces a hard error.",
"""With `static_assert(std::is_integral_v<T>)` inside a function, the function still appears viable during overload resolution, so you can't have another overload for floats selected automatically, and the error appears deep inside the implementation.

Concepts constrain the **interface**: `template<std::integral T> void f(T)` removes the overload for non-integral types, lets another overload handle them, supports ordering by subsumption, and reports \"constraints not satisfied\" at the call site. Use `static_assert` for internal invariants and concepts for interface requirements.""",
"Using `static_assert` to restrict template parameters and then wondering why overload resolution picks that template and fails instead of choosing another overload.",
["Can `static_assert`-based checks select between overloads? => No; they fire after an overload is chosen.",
 "Where does `static_assert` still make sense? => For invariants inside code, e.g. struct sizes matching a hardware layout."]),

345: D("C++20 coroutines are functions that can suspend and resume execution, using `co_await` (suspend until an awaitable completes), `co_yield` (produce a value and suspend) and `co_return` (finish), with state stored in a compiler-managed coroutine frame.",
"""They enable asynchronous code written sequentially (network or device I/O without callbacks), lazy generators, and state machines. The language provides the mechanism (promise types, awaiters, `std::coroutine_handle`); C++20 didn't ship high-level types, but C++23 adds `std::generator` and libraries (cppcoro, Boost.Asio, folly) provide tasks.

Considerations: coroutine frames are usually heap-allocated (elision possible), lifetimes of references in parameters are a common bug (the caller's temporaries may be gone when the coroutine resumes), and debugging is harder.""",
"Passing references to temporaries into a coroutine that suspends; when it resumes, the temporaries are destroyed and the references dangle.",
["What is `std::generator` (C++23)? => A standard coroutine type for lazily producing sequences with `co_yield`.",
 "Where is a coroutine's local state stored? => In a coroutine frame, typically heap-allocated unless the compiler elides the allocation."]),

346: D("The ranges library (C++20) lets algorithms operate on whole ranges and introduces **views**: lightweight, lazily evaluated, composable ranges that don't own elements, as opposed to containers, which own and store their elements.",
"""A view like `readings | std::views::filter(valid) | std::views::transform(scale)` computes elements on demand as you iterate; creating it is O(1) and allocates nothing. Containers store elements eagerly.

Views are cheap to copy and pass around but can dangle if they refer to a destroyed container. Materialize results with C++23 `std::ranges::to<std::vector>()` when you need storage. Range algorithms add projections and accept whole containers (`std::ranges::sort(v)`).""",
"Returning a view built on a local container from a function; the container is destroyed and the view dangles.",
["Is building a view pipeline expensive? => No; views are lazy and compose in constant time, work happens during iteration.",
 "How do you convert a view into a container? => `std::ranges::to<Container>()` in C++23, or construct the container from the view's iterators."]),

347: D("The three-way comparison operator `<=>` (C++20) compares two values and returns an ordering object (`std::strong_ordering`, `weak_ordering` or `partial_ordering`) indicating less, equal or greater; from it the compiler synthesizes `<`, `<=`, `>` and `>=`.",
"""`auto operator<=>(const Version&) const = default;` compares members lexicographically; with `bool operator==(const Version&) const = default;` you get all six comparisons from two lines. Defaulting `<=>` also implicitly defaults `==`.

The ordering categories matter: `partial_ordering` for floats (NaN is unordered), `weak_ordering` for case-insensitive comparisons (equivalent but distinguishable), `strong_ordering` for true equality.""",
"Defining a custom `<=>` for efficiency but forgetting `==`; a user-defined (non-defaulted) `<=>` doesn't provide `==` automatically.",
["What does `= default` on `<=>` generate? => Member-wise lexicographic comparison, plus a defaulted `==`.",
 "Why is comparing doubles a `partial_ordering`? => NaN compares unordered with every value."]),

348: D("C++20 modules are compiled units with explicit exported interfaces (`export module drivers; export class Nvme;`) that are imported (`import drivers;`) instead of textually included, solving slow builds, macro leakage and ODR fragility of headers.",
"""With `#include`, every translation unit re-parses the same headers; macros and non-exported helpers leak everywhere, and include order can change meaning. A module interface is compiled once into a binary form (BMI); importers read that, which is faster, isolated from importer macros, and only sees exported names.

The standard library is available as `import std;` since C++23. Adoption depends on build-system support (CMake 3.28+, MSVC, recent Clang and GCC); mixing with legacy headers uses header units or the global module fragment.""",
"Expecting modules to speed up builds with no build-system changes; they require dependency scanning and compilation ordering support.",
["What is a BMI? => A built module interface: the compiled representation of a module that importers consume.",
 "Do macros cross module boundaries? => No, macros defined inside a module aren't visible to importers (except via header units)."]),

349: D("`constinit` (C++20) requires a static or thread-local variable to be initialized at compile time (constant initialization), without making it const; `constexpr` variables are both compile-time initialized and immutable.",
"""`constinit` targets the static initialization order fiasco: a global that must be ready before any dynamic initialization runs, but may be modified later (a counter, a mutable table, a lock). If the initializer isn't a constant expression, compilation fails, so you can't accidentally depend on dynamic initialization order.

Example: `constinit std::atomic<int> g_activeDevices{0};` is guaranteed initialized before any code runs.""",
"Marking a global `constinit` and then initializing it from a non-constexpr function call; the compiler rejects it, revealing the hidden dynamic initialization.",
["Can a `constinit` variable be modified? => Yes; only its initialization is required to be constant.",
 "Does `constinit` apply to local variables? => Only to variables with static or thread storage duration."]),

350: D("The static initialization order fiasco is that dynamic initialization of globals in different translation units happens in unspecified order, so a global constructor that uses another file's global may see it uninitialized.",
"""Example: `Logger g_logger;` in one file, and a global `Registry g_reg;` in another whose constructor logs through `g_logger`. It works or crashes depending on link order.

Mitigations: construct on first use with a function-local static (`Logger& logger() { static Logger l; return l; }`), `constexpr`/`constinit` globals (initialized at compile time, before any dynamic initialization), avoiding non-trivial globals entirely, and explicit initialization in `main`. The mirror problem exists at shutdown (destruction order).""",
"A global object's constructor calling into another translation unit's global (config, logger, registry), which works in debug builds and breaks when the link order changes.",
["How does a function-local static fix the problem? => The object is initialized the first time it's used, so it's always ready when accessed.",
 "How does `constinit` help? => It guarantees compile-time initialization, which happens before any dynamic initialization."]),

351: D("`std::variant<Ts...>` holds exactly one value from a fixed set of types, and `std::visit` applies a callable to whichever alternative is active, giving type-safe sum types (tagged unions) like enums with data.",
"""Example: `using Event = std::variant<IoComplete, Timeout, DeviceRemoved>;` handled with `std::visit(overloaded{[](const IoComplete& e){...}, [](const Timeout& t){...}, [](const DeviceRemoved&){...}}, ev);`. If a case is missing, compilation fails, unlike a `switch` on an enum with a `default`.

Compared to inheritance: values instead of heap-allocated objects, no virtual functions, and adding an operation is easy while adding a type requires updating visitors (the Visitor pattern trade-off). A variant can become `valueless_by_exception` if an assignment throws mid-way.""",
"Using `std::get<T>(v)` without checking the active type; it throws `std::bad_variant_access`. Use `std::visit`, `std::holds_alternative` or `std::get_if`.",
["What is `valueless_by_exception`? => A state a variant enters if changing the alternative throws partway through.",
 "How does `std::visit` guarantee all cases are handled? => The callable must be invocable for every alternative, or compilation fails."]),

352: D("C++20 designated initializers let you initialize aggregate members by name (`Config c{.timeout_ms = 500, .retries = 3};`), whereas regular aggregate initialization assigns values by position.",
"""Named initialization makes code self-documenting and robust to reordering mistakes, especially for structs with many same-typed fields (timeouts, sizes, flags). Omitted members get their default member initializers or are value-initialized.

C++ rules are stricter than C99: designators must appear in declaration order, can't be mixed with positional initializers, and nested/array designators aren't allowed. Only aggregates qualify (no user-declared constructors, no private members).""",
"Writing designators out of declaration order (`{.retries = 3, .timeout_ms = 500}` when `timeout_ms` is declared first); C++ requires declaration order.",
["What happens to members you don't designate? => They use their default member initializer or are value-initialized.",
 "Can you use designated initializers with a class that has constructors? => No, only with aggregates."]),

353: D("Together, `std::span` (safe views of contiguous memory), ranges (composable algorithms and views) and `std::format` (type-safe formatting) replace C-style idioms (pointer-plus-length, hand-written loops, `printf`) with safer, clearer and still efficient code.",
"""Before: `void process(const uint8_t* buf, size_t len)`, manual index loops, `sprintf(out, \"%d\", x)` with overflow and type risks. After: `void process(std::span<const std::byte> buf)`, `std::ranges::count_if(buf, pred)`, `std::format(\"{:#x}\", x)` checked at compile time.

The theme of modern C++ is expressing intent through types (views, optional, variant, expected) so the compiler catches misuse, while keeping zero-cost abstractions. C++23 adds `std::print`, `std::expected`, `std::mdspan` and more views to continue this.""",
"Modernizing syntax (auto, lambdas) while keeping pointer-plus-length interfaces and `printf`, which leaves the main safety problems in place.",
["What does `std::format` check at compile time? => That the format string is valid for the argument types.",
 "What replaces `(T* p, size_t n)` parameters? => `std::span<T>`."]),

354: D("`std::optional<T>` explicitly represents \"a T or nothing\" in the type, storing the value inline, whereas a raw pointer (null for absent) or sentinel value (-1, empty string) encodes absence by convention that callers can forget.",
"""Sentinels break when the sentinel is a valid value (a temperature of -1, an LBA of 0), and nothing forces callers to check. Pointers imply indirection, ownership questions and a heap object or external storage.

With `optional`, the type system documents that absence is possible, `value_or(default)` handles defaults cleanly, and C++23 monadic operations chain transformations (`parse(s).and_then(validate).transform(scale)`). For absence with a reason, use `std::expected`.""",
"Returning `int` with `-1` meaning \"not found\" from a function where -1 can also be a legitimate reading.",
["Is `std::optional<T&>` allowed? => Not in C++23 (it's being added in C++26); use `T*` or `std::optional<std::reference_wrapper<T>>`.",
 "What does `value_or` do? => Returns the contained value or the given default if empty."]),

355: D("The as-if rule lets the compiler transform a program in any way as long as its observable behaviour (volatile accesses, I/O, the final state visible to the outside) is the same as the abstract machine's; it's the foundation of all optimizations.",
"""Under as-if, compilers inline, reorder, remove dead code, keep variables in registers and vectorize loops. Copy elision is special: it's an explicit exception, allowed to change observable behaviour (skipping side effects in copy/move constructors), and mandatory for prvalues since C++17.

Programs with undefined behaviour get no protection: the as-if rule only preserves the behaviour of well-defined programs, which is why UB can lead to \"impossible\" results. `volatile` marks accesses as observable, which is why hardware register access must use it.""",
"Expecting a busy-wait loop on a plain variable (or timing code without side effects) to survive optimization; under the as-if rule it may be removed or hoisted.",
["Why must memory-mapped registers be `volatile`? => Volatile accesses are observable behaviour, so the compiler can't remove or merge them.",
 "Is copy elision allowed by the as-if rule? => It's a separate explicit permission, since it can change observable side effects."]),
}
