DEEP = {

396: D("Singleton ensures a class has exactly one instance and provides a global access point; in modern C++ it's implemented with a function-local static (the Meyers singleton), which is lazily and thread-safely initialized.",
"""`static Logger& instance() { static Logger inst; return inst; }` with deleted copy and move operations. Since C++11, initialization of function-local statics is thread-safe.

Drawbacks: hidden global state, order-dependent tests, and hard-to-replace dependencies. Legitimate uses are genuinely unique resources (one hardware controller, process-wide logger); otherwise prefer creating one instance in `main` and passing it by reference (dependency injection).""",
"Implementing Singleton with a raw `new` and manual double-checked locking; the function-local static is simpler and correct.",
["Is the Meyers singleton destroyed? => Yes, at program exit, in reverse order of construction relative to other statics.",
 "How do you test code that uses a singleton? => Access it through an interface injected into the code, so tests can substitute a fake."]),

397: D("The Factory pattern centralizes object creation so client code asks for an object by abstraction (an interface or a key) instead of calling a concrete constructor.",
"""Forms: a simple factory function (`std::unique_ptr<Device> makeDevice(DeviceType t)`), Factory Method (a virtual creation function overridden by subclasses), Abstract Factory (a family of creation methods), and registries mapping names to creator functions (plugins).

Benefits: decouples clients from concrete types, one place to change construction logic, runtime selection from configuration. Return `std::unique_ptr` to make ownership clear.""",
"A giant `switch` on type names inside the factory that every new type must edit; use a registry of creator functions instead.",
["Why should factories return `unique_ptr`? => It makes ownership explicit and converts easily to `shared_ptr` if needed.",
 "How do you add new types without changing the factory? => Self-registering creators in a registry map."]),

398: D("The Observer pattern lets a subject notify a list of observers automatically when its state changes, decoupling the source of events from the code reacting to them.",
"""C++ implementations: a subject with a list of observer interfaces or `std::function` callbacks, signal/slot libraries (Qt, Boost.Signals2), or event buses.

Key C++ issues: observer lifetime (dangling observers if not unsubscribed; use RAII subscription handles or `weak_ptr`), thread safety (copy the observer list under a lock, notify outside it), and reentrancy (an observer unsubscribing during notification).""",
"Storing raw observer pointers and forgetting to unsubscribe in the observer's destructor, leading to calls on destroyed objects.",
["How do you make unsubscription automatic? => Return an RAII connection object that unsubscribes in its destructor.",
 "Why notify outside the lock? => Observers might call back into the subject or take other locks, risking deadlock."]),

399: D("Factory Method defines one virtual creation function that subclasses override to create a single product; Abstract Factory is an object with several creation functions producing a family of related products that must be used together.",
"""Factory Method uses inheritance (the creator subclass decides); Abstract Factory uses composition (you pass a factory object). Example: a test framework's `createDriver()` override vs a `HardwareFactory` producing a matching driver, power controller and thermal sensor for a given lab setup.

Adding a new product type is easy with Factory Method and hard with Abstract Factory (every factory changes); adding a new family is easy with Abstract Factory.""",
"Using Abstract Factory when only one product type varies, adding interfaces and classes with no benefit.",
["Which pattern ensures products are consistent? => Abstract Factory, since one factory creates the whole matching family.",
 "Which one uses inheritance vs composition? => Factory Method uses inheritance; Abstract Factory uses composition."]),

400: D("The Strategy pattern encapsulates interchangeable algorithms behind a common interface so they can be selected at runtime; in C++ it can be a virtual interface, a `std::function`, or a template parameter.",
"""Virtual interface: `class ChecksumStrategy { virtual uint32_t compute(std::span<const std::byte>) = 0; };` with CRC32 and Adler implementations, held via `std::unique_ptr`. Flexible and familiar, one virtual call per use.

`std::function<uint32_t(std::span<const std::byte>)>`: no class hierarchy; any lambda or function works; type-erased call.

Template parameter (policy): `template<class Checksum> class Verifier`: zero overhead and inlinable, but chosen at compile time. Choose based on whether runtime selection is needed and how hot the call is.""",
"Building a class hierarchy for strategies that are simple stateless functions; a lambda or `std::function` is far less code.",
["When is the template-based strategy best? => When the algorithm is known at compile time and called in hot code.",
 "When is `std::function` preferable to a virtual interface? => For simple single-function strategies, especially when lambdas are natural."]),

401: D("The Decorator pattern adds responsibilities to an object at runtime by wrapping it in objects that implement the same interface and delegate to it, instead of creating a subclass for every combination of features.",
"""Example: `TracingDevice(FaultInjectingDevice(RealDevice))`, each wrapper implements `BlockDevice` and adds logging or fault injection. Combinations are built at runtime without subclasses like `TracingFaultInjectingRealDevice`.

Compared to inheritance: behaviour composed dynamically, single-responsibility wrappers, but more small objects and indirections. C++ variants include function decorators (higher-order functions wrapping callables) and stream buffers layered in iostreams.""",
"Forgetting to forward some interface methods in a decorator, so calls to those methods bypass the added behaviour or hit a default implementation.",
["Decorator vs inheritance? => Inheritance fixes features at compile time per subclass; decorators combine features at runtime.",
 "Decorator vs Proxy? => Decorator adds behaviour; Proxy controls access (lazy creation, remote access, permissions)."]),

402: D("The Adapter pattern converts one interface into another that clients expect, letting classes with incompatible interfaces work together without modifying them.",
"""Typical use in C++: wrapping a vendor C API or legacy class behind your own interface. The object adapter holds the adaptee (composition); the class adapter inherits privately from the adaptee and publicly from the target.

Standard library examples: `std::stack`, `std::queue` (container adaptors), `std::reverse_iterator`, `std::back_insert_iterator`. Keep adapters thin (translation only) and return your own types rather than leaking the adaptee's.""",
"Adapters that return the vendor SDK's error codes or structs to callers, so the rest of the code still depends on the vendor.",
["Name container adaptors in the STL. => `std::stack`, `std::queue`, `std::priority_queue`.",
 "Object adapter vs class adapter? => Object adapter composes the adaptee (flexible); class adapter inherits from it (can override its virtuals)."]),

403: D("The pImpl idiom hides a class's private members behind a pointer to an incomplete implementation type (`std::unique_ptr<Impl>`), defined only in the `.cpp` file.",
"""Problems solved: **compilation firewall** (changing private members doesn't force recompiling every user), **ABI stability** (the public class's layout is just one pointer, so shared libraries can change internals without breaking binaries), and hiding implementation headers (vendor SDKs, platform includes) from users.

Costs: a heap allocation per object, an indirection on every access, and boilerplate. The destructor (and move operations) must be declared in the header and defined in the `.cpp` where `Impl` is complete.""",
"Letting the compiler generate the destructor in the header: `std::unique_ptr<Impl>` then needs `Impl`'s complete type there and compilation fails.",
["Why must the pImpl destructor be defined in the `.cpp`? => `unique_ptr<Impl>` needs the complete type to delete it.",
 "How does pImpl help ABI stability? => The public class's size and layout stay constant (one pointer) regardless of implementation changes."]),

404: D("RAII (Resource Acquisition Is Initialization) binds a resource's lifetime to an object's lifetime so the destructor releases it automatically; it's the foundation for C++ resource-management patterns like scope guards, smart pointers and lock guards.",
"""Related patterns: **scope guard** (run a cleanup action on scope exit, optionally dismissed on success), **transaction/rollback** objects, **handle wrappers** for OS resources (file descriptors, device handles), and **ownership types** (`unique_ptr`, containers).

RAII composes: a class whose members are RAII objects gets correct cleanup for free (Rule of Zero). It's exception safe and replaces `try/finally` constructs of other languages.""",
"Holding OS handles as raw integers in classes and closing them in a `close()` method that callers may forget, instead of an RAII wrapper.",
["What is a scope guard? => An RAII object that executes a cleanup lambda in its destructor unless dismissed.",
 "How does RAII relate to the Rule of Zero? => Classes built from RAII members need no custom special member functions."]),

405: D("The Builder pattern constructs a complex object step by step through a separate builder object, usually with a fluent interface, validating and producing the final object in `build()`.",
"""Useful when an object has many optional parameters (avoiding telescoping constructors), when construction needs validation across fields, or when the product should be immutable. Example: `CommandBuilder().opcode(0x02).nsid(1).slba(lba).nlb(7).build()` producing a validated NVMe submission entry.

C++20 designated initializers cover simple cases (`Options{.retries = 3}`); builders remain useful for validation and incremental construction.""",
"A mutable builder shared between callers and reused after `build()`, so one caller's settings leak into another's object.",
["When are designated initializers enough instead of a builder? => For plain aggregates without cross-field validation.",
 "How do you prevent reuse after `build()`? => Make `build()` rvalue-qualified (`build() &&`) so it can only be called on a temporary or moved builder."]),

406: D("CRTP implements static polymorphism by having a base class template take the derived class as a template argument and call derived functions via `static_cast<Derived*>(this)`, resolving calls at compile time without virtual functions.",
"""The base defines the interface and shared logic; the derived class supplies the implementation. Calls are direct and inlinable, and objects need no vptr.

Limitation: different derived types have unrelated base types (`Base<A>` vs `Base<B>`), so there's no common runtime handle; heterogeneous collections still need virtual functions or `std::variant`. C++23 deducing `this` can replace many CRTP uses.""",
"Expecting to store `Base<A>` and `Base<B>` objects in one `std::vector<Base*>`; there's no common base type.",
["What does CRTP save compared to virtual functions? => The vptr per object and the indirect call, enabling inlining.",
 "How does C++23 deducing this simplify CRTP? => A base member function can take `this auto& self` and call derived members without a template parameter for the derived type."]),

407: D("The Visitor pattern separates operations from the object structure they operate on, so new operations can be added without modifying the element classes; in modern C++ it pairs naturally with `std::variant` and `std::visit`.",
"""Classic Visitor uses double dispatch: `element.accept(visitor)` calls `visitor.visit(*this)`, requiring an abstract visitor with one overload per element type. With `std::variant<Circle, Square, Triangle>` and `std::visit(overloaded{...}, shape)`, you get the same separation with value semantics, no virtual functions, and a compile error if an alternative isn't handled.

Trade-off (same for both): easy to add operations, hard to add types.""",
"Choosing classic Visitor for a type set that changes often; every new type requires updating every visitor.",
["Why does `std::visit` catch missing cases? => The visitor callable must accept every alternative, or compilation fails.",
 "What is double dispatch? => Selecting behaviour based on the runtime types of two objects: the element and the visitor."]),

408: D("A function-local static variable (`static T& instance() { static T obj; return obj; }`) gives a thread-safe lazy singleton without explicit locking, because C++11 guarantees that static local initialization happens exactly once even with concurrent callers.",
"""Compilers implement this with a guard variable and efficient synchronization (fast path is just a check of an initialized flag). If the constructor throws, initialization is retried on the next call.

Alternatives: `std::call_once` with `std::once_flag` for lazy initialization of other state, and `constinit` for globals that can be constant-initialized. Beware of destruction order at exit if other statics use the singleton in their destructors.""",
"Writing manual double-checked locking with a non-atomic pointer, which is a data race and can expose a half-constructed object.",
["What happens if the constructor of a function-local static throws? => Initialization isn't complete, so the next call tries again.",
 "Can compilers disable thread-safe statics? => GCC has `-fno-threadsafe-statics`, used in some embedded code; then initialization isn't synchronized."]),

409: D("The Command pattern encapsulates a request as an object so it can be queued, logged, retried or undone; in modern C++, `std::function` or lambdas often replace a hierarchy of command classes.",
"""Classic: `class Command { virtual void execute() = 0; virtual void undo() = 0; };` with a class per command. Simplified: `std::queue<std::function<void()>> tasks; tasks.push([dev, lba]{ dev->trim(lba); });`.

Use classes when commands need more than one operation (undo/redo, serialization, descriptions); use lambdas for simple deferred work, thread pool tasks and callbacks. `std::move_only_function` (C++23) holds move-only captures.""",
"Capturing references in lambdas queued for later execution, which dangle when the command finally runs.",
["When do you still need command classes? => When commands must support undo, serialization or introspection.",
 "What stores move-only lambdas? => `std::move_only_function` (C++23)."]),

410: D("Type erasure hides concrete types behind a uniform interface without requiring them to share a base class: the wrapper stores the object and a set of operations (often a hand-made vtable) that work on it.",
"""`std::function` erases the callable's type, keeping only the call signature; `std::any` erases everything except copying and type identification; `std::shared_ptr<void>` erases the deleter's type. Libraries like Boost.TypeErasure, Dyno and Sean Parent's \"runtime polymorphism\" talk show general techniques.

Benefits: value semantics, non-intrusive (types don't inherit anything), and heterogeneous storage. Costs: indirection and possibly heap allocation (mitigated by small-buffer optimization).""",
"Writing inheritance hierarchies just to store different callable types in a container, when `std::function` or a small type-erased wrapper is enough.",
["How does type erasure differ from inheritance? => Stored types needn't derive from a common base; the wrapper provides the uniform interface.",
 "What is small-buffer optimization in `std::function`? => Small callables are stored inline to avoid heap allocation."]),
}
