DEEP = {

141: D("A pointer is an object that holds the address of another object or function (or a null value), and whose type tells the compiler what it points to.",
"""Pointers support dereference (`*p`), member access (`p->x`), arithmetic within arrays, comparison and reassignment. The pointed-to type controls arithmetic scaling and what `*p` yields.

In modern C++, raw pointers should be **non-owning** (observers). Ownership belongs to smart pointers or containers; if something can't be null, prefer a reference; for arrays prefer `std::span`.

On embedded and driver code, pointers to `volatile` memory-mapped registers are a legitimate raw-pointer use.""",
"Using raw owning pointers (`T* p = new T;`) in application code, making leaks and double deletes easy.",
["What is a non-owning pointer? => A pointer used only to observe an object whose lifetime is managed elsewhere.",
 "When should you use a pointer instead of a reference? => When the target is optional (may be null) or must be reseated."]),

142: D("A null pointer is a pointer value that points to no object; in C++11 and later it is written `nullptr`, of type `std::nullptr_t`.",
"""`nullptr` replaced `NULL` and `0` because those are integers: with overloads `f(int)` and `f(char*)`, `f(NULL)` calls the `int` version, while `f(nullptr)` correctly calls the pointer version. `nullptr` converts to any pointer and pointer-to-member type but not to integers.

Dereferencing a null pointer is undefined behaviour. Deleting a null pointer is a safe no-op, so `if (p) delete p;` is unnecessary.""",
"Using `NULL` or `0` in overloaded calls or templates, where they deduce as integers instead of pointers.",
["Why was `nullptr` introduced? => To have a null pointer constant with its own type that never converts to integers, fixing overload and template deduction problems.",
 "Is `delete nullptr` safe? => Yes, deleting a null pointer does nothing."]),

143: D("A dangling pointer points to memory that is no longer a valid object: freed heap memory, a destroyed local variable, or an element of a container that reallocated.",
"""Common causes: using a pointer after `delete`, returning the address of a local, keeping pointers into a `std::vector` across `push_back`, storing `std::string_view` or `span` of temporaries, or capturing `this` in a callback that outlives the object.

Dereferencing a dangling pointer is undefined behaviour; it may appear to work until memory is reused. Detection: AddressSanitizer (heap-use-after-free, stack-use-after-return), static analysers, and lifetime-aware code review.

Prevention: clear ownership with smart pointers, `std::weak_ptr` for observers of shared objects, indices instead of pointers into growing containers.""",
"Setting `p = nullptr` after `delete p` and believing all dangling pointers are gone, while other copies of the pointer still refer to freed memory.",
["Which tool catches use-after-free? => AddressSanitizer (`-fsanitize=address`).",
 "How do you safely observe an object owned by a `shared_ptr`? => Hold a `std::weak_ptr` and `lock()` it before use."]),

144: D("Pointer arithmetic adds or subtracts integers to move a pointer by whole elements of its pointed-to type, and subtracts two pointers into the same array to get the element distance (`std::ptrdiff_t`).",
"""`p + n` advances by `n * sizeof(*p)` bytes. It's defined only within the same array object (including one past the end); going beyond, or subtracting pointers from different arrays, is undefined behaviour.

Arithmetic isn't allowed on `void*` in standard C++ (GCC allows it as an extension); cast to `std::byte*` or `char*` for byte offsets.

Prefer iterators, indices, and `std::span` subranges (`s.subspan(off, len)`), which express the same thing with bounds information.""",
"Computing `p + len` beyond the one-past-the-end position \"just to compare\"; merely forming such a pointer is undefined behaviour.",
["What type is the difference of two pointers? => `std::ptrdiff_t`, a signed integer type.",
 "How do you do byte-offset arithmetic safely? => Use `std::byte*` / `unsigned char*`, or better `std::span<std::byte>` with `subspan`."]),

145: D("A `void*` is a pointer to an object of unknown type; any object pointer converts to it implicitly, but it must be cast back to the correct type before dereferencing.",
"""Uses: C APIs (`memcpy`, `malloc`, callback user data), type-erased storage in low-level code.

In C++, converting `void*` back requires an explicit `static_cast<T*>`, and casting to the wrong type is undefined behaviour. You can't dereference it, do arithmetic on it, or `delete` it meaningfully (the destructor isn't known).

Modern alternatives: templates, `std::any`, `std::variant`, `std::span<std::byte>` for raw buffers, and typed callbacks (`std::function`).""",
"Casting a `void*` user-data pointer back to a base class when it was stored as a derived pointer (or vice versa) in multiple inheritance, landing on the wrong address.",
["Why can't you `delete` a `void*` safely? => The compiler doesn't know the type, so no destructor runs; it's undefined behaviour.",
 "What's the type-safe replacement for `void*` user data? => A capturing lambda stored in `std::function`, or templates."]),

146: D("A reference is an alias that must be bound to an object at initialization and can't be reseated or null; a pointer is an object holding an address that can be null, reassigned and used for arithmetic.",
"""Syntax: references are used like the object itself (`r.x`), pointers need `*` or `->`. A reference has no identity of its own (you can't take its address or make arrays of references); a pointer is a first-class object.

Use references for parameters and return values that always refer to a valid object; pointers when \"no object\" is valid or rebinding is needed. `std::reference_wrapper<T>` provides a copyable, reseatable reference for containers.""",
"Returning a reference from a function that might have nothing to return, forcing callers to trust a hidden precondition; return a pointer or `std::optional`.",
["How do you store references in a container? => Use `std::reference_wrapper<T>` (via `std::ref`).",
 "Is `sizeof` a reference equal to `sizeof` a pointer? => `sizeof(T&)` is `sizeof(T)`; references aren't objects, though implementations often use pointers internally."]),

147: D("A pointer to a pointer (`T**`) stores the address of a pointer, allowing a function to change which object the caller's pointer refers to, or to represent arrays of pointers.",
"""Classic uses: C APIs that return allocated objects through an out-parameter (`int create(Device** out)`), `char** argv`, and arrays of strings.

In C++ prefer a reference to a pointer (`T*&`), returning the pointer (or `std::unique_ptr`), or containers (`std::vector<std::string>` instead of `char**`). Jagged 2D data should be `std::vector<std::vector<T>>` or a flat vector with index math.""",
"Allocating 2D arrays as `int**` with a separate `new` per row, which fragments memory and complicates cleanup; use a single contiguous buffer.",
["Why does a C API take `Device**`? => To write the created pointer back into the caller's variable.",
 "What's the C++ equivalent of an out-pointer parameter? => Return `std::unique_ptr<Device>` (or `std::expected`), or take `Device*&`."]),

148: D("A function pointer stores the address of a function with a specific signature, e.g. `int (*cmp)(const void*, const void*);`, and can be called like the function.",
"""Readability helpers: `using Handler = void(*)(int);` or `std::add_pointer_t<void(int)>`.

Function pointers can't capture state; stateless lambdas convert to them, which is how C callbacks are fed from C++. For stateful callbacks, use `std::function` (type-erased, may allocate) or a template parameter (inlinable).

In firmware, arrays of function pointers implement dispatch tables and interrupt vector tables.""",
"Passing a capturing lambda where a C function pointer is required; only captureless lambdas convert. Pass state through a `void*` user-data argument instead.",
["How do you make a function-pointer type readable? => A type alias: `using Callback = void(*)(int status);`.",
 "`std::function` vs function pointer? => `std::function` can hold stateful callables but has type-erasure overhead; function pointers are lightweight but stateless."]),

149: D("A pointer to member function (`R (C::*pmf)(Args)`) identifies a member function independent of any object; you call it with an object using `.*` or `->*`, e.g. `(obj.*pmf)(args)`.",
"""Declaration: `void (Device::*action)(int) = &Device::reset;` then `(dev.*action)(3);` or `(ptr->*action)(3);`. Parentheses are required because `.*` binds weaker than the call operator.

Member function pointers may be larger than ordinary pointers (they can encode virtual function offsets and `this` adjustments for multiple inheritance), so they can't be converted to `void*`.

Modern code often uses `std::invoke(pmf, obj, args...)`, `std::mem_fn`, or lambdas instead.""",
"Writing `obj.*pmf(args)` without parentheses, which parses as `obj.*(pmf(args))` and fails to compile.",
["Why can a member function pointer be bigger than a normal pointer? => It may store a vtable offset and a `this` adjustment for multiple/virtual inheritance.",
 "What does `std::invoke` do with a member pointer? => Calls it on the given object uniformly, like `(obj.*pmf)(args...)`."]),

150: D("`const int* p` (same as `int const* p`) is a pointer to const int; `int* const p` is a const pointer to int; `const int* const p` is a const pointer to const int.",
"""Read declarations from right to left: \"`p` is a const pointer to int\" for `int* const p`.

- `const int* p`: `*p = 1` is an error; `p = &other` is fine.
- `int* const p`: `*p = 1` is fine; `p = &other` is an error.
- `const int* const p`: neither is allowed.

`const int*` doesn't make the pointee immutable; it only forbids changing it **through this pointer**. Another non-const alias can still modify it, which is why the compiler must reload values after writes through other pointers.""",
"Assuming `const T*` guarantees the object never changes; other aliases can modify it while you hold the pointer.",
["What does \"east const\" mean? => Writing `int const*` so const always applies to what's on its left.",
 "Can you convert `int*` to `const int*` implicitly? => Yes; adding const is safe. The reverse needs `const_cast`."]),

151: D("References can't be reseated because the language defines a reference as a permanent alias for the object it was initialized with; assignment through a reference assigns to that object.",
"""`int& r = a; r = b;` copies `b`'s value into `a`; it doesn't make `r` refer to `b`. This design guarantees that a reference always refers to the same valid object, which simplifies reasoning and optimization.

When rebinding is needed, use a pointer, `std::reference_wrapper` (whose assignment rebinds), or `std::optional<std::reference_wrapper<T>>` for an optional rebindable reference. Classes with reference members can't be copy-assigned (the implicit assignment is deleted) for the same reason.""",
"Adding a reference member to a class and then being surprised that it isn't assignable, breaking use in containers that require assignment.",
["What does `r = b;` do for a reference `r`? => Assigns `b`'s value to the object `r` refers to.",
 "Why are classes with reference members not copy-assignable? => References can't be reseated, so the implicit assignment operator is deleted."]),

152: D("Array-to-pointer decay is the implicit conversion of an array expression to a pointer to its first element, which loses the array's size information.",
"""Arrays decay when passed to functions (`void f(int* p)` or `void f(int p[])`, both the same), in most expressions, and when assigned to pointers. Exceptions: `sizeof(arr)`, `&arr`, `decltype(arr)`, and binding to a reference to array (`int (&r)[5] = arr;`).

The consequence is the classic bug of `sizeof(p)` inside a function returning the pointer size, not the array size.

Avoid decay with `std::array` (value semantics, knows its size), `std::span` (pointer plus size), or passing arrays by reference to a template (`template<std::size_t N> void f(int (&a)[N])`).""",
"Computing `sizeof(arr) / sizeof(arr[0])` inside a function that received the array as a parameter; it divides pointer size by element size.",
["How can a function receive an array without decay? => By reference: `template<std::size_t N> void f(int (&a)[N])`, or take `std::span<int>`.",
 "What's `std::size(arr)`? => A C++17 function returning the number of elements of an array (and containers), failing to compile for pointers."]),

153: D("A wild pointer is an uninitialized pointer whose value is indeterminate, so it points to an arbitrary location; using it is undefined behaviour.",
"""Wild pointers come from declaring `T* p;` without initialization (automatic storage). Unlike dangling pointers, they never pointed to a valid object.

Prevention: always initialize pointers (to a valid address or `nullptr`), declare variables at the point where they can be initialized, enable warnings (`-Wuninitialized`, `-Wmaybe-uninitialized`), and use sanitizers (MemorySanitizer for uninitialized reads).""",
"Declaring `Device* dev;` at the top of a function and assigning it in only some branches, then using it on a path where it was never set.",
["Wild vs dangling pointer? => Wild was never initialized; dangling was valid once but its object is gone.",
 "Which sanitizer finds uses of uninitialized values? => MemorySanitizer (Clang `-fsanitize=memory`)."]),

154: D("To pass a 2D array, the function must know all dimensions except the first: `void f(int a[][4], int rows)` or `void f(int (*a)[4], int rows)`; modern C++ prefers a flat buffer with index math or `std::mdspan` (C++23).",
"""Built-in 2D arrays are contiguous rows; decay produces a pointer to the first row (`int (*)[4]`), so the column count must be a compile-time constant in the parameter type. Templates can deduce both: `template<std::size_t R, std::size_t C> void f(int (&a)[R][C])`.

For runtime sizes, use `std::vector<T>` of size `rows * cols` with `a[r * cols + c]`, or `std::vector<std::vector<T>>` for jagged data. C++23 `std::mdspan` provides a multi-dimensional view over contiguous memory with runtime extents.""",
"Passing a `int[3][4]` array to a function taking `int**`: the types are incompatible, and forcing it with a cast reads garbage.",
["Why must the column count be known? => Row-major indexing `a[r][c]` computes `r * cols + c`, so `cols` must be part of the type.",
 "What does `std::mdspan` add? => A non-owning multi-dimensional view with configurable layout and runtime extents (C++23)."]),

155: D("`int* p = arr;` points to the first element (type `int*`, stepping by one `int`); `int (*p)[SIZE] = &arr;` points to the whole array (type pointer-to-array, stepping by `SIZE` ints).",
"""Both hold the same address value, but their types differ: `p + 1` in the first case moves 4 bytes (one int), in the second case `SIZE * 4` bytes (one whole array). Dereferencing the pointer-to-array gives the array itself (`(*p)[i]`), and `sizeof(*p)` is the full array size.

Pointers to arrays appear naturally with 2D arrays (a row pointer) and are how array size can be preserved in function parameters.""",
"Assuming `arr` and `&arr` are interchangeable because they print the same address; their types and arithmetic are different.",
["What is `sizeof(*p)` for `int (*p)[10]`? => `10 * sizeof(int)`.",
 "Where do pointers to arrays appear naturally? => As the decayed type of 2D arrays: `int m[3][4]` decays to `int (*)[4]`."]),

156: D("Yes: a reference to a pointer (`T*&`) lets a function modify the caller's pointer variable itself, for example to allocate or advance it.",
"""Example: `void advance(const char*& cursor) { while (*cursor == ' ') ++cursor; }` moves the caller's cursor. Another: `void reset(Node*& head) { delete head; head = nullptr; }`.

It's the C++ alternative to C's pointer-to-pointer out-parameters, with cleaner syntax. Note the order: `T*&` is a reference to a pointer; a \"pointer to a reference\" (`T&*`) doesn't exist.""",
"Writing `T&*` expecting a reference to a pointer; that's ill-formed because pointers to references aren't allowed.",
["Can you have a pointer to a reference? => No; references aren't objects, so they have no address of their own.",
 "When is `T*&` preferable to returning a new pointer? => When the function updates a cursor or head pointer in place, e.g. in parsers or linked lists."]),

157: D("Passing a pointer by value copies the address, so the function can modify the pointee but not the caller's pointer; passing a pointer by reference (`T*&`) or pointer-to-pointer lets the function change the caller's pointer.",
"""Example bug: `void allocate(int* p) { p = new int(5); }` changes only the local copy, and the caller's pointer stays null (and the allocation leaks). With `void allocate(int*& p)`, the caller's variable is updated.

In modern C++ it's cleaner to return the new pointer, ideally as `std::unique_ptr`, than to use out-parameters.""",
"Writing `init(buffer)` expecting the function to allocate into the caller's pointer when the parameter is taken by value; the caller's pointer is unchanged and memory leaks.",
["Why does assigning to a by-value pointer parameter not affect the caller? => The parameter is a copy of the address.",
 "What's the modern replacement for pointer out-parameters? => Return values (`std::unique_ptr`, `std::optional`, structured bindings)."]),

158: D("Arrays and pointers are different types: an array is a contiguous block of elements with a size known to the type, while a pointer holds one address; arrays decay to pointers to their first element in most expressions, which makes them look similar.",
"""Where they coincide: `a[i]` is defined as `*(a + i)` for both; arrays passed to functions arrive as pointers.

Where they differ: `sizeof(array)` gives the whole size, `sizeof(pointer)` gives 4 or 8; arrays can't be assigned or returned by value; `&array` has type pointer-to-array; string literals are arrays of const char; a pointer can be reseated, an array name cannot.

`std::array` fixes most array quirks: it's copyable, returnable and doesn't decay.""",
"Declaring `extern char* name;` in one file for `char name[] = \"x\";` defined in another: types mismatch and the program misreads memory.",
["Why does `a[i]` work for pointers too? => The subscript operator is defined as `*(a + i)`.",
 "Can you return a C array from a function? => Not by value; return `std::array` instead."]),

159: D("A smart pointer is a class that owns a dynamically allocated object and releases it automatically (RAII), preventing leaks and making ownership explicit.",
"""`std::unique_ptr<T>`: exclusive ownership, move-only, zero overhead compared with a raw pointer; destroys the object when it goes out of scope.

`std::shared_ptr<T>`: shared ownership via a reference-counted control block; the object is destroyed when the last owner goes away. Costs atomic counter updates and an extra allocation (reduced with `make_shared`).

`std::weak_ptr<T>`: non-owning observer of a `shared_ptr`-managed object; `lock()` gives a temporary `shared_ptr` or empty if the object is gone, which avoids dangling access and breaks reference cycles.

Smart pointers prevent leaks and double deletes, but not all dangling: a raw pointer obtained with `.get()` can still outlive the object.""",
"Creating two `shared_ptr`s from the same raw pointer (`shared_ptr<T> a(p), b(p);`): two control blocks, and the object is deleted twice.",
["Which smart pointer should be the default? => `std::unique_ptr`; switch to `shared_ptr` only for genuinely shared ownership.",
 "How does `weak_ptr` break cycles? => It doesn't increase the reference count, so cyclic structures can still be destroyed."]),

160: D("`const T&` means \"a valid object I will read but not modify\"; `const T*` means \"an object I will read, or possibly nothing (null)\", and makes the address-taking visible at the call site.",
"""References communicate non-optional input and allow calls with temporaries (`f(T{})`); pointers communicate optionality and may be stored for later (though storing either raises lifetime questions).

Guideline: use `const T&` for required inputs, `const T*` (or `std::optional<std::reference_wrapper<const T>>`, or an overload) for optional ones. Neither transfers ownership; pass `std::unique_ptr` by value to transfer ownership.""",
"Taking `const T*` for a required parameter, forcing every caller to write `&obj` and every implementation to check for null.",
["Can a `const T&` parameter bind to a temporary? => Yes; a `const T*` parameter needs an addressable object.",
 "How do you signal ownership transfer in a signature? => Take `std::unique_ptr<T>` by value."]),

161: D("Inside a `const` member function of class `C`, `this` has type `const C*` (a prvalue, so it can't be reassigned), which is why non-mutable members can't be modified there.",
"""Every member access `x` means `this->x`, so writing to a member through a `const C*` is a compile error, except for members declared `mutable`. Calling another member function from a const one is only allowed if that function is also const.

In a `volatile` or `const volatile` member function, `this` is `volatile C*` or `const volatile C*` accordingly. C++23's explicit object parameter makes this visible: `void f(this const C& self)`.""",
"Using `const_cast<C*>(this)` inside a const function to modify state, which is undefined behaviour if the object itself was declared const.",
["What is `this` in a non-const member function? => `C*`.",
 "How do you allow modification of a cache in a const function? => Declare the cache member `mutable` (and protect it if accessed from threads)."]),

162: D("Returning a pointer or reference to a local variable produces a dangling pointer or reference: the local is destroyed when the function returns, so any use afterwards is undefined behaviour.",
"""Examples: `int* f() { int x = 5; return &x; }`, `const std::string& name() { std::string s = ...; return s; }`, or returning `std::string_view` of a local `std::string`.

It may seem to work in tests because the stack memory isn't overwritten yet. Compilers warn (`-Wreturn-local-addr`, `-Wdangling`) in simple cases, and AddressSanitizer's `detect_stack_use_after_return` catches it at runtime.

Return by value instead; move semantics and copy elision make it cheap.""",
"Returning `std::string_view` or `std::span` into a local container; the view compiles fine and dangles immediately.",
["Why can the bug appear to work? => The stack memory still holds the old value until another call overwrites it.",
 "What should you return instead? => The object by value; copy elision and moves make it efficient."]),

163: D("Pointer aliasing means two or more pointers (or references) may refer to the same memory; because writes through one could change what another reads, the compiler must be conservative, which limits optimization.",
"""Example: in `void add(int* a, int* b, int n) { for (...) a[i] += *b; }`, the compiler must reload `*b` every iteration because `a[i]` might alias `*b`.

The **strict aliasing rule** lets compilers assume that pointers to different types (e.g. `int*` and `float*`) don't alias, except for `char`, `unsigned char` and `std::byte`, which may alias anything. Violating it (type punning through casts) is undefined behaviour and breaks under optimization.

Hints: the non-standard `__restrict` extension, copying values into locals, and `std::bit_cast` or `memcpy` for type punning.""",
"Reading a `float` through an `int*` obtained by `reinterpret_cast` to inspect its bits; with optimizations the compiler may reorder or remove the access. Use `std::bit_cast`.",
["Which types may alias any object? => `char`, `unsigned char` and `std::byte`.",
 "How do you tell the compiler pointers don't alias? => The `__restrict` extension (GCC, Clang, MSVC), or restructure code to use local copies."]),

164: D("`std::addressof(x)` always returns the real address of `x`, even if its type overloads unary `operator&`; `&x` calls that overload if one exists.",
"""Some types overload `operator&` (COM smart pointers like `CComPtr`, proxy and expression types), so `&x` may return something other than the object's address. Generic code (containers, allocators, `std::construct_at`) therefore uses `std::addressof`. It's also `constexpr` since C++17.

In everyday non-generic code with ordinary types, `&x` is fine.""",
"Using `&x` inside a template that stores addresses of arbitrary types; a type with overloaded `operator&` breaks it.",
["Why would a type overload `operator&`? => To return an interface pointer or proxy (e.g. COM wrappers), which is rare and usually discouraged.",
 "Where does the standard library use `std::addressof`? => In containers, allocators and algorithms that need real object addresses in generic code."]),

165: D("Deleting through a `void*` is undefined behaviour: the compiler doesn't know the object's type, so it can't call the destructor or know the correct size and deallocation function.",
"""Compilers usually warn (\"deleting 'void*' is undefined\"). Even for trivial types where no destructor is needed, it's formally undefined.

When type-erased storage must be freed, keep the type information: store a deleter function along with the pointer (`std::unique_ptr<void, void(*)(void*)>` with a correct deleter), or use `std::any`/`std::shared_ptr<void>` (which captures the right deleter when constructed from a typed pointer).""",
"Storing objects of various types as `void*` in a registry and deleting them as `void*` at shutdown; destructors never run and behaviour is undefined.",
["How does `std::shared_ptr<void>` delete correctly? => It captures the real deleter from the original typed pointer at construction.",
 "What's the correct way to free a type-erased object? => Store a deleter that knows the real type alongside the pointer."]),

166: D("A fat pointer carries extra information alongside the address, such as a length, a vtable pointer or a `this` adjustment; in C++ the concept appears in `std::span`, `std::string_view`, member function pointers and type-erased callables.",
"""Examples:

- `std::span<T>` and `std::string_view`: pointer plus length (two words), enabling bounds-aware views.
- Pointers to member functions: may encode a virtual function offset and `this` adjustment.
- `std::function`, `std::any`: store the object plus operations (manual vtable).

Contrast with C++ polymorphism, where the vtable pointer lives inside the object (thin pointer), whereas Rust's trait objects and Go's interfaces use fat pointers (data plus vtable).""",
"Passing `(T* data, size_t len)` pairs manually through many functions instead of a single `std::span`, inviting mismatched lengths.",
["Why is `std::span` a fat pointer? => It stores both the data pointer and the element count.",
 "Where does C++ put the vtable pointer for polymorphic objects? => Inside the object (vptr), so ordinary pointers stay thin."]),

167: D("`static_cast` between pointer types only allows well-defined conversions (to and from `void*`, and up/down a class hierarchy, adjusting the address when needed); `reinterpret_cast` converts between unrelated pointer types by reinterpreting the address, without any adjustment or checking.",
"""In multiple inheritance, `static_cast<Base2*>(derivedPtr)` adds the correct offset; `reinterpret_cast<Base2*>(derivedPtr)` keeps the same address, which is wrong.

`reinterpret_cast` is for low-level tasks: pointer-to-integer conversions (`std::uintptr_t`), memory-mapped register addresses (`reinterpret_cast<volatile uint32_t*>(0x40021000)`), and serialization buffers viewed as `std::byte*`. Accessing an object through an unrelated type obtained this way usually violates strict aliasing.""",
"Using `reinterpret_cast` to move between classes in a hierarchy, skipping the pointer adjustment that multiple inheritance requires.",
["Which cast is used for memory-mapped hardware registers? => `reinterpret_cast` from an integer address to a `volatile` pointer type.",
 "Does `static_cast` check downcasts at runtime? => No; only `dynamic_cast` does. A wrong `static_cast` downcast is undefined behaviour."]),

168: D("Relational comparison (`<`, `>`) of pointers to unrelated objects is not defined by the language ordering rules: in C++ the result is **unspecified** (in C it's undefined), because objects may live in unrelated memory regions without a meaningful order.",
"""Pointer ordering is defined only within the same array (or members of the same object). Across unrelated objects, implementations may use segmented or tagged address spaces, so no consistent order is guaranteed by `<`.

When you need a consistent total order (e.g. to use pointers as keys in `std::map` or to lock mutexes in address order), use `std::less<T*>`, which the standard guarantees provides a strict total order over all pointers, or compare `std::uintptr_t` values.

Equality comparison (`==`, `!=`) of any two pointers of compatible type is always well-defined.""",
"Ordering unrelated pointers with `<` in a custom comparator for a lock-ordering scheme; use `std::less<>` for a guaranteed total order.",
["What gives a guaranteed total order over pointers? => `std::less<T*>` (and `std::ranges::less`).",
 "Is `p == q` always valid for unrelated pointers? => Yes, equality comparison is always defined."]),

169: D("Dereferencing a null pointer is undefined behaviour, not a guaranteed crash: the standard imposes no requirements, and compilers assume it never happens when optimizing.",
"""On typical desktop OSes page zero is unmapped, so a raw dereference usually faults. But: some embedded systems map valid memory at address 0 (reads succeed silently); accessing a member at a large offset (`p->big_array[100000]`) may land in mapped memory; and optimizers can delete a later null check because \"the pointer was already dereferenced, so it can't be null\" (a known Linux kernel bug class).

Treat null-pointer bugs as logic errors: check at boundaries, use references or `gsl::not_null` for non-null parameters, and test with UBSan (`-fsanitize=null`).""",
"Relying on a segfault to detect null dereferences in firmware where address 0 is valid flash or RAM; the bug silently reads or corrupts data.",
["How can the optimizer remove a null check? => If the pointer was dereferenced earlier, the compiler may assume it's non-null and drop the later check.",
 "Which tool catches null dereferences reliably? => UBSan with `-fsanitize=null` (part of `-fsanitize=undefined`)."]),

170: D("Shallow pointer equality compares addresses (do both pointers refer to the same object?); deep equality compares the pointed-to objects' values (are the objects equivalent?).",
"""`p == q` is shallow: two distinct objects with equal contents compare unequal. Deep equality is `*p == *q` (after null checks), or a custom comparator for containers of pointers.

Smart pointers follow the same rule: `shared_ptr` and `unique_ptr` compare the stored addresses. So `std::set<std::shared_ptr<T>>` orders by address, not by value; pass a comparator that dereferences if value semantics are wanted.""",
"Using `std::find(v.begin(), v.end(), ptr)` on a vector of pointers to look for an equal value; it compares addresses. Use `find_if` with a dereferencing predicate.",
["How do you find a value in a vector of `unique_ptr`? => `std::find_if(v.begin(), v.end(), [&](auto& p){ return *p == target; })`.",
 "Do `shared_ptr` comparisons compare the objects? => No, they compare the stored pointers."]),
}
