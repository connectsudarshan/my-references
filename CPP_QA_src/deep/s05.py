DEEP = {

121: D("Operator overloading lets you define what built-in operators (`+`, `==`, `<<`, `[]`, `()`) mean for user-defined types by writing functions named `operator@`.",
"""It makes domain types read naturally: `a + b` for vectors, `price * qty` for money, `data[i]` for containers. The expression `a + b` is just sugar for `a.operator+(b)` or `operator+(a, b)`.

Rules: at least one operand must be a user-defined type; precedence, associativity and arity can't change; you can't invent new operators.

Guideline: overload only when the meaning is obvious and conventional (the \"do as the ints do\" principle), keep related operators consistent (`+` with `+=`, `==` with `!=`, `<` with the other comparisons, or use C++20 `<=>`).""",
"Overloading operators with surprising meanings (e.g. `+` that mutates its left operand), which makes code misleading to read.",
["Can you change an operator's precedence? => No; overloaded operators keep the built-in precedence and associativity.",
 "What does C++20's `<=>` simplify? => Defining one three-way comparison (often `= default`) generates `<`, `<=`, `>`, `>=`, and `==` can also be defaulted."]),

122: D("You can't overload `::` (scope resolution), `.` (member access), `.*` (pointer-to-member access), `?:` (conditional), `sizeof`, `alignof`, `typeid`, and the preprocessor operators `#` and `##`.",
"""These are excluded because they operate on names or types rather than values, or because overloading them would make basic language semantics unreliable (e.g. `.` must always mean member access so objects behave predictably).

Operators that **can** be overloaded but only as members: `=`, `()`, `[]`, `->`, and conversion operators. `new`, `delete` and their array forms can be overloaded globally or per class. C++23 allows `operator[]` with multiple arguments and static `operator()`/`operator[]`.""",
"Trying to overload `operator.` for smart-reference types; use `operator->` (which can be overloaded) instead.",
["Which operators must be members? => `=`, `()`, `[]`, `->` and conversion operators.",
 "What did C++23 add for `operator[]`? => Multiple subscript arguments (`m[i, j]`), useful for matrices and `std::mdspan`."]),

123: D("Most operators can be implemented either as member functions (left operand is `*this`) or as non-member functions (all operands are parameters, optionally friends for private access).",
"""Choose members for operators that modify the object or need access to its internals and have the object on the left (`+=`, `-=`, `=`, `[]`, `()`, `->`, unary operators).

Choose non-members for symmetric binary operators (`+`, `-`, `*`, `==`, `<`) so implicit conversions apply to both operands, and for operators whose left operand isn't your type (`std::ostream& operator<<(std::ostream&, const T&)`).

A common pattern: implement `+=` as a member and `+` as a non-member using it: `T operator+(T a, const T& b) { a += b; return a; }`.""",
"Implementing `operator+` as a member so `money + 5` compiles but `5 + money` doesn't.",
["Why implement `+` in terms of `+=`? => Single source of truth for the arithmetic, and `+` gets a correct copy-then-modify implementation for free.",
 "Why is `operator<<` for streams a non-member? => The left operand is `std::ostream`, which you can't add members to."]),

124: D("`operator=`, `operator[]`, `operator()` and `operator->` are required by the language to be non-static member functions, because they're tightly bound to the object on their left.",
"""For assignment specifically: if you could declare a free `operator=`, the compiler's implicitly declared member copy assignment would still exist, making the rules for which one applies confusing; requiring members keeps class semantics self-contained.

`operator[]` and `operator()` usually need direct access to internal storage and should never allow implicit conversions on the object operand (a free function would let `5[obj]`-style conversions creep in).

C++23 relaxes one related rule: `operator()` and `operator[]` may be `static`, useful for stateless function objects.""",
"Trying to write a free `operator=` to add assignment from another type; add a member assignment overload or a converting constructor instead.",
["What does C++23 allow for `operator()`? => It may be declared `static` when the functor has no state, avoiding the implicit object parameter.",
 "Why shouldn't the object operand of `[]` allow implicit conversions? => It would let unrelated types be subscripted after silent conversion, hiding bugs."]),

125: D("Overload `operator<<` as a non-member taking `std::ostream&` and `const T&`, writing the object and returning the stream so calls can be chained.",
"""Signature: `std::ostream& operator<<(std::ostream& os, const Point& p)`. Make it a `friend` (often a hidden friend defined inside the class) if it needs private members, or use public accessors.

Guidelines: don't add a trailing newline (let callers decide), respect stream formatting where reasonable, and return the stream reference. For input, `operator>>` should set `failbit` on malformed input and leave the object in a valid state.

In C++20/23, also consider `std::formatter<Point>` specializations so the type works with `std::format` and `std::print`.""",
"Returning the stream by value or not returning it at all, which breaks chaining like `std::cout << a << b`.",
["Why is it best as a hidden friend? => It's only found through ADL for `Point`, keeping global overload sets small and avoiding accidental conversions.",
 "How do you support `std::format` for your type? => Specialize `std::formatter<T>` with `parse` and `format` members."]),

126: D("Prefix `operator++()` increments and returns a reference to the updated object; postfix `operator++(int)` takes a dummy `int` parameter to distinguish it, returns a copy of the old value, then increments.",
"""Canonical forms:

- `T& operator++() { /* increment */ return *this; }`
- `T operator++(int) { T old = *this; ++*this; return old; }`

Postfix must make a copy, so for iterators and heavy types prefer `++it` in loops. For built-in types the compiler optimizes both equally when the result is unused.

Implement postfix in terms of prefix so the increment logic exists once.""",
"Returning `T&` from postfix or modifying the value before copying it: callers get the new value instead of the old one.",
["Why does postfix take an `int` parameter? => Only to give it a different signature from prefix; the value is unused.",
 "Why prefer `++it` over `it++` for iterators? => Postfix copies the iterator, which may be non-trivial; prefix doesn't."]),

127: D("`==` and `!=` must agree (`a != b` should always equal `!(a == b)`); implementing one in terms of the other guarantees it, and C++20 generates `!=` from `==` automatically.",
"""Equality should be an equivalence relation: reflexive, symmetric and transitive, and consistent with `std::hash` when the type is used in unordered containers (equal objects must hash equally).

Before C++20 you wrote both (usually as non-members). In C++20, declaring `bool operator==(const T&) const = default;` compares all members in order, and `a != b` is rewritten as `!(a == b)`. Reversed argument order (`5 == obj`) is also handled by rewriting.

Decide what equality means: value equality of all members, or only identity-defining fields (e.g. serial number); document it.""",
"Defining `==` to compare some fields but hashing different fields, so equal objects end up in different buckets of an `unordered_set`.",
["What does C++20 rewrite `a != b` into? => `!(a == b)`, so you only need `operator==`.",
 "What must hold between `==` and `std::hash`? => Equal objects must produce equal hashes."]),

128: D("Self-assignment (`a = a`) breaks naive assignment operators that free their own resources before copying from the source, because the source is the object just freed.",
"""Naive code: `delete[] data_; data_ = new char[o.size_]; std::copy(o.data_, ...)` reads freed memory when `&o == this`.

Fixes: a self-check `if (this == &o) return *this;` (cheap but doesn't give exception safety), allocate and copy into a temporary **before** releasing the old data, or use copy-and-swap, which handles self-assignment and gives the strong exception guarantee.

Self-assignment is rare but happens through aliases: `v[i] = v[j]` with `i == j`, or `*p = *q` when both point to the same object.""",
"Adding only the `this == &o` check and still freeing the old buffer before the new allocation, so an allocation failure leaves the object with a dangling pointer.",
["How can self-assignment happen unintentionally? => Through aliases: references or indices that happen to refer to the same object.",
 "Why is copy-and-swap self-assignment safe? => It copies the source first, then swaps; the old state is released only after the copy succeeded."]),

129: D("Overloading `operator()` makes objects callable like functions; such objects are called **function objects** or **functors**.",
"""Functors can carry state (a threshold, a counter, a random generator) and are easily inlined by the compiler, which is why STL algorithms take them as template parameters (`std::sort(v.begin(), v.end(), ByLatency{})`).

Lambdas are syntactic sugar for compiler-generated functor classes: captured variables become members and the body becomes `operator()`.

Standard functors include `std::less<>`, `std::plus<>`, `std::hash<T>`; the transparent forms like `std::less<>` enable heterogeneous lookup in ordered containers.""",
"Writing a functor whose `operator()` modifies state and passing it to algorithms that may copy it; each copy has its own state, so results are inconsistent. Use `std::ref` or lambdas capturing by reference.",
["How does a lambda relate to a functor? => The compiler generates a unique class with the captures as members and the body as `operator()`.",
 "Why are functors often faster than function pointers in `std::sort`? => The call target is part of the type, so the compiler can inline it."]),

130: D("Provide two overloads of `operator[]`: a non-const one returning `T&` (read and write) and a const one returning `const T&` (or a value) for read-only access on const objects.",
"""The const overload is essential: without it, a `const Matrix&` parameter can't be indexed. Both typically share one private implementation to avoid duplication (C++23 \"deducing this\" can write them as one function).

Decide on bounds checking: `operator[]` is conventionally unchecked (like `std::vector`), with a separate `at()` that throws `std::out_of_range`.

For sparse or proxy-based containers (e.g. `std::vector<bool>`), `operator[]` returns a proxy object, which behaves differently from a real reference (`auto x = v[0];` copies the proxy).""",
"Providing only a non-const `operator[]`, making the container unusable through const references.",
["Why do standard containers offer both `[]` and `at()`? => `[]` is unchecked for speed; `at()` checks bounds and throws.",
 "What's the pitfall of proxy references like `std::vector<bool>::reference`? => `auto` captures the proxy, not a bool, which may dangle or behave unexpectedly."]),

131: D("Copy-and-swap implements assignment by taking the argument by value (making a copy or move), swapping its contents with `*this`, and letting the parameter's destructor release the old state.",
"""`T& operator=(T other) noexcept { swap(*this, other); return *this; }` with a `noexcept` `swap` that exchanges members.

Properties: **strong exception guarantee** (if the copy throws, `*this` is untouched because the copy happens before the function body), automatic self-assignment safety, and a single function serving as both copy and move assignment (the parameter is move-constructed from rvalues).

Cost: it always creates a new copy even when existing capacity could be reused (e.g. assigning a vector of equal size), so performance-critical containers implement assignment more carefully.""",
"Implementing `swap` in terms of `std::swap(*this, other)`, which for the class itself calls the assignment operator: infinite recursion. Swap members individually.",
["What exception guarantee does copy-and-swap provide? => The strong guarantee: either the assignment succeeds or `*this` is unchanged.",
 "When is copy-and-swap slower than a hand-written assignment? => When the target could reuse its existing buffer instead of allocating a new one."]),

132: D("Yes, `operator,` can be overloaded, but it's almost never a good idea: the overloaded version loses the built-in left-to-right sequencing guarantee (pre-C++17) and surprises readers.",
"""The built-in comma evaluates the left operand, discards it, then evaluates the right. An overloaded comma is a normal function call; before C++17 the evaluation order of its operands was unspecified. C++17 restored left-to-right evaluation for overloaded commas too, but the surprise factor remains.

Historic uses: DSLs like Boost.Assign (`v += 1, 2, 3;`) and expression templates. Modern alternatives: initializer lists and variadic functions. Generic code sometimes casts to `void` (`(void)a, b`) to avoid invoking a user's overloaded comma.""",
"Overloading comma so that `f(a, b)` style code inside a macro or template silently calls your operator instead of separating arguments or expressions.",
["Why do generic libraries write `(void)expr, next`? => Casting to `void` prevents an overloaded comma operator from being selected.",
 "What replaced Boost.Assign-style comma DSLs? => Initializer lists (`std::vector<int> v{1, 2, 3};`)."]),

133: D("An overloaded operator must have at least one operand of class or enumeration type, so you can't redefine operators between built-in types like `int + int`.",
"""This keeps the meaning of basic arithmetic stable and prevents libraries from changing how the whole program computes integers.

If you need different semantics for numbers, wrap them in a type: `struct Saturating { int v; };` with its own `operator+`, or strong typedefs (`Meters`, `Seconds`) that also prevent mixing units. Enumerations can have overloaded operators (commonly `|` and `&` for bit-flag enums).""",
"Trying to overload `operator+(double, double)` to add rounding behaviour globally; wrap the value in a dedicated type instead.",
["Can you overload operators for enums? => Yes, e.g. `Flags operator|(Flags a, Flags b)` for flag enums.",
 "How do you get special arithmetic (saturating, modular)? => Define a wrapper type with its own operators."]),

134: D("A global `operator new`/`delete` replaces allocation for the entire program; a class-specific `operator new`/`delete` (static member functions) affects only objects of that class and its derived classes.",
"""Global replacement is used for tracking allocations, custom heaps, or failing loudly in real-time code; it must be defined once, with matching forms (`new`/`delete`, array and aligned variants, sized delete).

Per-class overloads suit fixed-size pools (a slab allocator for many small `Packet` objects) and are found by lookup before the global ones. Remember to provide matching `operator delete`, and the array forms if arrays are allocated.

Allocator-aware containers use `std::allocator` (which calls global `operator new`), not class-specific overloads; use `std::pmr` memory resources for container-level control.""",
"Overriding `operator new` without the matching `operator delete` (or array variants), so memory from the custom allocator is released to the wrong heap.",
["Where is a class-specific `operator new` found? => By lookup in the class scope first, so it applies to that class and derived classes.",
 "What's a modern alternative for custom container allocation? => `std::pmr` polymorphic memory resources (e.g. `monotonic_buffer_resource`)."]),

135: D("`operator<` for ordered containers must be a **strict weak ordering**: irreflexive (`!(a < a)`), transitive, and with transitive equivalence (if `a` and `b` are equivalent and `b` and `c` are, so are `a` and `c`).",
"""The easiest correct implementation compares members lexicographically with `std::tie(a.x, a.y) < std::tie(b.x, b.y)`, or in C++20 `auto operator<=>(const T&) const = default;`.

Containers use `!(a < b) && !(b < a)` as equivalence; if your ordering is inconsistent (e.g. uses `<=`, or compares floats with NaN), `std::set` and `std::map` can corrupt their trees or lose elements, and `std::sort` can crash.

For floating-point keys, handle NaN explicitly (or use `std::strong_order`/`std::weak_order` in C++20).""",
"Writing `return a.x <= b.x;` or comparing only one field while `==` compares all fields; `std::sort` may run past the end of the range.",
["What is a strict weak ordering? => An ordering where `<` is irreflexive and transitive and equivalence (neither `a<b` nor `b<a`) is transitive.",
 "How does `std::tie` help? => It builds tuples of references whose `<` compares elements lexicographically."]),

136: D("Implicit conversion operators (`operator T()`) let objects convert silently to another type, which can trigger unexpected overloads, lossy conversions and ambiguities.",
"""Classic example: pre-C++11 smart pointers with `operator bool()` allowed `ptr1 + ptr2` or `int x = ptr;`. The \"safe bool\" idiom was a workaround; C++11 `explicit operator bool()` solves it: usable in conditions, not in arithmetic.

Other problems: two types converting to each other produce ambiguous overloads, and conversions to `const char*` or references may dangle.

Guideline: mark conversion operators `explicit` unless the conversion is lossless and truly natural; prefer named functions (`toString()`, `asSeconds()`).""",
"A `String` class with implicit `operator const char*()` that returns a pointer into a temporary's buffer, leaving callers with a dangling pointer.",
["What is `explicit operator bool()` for? => It allows use in conditions (`if (p)`) but blocks accidental arithmetic or integer conversions.",
 "Why prefer named conversion functions? => They make conversions visible at call sites and can't be triggered accidentally."]),

137: D("For an expression like `a + b`, the compiler gathers member candidates (`a.operator+(b)`), non-member candidates found by ordinary and argument-dependent lookup, and built-in candidates, then runs normal overload resolution on all of them.",
"""Member and non-member candidates compete on equal terms, using the implicit object parameter for members; the best conversion sequence wins, and if two are equally good the call is ambiguous.

C++20 adds **rewritten candidates**: `a != b` may use `!(a == b)`, `b == a` can use `a == b` with reversed arguments, and `a < b` can use `(a <=> b) < 0`. Non-rewritten candidates win ties over rewritten ones.

Defining the same operation both as member and non-member with equivalent signatures is a common source of ambiguity errors.""",
"Having both `bool Money::operator==(const Money&) const` and a free `bool operator==(const Money&, const Money&)`: every comparison becomes ambiguous.",
["What are rewritten candidates in C++20? => Expressions using reversed or synthesized forms of `==` and `<=>` (e.g. `!=`, `<`, reversed argument order).",
 "Are member and non-member operator candidates treated differently? => No, they participate in the same overload resolution."]),

138: D("Arithmetic operators are recommended as non-members so both operands are treated symmetrically: implicit conversions (from converting constructors) apply to the left operand as well as the right.",
"""With a member `Rational Rational::operator*(const Rational&) const`, `r * 2` compiles (2 converts to `Rational`) but `2 * r` doesn't, because member functions don't consider conversions on their object operand.

A non-member `Rational operator*(const Rational&, const Rational&)` accepts both. It can be a hidden friend or be built on the member `*=`. Scott Meyers' Effective C++ Item 24 covers this example.""",
"Implementing only member arithmetic operators and discovering that mixed expressions compile in one direction only.",
["Why don't members allow conversions on the left operand? => The left operand is the object the member is called on; no conversion is considered for it.",
 "How do you avoid duplicating arithmetic logic? => Implement compound assignment (`*=`) as a member and the binary operator as a non-member calling it."]),

139: D("Operator overloading becomes ambiguous when two or more candidates are equally good matches; user-defined conversions (converting constructors and conversion operators) often create such ties.",
"""Example: `struct A { A(int); }; struct B { B(int); }; void operator+(A, A); void operator+(B, B);` then `1 + x` style expressions where the other operand converts to both.

Also common: a type with implicit `operator int()` and an `operator+(T, T)`: `t + 1` could convert `1` to `T` or `t` to `int` and use built-in addition.

Remedies: make constructors and conversion operators `explicit`, provide exact-match overloads for common mixed cases, and avoid implicit conversions in both directions between two types.""",
"Giving a type both an implicit converting constructor from `int` and an implicit conversion to `int`, making nearly every mixed arithmetic expression ambiguous.",
["How many user-defined conversions can one implicit conversion sequence use? => One; two chained user-defined conversions are never applied implicitly.",
 "What's the simplest fix for these ambiguities? => Make conversions `explicit` and add targeted overloads."]),

140: D("You can overload `operator&&` and `operator||`, but the overloaded versions are ordinary function calls: **both operands are always evaluated**, so the short-circuit behaviour of the built-ins is lost.",
"""Code like `if (ptr && ptr->valid())` relies on short-circuiting; with an overloaded `&&` on some wrapper type, `ptr->valid()` would run even when `ptr` is null.

Since C++17 the left operand is still evaluated before the right, but evaluation of both happens regardless. Expression-template libraries (Boost.Proto, some query DSLs) overload them deliberately to build expression trees rather than evaluate.

Guideline: don't overload `&&`, `||` or `,` for everyday types.""",
"Overloading `&&` on a condition wrapper and breaking null-check idioms that depend on short-circuit evaluation.",
["Why can't an overloaded `&&` short-circuit? => Both arguments must be evaluated before calling the function.",
 "When is overloading `&&` legitimate? => In DSLs or expression templates that build an expression tree instead of evaluating immediately."]),
}
