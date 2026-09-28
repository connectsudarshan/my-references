EXTRAS = [

X(0, "How does inheritance work", terms=[
    ("Base class / subclass", "The parent class, and the child class that inherits from it."),
    ("`__bases__`", "Tuple of a class's direct base classes."),
], pitfall="""Forgetting to call `super().__init__()` in an overriding `__init__`. The parent's attributes are never set, and the error shows up later as an `AttributeError`.""",
follow=[
    ("Does a subclass inherit class attributes?", "Yes, they are found through the MRO unless the subclass overrides them."),
    ("How do you list a class's subclasses?", "`Parent.__subclasses__()` returns direct subclasses that are still alive."),
]),

X(1, "What does `super()` actually do", terms=[
    ("Proxy object", "`super()` returns an object that forwards attribute lookups to the classes after the current one in the MRO."),
    ("Zero-argument `super()`", "Uses the compiler-provided `__class__` cell and the first argument of the method."),
], pitfall="""Using zero-argument `super()` in a function defined outside the class and attached later. There is no `__class__` cell, so it raises `RuntimeError: super(): __class__ cell not found`.""",
follow=[
    ("What is the two-argument form?", "`super(Class, obj)` starts the search after `Class` in `type(obj).__mro__`; needed only outside class bodies."),
    ("Does `super()` work for attributes, not just methods?", "Yes, for class-level attributes and descriptors, but not for instance attributes stored in `__dict__`."),
]),

X(2, "What is the MRO", terms=[
    ("C3 linearization", "The algorithm that merges parent MROs while keeping local precedence order and monotonicity."),
    ("`__mro__`", "The tuple of classes in lookup order; `Class.mro()` returns it as a list."),
], pitfall="""Assuming `super()` means \"my parent class\". In multiple inheritance it may call a sibling class that your class knows nothing about.""",
follow=[
    ("What is monotonicity in C3?", "If C1 precedes C2 in a class's MRO, it also precedes it in the MRO of every subclass."),
    ("Can you customize the MRO?", "Yes, a metaclass can override `mro()`, but this is almost never a good idea."),
]),

X(3, "What is the diamond problem", terms=[
    ("Diamond inheritance", "Two classes share a common base and a fourth class inherits from both."),
], pitfall="""Calling `Parent.__init__(self)` explicitly in a diamond. The shared base's `__init__` then runs twice; use `super()` everywhere.""",
follow=[
    ("What is D's MRO for `class D(B, C)` with B and C inheriting A?", "`D, B, C, A, object`."),
    ("Why is every class hierarchy a diamond in Python 3?", "All classes share `object` as a base, so multiple inheritance always forms a diamond at the top."),
]),

X(4, "When does Python refuse to create a class", terms=[
    ("Inconsistent MRO", "When bases require contradictory orderings, such as `class C(A, B)` where `B` is a subclass of `A`."),
], pitfall="""Listing a base before its own subclass (`class X(Base, Derived)`). Put more specific classes first: `class X(Derived, Base)`, or just `class X(Derived)`.""",
follow=[
    ("What is the exact error message?", "`TypeError: Cannot create a consistent method resolution order (MRO) for bases ...`."),
    ("Why is this a creation-time error rather than a lookup-time one?", "The MRO is computed once when the class is created and stored in `__mro__`."),
]),

X(5, "What is method overriding", terms=[
    ("Override", "A subclass redefines an inherited method with the same name."),
    ("`@typing.override`", "(3.12+) marks a method as intended to override one, so type checkers flag typos."),
], pitfall="""Overriding with an incompatible signature (fewer parameters). Code that works with the base class then breaks with the subclass, violating the Liskov substitution principle.""",
follow=[
    ("What is the Liskov substitution principle?", "A subclass instance must be usable anywhere the base is expected without breaking correctness."),
    ("How do you extend rather than replace a method?", "Call `super().method(...)` inside the override and add behavior before or after."),
]),

X(6, "Does Python support method overloading", terms=[
    ("`singledispatch`", "Chooses an implementation based on the type of the first argument."),
    ("`@typing.overload`", "Declares multiple signatures for type checkers only; there is still one runtime implementation."),
], pitfall="""Defining two methods with the same name and expecting both to exist. The later `def` silently replaces the earlier one; linters flag this as a redefinition.""",
follow=[
    ("How do you dispatch on methods?", "`functools.singledispatchmethod`, which dispatches on the first argument after `self`."),
    ("Does `singledispatch` use type hints?", "Yes, `@f.register` can read the annotation of the first parameter instead of taking the type explicitly."),
]),

X(7, "What is polymorphism in Python", terms=[
    ("Ad-hoc polymorphism", "Different implementations selected by type (operator overloading, `singledispatch`)."),
    ("Subtype polymorphism", "Code written against a base type works with any subclass."),
], pitfall="""Using `isinstance` chains (`if isinstance(s, Circle): ... elif isinstance(s, Square): ...`) instead of a method on each class. New types then require editing every chain.""",
follow=[
    ("How does `len()` achieve polymorphism?", "It calls `type(obj).__len__`, which each type implements."),
    ("Is polymorphism in Python tied to inheritance?", "No; duck typing gives polymorphism without any shared base class."),
]),

X(8, "What is a mixin", terms=[
    ("Mixin", "A class that adds one feature and is not meant to be instantiated on its own."),
], pitfall="""A mixin with its own `__init__` that does not call `super().__init__(**kwargs)`. It breaks the initialization chain for the classes after it in the MRO.""",
follow=[
    ("Why are mixins listed first in the bases?", "So their methods take precedence over the main base class's methods in the MRO."),
    ("What are common stdlib mixin examples?", "`socketserver.ThreadingMixIn` and `ForkingMixIn`."),
]),

X(9, "How do `isinstance` and `issubclass` work with ABCs", terms=[
    ("`__subclasshook__`", "A classmethod on an ABC that can accept a class structurally, for example any class with `__len__` for `Sized`."),
], pitfall="""Registering a class with an ABC via `register()` and assuming it now inherits the ABC's mixin methods. Registration only affects `isinstance`; no methods are added and abstract methods are not checked.""",
follow=[
    ("Why is `isinstance([], collections.abc.Sequence)` True even though list does not inherit it?", "`list` is registered as a virtual subclass of `Sequence`."),
    ("Is `isinstance` with an ABC slower?", "The first check is slower; results are cached per class afterwards."),
]),

X(10, "How should `__init__` be written in cooperative", terms=[
    ("Cooperative multiple inheritance", "Every class in the hierarchy calls `super()` so each `__init__` runs exactly once."),
], pitfall="""Passing leftover keyword arguments into `object.__init__`, which raises `TypeError: object.__init__() takes exactly one argument`. Each class must consume its own arguments.""",
follow=[
    ("Why use keyword-only arguments here?", "Positional arguments cannot be split reliably among classes whose order depends on the MRO."),
    ("What if a third-party base class does not call `super()`?", "Wrap it with an adapter class that does, or use composition."),
]),

X(11, "What is the difference between inheriting from `list`", terms=[
    ("`UserList` / `UserDict`", "Pure-Python wrappers that store data in `self.data` and route all operations through overridable methods."),
    ("`MutableSequence`", "ABC that derives many methods from a few abstract ones you implement."),
], pitfall="""Subclassing `dict`, overriding `__setitem__` to validate, and then calling `update()` or the constructor. Those do not go through your `__setitem__`, so invalid data slips in.""",
follow=[
    ("Which abstract methods does `MutableMapping` need?", "`__getitem__`, `__setitem__`, `__delitem__`, `__iter__` and `__len__`."),
    ("When is subclassing `dict` directly fine?", "When you only add new methods or `__missing__`, not change existing behavior."),
]),

X(12, "Can you call a parent method that the child has overridden", terms=[
    ("Explicit base call", "`Parent.method(self)`, a direct call that bypasses the MRO."),
], pitfall="""Calling `super().method()` in a class whose parent does not define `method`. It raises `AttributeError: 'super' object has no attribute ...`.""",
follow=[
    ("How do you call a grandparent's method, skipping the parent?", "`super(Parent, self).method()`, though needing this is usually a design smell."),
    ("Can you call an overridden method from outside the class?", "Yes, `Parent.method(obj)`."),
]),

X(13, "What is `typing.Protocol`", terms=[
    ("Structural subtyping", "Compatibility decided by an object's shape (its methods and attributes), not by declared inheritance."),
    ("`@runtime_checkable`", "Allows `isinstance` checks against a protocol (method presence only)."),
], pitfall="""Relying on `isinstance(x, SomeProtocol)` to validate signatures. The runtime check only confirms the attributes exist, not their parameters or types.""",
follow=[
    ("Can a class explicitly inherit a Protocol?", "Yes; then it also gets any default method implementations the protocol defines."),
    ("When do you prefer a Protocol over an ABC?", "When you do not control the implementing classes, for example third-party types that already have the methods."),
]),

X(14, "What is `object` and what does every class", terms=[
    ("`object.__init_subclass__`", "The default no-op subclass hook every class inherits."),
], pitfall="""Calling `object()` expecting a useful object; instances of plain `object` cannot even take attributes (no `__dict__`). They are only useful as unique sentinels.""",
follow=[
    ("Why can't you set attributes on `object()`?", "`object` instances have no `__dict__`; subclasses get one automatically unless they use `__slots__`."),
    ("What does default `__eq__` compare?", "Identity; it returns `NotImplemented` for different objects, and Python then falls back to an identity comparison."),
]),

X(15, "Why is deep inheritance often discouraged", terms=[
    ("Yo-yo problem", "Having to jump up and down a deep hierarchy to understand which method actually runs."),
], pitfall="""Creating base classes to share a couple of helper methods. A module-level function or a small collaborator object is simpler and keeps classes decoupled.""",
follow=[
    ("How deep is too deep?", "No fixed number, but more than two or three levels of your own classes is a warning sign."),
    ("What patterns replace inheritance?", "Composition, strategy objects, protocols, and plain functions passed as parameters."),
]),

X(16, "How do you prevent a class from being subclassed", terms=[
    ("`@typing.final`", "Marks a class or method as not to be subclassed or overridden; checked by type checkers only."),
], pitfall="""Expecting `@final` to raise at runtime. It does nothing when the program runs; use `__init_subclass__` raising `TypeError` if runtime enforcement is required.""",
follow=[
    ("How does `__init_subclass__` enforce it?", "`def __init_subclass__(cls, **kw): raise TypeError(\"cannot subclass\")` on the base class."),
    ("Which built-in types cannot be subclassed?", "`bool`, `NoneType`, `range`, `slice`, `memoryview` and function types, among others."),
]),

X(17, "What does `super()` do in a classmethod", terms=[
    ("`__new__` as a static method", "`__new__` is implicitly static, so `super().__new__(cls)` must pass `cls` explicitly."),
], pitfall="""Calling `super().__new__(cls, *args)` when the next class is `object`. Once `__new__` is overridden, `object.__new__` rejects extra arguments with `TypeError`; pass only `cls`.""",
follow=[
    ("What does `super()` bind to inside a classmethod?", "The class (`cls`) instead of an instance, so the next classmethod receives the same `cls`."),
    ("Can you use `super()` inside a staticmethod?", "Not zero-argument; there is no first argument to bind. Use `super(Class, Class)` explicitly, if at all."),
]),

X(18, "What are dunder (magic) methods", terms=[
    ("Special method", "The official name for dunder methods; the interpreter looks them up on the type."),
], pitfall="""Calling dunders directly (`x.__len__()`) instead of the built-in (`len(x)`). The built-ins add checks and fallbacks, such as `len()` requiring a non-negative int.""",
follow=[
    ("Should you invent your own dunder names?", "No; the `__name__` space is reserved for Python and may gain meaning in future versions."),
    ("Where are all special methods documented?", "In the \"Data model\" chapter of the language reference."),
]),

X(19, "What are reflected operators", terms=[
    ("Reflected (swapped) operand", "`b.__radd__(a)` is tried for `a + b` when `a` cannot handle it."),
], pitfall="""Forgetting `__radd__`, so `sum(my_objects)` fails: `sum` starts from `0` and evaluates `0 + obj`, which needs `obj.__radd__`.""",
follow=[
    ("When does Python try the reflected method first?", "When the right operand's type is a subclass of the left operand's type and overrides the reflected method."),
    ("Is there a reflected version of `+=`?", "No; `+=` tries `__iadd__`, then `__add__`, then the right operand's `__radd__`."),
]),

X(20, "Why return `NotImplemented`", terms=[
    ("`NotImplemented`", "A singleton signaling \"this operand type is not supported here\"; it is not an exception."),
], pitfall="""Returning `NotImplemented` from a normal method, or using it in a boolean context. Using it as a boolean was deprecated in 3.9 and raises `TypeError` since 3.14.""",
follow=[
    ("What happens if both sides return `NotImplemented` for `==`?", "Python falls back to identity comparison, so `==` returns False instead of raising."),
    ("And for `<`?", "It raises `TypeError: '<' not supported between instances of ...`."),
]),

X(21, "How do you make objects comparable", terms=[
    ("Rich comparison", "Separate methods for each operator: `__lt__`, `__le__`, `__eq__`, `__ne__`, `__gt__`, `__ge__`."),
], pitfall="""`@dataclass(order=True)` compares fields in declaration order, including fields you did not intend to sort by. Exclude them with `field(compare=False)` or write a custom key.""",
follow=[
    ("What is the cost of `total_ordering`?", "The derived methods are slower than hand-written ones because they call your base method and invert or combine results."),
    ("How does sorting use comparisons?", "`sort` and `sorted` only use `<` (`__lt__`)."),
]),

X(22, "What does `__call__` do", terms=[
    ("Callable", "Any object that can be called with `()`; test with `callable(obj)`."),
], pitfall="""Using a class with `__call__` where a closure or `functools.partial` would do. Reserve callable objects for cases that need state inspection or several methods.""",
follow=[
    ("Are classes callable?", "Yes, calling a class runs its metaclass's `__call__`, which invokes `__new__` then `__init__`."),
    ("How do you write a class-based decorator?", "Store the function in `__init__` and call it in `__call__`; add `__get__` if it must work on methods."),
]),

X(23, "How do `__getitem__`, `__setitem__`", terms=[
    ("`slice` object", "Passed to `__getitem__` for `obj[a:b:c]`, with `.start`, `.stop`, `.step` and `.indices(len)`."),
], pitfall="""Implementing `__getitem__` without handling slices or negative indexes. `obj[-1]` and `obj[1:3]` then fail or return nonsense; use `slice.indices(len(self))` to normalize.""",
follow=[
    ("How does `in` work without `__contains__`?", "Python falls back to iterating via `__iter__` (or `__getitem__`) and comparing each item."),
    ("What does `obj[1, 2]` pass to `__getitem__`?", "A tuple `(1, 2)`; this is how NumPy supports multidimensional indexing."),
]),

X(24, "What is `__bool__`", terms=[
    ("Truthiness fallback", "`__bool__`, then `__len__`, then always true."),
], pitfall="""A container class with a `__len__` that is expensive (for example a database count). Every `if obj:` then runs the query; define a cheap `__bool__`.""",
follow=[
    ("What must `__bool__` return?", "Exactly `True` or `False`; returning an int raises `TypeError`."),
    ("Why is `if x == True:` discouraged?", "It fails for truthy non-bool values; write `if x:`."),
]),

X(25, "What do `__enter__` and `__exit__` do", terms=[
    ("Suppressing exceptions", "`__exit__` returning a truthy value tells Python to swallow the exception."),
], pitfall="""Returning `True` from `__exit__` accidentally (for example returning a result object). It silently suppresses every exception raised in the block.""",
follow=[
    ("Does `__exit__` run if `__enter__` raises?", "No; only when `__enter__` succeeded."),
    ("What are the async versions?", "`__aenter__` and `__aexit__`, used by `async with`."),
]),

X(26, "What is `__hash__` and what is the rule", terms=[
    ("`__hash__ = None`", "Marks a class as unhashable; set implicitly when you define `__eq__` without `__hash__`."),
], pitfall="""Implementing `__hash__` from mutable fields to make a class \"work\" in sets. It works until a field changes, and then lookups silently fail.""",
follow=[
    ("How do you inherit the parent's hash after defining `__eq__`?", "Set `__hash__ = Parent.__hash__` in the class body."),
    ("Must unequal objects have different hashes?", "No; collisions are allowed and only affect performance."),
]),

X(27, "What is `__getattribute__` vs `__getattr__`", terms=[
    ("`object.__getattribute__`", "The default lookup: data descriptors on the type, then the instance `__dict__`, then non-data descriptors and class attributes."),
], pitfall="""Writing `self.x = v` inside `__setattr__`. It calls `__setattr__` again forever; use `super().__setattr__(\"x\", v)` or `object.__setattr__`.""",
follow=[
    ("Why is overriding `__getattribute__` risky?", "Every access, including `self.__dict__`, goes through it, so mistakes cause recursion and it slows all attribute access."),
    ("What are good uses of `__getattr__`?", "Proxies and delegation, lazy attributes, and deprecation shims for renamed attributes."),
]),

X(28, "What is `__len__` vs `__length_hint__`", terms=[
    ("`operator.length_hint`", "Returns `len(obj)` if available, otherwise `__length_hint__`, otherwise a default."),
], pitfall="""Returning a huge or negative value from `__len__`. `len()` raises `OverflowError` above `sys.maxsize` and `ValueError` for negative values.""",
follow=[
    ("Who uses length hints?", "`list()` and similar constructors use them to pre-size storage when consuming iterators."),
    ("Must the hint be exact?", "No, it is only an optimization hint."),
]),

X(29, "What is `__format__`", terms=[
    ("Format spec mini-language", "The text after `:` in a replacement field, interpreted by the object's `__format__`."),
], pitfall="""Defining `__format__` but ignoring an empty spec. `f\"{obj}\"` calls `__format__(\"\")`, which should normally return `str(self)`.""",
follow=[
    ("How does `datetime` use it?", "`f\"{dt:%Y-%m-%d}\"` passes the strftime pattern as the spec."),
    ("What does `object.__format__` do with a non-empty spec?", "Raises `TypeError`, so unsupported specs fail loudly."),
]),

X(30, "What are `__iter__` / `__next__`", terms=[
    ("Iterator protocol", "`__iter__` returns an iterator; `__next__` returns the next item or raises `StopIteration`."),
], pitfall="""Raising `StopIteration` inside a generator to end it. Since 3.7 (PEP 479) that becomes `RuntimeError`; just `return`.""",
follow=[
    ("What does `reversed()` fall back to without `__reversed__`?", "`__len__` plus `__getitem__` (the sequence protocol)."),
    ("How do you make an iterator restartable?", "Make the container's `__iter__` return a new iterator (or generator) on each call."),
]),

X(31, "What is `__class_getitem__`", terms=[
    ("`types.GenericAlias`", "The object returned by `list[int]`; it records the origin and arguments for type hints."),
], pitfall="""Expecting `list[int]` to enforce element types at runtime. `list[int]()` creates an ordinary list that accepts anything.""",
follow=[
    ("How do you make your own class generic?", "Inherit `typing.Generic[T]` or, since 3.12, use `class Box[T]: ...` syntax."),
    ("Why is it a separate hook rather than a metaclass `__getitem__`?", "To avoid needing a metaclass just for subscription (PEP 560)."),
]),

X(32, "What is `__del__` and why", terms=[
    ("Finalizer", "Code run when an object is reclaimed; `weakref.finalize` is the safer alternative."),
], pitfall="""Releasing important resources (flushing files, closing connections) only in `__del__`. It may run late, never (at interpreter exit), or in an unexpected thread; use context managers.""",
follow=[
    ("Do objects with `__del__` in cycles get collected?", "Yes, since Python 3.4 (PEP 442) the cyclic GC can collect them."),
    ("What happens if `__del__` raises?", "The exception is printed as \"Exception ignored in\" and otherwise ignored."),
]),

X(33, "What are `__copy__` and `__deepcopy__`", terms=[
    ("`memo`", "The dict passed to `__deepcopy__`; pass it on to nested `copy.deepcopy(x, memo)` calls."),
], pitfall="""Calling `copy.deepcopy(self.x)` without passing `memo` inside `__deepcopy__`. Shared or cyclic references are then duplicated or recurse infinitely.""",
follow=[
    ("How do you exclude a field from copying?", "In `__deepcopy__`, create the new object and copy every field except that one (sharing or resetting it)."),
    ("Does `pickle` use these hooks?", "No; pickle uses `__reduce_ex__`, `__getstate__` and `__setstate__`, which `copy` also falls back to."),
]),

X(34, "What are `__set_name__`", terms=[
    ("Descriptor protocol", "`__get__`, `__set__`, `__delete__` (and `__set_name__`) control attribute access for class attributes."),
    ("Data vs non-data descriptor", "Data descriptors define `__set__` or `__delete__` and take precedence over the instance `__dict__`."),
], pitfall="""Storing per-instance values on the descriptor itself (`self.value = v`). The descriptor is shared by all instances, so every instance sees the same value; store it in `instance.__dict__`.""",
follow=[
    ("Is `__set_name__` called for attributes added after class creation?", "No; call it manually if you attach a descriptor later with `setattr`."),
    ("What built-ins are descriptors?", "Functions, `property`, `classmethod`, `staticmethod` and `__slots__` members."),
]),

X(35, "Why does `len(obj)` work but `obj.__len__`", terms=[
    ("Type-level lookup", "Implicit special-method calls look up the method on `type(obj)`, bypassing the instance and `__getattribute__`."),
], pitfall="""Monkeypatching a dunder on one instance in a test (`obj.__eq__ = ...`). Operators ignore it; patch the class or use a subclass.""",
follow=[
    ("Why does Python do this?", "Speed, and correctness for classes: `hash(int)` must call `type.__hash__`, not `int.__hash__`."),
    ("Does explicit `obj.__len__()` see the instance attribute?", "Yes, explicit attribute access finds it; only implicit calls skip it."),
]),

X(36, "How do you implement a container that supports `+=`", terms=[
    ("In-place operator", "`__iadd__`, `__isub__`, ... which should mutate `self` and return it."),
], pitfall="""Forgetting `return self` in `__iadd__`. The name is rebound to `None` after `x += y`.""",
follow=[
    ("Why should immutable types not define `__iadd__`?", "Without it, `+=` falls back to `__add__` and rebinds the name, which is the correct behavior for immutables."),
    ("What does `__iadd__` do for a tuple element that is a list?", "It mutates the list, then the tuple item assignment raises `TypeError` (the famous `t[0] += [1]` puzzle)."),
]),

X(37, "What is `__missing__`", terms=[
    ("`__missing__`", "Called by `dict.__getitem__` for absent keys; its return value becomes the result."),
], pitfall="""Expecting `__missing__` to store the value automatically. It only returns it; insert explicitly (`self[key] = value`) as `defaultdict` does.""",
follow=[
    ("Does `__missing__` work on non-dict classes?", "No; it is a hook of `dict.__getitem__` only."),
    ("What is a typical custom use?", "Formatting templates with `str.format_map(SafeDict(...))`, where `__missing__` returns `\"{key}\"` for unknown placeholders."),
]),
]
