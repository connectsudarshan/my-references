DEEP = {

471: D("`5 / 2` is integer division because both operands are `int`, so the result is `2`: the fractional part is discarded (truncation toward zero since C++11).",
"""To get 2.5, make at least one operand floating-point: `5.0 / 2` or `static_cast<double>(a) / b`. Truncation toward zero also applies to negatives: `-5 / 2 == -2` and `-5 % 2 == -1` (the sign of `%` follows the dividend).

Common real bug: computing averages or percentages as `sum / count * 100` in integers, which yields 0 for any ratio below 1.""",
"Writing `double avg = total / count;` with integer operands, which divides as integers before converting to double.",
["What is `-7 / 2` in C++? => `-3`, truncating toward zero.",
 "What sign does `%` have for negative operands? => The sign of the dividend, e.g. `-7 % 2 == -1`."]),

472: D("`++i` (pre-increment) increments and yields the updated object as an lvalue; `i++` (post-increment) increments but yields a copy of the old value.",
"""For built-in types in standalone statements, both compile to the same code. For class types (iterators), post-increment must copy the old state, so `++it` can be cheaper; prefer pre-increment by habit.

Canonical overloads: `T& operator++()` and `T operator++(int)` implemented via the prefix one. In expressions, the value differs: `a[i++]` uses the old index.""",
"Implementing postfix `operator++` returning a reference to a local copy, which dangles.",
["How is postfix `operator++` distinguished in overloading? => It takes a dummy `int` parameter.",
 "Is there a performance difference for `int`? => No, not when the result is unused; compilers generate identical code."]),

473: D("The size of an empty class is at least 1 byte, because every complete object must have a unique address; if size were 0, two distinct objects (e.g. array elements) could share the same address.",
"""`struct Empty {}; sizeof(Empty) == 1`. As a base class, however, empty classes usually occupy no space (Empty Base Optimization), and C++20 `[[no_unique_address]]` allows empty members to take no space too.

This matters for stateless allocators, comparators and policy classes stored inside containers.""",
"Storing a stateless policy object as a normal member in a size-critical class, adding padding for no data; use `[[no_unique_address]]` or EBO.",
["What is the Empty Base Optimization? => An empty base class subobject can occupy zero bytes in the derived object.",
 "What does `[[no_unique_address]]` do? => Lets an empty member share its address with other members, taking no space."]),

474: D("`sizeof` on a pointer returns the size of the pointer itself (typically 8 bytes on 64-bit platforms, 4 on 32-bit), regardless of the size of the pointed-to object.",
"""The classic bug: an array passed to a function decays to a pointer, so `sizeof(arr) / sizeof(arr[0])` inside the function gives 8/4 = 2 instead of the element count. Use `std::size`, `std::span`, `std::array` or pass the length.

Function pointers and member pointers can have different sizes (member function pointers are often 16 bytes on Itanium ABI).""",
"Using `memset(p, 0, sizeof(p))` with a pointer `p`, which clears only 8 bytes rather than the whole object or buffer.",
["Why does `sizeof(arr)` differ inside a function? => The array parameter is really a pointer.",
 "Are all pointers the same size? => Usually for data pointers, but member function pointers are often larger."]),

475: D("`'a' + 1` promotes the `char` to `int` (integral promotion), so the result is the `int` 98 and `cout` prints a number; casting back to `char` selects the `char` overload of `operator<<`, printing `b`.",
"""Arithmetic on types smaller than `int` (`char`, `short`, `bool`) promotes operands to `int` first. The chosen `operator<<` overload depends on the static type, and `int` prints numerically.

Related gotchas: `uint8_t`/`int8_t` are usually character types, so `cout << uint8_t(65)` prints `A`, not `65`; use `+x` or cast to `int` to print the number.""",
"Printing `uint8_t` values (e.g. register bytes) with `cout` and getting control characters or letters instead of numbers.",
["How do you print a `uint8_t` as a number? => Cast to `int` or use unary plus: `cout << +byte`.",
 "What is integral promotion? => Converting small integer types to `int` (or `unsigned int`) before arithmetic."]),

476: D("`int y = x++ + ++x;` has undefined behaviour: `x` is modified twice (and read) without sequencing between the two operands of `+`, so there's no correct output to predict.",
"""C++17 added sequencing rules for some operators (`<<`, `>>`, assignment, `[]`, function call arguments indeterminately sequenced), but the operands of `+` remain unsequenced relative to each other. Different compilers and optimization levels produce different values, and warnings (`-Wsequence-point`, `-Wunsequenced`) flag it.

The correct interview answer is \"undefined behaviour, don't write it\", not a number.""",
"Answering with a specific value (like 12) as if the language defined it.",
["Did C++17 make this well-defined? => No; operands of `+` are still unsequenced.",
 "Which warning catches it? => GCC's `-Wsequence-point` and Clang's `-Wunsequenced`."]),

477: D("`std::endl` inserts a newline and then flushes the stream; `\"\\n\"` only inserts a newline, leaving buffered output to be flushed later.",
"""Flushing forces a write system call each time, which makes loops printing thousands of lines far slower. Prefer `'\\n'` and flush explicitly (`std::flush`) when needed, such as before a crash-prone operation or when interactive output must appear.

`std::cerr` is unbuffered (unit-buffered) and `std::cout` is typically tied to `std::cin`, so it's flushed before input anyway.""",
"Using `std::endl` in hot logging loops, making output many times slower.",
["When is flushing actually needed? => Before a potential crash, when another process reads the output live, or for interactive prompts.",
 "Why does `cout` appear before `cin` reads input even without flushing? => `cin` is tied to `cout`, which flushes it before input operations."]),

478: D("Floating-point numbers represent most decimal values approximately and accumulate rounding error, so mathematically equal results can differ in the last bits: `0.1 + 0.2 == 0.3` is false.",
"""Compare with a tolerance appropriate to the magnitude: absolute epsilon near zero, relative tolerance otherwise (`abs(a - b) <= rel * max(abs(a), abs(b))`), or units-in-the-last-place comparison. `std::numeric_limits<double>::epsilon()` is the gap at 1.0, not a universal tolerance.

Exact comparison is fine for values known to be exactly representable (small integers, results of copying). NaN compares unequal to everything, including itself.""",
"Using `numeric_limits<double>::epsilon()` as an absolute tolerance for large values, where it's smaller than the spacing between representable numbers.",
["How do you check for NaN? => `std::isnan(x)` or `x != x`.",
 "Why is `epsilon()` not a general tolerance? => It's the spacing at 1.0; spacing scales with magnitude."]),

479: D("Integer overflow occurs when a result exceeds the type's range; unsigned overflow is well defined (wraps modulo 2ⁿ), but signed overflow is undefined behaviour in C++.",
"""Because signed overflow is UB, compilers assume it never happens: `x + 1 > x` may be optimized to `true`, and loops can be transformed accordingly. C++20 mandates two's complement representation but still leaves overflow undefined.

Detection: `__builtin_add_overflow` (GCC/Clang), checking before operating (`a > INT_MAX - b`), using wider types, `-fsanitize=signed-integer-overflow` (UBSan), or `-ftrapv`.""",
"Checking for overflow after the fact with `if (a + b < a)` on signed integers; the check itself relies on UB and may be optimized away.",
["Did C++20's two's complement guarantee make overflow defined? => No; only the representation is defined, arithmetic overflow is still UB.",
 "How do you safely detect overflow? => Pre-checks against limits or `__builtin_add_overflow`/`ckd_add`-style checked functions."]),

480: D("`std::cin >> variable` skips leading whitespace and reads one whitespace-delimited token, leaving the terminating newline in the buffer; `std::getline(std::cin, str)` (or `cin.getline(buf, n)`) reads a whole line including spaces up to the newline, which it consumes and discards.",
"""The classic bug: `cin >> age; getline(cin, name);` makes `getline` return an empty string immediately because the newline after the number is still pending. Fix with `cin >> std::ws` or `cin.ignore(std::numeric_limits<std::streamsize>::max(), '\\n')` before `getline`.

`cin.getline(char*, n)` works with C arrays; `std::getline` with `std::string` is safer.""",
"Mixing `>>` and `getline` without discarding the leftover newline, getting empty lines.",
["How do you fix an empty `getline` after `>>`? => `std::getline(std::cin >> std::ws, line)` or `cin.ignore(...)`.",
 "What happens when `>>` fails to parse? => The stream enters a fail state; later reads fail until `clear()` is called."]),

481: D("`const` means an object can't be modified through that name (its value may be known only at runtime); `constexpr` means the value or function is usable in constant expressions, evaluated at compile time where required, and `constexpr` variables are also implicitly `const`.",
"""`const int n = readConfig();` is fine; `constexpr int n = readConfig();` fails unless `readConfig` is `constexpr` and evaluable at compile time. `constexpr` values can be array bounds, template arguments and `static_assert` operands.

\"Shallow\" const: for pointers, `const` applies to one level only (`int* const p` vs `const int* p`), and a `const` member function can't modify members but can modify objects they point to.""",
"Assuming `const` implies compile-time evaluation; a `const` variable initialized at runtime can't be used as a template argument.",
["What does `consteval` add? => It requires evaluation at compile time for every call (immediate functions).",
 "What is \"shallow\" const for pointers? => Constness of the pointer doesn't propagate to the pointee; `std::experimental::propagate_const` addresses this."]),

482: D("Since C++11, `std::string` guarantees that `s[s.size()]` returns a reference to a null character `CharT()`, so reading `std::string(\"abc\")[3]` is well-defined and yields `'\\0'`.",
"""The string's buffer is always null-terminated (so `c_str()` and `data()` are O(1)). You may read that element, but modifying it to any value other than `CharT()` is undefined behaviour.

`at(size())` still throws `std::out_of_range`, and `s[size() + 1]` is undefined. For `std::vector` or `std::string_view`, indexing at `size()` is undefined.""",
"Assuming `std::string_view` also guarantees a terminator at `sv[sv.size()]`; it doesn't, which breaks code passing `sv.data()` to C APIs.",
["Does `at(size())` also return the null character? => No, `at()` throws `std::out_of_range` for `pos >= size()`.",
 "Is it safe to pass `string_view::data()` to a C function? => Only if you know the view is null-terminated, which it doesn't guarantee."]),

483: D("The most derived object is the complete object whose dynamic type is the class actually constructed (e.g. `Derived` in `new Derived`); base class subobjects are parts of it, and polymorphic operations use its type.",
"""`typeid(*ptr)` and virtual dispatch report the most derived type (for polymorphic classes); `dynamic_cast<void*>(p)` returns the address of the most derived object, which may differ from `p` under multiple inheritance.

During construction and destruction the dynamic type changes: while `Base`'s constructor runs, the object behaves as a `Base`. Virtual bases are initialized by the most derived class's constructor.""",
"Assuming a base pointer's address equals the full object's address under multiple inheritance, then freeing or comparing it incorrectly.",
["What does `dynamic_cast<void*>` return? => A pointer to the most derived object.",
 "Who initializes virtual base classes? => The most derived class's constructor."]),

484: D("During destruction, the object's dynamic type reverts to the class whose destructor is running, so a virtual call from an abstract class's destructor resolves to that class's own pure virtual function; calling a pure virtual this way is undefined behaviour.",
"""Derived members have already been destroyed, so dispatching to derived overrides would access dead objects; hence the language resolves calls to the current class. If that function is pure, most implementations call `__cxa_pure_virtual` and abort with \"pure virtual method called\".

Direct calls are often diagnosed; indirect ones (the destructor calls a non-virtual helper that calls the virtual function) usually aren't. The same applies to constructors.""",
"Calling a helper like `shutdown()` in a base destructor that internally invokes a pure virtual `doShutdown()`, crashing at runtime.",
["What message usually appears? => \"pure virtual method called\" followed by termination.",
 "How do you run derived cleanup correctly? => Put it in the derived destructor, or call an explicit `close()` before destruction."]),

485: D("Sequenced-before is an ordering where one evaluation completes before another starts; unsequenced evaluations may overlap or occur in any order (conflicting modifications are undefined behaviour); indeterminately sequenced evaluations occur in some unspecified order but don't overlap.",
"""Examples: statements are sequenced; operands of `+` are unsequenced (`i++ + i++` is UB); function arguments are indeterminately sequenced since C++17 (each argument fully evaluated before another starts, order unspecified), so `f(g(), h())` is well-defined but order-dependent.

C++17 made `a << b`, `a = b` (right before left), `a[b]` and `a.b(c)` chaining sequenced left to right, fixing cases like `s.replace(...).replace(...)` and `m[k] = m.size()`.""",
"Relying on function argument evaluation order (e.g. both arguments read from the same stream) and getting different results across compilers.",
["Is `f(i++, i++)` UB in C++17? => No, the arguments are indeterminately sequenced, so it's unspecified which gets which value, but not UB.",
 "What did C++17 change for `cout << a << b`? => Left operands are sequenced before right ones for `<<`, so side effects occur in order."]),

486: D("Class members are always initialized in their declaration order in the class, regardless of the order written in the constructor's member initializer list.",
"""If the initializer list is written in a different order and one member's initializer uses another, you may read an uninitialized member: `struct S { int a; int b; S() : b(1), a(b + 1) {} };` initializes `a` first from garbage `b`.

Compilers warn (`-Wreorder`). Best practice: write initializer lists in declaration order, and avoid initializers depending on other members; base classes are initialized before members, in declaration order of the base list.""",
"Initializing a buffer member from a `size_` member declared after it, reading an uninitialized size.",
["Which warning catches mismatched order? => `-Wreorder` (enabled by `-Wall` in GCC).",
 "In what order are members destroyed? => Reverse declaration order."]),

487: D("The as-if rule lets the compiler transform a program in any way as long as its observable behaviour matches the abstract machine's: volatile accesses, data written to files at termination, and interactive I/O dynamics.",
"""Everything else (temporaries, loop structure, function calls, memory layout of locals) may be changed: inlining, reordering, removing dead stores, and vectorizing are all as-if transformations. Copy elision is an explicit exception allowed to change observable behaviour (skipping side effects in copy constructors).

Programs with undefined behaviour have no constraints at all; the as-if rule then gives no guarantees, which is why UB can \"time travel\".""",
"Assuming timing, memory contents or unused writes are observable behaviour; measuring code whose result is unused may be optimized away entirely.",
["Why can benchmarks be optimized away? => Unused results aren't observable, so computations producing them can be removed.",
 "Which optimization may change observable behaviour legally? => Copy/move elision."]),

488: D("`volatile` tells the compiler that every access to the object is observable and must be performed exactly as written (no caching in registers, no elimination or reordering relative to other volatile accesses); it doesn't provide atomicity or inter-thread ordering.",
"""Correct uses: memory-mapped hardware registers, variables modified by signal handlers (with `volatile sig_atomic_t`), and preventing benchmark code elimination. Common misconception: using `volatile` for thread synchronization. It doesn't prevent data races (still UB), doesn't emit memory barriers, and `volatile int++` isn't atomic.

C++20 deprecated some compound operations on volatiles (`++`, `+=` on volatile) because they imply misleading atomicity.""",
"Using a `volatile bool stop` flag between threads instead of `std::atomic<bool>`, which is a data race in C++.",
["What should replace volatile for thread flags? => `std::atomic<bool>`.",
 "Why is volatile essential for MMIO? => Each register read or write has side effects on hardware, so none can be elided or merged."]),

489: D("A trivial type has trivial (compiler-provided, doing nothing special) default constructor, copy/move operations and destructor; a trivially copyable type has trivial copy/move and destructor, which is what makes copying its bytes with `memcpy` well-defined.",
"""Trivially copyable types can be copied with `memcpy`, sent as raw bytes, used with `std::bit_cast`, and stored in `std::atomic`. Non-trivially copyable types (with user copy constructors, virtual functions, owning pointers) may break when copied bytewise (vptrs, self-pointers, double frees).

Check with `static_assert(std::is_trivially_copyable_v<T>)` next to code that relies on it, e.g. structs overlaid on device command buffers.""",
"`memcpy`-ing a struct containing a `std::string`, duplicating the internal pointer and causing double frees.",
["Which trait matters for `memcpy`? => `std::is_trivially_copyable`.",
 "Does a user-defined constructor break trivial copyability? => Only a user-provided copy/move constructor, assignment or destructor does; other constructors affect triviality of default construction."]),

490: D("POD (Plain Old Data) described types compatible with C: both trivial and standard-layout; C++20 deprecated `std::is_pod` in favour of the two separate traits.",
"""Trivial means special member functions are compiler-provided (safe to `memcpy` and create without construction); standard-layout means a predictable memory layout like a C struct (same access control for data members, no virtual functions or virtual bases, restrictions on base classes).

C compatibility needs standard layout (layout matches C) and trivial copyability (bytes can be shared). Such types can be passed across `extern \"C\"` interfaces and overlaid on hardware or file formats.""",
"Adding a virtual function or a `std::string` member to a struct shared with C code or firmware, silently changing its layout.",
["Why was `std::is_pod` deprecated? => It conflated two separate properties; use `is_trivial` and `is_standard_layout` explicitly.",
 "What does standard layout guarantee? => A C-compatible layout, and the first member's address equals the object's address."]),

491: D("`std::is_trivially_copyable` means objects can be copied byte-by-byte (via `memcpy`) safely; `std::is_standard_layout` means the object's memory layout is C-compatible and predictable (members in order, first member at offset 0, `offsetof` supported).",
"""They're independent: a class with private and public data members may be trivially copyable but not standard layout; a class with a user-defined copy constructor may be standard layout but not trivially copyable.

For serialization to binary formats or sharing with C and hardware, you typically want both. `std::has_unique_object_representations` additionally says there's no padding, needed for hashing bytes.""",
"Hashing or comparing structs bytewise (`memcmp`) when padding bytes may contain garbage, even though they're trivially copyable.",
["Can a type be trivially copyable but not standard layout? => Yes, e.g. data members with mixed access specifiers.",
 "What trait tells you there's no padding? => `std::has_unique_object_representations`."]),

492: D("With multiple empty bases, the Empty Base Optimization usually lets them all occupy zero bytes, except that two subobjects of the same type can't share an address, so repeating an empty base type (directly or indirectly) forces padding.",
"""`struct A{}; struct B{}; struct D : A, B { int x; };` is typically `sizeof(int)`. But if an empty base's type matches the first member's type, or the same empty type appears twice as a base, the compiler must give them distinct addresses.

MSVC historically didn't apply EBO to multiple empty bases by default (`__declspec(empty_bases)` enables it). C++20 `[[no_unique_address]]` offers the same effect for members.""",
"Expecting EBO for classes deriving from several empty policies on MSVC without `__declspec(empty_bases)`, getting larger objects.",
["When can't EBO apply? => When two subobjects of the same empty type would share an address.",
 "What's the MSVC quirk? => Multiple-empty-base EBO requires `__declspec(empty_bases)`."]),

493: D("Unspecified behaviour is valid behaviour where the standard allows several outcomes without requiring documentation (like function argument evaluation order); undefined behaviour means the standard imposes no requirements at all, and the entire program's behaviour becomes unpredictable.",
"""Unspecified: the program is correct as long as it doesn't depend on the choice (e.g. order of evaluating `f() + g()` operands, whether string literals are distinct objects). UB: signed overflow, out-of-bounds access, null dereference, data races, use after free; compilers optimize assuming it never happens.

Tools: sanitizers catch UB at runtime; `constexpr` evaluation rejects UB at compile time.""",
"Treating UB as \"unspecified\" and assuming it yields some reasonable value; optimizers can delete checks or entire code paths.",
["Give an example of unspecified behaviour. => Order of evaluation of operands of `+`, or of function arguments.",
 "How can you catch UB during testing? => Sanitizers (ASan, UBSan, TSan) and compile-time evaluation in `constexpr`."]),

494: D("Implementation-defined behaviour is behaviour the standard leaves to the implementation, which must document its choice: sizes of `int` and `long`, whether `char` is signed, the result of right-shifting negative numbers before C++20.",
"""Compared with unspecified behaviour (valid choices, not documented) and undefined behaviour (no requirements), implementation-defined behaviour is predictable on a given compiler and platform but non-portable.

Portable code uses fixed-width types (`std::int32_t`), `static_assert` on assumptions (e.g. `static_assert(sizeof(long) == 8)`), and avoids depending on `char` signedness.""",
"Assuming `char` is signed; on ARM Linux it's unsigned by default, breaking checks like `c < 0`.",
["Name three implementation-defined properties. => Size of `int`, signedness of `char`, and `std::size_t`'s width.",
 "How do you guard assumptions about implementation-defined behaviour? => `static_assert` checks on sizes and traits."]),

495: D("Default initialization (`T x;`) calls the default constructor for classes but leaves scalars and arrays of scalars with indeterminate values; value initialization (`T x{};`, `T()`) zero-initializes scalars and default-constructs or zero-initializes class objects; zero initialization sets memory to zero and happens for static-storage objects before other initialization.",
"""For a class with a user-provided default constructor, value initialization just calls it. For an aggregate or class without one, `{}` zero-initializes members before any constructor runs. Static and thread-local variables are always zero-initialized first.

Reading an indeterminate value is undefined behaviour (C++26 changes this to \"erroneous behaviour\"). Rule of thumb: always use `{}` for local variables without a meaningful initial value.""",
"`Config c;` for an aggregate struct with `int` members, reading garbage values; write `Config c{};`.",
["What's the difference between `new int` and `new int()`? => `new int` is default initialized (indeterminate); `new int()` is value initialized to 0.",
 "When does zero initialization happen automatically? => For objects with static or thread storage duration, before any dynamic initialization."]),

496: D("`int arr[5] = {};` is aggregate initialization: elements without explicit initializers are value-initialized (zero); `int x;` for a local variable is default initialization, which leaves a scalar with an indeterminate value.",
"""Rule: with a brace initializer, missing elements become zero (`int a[5] = {1};` gives `{1,0,0,0,0}`). Without an initializer, local scalars and arrays are indeterminate; globals and statics are zero-initialized.

The distinction exists for performance: large local buffers that will be overwritten needn't be zeroed. Compilers offer `-ftrivial-auto-var-init=zero` for hardening, and C++26 defines reading them as erroneous behaviour.""",
"Assuming `int a[5] = {1};` fills all elements with 1; only the first is 1 and the rest are 0.",
["What does `int a[5] = {1};` produce? => `{1, 0, 0, 0, 0}`.",
 "Why aren't local variables zeroed by default? => To avoid initialization costs when values are about to be overwritten."]),

497: D("A complete type is one whose size and layout are known at that point (e.g. a class after its definition); an incomplete type has been declared but not defined (`class Device;`), `void`, or an array of unknown bound.",
"""With an incomplete type you can declare pointers and references, declare functions taking or returning it, and forward-declare. You can't create objects, use `sizeof`, access members, inherit from it, or delete it (deleting an incomplete type with a non-trivial destructor is UB; compilers warn).

This underlies forward declarations, pImpl (`std::unique_ptr<Impl>` requires completeness where the destructor is instantiated), and some standard library constraints (`std::vector<Incomplete>` members are allowed since C++17 with conditions).""",
"`delete`-ing a pointer to an incomplete type, which skips the destructor (UB); `std::unique_ptr` turns it into a compile error, which is safer.",
["Why does `unique_ptr<T>` need a complete type at destruction? => Its deleter uses `sizeof`/calls the destructor, so it statically asserts completeness.",
 "Can `std::vector` hold an incomplete type? => Since C++17 you can declare such a vector member, but the type must be complete before members like `size()` are used."]),

498: D("The strict aliasing rule says an object may be accessed only through an lvalue of its own type (with cv and signedness variants), a base class, or `char`/`unsigned char`/`std::byte`; accessing it through an unrelated type is undefined behaviour.",
"""Compilers use this to assume that pointers of unrelated types don't point to the same memory, allowing values to stay in registers and loads to be reordered. Code like `float f; int bits = *(int*)&f;` may then read stale values at `-O2`.

Safe alternatives: `std::memcpy` into the target type (optimized to a register move), `std::bit_cast` (C++20), or `std::start_lifetime_as` (C++23). Some projects disable the optimization with `-fno-strict-aliasing` (the Linux kernel does).""",
"Casting a byte buffer received from a device to `uint32_t*` and reading from it, violating aliasing and possibly alignment.",
["What's the safe way to reinterpret float bits? => `std::bit_cast<std::uint32_t>(f)` or `memcpy`.",
 "Which types may alias anything? => `char`, `unsigned char` and `std::byte`."]),

499: D("A narrowing conversion is an implicit conversion that may lose information: floating to integer, larger to smaller integer, integer to floating that can't represent it, or signed/unsigned changes that can't represent the value; brace initialization rejects narrowing, unlike `=` or parentheses.",
"""`int x = 3.7;` compiles (with a possible warning) and yields 3; `int x{3.7};` is a compile error. `char c{300};` fails; `std::uint8_t b{len};` fails if `len` is an `int` variable, even if its value fits, because only constant expressions whose values fit are allowed.

This makes `{}` initialization a useful safety net, together with `-Wconversion` for other contexts.""",
"Relying on `{}` to catch narrowing in function arguments or assignments; it only applies to list initialization.",
["Is `std::uint8_t b{200};` narrowing? => No, a constant expression whose value fits is allowed.",
 "Which warning catches narrowing outside brace initialization? => `-Wconversion` (and `-Wsign-conversion`)."]),

500: D("Duff's device is a manual loop-unrolling technique interleaving a `switch` with a `do-while` loop to handle the remainder iterations; compiler auto-vectorization instead transforms simple loops automatically into SIMD instructions processing several elements per instruction.",
"""Duff's device (1983) reduced loop overhead on processors without good branch handling; today it's a curiosity. Its irregular control flow (jumping into the middle of a loop) actually prevents modern optimizations like vectorization.

Modern approach: write a simple, clear loop over contiguous data, let the compiler unroll and vectorize at `-O2`/`-O3`, verify with vectorization reports, and use intrinsics or SIMD libraries only for measured hotspots.""",
"Hand-writing Duff's device in modern code \"for performance\", which usually makes it slower by blocking vectorization.",
["Why does Duff's device hurt modern optimizers? => Its irregular control flow prevents loop analysis needed for vectorization.",
 "What's the modern replacement? => A plain loop the compiler unrolls and vectorizes automatically, verified via reports."]),
}
