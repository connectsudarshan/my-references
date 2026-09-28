PATTERNS = [

{
"id": "singleton", "cat": "creational", "name": "Singleton",
"alias": "Exactly one instance of a class, with a global access point.",
"simple": "A country has one president at a time. Everyone who says \"call the president\" reaches the same person. Asking for a \"new\" president while one is in office just gives you the current one.",
"intent": """<p>Guarantee a class has a single instance and give everyone the same way to reach it. Typical uses are objects that model something unique: the app's configuration, a process-wide cache, a hardware device handle.</p>
<p>In Python the cleanest singleton is usually <b>a module</b>: modules run once and are cached in <code>sys.modules</code>, so every <code>import config</code> returns the same object. When you need a class (for lazy creation or subclassing), override <code>__new__</code> or use a metaclass, and add a lock if threads may race on first creation.</p>""",
"structure": """  caller A --.                      +---------------------+
             +--> AppConfig() ----> | _instance (cached)  |  <- created once
  caller B --'   (same object)      +---------------------+""",
"code": r'''
import threading

class SingletonMeta(type):
    """Metaclass: every class using it gets exactly one instance."""
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:              # fast path, no lock
            with cls._lock:                        # double-checked locking
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class AppConfig(metaclass=SingletonMeta):
    def __init__(self):
        print("loading config once...")
        self.settings = {"db_url": "postgres://db/prod", "debug": False}

def worker(results):
    results.append(id(AppConfig()))

results = []
threads = [threading.Thread(target=worker, args=(results,)) for _ in range(8)]
for t in threads: t.start()
for t in threads: t.join()

print("distinct instances across 8 threads:", len(set(results)))
a, b = AppConfig(), AppConfig()
b.settings["debug"] = True
print("a is b:", a is b, "| a sees b's change:", a.settings["debug"])
''',
"pythonic": r'''
# config.py would normally be its own file; we fake that with types.ModuleType
import sys, types

config = types.ModuleType("config")
config.settings = {"db_url": "postgres://db/prod"}
sys.modules["config"] = config           # what the import system does on first import

import config as c1                      # anywhere in the program...
import config as c2                      # ...always the same module object
c1.settings["debug"] = True
print(c1 is c2, c2.settings)

# The standard library does this too: module-level functions share one hidden instance
import random
print(random.random.__self__ is random.randint.__self__)   # both bound to random._inst
''',
"pythonic_note": "Most Python code never writes a singleton class. A module is already a singleton, and the standard library uses exactly this trick.",
"examples": [
  {"where": "stdlib", "title": "<code>None</code>, <code>True</code>, <code>False</code>, <code>Ellipsis</code>, <code>NotImplemented</code>", "body": "The interpreter creates each of these once. That is why <code>x is None</code> is the correct test: there is only one <code>None</code> object to compare identity with."},
  {"where": "stdlib", "title": "<code>random</code> module's hidden instance", "body": "<code>random.py</code> creates <code>_inst = Random()</code> at import and binds <code>random()</code>, <code>randint()</code>, <code>shuffle()</code> and friends to it. Calling <code>random.seed(42)</code> therefore affects every caller in the process."},
  {"where": "stdlib", "title": "<code>logging.getLogger(name)</code>", "body": "Returns the same Logger object for the same name every time (a per-name singleton, sometimes called a Multiton). Configure <code>getLogger('payments')</code> once in <code>main</code> and every module that asks for it gets the configured logger."},
  {"where": "framework", "title": "Django <code>settings</code>", "body": "<code>django.conf.settings</code> is one module-level <code>LazySettings</code> instance. It loads your settings module on first attribute access and every app reads from that one object."},
  {"where": "production", "title": "Per-process clients: DB engine, Redis, boto3 session", "body": "Web services create one SQLAlchemy <code>Engine</code> or Redis client per process and share it, because each owns a connection pool. Creating one per request exhausts database connections under load."}
],
"use": ["The domain really has one of something (config, device handle, process-wide registry)", "An expensive shared resource must be created once per process (connection pool, loaded ML model)"],
"avoid": ["You only want to avoid passing an argument around: that is a hidden global and makes tests share state", "You need different instances in tests or per tenant; inject the object instead", "Across processes: each worker process (gunicorn, multiprocessing) gets its own copy"],
"pitfall": "Overriding <code>__new__</code> but not <code>__init__</code>: <code>__init__</code> still runs on every <code>AppConfig()</code> call and silently resets state. The metaclass version above avoids this because <code>__call__</code> skips both.",
"qa": [
  {"q": "How do you implement a singleton in Python? Which way do you prefer?", "a": "<p>Options: a module (simplest, preferred), overriding <code>__new__</code>, a metaclass overriding <code>__call__</code>, or a decorator that caches the instance. I prefer a module, or a metaclass when I need a class with lazy init. Add a lock for thread-safe first creation.</p>"},
  {"q": "Is a singleton thread-safe in Python?", "a": "<p>Module import is protected by the import lock, so module singletons are safe. A class-based singleton can race on first creation (two threads both see no instance). Use double-checked locking with <code>threading.Lock</code> as shown. Note that free-threaded Python (3.13t+, no GIL) makes this even more important.</p>"},
  {"q": "Why do many people call Singleton an anti-pattern?", "a": "<p>It is global mutable state: hidden dependencies, order-dependent tests, and hard-to-replace collaborators. The fix is usually dependency injection: create one instance at startup and pass it in.</p>"}
],
"related": ["lazy", "object-pool", "dependency-injection", "flyweight"]
},

{
"id": "factory-method", "cat": "creational", "name": "Factory Method",
"alias": "Let a method (often overridable) decide which concrete class to instantiate.",
"simple": "You order \"a coffee\" at the counter. You don't go into the kitchen and pick the machine. The barista (factory) decides whether it comes from the espresso machine or the filter pot based on what you asked.",
"intent": """<p>Callers ask for an object through a method instead of calling a concrete class directly. The method (or a subclass override of it) decides the concrete type. This decouples client code from the classes it uses and gives you one place to change the decision.</p>
<p>In Python, two forms are everywhere: <b>overridable hook methods</b> such as <code>get_serializer_class()</code> in a base class, and <b>alternate constructors</b> as <code>@classmethod</code>s such as <code>datetime.fromtimestamp()</code>. A plain function that returns different classes is a simple factory and is fine for most code.</p>""",
"structure": """ Exporter (base)                    create_writer() is the factory method
   export(): w = self.create_writer(); w.write(rows)
       ^                      ^
 CsvExporter              JsonExporter
   create_writer()->CsvWriter   create_writer()->JsonWriter""",
"code": r'''
import csv, io, json
from abc import ABC, abstractmethod

class Exporter(ABC):
    """export() is fixed; subclasses decide WHICH writer to create."""
    def export(self, rows):
        out = io.StringIO()
        writer = self.create_writer(out)          # <-- factory method
        writer(rows)
        return out.getvalue()

    @abstractmethod
    def create_writer(self, out): ...

class CsvExporter(Exporter):
    def create_writer(self, out):
        def write(rows):
            w = csv.DictWriter(out, fieldnames=rows[0].keys(), lineterminator="\n")
            w.writeheader(); w.writerows(rows)
        return write

class JsonExporter(Exporter):
    def create_writer(self, out):
        return lambda rows: json.dump(rows, out)

EXPORTERS = {"csv": CsvExporter, "json": JsonExporter}

def exporter_for(fmt: str) -> Exporter:         # simple factory keyed by config
    return EXPORTERS[fmt]()

rows = [{"sku": "A1", "qty": 3}, {"sku": "B7", "qty": 1}]
for fmt in ("csv", "json"):
    print(f"--- {fmt}")
    print(exporter_for(fmt).export(rows).strip())
''',
"pythonic": r'''
from datetime import datetime, timezone
from dataclasses import dataclass

@dataclass
class Money:
    cents: int
    currency: str

    @classmethod                               # alternate constructor = named factory
    def from_string(cls, text: str) -> "Money":
        amount, cur = text.split()
        return cls(round(float(amount) * 100), cur)

print(Money.from_string("19.99 USD"))
print(datetime.fromtimestamp(0, tz=timezone.utc))   # stdlib alternate constructor
print(dict.fromkeys(["a", "b"], 0))                 # another one
print(int.from_bytes(b"\x01\x00", "little"))
''',
"pythonic_note": "Classes are callables, so a dict of classes is already a factory. For different input formats, add <code>@classmethod</code> alternate constructors named <code>from_*</code>.",
"examples": [
  {"where": "stdlib", "title": "<code>pathlib.Path(...)</code>", "body": "Calling <code>Path('data.csv')</code> returns a <code>WindowsPath</code> on Windows and a <code>PosixPath</code> elsewhere. <code>Path.__new__</code> picks the concrete class so your code never has to."},
  {"where": "stdlib", "title": "Alternate constructors: <code>datetime.fromisoformat</code>, <code>dict.fromkeys</code>, <code>int.from_bytes</code>", "body": "Classmethods named <code>from_*</code> are the standard Python idiom for \"another way to build this object\". <code>Decimal.from_float</code> and <code>bytes.fromhex</code> follow it too."},
  {"where": "stdlib", "title": "<code>logging.setLogRecordFactory()</code>", "body": "Logging creates every record through a replaceable factory. Services use it to attach a request ID or tenant ID to every <code>LogRecord</code> without touching any logging call."},
  {"where": "framework", "title": "Django REST Framework <code>get_serializer_class()</code>", "body": "<code>GenericAPIView</code> calls this hook to pick the serializer. A viewset overrides it to return a light <code>OrderListSerializer</code> for list views and a detailed one for retrieve, while the base class keeps all request handling."},
  {"where": "framework", "title": "Django <code>Manager.get_queryset()</code> and <code>FormMixin.get_form_class()</code>", "body": "Custom managers override <code>get_queryset()</code> (for example to hide soft-deleted rows); class-based views override <code>get_form_class()</code> to choose a form per user role."}
],
"use": ["The exact class depends on config, input or platform", "A framework base class must let subclasses choose a collaborator", "An object can be built from several input formats (<code>from_json</code>, <code>from_row</code>)"],
"avoid": ["There is only one concrete type; call the class", "A deep class hierarchy only to pick between two classes: a dict or a function is enough"],
"pitfall": "Growing an <code>if/elif</code> chain inside the factory for every new type. Use a registry dict (or <code>__init_subclass__</code> registration) so adding a type does not edit the factory.",
"qa": [
  {"q": "Factory Method vs simple factory vs Abstract Factory?", "a": "<p><b>Simple factory</b>: a function/dict returning one of several classes. <b>Factory Method</b>: an overridable method in a base class; subclasses decide the product. <b>Abstract Factory</b>: an object that creates a whole family of related products that must match.</p>"},
  {"q": "What is an alternate constructor in Python?", "a": "<p>A <code>@classmethod</code> that builds an instance from a different input, returning <code>cls(...)</code>. Because it uses <code>cls</code>, subclasses automatically get instances of the subclass. Examples: <code>datetime.fromtimestamp</code>, <code>dict.fromkeys</code>.</p>"},
  {"q": "Why use <code>cls(...)</code> instead of the class name inside a classmethod factory?", "a": "<p>So the factory respects inheritance: <code>SubMoney.from_string()</code> returns a <code>SubMoney</code>, not the base class.</p>"}
],
"related": ["abstract-factory", "registry", "template-method", "prototype"]
},

{
"id": "abstract-factory", "cat": "creational", "name": "Abstract Factory",
"alias": "Create families of related objects that must be used together, without naming concrete classes.",
"simple": "IKEA sells furniture in styles. If you pick the \"Scandinavian\" catalogue, the chair, table and lamp all match. You never end up with a Scandinavian chair and a Baroque table because you only ever order from one catalogue at a time.",
"intent": """<p>An abstract factory is an object with several creation methods (<code>create_queue()</code>, <code>create_storage()</code>, ...). Each concrete factory returns a <b>matching set</b> of products. Client code receives one factory and never mixes families by accident.</p>
<p>Use it when products come in families: one per cloud provider, per database backend, per UI theme, or "real" vs "fake" for tests.</p>""",
"structure": """ CloudFactory:  create_storage()  create_queue()
     |                        |
 AwsFactory -> S3Storage, SqsQueue
 LocalFactory -> DiskStorage, MemoryQueue      (for tests / laptops)
 app code:  f = factory_for(env);  f.create_storage().put(...)""",
"code": r'''
from abc import ABC, abstractmethod
from collections import deque

# ---- product interfaces
class Storage(ABC):
    @abstractmethod
    def put(self, key, data): ...
class Queue(ABC):
    @abstractmethod
    def send(self, msg): ...

# ---- family 1: "cloud" (stubs that just print)
class S3Storage(Storage):
    def put(self, key, data): print(f"S3 PUT s3://bucket/{key} ({len(data)} bytes)")
class SqsQueue(Queue):
    def send(self, msg): print(f"SQS send -> {msg}")

# ---- family 2: local, used in tests and on laptops
class DiskStorage(Storage):
    def __init__(self): self.files = {}
    def put(self, key, data): self.files[key] = data; print(f"disk write {key}")
class MemoryQueue(Queue):
    def __init__(self): self.q = deque()
    def send(self, msg): self.q.append(msg); print(f"memory queue size={len(self.q)}")

# ---- the abstract factory and its concrete factories
class InfraFactory(ABC):
    @abstractmethod
    def create_storage(self) -> Storage: ...
    @abstractmethod
    def create_queue(self) -> Queue: ...

class AwsFactory(InfraFactory):
    def create_storage(self): return S3Storage()
    def create_queue(self): return SqsQueue()

class LocalFactory(InfraFactory):
    def create_storage(self): return DiskStorage()
    def create_queue(self): return MemoryQueue()

def upload_invoice(factory: InfraFactory, invoice_id: str, pdf: bytes):
    """Business code: knows nothing about AWS or disks."""
    factory.create_storage().put(f"invoices/{invoice_id}.pdf", pdf)
    factory.create_queue().send({"event": "InvoiceStored", "id": invoice_id})

for env, factory in {"prod": AwsFactory(), "test": LocalFactory()}.items():
    print(f"[{env}]"); upload_invoice(factory, "INV-42", b"%PDF-1.7 ...")
''',
"examples": [
  {"where": "stdlib", "title": "<code>xml.dom</code> implementations", "body": "<code>xml.dom.getDOMImplementation()</code> returns an implementation object whose <code>createDocument()</code> and <code>createDocumentType()</code> build nodes that belong together (minidom nodes only work with minidom documents)."},
  {"where": "framework", "title": "Django database backends", "body": "Each backend's <code>DatabaseWrapper</code> declares a family: <code>ops_class</code>, <code>features_class</code>, <code>introspection_class</code>, <code>creation_class</code>, <code>client_class</code>. Switching <code>ENGINE</code> from PostgreSQL to SQLite swaps the whole matching set."},
  {"where": "framework", "title": "SQLAlchemy dialects", "body": "A <code>Dialect</code> supplies a matching SQL compiler, DDL compiler, type compiler and identifier preparer. The PostgreSQL dialect's pieces all agree on quoting and types; you never get a MySQL compiler with a PostgreSQL type map."},
  {"where": "production", "title": "Multi-cloud or on-prem products", "body": "Products sold to customers on AWS, Azure and on-prem ship an <code>AwsFactory</code>, <code>AzureFactory</code> and <code>OnPremFactory</code> producing storage, queue and secrets clients. The business logic has no cloud-specific imports."},
  {"where": "production", "title": "Test doubles for a hardware abstraction layer", "body": "Firmware test rigs swap a <code>RealDeviceFactory</code> (NVMe controller, power relay, UART) for a <code>SimulatedDeviceFactory</code>, so the same test scripts run in CI without hardware."}
],
"use": ["Objects come in families that must match (cloud provider, DB backend, theme)", "You want one switch to change the whole environment (prod vs local vs test)"],
"avoid": ["Only one product type varies: use Factory Method", "Families rarely change; every new product type means editing every factory"],
"pitfall": "Creating the factory deep inside business code (<code>AwsFactory()</code> inline). Pick the factory once at startup from config and pass it in, or the abstraction buys nothing.",
"qa": [
  {"q": "When would you choose Abstract Factory over Factory Method?", "a": "<p>When you must create <b>several related products</b> that have to be consistent with each other. Factory Method varies one product through subclassing; Abstract Factory varies a whole family through composition (you pass in a factory object).</p>"},
  {"q": "What is the main drawback?", "a": "<p>Adding a new <b>product type</b> (say <code>create_cache()</code>) forces a change to the interface and every concrete factory. Adding a new <b>family</b> is easy.</p>"},
  {"q": "How does this help testing?", "a": "<p>Tests pass a factory that returns in-memory fakes, so the code under test runs without network or cloud credentials and still exercises the same paths.</p>"}
],
"related": ["factory-method", "dependency-injection", "bridge"]
},

{
"id": "builder", "cat": "creational", "name": "Builder",
"alias": "Construct a complex object step by step; the same steps can produce different results.",
"simple": "At a sandwich counter you say: \"wheat bread, add chicken, add cheese, no onions, toast it\". Each step adds something, and at the end they hand you the finished sandwich. Nobody makes you shout all 12 choices in one breath.",
"intent": """<p>A builder collects configuration through small, readable steps and produces the final object with <code>build()</code> (or <code>prepare()</code>, <code>compile()</code>). It avoids constructors with a dozen optional arguments, lets you validate the whole thing at the end, and can keep the product immutable.</p>
<p>Python's keyword arguments and dataclasses remove much of the need for simple cases. Builders still earn their place when construction is <b>incremental</b> (built across several functions), <b>conditional</b>, or produces text/structures such as SQL queries, HTTP requests and emails. The chained style (<code>.where().order_by()</code>) is called a fluent interface.</p>""",
"structure": """ QueryBuilder("orders")
   .where("status = ?", "PAID")     each call records a part,
   .where("total > ?", 100)         returns self (or a new builder)
   .order_by("created_at DESC")
   .limit(10)
   .build()  -> (sql_string, params)   validated, final product""",
"code": r'''
class QueryBuilder:
    """Builds a parameterised SELECT; each method returns a NEW builder (immutable)."""
    def __init__(self, table, cols=("*",), wheres=(), params=(), order=None, lim=None):
        self.table, self.cols, self.wheres = table, cols, wheres
        self.params, self.order, self.lim = params, order, lim

    def _copy(self, **kw):
        d = dict(table=self.table, cols=self.cols, wheres=self.wheres,
                 params=self.params, order=self.order, lim=self.lim)
        d.update(kw)
        return QueryBuilder(**d)

    def select(self, *cols):        return self._copy(cols=cols)
    def where(self, cond, *vals):   return self._copy(wheres=self.wheres + (cond,), params=self.params + vals)
    def order_by(self, clause):     return self._copy(order=clause)
    def limit(self, n):
        if n <= 0: raise ValueError("limit must be positive")
        return self._copy(lim=n)

    def build(self):
        sql = f"SELECT {', '.join(self.cols)} FROM {self.table}"
        if self.wheres: sql += " WHERE " + " AND ".join(self.wheres)
        if self.order:  sql += f" ORDER BY {self.order}"
        if self.lim:    sql += f" LIMIT {self.lim}"
        return sql, list(self.params)

base = QueryBuilder("orders").select("id", "total").where("status = ?", "PAID")

# built incrementally, maybe in different functions, based on user filters
recent_big = base.where("total > ?", 100).order_by("created_at DESC").limit(10)
print(recent_big.build())
print(base.build())          # base is unchanged: safe to reuse
''',
"pythonic": r'''
from dataclasses import dataclass, field, replace

@dataclass(frozen=True)
class HttpRequest:                      # for simple cases, keywords + defaults ARE the builder
    url: str
    method: str = "GET"
    headers: dict = field(default_factory=dict)
    timeout: float = 5.0

req = HttpRequest("https://api.example.com/orders", method="POST",
                  headers={"Content-Type": "application/json"})
retry = replace(req, timeout=10.0)      # "modify" a frozen object -> new object
print(req); print(retry.timeout)

# stdlib builder: email.message.EmailMessage
from email.message import EmailMessage
msg = EmailMessage()
msg["Subject"] = "Invoice INV-42"
msg["To"] = "billing@example.com"
msg.set_content("Please find the invoice attached.")
msg.add_attachment(b"%PDF-1.7", maintype="application", subtype="pdf", filename="INV-42.pdf")
print(msg.is_multipart(), [p.get_content_type() for p in msg.iter_parts()])
''',
"pythonic_note": "For plain objects, keyword arguments with defaults plus <code>dataclasses.replace()</code> replace a builder. The stdlib's <code>EmailMessage</code> is a real builder for MIME messages.",
"examples": [
  {"where": "stdlib", "title": "<code>email.message.EmailMessage</code>", "body": "You set headers, call <code>set_content()</code>, then <code>add_attachment()</code> as many times as needed; the object turns itself into a correct multipart MIME structure. Building MIME by hand is famously error-prone."},
  {"where": "stdlib", "title": "<code>argparse.ArgumentParser</code>", "body": "A parser is assembled with repeated <code>add_argument()</code>, <code>add_subparsers()</code> and <code>add_mutually_exclusive_group()</code> calls, then <code>parse_args()</code> produces the result."},
  {"where": "framework", "title": "SQLAlchemy <code>select(...).where(...).order_by(...)</code>", "body": "Each call returns a new statement object (SQLAlchemy calls this \"generative\"), so a base query can be shared and extended safely. Compilation to SQL happens at the end, per dialect."},
  {"where": "framework", "title": "requests <code>Request(...).prepare()</code>", "body": "<code>requests.Request</code> collects method, URL, headers, params, JSON and auth; <code>prepare()</code> builds the final <code>PreparedRequest</code> with encoded body and headers, which the session then sends."},
  {"where": "framework", "title": "Django QuerySet chaining", "body": "<code>Order.objects.filter(status='PAID').exclude(total=0).order_by('-created')[:10]</code> builds a query step by step. No SQL runs until you iterate, which is why chains can be passed between functions."}
],
"use": ["Construction has many optional or conditional steps", "The object is assembled across several functions", "The product is text or a structure that must be valid as a whole (SQL, HTTP, MIME, config)"],
"avoid": ["A dataclass with keyword defaults already reads clearly", "A mutable builder shared across callers: one caller's <code>.where()</code> leaks into another's query"],
"pitfall": "Mutable builders that return <code>self</code>: reusing a partially built object in two places silently mixes both configurations. Return a new builder per step (like SQLAlchemy) or document single use.",
"qa": [
  {"q": "Why do you need Builder less often in Python than in Java or C++?", "a": "<p>Keyword arguments with defaults, <code>dataclasses</code> and <code>replace()</code> already give readable construction with optional parameters. Builder is kept for incremental, conditional or validated construction.</p>"},
  {"q": "What is a fluent interface?", "a": "<p>An API where each method returns an object (self or a new one) so calls chain: <code>q.where(...).order_by(...).limit(10)</code>. Builders are the most common place you see it.</p>"},
  {"q": "Builder vs Factory?", "a": "<p>A factory decides <b>which</b> class to create, in one call. A builder decides <b>how</b> one complex object is assembled, over several calls.</p>"}
],
"related": ["prototype", "facade", "factory-method"]
},

{
"id": "prototype", "cat": "creational", "name": "Prototype",
"alias": "Create new objects by copying a fully configured existing object.",
"simple": "A teacher prepares one perfect worksheet, then photocopies it for 40 students. Each student writes on their own copy, and the original stays clean for next year.",
"intent": """<p>When an object is expensive or fiddly to set up, configure it once (the prototype) and clone it whenever you need another. The clone can then be adjusted without touching the original.</p>
<p>Python has this built in: <code>copy.copy()</code> (shallow) and <code>copy.deepcopy()</code> (recursive), customizable with <code>__copy__</code> / <code>__deepcopy__</code>. <code>dataclasses.replace()</code> and, since 3.13, <code>copy.replace()</code> create a copy with some fields changed. The key decision is <b>shallow vs deep</b>: a shallow copy shares nested lists and dicts with the original.</p>""",
"structure": """ prototype = EnemyTemplate(mesh, stats, ai)   <- configured once (expensive)
 e1 = copy.deepcopy(prototype); e1.pos = (3, 4)
 e2 = copy.deepcopy(prototype); e2.pos = (9, 1)   independent clones""",
"code": r'''
import copy

class ReportTemplate:
    def __init__(self, title, sections, style):
        self.title = title
        self.sections = sections          # nested list: the shallow/deep trap
        self.style = style
    def __repr__(self):
        return f"<{self.title}: {self.sections}>"

base = ReportTemplate("Monthly", ["Summary", "Revenue"], {"font": "Inter", "logo": "acme.png"})

shallow = copy.copy(base)
shallow.title = "March (shallow)"
shallow.sections.append("Churn")         # mutates the SHARED list
print("after shallow edit, base:", base)

base.sections.remove("Churn")
deep = copy.deepcopy(base)
deep.title = "March (deep)"
deep.sections.append("Churn")            # its own list
print("after deep edit, base:   ", base)
print("deep copy:              ", deep)

class Connection:
    def __init__(self, dsn): self.dsn, self.sock = dsn, object()  # pretend socket
    def __deepcopy__(self, memo):
        # never clone live resources: make a fresh connection instead
        return Connection(self.dsn)

c = Connection("db://prod")
print("socket shared?", copy.deepcopy(c).sock is c.sock)
''',
"pythonic": r'''
from dataclasses import dataclass, replace
import copy

@dataclass(frozen=True)
class RetryPolicy:
    attempts: int = 3
    backoff: float = 0.2
    retry_on: tuple = (502, 503, 504)

DEFAULT = RetryPolicy()                              # the prototype
payments = replace(DEFAULT, attempts=5)              # clone + change
print(payments)
print(copy.replace(DEFAULT, backoff=1.0))            # Python 3.13+: works for dataclasses, namedtuples...
''',
"pythonic_note": "For immutable value objects, <code>dataclasses.replace()</code> (or <code>copy.replace()</code> on 3.13+) is the prototype pattern in one line.",
"examples": [
  {"where": "stdlib", "title": "<code>copy</code> module, <code>__copy__</code> / <code>__deepcopy__</code>", "body": "The standard protocol for cloning. <code>deepcopy</code> keeps a <code>memo</code> dict so shared references and cycles are copied once and stay shared inside the clone."},
  {"where": "stdlib", "title": "<code>dataclasses.replace()</code> and <code>copy.replace()</code>", "body": "Create a modified copy of a frozen dataclass or namedtuple. Common for configuration objects: keep a default policy and derive per-service variants."},
  {"where": "framework", "title": "scikit-learn <code>sklearn.base.clone()</code>", "body": "Builds a new, unfitted estimator with the same hyperparameters. <code>GridSearchCV</code> and <code>cross_val_score</code> clone your estimator for every fold so folds never share learned state."},
  {"where": "framework", "title": "Django <code>QuerySet._clone()</code>", "body": "Every <code>.filter()</code>, <code>.exclude()</code> or <code>.order_by()</code> clones the queryset and modifies the clone. That is why <code>qs.filter(...)</code> does not change <code>qs</code>."},
  {"where": "production", "title": "Game engines and simulations", "body": "Spawning hundreds of enemies or test packets from one fully configured template object is much cheaper than rebuilding each (loading meshes, stats, default fields) from scratch."}
],
"use": ["Setup is expensive (parsing, I/O, many fields) and many similar objects are needed", "You want to derive variants from a default configuration", "Objects must be independent snapshots of a starting state"],
"avoid": ["Objects hold live resources (sockets, file handles, locks) unless you customize <code>__deepcopy__</code>", "Construction is cheap and a constructor call is clearer"],
"pitfall": "Using <code>copy.copy()</code> (or <code>list(...)</code>, <code>dict(...)</code>, <code>[:]</code>) and then mutating a nested list: the \"copy\" and the original change together.",
"qa": [
  {"q": "Shallow copy vs deep copy?", "a": "<p>A shallow copy creates a new outer object but keeps references to the same inner objects. A deep copy recursively copies inner objects too. <code>list.copy()</code>, <code>dict.copy()</code>, slicing and <code>copy.copy()</code> are shallow.</p>"},
  {"q": "What is the <code>memo</code> argument in <code>__deepcopy__</code>?", "a": "<p>A dict mapping <code>id(original)</code> to its copy. It lets <code>deepcopy</code> handle cycles and shared references: an object referenced twice is copied once. Pass it to nested <code>copy.deepcopy(x, memo)</code> calls.</p>"},
  {"q": "Why does scikit-learn clone estimators?", "a": "<p>To guarantee each training run starts from the same unfitted state with the same hyperparameters, so cross-validation folds and grid-search candidates never leak fitted state into each other.</p>"}
],
"related": ["memento", "builder", "flyweight"]
},

{
"id": "object-pool", "cat": "creational", "name": "Object Pool",
"alias": "Keep a set of ready-to-use expensive objects and lend them out instead of creating new ones.",
"simple": "A bike-sharing station has 20 bikes. You borrow one, ride, and return it to the dock. The city doesn't build a new bike for every trip, and when all 20 are out, you wait for one to come back.",
"intent": """<p>Some objects are expensive to create but cheap to reuse: database connections (TCP + TLS + auth), HTTP connections, threads, processes. A pool creates a limited number, hands one out on request, and takes it back when the caller is done.</p>
<p>Good pools do three more things: <b>cap</b> the total (protecting the database from too many connections), <b>block or time out</b> when empty, and <b>reset or health-check</b> objects on return so the next borrower gets a clean one. In Python, lending is best expressed as a context manager so objects always come back.</p>""",
"structure": """   acquire()  ---> [conn1][conn2][conn3]  <--- release() (reset + return)
   pool empty?  wait up to timeout, then raise
   max size caps load on the database""",
"code": r'''
import queue, threading, time, itertools
from contextlib import contextmanager

class Connection:
    _ids = itertools.count(1)
    def __init__(self):
        time.sleep(0.05)                 # pretend: TCP + TLS + auth handshake
        self.id = next(self._ids)
        self.in_tx = False
    def query(self, sql): return f"conn{self.id}: {sql}"
    def reset(self): self.in_tx = False  # roll back leftovers before reuse

class ConnectionPool:
    def __init__(self, size):
        self._q = queue.Queue(maxsize=size)
        for _ in range(size):
            self._q.put(Connection())
        self.created = size

    @contextmanager
    def connection(self, timeout=1.0):
        try:
            conn = self._q.get(timeout=timeout)      # blocks when all are lent out
        except queue.Empty:
            raise TimeoutError("pool exhausted") from None
        try:
            yield conn
        finally:
            conn.reset()
            self._q.put(conn)                         # always returned, even on error

pool = ConnectionPool(size=3)
used = []
def handle_request(n):
    with pool.connection() as c:
        used.append(c.id)
        time.sleep(0.01)
        c.query(f"SELECT * FROM orders WHERE id={n}")

start = time.perf_counter()
threads = [threading.Thread(target=handle_request, args=(i,)) for i in range(30)]
for t in threads: t.start()
for t in threads: t.join()
print(f"30 requests served by {len(set(used))} connections (created {pool.created})")
print(f"elapsed {time.perf_counter() - start:.2f}s vs ~{30 * 0.05:.1f}s if each request opened its own")
''',
"pythonic": r'''
from concurrent.futures import ThreadPoolExecutor
import threading

def work(n):
    return n * n, threading.current_thread().name

# the stdlib pools threads for you: at most 4 threads, reused for 10 tasks
with ThreadPoolExecutor(max_workers=4, thread_name_prefix="w") as pool:
    results = list(pool.map(work, range(10)))
print([r[0] for r in results])
print("threads used:", sorted({r[1] for r in results}))
''',
"pythonic_note": "You rarely write a pool yourself. The stdlib pools threads and processes; database drivers and HTTP clients pool connections. Your job is to size and configure them.",
"examples": [
  {"where": "stdlib", "title": "<code>concurrent.futures.ThreadPoolExecutor</code> / <code>ProcessPoolExecutor</code>, <code>multiprocessing.Pool</code>", "body": "Worker threads or processes are created once and reused for many tasks. Starting a process costs milliseconds; reusing one costs almost nothing."},
  {"where": "framework", "title": "SQLAlchemy <code>QueuePool</code>", "body": "<code>create_engine()</code> uses a <code>QueuePool</code> by default (<code>pool_size=5</code>, <code>max_overflow=10</code>). <code>pool_pre_ping=True</code> checks a connection is alive before lending it, and <code>pool_recycle</code> replaces old ones."},
  {"where": "framework", "title": "requests + urllib3 connection pools", "body": "A <code>requests.Session</code> keeps urllib3 connection pools per host (tuned via <code>HTTPAdapter(pool_connections, pool_maxsize)</code>). Reusing a Session avoids a new TCP and TLS handshake per call, which is often the biggest speed-up in API clients."},
  {"where": "framework", "title": "redis-py <code>ConnectionPool</code>, psycopg <code>ConnectionPool</code>", "body": "Redis clients share a pool across threads by default. <code>psycopg_pool.ConnectionPool</code> provides min/max size, timeouts and health checks for PostgreSQL."},
  {"where": "production", "title": "Protecting the database under load", "body": "With 20 gunicorn workers x 10 pooled connections each, the DB sees at most 200 connections. Without a cap, a traffic spike opens thousands and the database refuses new connections for everyone. PgBouncer adds a shared pool in front of PostgreSQL for the same reason."}
],
"use": ["Objects are expensive to create and can be safely reused (connections, threads, processes, buffers)", "You must cap concurrent use of a scarce resource"],
"avoid": ["Cheap objects: Python's allocator is fast, and pooling adds complexity", "Objects that carry per-user state you cannot reliably reset"],
"pitfall": "Forgetting to return objects on exceptions. After a few errors the pool is empty and every request hangs. Always lend through <code>with</code> / <code>try...finally</code>.",
"qa": [
  {"q": "Why pool database connections?", "a": "<p>Opening a connection means TCP setup, TLS, authentication and server-side process creation, often several milliseconds. Pooling reuses connections and caps the total so the database is not overwhelmed.</p>"},
  {"q": "How do you size a connection pool?", "a": "<p>Start from the database's max connections divided by the number of app processes, then load-test. Larger is not always better: too many concurrent queries cause lock contention. Monitor wait time for a connection and DB CPU.</p>"},
  {"q": "What happens to a pool after fork (gunicorn preload, multiprocessing)?", "a": "<p>Sockets inherited by the child are shared with the parent and get corrupted if both use them. Create pools after fork, or dispose them in the child (SQLAlchemy: <code>engine.dispose(close=False)</code>).</p>"}
],
"related": ["singleton", "flyweight", "context-manager"]
},

]
