EXTRAS = [

X(0, "What is Python", terms=[
    ("CPython", "The reference implementation, written in C. When people say \"Python\" they almost always mean CPython."),
    ("Dynamic typing", "Types belong to objects, not names, and are checked while the program runs."),
], pitfall="""Saying Python is \"slow\" without qualification. Pure-Python loops are slow compared to C, but most real programs spend their time in C-implemented built-ins, NumPy, databases or I/O, where Python is only the glue.""",
follow=[
    ("Name some Python implementations besides CPython.", "PyPy (JIT compiler, often much faster for pure-Python loops), MicroPython (microcontrollers), GraalPy (JVM/GraalVM) and Jython (older, Python 2 only)."),
    ("Why is Python popular for data science and scripting?", "Readable syntax, a huge ecosystem (NumPy, pandas, PyTorch), an interactive REPL/notebook workflow, and easy bindings to fast C/C++/Fortran code."),
]),

X(1, "Is Python compiled", terms=[
    ("Bytecode", "The compact instruction set the CPython virtual machine executes; inspect it with `dis`."),
    ("`__pycache__`", "Folder where CPython caches compiled `.pyc` files so it can skip recompiling unchanged modules."),
], pitfall="""Assuming `.pyc` files make code faster to run. They only skip the compile step on import; the bytecode runs at exactly the same speed.""",
follow=[
    ("When is a `.pyc` file regenerated?", "When the source file's modification time or size (or its hash, for hash-based pycs) no longer matches what is recorded in the `.pyc` header."),
    ("Is the main script cached as a `.pyc`?", "No. Only imported modules are cached; the script you run directly is compiled fresh every time."),
]),

X(2, "What is PEP 8", terms=[
    ("PEP", "Python Enhancement Proposal: the design document format used to propose and record language changes."),
    ("Linter / formatter", "A linter (Ruff, flake8) reports style and bug patterns; a formatter (Black, `ruff format`) rewrites code into one consistent style."),
], pitfall="""Arguing style in code review by hand. Put a formatter and linter in pre-commit and CI so style is never a discussion.""",
follow=[
    ("What does PEP 8 itself say about consistency?", "Consistency within a project matters more than consistency with PEP 8, and consistency within one module or function matters most."),
    ("What is PEP 257?", "The docstring conventions: triple double quotes, a one-line summary, then a blank line before any details."),
]),

X(3, "How does indentation work", terms=[
    ("Block", "A group of statements that runs together, such as a function body or the body of an `if`. Python marks blocks with indentation."),
    ("`TabError`", "Subclass of `IndentationError`, raised when tabs and spaces are mixed ambiguously."),
], pitfall="""Copy-pasting code from a web page or chat that mixes tabs and non-breaking spaces. Configure the editor to insert 4 spaces and show whitespace.""",
follow=[
    ("Where does indentation NOT matter?", "Inside brackets, parentheses and braces (implicit line joining), and in continuation lines after a backslash."),
    ("Why did Python choose indentation over braces?", "Code is indented for humans anyway; making indentation the syntax removes the mismatch between what the code looks like and what it does."),
]),

X(4, "What is the difference between `is`", terms=[
    ("Identity", "Whether two references point to the same object, as reported by `id()`."),
    ("Equality", "Whether two objects are considered equal by `__eq__`."),
], pitfall="""Writing `x is 1000` or `s is "hello"`. It may appear to work because of caching and interning, then fail for other values; CPython 3.8+ even emits a `SyntaxWarning` for `is` with a literal.""",
follow=[
    ("Can `a == b` be True while `a is b` is False?", "Yes, any two equal but distinct objects, for example two separate lists `[1] == [1]`."),
    ("Can `a is b` be True while `a == b` is False?", "Yes, when `__eq__` says so. `float('nan')` is the classic case: `x = float('nan'); x is x` is True but `x == x` is False."),
]),

X(5, "What are Python's built-in data types", terms=[
    ("Sequence", "An ordered collection indexed by integers: `str`, `list`, `tuple`, `range`, `bytes`."),
    ("Mapping", "Key-to-value lookup; `dict` is the built-in one."),
], pitfall="""Forgetting that `bool` is an `int` subclass, so `isinstance(True, int)` is True and `True` can slip through numeric validation.""",
follow=[
    ("Which built-in types are immutable?", "`int`, `float`, `complex`, `bool`, `str`, `tuple`, `frozenset`, `bytes`, `range` and `NoneType`."),
    ("What is `frozenset` for?", "An immutable, hashable set, so it can be a dict key or an element of another set."),
]),

X(6, "What is `None`", terms=[
    ("Singleton", "A type with exactly one instance. `None`, `True`, `False`, `...` and `NotImplemented` are singletons."),
    ("Sentinel", "A unique marker object used to mean \"no value given\" when `None` is itself a valid value."),
], pitfall="""Using `if not x:` when you mean `if x is None:`. It also treats `0`, `\"\"` and `[]` as missing.""",
follow=[
    ("How do you tell \"argument not passed\" from \"passed None\"?", "Use a private sentinel: `_MISSING = object()` and `def f(x=_MISSING): if x is _MISSING: ...`."),
    ("What does a function return if it has only a bare `return`?", "`None`, the same as falling off the end of the function."),
]),

X(7, "What does `pass` do", terms=[
    ("`Ellipsis`", "The singleton object `...`; used as a placeholder, in type hints (`tuple[int, ...]`) and in NumPy slicing."),
], pitfall="""Leaving `pass` in an `except` block (`except Exception: pass`). It silently swallows errors; at least log them.""",
follow=[
    ("Is `...` valid as a function body?", "Yes. It is an expression statement, so `def f(): ...` is legal and is common in stubs and protocols."),
    ("What is the difference between `pass` and `...` at runtime?", "None that matters: the compiler drops both (a constant expression statement is optimized away), so neither costs anything."),
]),

X(8, "What is the difference between `break`", terms=[
    ("Nearest loop", "`break` and `continue` affect only the innermost enclosing `for`/`while`."),
], pitfall="""Expecting `break` to leave nested loops. Python has no labelled break; move the loops into a function and `return`, or use a flag.""",
follow=[
    ("How do you break out of two nested loops cleanly?", "Put them in a function and `return`, or use `for ... else: continue` followed by `break` in the outer loop."),
    ("Does `continue` inside `try/finally` run the `finally`?", "Yes. `finally` always runs when control leaves the `try`, including via `continue`, `break` or `return`."),
]),

X(9, "What does the `else` clause on a `for`", terms=[
    ("Loop `else`", "A block that runs when the loop ends normally (the iterable is exhausted or the `while` condition turns false), not after `break`."),
], pitfall="""Reading loop `else` as \"if the loop did not run\". It also runs when the loop ran to completion; it is really \"no break\".""",
follow=[
    ("Does `else` run if the loop body never executes?", "Yes. An empty iterable finishes without a `break`, so the `else` runs."),
    ("What is a more readable alternative?", "Often `any()`/`next()` with a generator, or a helper function that returns early when it finds the item."),
]),

X(10, "How do you take input", terms=[
    ("stdin / stdout", "The standard input and output streams, available as `sys.stdin` and `sys.stdout`."),
], pitfall="""Calling `input()` in a loop to read large data in competitive programming or pipelines. Use `sys.stdin.read()` or `sys.stdin.buffer` instead; it is far faster.""",
follow=[
    ("How do you print without a newline?", "`print(x, end=\"\")`; add `flush=True` if the output must appear immediately, for example in a progress bar."),
    ("How do you print to stderr?", "`print(msg, file=sys.stderr)`."),
]),

X(11, "What are f-strings", terms=[
    ("Format spec", "The mini-language after the colon: `{x:>10.2f}` means right-align, width 10, 2 decimals."),
    ("Conversion", "`!r`, `!s`, `!a` apply `repr()`, `str()` or `ascii()` before formatting."),
], pitfall="""Building SQL or shell commands with f-strings. That enables injection; use parameterized queries and argument lists.""",
follow=[
    ("What does `f\"{x=}\"` print?", "The expression text and its repr, for example `x=42`; very handy for debugging (3.8+)."),
    ("What changed for f-strings in Python 3.12?", "PEP 701 formalized them in the grammar, so you can reuse the same quote type inside, and use backslashes and comments inside the braces."),
]),

X(12, "What is the difference between `/`", terms=[
    ("Floor division", "Division rounded toward negative infinity, so `-7 // 2` is -4."),
    ("`divmod()`", "Returns `(a // b, a % b)` in one call."),
], pitfall="""Porting C code that assumes truncation toward zero. In Python `-7 // 2 == -4` and `-7 % 2 == 1`; use `math.trunc(a / b)` or `int(a / b)` for C-style results (with float precision caveats).""",
follow=[
    ("What is `math.fmod` versus `%`?", "`math.fmod` follows C: the result has the sign of the dividend. `%` gives the sign of the divisor."),
    ("What does `//` return for floats?", "A float that is floored: `7.5 // 2` is `3.0`."),
]),

X(13, "What does `**` do", terms=[
    ("Right-associative", "Groups from the right: `a ** b ** c` means `a ** (b ** c)`."),
    ("Three-argument `pow`", "`pow(b, e, m)` computes modular exponentiation efficiently; `pow(b, -1, m)` gives the modular inverse (3.8+)."),
], pitfall="""Writing `-2 ** 2` and expecting 4. It is `-(2 ** 2)`, which is -4; use `(-2) ** 2`.""",
follow=[
    ("What does `2 ** -1` return?", "`0.5`, a float, because a negative integer exponent cannot give an int."),
    ("What does `(-8) ** (1/3)` return?", "A complex number, because a negative base with a fractional exponent has no real principal value in floating point."),
]),

X(14, "What are comments and docstrings", terms=[
    ("`__doc__`", "The attribute that stores a module's, class's or function's docstring."),
], pitfall="""Using triple-quoted strings as block comments in the middle of code. They are evaluated expressions (discarded) and confuse doc tools; use `#`.""",
follow=[
    ("Which docstring styles are common?", "Google style, NumPy style and reStructuredText (Sphinx). Pick one per project."),
    ("Does `python -OO` affect docstrings?", "Yes, `-OO` strips docstrings (and asserts), so code must not depend on `__doc__` at runtime."),
]),

X(15, "What is `if __name__", terms=[
    ("`__main__`", "The name given to the module that started the program, and the name of the file `python -m pkg` runs (`pkg/__main__.py`)."),
], pitfall="""Leaving top-level work (network calls, heavy computation) outside the guard. Importing the module for a test or with multiprocessing's spawn start method then runs it again.""",
follow=[
    ("Why is the guard required with multiprocessing on Windows and macOS?", "The spawn start method imports the main module in each child; without the guard the child would start its own children."),
    ("What does `python -m module` do differently from `python file.py`?", "It finds the module on `sys.path`, sets up package context so relative imports work, and runs it as `__main__`."),
]),

X(16, "What is the walrus operator", terms=[
    ("Assignment expression", "The official name of `name := value` (PEP 572)."),
], pitfall="""Using `:=` just to be clever in a one-liner. It helps only when it removes a duplicated call; otherwise a normal assignment is clearer.""",
follow=[
    ("Where is `:=` not allowed without parentheses?", "At the top level of an expression statement, and in some positions such as keyword argument values; `y := 5` alone is a `SyntaxError`, `(y := 5)` is fine."),
    ("Does a walrus in a comprehension leak the name?", "Yes. The target binds in the enclosing function scope, unlike the comprehension's loop variable."),
]),

X(17, "How do you swap two variables", terms=[
    ("Tuple packing / unpacking", "`b, a` builds a tuple on the right; `a, b = ...` unpacks it into the names on the left."),
], pitfall="""Swapping items with computed indices, such as `a[i], a[a[i]] = a[a[i]], a[i]`. The targets are assigned left to right, so the second index is computed after `a[i]` has already changed.""",
follow=[
    ("Does CPython really build a tuple for `a, b = b, a`?", "No. For two or three names the compiler emits a stack swap without creating a tuple."),
    ("How do you rotate three variables?", "`a, b, c = b, c, a`."),
]),

X(18, "What is extended unpacking", terms=[
    ("Starred target", "A `*name` on the left of an assignment that collects the remaining items into a list."),
], pitfall="""Expecting the starred name to be a tuple or the original type. It is always a list, even when unpacking a tuple or a string.""",
follow=[
    ("What does `*a, = range(3)` do?", "Binds `a` to `[0, 1, 2]`; the trailing comma makes the left side a tuple target."),
    ("What happens with too few items, as in `a, *b, c = [1]`?", "`ValueError: not enough values to unpack (expected at least 2, got 1)`."),
]),

X(19, "What is the ternary", terms=[
    ("Conditional expression", "`A if cond else B`; only the chosen branch is evaluated."),
], pitfall="""Nesting ternaries (`a if x else b if y else c`). It parses, but it is hard to read; use `if/elif` or a lookup dict.""",
follow=[
    ("What is the old `cond and a or b` idiom and why is it buggy?", "It returns `b` whenever `a` is falsy, even when `cond` is true; the real conditional expression has no such issue."),
    ("Can you use a ternary on the left of an assignment?", "No, it is an expression. Use `(x if c else y).attr = ...` only for attribute or item targets, and even then an `if` is clearer."),
]),

X(20, "What is chained comparison", terms=[
    ("Chaining", "`a op1 b op2 c` means `a op1 b and b op2 c`, with `b` evaluated only once and short-circuiting."),
], pitfall="""Writing `x == y == True` or `a < b == c` and misreading it. `False == False in [False]` is True because it means `(False == False) and (False in [False])`.""",
follow=[
    ("Is `1 < x < 10` faster than `1 < x and x < 10`?", "Roughly the same; the benefit is readability and evaluating `x` only once when it is an expensive expression."),
    ("Does `in` chain?", "Yes, `in`, `not in`, `is` and `is not` are comparison operators and chain like `<`."),
]),

X(21, "What does `match`", terms=[
    ("Capture pattern", "A bare name in a pattern that binds the matched value, such as `case [x, y]:`."),
    ("Value pattern", "A dotted name such as `Color.RED`, which compares by equality instead of capturing."),
], pitfall="""Writing `case RED:` expecting it to compare with a constant `RED`. A bare name is a capture pattern that matches everything; use a dotted name (`Color.RED`) or a guard.""",
follow=[
    ("How do class patterns match positional arguments?", "Through the class's `__match_args__`; dataclasses and namedtuples set it automatically."),
    ("Is `match` just a switch statement?", "No. It destructures sequences, mappings and objects and binds names; a plain switch is only the literal-pattern case."),
]),

X(22, "What is `del`", terms=[
    ("Name binding", "The link between a name and an object in a namespace; `del` removes the link, not the object."),
    ("`__del__`", "A finalizer that may run when an object is reclaimed; it is not what `del` calls."),
], pitfall="""Using `del x` to free memory while another reference (a list, a cache, a closure) still holds the object. Nothing is freed until the last reference goes.""",
follow=[
    ("What does `del a[:]` do?", "Empties the list in place, like `a.clear()`, so every other reference to that list sees it empty."),
    ("What happens if you use a name after `del`?", "`NameError` (or `UnboundLocalError` inside a function)."),
]),

X(23, "What are Python's keywords", terms=[
    ("Soft keyword", "A word that is a keyword only in a specific grammar context (`match`, `case`, `_`, `type`), so it stays usable as a normal name elsewhere."),
], pitfall="""Shadowing built-ins such as `list`, `id`, `type` or `input` with variable names. They are not keywords, so Python allows it, and later calls break confusingly.""",
follow=[
    ("How do you list keywords programmatically?", "`import keyword; keyword.kwlist` and `keyword.softkwlist`."),
    ("Why were `async`/`await` made full keywords only in 3.7?", "To avoid breaking existing code that used them as names; they were soft keywords in 3.5 and 3.6."),
]),

X(24, "What are mutable and immutable", terms=[
    ("Mutable", "Can change in place while keeping the same identity."),
    ("Immutable", "Any \"change\" produces a new object; the original is never modified."),
], pitfall="""Using a mutable default argument (`def f(x=[])`). The list is created once and shared by every call.""",
follow=[
    ("Why are dict keys required to be immutable (hashable)?", "The hash decides where the key lives in the table; if the key changed, lookups would search the wrong slot."),
    ("Is a frozen dataclass truly immutable?", "Attribute assignment raises `FrozenInstanceError`, but fields that hold mutable objects can still be mutated, and `object.__setattr__` can bypass it."),
]),

X(25, "How are variables different", terms=[
    ("Reference semantics", "Names hold references to objects; assignment copies the reference, never the object."),
], pitfall="""Thinking `b = a` copies a list. Both names refer to one list, so `b.append(1)` changes `a` too.""",
follow=[
    ("What is the closest C analogy to a Python variable?", "A `PyObject *` pointer: every name is a pointer to a heap object that carries its own type and reference count."),
    ("Does `x = 5; x = x + 1` modify the int 5?", "No. It creates or looks up the int 6 and rebinds `x`; ints are immutable."),
]),

X(26, "What is dynamic typing", terms=[
    ("Strong typing", "No implicit conversion between unrelated types: `\"1\" + 1` raises `TypeError`."),
    ("Duck typing", "Using an object by what it can do (its methods) rather than its declared type."),
], pitfall="""Assuming type hints are enforced at runtime. They are not; use a type checker (mypy, pyright) or a validation library (pydantic) for enforcement.""",
follow=[
    ("Which implicit conversions DO happen?", "Numeric widening (`int` to `float` to `complex`) and truth testing via `__bool__`/`__len__`."),
    ("What is gradual typing?", "Adding optional static types to a dynamic language, so typed and untyped code can mix (PEP 483/484)."),
]),

X(27, "What values are falsy", terms=[
    ("Truth testing", "`bool(x)` calls `__bool__`, falling back to `__len__`; objects without either are truthy."),
], pitfall="""Checking `if value:` where 0 or an empty string is a legitimate value, for example a quantity of 0 or an empty name field.""",
follow=[
    ("Is `numpy.array([1, 2])` truthy?", "Neither; `bool()` on a multi-element array raises `ValueError`. Use `.any()` or `.all()`."),
    ("What is the truth value of `datetime.time(0, 0)`?", "Since Python 3.5 it is True; earlier versions treated midnight as falsy."),
]),

X(28, "How do `int` and `float` differ", terms=[
    ("Arbitrary precision", "Integers grow digit by digit in memory, so they cannot overflow."),
    ("IEEE-754 double", "The 64-bit binary floating-point format used by `float`: 53-bit mantissa, roughly 15-17 significant decimal digits."),
], pitfall="""Converting huge ints to float (`float(10**400)` raises `OverflowError`), or losing precision silently above 2**53, where not every integer is representable as a float.""",
follow=[
    ("What is `sys.float_info.max`?", "About 1.8e308, the largest finite float."),
    ("Why did Python 3.11 limit int-to-str conversion length?", "Converting enormous ints to decimal is quadratic and was a denial-of-service risk; the default limit is 4300 digits (`sys.set_int_max_str_digits`)."),
]),

X(29, "Why is `0.1 + 0.2", terms=[
    ("Representation error", "The difference between a decimal literal and the nearest binary float."),
    ("`math.isclose`", "Compares with a relative tolerance (default 1e-9), plus an optional absolute tolerance for values near zero."),
], pitfall="""Using `math.isclose(x, 0.0)` without `abs_tol`. The relative tolerance of zero is zero, so only an exact 0.0 passes.""",
follow=[
    ("When should you use `Decimal` versus `Fraction`?", "`Decimal` for money and human-facing decimal arithmetic; `Fraction` for exact rational arithmetic such as ratios."),
    ("Why build `Decimal` from strings?", "`Decimal(0.1)` captures the float's binary error exactly; `Decimal(\"0.1\")` is exactly one tenth."),
]),

X(30, "How does `round()` work", terms=[
    ("Banker's rounding", "Round half to even: ties go to the nearest even digit to avoid a systematic upward bias."),
], pitfall="""Using `round()` for money. Use `Decimal.quantize(Decimal(\"0.01\"), rounding=ROUND_HALF_UP)` so ties follow your business rule.""",
follow=[
    ("What does `round(x)` return versus `round(x, 2)`?", "`round(x)` returns an int; `round(x, n)` returns a float (for float input)."),
    ("How do you always round up?", "`math.ceil()` for integers; `Decimal` with `ROUND_CEILING` for a specific number of decimals."),
]),

X(31, "How do you convert between types", terms=[
    ("Constructor conversion", "Calling the type itself, such as `int(\"42\")`, to build a new object from another value."),
], pitfall="""`int(\"3.7\")` raises `ValueError` and `bool(\"False\")` is True. Parse explicitly: `int(float(s))`, and compare strings for booleans.""",
follow=[
    ("What does `int(3.9)` return?", "3; it truncates toward zero, it does not round."),
    ("How do you safely parse a Python literal from a string?", "`ast.literal_eval`, never `eval`."),
]),

X(32, "What is `bool` in Python", terms=[
    ("Subclass of `int`", "`bool` inherits from `int`, with exactly two instances, `True` (1) and `False` (0)."),
], pitfall="""JSON or config validation that checks `isinstance(v, int)` also accepts `True`. Test `type(v) is int` or exclude bool explicitly.""",
follow=[
    ("What does `sum([True, False, True])` return?", "2."),
    ("Can you subclass `bool`?", "No, `bool` is final; `class B(bool): pass` raises `TypeError`."),
]),

X(33, "What is the difference between `type()`", terms=[
    ("Virtual subclass", "A class registered with an ABC via `register()`, so `isinstance` accepts it without real inheritance."),
], pitfall="""Using `type(x) == dict` to check input. It rejects `OrderedDict`, `defaultdict` and custom mappings; use `isinstance(x, Mapping)`.""",
follow=[
    ("What does `type` with three arguments do?", "Creates a class dynamically: `type(\"C\", (Base,), {\"x\": 1})`."),
    ("Can `isinstance` be customized?", "Yes, via `__instancecheck__` on the metaclass; ABCs use this."),
]),

X(34, "What happens when you pass a mutable", terms=[
    ("Call by sharing", "The parameter is bound to the same object as the argument; rebinding the parameter does not affect the caller."),
], pitfall="""Mutating an argument the caller did not expect to change, such as sorting a list in place inside a helper. Copy it first or document the mutation.""",
follow=[
    ("Why does `x = x + [1]` inside a function not affect the caller, but `x += [1]` does?", "`x + [1]` builds a new list and rebinds the local name; `+=` on a list calls `__iadd__`, which extends the shared list in place."),
    ("How do you make a function safe from caller mutation?", "Accept an immutable type (tuple, frozenset), or copy on entry."),
]),

X(35, "Shallow copy vs deep copy", terms=[
    ("`__deepcopy__`", "Hook a class can define to control how `copy.deepcopy` copies it."),
    ("Memo dict", "The dict `deepcopy` uses to track already-copied objects, which is how it handles cycles and shared references."),
], pitfall="""Using `deepcopy` in a hot loop or on objects holding locks, sockets or large arrays. It is slow and can fail; copy only what you need.""",
follow=[
    ("Does `deepcopy` preserve shared references inside the structure?", "Yes. If two slots referred to the same inner list, the copy's two slots refer to one new list."),
    ("How do you shallow-copy a dict?", "`d.copy()`, `dict(d)` or `{**d}`."),
]),

X(36, "Why does `[[0] * 3] * 3`", terms=[
    ("Aliasing", "Several references to one mutable object, so a change through one is seen through all."),
], pitfall="""The same bug with `dict.fromkeys(keys, [])`: every key shares one list. Use `{k: [] for k in keys}`.""",
follow=[
    ("Is `[0] * 3` safe?", "Yes, because ints are immutable; replacing an item rebinds that slot instead of mutating a shared object."),
    ("How can you detect the aliasing?", "`grid[0] is grid[1]` returns True."),
]),

X(37, "Are tuples always immutable", terms=[
    ("Shallow immutability", "The container's slots are fixed, but the objects in them may themselves be mutable."),
], pitfall="""Using a tuple containing a list as a dict key or set member. It raises `TypeError: unhashable type: 'list'`.""",
follow=[
    ("What does `t = ([1],); t[0] += [2]` do?", "It raises `TypeError` but the list is still extended to `[1, 2]`: `+=` mutates the list first, then the tuple item assignment fails."),
    ("How do you make a deeply immutable record?", "Use tuples of immutables, `frozenset`, or a frozen dataclass whose fields are themselves immutable."),
]),

X(38, "What is hashability", terms=[
    ("Hash/eq contract", "If `a == b` then `hash(a) == hash(b)`; the reverse is not required."),
], pitfall="""Defining `__eq__` on a class without `__hash__`. Python sets `__hash__ = None`, so instances become unhashable and cannot go into sets.""",
follow=[
    ("Why is `hash(-1) == hash(-2)` in CPython?", "-1 is reserved as an error code in the C API, so `hash(-1)` returns -2."),
    ("Are user-defined objects hashable by default?", "Yes, by identity (derived from `id()`), and equal only to themselves."),
]),

X(39, "What is `id()`", terms=[
    ("Object lifetime", "From creation until the reference count (or cyclic GC) reclaims it; `id` values may be reused afterwards."),
], pitfall="""Storing `id(obj)` as a key after the object may die. A new object can get the same id; keep a reference or use `weakref`.""",
follow=[
    ("Why can `id([]) == id([])` be True?", "The first list is freed immediately after `id()` returns, and the second list reuses the same memory."),
    ("Is `id` the memory address on every implementation?", "No, only in CPython; PyPy and others return an arbitrary unique integer."),
]),

X(40, "What are augmented assignments", terms=[
    ("`__iadd__`", "In-place addition hook; must return the resulting object (usually `self`)."),
], pitfall="""A list used as a class attribute and extended with `self.items += [x]`. It mutates the shared class-level list, and then also creates an instance attribute pointing to it.""",
follow=[
    ("What does `x += 1` do for an int?", "No `__iadd__` exists, so it computes `x + 1` and rebinds `x` to the new int."),
    ("Is `a += b` for strings in a loop slow?", "CPython sometimes optimizes it in place, but it is not guaranteed; `\"\".join(parts)` is the reliable way."),
]),

X(41, "What are `bytes` and `bytearray`", terms=[
    ("Encoding", "A mapping from Unicode code points to bytes, such as UTF-8."),
    ("`memoryview`", "A zero-copy view over a bytes-like object's buffer."),
], pitfall="""Relying on the platform default encoding in `open()` and `.encode()`. Always pass `encoding=\"utf-8\"` (UTF-8 mode becomes the default in Python 3.15).""",
follow=[
    ("What does indexing a `bytes` object return?", "An int (`b\"A\"[0] == 65`); slicing returns `bytes`."),
    ("How do you handle undecodable bytes?", "Pass `errors=\"replace\"`, `\"ignore\"`, `\"backslashreplace\"` or `\"surrogateescape\"` to `decode`."),
]),

X(42, "What is `complex`", terms=[
    ("`cmath`", "Math functions for complex numbers, such as `cmath.sqrt(-1) == 1j`."),
], pitfall="""Calling `math.sqrt(-1)`, which raises `ValueError`. Use `cmath.sqrt` when complex results are expected.""",
follow=[
    ("Can complex numbers be ordered with `<`?", "No, `<` raises `TypeError`; compare magnitudes with `abs()`."),
    ("How do you get the phase angle?", "`cmath.phase(z)`, or `cmath.polar(z)` for `(r, phi)`."),
]),

X(43, "What are `NaN` and `inf`", terms=[
    ("NaN", "Not a Number: the result of undefined operations such as `inf - inf`; it compares unequal to everything."),
], pitfall="""Sorting or taking `max()` of data containing NaN. Comparisons with NaN are all False, so results depend on position; filter with `math.isnan` first.""",
follow=[
    ("Why does `nan in [nan]` return True for the same object?", "Containment checks identity before equality, so the same NaN object is found even though `nan == nan` is False."),
    ("How do you create infinity?", "`float(\"inf\")` or `math.inf`."),
]),

X(44, "Explain integer caching", terms=[
    ("Small int cache", "CPython keeps preallocated objects for -5..256."),
    ("`sys.intern`", "Explicitly interns a string so equal strings share one object, making dict lookups on them cheaper."),
], pitfall="""Writing tests that pass because of caching (`a is b` for small ints or short strings) and fail with other values or on other interpreters.""",
follow=[
    ("Why are identifier-like strings interned automatically?", "Attribute and variable names are looked up in dicts constantly; sharing one object speeds up comparisons."),
    ("Are constants in the same code object shared?", "Often yes; equal constants in one compiled unit can be merged, which is why results differ between the REPL and a script."),
]),

X(45, "What is the difference between `==` and `is` for `True`", terms=[
    ("Key collision", "Distinct objects that compare equal with equal hashes map to one dict slot."),
], pitfall="""Building `{1: \"a\", True: \"b\", 1.0: \"c\"}` and expecting three entries. You get one entry: key `1`, value `\"c\"`.""",
follow=[
    ("Which key object is kept when equal keys collide?", "The first inserted key object stays; only the value is replaced."),
    ("How would you keep 1 and True distinct?", "Key by `(type(k), k)`."),
]),

X(46, "What are constants in Python", terms=[
    ("`typing.Final`", "A type-checker annotation meaning the name must not be reassigned or overridden."),
], pitfall="""Making a \"constant\" list or dict and then mutating it. `Final` only stops rebinding; use a tuple or `types.MappingProxyType` for read-only data.""",
follow=[
    ("How do you group related constants?", "Use an `enum.Enum` (or `IntEnum`/`StrEnum`) so values are named, typed and iterable."),
    ("Can a module prevent reassignment of its globals?", "Not directly; a module-level `__setattr__` is not supported, though you can replace the module's class with a subclass that defines one."),
]),
]
