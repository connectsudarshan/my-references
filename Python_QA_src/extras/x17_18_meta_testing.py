EXTRAS = [

X(0, "What is a descriptor", terms=[
    ("Owner class", "The class on which the descriptor is stored; passed to `__get__` as `owner`."),
    ("`__get__(self, instance, owner)`", "Called for attribute reads; `instance` is `None` when accessed on the class."),
], pitfall="""Storing a descriptor as an instance attribute (`self.x = MyDescriptor()`). The protocol only works for class attributes, so it behaves like a plain object.""",
follow=[
    ("What should `__get__` return when `instance is None`?", "Usually the descriptor itself, so class-level access and introspection work."),
    ("Where are descriptors used in the stdlib?", "`property`, `classmethod`, `staticmethod`, `functools.cached_property`, bound methods and `__slots__`."),
]),

X(1, "Data vs non-data descriptors", terms=[
    ("Precedence", "Data descriptor on the type, then instance `__dict__`, then non-data descriptor or plain class attribute, then `__getattr__`."),
], pitfall="""Expecting to override a `property` by assigning an instance attribute. Properties are data descriptors, so the assignment calls the setter (or raises `AttributeError`) instead.""",
follow=[
    ("Why does `cached_property` work?", "It is a non-data descriptor: after the first call, the value stored in the instance `__dict__` wins on later lookups."),
    ("Are functions data descriptors?", "No, non-data; that is why you can shadow a method with an instance attribute."),
]),

X(2, "How is `property` implemented", terms=[
    ("`fget` / `fset` / `fdel`", "The functions stored on a property object."),
], pitfall="""Naming the setter method differently from the property (`@x.setter def set_x`). That creates a second property named `set_x` and leaves `x` read-only.""",
follow=[
    ("How do you write a property without decorators?", "`x = property(get_x, set_x, del_x, \"doc\")`."),
    ("Can a property be abstract?", "Yes, stack `@property` over `@abstractmethod`."),
]),

X(3, "What is a metaclass", terms=[
    ("`type`", "The default metaclass; `type(cls)` shows a class's metaclass."),
], pitfall="""Reaching for a metaclass when `__init_subclass__`, a class decorator or `__set_name__` would do. Metaclasses conflict easily when combining libraries.""",
follow=[
    ("What is a metaclass conflict?", "Deriving from two bases with unrelated metaclasses raises `TypeError`; you need a metaclass that subclasses both."),
    ("Which method creates the class object?", "`metaclass.__new__(mcls, name, bases, namespace)`; `__init__` then initializes it."),
]),

X(4, "How can you create a class dynamically", terms=[
    ("`types.new_class`", "Creates a class while correctly handling metaclasses and `__prepare__`."),
], pitfall="""Forgetting `__module__` and `__qualname__` in dynamically created classes. Pickling and reprs then point to the wrong place; set them explicitly.""",
follow=[
    ("How do you create a dataclass dynamically?", "`dataclasses.make_dataclass(\"Point\", [\"x\", \"y\"])`."),
    ("How do you define methods for `type()`?", "Put functions in the namespace dict; they become methods."),
]),

X(5, "What real-world problems do metaclasses solve", terms=[
    ("Declarative API", "Users describe structure with class attributes, and the framework builds behavior from them."),
], pitfall="""Writing a metaclass that silently changes semantics (renaming attributes, injecting methods). Debugging user classes becomes very hard; document and minimize the magic.""",
follow=[
    ("Which stdlib features use metaclasses?", "`abc.ABCMeta` and `enum.EnumType` (formerly `EnumMeta`)."),
    ("What can `__prepare__` enable?", "A custom namespace, for example one recording definition order or detecting duplicate names."),
]),

X(6, "What is the order of operations when a class statement runs", terms=[
    ("`__prepare__`", "Returns the mapping used as the class namespace while the body executes."),
], pitfall="""Expecting decorators to run before `__init_subclass__`. The class is fully created (including `__set_name__` and `__init_subclass__`) before class decorators are applied.""",
follow=[
    ("Where do `__set_name__` calls happen?", "Inside `type.__new__`, after the class object exists, before `__init_subclass__`."),
    ("When is the metaclass's `__call__` used?", "Not at class creation, but when instances are created: `Cls()` calls `type(Cls).__call__`."),
]),

X(7, "What does `__slots__` do and what are its limitations", terms=[
    ("Slot", "A fixed attribute stored at a known offset in the instance."),
], pitfall="""Adding `__slots__` to an existing class and breaking callers that use `obj.__dict__`, `vars(obj)`, or set ad-hoc attributes (common in tests and mocks). Search for such uses first.""",
follow=[
    ("Can you mix `__slots__` and `__dict__`?", "Yes, include `\"__dict__\"` in `__slots__` to allow dynamic attributes too."),
    ("Do slots work with multiple inheritance?", "Only one base in the hierarchy may have non-empty slots, otherwise you get a layout conflict."),
]),

X(8, "What is monkey patching", terms=[
    ("Patch", "A runtime replacement of an attribute, restored afterwards in tests."),
], pitfall="""Monkey patching in production code to fix a library bug and forgetting it. Upgrades silently change behavior; pin the version, add a test, and link the upstream issue.""",
follow=[
    ("How does pytest make patching safe?", "The `monkeypatch` fixture undoes every change after the test."),
    ("What is gevent's `monkey.patch_all()`?", "It replaces blocking stdlib functions with cooperative versions; it must run before other imports."),
]),

X(9, "What does `inspect` let you do", terms=[
    ("`inspect.getsource`", "Returns the source code of a function, class or module when the file is available."),
    ("`inspect.stack`", "Returns information about the current call stack."),
], pitfall="""Calling `inspect.stack()` in hot paths. It is slow because it reads source lines; use `sys._getframe()` if you only need the frame.""",
follow=[
    ("How do you check for async functions?", "`inspect.iscoroutinefunction`, `isasyncgenfunction`, `isawaitable`."),
    ("How do you get members of a module?", "`inspect.getmembers(module, inspect.isfunction)`."),
]),

X(10, "How do `eval`, `exec` and `compile` differ", terms=[
    ("Code object", "Compiled bytecode plus metadata, returned by `compile`."),
], pitfall="""Believing `eval(s, {\"__builtins__\": {}})` is a sandbox. Attribute tricks like `().__class__.__base__.__subclasses__()` escape it; never evaluate untrusted input.""",
follow=[
    ("What is the safe alternative for literals?", "`ast.literal_eval`."),
    ("What are legitimate uses of `exec`?", "Code generation in tools (e.g. dataclasses and namedtuple historically), REPLs and template engines."),
]),

X(11, "What is the `ast` module used for", terms=[
    ("`NodeVisitor` / `NodeTransformer`", "Classes that walk an AST, optionally replacing nodes."),
    ("`ast.unparse`", "(3.9+) Turns an AST back into source code."),
], pitfall="""Expecting `ast.parse` then `ast.unparse` to preserve formatting and comments. Comments are lost; use `libcst` for formatting-preserving refactors.""",
follow=[
    ("How do you view an AST?", "`print(ast.dump(ast.parse(src), indent=2))`."),
    ("How does pytest use AST rewriting?", "It rewrites `assert` statements in test modules to record intermediate values for detailed failure messages."),
]),

X(12, "How can you add methods or attributes to a class after", terms=[
    ("`types.MethodType`", "Binds a function to one instance as a method."),
], pitfall="""Assigning a function to an instance (`obj.m = func`) and expecting `self` to be passed. Functions on instances are not bound; use `types.MethodType(func, obj)`.""",
follow=[
    ("Do existing instances see a method added to the class?", "Yes; method lookup goes through the class at call time."),
    ("Can you add methods to built-in types like `str`?", "No; built-in types are immutable (`TypeError: cannot set ... attribute of immutable type 'str'`)."),
]),

X(13, "How do Django/SQLAlchemy model fields know their own names", terms=[
    ("`__set_name__(owner, name)`", "Hook called on each class attribute after class creation."),
], pitfall="""Reusing one descriptor instance for two attributes (`a = b = Field()`). `__set_name__` is called twice, and the second name overwrites the first.""",
follow=[
    ("How did frameworks do this before 3.6?", "A metaclass scanned the class namespace and told each field its name."),
    ("How do fields keep their definition order?", "Class namespaces are ordered dicts, so iteration follows definition order."),
]),

X(14, "What testing frameworks are common", terms=[
    ("Test runner", "The tool that discovers, runs and reports tests: pytest, `python -m unittest`."),
], pitfall="""Mixing unittest-style classes and pytest fixtures without knowing the limits. Fixtures cannot be injected into `unittest.TestCase` methods as parameters.""",
follow=[
    ("Can pytest run unittest tests?", "Yes, pytest discovers and runs `unittest.TestCase` subclasses."),
    ("What is `tox`/`nox`?", "Tools to run tests in several environments or Python versions."),
]),

X(15, "Write a basic unittest test case", terms=[
    ("`setUpClass`", "Classmethod run once before all tests in the class."),
    ("`addCleanup`", "Registers teardown functions that run even if `setUp` fails later."),
], pitfall="""Using `assertTrue(a == b)`. On failure it only says \"False is not true\"; `assertEqual(a, b)` shows both values.""",
follow=[
    ("How do you skip a test?", "`@unittest.skip(\"reason\")` or `@unittest.skipIf(cond, \"reason\")`."),
    ("How do you run a single test?", "`python -m unittest tests.test_mod.TestClass.test_method`."),
]),

X(16, "Why is pytest preferred", terms=[
    ("Assertion rewriting", "pytest rewrites `assert` statements to show the compared values on failure."),
    ("Parametrization", "`@pytest.mark.parametrize` runs one test with many inputs."),
], pitfall="""Writing `assert (a, b)` or asserting a non-empty tuple. It always passes; pytest warns about it.""",
follow=[
    ("How do you run tests matching a name?", "`pytest -k \"login and not slow\"`."),
    ("How do you stop at the first failure?", "`pytest -x`, and `--lf` reruns only last failures."),
]),

X(17, "What are pytest fixtures and scopes", terms=[
    ("Scope", "`function`, `class`, `module`, `package` or `session`: how long a fixture instance lives."),
    ("`conftest.py`", "File whose fixtures are visible to tests in its directory and below."),
], pitfall="""Session-scoped fixtures returning mutable objects that tests modify. State leaks between tests and makes results depend on order.""",
follow=[
    ("What does `autouse=True` do?", "Applies the fixture to every test in its scope without naming it."),
    ("How do you parametrize a fixture?", "`@pytest.fixture(params=[...])` and read `request.param`."),
]),

X(18, "How do you mock a dependency in tests", terms=[
    ("Test double", "A stand-in object: stub, fake, mock or spy."),
], pitfall="""Mocking so much that tests only check that mocks were called. They pass while real behavior is broken; mock at system boundaries (network, clock, filesystem).""",
follow=[
    ("How do you assert a call happened?", "`mock.assert_called_once_with(...)`; also inspect `mock.call_args_list`."),
    ("How do you make a mock raise?", "`mock.side_effect = ValueError(\"boom\")`; a list makes successive calls return successive values."),
]),

X(19, "Why does `mock.patch` sometimes not work", terms=[
    ("Lookup location", "The module namespace where the code under test finds the name at call time."),
], pitfall="""Patching `requests.get` when the code did `from requests import get`. The code keeps its own reference; patch `mymodule.get`.""",
follow=[
    ("How do you patch an attribute of an object?", "`mock.patch.object(SomeClass, \"method\")`."),
    ("How do you patch a dict or environment variables?", "`mock.patch.dict(os.environ, {\"KEY\": \"v\"})`, or pytest's `monkeypatch.setenv`."),
]),

X(20, "What is `MagicMock` vs `Mock`", terms=[
    ("`spec`", "Restricts a mock to the attributes of a real object."),
    ("`autospec`", "Also checks call signatures of methods."),
], pitfall="""Misspelling an assertion method on a plain `Mock` (`mock.assert_called_onse()`). Old versions returned a new mock and the test passed; modern versions raise `AttributeError` for names starting with `assert`, but `spec` catches more typos.""",
follow=[
    ("What is `AsyncMock`?", "A mock whose calls return awaitables; `patch` uses it automatically for async functions."),
    ("What is `seal()`?", "Prevents a mock from creating new attributes automatically."),
]),

X(21, "How do you test code that raises exceptions or logs", terms=[
    ("`caplog`", "pytest fixture capturing log records."),
    ("`capsys`", "pytest fixture capturing stdout/stderr."),
], pitfall="""Using `pytest.raises` around too much code. The test passes if any line raises that exception; wrap only the call that should raise.""",
follow=[
    ("How do you check exception attributes?", "`with pytest.raises(E) as exc_info:` then inspect `exc_info.value`."),
    ("How do you test exception groups?", "`pytest.raises(ExceptionGroup)` with `exc_info.group_contains(ValueError)` (pytest 8+), or `pytest.RaisesGroup`."),
]),

X(22, "What is property-based testing", terms=[
    ("Strategy", "A Hypothesis generator of input values, such as `st.integers()`."),
    ("Shrinking", "Reducing a failing input to a minimal example."),
], pitfall="""Writing properties that re-implement the function under test. Test invariants instead: round trips, idempotence, ordering, comparison with a simple reference implementation.""",
follow=[
    ("What are good properties for a sort function?", "The output is ordered, has the same length, and is a permutation (same `Counter`) of the input."),
    ("How does Hypothesis reproduce failures?", "It stores failing examples in a local database and replays them first."),
]),

X(23, "How do you debug Python code", terms=[
    ("`PYTHONBREAKPOINT`", "Environment variable choosing what `breakpoint()` calls, or `0` to disable it."),
    ("Post-mortem", "Debugging after a crash with `python -m pdb script.py` or `pdb.pm()`."),
], pitfall="""Leaving `breakpoint()` calls in committed code. CI hangs waiting for input; add a linter rule (Ruff T100) against it.""",
follow=[
    ("How do you debug in pytest on failure?", "`pytest --pdb` opens the debugger at the failing line."),
    ("How do you attach to a running process?", "`python -m pdb -p PID` (3.14+), or IDE/debugpy attach."),
]),

X(24, "How do you read a Python traceback", terms=[
    ("Frame line", "`File \"x.py\", line N, in func` followed by the source line."),
    ("Chained traceback", "Several tracebacks joined by \"direct cause\" or \"during handling\" messages."),
], pitfall="""Reading only the top of a long traceback. The actual failure is at the bottom, and with chained exceptions the root cause is often the first traceback printed.""",
follow=[
    ("What do the `^^^^` markers mean?", "Since 3.11 they point at the exact sub-expression that failed."),
    ("How do you print a traceback without raising?", "`traceback.print_exc()` inside `except`, or `traceback.print_stack()` anywhere."),
]),

X(25, "What is code coverage", terms=[
    ("Branch coverage", "Whether both outcomes of each condition were executed."),
], pitfall="""Chasing 100% line coverage. Tests can execute every line without asserting anything meaningful; review assertions and consider mutation testing (mutmut).""",
follow=[
    ("How do you enable branch coverage?", "`coverage run --branch` or `pytest --cov --cov-branch`."),
    ("What is `sys.monitoring`'s effect on coverage?", "Since 3.12, coverage.py can use the low-overhead `sys.monitoring` API, making coverage much faster."),
]),

X(26, "How do you test async code", terms=[
    ("`IsolatedAsyncioTestCase`", "unittest base class that runs each test in a fresh event loop."),
], pitfall="""Writing `async def test_x()` without the plugin or marker. Plain pytest does not run the coroutine; depending on the version it warns, fails or skips it.""",
follow=[
    ("How do you avoid real sleeps in async tests?", "Inject the sleep function or clock, or patch `asyncio.sleep` with an `AsyncMock`."),
    ("What is anyio's pytest plugin?", "Runs async tests on asyncio and trio backends with `@pytest.mark.anyio`."),
]),

X(27, "What's the difference between unit, integration", terms=[
    ("Test pyramid", "Many fast unit tests, fewer integration tests, and a few end-to-end tests."),
], pitfall="""Mocking the database in all \"integration\" tests. Real query behavior (constraints, transactions, SQL dialect) goes untested; use a real database in a container (testcontainers).""",
follow=[
    ("What are contract tests?", "Tests that check a service honors the API expected by its consumers, such as with Pact."),
    ("How do you keep slow tests out of the default run?", "Mark them (`@pytest.mark.slow`) and deselect with `-m \"not slow\"`."),
]),

X(28, "How do you freeze time or control randomness", terms=[
    ("Dependency injection", "Passing collaborators (clock, RNG) in rather than using globals."),
], pitfall="""Patching `datetime.datetime.now` directly with `mock.patch`. It fails because built-in types cannot be patched; use `freezegun`/`time-machine` or inject a clock.""",
follow=[
    ("Why is time-machine faster than freezegun?", "It patches time at the C level instead of replacing modules' references."),
    ("How do you seed Hypothesis or NumPy?", "Hypothesis manages its own seed (`--hypothesis-seed`); NumPy uses `np.random.default_rng(seed)`."),
]),

X(29, "What is logging best practice", terms=[
    ("`NullHandler`", "A handler that discards records, avoiding \"no handler\" warnings in libraries."),
    ("Structured logging", "Logging key-value data (JSON), for example with `structlog`, instead of free text."),
], pitfall="""Using f-strings inside log calls at DEBUG level in hot paths. The string is formatted even when DEBUG is disabled; pass arguments (`log.debug(\"x=%s\", x)`).""",
follow=[
    ("How do you add request IDs to every log line?", "A `logging.Filter` or `LoggerAdapter` reading a `contextvars.ContextVar`."),
    ("Where should applications configure logging?", "Once at startup, in the entry point, typically with `dictConfig`."),
]),

X(30, "How do you find where a slow or hanging Python process", terms=[
    ("Sampling profiler", "Periodically records stacks with low overhead; py-spy works without modifying the program."),
    ("`faulthandler`", "Dumps Python tracebacks on crashes or on a signal/timeout."),
], pitfall="""Adding print statements to production to find a hang. Attach py-spy or enable `faulthandler.register(signal.SIGUSR1)` instead; no restart or code change needed.""",
follow=[
    ("What is new in Python 3.14 for this?", "`python -m asyncio ps PID` and `pstree PID` show running asyncio tasks of another process."),
    ("How do you profile CPU in development?", "`python -m cProfile -o out.prof script.py`, viewed with snakeviz, or use scalene/py-spy flame graphs."),
]),

X(31, "What are doctests", terms=[
    ("`ELLIPSIS` option", "Doctest directive allowing `...` to match any output."),
], pitfall="""Doctests with unstable output (dict ordering in old versions, memory addresses, floats). They fail randomly; use doctests for simple, deterministic examples.""",
follow=[
    ("How does pytest run doctests?", "`pytest --doctest-modules`."),
    ("Are doctests a replacement for unit tests?", "No; they keep documentation correct but are awkward for edge cases and setup."),
]),

X(32, "How do you structure tests in a project", terms=[
    ("src layout", "Package under `src/`, so tests run against the installed package, not the working directory."),
], pitfall="""Putting `__init__.py`-less test folders with duplicate file names (`tests/a/test_utils.py`, `tests/b/test_utils.py`). pytest's default import mode raises errors; use unique names or `--import-mode=importlib`.""",
follow=[
    ("Where should test configuration live?", "`[tool.pytest.ini_options]` in `pyproject.toml`, or a `pytest.ini`."),
    ("How do you run tests in parallel?", "`pytest -n auto` with the pytest-xdist plugin."),
]),
]
