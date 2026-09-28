EXTRAS = [

X(0, "What are `*args` and `**kwargs`", terms=[
    ("Packing", "`*args`/`**kwargs` in a `def` collect extra arguments."),
    ("Unpacking", "`f(*seq, **mapping)` at a call site spreads a sequence and a mapping into separate arguments."),
], pitfall="""Using `*args, **kwargs` as a public signature. IDEs, `help()` and type checkers can no longer show the real parameters, and a misspelled keyword is accepted silently or fails far from the call. Keep explicit parameters, and forward with `ParamSpec` when wrapping.""",
follow=[
    ("What order must parameters appear in?", "Positional-only, `/`, normal, `*args` (or bare `*`), keyword-only, `**kwargs`."),
    ("How do you type-hint `*args` and `**kwargs`?", "Annotate the element type: `*args: int, **kwargs: str`; use `ParamSpec` (`P.args`, `P.kwargs`) to forward another function's signature."),
]),

X(1, "What is the mutable default argument trap", terms=[
    ("Definition time", "The moment the `def` statement executes; default expressions are evaluated then, once."),
], pitfall="""The same trap in dataclasses: `items: list = []` is rejected with `ValueError`; use `field(default_factory=list)`.""",
follow=[
    ("Is the shared default ever useful?", "Occasionally as a deliberate per-function cache (`def f(x, _cache={})`), but `functools.cache` is clearer."),
    ("Where can you see the stored default?", "`f.__defaults__`; you can watch it grow between calls."),
]),

X(2, "What are positional-only and keyword-only", terms=[
    ("`/` marker", "Everything before it can only be passed by position (PEP 570)."),
    ("Bare `*`", "Everything after it must be passed by keyword."),
], pitfall="""Adding a new positional parameter in the middle of a public function. Existing positional calls silently shift meaning; add new parameters as keyword-only.""",
follow=[
    ("Why do many built-ins use positional-only parameters?", "Their C implementations never had parameter names, and it leaves the names free to change; for example `len(obj=x)` is invalid."),
    ("How do positional-only parameters help with `**kwargs`?", "A positional-only `name` does not clash with a `\"name\"` key collected in `**kwargs`."),
]),

X(3, "What is the LEGB rule", terms=[
    ("Scope", "The region of code where a name binding is visible."),
    ("`builtins` module", "Holds the built-in names (`len`, `print`, ...), searched last."),
], pitfall="""Class bodies are not an enclosing scope for methods. A method cannot see a class attribute by its bare name; use `self.attr` or `ClassName.attr`.""",
follow=[
    ("Do comprehensions have their own scope?", "Yes, the loop variable is local to the comprehension (since Python 3); since 3.12 comprehensions are inlined but keep that isolation."),
    ("Where do `if`/`for` blocks fit in?", "They do not create scopes; a variable assigned inside an `if` is visible after it in the same function."),
]),

X(4, "What do `global` and `nonlocal` do", terms=[
    ("Rebinding", "Making a name point to a different object, as opposed to mutating the object."),
], pitfall="""Adding `global` for a variable you only mutate (`counts.append(x)`). Mutation does not need it; only assignment to the name does.""",
follow=[
    ("What happens with `nonlocal x` if no enclosing function defines `x`?", "A `SyntaxError` at compile time."),
    ("What is a cleaner alternative to `global` state?", "Pass values explicitly, return new values, or wrap the state in a class or a small object."),
]),

X(5, "Why does this raise `UnboundLocalError`", terms=[
    ("Compile-time scoping", "The compiler decides whether a name is local by scanning the whole function body for assignments."),
], pitfall="""An `import x` or `for x in ...` later in the function also counts as assignment, making an earlier use of the global `x` fail.""",
follow=[
    ("Is `UnboundLocalError` a subclass of `NameError`?", "Yes."),
    ("How do you inspect which names are local?", "`fn.__code__.co_varnames` lists local variable names."),
]),

X(6, "What is a closure", terms=[
    ("Free variable", "A variable used in a function but defined in an enclosing function."),
    ("Cell", "An object that holds a free variable so both the outer and inner function share it."),
], pitfall="""Assuming a closure snapshots values. It shares the variable, so later changes in the outer scope are visible inside.""",
follow=[
    ("How do you read a closure's captured values?", "`[c.cell_contents for c in fn.__closure__]`, with names in `fn.__code__.co_freevars`."),
    ("Closure or class: which to choose?", "A closure for one small function with a little state; a class when you need several methods, introspection or a clear name for the state."),
]),

X(7, "Why do closures created in a loop", terms=[
    ("Late binding", "The value of a free variable is looked up when the inner function runs, not when it is created."),
], pitfall="""The same bug with callbacks in GUI code or `asyncio` tasks created in a loop: every handler sees the final loop value.""",
follow=[
    ("Besides a default argument, how can you bind the value?", "`functools.partial(func, i)` or a factory function `make(i)` that returns the inner function."),
    ("Does a list comprehension of lambdas have the same issue?", "Yes: `[lambda: i for i in range(3)]` all return 2."),
]),

X(8, "What is a lambda function", terms=[
    ("Anonymous function", "A function object without a statement-level name; its `__name__` is `\"<lambda>\"`."),
], pitfall="""Assigning a lambda to a name (`f = lambda x: x * 2`). Use `def`; you get a real name in tracebacks, a docstring and PEP 8 compliance.""",
follow=[
    ("Can a lambda contain statements?", "No, only one expression; no assignments (except `:=`), no `return`, no `try`."),
    ("What can replace common lambdas?", "`operator.itemgetter`, `attrgetter` and `methodcaller`."),
]),

X(9, "What does it mean that functions are first-class", terms=[
    ("First-class object", "Can be created at runtime, stored, passed and returned like any value."),
], pitfall="""Passing `f()` instead of `f` as a callback. The function runs immediately and its return value is passed.""",
follow=[
    ("What is a dispatch table?", "A dict mapping keys to functions, replacing long `if/elif` chains: `handlers[cmd](args)`."),
    ("Can you attach attributes to a function?", "Yes, `f.calls = 0`; functions have a `__dict__`."),
]),

X(10, "What are `map`, `filter`", terms=[
    ("Fold", "Combining a sequence into one value with a binary function; `reduce` is Python's fold."),
], pitfall="""Consuming a `map` or `filter` object twice. They are one-shot iterators, so the second pass is empty.""",
follow=[
    ("When is `map` preferred over a comprehension?", "When applying an existing function, especially a built-in, such as `map(str, nums)`; with a lambda, a comprehension is clearer."),
    ("What does `filter(None, it)` do?", "Keeps only truthy items."),
]),

X(11, "What is `functools.partial`", terms=[
    ("Partial application", "Fixing some arguments of a function to produce a function of fewer arguments."),
    ("`partialmethod`", "The version for methods defined in a class body."),
], pitfall="""Later keyword arguments override the pre-filled ones, but repeating a pre-filled positional argument by keyword raises `TypeError: got multiple values`.""",
follow=[
    ("How do you inspect a partial?", "`p.func`, `p.args` and `p.keywords`."),
    ("Why prefer `partial` to a lambda in multiprocessing?", "A partial of a module-level function can be pickled; a lambda cannot."),
]),

X(12, "What does a function return if it has no `return`", terms=[
    ("Implicit return", "Falling off the end of a function returns `None`."),
], pitfall="""Returning a value on some paths and nothing on others. Callers then receive `None` unexpectedly; type checkers flag this with a declared return type.""",
follow=[
    ("How do you return multiple values with names?", "Return a `NamedTuple` or dataclass instead of a bare tuple."),
    ("What does `-> NoReturn` (or `Never`) mean?", "The function never returns normally; it always raises or exits."),
]),

X(13, "What is recursion", terms=[
    ("Base case", "The condition that stops recursion."),
    ("Tail call optimization", "Reusing the stack frame for a final call; CPython does not do it."),
], pitfall="""Raising the limit with `sys.setrecursionlimit(10**6)` for deep recursion. The C stack can still overflow and crash the process; convert to iteration with an explicit stack.""",
follow=[
    ("Why does CPython not do tail call optimization?", "It would remove frames from tracebacks and complicate debugging, and Guido chose not to add it."),
    ("How do you make a recursive DFS iterative?", "Replace the call stack with a list used as a stack, pushing child nodes and popping in a loop."),
]),

X(14, "How do you memoize a recursive function", terms=[
    ("Memoization", "Caching a function's results by its arguments."),
    ("`cache_info()`", "Reports hits, misses and current size for `lru_cache`/`cache` functions."),
], pitfall="""Putting `@lru_cache` on a method. The cache holds `self`, keeping every instance alive for the life of the program; cache on a module function or use `cached_property`.""",
follow=[
    ("How do you clear the cache?", "`fn.cache_clear()`."),
    ("What does `typed=True` do?", "Caches `f(3)` and `f(3.0)` separately."),
]),

X(15, "How are arguments passed", terms=[
    ("Call by sharing", "The callee gets a new name bound to the same object the caller passed."),
], pitfall="""Trying to write a `swap(a, b)` function that swaps the caller's variables. Rebinding parameters cannot affect the caller; return the new values instead.""",
follow=[
    ("How do you let a function \"modify\" an immutable argument?", "Return the new value and let the caller rebind it."),
    ("Is anything copied at the call?", "Only references; no object is copied."),
]),

X(16, "What are function annotations", terms=[
    ("Deferred annotations", "Python 3.14 (PEP 649/749) evaluates annotations lazily when first accessed, so forward references work without quotes."),
    ("`annotationlib`", "3.14 module for reading annotations in different formats (values, forward refs, strings)."),
], pitfall="""Reading `obj.__annotations__` directly on classes in older code. Use `inspect.get_annotations()` or `annotationlib.get_annotations()`, which handle inheritance and lazy evaluation correctly.""",
follow=[
    ("What did `from __future__ import annotations` do?", "Stored annotations as strings (PEP 563); in 3.14 the new lazy evaluation is the default instead."),
    ("Can annotations be used at runtime?", "Yes, libraries such as pydantic, FastAPI and dataclasses read them."),
]),

X(17, "How do you inspect a function's signature", terms=[
    ("`Parameter.kind`", "One of POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD, VAR_POSITIONAL, KEYWORD_ONLY, VAR_KEYWORD."),
    ("`Signature.bind`", "Maps arguments to parameters exactly as a call would, raising `TypeError` if they do not fit."),
], pitfall="""Inspecting a decorated function whose wrapper does not use `functools.wraps`. You see `(*args, **kwargs)` instead of the real signature.""",
follow=[
    ("How does `wraps` make `signature()` work?", "It sets `__wrapped__`, which `inspect.signature` follows to the original function."),
    ("Can every callable be inspected?", "Most can; some C built-ins without text signatures raise `ValueError`."),
]),

X(18, "What is the difference between a function and a method", terms=[
    ("Descriptor", "An object with `__get__`; functions are descriptors, which is how they become bound methods."),
    ("`__self__` / `__func__`", "A bound method's instance and underlying function."),
], pitfall="""Comparing bound methods with `is`. Each attribute access creates a new bound method object, so `obj.m is obj.m` is False; use `==`.""",
follow=[
    ("What happens when you access a method on the class?", "You get the plain function; call it with the instance explicitly: `Class.m(obj)`."),
    ("Why can storing `obj.method` as a callback leak memory?", "The bound method holds a strong reference to `obj`; use `weakref.WeakMethod` if needed."),
]),

X(19, "What is a higher-order function", terms=[
    ("Callback", "A function passed to another function to be called later."),
], pitfall="""Writing higher-order helpers that swallow the passed function's exceptions or change its signature without `functools.wraps`.""",
follow=[
    ("What is function composition?", "Building `h(x) = f(g(x))`; Python has no built-in operator for it, but `functools.reduce` can compose a list of functions."),
    ("Is a decorator a higher-order function?", "Yes, it takes a function and returns a function."),
]),

X(20, "How do default argument values and `__defaults__`", terms=[
    ("`__kwdefaults__`", "Dict of defaults for keyword-only parameters."),
], pitfall="""Patching `__defaults__` at runtime to change behavior. It works, but it is invisible to readers and type checkers; use a parameter or configuration.""",
follow=[
    ("Why is `__defaults__` a tuple aligned to the end?", "Only the last N positional parameters can have defaults, so the tuple matches them from the right."),
    ("Are defaults re-evaluated if the module is reloaded?", "Yes, reloading re-runs the `def`, creating a new function with new defaults."),
]),

X(21, "How would you write a function that accepts any number", terms=[
    ("`statistics.fmean`", "Fast float mean (3.8+); `statistics.mean` handles `Fraction`/`Decimal` exactly but is slower."),
], pitfall="""Dividing by `len(args)` without handling zero arguments, which raises `ZeroDivisionError`. Decide explicitly: raise a clear `ValueError` or return `None`.""",
follow=[
    ("How would you also accept one iterable argument?", "Check `len(args) == 1 and isinstance(args[0], Iterable)`, but a single calling convention is cleaner."),
    ("How do you avoid float precision loss when summing many values?", "Use `math.fsum`."),
]),

X(22, "What are classes and objects", terms=[
    ("Instance", "An object created from a class; `type(obj)` is its class."),
    ("`type`", "The default metaclass: classes are instances of `type`."),
], pitfall="""Using classes as namespaces for loosely related functions. In Python a module already is a namespace.""",
follow=[
    ("Is a class an object?", "Yes; you can pass it around, add attributes and create it dynamically with `type(name, bases, ns)`."),
    ("What does `object` provide?", "Default `__init__`, `__repr__`, `__eq__` (identity), `__hash__` and attribute access machinery."),
]),

X(23, "What is `self`", terms=[
    ("Explicit self", "Python passes the instance as an ordinary first argument instead of an implicit `this`."),
], pitfall="""Forgetting `self` in a method definition. Calling it then fails with `TypeError: takes 0 positional arguments but 1 was given`.""",
follow=[
    ("Is `self` a keyword?", "No, just a convention; any name works, but always use `self`."),
    ("Why is self explicit?", "It makes instance-variable access obvious, and methods are just functions called with the instance."),
]),

X(24, "What is `__init__`", terms=[
    ("`__new__`", "Static method that creates and returns the instance; used for immutable types and singletons."),
], pitfall="""Returning a value from `__init__`, which raises `TypeError: __init__() should return None`.""",
follow=[
    ("When would you override `__new__`?", "Subclassing immutable types (`int`, `str`, `tuple`), instance caching, or returning a different class."),
    ("Is `__init__` called if `__new__` returns an object of another class?", "No, only when `__new__` returns an instance of the class being created."),
]),

X(25, "Class attributes vs instance attributes", terms=[
    ("Shadowing", "An instance attribute with the same name hides the class attribute for that instance."),
], pitfall="""A mutable class attribute (`items = []`) used as per-instance storage. All instances share one list; create it in `__init__`.""",
follow=[
    ("What does `self.count += 1` do when `count` is a class attribute?", "Reads the class value, then creates an instance attribute; the class attribute is unchanged."),
    ("How do you update a class attribute from an instance method?", "`type(self).count += 1` or `ClassName.count += 1`."),
]),

X(26, "What are instance methods, class methods", terms=[
    ("Alternate constructor", "A classmethod such as `from_json` that builds an instance from another format."),
], pitfall="""Making a helper `@staticmethod` and then calling other class methods by the hard-coded class name. Subclasses cannot override those calls; use a classmethod.""",
follow=[
    ("Why use `cls(...)` rather than `ClassName(...)` in an alternate constructor?", "So subclasses calling it get instances of the subclass."),
    ("Can a staticmethod be called on an instance?", "Yes, `obj.helper()` works; no instance is passed."),
]),

X(27, "What is encapsulation in Python", terms=[
    ("Name mangling", "`__name` in a class body becomes `_ClassName__name`, to avoid clashes in subclasses."),
], pitfall="""Using `__name` for \"privacy\". It is not security, and it complicates subclassing and testing; a single underscore is the norm.""",
follow=[
    ("Can you still reach a mangled attribute?", "Yes, as `obj._ClassName__name`."),
    ("Does `from module import *` import `_names`?", "No, unless they are listed in `__all__`."),
]),

X(28, "What is `@property`", terms=[
    ("Managed attribute", "An attribute whose get, set and delete go through methods."),
    ("`cached_property`", "Computes once on first access and stores the result in the instance `__dict__`."),
], pitfall="""Doing expensive work or I/O inside a property. Callers expect attribute access to be cheap; use a method with a verb name.""",
follow=[
    ("How do you make a read-only attribute?", "Define only the getter; assignment then raises `AttributeError`."),
    ("Does `cached_property` work with `__slots__`?", "Not without a `__dict__` slot, because it stores the value in the instance dict."),
]),

X(29, "What are the four pillars of OOP", terms=[
    ("Polymorphism", "Different types responding to the same operation or method name."),
], pitfall="""Forcing Java-style patterns (getters/setters for everything, deep hierarchies). Python favors plain attributes, properties when needed, and duck typing.""",
follow=[
    ("How does Python support abstraction without interfaces?", "ABCs and `typing.Protocol` define the required methods."),
    ("Is operator overloading polymorphism?", "Yes, `+` works on ints, strings and lists through `__add__`."),
]),

X(30, "What are abstract base classes", terms=[
    ("`@abstractmethod`", "Marks a method subclasses must override before they can be instantiated."),
    ("`register`", "Declares a virtual subclass without inheritance."),
], pitfall="""Using `ABC` but forgetting to inherit from it (or use `ABCMeta`). `@abstractmethod` then has no effect and the class can be instantiated.""",
follow=[
    ("ABC or Protocol?", "ABC for explicit, nominal interfaces with shared code; Protocol for structural typing checked statically."),
    ("Can abstract methods have an implementation?", "Yes; subclasses can call it via `super()`."),
]),

X(31, "What is duck typing", terms=[
    ("EAFP", "Easier to Ask Forgiveness than Permission: try the operation and handle the exception."),
    ("`typing.Protocol`", "Static duck typing: a type matches if it has the right methods."),
], pitfall="""Partial duck types: an object with `read()` but not `readline()` passed to code that needs both. Document the exact protocol needed.""",
follow=[
    ("LBYL or EAFP?", "EAFP is usually more Pythonic and avoids race conditions; LBYL (checks first) fits when failures are expensive to undo."),
    ("Can you check duck types at runtime?", "Yes with `@runtime_checkable` protocols and `isinstance`, but it only checks method presence, not signatures."),
]),

X(32, "What are dataclasses", terms=[
    ("`field(default_factory=...)`", "Creates a fresh default for each instance."),
    ("`slots=True`", "(3.10+) generates `__slots__` for lower memory and faster attribute access."),
], pitfall="""Expecting dataclasses to validate types. `Point(x=\"a\")` is accepted; add checks in `__post_init__` or use pydantic.""",
follow=[
    ("What does `kw_only=True` do?", "Makes all fields keyword-only, which also avoids field-ordering errors with defaults."),
    ("How do you copy with changes?", "`dataclasses.replace(obj, x=1)`, or `copy.replace` in 3.13+."),
]),

X(33, "Composition vs inheritance", terms=[
    ("Fragile base class", "Changes in a base class unexpectedly breaking subclasses."),
], pitfall="""Subclassing `dict` or `list` to add behavior. Built-in methods like `update` or `extend` do not call your overridden `__setitem__`/`append`; use `collections.UserDict` or composition.""",
follow=[
    ("What is delegation?", "Forwarding calls to a contained object, sometimes automatically via `__getattr__`."),
    ("When is inheritance right?", "For genuine is-a relationships and framework hooks designed for subclassing (e.g. `unittest.TestCase`)."),
]),

X(34, "How do you compare objects for equality", terms=[
    ("`NotImplemented`", "Return it from `__eq__` for unknown types so Python tries the reflected operation."),
], pitfall="""Hashing on mutable fields. If a field used in `__hash__` changes while the object is in a set, the object is lost in the set.""",
follow=[
    ("How do you get all comparison operators from two?", "`functools.total_ordering` with `__eq__` and one of `__lt__`, `__le__`, `__gt__`, `__ge__`."),
    ("What is a good `__hash__` implementation?", "`hash((self.a, self.b))` over the same fields `__eq__` uses."),
]),

X(35, "What is `__dict__` on an object", terms=[
    ("`mappingproxy`", "A read-only view of a class namespace."),
], pitfall="""Iterating `obj.__dict__` to serialize an object. It misses properties, slots and class attributes, and includes private state; define an explicit method.""",
follow=[
    ("How do you list all attributes including inherited ones?", "`dir(obj)`."),
    ("Why can't you assign `Class.__dict__[\"x\"] = 1`?", "The class dict is exposed read-only so the type's attribute cache stays valid; use `setattr(Class, \"x\", 1)`."),
]),

X(36, "How do `getattr`, `setattr`", terms=[
    ("`__getattr__`", "Called only when normal lookup fails."),
    ("`__getattribute__`", "Called for every attribute access; overriding it is powerful and easy to get wrong."),
], pitfall="""Accessing `self.something` inside `__getattr__` for an attribute that may not exist yet (e.g. during unpickling). It recurses into `__getattr__` until `RecursionError`.""",
follow=[
    ("How do you give `getattr` a default?", "`getattr(obj, name, default)` returns the default instead of raising."),
    ("How does `hasattr` behave with properties that raise?", "Since Python 3.2 it only swallows `AttributeError`; other exceptions propagate."),
]),

X(37, "What is the difference between `__str__` and `__repr__`", terms=[
    ("`__format__`", "Hook for format specs used by f-strings and `format()`."),
], pitfall="""Putting secrets such as tokens and passwords in `__repr__`. They end up in logs and error reports; mask them.""",
follow=[
    ("What does a good repr look like?", "`ClassName(field=value, ...)`, ideally valid Python that recreates the object."),
    ("What does `!r` do in an f-string?", "Uses `repr()` of the value."),
]),

X(38, "How do you make a class iterable", terms=[
    ("Iterable vs iterator", "An iterable returns a new iterator from `__iter__`; an iterator has `__next__` and returns itself from `__iter__`."),
], pitfall="""Returning `self` from `__iter__` of a container. Then only one loop can run at a time and the object is exhausted after one pass.""",
follow=[
    ("What does the legacy `__getitem__` protocol do?", "Without `__iter__`, Python iterates by calling `__getitem__(0)`, `(1)`, ... until `IndexError`."),
    ("How do you support `reversed()`?", "Define `__reversed__`, or `__len__` plus `__getitem__`."),
]),

X(39, "What is `__init_subclass__`", terms=[
    ("Class hook", "A method on a base class that runs whenever a subclass is created."),
], pitfall="""Forgetting to call `super().__init_subclass__(**kwargs)`. In multiple-inheritance hierarchies other bases' hooks then silently do not run.""",
follow=[
    ("How do class keyword arguments reach it?", "`class Plugin(Base, name=\"x\"):` passes `name=\"x\"` to `Base.__init_subclass__`."),
    ("What does `__set_name__` do?", "Called on descriptors when the owning class is created, telling them their attribute name."),
]),

X(40, "What are class-level `__slots__`", terms=[
    ("Slot descriptor", "Each slot becomes a descriptor on the class that stores the value at a fixed offset in the instance."),
], pitfall="""Adding `__slots__` to a subclass whose base does not define slots. The instances still get a `__dict__`, so there is no memory saving.""",
follow=[
    ("Do slots prevent weak references?", "Yes, unless `\"__weakref__\"` is listed in the slots."),
    ("Can you have class-level defaults for slot names?", "No; a class attribute with the same name as a slot raises `ValueError`. Set defaults in `__init__`."),
]),

X(41, "How do you implement a singleton", terms=[
    ("Borg pattern", "Instances share state (one `__dict__`) rather than being the same object."),
], pitfall="""Implementing a singleton via `__new__` while `__init__` still runs on every construction, resetting state each time.""",
follow=[
    ("Why are singletons often discouraged?", "They are hidden global state, make tests interfere with each other and hide dependencies; prefer passing objects in."),
    ("Is a module-level instance thread-safe to create?", "Yes; module import is protected by the import lock, so it runs once."),
]),

X(42, "What is the difference between `copy.copy` of an object", terms=[
    ("`__copy__` / `__reduce_ex__`", "Hooks controlling how `copy` creates the new object."),
], pitfall="""Copying objects that own resources such as open files, sockets or locks. The copy shares the underlying resource; define `__copy__` or disallow copying.""",
follow=[
    ("How does `copy` create an instance without `__init__`?", "It uses the pickle protocol: `cls.__new__(cls)` then updates `__dict__` or slots."),
    ("What is `copy.replace` (3.13)?", "Creates a modified copy for types that implement `__replace__`, such as dataclasses and namedtuples."),
]),

X(43, "What is an enum", terms=[
    ("`auto()`", "Assigns values automatically."),
    ("`Flag`", "Enum whose members combine with bitwise operators."),
], pitfall="""Comparing a plain `Enum` member to its value (`Color.RED == 1`). It is False; compare members, or use `IntEnum`/`StrEnum` if value equality is needed.""",
follow=[
    ("How do you look up a member by value or name?", "By value `Color(1)`, by name `Color[\"RED\"]`."),
    ("How do you prevent duplicate values?", "Decorate with `@enum.unique`."),
]),
]
