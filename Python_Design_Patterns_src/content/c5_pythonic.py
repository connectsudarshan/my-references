PATTERNS = [

{
"id": "registry", "cat": "pythonic", "name": "Registry / Plugin",
"alias": "Classes or functions register themselves in a lookup table so they can be found by name.",
"simple": "A food court directory board: every new stall adds its name and counter number to the board. Visitors look up \"pizza\" on the board; the building manager never has to be told about each new stall.",
"intent": """<p>A registry is a dict from a key (name, type, file extension, command) to a class or function. Code that needs one looks it up instead of importing it directly. Adding a feature means adding a new registered class, with no edits to the dispatching code (Open/Closed Principle).</p>
<p>Python gives you three ways to register: a <b>decorator</b> (<code>@register("csv")</code>), <b><code>__init_subclass__</code></b> (every subclass registers automatically), and <b>package entry points</b> (<code>importlib.metadata.entry_points</code>) so separately installed packages can add plugins, which is how pytest, Flask and many CLIs load extensions.</p>""",
"structure": """ PARSERS = {"csv": CsvParser, "json": JsonParser, "xml": XmlParser}
 class YamlParser(Parser, fmt="yaml")   -> auto-added by __init_subclass__
 parser_for("report.yaml")  -> PARSERS["yaml"]()""",
"code": r'''
import json, csv, io

class Parser:
    registry: dict[str, type["Parser"]] = {}

    def __init_subclass__(cls, *, ext: str, **kw):     # runs when a subclass is DEFINED
        super().__init_subclass__(**kw)
        if ext in Parser.registry:
            raise ValueError(f"duplicate parser for .{ext}")
        Parser.registry[ext] = cls

    @classmethod
    def for_file(cls, filename: str) -> "Parser":
        ext = filename.rsplit(".", 1)[-1].lower()
        try:
            return cls.registry[ext]()
        except KeyError:
            raise ValueError(f"no parser for .{ext}; known: {sorted(cls.registry)}") from None

class JsonParser(Parser, ext="json"):
    def parse(self, text): return json.loads(text)

class CsvParser(Parser, ext="csv"):
    def parse(self, text): return list(csv.DictReader(io.StringIO(text)))

# a plugin added later, in another module: no edits above
class KeyValueParser(Parser, ext="env"):
    def parse(self, text): return dict(l.split("=", 1) for l in text.splitlines() if l)

print("registered:", sorted(Parser.registry))
print(Parser.for_file("orders.csv").parse("id,total\n1,99\n"))
print(Parser.for_file("app.ENV").parse("DEBUG=0\nDB=postgres"))
try:
    Parser.for_file("photo.png")
except ValueError as e:
    print(e)
''',
"pythonic": r'''
from importlib.metadata import entry_points

# decorator-based registry for functions (how CLIs and task runners register commands)
COMMANDS = {}
def command(name):
    def deco(fn):
        COMMANDS[name] = fn
        return fn
    return deco

@command("greet")
def greet(who="world"): return f"hello {who}"
@command("version")
def version(): return "2.4.1"

print(COMMANDS["greet"]("riya"), "|", COMMANDS["version"]())

# installed packages register plugins through entry points (pip installs, no code edits)
groups = entry_points()
print("console_scripts found:", len(groups.select(group="console_scripts")) > 0)
''',
"pythonic_note": "A decorator that fills a dict is the lightest registry. Entry points extend it across packages: a plugin just declares itself in its <code>pyproject.toml</code>.",
"examples": [
  {"where": "stdlib", "title": "<code>atexit.register</code>, <code>codecs.register</code>, <code>copyreg.pickle</code>, <code>mimetypes.add_type</code>", "body": "Registries all over the stdlib: exit handlers, text encodings looked up by name (<code>'utf-8'</code>), custom pickling functions per type, and file-extension to MIME-type mappings."},
  {"where": "stdlib", "title": "<code>abc.ABC.register</code> and <code>importlib.metadata.entry_points</code>", "body": "<code>Sequence.register(MyList)</code> makes <code>isinstance(x, Sequence)</code> true without inheritance (a virtual subclass registry). Entry points are the packaging-level plugin registry."},
  {"where": "framework", "title": "pytest plugins, Flask extensions and blueprints", "body": "pytest discovers plugins through the <code>pytest11</code> entry-point group (via pluggy). Flask apps call <code>app.register_blueprint(bp)</code>, and <code>@app.route</code> is itself a registry of URL rules."},
  {"where": "framework", "title": "Django <code>admin.site.register</code>, DRF <code>router.register</code>, Celery <code>@app.task</code>", "body": "Admin pages, API routes and background tasks are all looked up by name from registries filled at import time."},
  {"where": "production", "title": "File-format, payment-provider and device-driver plugins", "body": "Data platforms register one parser per format, payment services one adapter per provider, test frameworks one driver per device model. New ones ship as separate modules or packages without touching the core."}
],
"use": ["Many interchangeable implementations chosen by a key (format, name, type)", "Third parties or other teams should add implementations without editing core code", "CLI commands, routes, handlers, serializers"],
"avoid": ["Only a couple of fixed implementations: an explicit dict literal is clearer", "Registration by import side effect when nothing imports the module (the plugin silently never registers)"],
"pitfall": "Plugins register only when their module is imported. If nothing imports <code>yaml_parser.py</code>, it is not in the registry. Import plugin modules explicitly at startup, or use entry points, which are discovered without imports.",
"qa": [
  {"q": "What is <code>__init_subclass__</code> and how is it used for registries?", "a": "<p>A classmethod hook (PEP 487, Python 3.6+) called on the base class whenever a subclass is created. It receives class keyword arguments, so <code>class JsonParser(Parser, ext='json')</code> can register itself without a metaclass.</p>"},
  {"q": "How do Python plugin systems discover plugins from other packages?", "a": "<p>Through entry points: a package declares <code>[project.entry-points.\"myapp.plugins\"]</code> in <code>pyproject.toml</code>; the host calls <code>importlib.metadata.entry_points(group='myapp.plugins')</code> and loads each one.</p>"},
  {"q": "How does a registry relate to Factory Method?", "a": "<p>A registry is the lookup table a factory uses: <code>Parser.for_file()</code> is a factory whose choice comes from the registry, so adding types doesn't change the factory.</p>"}
],
"related": ["factory-method", "strategy", "dependency-injection"]
},

{
"id": "dependency-injection", "cat": "pythonic", "name": "Dependency Injection",
"alias": "Give an object its collaborators from outside instead of letting it create them.",
"simple": "A chef doesn't grow vegetables or build the stove. The restaurant hands the chef ingredients and equipment. In a cooking class the chef gets toy ingredients to practise with, same recipes, no real cost.",
"intent": """<p>If <code>OrderService</code> creates its own <code>StripeClient()</code> and <code>PostgresRepo()</code> inside <code>__init__</code>, it can't be tested without Stripe and PostgreSQL, and it can't be reconfigured. With DI, dependencies are <b>passed in</b> (usually to the constructor). The code that wires real objects together lives in one place at startup (the <b>composition root</b>).</p>
<p>Python needs no framework for this: constructor arguments with type hints (often <code>Protocol</code>s) are enough. Frameworks like FastAPI (<code>Depends</code>) and pytest (fixtures) do injection for you by looking at function parameters.</p>""",
"structure": """ main():   repo = PostgresRepo(dsn); pay = StripeGateway(key)
           service = OrderService(repo, pay)           <- composition root
 tests:    service = OrderService(FakeRepo(), FakeGateway())
 OrderService never calls PostgresRepo() or StripeGateway() itself""",
"code": r'''
from typing import Protocol
from dataclasses import dataclass, field

class PaymentGateway(Protocol):
    def charge(self, customer_id: str, amount: float) -> str: ...
class OrderRepo(Protocol):
    def save(self, order: dict) -> None: ...
class Clock(Protocol):
    def now(self) -> str: ...

class OrderService:
    def __init__(self, repo: OrderRepo, payments: PaymentGateway, clock: Clock):
        self.repo, self.payments, self.clock = repo, payments, clock   # injected

    def place(self, customer_id, amount):
        ref = self.payments.charge(customer_id, amount)
        order = {"customer": customer_id, "amount": amount, "ref": ref, "at": self.clock.now()}
        self.repo.save(order)
        return order

# ---- test doubles: no network, no DB, deterministic time
@dataclass
class FakeRepo:
    saved: list = field(default_factory=list)
    def save(self, order): self.saved.append(order)

class FakeGateway:
    def __init__(self, fail=False): self.fail, self.calls = fail, []
    def charge(self, customer_id, amount):
        self.calls.append((customer_id, amount))
        if self.fail: raise RuntimeError("card declined")
        return "PAY-TEST-1"

class FixedClock:
    def now(self): return "2026-09-28T10:00:00Z"

repo, gw = FakeRepo(), FakeGateway()
svc = OrderService(repo, gw, FixedClock())
print(svc.place("C-7", 499.0))
assert repo.saved[0]["ref"] == "PAY-TEST-1" and gw.calls == [("C-7", 499.0)]

failing = OrderService(FakeRepo(), FakeGateway(fail=True), FixedClock())
try:
    failing.place("C-8", 10.0)
except RuntimeError as e:
    print("declined path tested without Stripe:", e, "| saved:", failing.repo.saved)
''',
"pythonic": r'''
# How pytest injects fixtures: it reads parameter NAMES and supplies matching objects.
# A 15-line imitation of the idea:
import inspect

PROVIDERS = {}
def fixture(fn): PROVIDERS[fn.__name__] = fn; return fn

@fixture
def db(): return {"users": ["riya", "arjun"]}
@fixture
def user_count(db): return len(db["users"])          # fixtures can depend on fixtures

def run_test(test):
    def resolve(name):
        f = PROVIDERS[name]
        return f(*[resolve(p) for p in inspect.signature(f).parameters])
    kwargs = {p: resolve(p) for p in inspect.signature(test).parameters}
    test(**kwargs); print(f"{test.__name__} passed with {sorted(kwargs)}")

def test_users(db, user_count):
    assert user_count == 2 and "riya" in db["users"]
run_test(test_users)
''',
"pythonic_note": "pytest and FastAPI both inject by inspecting function signatures. This toy version shows the mechanism: parameter names are looked up in a provider registry, recursively.",
"examples": [
  {"where": "stdlib", "title": "<code>http.server.HTTPServer(addr, HandlerClass)</code>, <code>json.loads(object_hook=, cls=)</code>", "body": "The server doesn't create a specific handler; you inject the handler class. <code>json</code> and <code>logging</code> (handlers, formatters, filters) accept collaborators as arguments rather than hard-coding them."},
  {"where": "framework", "title": "FastAPI <code>Depends()</code>", "body": "<code>def get_orders(db: Session = Depends(get_db), user = Depends(current_user))</code>: FastAPI calls the providers per request, caches them within the request, and tests swap them with <code>app.dependency_overrides[get_db] = fake_db</code>."},
  {"where": "framework", "title": "pytest fixtures", "body": "Tests declare what they need as parameters (<code>def test_x(tmp_path, client, db_session)</code>) and pytest builds the dependency graph, with scopes (function, module, session) and teardown."},
  {"where": "framework", "title": "Django pluggable backends, dependency-injector library", "body": "Django injects implementations by import path in settings (<code>EMAIL_BACKEND</code>, <code>CACHES</code>, <code>STORAGES</code>); tests switch to <code>locmem</code> email. The <code>dependency-injector</code> package offers containers and providers for large apps."},
  {"where": "production", "title": "Hexagonal / clean architecture services", "body": "Domain services depend on ports (<code>Protocol</code>s for repositories, gateways, clocks); adapters for PostgreSQL, Stripe or Kafka are wired in <code>main.py</code>. Unit tests run in milliseconds with in-memory fakes."}
],
"use": ["Code talks to databases, APIs, clocks, randomness or the filesystem and needs tests", "Implementations differ between environments", "Large applications where wiring should be visible in one place"],
"avoid": ["Injecting pure helpers (<code>math</code>, a formatting function): import them", "Heavy DI containers in small scripts: plain constructor arguments are enough"],
"pitfall": "Using <code>unittest.mock.patch</code> on module paths everywhere instead of injecting. Tests then break whenever an import moves, and they test wiring rather than behaviour. Inject the collaborator and pass a fake.",
"qa": [
  {"q": "What is dependency injection and why use it?", "a": "<p>Providing an object's dependencies from outside (constructor, parameters) instead of creating them inside. Benefits: testability with fakes, configurable implementations, explicit dependencies, and looser coupling.</p>"},
  {"q": "DI vs Service Locator vs Singleton?", "a": "<p>With DI dependencies are pushed in and visible in the signature. A service locator or singleton is pulled from a global inside the code, hiding dependencies and making tests share state.</p>"},
  {"q": "How do you override a dependency in FastAPI tests?", "a": "<p><code>app.dependency_overrides[get_db] = lambda: fake_session</code>, then use <code>TestClient(app)</code>. Every endpoint depending on <code>get_db</code> receives the fake.</p>"}
],
"related": ["abstract-factory", "repository", "singleton", "strategy"]
},

{
"id": "context-manager", "cat": "pythonic", "name": "Context Manager (Execute Around)",
"alias": "Guarantee setup and cleanup around a block of code with <code>with</code>.",
"simple": "A library book: you check it out, read it, and it must go back, even if you spill coffee on it. The <code>with</code> statement is the librarian who makes sure the book is returned no matter what happened while you had it.",
"intent": """<p>Many resources need a paired action: open/close, acquire/release, begin/commit-or-rollback, set/restore. A context manager bundles both halves so the cleanup <b>always</b> runs, including when an exception is raised or the function returns early. It is Python's version of C++ RAII and the "Execute Around" pattern.</p>
<p>Write one as a class with <code>__enter__</code>/<code>__exit__</code>, or as a generator with <code>@contextlib.contextmanager</code> (code before <code>yield</code> is setup, after is cleanup). <code>__exit__</code> receives the exception and may suppress it by returning <code>True</code>. Async versions use <code>async with</code> and <code>__aenter__</code>/<code>__aexit__</code>.</p>""",
"structure": """ with transaction(conn) as tx:        __enter__: BEGIN
     tx.execute(...)                   body
     tx.execute(...)                   __exit__: COMMIT, or ROLLBACK if an exception escaped
 # cleanup guaranteed on success, exception, return or break""",
"code": r'''
import sqlite3, time
from contextlib import contextmanager

@contextmanager
def transaction(conn):
    cur = conn.cursor()
    cur.execute("BEGIN")
    try:
        yield cur
    except Exception:
        conn.rollback(); print("  ROLLBACK")
        raise
    else:
        conn.commit(); print("  COMMIT")

class Timer:
    def __enter__(self):
        self.t0 = time.perf_counter(); return self
    def __exit__(self, exc_type, exc, tb):
        self.ms = (time.perf_counter() - self.t0) * 1000
        print(f"  block took {self.ms:.2f} ms (exception: {exc_type.__name__ if exc_type else None})")
        return False                                  # don't swallow exceptions

conn = sqlite3.connect(":memory:", isolation_level=None)
conn.execute("CREATE TABLE accounts (name TEXT PRIMARY KEY, balance INT CHECK (balance >= 0))")
conn.executemany("INSERT INTO accounts VALUES (?, ?)", [("riya", 500), ("arjun", 100)])

def transfer(src, dst, amount):
    with Timer(), transaction(conn) as cur:
        cur.execute("UPDATE accounts SET balance = balance + ? WHERE name = ?", (amount, dst))
        cur.execute("UPDATE accounts SET balance = balance - ? WHERE name = ?", (amount, src))

transfer("riya", "arjun", 200)
try:
    transfer("arjun", "riya", 1_000)                  # violates CHECK -> rollback
except sqlite3.IntegrityError as e:
    print("  failed:", e)
print(dict(conn.execute("SELECT name, balance FROM accounts")))
''',
"pythonic": r'''
import contextlib, os, tempfile, threading, decimal

lock = threading.Lock()
with lock:                                            # acquire / release
    print("in critical section, locked =", lock.locked())
print("after, locked =", lock.locked())

with contextlib.suppress(FileNotFoundError):          # ignore one specific error
    os.remove("does-not-exist.tmp")

with decimal.localcontext() as ctx:                   # temporarily change settings
    ctx.prec = 5
    print(decimal.Decimal(1) / decimal.Decimal(7))
print(decimal.Decimal(1) / decimal.Decimal(7))

with contextlib.ExitStack() as stack:                 # a dynamic number of resources
    d = stack.enter_context(tempfile.TemporaryDirectory())
    files = [stack.enter_context(open(os.path.join(d, f"part{i}.txt"), "w")) for i in range(3)]
    for f in files: f.write("data")
    print(len(files), "files open")
print("all closed:", all(f.closed for f in files))
''',
"pythonic_note": "The stdlib is full of ready-made context managers: locks, <code>decimal.localcontext</code>, <code>tempfile.TemporaryDirectory</code>, <code>contextlib.suppress</code>, <code>contextlib.chdir</code> (3.11+) and <code>ExitStack</code> for a variable number of resources.",
"examples": [
  {"where": "stdlib", "title": "<code>open()</code>, <code>threading.Lock</code>, <code>sqlite3</code> connections", "body": "Files close, locks release, and a <code>sqlite3</code> connection used in <code>with conn:</code> commits on success or rolls back on exception, even when the block raises."},
  {"where": "stdlib", "title": "<code>contextlib</code>: <code>contextmanager</code>, <code>ExitStack</code>, <code>suppress</code>, <code>redirect_stdout</code>, <code>chdir</code>", "body": "Toolkit for writing and combining context managers. <code>ExitStack</code> is what you use when the number of resources is only known at runtime."},
  {"where": "stdlib", "title": "<code>unittest.mock.patch</code>, <code>decimal.localcontext</code>, <code>warnings.catch_warnings</code>", "body": "Temporarily change global state and reliably restore it at the end of the block, which is essential in tests."},
  {"where": "framework", "title": "SQLAlchemy sessions, Django <code>transaction.atomic()</code>, <code>torch.no_grad()</code>", "body": "<code>with Session(engine) as s, s.begin():</code> commits or rolls back; <code>atomic()</code> wraps a DB transaction or savepoint; <code>no_grad()</code> disables gradient tracking for inference inside the block."},
  {"where": "production", "title": "Distributed locks, spans and temporary infrastructure", "body": "<code>with redis_client.lock('invoice:42', timeout=10):</code> prevents double processing across servers; tracing libraries use <code>with tracer.start_as_current_span('charge'):</code>; test harnesses spin up and tear down containers or devices around a test."}
],
"use": ["Any acquire/release, open/close, begin/commit pair", "Temporarily changing global state (cwd, env vars, settings, mocks)", "Timing, tracing or logging around a block"],
"avoid": ["No cleanup is needed: a plain function call is clearer", "The resource must outlive the block (return it and manage its lifetime elsewhere)"],
"pitfall": "In a <code>@contextmanager</code> generator, putting cleanup after <code>yield</code> without <code>try/finally</code>. If the block raises, the code after <code>yield</code> never runs and the resource leaks.",
"qa": [
  {"q": "What happens in <code>__exit__</code> when an exception occurs?", "a": "<p>It receives <code>(exc_type, exc_value, traceback)</code>. Returning a truthy value suppresses the exception; returning <code>False</code>/<code>None</code> lets it propagate after cleanup. With no exception all three are <code>None</code>.</p>"},
  {"q": "Class-based vs <code>@contextmanager</code>?", "a": "<p>The decorator is shorter for simple setup/teardown (wrap <code>yield</code> in <code>try/finally</code>). A class is better when the manager has state or methods, is reusable, or needs to be re-entrant.</p>"},
  {"q": "What is <code>ExitStack</code> for?", "a": "<p>Managing a dynamic number of context managers (for example opening N files from a list) and registering arbitrary cleanup callbacks; everything is unwound in reverse order when the stack exits.</p>"}
],
"related": ["object-pool", "decorator", "repository"]
},

{
"id": "null-object", "cat": "pythonic", "name": "Null Object",
"alias": "Use a do-nothing object with the right interface instead of <code>None</code> checks.",
"simple": "A mannequin in a shop window wears clothes like a person but never talks or moves. Code that \"dresses\" whoever is in the window works the same whether it's a real model or a mannequin; nobody has to check first.",
"intent": """<p>Code sprinkled with <code>if self.logger is not None:</code> or <code>if user is not None and user.is_admin</code> is noisy and easy to get wrong. A Null Object implements the expected interface with safe, neutral behaviour: log nothing, cache nothing, return an empty list, deny permissions. Callers use it like any real object.</p>
<p>It is great for optional collaborators (loggers, metrics, caches, tracers) and "absent" domain objects (anonymous user, no discount). It should never hide real errors: use it only where "do nothing" is the correct behaviour.</p>""",
"structure": """ Checkout(discount=NoDiscount())      NoDiscount.apply(total) -> total
 Service(metrics=NullMetrics())       NullMetrics.incr(...)  -> does nothing
 request.user = AnonymousUser()       .is_authenticated -> False, .has_perm() -> False""",
"code": r'''
from typing import Protocol

class Metrics(Protocol):
    def incr(self, name: str, value: int = 1) -> None: ...

class PrintMetrics:
    def incr(self, name, value=1): print(f"  metric {name} += {value}")

class NullMetrics:                        # the null object: same interface, no effect
    def incr(self, name, value=1): pass

class Discount(Protocol):
    def apply(self, total: float) -> float: ...

class PercentOff:
    def __init__(self, pct): self.pct = pct
    def apply(self, total): return round(total * (1 - self.pct / 100), 2)

class NoDiscount:                         # null object instead of discount=None
    def apply(self, total): return total

class AnonymousUser:
    is_authenticated = False
    name = "guest"
    def has_perm(self, perm): return False

def checkout(total, user, discount: Discount = NoDiscount(), metrics: Metrics = NullMetrics()):
    metrics.incr("checkout.started")                      # no "if metrics:" anywhere
    final = discount.apply(total)
    can_invoice = user.has_perm("invoice.create")
    return f"{user.name}: pay {final} (invoice allowed: {can_invoice})"

print(checkout(1000, AnonymousUser()))
print(checkout(1000, AnonymousUser(), PercentOff(10), PrintMetrics()))
''',
"pythonic": r'''
import logging, contextlib

# stdlib null object 1: libraries attach NullHandler so they never print unless the app configures logging
lib_log = logging.getLogger("mylib")
lib_log.addHandler(logging.NullHandler())
lib_log.warning("silently ignored unless the app adds a handler")
print("handlers:", [type(h).__name__ for h in lib_log.handlers])

# stdlib null object 2: nullcontext when a lock/transaction is optional
import threading
def update(counter, lock=None):
    with lock or contextlib.nullcontext():       # no if/else around the with-block
        counter["n"] += 1
c = {"n": 0}
update(c); update(c, threading.Lock())
print(c)
''',
"pythonic_note": "<code>logging.NullHandler</code> and <code>contextlib.nullcontext</code> are Null Objects shipped in the stdlib for exactly this purpose.",
"examples": [
  {"where": "stdlib", "title": "<code>logging.NullHandler</code>", "body": "The logging HOWTO recommends that libraries add a <code>NullHandler</code> to their top-level logger, so they stay quiet unless the application configures logging."},
  {"where": "stdlib", "title": "<code>contextlib.nullcontext</code> and <code>os.devnull</code>", "body": "<code>nullcontext()</code> is a context manager that does nothing, used when a real lock or transaction is optional. Writing to <code>os.devnull</code> is the file-system null object for discarding output."},
  {"where": "framework", "title": "Django <code>AnonymousUser</code>", "body": "When nobody is logged in, <code>request.user</code> is an <code>AnonymousUser</code> with <code>is_authenticated = False</code> and <code>has_perm()</code> returning False, so views and templates never check for <code>None</code>."},
  {"where": "framework", "title": "Django <code>DummyCache</code>, OpenTelemetry no-op tracer", "body": "<code>django.core.cache.backends.dummy.DummyCache</code> implements the cache API but stores nothing (handy in development). The OpenTelemetry API returns a no-op tracer when no SDK is configured, so instrumented libraries cost almost nothing."},
  {"where": "production", "title": "Optional integrations and feature flags", "body": "Services inject <code>NullMetrics</code>, <code>NullNotifier</code> or <code>NoDiscount</code> when a feature is disabled or in tests, removing dozens of <code>if enabled:</code> branches from business code."}
],
"use": ["An optional collaborator where \"do nothing\" is correct (logging, metrics, tracing, caching)", "Replacing repeated <code>None</code> checks for an absent domain object"],
"avoid": ["Absence is an error the caller must handle (a missing required config, a missing order)", "It would hide bugs, for example a <code>NullPaymentGateway</code> in production"],
"pitfall": "A null object that silently returns wrong data (e.g. a <code>NullUser</code> with admin rights or a null repository returning an empty list during an outage). Neutral must mean safe, and it must be obvious in configuration when it is active.",
"qa": [
  {"q": "What problem does the Null Object pattern solve?", "a": "<p>It removes repeated <code>None</code> checks by providing an object with the expected interface and harmless behaviour, simplifying callers and preventing <code>AttributeError: 'NoneType' object has no attribute ...</code>.</p>"},
  {"q": "Why should libraries add <code>logging.NullHandler</code>?", "a": "<p>So the library doesn't emit \"No handlers could be found\" warnings or print unexpectedly; the application decides where logs go by configuring handlers on the root or library logger.</p>"},
  {"q": "When is Null Object a bad idea?", "a": "<p>When absence is exceptional and must be handled (raise or return an <code>Optional</code> the caller checks). A silent null object can hide misconfiguration.</p>"}
],
"related": ["strategy", "dependency-injection", "proxy"]
},

{
"id": "mixin", "cat": "pythonic", "name": "Mixin",
"alias": "Small classes that add one reusable capability through multiple inheritance.",
"simple": "Phone accessories: a wireless-charging back, a camera lens clip, a card holder. Each adds one feature to any phone. You combine the ones you need instead of buying a new phone model for every combination.",
"intent": """<p>A mixin is a class not meant to stand alone. It provides one focused capability (JSON serialization, timestamps, login checks, threading) that you add by listing it as a base: <code>class Order(TimestampMixin, JsonMixin, Model)</code>. It relies on the <b>MRO</b> (method resolution order) and cooperative <code>super()</code> calls so several mixins can wrap the same method.</p>
<p>Rules of thumb: mixins have no <code>__init__</code> state of their own (or call <code>super().__init__</code>), put them <b>left</b> of the main base class, and name them <code>...Mixin</code>. Prefer composition when a capability needs its own state or configuration.</p>""",
"structure": """ class ThreadingHTTPServer(ThreadingMixIn, HTTPServer)
 MRO: ThreadingHTTPServer -> ThreadingMixIn -> HTTPServer -> TCPServer -> BaseServer -> object
 ThreadingMixIn.process_request() overrides BaseServer's to run each request in a thread""",
"code": r'''
import json
from datetime import datetime, timezone

class JsonMixin:
    def to_json(self):
        return json.dumps({k: v for k, v in vars(self).items() if not k.startswith("_")}, default=str)

class TimestampMixin:
    def save(self):
        now = datetime(2026, 9, 28, 10, 0, tzinfo=timezone.utc)     # fixed for the demo
        self.created_at = getattr(self, "created_at", now)
        self.updated_at = now
        return super().save()                                        # cooperative

class AuditMixin:
    def save(self):
        print(f"  audit: saving {type(self).__name__}")
        return super().save()

class Model:
    def save(self): print(f"  INSERT {type(self).__name__}"); return self

class Order(AuditMixin, TimestampMixin, JsonMixin, Model):
    def __init__(self, oid, total): self.oid, self.total = oid, total

o = Order("O-5", 1299).save()
print(o.to_json())
print("MRO:", " -> ".join(c.__name__ for c in Order.__mro__))
''',
"pythonic": r'''
import socketserver, http.server

# the stdlib builds its threading HTTP server from a mixin + a base server
print(http.server.ThreadingHTTPServer.__mro__[:3])
print(issubclass(http.server.ThreadingHTTPServer, socketserver.ThreadingMixIn))

# collections.abc mixins: inherit behaviour from a few required methods
from collections.abc import MutableSet
class TagSet(MutableSet):
    def __init__(self, it=()): self._s = {t.lower() for t in it}
    def __contains__(self, x): return x.lower() in self._s
    def __iter__(self): return iter(sorted(self._s))
    def __len__(self): return len(self._s)
    def add(self, x): self._s.add(x.lower())
    def discard(self, x): self._s.discard(x.lower())
tags = TagSet(["Python", "SQL"])
tags |= {"Docker"}                        # |=, -=, isdisjoint, pop... come from the mixin
print(list(tags), "PYTHON" in tags, tags.isdisjoint({"java"}))
''',
"pythonic_note": "<code>http.server.ThreadingHTTPServer</code> is literally <code>ThreadingMixIn</code> + <code>HTTPServer</code>. <code>collections.abc.MutableSet</code> gives you <code>|=</code>, <code>-=</code>, <code>pop</code> and more from five methods.",
"examples": [
  {"where": "stdlib", "title": "<code>socketserver.ThreadingMixIn</code> / <code>ForkingMixIn</code>", "body": "Add concurrency to any socketserver: <code>class ThreadingTCPServer(ThreadingMixIn, TCPServer)</code>. <code>http.server.ThreadingHTTPServer</code> is defined exactly this way."},
  {"where": "stdlib", "title": "<code>collections.abc</code> mixin methods", "body": "<code>Mapping</code>, <code>MutableSequence</code> and <code>MutableSet</code> supply many concrete methods once you implement the abstract ones, which is how you make custom containers behave like built-ins."},
  {"where": "framework", "title": "Django class-based view mixins", "body": "<code>class InvoiceView(LoginRequiredMixin, PermissionRequiredMixin, DetailView)</code> adds authentication and permission checks to a generic view; <code>FormMixin</code>, <code>SingleObjectMixin</code> and <code>ContextMixin</code> build the generic views themselves."},
  {"where": "framework", "title": "Django REST Framework model mixins", "body": "<code>ListModelMixin</code>, <code>CreateModelMixin</code>, <code>RetrieveModelMixin</code> combine with <code>GenericViewSet</code>; <code>ModelViewSet</code> is just all of them together."},
  {"where": "production", "title": "ORM model mixins: timestamps, soft delete, tenancy", "body": "SQLAlchemy and Django projects commonly share <code>TimestampMixin</code> (created_at/updated_at columns), <code>SoftDeleteMixin</code> (deleted_at plus a filtered manager) and <code>TenantMixin</code> across dozens of models."}
],
"use": ["The same small capability is needed across unrelated classes", "Frameworks designed for composition by mixins (Django CBVs, DRF, socketserver)"],
"avoid": ["The capability needs its own state and configuration: use composition", "Long mixin lists whose methods interact in surprising MRO order"],
"pitfall": "Not calling <code>super()</code> in a mixin method: the chain stops and later mixins or the base class never run (in the example, removing <code>super().save()</code> from <code>AuditMixin</code> would skip timestamps and the INSERT).",
"qa": [
  {"q": "What is the MRO and how does Python compute it?", "a": "<p>The method resolution order is the sequence of classes searched for attributes. Python uses the C3 linearization: children before parents, left-to-right base order preserved, each class once. See it with <code>Cls.__mro__</code>.</p>"},
  {"q": "Why do mixins go to the left of the base class?", "a": "<p>So their methods come first in the MRO and can override and extend the base's methods via <code>super()</code>. <code>class V(LoginRequiredMixin, View)</code> runs the login check before <code>View.dispatch</code>.</p>"},
  {"q": "Mixin vs composition?", "a": "<p>Mixins share behaviour through inheritance and are convenient for small stateless capabilities. Composition (holding a collaborator) is better for stateful or configurable behaviour and avoids MRO surprises.</p>"}
],
"related": ["template-method", "decorator", "registry"]
},

{
"id": "repository", "cat": "pythonic", "name": "Repository & Unit of Work",
"alias": "Hide persistence behind a collection-like interface, and commit a batch of changes atomically.",
"simple": "A library catalogue: you ask the librarian \"get me the book with ID 42\" or \"add this book\". You don't know whether books are in the basement, a warehouse or on loan. The Unit of Work is the checkout desk: all the books you borrow in one visit are recorded together, or not at all.",
"intent": """<p>A <b>Repository</b> gives domain code a simple, collection-like API (<code>add</code>, <code>get</code>, <code>list_by_customer</code>) and hides SQL, ORMs and HTTP storage behind it. Business logic becomes testable with an in-memory fake repository.</p>
<p>A <b>Unit of Work</b> tracks everything changed during one business operation and commits it atomically at the end (or rolls back). It usually also owns the repositories, so a use case reads: <code>with uow: order = uow.orders.get(id); order.ship(); uow.commit()</code>. These two patterns are the heart of Cosmic Python's architecture.</p>""",
"structure": """ service: with uow:                          SqlUnitOfWork -> session/transaction
            order = uow.orders.get("O-9")      SqlOrderRepository -> SELECT ...
            order.ship()                       (changes tracked)
            uow.commit()                       COMMIT (or ROLLBACK on error)
 tests:   FakeUnitOfWork + dict-based FakeOrderRepository""",
"code": r'''
import sqlite3
from dataclasses import dataclass

@dataclass
class Order:
    id: str; customer: str; status: str = "PAID"
    def ship(self):
        if self.status != "PAID": raise ValueError(f"cannot ship {self.status} order")
        self.status = "SHIPPED"

# ---- repository: collection-like API, SQL hidden inside
class SqlOrderRepository:
    def __init__(self, conn): self.conn, self.seen = conn, {}
    def add(self, o): self.conn.execute("INSERT INTO orders VALUES (?,?,?)", (o.id, o.customer, o.status)); self.seen[o.id] = o
    def get(self, oid):
        row = self.conn.execute("SELECT id, customer, status FROM orders WHERE id=?", (oid,)).fetchone()
        o = Order(*row); self.seen[oid] = o; return o          # identity map, simplified

# ---- unit of work: one transaction per business operation
class SqlUnitOfWork:
    def __init__(self, conn): self.conn = conn
    def __enter__(self):
        self.orders = SqlOrderRepository(self.conn); self.conn.execute("BEGIN"); return self
    def commit(self):
        for o in self.orders.seen.values():                  # flush tracked changes
            self.conn.execute("UPDATE orders SET status=? WHERE id=?", (o.status, o.id))
        self.conn.execute("COMMIT"); self.committed = True
    def __exit__(self, exc_type, *_):
        if not getattr(self, "committed", False): self.conn.execute("ROLLBACK")
        self.committed = False

def ship_order(uow, oid):                                    # service layer: no SQL here
    with uow:
        order = uow.orders.get(oid)
        order.ship()
        uow.commit()

conn = sqlite3.connect(":memory:", isolation_level=None)
conn.execute("CREATE TABLE orders (id TEXT PRIMARY KEY, customer TEXT, status TEXT)")
uow = SqlUnitOfWork(conn)
with uow:
    uow.orders.add(Order("O-9", "riya")); uow.orders.add(Order("O-10", "arjun", "PENDING")); uow.commit()

ship_order(uow, "O-9")
try:
    ship_order(uow, "O-10")
except ValueError as e:
    print("rejected:", e)
print(conn.execute("SELECT * FROM orders").fetchall())
''',
"pythonic": r'''
from dataclasses import dataclass

@dataclass
class Order:
    id: str; status: str = "PAID"
    def ship(self): self.status = "SHIPPED"

class FakeRepo:                                   # in-memory repository for unit tests
    def __init__(self, *orders): self._d = {o.id: o for o in orders}
    def get(self, oid): return self._d[oid]

class FakeUoW:
    def __init__(self, repo): self.orders, self.committed = repo, False
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def commit(self): self.committed = True

def ship_order(uow, oid):                         # the SAME service function as production
    with uow:
        uow.orders.get(oid).ship(); uow.commit()

uow = FakeUoW(FakeRepo(Order("O-1")))
ship_order(uow, "O-1")
print(uow.orders.get("O-1").status, "committed:", uow.committed, "(no database needed)")
''',
"pythonic_note": "The payoff: the service function runs unchanged against an in-memory fake, so business rules are tested in microseconds without a database.",
"examples": [
  {"where": "stdlib", "title": "<code>sqlite3</code> transactions and <code>shelve</code>", "body": "A <code>sqlite3</code> connection used as a context manager commits or rolls back a batch of statements together, a minimal unit of work. <code>shelve</code> offers a dict-like persistent store: a repository-style interface over <code>dbm</code> files."},
  {"where": "framework", "title": "SQLAlchemy <code>Session</code>", "body": "SQLAlchemy's documentation describes the Session as implementing the Unit of Work pattern with an identity map: it tracks new, dirty and deleted objects and flushes them in the right order within one transaction on <code>commit()</code>."},
  {"where": "framework", "title": "Django managers and QuerySets", "body": "<code>Order.objects</code> is a repository-like entry point; custom managers (<code>Order.objects.overdue()</code>) keep query logic out of views. <code>transaction.atomic()</code> supplies the unit-of-work boundary."},
  {"where": "production", "title": "\"Architecture Patterns with Python\" (Cosmic Python)", "body": "Harry Percival and Bob Gregory's book (O'Reilly, 2020, free online as cosmicpython.com) builds a Flask + SQLAlchemy service around Repository, Unit of Work, service layer and domain events, and is the standard Python reference for these patterns."},
  {"where": "production", "title": "Swapping storage without touching business logic", "body": "Teams move an aggregate from PostgreSQL to DynamoDB, or add a Redis read-through cache, by writing a new repository class. Services and tests stay the same."}
],
"use": ["Non-trivial domain logic you want to test without a database", "Several storage backends, or likely future migration", "Operations that change several objects and must commit atomically"],
"avoid": ["Simple CRUD apps where the ORM already is a fine repository", "Wrapping every ORM feature: you end up rebuilding the ORM badly"],
"pitfall": "Leaky repositories that return ORM query objects or raw rows. Callers then depend on SQLAlchemy/Django anyway. Return domain objects, and put transaction control in the unit of work, not scattered <code>commit()</code> calls inside repositories.",
"qa": [
  {"q": "What is the Repository pattern?", "a": "<p>An abstraction over persistence that looks like an in-memory collection of domain objects (<code>add</code>, <code>get</code>, queries by business meaning). It decouples domain logic from the database and makes testing with fakes easy.</p>"},
  {"q": "What does Unit of Work add?", "a": "<p>A boundary for one business operation: it tracks changes and commits them atomically or rolls back, and gives the service one object that provides repositories and transaction control.</p>"},
  {"q": "Isn't Django's ORM already a repository?", "a": "<p>Largely, yes, and for many apps that's enough. A separate repository layer pays off when domain logic is complex, you want very fast unit tests, or you need to hide which store is used.</p>"}
],
"related": ["dependency-injection", "context-manager", "facade"]
},

{
"id": "pipeline", "cat": "pythonic", "name": "Generator Pipeline",
"alias": "Chain small lazy stages so data streams through them one item at a time.",
"simple": "A car-wash tunnel: soap, brushes, rinse, dry. Each car moves through every station, and many cars are inside at once at different stations. No station waits for all cars of the day before starting.",
"intent": """<p>A pipeline is a series of stages, each taking an iterable and yielding transformed items: read, parse, filter, enrich, batch, write. Built from generators, it processes one item at a time, so memory stays constant regardless of input size, and stages are small, testable and reorderable.</p>
<p>The idea is the Unix pipe (<code>cat | grep | sort</code>) expressed in Python. Libraries lift the same concept to ML (scikit-learn Pipeline), dataframes (<code>df.pipe</code>) and distributed processing (Apache Beam).</p>""",
"structure": """ read_lines(path) -> parse_json -> only(status=500) -> enrich(geo) -> batched(500) -> write_db
    each stage: def stage(items): for x in items: ... yield y
    memory: O(batch size), not O(file size)""",
"code": r'''
import json, itertools, io, collections

RAW = io.StringIO("\n".join(json.dumps(r) for r in [
    {"ts": "10:00", "path": "/checkout", "status": 200, "ms": 120},
    {"ts": "10:01", "path": "/checkout", "status": 500, "ms": 3000},
    "not json at all",
    {"ts": "10:02", "path": "/search",   "status": 500, "ms": 800},
    {"ts": "10:03", "path": "/checkout", "status": 502, "ms": 2500},
    {"ts": "10:04", "path": "/login",    "status": 200, "ms": 90},
]))

def read_lines(f):
    for line in f:
        yield line.strip()

def parse(lines, errors):
    for line in lines:
        try:
            rec = json.loads(line)
            if isinstance(rec, dict): yield rec
            else: errors["not an object"] += 1
        except json.JSONDecodeError:
            errors["bad json"] += 1

def server_errors(records):
    return (r for r in records if r["status"] >= 500)

def enrich(records):
    for r in records:
        yield {**r, "slow": r["ms"] > 1000}

def write(batches):
    for i, batch in enumerate(batches, 1):
        print(f"  batch {i}: INSERT {len(batch)} rows ->", [(r["path"], r["status"]) for r in batch])

errors = collections.Counter()
stream = enrich(server_errors(parse(read_lines(RAW), errors)))   # nothing has run yet
write(itertools.batched(stream, 2))                               # pulling drives the pipeline
print("skipped:", dict(errors))
''',
"pythonic": r'''
from functools import reduce

def compose(*stages):
    return lambda data: reduce(lambda acc, stage: stage(acc), stages, data)

strip   = lambda xs: (x.strip() for x in xs)
nonempty = lambda xs: (x for x in xs if x)
upper   = lambda xs: (x.upper() for x in xs)

clean = compose(strip, nonempty, upper)          # reusable, reorderable pipeline
print(list(clean(["  pune ", "", " bengaluru", "   "])))
''',
"pythonic_note": "Stages are plain functions from iterable to iterable, so composing them is a one-line <code>reduce</code>.",
"examples": [
  {"where": "stdlib", "title": "Generators, <code>itertools</code>, file iteration", "body": "Generator expressions, <code>filter</code>, <code>map</code>, <code>itertools.batched</code>, <code>groupby</code> and <code>islice</code> are pipeline stages; file objects and <code>csv.reader</code> are sources. David Beazley's \"Generator Tricks for Systems Programmers\" talk popularized this style."},
  {"where": "stdlib", "title": "<code>subprocess</code> pipes", "body": "Connecting <code>Popen(..., stdout=PIPE)</code> into another process's <code>stdin</code> builds a real OS-level pipeline from Python, the same model as a shell <code>|</code>."},
  {"where": "framework", "title": "scikit-learn <code>Pipeline</code> / <code>make_pipeline</code>", "body": "<code>make_pipeline(SimpleImputer(), StandardScaler(), LogisticRegression())</code> chains preprocessing and model so the exact same steps run in training, cross-validation and prediction, which prevents data leakage."},
  {"where": "framework", "title": "pandas <code>.pipe()</code> and Apache Beam", "body": "<code>df.pipe(clean).pipe(add_features).pipe(aggregate)</code> keeps dataframe transformations readable. Beam's Python SDK writes <code>p | ReadFromText(...) | beam.Map(parse) | beam.Filter(...)</code> and runs it on Dataflow or Spark."},
  {"where": "production", "title": "Log processing and ETL", "body": "Jobs that scan gigabytes of logs or export millions of DB rows stream through parse, filter, enrich and batch-write stages. They run in constant memory and any stage can be unit-tested with a short list."}
],
"use": ["Large or unbounded data processed in stages", "You want each transformation small, testable and reusable", "ETL, log analysis, data cleaning, ML preprocessing"],
"avoid": ["A stage needs all data at once (global sort, median): materialize explicitly there", "Tiny data where a list comprehension is simpler"],
"pitfall": "Error handling inside lazy stages: an exception surfaces only when the consumer pulls the bad item, far from where the stage was built. Handle and count bad records inside the stage (as <code>parse</code> does) rather than letting one bad line kill a 10-hour job.",
"qa": [
  {"q": "Why use generators for data pipelines?", "a": "<p>They are lazy: each item flows through all stages before the next is read, so memory stays constant, work starts immediately, and you can stop early. Stages are simple functions that are easy to test and combine.</p>"},
  {"q": "What does <code>yield from</code> do?", "a": "<p>Delegates to a sub-iterator, yielding all its values (and passing <code>send</code>/<code>throw</code> through). It is useful for flattening nested sources, for example reading many files in one stage.</p>"},
  {"q": "Why use scikit-learn's Pipeline instead of calling steps manually?", "a": "<p>It guarantees preprocessing is fitted only on training folds during cross-validation (no leakage), bundles the whole workflow into one estimator for grid search and deployment, and keeps training and serving identical.</p>"}
],
"related": ["iterator", "chain-of-responsibility", "composite"]
},

{
"id": "lazy", "cat": "pythonic", "name": "Lazy Initialization",
"alias": "Delay creating or computing something expensive until it is first needed, then keep it.",
"simple": "A hotel doesn't cook breakfast for every room at 6 am. It cooks when a guest orders, and if you order a second coffee, the pot that's already brewed is used. Nobody pays for food that no one eats.",
"intent": """<p>Many objects hold expensive parts that aren't always used: an ML model, a parsed config, a DB connection, a big lookup table, a slow import. Lazy initialization creates them on first access and caches the result, which speeds up startup (important for CLIs, serverless functions and tests) and avoids wasted work.</p>
<p>Python tools: <code>functools.cached_property</code> (compute once per instance), <code>functools.cache</code> (per argument), module-level <code>__getattr__</code> (PEP 562) for lazy module attributes and imports, and <code>importlib.util.LazyLoader</code>. Thread safety of the first initialization needs attention in multi-threaded servers.</p>""",
"structure": """ report.stats   first access -> compute (2 s) -> stored in report.__dict__["stats"]
 report.stats   later access -> plain attribute lookup (ns), no recompute
 del report.stats -> invalidates, next access recomputes""",
"code": r'''
import time
from functools import cached_property

class SalesReport:
    def __init__(self, rows): self.rows = rows

    @cached_property
    def stats(self):                               # expensive, computed on first access
        print("  computing stats (slow)...")
        time.sleep(0.05)
        totals = [r["total"] for r in self.rows]
        return {"count": len(totals), "sum": sum(totals), "max": max(totals)}

    @property
    def average(self):                             # cheap derived value built on the lazy one
        return self.stats["sum"] / self.stats["count"]

r = SalesReport([{"total": t} for t in (120, 80, 400, 250)])
print("created report (nothing computed yet)")
t0 = time.perf_counter(); print(r.stats, f"{(time.perf_counter() - t0) * 1000:.0f} ms")
t0 = time.perf_counter(); print(r.average, f"{(time.perf_counter() - t0) * 1000:.3f} ms")
r.rows.append({"total": 1000})
del r.stats                                        # invalidate the cache explicitly
print(r.stats)
''',
"pythonic": r'''
import sys, types

# PEP 562: module-level __getattr__ makes attributes (or heavy imports) lazy
mod = types.ModuleType("analytics")
exec("""
_loaded = {}
def __getattr__(name):
    if name == "model":
        print("  loading 500 MB model on first use...")
        _loaded[name] = {"weights": "..."}
        globals()[name] = _loaded[name]       # cache: next access skips __getattr__
        return _loaded[name]
    raise AttributeError(name)
""", mod.__dict__)
sys.modules["analytics"] = mod

import analytics
print("imported analytics (fast)")
print(analytics.model); print(analytics.model)   # loads once

import concurrent.futures as cf                   # the stdlib uses the same trick
print("ProcessPoolExecutor" in cf.__dict__, hasattr(cf, "__getattr__"))
''',
"pythonic_note": "<code>concurrent.futures</code> itself uses a module <code>__getattr__</code> so that importing the package doesn't eagerly import the process-pool machinery.",
"examples": [
  {"where": "stdlib", "title": "<code>functools.cached_property</code> and <code>functools.cache</code>", "body": "<code>cached_property</code> stores the computed value in the instance <code>__dict__</code> on first access (delete the attribute to invalidate). <code>cache</code>/<code>lru_cache</code> make any pure function compute each input once."},
  {"where": "stdlib", "title": "Module <code>__getattr__</code> (PEP 562) and <code>importlib.util.LazyLoader</code>", "body": "<code>concurrent.futures</code> exposes <code>ProcessPoolExecutor</code> and <code>ThreadPoolExecutor</code> through a module-level <code>__getattr__</code> that imports them on first access. <code>LazyLoader</code> defers executing a module until an attribute is touched."},
  {"where": "framework", "title": "Django <code>gettext_lazy</code>, lazy QuerySets, <code>SimpleLazyObject</code>", "body": "Translated strings in models are evaluated when rendered (so the active language is right), QuerySets hit the database only when iterated, and <code>request.user</code> loads only if used."},
  {"where": "framework", "title": "Scientific CLIs and lazy-loader packages", "body": "scikit-image and other Scientific Python projects adopted the <code>lazy_loader</code> package (SPEC 1) so <code>import skimage</code> doesn't import every submodule up front, which noticeably cuts import time."},
  {"where": "production", "title": "Serverless cold starts and ML services", "body": "AWS Lambda handlers and model-serving APIs load the model or DB client on first request (then reuse it across invocations in the same container), keeping cold starts and unused-code paths cheap."}
],
"use": ["Expensive resources that aren't always used", "Faster startup for CLIs, tests and serverless functions", "Values derived from immutable data (safe to cache)"],
"avoid": ["The value depends on data that changes: the cache goes stale silently", "Failures should surface at startup (bad config), not on the first unlucky request"],
"pitfall": "<code>cached_property</code> on mutable data: after <code>rows</code> changes, <code>stats</code> is stale until you <code>del obj.stats</code>. Also, first-time initialization can race in threaded servers: guard it with a lock if creation must happen once.",
"qa": [
  {"q": "<code>property</code> vs <code>cached_property</code>?", "a": "<p><code>property</code> recomputes on every access. <code>cached_property</code> computes once and stores the result as an instance attribute (it is a non-data descriptor, so the instance attribute then wins). It needs an instance <code>__dict__</code>, so it doesn't work with <code>__slots__</code>-only classes.</p>"},
  {"q": "How can you speed up a slow Python CLI start?", "a": "<p>Measure with <code>python -X importtime</code>, then move heavy imports inside the functions that need them, use module <code>__getattr__</code> or <code>LazyLoader</code> for optional submodules, and cache expensive setup lazily.</p>"},
  {"q": "What are the risks of lazy initialization?", "a": "<p>Unpredictable latency on first use, errors surfacing late, stale caches when underlying data changes, and races on first initialization under concurrency.</p>"}
],
"related": ["proxy", "singleton", "flyweight"]
},

]
