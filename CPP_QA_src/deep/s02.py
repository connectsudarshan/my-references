DEEP = {

31: D("The four pillars of OOP are encapsulation (hide state behind an interface), abstraction (expose what, not how), inheritance (derive specialized types) and polymorphism (one interface, many implementations).",
"""In C++ they map to concrete features: encapsulation to access specifiers and invariants maintained by member functions; abstraction to abstract classes and well-chosen interfaces; inheritance to derived classes; polymorphism to virtual functions (runtime) and overloading/templates (compile time).

Modern C++ design leans on composition over inheritance, and on static polymorphism (templates, concepts) where runtime flexibility isn't needed, because virtual dispatch has costs (indirect calls, no inlining, heap-allocated objects).

A strong interview answer ties each pillar to a design benefit: encapsulation protects invariants, abstraction reduces coupling, inheritance enables reuse of interfaces, polymorphism lets code work with types written later.""",
"Reciting the four words without examples. Interviewers expect how C++ implements each and when not to use inheritance.",
["What is static vs dynamic polymorphism in C++? => Static: overloading and templates resolved at compile time. Dynamic: virtual functions resolved at runtime through the vtable.",
 "Which pillar is most often misused? => Inheritance, when used for code reuse instead of modelling an is-a relationship; composition is usually better."]),

32: D("Encapsulation is bundling data with the functions that operate on it and restricting direct access, so the class can guarantee its invariants.",
"""An **invariant** is a condition that must always hold, e.g. a `Buffer`'s size never exceeds its capacity. Making data `private` and changing it only through member functions means every change passes through code that maintains the invariant.

Encapsulation also enables changing the representation later (switch a `std::vector` to a ring buffer) without breaking users.

It's not the same as writing getters and setters for every field: a class whose members all have trivial get/set pairs has no real encapsulation. Expose operations with meaning (`deposit`, `withdraw`), not raw fields.""",
"Adding a public setter for every private member, which lets any caller break the invariants the class exists to protect.",
["What is a class invariant? => A property that holds after construction and after every public member function returns, such as `size() <= capacity()`.",
 "When is a plain struct with public fields fine? => When there is no invariant to protect, e.g. a coordinate or a protocol header record."]),

33: D("Abstraction is exposing only the essential behaviour of a component through an interface while hiding implementation details.",
"""In C++ abstraction appears as abstract base classes (pure virtual functions), well-designed class interfaces, function signatures, and concepts that describe requirements for templates.

Example: a `BlockDevice` interface with `read(lba, buf)` and `write(lba, buf)` hides whether the implementation talks NVMe, SATA, a RAM disk or a simulator. Test code written against the abstraction runs against all of them.

Abstraction and encapsulation are related but distinct: abstraction decides **what** is exposed; encapsulation enforces **how** access is restricted.""",
"Leaky abstractions: an interface exposing implementation details (like NVMe-specific error codes in a generic `BlockDevice`), which couples every user to one implementation.",
["Abstraction vs encapsulation? => Abstraction chooses the interface (what users see); encapsulation hides and protects the implementation behind it.",
 "How do C++20 concepts provide abstraction? => They state the requirements a template argument must meet, like an interface checked at compile time."]),

34: D("A class is a user-defined type describing data and behaviour; an object is an instance of that type occupying storage with a lifetime.",
"""A class definition specifies members (data and functions), access control, and special members (constructors, destructor, copy and move operations). Objects are created with automatic storage (on the stack), static storage, dynamically (`new` / smart pointers), or as members and array elements of other objects.

An object's size is at least the sum of its non-static data members plus padding for alignment, plus a vptr if the class has virtual functions. Member functions don't take space in each object; they're shared code, and static members exist once per class.

Object lifetime begins when construction completes and ends when the destructor starts; accessing an object outside its lifetime is undefined behaviour.""",
"Assuming `sizeof(obj)` equals the sum of member sizes; padding and a vptr often make it larger.",
["Does a member function increase object size? => No; only data members, padding and (for polymorphic classes) the vptr do.",
 "What is the size of an empty class? => At least 1 byte, so distinct objects have distinct addresses."]),

35: D("Access specifiers `public`, `protected` and `private` control which code may name a class member: everyone, the class and its derived classes, or only the class itself (plus friends).",
"""Access is checked at compile time and applies to names, not objects: a member function can access private members of **other objects** of the same class (which is how copy constructors work).

In inheritance, the base-specifier (`public`, `protected`, `private` inheritance) caps the access of inherited members: with private inheritance, base public members become private in the derived class.

Access control is not a security boundary: it's a compile-time design tool. Protected data members are generally discouraged because derived classes then depend on base internals.""",
"Believing `private` means \"private per object\": a member function can read another instance's private members of the same class.",
["Can a member function access private members of another object of the same class? => Yes; access is per class, not per object.",
 "Why are protected data members discouraged? => Every derived class can modify them, so the base can't maintain its invariants."]),

36: D("A friend function is a non-member function (or class) declared with `friend` inside a class, granting it access to the class's private and protected members.",
"""Friendship is granted by the class, not taken; it isn't inherited and isn't transitive.

Legitimate uses: symmetric operators like `operator<<` and `operator==` that need private data but shouldn't be members (so conversions apply to both operands); tightly coupled helper classes (an iterator of a container); and the \"hidden friend\" idiom, where a friend defined inside the class is only found by ADL, reducing overload-set pollution.

Overusing friends breaks encapsulation; prefer adding a proper public member when many outsiders need the same access.""",
"Making a whole test class or unrelated module a friend to get at private data, which couples them tightly to implementation details.",
["Why is `operator<<` usually a friend rather than a member? => Its left operand is `std::ostream`, so it can't be a member of your class; being a friend gives it access to private data.",
 "What is a hidden friend? => A friend function defined inside the class body; it isn't visible to ordinary lookup, only through ADL on arguments of that class."]),

37: D("A static member belongs to the class itself rather than to any object: static data exists once for all instances, and static member functions have no `this` pointer.",
"""Static data members need a definition in exactly one translation unit, unless declared `inline static` (C++17) or `static constexpr`, which can be defined in the class body.

Static member functions can be called without an object (`Registry::instance()`), can access static members, and have ordinary function pointer types (so they work as C callbacks).

Static data members are initialized before `main` (for constant initialization) or dynamically in unspecified order across translation units; wrap them in a function-local static when initialization order matters.""",
"Declaring `static int count;` in a class and forgetting the out-of-class definition, producing an \"undefined reference\" link error (fixed in C++17 with `inline static`).",
["Why can a static member function be used as a C callback? => It has no hidden `this` parameter, so its type is an ordinary function pointer.",
 "How do you define a static data member in a header since C++17? => `inline static int count = 0;` inside the class."]),

38: D("A member function is part of the class and receives an implicit `this`; a friend function is a non-member that has been granted access to the class's private members.",
"""Differences: member functions are called on an object (`obj.f()`), can be virtual, and have the object as an implicit first argument; friends are called like free functions, can't be virtual, and take all operands explicitly.

A key reason to prefer friend (or free) functions for binary operators: implicit conversions apply to **both** operands only for non-members. With `Money operator+(const Money&) const` as a member, `m + 5` may work but `5 + m` won't.

Scott Meyers' guideline: prefer non-member non-friend functions where possible; they increase encapsulation because they can use only the public interface.""",
"Implementing `operator==` or `operator+` as members and discovering that `5 + m` fails to compile while `m + 5` works.",
["Can a friend function be virtual? => No; virtual applies only to non-static member functions.",
 "Why prefer non-member non-friend functions? => They can only use the public interface, so fewer functions depend on private data."]),

39: D("No: a static member function has no `this` pointer, so it can access non-static members only through an explicit object (reference or pointer) passed to it.",
"""Inside a static member function, `x` (a non-static data member) has no object to refer to, so it's a compile error. You can still access private non-static members **of an object you are given**, because access control is per class: `static void reset(Counter& c) { c.value_ = 0; }` is legal.

This is common for factory functions (`static Widget create(...)` constructing and configuring a new object) and C-style callbacks that receive a `void* user_data` which is cast back to the object.""",
"Trying to call a non-static member function from a static callback without an object, instead of passing the object through the callback's user-data pointer.",
["How do you call a member function from a C callback? => Register a static member function and pass `this` as the `void*` user data; cast it back inside the callback.",
 "Can a static member function be const or virtual? => Neither; both qualifiers need a `this` object."]),

40: D("`this` is a prvalue pointer to the object on which a non-static member function was called; its type is `T*` or `const T*` in a const member function.",
"""Uses: disambiguating members from parameters (`this->size = size`), returning `*this` for chaining (`Builder& set(...) { ...; return *this; }`), passing the current object to other functions, and accessing dependent base-class members in templates (`this->member` makes the name dependent so it is found in the base).

C++23 adds **explicit object parameters** (\"deducing this\"): `void f(this Self&& self)` lets one function handle const/non-const and lvalue/rvalue objects, and simplifies CRTP.

`delete this` is legal only if the object was allocated with `new` and is never touched afterward.""",
"Capturing `this` in a lambda stored for later (e.g. an async callback) and calling it after the object was destroyed, producing a dangling pointer.",
["Why do you need `this->` in class templates with dependent bases? => Names from a dependent base aren't looked up by default; `this->` makes the name dependent so it's found at instantiation.",
 "What does C++23 deducing this change? => Member functions can take the object as an explicit, deduced parameter, removing duplicated const/non-const overloads and CRTP boilerplate."]),

41: D("Composition builds a type from member objects (\"has-a\"); inheritance derives a type from a base (\"is-a\"). Prefer composition unless you need substitutability through a common interface.",
"""Inheritance couples the derived class to the base's implementation (the fragile base class problem) and is fixed at compile time. Composition keeps components independent, lets you swap implementations (pass a different strategy object), and hides the component's interface unless you choose to forward it.

Use public inheritance when the derived type genuinely **is** a base type and should be usable wherever the base is expected (Liskov substitution), usually through a small abstract interface.

A good pattern is \"inherit interfaces, compose implementations\": classes implement abstract interfaces and delegate work to member objects.""",
"Inheriting from `std::vector` to get a container with extra methods: `std::vector` has no virtual destructor, and the derived class exposes every vector operation, including ones that break its invariants.",
["Why shouldn't you publicly inherit from STL containers? => They lack virtual destructors and weren't designed as bases; wrap them as members instead.",
 "What is the fragile base class problem? => Changes inside a base class can break derived classes that depend on its implementation details."]),

42: D("An abstract class is a class with at least one pure virtual function (`= 0`); it cannot be instantiated and serves as a base defining an interface.",
"""Derived classes must override all pure virtual functions to become concrete. An abstract class can still have data members, constructors and non-pure member functions providing shared behaviour.

A pure virtual function may even have a definition, which derived classes can call explicitly (`Base::f()`). A pure virtual destructor must have a definition, because derived destructors always call it.

Abstract classes are used through pointers or references (`std::unique_ptr<Shape>`, `const Shape&`); you can't pass or return them by value.""",
"Forgetting to implement one pure virtual function in a derived class: the derived class silently stays abstract and fails only when someone tries to instantiate it.",
["Can an abstract class have a constructor? => Yes; it initializes base state and runs when derived objects are constructed.",
 "Can a pure virtual function have a body? => Yes; derived classes can call it explicitly, and a pure virtual destructor must have one."]),

43: D("C++ has no `interface` keyword; an interface is conventionally a class containing only pure virtual functions and a virtual destructor (often with protected or defaulted special members).",
"""Typical interface: `struct ILogger { virtual ~ILogger() = default; virtual void log(std::string_view) = 0; };`.

Classes implement several interfaces through multiple inheritance, which is safe when the interfaces have no data members (no diamond data duplication).

Alternatives: C++20 **concepts** give compile-time interfaces for templates without virtual dispatch; type erasure (`std::function`, custom type-erased wrappers) gives runtime polymorphism without inheritance.""",
"Omitting the virtual destructor in an interface, so deleting an implementation through an interface pointer is undefined behaviour.",
["Interface via abstract class vs concept? => Abstract classes give runtime polymorphism with virtual calls; concepts constrain templates at compile time with no runtime cost.",
 "Is multiple inheritance of interfaces problematic? => Not usually; pure interfaces have no data, so the diamond data problem doesn't arise."]),

44: D("Overloading is multiple functions with the same name but different parameters in the same scope, resolved at compile time; overriding is a derived class redefining a base class virtual function with the same signature, resolved at runtime.",
"""Mark overrides with `override`: the compiler then errors if the signature doesn't match a base virtual function (e.g. a missing `const`, a different parameter type). Without it, a mismatch silently creates a new function that hides the base one.

A derived class declaring a function with the same name as a base function **hides** all base overloads of that name, even with different parameters; bring them back with `using Base::f;`.

`final` prevents further overriding of a function or derivation from a class, and can let the compiler devirtualize calls.""",
"Changing a base virtual function's signature (adding `const`) while derived classes lack `override`: they stop overriding, and calls quietly go to the base version.",
["What does `override` protect against? => Signature mismatches that would otherwise create a new, non-overriding function.",
 "What is name hiding? => Declaring `f` in a derived class hides every base-class `f` overload; `using Base::f;` brings them back."]),

45: D("No. A constructor can't be virtual because virtual dispatch needs an existing object with an initialized vptr, and the constructor is what creates that object; the caller must know the exact type.",
"""When you write `new Circle(...)`, the type is fixed at the call site, so there's nothing to dispatch on. During construction, the vptr is set to each class's vtable in turn as base and member construction proceeds.

When you need \"virtual construction\" (creating an object whose type is chosen at runtime, or copying through a base pointer), use the **virtual constructor idiom**: a virtual `clone()` for copies and factory functions or registries for creation.""",
"Trying to get polymorphic copying via the copy constructor of a base class, which slices; use a virtual `clone()` returning `std::unique_ptr<Base>`.",
["How do you copy an object through a base pointer? => Add `virtual std::unique_ptr<Base> clone() const = 0;` and implement it in each derived class.",
 "What does the vptr point to during base-class construction? => The base class's vtable; it's updated to the derived vtable when the derived constructor body starts."]),

46: D("Destructors can and often must be virtual: if an object is deleted through a pointer to its base class, the base destructor must be virtual, otherwise behaviour is undefined (typically the derived destructor never runs).",
"""With a virtual destructor, `delete basePtr;` calls the most-derived destructor first, then each base destructor in reverse order of construction. Without it, only the base destructor runs (derived resources leak), and formally the behaviour is undefined.

Rule of thumb (Herb Sutter): a base class destructor should be either **public and virtual** (polymorphic deletion allowed) or **protected and non-virtual** (deletion through the base is prevented at compile time).

`std::shared_ptr<Base>(new Derived)` captures the correct deleter even without a virtual destructor; `std::unique_ptr<Base>` does not.""",
"Deleting derived objects through `std::unique_ptr<Base>` when `Base` has no virtual destructor: the derived part is never destroyed.",
["When should a destructor not be virtual? => In classes not meant to be used polymorphically, or bases with a protected non-virtual destructor, to avoid the vptr overhead.",
 "Why does `shared_ptr<Base>` work without a virtual destructor? => It stores a deleter for the actual type at construction; `unique_ptr<Base>` uses `default_delete<Base>`."]),

47: D("A pure virtual function is a virtual function declared with `= 0`; it has no required implementation in the base, makes the class abstract, and must be overridden by concrete derived classes.",
"""Syntax: `virtual double area() const = 0;`. The vtable slot for it points to a runtime handler (`__cxa_pure_virtual` in GCC/Clang) that aborts if it's ever called, which can only happen during construction or destruction of the base.

Pure virtual functions may still have a definition outside the class, callable explicitly; this is used to provide default behaviour that derived classes must opt into.""",
"Calling a pure virtual function indirectly from a base constructor or destructor, leading to a \"pure virtual function called\" abort at runtime.",
["What happens if a pure virtual function is called during construction? => It resolves to the base (pure) version and the program aborts with \"pure virtual function called\".",
 "Why give a pure virtual function a body? => To offer default behaviour that derived classes must explicitly choose to reuse by calling `Base::f()`."]),

48: D("With `struct` the default inheritance is `public`; with `class` it is `private`. The keyword of the **derived** class decides the default.",
"""`struct D : B {}` is public inheritance; `class D : B {}` is private inheritance. Default member access follows the same rule (public for struct, private for class).

Private inheritance means \"implemented in terms of\": base public members become private in the derived class, and a `D*` can't be implicitly converted to `B*` outside `D`. It's rarely needed; composition usually expresses the same thing more clearly, except when you need to override a base virtual function or use the empty base optimization.

Always write the access specifier explicitly (`class D : public B`) to avoid relying on defaults.""",
"Omitting `public` in `class Derived : Base`, then getting \"Base is an inaccessible base of Derived\" when passing `Derived*` to a function taking `Base*`.",
["When is private inheritance useful? => To override a virtual function of a base you don't want to expose, or to benefit from empty base optimization; otherwise prefer composition.",
 "Which keyword decides the default: the base's or the derived's? => The derived class's keyword."]),

49: D("\"Is-a\" means a type is a specialized kind of another type (modelled with public inheritance); \"has-a\" means a type contains another as a part (modelled with composition, i.e. a data member).",
"""Test for is-a: can the derived object be used anywhere the base is expected without surprising behaviour (Liskov substitution)? A `Car` is a `Vehicle`; a `Car` has an `Engine`.

Wrong is-a relationships cause trouble: a `Square` inheriting from `Rectangle` breaks code that sets width and height independently. When in doubt, choose has-a: it's easier to change later.

Has-a also covers weaker relationships: aggregation (a part that can exist independently, often a pointer or reference) versus composition (the part's lifetime is owned by the whole).""",
"Using inheritance to reuse code (\"Stack is-a vector\") when the relationship is really has-a; the derived class then exposes operations that break its semantics.",
["How do you decide between is-a and has-a? => If substitutability through the base interface makes sense, is-a; otherwise has-a.",
 "Why is Square-inherits-Rectangle a classic LSP violation? => Code that sets width and height independently breaks for a Square, so it isn't substitutable."]),

50: D("Overriding replaces a base class **virtual** function with the same signature, selected at runtime; hiding happens when a derived class declares a name that makes base members with that name invisible, selected at compile time by static type.",
"""Hiding occurs for non-virtual functions with the same name, and for any same-named function with different parameters (even if the base one is virtual). Calls through a base pointer then use the base function; calls through a derived object see only the derived name.

Fixes: `using Base::f;` in the derived class to re-expose base overloads; `override` to confirm an intended override; and avoid redefining non-virtual base functions entirely (Effective C++, Item 36).""",
"Adding `void f(double)` in a derived class and finding that `derived.f(42)` no longer calls the base's `f(int)`, because the base overload is hidden.",
["How do you bring hidden base overloads back? => `using Base::f;` inside the derived class.",
 "Why is redefining a non-virtual base function a bad idea? => Behaviour then depends on the static type of the pointer or reference used, which surprises readers."]),

51: D("Most compilers implement virtual functions with a per-class **vtable** (a table of function pointers) and a hidden per-object **vptr** that points to the vtable of the object's dynamic type.",
"""A virtual call `p->f()` loads the vptr from the object, loads the function pointer from a fixed slot in the vtable, and calls it indirectly. Cost: one or two memory loads plus an indirect call, and more importantly the lost opportunity to inline.

Each polymorphic object grows by one pointer (per base subobject with virtual functions in multiple inheritance). The vtable also usually holds RTTI (type info) and offsets used for multiple and virtual inheritance.

The standard doesn't require vtables; they are the universal implementation strategy (specified by the Itanium C++ ABI on Linux, and by MSVC's ABI on Windows). Compilers can devirtualize calls when the dynamic type is known (e.g. `final` classes or objects of known type).""",
"Assuming virtual calls are always \"slow\": the indirect call is cheap; the real cost is lost inlining in hot loops. Measure before replacing virtual dispatch with templates.",
["Where is the vptr set? => In each constructor (and destructor) of the hierarchy, so it reflects the class currently being constructed or destroyed.",
 "What does `final` enable? => The compiler knows no further override exists, so it can devirtualize and inline calls."]),

52: D("Calling a virtual function from a constructor or destructor dispatches to the version of the class currently being constructed or destroyed, not to the most-derived override.",
"""During `Base`'s constructor, the `Derived` part doesn't exist yet (its members are uninitialized), so the language deliberately treats the object as a `Base`: the vptr points to `Base`'s vtable. The same applies in reverse during destruction, where the derived part has already been destroyed.

If the function is pure virtual in `Base`, the call is undefined behaviour, typically aborting with \"pure virtual function called\".

Fix: move polymorphic initialization into a separate `init()` called after construction, use a factory function that constructs and then initializes, or pass the needed information to the base constructor as parameters.""",
"Expecting a base constructor's call to `virtual void setup()` to run the derived override; it runs the base version, so derived setup silently never happens.",
["Why doesn't C++ dispatch to the derived override during base construction? => The derived members aren't initialized yet, so calling derived code would use uninitialized state.",
 "How do you run derived-specific initialization after construction? => Two-phase construction via a factory function, or pass the data up through base constructor parameters."]),

53: D("Object slicing occurs when a derived object is copied into a base-class object by value: only the base subobject is copied, and the derived data and dynamic type are lost.",
"""Examples: passing a `Derived` to a function taking `Base` by value, assigning `Base b = derived;`, or storing derived objects in `std::vector<Base>`. After slicing, virtual calls on the copy run the base implementation.

A subtler form is **partial assignment**: `Base& r = d1; r = d2;` copies only the base part of `d2` into `d1`, leaving a mixed object.

Slicing is the reason polymorphic types are handled through pointers or references (`std::unique_ptr<Base>`, `const Base&`).""",
"Storing polymorphic objects in `std::vector<Shape>`: every element is sliced to a plain `Shape`, and virtual calls no longer reach the derived overrides.",
["How do you store heterogeneous derived objects in a container? => `std::vector<std::unique_ptr<Base>>`, or `std::vector<std::variant<A, B>>` for a closed set of types.",
 "What is partial assignment? => Assigning through a base reference copies only the base subobject, leaving the target half old, half new."]),

54: D("Prevent slicing by handling polymorphic objects through references or pointers and by making it impossible to copy the base class by value.",
"""Techniques:

- Pass and store by `const Base&`, `Base*` or smart pointers.
- In polymorphic bases, delete or protect copy operations: `Base(const Base&) = delete; Base& operator=(const Base&) = delete;` (C++ Core Guidelines C.67). Then accidental by-value copies are compile errors.
- Provide a virtual `clone()` when copies are genuinely needed.
- Make bases abstract so they can't be instantiated by value at all.
- For closed sets of types, use `std::variant` instead of inheritance: values then carry their full type.""",
"Leaving the implicitly generated copy constructor public in a polymorphic base, so slicing compiles silently wherever someone passes by value.",
["What does C++ Core Guideline C.67 recommend? => A polymorphic class should suppress public copy/move to prevent slicing.",
 "How does `std::variant` avoid slicing? => The variant stores the complete object of whichever alternative it holds, by value."]),

55: D("The diamond problem arises when a class inherits from two classes that share a common base: without special handling the final object contains two copies of that base, making member access ambiguous. C++ solves it with **virtual inheritance**.",
"""With `class A {}; class B : public A {}; class C : public A {}; class D : public B, public C {};`, a `D` holds two `A` subobjects, so `d.x` (a member of `A`) is ambiguous, and converting `D*` to `A*` is ambiguous.

Declaring `class B : virtual public A` and `class C : virtual public A` makes `D` contain a single shared `A` subobject. The **most-derived class** (`D`) is then responsible for constructing `A`; `B`'s and `C`'s initializations of `A` are ignored.

Virtual inheritance has costs (extra pointers or offsets, slower access to base members), so it's used mostly for interface-like bases (e.g. `std::iostream` from `std::istream` and `std::ostream`).""",
"Expecting `B`'s constructor call `A(1)` to initialize the shared virtual base when constructing a `D`; the most-derived class's initializer (or `A`'s default constructor) is used instead.",
["Who constructs a virtual base class? => The most-derived class, before any non-virtual bases.",
 "Where does the standard library use virtual inheritance? => `std::basic_iostream` derives from `basic_istream` and `basic_ostream`, which virtually inherit `basic_ios`."]),

56: D("With normal inheritance a base subobject sits at a fixed offset inside each derived object; with virtual inheritance the shared base's position varies with the most-derived type, so it is reached through extra indirection (a virtual base offset stored via the vtable or a virtual base pointer).",
"""Consequences of virtual inheritance: objects grow (additional pointers), casting from derived to virtual base needs a runtime offset lookup, `static_cast` from a virtual base down to a derived class is not allowed (use `dynamic_cast`), and construction order changes (virtual bases first, by the most-derived class).

Exact layout is ABI-specific (Itanium C++ ABI stores virtual base offsets in the vtable; MSVC uses a separate virtual base table pointer). You can inspect it with `clang -Xclang -fdump-record-layouts` or MSVC's `/d1reportSingleClassLayout`.""",
"Using `static_cast` to downcast from a virtual base class: it's ill-formed; only `dynamic_cast` can navigate from a virtual base.",
["Why can't `static_cast` downcast from a virtual base? => The offset of the virtual base inside the derived object isn't known at compile time.",
 "How can you view a class's memory layout? => Clang's `-fdump-record-layouts`, MSVC's `/d1reportSingleClassLayout`, or `offsetof`/`sizeof` experiments."]),

57: D("Yes. A private (or protected) destructor prevents objects from being created on the stack or deleted by outsiders, forcing a controlled lifetime such as heap-only objects destroyed through a member function or a friend.",
"""Use cases:

- **Heap-only objects** with reference counting or self-management: clients call `release()`, which does `delete this` when the count hits zero (COM-style interfaces).
- **Singletons or registries** that must control destruction.
- Preventing deletion through a base pointer: a **protected** non-virtual destructor in a base class makes `delete basePtr` a compile error while allowing derived classes to destroy normally.

With a private destructor, automatic (stack) objects and `std::unique_ptr` with the default deleter won't compile; provide a custom deleter or a friend that destroys.""",
"Making the destructor private and then wondering why `std::make_unique<T>()` fails: the default deleter can't call it; supply a custom deleter or friend.",
["How do you force heap-only allocation? => Private or protected destructor plus a static factory and a `destroy()`/`release()` member.",
 "Why use a protected non-virtual base destructor? => It prevents polymorphic deletion through the base at compile time without the cost of a vtable."]),

58: D("A covariant return type allows an overriding virtual function to return a pointer or reference to a class derived from the base function's return type.",
"""Example: `Base* Base::clone() const` can be overridden as `Derived* Derived::clone() const`. Callers using the derived type get the precise type without casting; callers through the base still receive a `Base*`.

Covariance only works with raw pointers and references, not with smart pointers: `std::unique_ptr<Derived>` is unrelated to `std::unique_ptr<Base>` as a return type for overriding. The usual workaround is a non-virtual public function returning `unique_ptr<Derived>` that calls a private virtual `clone_impl()` returning `Base*`.""",
"Trying to override `std::unique_ptr<Base> clone()` with `std::unique_ptr<Derived> clone()`: it's a compile error, not covariance.",
["Why doesn't covariance work with `unique_ptr`? => The two `unique_ptr` specializations are unrelated types; covariance is defined only for pointers and references to classes.",
 "What's the workaround for covariant smart-pointer clones? => A public non-virtual wrapper returning `unique_ptr<Derived>` around a private virtual function returning a raw pointer."]),

59: D("CRTP is a pattern where a class template takes the deriving class as a template argument (`class Derived : Base<Derived>`), letting the base call derived functions at compile time: static polymorphism without virtual calls.",
"""The base does `static_cast<Derived*>(this)->impl()`; the call is resolved at compile time and can be inlined, with no vptr or vtable.

Uses: mixins that add functionality (comparison operators from one `compare`, `enable_shared_from_this`, counters of live instances), compile-time interfaces with zero overhead, and expression templates.

Limits: each `Base<Derived>` is a different type, so you can't store heterogeneous objects in one container through the base; C++20 concepts and C++23 deducing `this` replace many CRTP uses more simply.""",
"Writing `class B : public Base<A>` by copy-paste mistake: the base then casts `this` to the wrong type, which is undefined behaviour. Guard with a private base constructor and `friend Derived;`.",
["CRTP vs virtual functions? => CRTP dispatches at compile time (inlinable, no vptr) but can't provide runtime polymorphism across a heterogeneous collection.",
 "Which standard library class uses CRTP? => `std::enable_shared_from_this<T>`."]),

60: D("Early (static) binding resolves a function call at compile time from the static type; late (dynamic) binding resolves it at runtime from the object's dynamic type through virtual dispatch.",
"""Early binding applies to non-virtual functions, overloads, templates and calls on objects (not pointers or references) of known type; it allows inlining. Late binding applies to virtual functions called through a pointer or reference.

A virtual function called with explicit qualification (`obj.Base::f()`) or on an object by value is also bound early.

Compilers turn late binding into early binding when they can prove the dynamic type (devirtualization), e.g. with `final` classes, local objects of known type, or link-time optimization.""",
"Expecting virtual behaviour from calls on objects passed by value; the copy has the static type, so the call is bound early to that type's function.",
["Is a virtual call through an object (not a pointer) late-bound? => No; the object's type is known, so it's bound at compile time.",
 "What is devirtualization? => The compiler proves the dynamic type and replaces the indirect virtual call with a direct (often inlined) call."]),

61: D("A static member function has no object and therefore no vptr to dispatch through, so it can't be virtual; virtual dispatch depends on the dynamic type of an object.",
"""Virtual means \"choose the implementation based on the object's dynamic type\". A static function is called on the class (`Widget::create()`), not on an object, so there is nothing whose dynamic type could choose.

If you need per-type behaviour without an object, options are: a virtual non-static function that returns per-type information (e.g. `virtual std::string_view typeName() const`), a registry mapping type IDs to factory functions, or templates/CRTP for compile-time per-type behaviour.""",
"Trying to override a static function in a derived class expecting polymorphism: it only hides the base static function.",
["How can you get \"virtual static\" behaviour? => A virtual instance function returning per-class data, or a registry keyed by type.",
 "What happens if a derived class declares a static function with the same name? => It hides the base function; calls resolve by static type."]),

62: D("When two base classes both provide a member with the same name, using it through the derived class is ambiguous; without virtual inheritance you resolve it by qualifying the name or by declaring a disambiguating member in the derived class.",
"""Options:

- Qualify the call: `d.Printer::start()` or `d.Scanner::start()`.
- Add `using Printer::start;` in the derived class to choose one.
- Override the function in the derived class and call one or both bases explicitly, which is often the clearest.

Ambiguity is detected at the point of use, not at class definition, so a class can compile fine until someone calls the ambiguous member.""",
"Assuming the compiler will pick the \"first\" base in the base list; it never does, the call is simply ambiguous.",
["When is the ambiguity reported? => At the point where the ambiguous name is used, not when the class is defined.",
 "Can a `using` declaration resolve the ambiguity? => Yes: `using Base1::f;` in the derived class selects that version."]),

63: D("The empty base optimization (EBO) lets an empty base class subobject occupy zero bytes inside the derived object, even though a standalone empty object has size at least 1.",
"""Empty classes (no non-static data members, no virtual functions) are common as policies, allocators, comparators and tag types. Storing them as data members would cost at least one byte plus padding; inheriting from them usually costs nothing.

This is why `std::unique_ptr<T, Deleter>` with a stateless deleter is the same size as a raw pointer, and why STL containers store allocators via EBO.

C++20 adds `[[no_unique_address]]`, which applies the same optimization to data members without inheritance: `[[no_unique_address]] Deleter d_;`.""",
"Storing stateless comparators or allocators as plain members in space-critical types, adding bytes (and padding) to every object.",
["Why is `sizeof(std::unique_ptr<T>)` equal to `sizeof(T*)`? => The default deleter is empty and stored via EBO (or `[[no_unique_address]]`).",
 "What does `[[no_unique_address]]` do? => Allows an empty data member to share storage with other members, giving EBO without inheritance."]),

64: D("Inheritance is an is-a relationship between types; composition is a has-a relationship where the whole owns the part's lifetime; aggregation is a has-a relationship where the part exists independently and is only referenced.",
"""In C++ terms: composition is usually a data member or a `std::unique_ptr` member (destroyed with the owner); aggregation is a reference, raw non-owning pointer, `std::weak_ptr` or a shared pointer to something whose lifetime is managed elsewhere; inheritance is a base class.

Example: a `Car` composes its `Engine` (destroyed with the car) but aggregates a `Driver` (who exists before and after the car). In UML, composition is a filled diamond and aggregation a hollow one.

Getting ownership right avoids leaks and dangling pointers: owners hold `unique_ptr`, observers hold references or raw pointers with documented lifetimes.""",
"Modelling aggregation with `std::shared_ptr` everywhere \"to be safe\", which blurs ownership and can create reference cycles that leak.",
["How do you express a non-owning reference to an aggregated part? => A reference, a raw pointer documented as non-owning, or `std::weak_ptr` when the part is shared-owned.",
 "What's the ownership difference between composition and aggregation? => Composition owns the part's lifetime; aggregation only refers to a part owned elsewhere."]),

65: D("The Liskov Substitution Principle states that objects of a derived class must be usable wherever the base class is expected without breaking the program's correctness.",
"""Formally: derived classes may not **strengthen preconditions**, **weaken postconditions**, or violate the base's invariants; they must also not throw new kinds of exceptions callers don't expect.

Classic violations: `Square` derived from `Rectangle` (setting width changes height), a `ReadOnlyFile` derived from `File` whose `write()` throws, or an override that ignores part of the base contract.

In C++ design this means: keep base interfaces small and precise, document contracts, prefer composition when behaviour differs, and write tests against the base interface that every implementation must pass (contract tests).""",
"Overriding a method to throw `std::logic_error(\"not supported\")` in a derived class: callers written against the base contract break.",
["What is a precondition strengthening example? => A base `setSpeed(int)` accepting any value, overridden to reject values above 100 in a derived class.",
 "How do you enforce LSP in practice? => Contract tests: one test suite written against the base interface that every derived implementation must pass."]),
}
