DEEP = {

91: D("Inheritance lets a class (derived) reuse and extend another class (base): it acquires the base's members and can be used where the base is expected (with public inheritance).",
"""Public inheritance models is-a and enables substitutability; the derived object contains a base subobject, so a `Derived*` converts implicitly to `Base*`.

What is not inherited: constructors (unless brought in with `using Base::Base;`), destructors, assignment operators (hidden by the derived ones), and friendships.

Use inheritance for polymorphic interfaces and genuine specialization; use composition for code reuse. Deep hierarchies become fragile; most well-designed C++ codebases keep them to one or two levels.""",
"Using inheritance mainly to reuse helper functions from a base class, coupling unrelated classes to its implementation.",
["Are constructors inherited? => Not by default; C++11 `using Base::Base;` inherits them.",
 "What is converted implicitly with public inheritance? => `Derived*` to `Base*` and `Derived&` to `Base&` (upcasts)."]),

92: D("C++ supports single, multiple, multilevel, hierarchical and hybrid inheritance, each combinable with public, protected or private access and optionally virtual.",
"""- **Single**: one base.
- **Multiple**: several bases (`class D : public A, public B`).
- **Multilevel**: a chain (A <- B <- C).
- **Hierarchical**: many classes derived from one base.
- **Hybrid**: combinations, often producing a diamond, handled with virtual inheritance.

Orthogonal choices: access (public for is-a, private or protected for implemented-in-terms-of) and virtual inheritance for shared bases.""",
"Treating these categories as separate language features; they're just shapes of the same mechanism, and the interview value is in knowing their consequences (ambiguity, diamonds, layout).",
["Which inheritance shapes can create a diamond? => Multiple (hybrid) inheritance where two bases share a common base.",
 "What does private inheritance model? => \"Implemented in terms of\", not is-a."]),

93: D("Polymorphism is the ability of one interface to work with objects of different types, each providing its own behaviour.",
"""C++ offers several kinds:

- **Subtype (runtime) polymorphism**: virtual functions called through base pointers or references.
- **Parametric (compile-time) polymorphism**: templates and concepts.
- **Ad-hoc polymorphism**: function and operator overloading.
- **Coercion**: implicit conversions.

Runtime polymorphism supports open sets of types chosen at runtime; compile-time polymorphism gives zero-overhead code for types known at compile time. `std::variant` + `std::visit` offers a third option for closed sets of types without inheritance.""",
"Assuming polymorphism in C++ always means virtual functions; templates and overloading are equally central, and often cheaper.",
["When would you choose `std::variant` over virtual functions? => For a closed, known set of types where you want value semantics and no heap allocation.",
 "What is ad-hoc polymorphism? => Overloading: the same name selects different implementations based on argument types."]),

94: D("Compile-time polymorphism resolves which code to run during compilation (overloads, templates, CRTP); runtime polymorphism resolves it during execution based on the object's dynamic type (virtual functions).",
"""Trade-offs:

- Compile-time: no dispatch overhead, inlinable, type errors at compile time; but code bloat from instantiations, longer builds, and types must be known when compiling.
- Runtime: types can be chosen at runtime (plugins, configuration), one compiled copy of the code, stable binary interfaces; costs an indirect call, a vptr per object, and usually heap allocation.

Many systems combine them: a runtime interface at module boundaries, templates inside hot loops.""",
"Replacing every virtual interface with templates for speed without measuring: build times and binary size grow, and runtime flexibility is lost.",
["Which is faster? => Usually compile-time, because calls can be inlined; but the difference only matters in hot paths.",
 "How can you get runtime polymorphism without inheritance? => Type erasure (`std::function`, `std::any`, custom erased wrappers) or `std::variant`."]),

95: D("`protected` members are accessible to the class itself, its friends, and derived classes (through objects of the derived type), but not to other code.",
"""A subtle rule: a derived class can access protected members only through objects of its own type (or further derived), not through an arbitrary `Base&`. So `void Derived::f(Base& b) { b.prot_; }` is an error.

Protected member **functions** are useful as customization hooks for derived classes (as in the Template Method / NVI pattern). Protected **data** is usually a mistake, because every derived class can break the base's invariants and the base can never change its representation.""",
"Exposing internal state as protected data \"so subclasses can use it\", making the base impossible to refactor.",
["Can a derived class access a protected member of another `Base` object? => Only through objects of the derived class type, not through a plain `Base` reference.",
 "When are protected functions a good idea? => As hooks that derived classes override or call, with the base controlling the overall algorithm."]),

96: D("The inheritance access specifier caps inherited members' access: public inheritance keeps base access levels; protected inheritance turns public members protected; private inheritance turns public and protected members private.",
"""Summary for a base's public member: public inheritance leaves it public; protected makes it protected; private makes it private in the derived class. Base private members are never accessible to the derived class regardless.

Conversions follow the same rule: only with public inheritance can arbitrary code convert `Derived*` to `Base*`.

A `using Base::member;` declaration in the derived class can restore a specific member's access level.""",
"Assuming private inheritance hides base members from the derived class itself; it hides them from users of the derived class, while the derived class can still use them.",
["Can outside code convert `Derived*` to `Base*` with private inheritance? => No; the base is inaccessible outside the derived class.",
 "How can you re-expose one base function under private inheritance? => `public: using Base::function;` inside the derived class."]),

97: D("Function hiding happens when a derived class declares a member with the same name as a base member: all base overloads of that name become invisible through the derived class, even if their signatures differ.",
"""Name lookup stops at the first scope where the name is found. If `Derived` declares `f(double)`, then `derived.f(1)` finds only `Derived::f(double)` and never considers `Base::f(int)`.

Avoid it by adding `using Base::f;` in the derived class to bring all overloads into scope, and by using `override` for intended overrides so accidental signature mismatches are compile errors. Compilers warn with `-Woverloaded-virtual`.""",
"Overriding only one overload of a virtual function set, unintentionally hiding the others from users of the derived class.",
["Why does hiding happen instead of overloading across scopes? => Lookup stops in the innermost scope containing the name, before overload resolution.",
 "Which warning flag helps? => `-Woverloaded-virtual` in GCC and Clang."]),

98: D("RTTI (Run-Time Type Information) is the runtime type data the compiler stores for polymorphic classes, enabling `dynamic_cast` and `typeid`.",
"""For classes with virtual functions, the vtable points to a `type_info` object describing the dynamic type and its bases. `dynamic_cast` walks this information to check downcasts and cross-casts; `typeid(expr)` returns the `std::type_info` of the dynamic type.

RTTI costs binary size (type names and hierarchy data), and some embedded and game codebases disable it (`-fno-rtti`), which also disables `dynamic_cast` on polymorphic types and `typeid` of polymorphic objects.

Frequent `dynamic_cast` in application code often signals a design issue: prefer virtual functions or visitors.""",
"Relying on `typeid(x).name()` for stable identifiers: its output is implementation-specific (mangled on GCC/Clang), not portable.",
["What stops working with `-fno-rtti`? => `dynamic_cast` on polymorphic types and `typeid` on polymorphic objects; exceptions still work on most toolchains.",
 "How can you compare types without RTTI? => Your own type IDs (enums or static addresses) exposed through a virtual function."]),

99: D("`typeid` returns a `const std::type_info&` describing an expression's type: the dynamic type for a polymorphic object accessed through a reference or dereferenced pointer, otherwise the static type.",
"""Uses: comparing types (`typeid(a) == typeid(b)`), keying maps by type via `std::type_index`, debugging and logging (`name()`).

Details: `typeid(*p)` with a null `p` to a polymorphic type throws `std::bad_typeid`; top-level const and references are ignored (`typeid(const int&) == typeid(int)`); for non-polymorphic types the result is computed at compile time.

`name()` returns an implementation-defined string, often mangled (use `abi::__cxa_demangle` on GCC/Clang for readable names).""",
"Writing `typeid(p)` instead of `typeid(*p)` for a base pointer: it reports the pointer's static type (`Base*`), not the object's dynamic type.",
["How do you use a type as a map key? => `std::unordered_map<std::type_index, Handler>` using `std::type_index(typeid(T))`.",
 "What happens with `typeid(*p)` if `p` is null? => For polymorphic types it throws `std::bad_typeid`."]),

100: D("For downcasting, `static_cast` trusts you and performs no runtime check (wrong type is undefined behaviour), while `dynamic_cast` checks the object's dynamic type at runtime and returns `nullptr` (pointers) or throws `std::bad_cast` (references) on mismatch.",
"""Use `static_cast` only when the type is guaranteed by design (e.g. CRTP, or a tag already checked); it's free at runtime. Use `dynamic_cast` when the type genuinely varies; it costs a hierarchy walk (string comparisons of type names in some implementations across shared libraries).

`dynamic_cast` also supports cross-casts (between sibling bases in multiple inheritance) and casts from virtual bases, which `static_cast` can't do.

If many downcasts appear, consider moving the behaviour into a virtual function or a visitor.""",
"Using `static_cast<Derived*>(base)` on objects that might be a different derived type; it compiles, returns a wrong pointer, and later code corrupts memory.",
["What does `dynamic_cast` require? => A polymorphic source type (at least one virtual function) and RTTI enabled.",
 "Can `dynamic_cast` cast sideways? => Yes, cross-casts between sibling bases of the same object work."]),

101: D("Yes: compile-time techniques (function overloading, templates, CRTP, concepts), `std::variant` with `std::visit`, type erasure and function pointers all provide polymorphic behaviour without virtual functions.",
"""Options:

- **Templates/concepts**: `template<Shape S> double area(const S&)` works for any type meeting the requirements.
- **CRTP**: static dispatch through a base template.
- **`std::variant` + `std::visit`**: closed set of alternatives, value semantics.
- **Type erasure**: `std::function`, `std::any`, or hand-written wrappers that hide the type behind a uniform interface (internally often using function pointers).
- **Function pointer tables**: common in C-style firmware drivers (`struct ops { int (*read)(...); }`), the manual equivalent of a vtable.""",
"Claiming C++ needs `virtual` for polymorphism; interviewers look for knowledge of static and value-based alternatives.",
["What is type erasure? => Hiding concrete types behind a uniform interface without inheritance in the user code, as `std::function` does for callables.",
 "How do C drivers implement polymorphism? => Structs of function pointers (ops tables), the same idea as a vtable."]),

102: D("Multilevel inheritance is a chain of derivation where a class derives from a class that itself derives from another (A -> B -> C).",
"""Each level adds or specializes behaviour; a `C` object contains a `B` subobject which contains an `A` subobject. Constructors run A, B, C; destructors run C, B, A. Virtual functions can be overridden at any level, and the most-derived override wins.

Deep chains are fragile: changes high in the hierarchy ripple down, and understanding behaviour means reading several classes. Mark leaf classes or overrides `final` to stop further derivation where it isn't intended.""",
"Building five-level hierarchies (Device -> StorageDevice -> NvmeDevice -> VendorNvme -> ModelX) where most levels add one method; flatter designs with composition are easier to maintain.",
["Which override is called in a multilevel chain? => The most-derived one for the object's dynamic type.",
 "How do you stop further derivation? => Mark the class `final`."]),

103: D("Hierarchical inheritance is when multiple derived classes inherit from the same single base class.",
"""This is the typical shape of runtime polymorphism: an abstract `Shape` with `Circle`, `Square` and `Triangle` derived from it, or a `BlockDevice` interface with NVMe, SATA and simulated implementations.

Client code depends only on the base interface, and new derived classes can be added without changing it (open/closed principle). The base should have a virtual destructor and a small, stable interface.""",
"Adding type checks (`if (dynamic_cast<Circle*>(s))`) in client code instead of virtual functions, defeating the point of the hierarchy.",
["What does hierarchical inheritance enable? => Treating all derived types uniformly through the base interface.",
 "How do you add an operation to every class in a stable hierarchy without editing them? => The Visitor pattern, or `std::variant` + `std::visit` for closed sets."]),

104: D("Hybrid inheritance combines two or more inheritance types (for example hierarchical plus multiple), which often produces a diamond structure.",
"""Example: `Device` is the base; `NetworkDevice` and `StorageDevice` derive from it; `NasDevice` derives from both. Without virtual inheritance, a `NasDevice` holds two `Device` subobjects and member access is ambiguous.

Resolve with virtual inheritance for the shared base, or redesign: make the shared part an interface without data, or use composition (a NAS **has** a network interface and storage).""",
"Creating diamond hierarchies with data in the shared base and forgetting virtual inheritance, leading to duplicated state that gets out of sync.",
["What problem does hybrid inheritance often create? => The diamond problem: duplicated base subobjects and ambiguous names.",
 "What's an alternative to virtual inheritance for diamonds? => Keep the shared base data-free (a pure interface) or use composition."]),

105: D("C++11 inheriting constructors (`using Base::Base;`) make the base class's constructors available in the derived class, so you don't write forwarding constructors.",
"""Example: `class LoggedFile : public File { public: using File::File; };` lets `LoggedFile(\"a.txt\", Mode::Read)` call the matching `File` constructor. Derived members are then default-initialized (or use their default member initializers).

Inherited constructors keep their access level and `explicit`-ness; default, copy and move constructors are not inherited (the implicit ones are generated as usual).

Useful for thin wrappers and strong types; avoid them when the derived class has invariants that its own constructor must establish.""",
"Inheriting constructors in a derived class that adds members needing specific initialization; those members silently get default values.",
["Are copy and move constructors inherited with `using Base::Base`? => No; the derived class gets its own implicit ones.",
 "What happens to derived-class members? => They're initialized by their default member initializers or default-initialized."]),

106: D("`dynamic_cast` (for downcasts) and `typeid` (for dynamic type) rely on RTTI attached to the vtable, which only exists for polymorphic classes, i.e. classes with at least one virtual function.",
"""For a non-polymorphic class there's no vptr in the object, so at runtime there is no way to find out the dynamic type. Therefore `dynamic_cast<Derived*>(basePtr)` on a non-polymorphic base is a compile error, and `typeid(*p)` returns the static type.

The usual fix is to give the base a virtual destructor, which you need anyway for polymorphic deletion and which makes the class polymorphic.""",
"Expecting `typeid(*basePtr)` to report the derived type when `Base` has no virtual functions; it reports `Base`.",
["What's the minimal change to make a class polymorphic? => Declare a virtual function, typically `virtual ~Base() = default;`.",
 "Does `dynamic_cast` for upcasts need RTTI? => No; upcasts are resolved statically."]),

107: D("`override` asks the compiler to verify that a function overrides a base virtual function; `final` prevents a virtual function from being overridden further or a class from being derived from.",
"""`override` turns silent bugs into compile errors: a mismatched signature (missing `const`, different parameter type, base function renamed) would otherwise create a new function that doesn't override anything.

`final` documents design intent and allows devirtualization: calls through a pointer to a `final` class can be direct calls. `override` and `final` are contextual keywords, so they can still be used as identifiers elsewhere.

Style (Core Guidelines C.128): use exactly one of `virtual`, `override` or `final` on each virtual function declaration.""",
"Adding `const` to a base virtual function during refactoring; derived classes without `override` stop overriding and nobody notices until runtime.",
["Why write `override` if the function already overrides? => It guarantees it keeps overriding when base signatures change.",
 "How can `final` improve performance? => The compiler knows no further override exists, so it can devirtualize and inline calls."]),

108: D("With non-virtual multiple inheritance, a derived object contains each base subobject laid out one after another (typically in declaration order), followed by the derived class's own members; each polymorphic base subobject has its own vptr.",
"""Consequence: converting a `Derived*` to the second base's pointer adjusts the address by an offset, so `static_cast<B2*>(d)` may not equal `(void*)d`. Virtual calls through the second base use **thunks** that adjust `this` before calling the derived override.

This is why comparing pointers across bases must use the correctly typed pointers, and why `reinterpret_cast` between base pointers is wrong. Exact layout is ABI-defined (Itanium ABI on Linux, MSVC ABI on Windows).""",
"Using `reinterpret_cast` (or `void*` round-trips through the wrong type) to convert between base pointers in multiple inheritance, skipping the required offset adjustment.",
["Why can `Derived*` and `Base2*` pointing to the same object have different values? => `Base2` lives at a non-zero offset inside `Derived`.",
 "What is a thunk? => A small adjustor stub that fixes up `this` before jumping to the real override for a secondary base."]),

109: D("A virtual base class is a base declared with `virtual` inheritance so that, in a diamond, all paths share one subobject of it instead of each path having its own copy.",
"""Use it when a class inherits the same base through several paths and should logically contain it once (the `iostream` hierarchy, or interfaces that carry some state).

Consequences: the most-derived class constructs the virtual base; access and casts to it go through an indirection; layout is more complex. Prefer designs where shared bases are pure interfaces without data, which removes the need in many cases.""",
"Adding `virtual` inheritance \"just in case\" everywhere; it complicates construction and adds overhead without benefit when no diamond exists.",
["Who initializes a virtual base? => The most-derived class; intermediate classes' initializers for it are ignored.",
 "When is virtual inheritance unnecessary in a diamond? => When the shared base has no data (a pure interface); duplication then causes only name ambiguity, which qualification can resolve."]),

110: D("The compiler uses the **final overrider**: for each virtual function, the dynamic type's class hierarchy must have one unique most-derived override, reached through the vtable of whichever base subobject the call goes through.",
"""With multiple inheritance, a derived class can override functions from both bases; each base subobject's vtable points to the derived override (via a `this`-adjusting thunk for secondary bases).

If two bases each provide an override of the same virtual function from a shared virtual base, the most-derived class must provide its own override; otherwise the program is ill-formed (no unique final overrider). If two unrelated bases declare functions with the same name, a single derived override overrides both.""",
"Inheriting two different overrides of the same virtual function through virtual inheritance without overriding it in the most-derived class; the compiler reports \"no unique final overrider\".",
["What is the final overrider? => The most-derived override of a virtual function for an object's dynamic type.",
 "Can one function override virtuals from two different bases? => Yes, if both bases declare a virtual with the same signature, one override in the derived class overrides both."]),

111: D("Interface segregation says clients shouldn't depend on methods they don't use; C++ multiple inheritance of small pure-virtual interfaces lets a class implement several focused interfaces instead of one fat one.",
"""Example: instead of one `Device` interface with `read`, `write`, `format`, `updateFirmware`, `getTemperature`, define `IBlockIo`, `IFormattable`, `IFirmwareUpdatable`, `IThermalSensor`. A drive implements all four; a read-only simulator implements only `IBlockIo`; tests depend only on the interfaces they need.

Since pure interfaces carry no data, multiple inheritance of them avoids diamond data problems.""",
"One huge abstract base forcing implementations to stub out irrelevant methods with `throw \"not supported\"`, which also violates Liskov substitution.",
["Why is multiple inheritance of interfaces generally safe? => Interfaces have no data, so there's no duplicated state or ambiguity about members' storage.",
 "How does ISP help testing? => Test doubles implement only the small interface the code under test needs."]),

112: D("Yes: a derived class can override a base class's **private** virtual function; access control affects who can call a function, not who can override it.",
"""This is the basis of the Non-Virtual Interface idiom: the base's public non-virtual function calls a private virtual hook; derived classes override the hook but can't call the base's private version or bypass the public entry point.

Herb Sutter's guideline: make virtual functions private by default, protected only if derived classes need to call the base implementation, and public only for destructors (when polymorphic deletion is needed).""",
"Assuming private virtual functions can't be overridden and making hooks public, which lets callers skip the base's checks and logging.",
["Can the derived class call the base's private virtual implementation? => No; if it needs to, make the hook protected.",
 "Why make virtual functions private? => The base keeps control of when they're called (pre/post-conditions), and derived classes only customize."]),

113: D("If a derived class doesn't override every pure virtual function, it remains abstract: it compiles as a class but can't be instantiated.",
"""The error appears only when you try to create an object (`Derived d;` or `std::make_unique<Derived>()`), often far from the class definition, with a message listing the missing overrides.

This is useful for intermediate abstract classes that implement part of an interface. To catch accidental omissions early, mark intended leaf classes `final` and add a `static_assert(!std::is_abstract_v<Derived>)` near the definition.""",
"A typo in an override's signature without `override`: the pure virtual stays unimplemented and the class is unexpectedly abstract.",
["How do you check at compile time that a class is concrete? => `static_assert(!std::is_abstract_v<T>);`.",
 "Can an abstract derived class add new pure virtual functions? => Yes, further derived classes must implement both old and new ones."]),

114: D("The Non-Virtual Interface (NVI) idiom makes public member functions non-virtual and has them call private (or protected) virtual functions that derived classes override.",
"""Example: `public: void process(Data& d) { validate(d); doProcess(d); log(d); } private: virtual void doProcess(Data&) = 0;`.

Benefits: the base enforces pre- and post-conditions, logging, locking and timing in one place; the public interface and the customization interface can evolve independently; derived classes can't bypass the checks. It's the C++ form of the Template Method pattern, used in the standard library (e.g. `std::streambuf`'s public functions calling protected virtuals).""",
"Making every virtual function public, so each override must remember to repeat validation and locking, and some inevitably forget.",
["Where does the standard library use NVI? => `std::basic_streambuf`: public functions like `sputc` call protected virtuals like `overflow`.",
 "What's the relation to Template Method? => NVI is how Template Method is typically implemented in C++."]),

115: D("A virtual call costs an extra memory load or two (vptr, then vtable slot) and an indirect branch, but the larger cost is that it usually prevents inlining and related optimizations.",
"""Micro-level: indirect calls are well predicted by modern CPUs when the target is stable, so the direct overhead is a few cycles. Macro-level: without inlining, the compiler can't constant-fold, vectorize or eliminate work across the call.

Objects also carry a vptr (8 bytes on 64-bit), which matters for millions of small objects and cache usage.

Guidance: virtual dispatch is fine at component boundaries and for coarse-grained operations; in tight inner loops (per pixel, per byte) prefer templates, `final` classes, or batching (one virtual call per buffer instead of per element).""",
"Micro-optimizing virtual calls in code that isn't hot; profile first, and batch work so each virtual call does more.",
["Why is the lost inlining often more expensive than the call itself? => Inlining enables further optimizations like constant propagation and vectorization across the call boundary.",
 "How can you reduce virtual call overhead in a hot loop? => Batch work per call, use `final`, or switch the hot path to templates."]),

116: D("Containers of base pointers (`std::vector<Base*>` or, better, `std::vector<std::unique_ptr<Base>>`) let one container hold objects of different derived types and call virtual functions on each without slicing.",
"""Ownership is the key design question: raw `Base*` in a container don't own anything, so someone else must delete the objects, and the container can easily hold dangling pointers. Use `std::unique_ptr<Base>` for exclusive ownership (the base needs a virtual destructor) or `std::shared_ptr<Base>` if ownership is genuinely shared.

Performance note: each element is a separate heap allocation, so iteration has poor cache locality. For closed sets of types, `std::vector<std::variant<A, B, C>>` stores objects contiguously.""",
"`std::vector<Base*> v; v.push_back(new Derived);` and later forgetting to delete, or deleting through a base without a virtual destructor.",
["Why not `std::vector<Base>`? => Objects would be sliced to `Base`.",
 "What's a cache-friendlier alternative for a fixed set of types? => `std::vector<std::variant<...>>` or one vector per concrete type."]),

117: D("Covariance lets an override return a more derived type than the base function; contravariance would let an override accept more general parameter types. C++ supports covariant return types (pointers and references only) but not contravariant parameters.",
"""Covariant returns: `Base* Base::clone()` may be overridden as `Derived* Derived::clone()`. Parameters must match exactly: an override declared with a different parameter type is a different function that hides the base one (and `override` would reject it).

Why no contravariance: it would complicate overload resolution and ABI; in practice you accept the base parameter type and use virtual calls or double dispatch inside.""",
"Declaring `void Derived::handle(DerivedEvent&)` expecting it to override `void Base::handle(Event&)`; it doesn't, it hides it.",
["Does covariance work with smart pointers? => No, only with raw pointers and references.",
 "How do you handle type-specific parameters in overrides? => Accept the base type and dispatch further (visitor/double dispatch or `dynamic_cast`)."]),

118: D("With protected inheritance, the base's public and protected members become protected in the derived class, and the is-a relationship is visible only to the derived class and its own descendants.",
"""It expresses \"implemented in terms of, and further derived classes may also rely on that\". Outside code can't convert `Derived*` to `Base*`, but classes derived from `Derived` can.

It's rarely used in practice; most codebases use public inheritance for interfaces and composition otherwise. One niche: mixin or policy bases that the whole hierarchy should reuse internally without exposing them to users.""",
"Choosing protected inheritance to \"hide\" a base while still expecting users to pass the object where the base is expected; that conversion isn't accessible to them.",
["Who can convert `Derived*` to `Base*` under protected inheritance? => Members and friends of `Derived` and of classes derived from it.",
 "Why is protected inheritance rare? => Composition usually expresses implementation reuse more clearly."]),

119: D("Dependency Inversion says high-level modules should depend on abstractions, not on low-level modules; C++ abstract classes provide those abstractions, which both high-level code and low-level implementations depend on.",
"""Example: a test sequencer depends on an abstract `IPowerController`; the real relay driver and a simulated controller both implement it. The sequencer never includes the relay driver's headers, so it can be compiled, tested and reused independently, and implementations can be swapped at runtime (injected via constructor).

The abstraction should be owned by the high-level module (it defines what it needs), not by the low-level library. Templates/concepts offer the same inversion at compile time.""",
"Defining the \"interface\" as a copy of the concrete driver's full API, so high-level code is still coupled to one implementation's details.",
["How do you inject the implementation? => Pass a reference or `std::unique_ptr` to the interface into the constructor (dependency injection).",
 "Can templates achieve dependency inversion? => Yes: `template<PowerController P> class Sequencer` depends on a concept, not a concrete class."]),

120: D("Virtual inheritance adds per-object overhead (extra pointers or offsets for locating the shared base), slower access to the virtual base's members, and more complex construction; the exact cost depends on the ABI.",
"""Memory: each class with a virtual base typically carries a vptr (or virtual base pointer) used to find the base's offset; objects are larger than with plain inheritance.

Time: accessing a member of the virtual base or converting to it needs an extra load to read the offset; `dynamic_cast` and construction are more complex, and the most-derived class must initialize the virtual base.

Because of this, use virtual inheritance only where a real diamond with shared state exists, typically in infrastructure hierarchies like streams.""",
"Paying the virtual-inheritance cost for every object in a performance-critical hierarchy where no diamond actually exists.",
["Why is access to a virtual base's members slower? => Its offset isn't fixed at compile time and must be loaded at runtime.",
 "How do you measure the layout cost? => Compare `sizeof` with and without virtual inheritance, or dump layouts with compiler flags."]),
}
