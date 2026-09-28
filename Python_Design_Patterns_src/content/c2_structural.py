PATTERNS = [

{
"id": "adapter", "cat": "structural", "name": "Adapter",
"alias": "Wrap an object so it fits the interface your code already expects.",
"simple": "Your Indian laptop charger won't fit a UK socket. You don't rewire the laptop or the wall; you plug in a travel adapter. It changes the shape of the plug and nothing else.",
"intent": """<p>An adapter translates calls from the interface a client expects (the <b>target</b>) into calls on an existing object with a different interface (the <b>adaptee</b>). Neither side changes.</p>
<p>Typical Python cases: wrapping a third-party SDK behind your own interface, fitting legacy code into new code, converting between sync and async, or between bytes and text. Because Python uses duck typing, the target interface is often informal ("anything with <code>.send(msg)</code>") or a <code>typing.Protocol</code>.</p>""",
"structure": """ client --> PaymentGateway.pay(amount_inr)      (target interface)
                 ^
          StripeAdapter.pay(...)  --translates-->  stripe_sdk.PaymentIntent.create(amount=paise, currency="inr")
                                                   (adaptee: third-party API)""",
"code": r'''
from typing import Protocol

# ---- the interface our checkout code is written against
class PaymentGateway(Protocol):
    def pay(self, order_id: str, amount_rupees: float) -> str: ...

# ---- two third-party SDKs with different shapes (the adaptees)
class StripeSDK:
    def create_payment_intent(self, amount, currency, metadata):
        return {"id": "pi_3Nx", "status": "succeeded", "amount": amount}

class LegacyBankClient:
    def DoTransfer(self, txn_ref, paise):           # old SOAP-style naming
        return f"OK|{txn_ref}|{paise}"

# ---- adapters: translate names, units and return types
class StripeAdapter:
    def __init__(self, sdk: StripeSDK): self.sdk = sdk
    def pay(self, order_id, amount_rupees):
        r = self.sdk.create_payment_intent(amount=round(amount_rupees * 100),
                                           currency="inr", metadata={"order": order_id})
        return r["id"]

class LegacyBankAdapter:
    def __init__(self, client: LegacyBankClient): self.client = client
    def pay(self, order_id, amount_rupees):
        status, ref, _ = self.client.DoTransfer(order_id, int(amount_rupees * 100)).split("|")
        if status != "OK":
            raise RuntimeError("bank transfer failed")
        return ref

def checkout(gateway: PaymentGateway, order_id, total):
    print(f"{type(gateway).__name__:18} -> payment ref {gateway.pay(order_id, total)}")

checkout(StripeAdapter(StripeSDK()), "ORD-1", 499.00)
checkout(LegacyBankAdapter(LegacyBankClient()), "ORD-2", 1250.50)
''',
"pythonic": r'''
import functools, io

# stdlib adapter 1: an old-style cmp function adapted to the key= interface
def compare_versions(a, b):                     # returns -1 / 0 / 1 (Python 2 style)
    pa, pb = [int(x) for x in a.split(".")], [int(x) for x in b.split(".")]
    return (pa > pb) - (pa < pb)
print(sorted(["1.10.0", "1.2.3", "1.9.9"], key=functools.cmp_to_key(compare_versions)))

# stdlib adapter 2: a bytes stream adapted to a text stream
raw = io.BytesIO("naïve café\nline two\n".encode("utf-8"))
text = io.TextIOWrapper(raw, encoding="utf-8")   # now you can iterate str lines
print([line.strip() for line in text])
''',
"pythonic_note": "The standard library ships adapters you use without noticing: <code>functools.cmp_to_key</code> and <code>io.TextIOWrapper</code> are both textbook Adapters.",
"examples": [
  {"where": "stdlib", "title": "<code>io.TextIOWrapper</code>", "body": "Adapts a binary stream (file, socket, <code>BytesIO</code>, <code>subprocess</code> pipe) into a text stream with decoding and newline handling. <code>open(path, 'r')</code> returns one."},
  {"where": "stdlib", "title": "<code>functools.cmp_to_key</code> and <code>socket.makefile()</code>", "body": "<code>cmp_to_key</code> adapts a two-argument compare function to the <code>key=</code> interface used by <code>sorted</code> since Python 3. <code>socket.makefile()</code> adapts a socket to the file interface so you can call <code>readline()</code>."},
  {"where": "framework", "title": "asgiref <code>sync_to_async</code> / <code>async_to_sync</code>", "body": "Django uses these adapters to call the synchronous ORM from async views, and async code from sync code, by running the call in a thread or an event loop behind a matching interface."},
  {"where": "framework", "title": "Django database backends over DB-API drivers", "body": "psycopg, mysqlclient and sqlite3 differ in parameter styles, error classes and type conversions. Each Django backend adapts its driver to the same interface the ORM uses."},
  {"where": "production", "title": "Wrapping vendor SDKs (payments, SMS, email)", "body": "Teams put Razorpay, Stripe or Twilio behind their own <code>PaymentGateway</code> / <code>SmsSender</code> interface. Switching vendors, or adding a fallback provider, then touches one adapter instead of every call site."}
],
"use": ["You must use a class whose interface doesn't match what your code expects", "Isolating a third-party SDK so it can be replaced or faked in tests", "Bridging sync/async, bytes/text, old/new APIs"],
"avoid": ["You own both sides and can simply change one interface", "The adapter starts adding business logic: it should only translate"],
"pitfall": "Leaking the adaptee's types through the adapter (returning the vendor's response object). Callers then depend on the vendor anyway. Return your own types.",
"qa": [
  {"q": "Adapter vs Facade vs Decorator?", "a": "<p><b>Adapter</b> changes the interface of one object to match an expected one. <b>Facade</b> gives a new, simpler interface over a whole subsystem. <b>Decorator</b> keeps the same interface and adds behaviour.</p>"},
  {"q": "Object adapter vs class adapter?", "a": "<p>An object adapter holds the adaptee (composition), as in the example. A class adapter inherits from the adaptee and the target (multiple inheritance). Composition is preferred: looser coupling and it can adapt any subclass instance.</p>"},
  {"q": "How does <code>typing.Protocol</code> help here?", "a": "<p>It declares the target interface structurally. Any adapter with a matching <code>pay()</code> type-checks without inheriting from anything, which fits Python's duck typing.</p>"}
],
"related": ["facade", "decorator", "proxy", "bridge"]
},

{
"id": "bridge", "cat": "structural", "name": "Bridge",
"alias": "Split an abstraction from its implementation so both can vary independently.",
"simple": "A TV remote (abstraction) and the TV (implementation) are separate. You can buy a fancy remote or a basic one, and use either with a Sony or a Samsung TV. Four combinations, but only two remotes and two TVs to build.",
"intent": """<p>When a class varies along two independent dimensions, inheritance explodes: <code>EmailAlert</code>, <code>SmsAlert</code>, <code>UrgentEmailAlert</code>, <code>UrgentSmsAlert</code>... Bridge splits the dimensions into two hierarchies connected by composition: the <b>abstraction</b> holds a reference to an <b>implementor</b>. With M abstractions and N implementations you write M + N classes instead of M x N.</p>
<p>It is designed up front (unlike Adapter, which fixes a mismatch after the fact). The <code>logging</code> module is the best-known Python example: loggers decide <i>what</i> to log, handlers decide <i>where</i> it goes.</p>""",
"structure": """  Notification (abstraction)  ----has-a---->  Channel (implementor)
     |- Alert                                   |- EmailChannel
     |- Reminder                                |- SmsChannel
     '- Digest                                  '- SlackChannel
  3 + 3 classes cover all 9 combinations""",
"code": r'''
from abc import ABC, abstractmethod

# ---- implementor hierarchy: HOW a message is delivered
class Channel(ABC):
    @abstractmethod
    def deliver(self, to: str, text: str): ...

class EmailChannel(Channel):
    def deliver(self, to, text): print(f"  email to {to}: {text}")
class SmsChannel(Channel):
    def deliver(self, to, text): print(f"  sms to {to}: {text[:40]}")
class SlackChannel(Channel):
    def deliver(self, to, text): print(f"  slack #{to}: {text}")

# ---- abstraction hierarchy: WHAT is sent and why
class Notification:
    def __init__(self, channel: Channel): self.channel = channel   # the bridge
    def send(self, to, subject): self.channel.deliver(to, self.render(subject))
    def render(self, subject): return subject

class Alert(Notification):
    def render(self, subject): return f"[ALERT] {subject.upper()}"
class Reminder(Notification):
    def render(self, subject): return f"Reminder: {subject}"

Alert(SmsChannel()).send("+91-98450-00000", "disk 95% full on db-2")
Alert(SlackChannel()).send("oncall", "disk 95% full on db-2")
Reminder(EmailChannel()).send("riya@example.com", "invoice due Friday")
print("combinations available:", 2 * 3, "classes written:", 2 + 3)
''',
"pythonic": r'''
import logging, io

# stdlib Bridge: Logger (what/level/hierarchy) x Handler (where) x Formatter (how it looks)
log = logging.getLogger("payments")
log.setLevel(logging.INFO)
buf = io.StringIO()
for handler, fmt in [(logging.StreamHandler(buf), "%(levelname)s %(name)s: %(message)s"),
                     (logging.StreamHandler(buf), '{"lvl":"%(levelname)s","msg":"%(message)s"}')]:
    handler.setFormatter(logging.Formatter(fmt))
    log.addHandler(handler)
log.info("charged order 42")
print(buf.getvalue().strip())
''',
"pythonic_note": "You already use a Bridge daily: the same <code>log.info()</code> call can go to the console, a file, syslog or a JSON collector, because loggers and handlers are separate hierarchies.",
"examples": [
  {"where": "stdlib", "title": "<code>logging</code>: Logger, Handler, Formatter", "body": "Loggers form a name hierarchy and filter by level; handlers (<code>FileHandler</code>, <code>RotatingFileHandler</code>, <code>SysLogHandler</code>, <code>SMTPHandler</code>, <code>QueueHandler</code>) decide the destination. Any logger works with any handler."},
  {"where": "framework", "title": "matplotlib figures and backends", "body": "Your plotting code builds Figures and Artists (the abstraction); a backend (Agg for PNG, PDF, SVG, TkAgg or QtAgg for windows) renders them. The same script saves a PNG on a server or opens a window on a laptop."},
  {"where": "framework", "title": "Django <code>FileField</code> and storage backends", "body": "Models use <code>FileField</code> and <code>default_storage</code>; the storage implementation can be the local filesystem or S3/GCS via django-storages. Changing <code>STORAGES</code> in settings moves every upload without touching models."},
  {"where": "framework", "title": "SQLAlchemy Engine over DBAPI drivers", "body": "The Engine/Session API is the abstraction; the driver (<code>psycopg</code>, <code>asyncpg</code>, <code>pymysql</code>) is selected by the URL, e.g. <code>postgresql+psycopg://</code>. Both sides evolve separately."},
  {"where": "production", "title": "Notification services", "body": "Alert, reminder, marketing and digest messages (abstractions) x email, SMS, push, WhatsApp, Slack (channels). New channel? One class. New message type? One class."}
],
"use": ["A class varies along two independent axes", "You want to switch implementations at runtime or by configuration", "Avoiding an M x N subclass explosion"],
"avoid": ["Only one dimension varies: Strategy or plain composition is enough", "Early in a design where the second dimension is speculative"],
"pitfall": "Letting implementation details leak into the abstraction's interface (for example an <code>sms_max_length</code> parameter on <code>Notification.send</code>). Keep channel-specific logic inside the channel.",
"qa": [
  {"q": "Bridge vs Adapter?", "a": "<p>Both use composition. Adapter is applied afterwards to make incompatible interfaces work together. Bridge is designed up front to let an abstraction and its implementation vary independently.</p>"},
  {"q": "Bridge vs Strategy?", "a": "<p>Structurally similar (an object holds a replaceable implementation). Strategy swaps one algorithm; Bridge separates two whole hierarchies that both keep growing.</p>"},
  {"q": "Give a stdlib example of Bridge.", "a": "<p>The <code>logging</code> package: <code>Logger</code> objects (abstraction) delegate output to any <code>Handler</code> (implementation), each with its own <code>Formatter</code>.</p>"}
],
"related": ["adapter", "strategy", "abstract-factory"]
},

{
"id": "composite", "cat": "structural", "name": "Composite",
"alias": "Treat individual objects and groups of objects through the same interface (trees).",
"simple": "An army: a general gives the order \"march\" to a division, which passes it to its brigades, which pass it to battalions, down to single soldiers. The general doesn't care whether he is talking to one soldier or ten thousand.",
"intent": """<p>Composite models part-whole hierarchies as trees where <b>leaves</b> and <b>containers</b> share one interface. Client code calls <code>size()</code>, <code>render()</code> or <code>run()</code> on any node; containers forward the call to their children and combine the results.</p>
<p>Anything tree-shaped fits: file systems, UI widget trees, org charts, menus, ASTs, test suites, neural network layers, bills of materials.</p>""",
"structure": """          Folder("project")            size() = sum(child.size())
          /        |        \\
   File(a.py)  Folder("src")  File(README)
                 /      \\
          File(x.py)  File(y.py)       File.size() = its own bytes""",
"code": r'''
from abc import ABC, abstractmethod

class Node(ABC):
    def __init__(self, name): self.name = name
    @abstractmethod
    def size(self) -> int: ...
    @abstractmethod
    def show(self, indent=0): ...

class File(Node):                           # leaf
    def __init__(self, name, nbytes):
        super().__init__(name); self.nbytes = nbytes
    def size(self): return self.nbytes
    def show(self, indent=0): print(" " * indent + f"{self.name} ({self.nbytes} B)")

class Folder(Node):                         # composite
    def __init__(self, name, *children):
        super().__init__(name); self.children = list(children)
    def add(self, node): self.children.append(node); return self
    def size(self): return sum(c.size() for c in self.children)   # recursion
    def show(self, indent=0):
        print(" " * indent + f"{self.name}/ ({self.size()} B)")
        for c in self.children: c.show(indent + 2)

project = Folder("project",
    File("README.md", 1_200),
    Folder("src", File("app.py", 8_400), File("models.py", 5_100),
           Folder("utils", File("dates.py", 900))),
    Folder("tests", File("test_app.py", 3_300)))

project.show()
print("total:", project.size(), "bytes | one file:", File("x", 7).size())  # same call on both
''',
"pythonic": r'''
import unittest

class TestMath(unittest.TestCase):
    def test_add(self): self.assertEqual(1 + 1, 2)
class TestStr(unittest.TestCase):
    def test_upper(self): self.assertEqual("a".upper(), "A")

# stdlib Composite: a TestSuite holds TestCases AND other TestSuites; all have run() / countTestCases()
inner = unittest.TestSuite([TestStr("test_upper")])
suite = unittest.TestSuite([TestMath("test_add"), inner])
print("tests in tree:", suite.countTestCases())
result = unittest.TestResult()
suite.run(result)
print("ran:", result.testsRun, "failures:", len(result.failures))
''',
"pythonic_note": "<code>unittest.TestSuite</code> is a Composite from the stdlib: suites contain tests or other suites, and you call <code>run()</code> on the root.",
"examples": [
  {"where": "stdlib", "title": "<code>unittest.TestSuite</code>", "body": "A suite contains test cases and nested suites; <code>run(result)</code> and <code>countTestCases()</code> work at every level. Test discovery builds exactly this tree from your packages."},
  {"where": "stdlib", "title": "<code>xml.etree.ElementTree</code> and <code>ast</code>", "body": "An <code>Element</code> has children that are <code>Element</code>s; <code>iter()</code> and <code>findall()</code> walk the tree uniformly. Every <code>ast</code> node, from <code>Module</code> down to <code>Constant</code>, shares the <code>ast.AST</code> base and is walked with the same tools."},
  {"where": "framework", "title": "PyTorch <code>nn.Module</code>", "body": "A model is a module containing layers that are themselves modules (and may contain modules). <code>model.parameters()</code>, <code>model.to('cuda')</code>, <code>model.eval()</code> and <code>state_dict()</code> recurse through the whole tree."},
  {"where": "framework", "title": "scikit-learn <code>Pipeline</code> and <code>ColumnTransformer</code>", "body": "A Pipeline of transformers is itself an estimator with <code>fit</code>/<code>predict</code>, so it can be nested in another Pipeline or passed to <code>GridSearchCV</code> exactly like a single model."},
  {"where": "production", "title": "Menus, permissions and bills of materials", "body": "E-commerce category trees, nested navigation menus, role hierarchies (a role grants permissions and other roles), and manufacturing BOMs (a product is parts and sub-assemblies) all compute totals by recursive Composite calls."}
],
"use": ["Data is naturally a tree (part-whole)", "Clients should treat one item and a group the same way"],
"avoid": ["The structure is flat, or leaves and groups need very different operations", "You need strict type rules on which children are allowed (the uniform interface makes this harder)"],
"pitfall": "Recursion on very deep or cyclic structures: a folder that (by a bug or a symlink) contains itself causes infinite recursion. Track visited nodes or guard depth.",
"qa": [
  {"q": "What problem does Composite solve?", "a": "<p>It lets client code handle single objects and collections uniformly through one interface, so tree operations (sum sizes, render, run) are written once instead of with type checks everywhere.</p>"},
  {"q": "Where should child-management methods (<code>add</code>, <code>remove</code>) live?", "a": "<p>Either only on the composite (safer: leaves can't have children, but clients must know the type) or on the shared interface (more uniform, leaves raise an error). Python code usually puts them only on the composite.</p>"},
  {"q": "Which pattern is often used to add operations over a Composite tree?", "a": "<p>Visitor (or <code>functools.singledispatch</code>): new operations such as export or validation are written in one place without changing node classes. Iterator is used to walk the tree.</p>"}
],
"related": ["visitor", "iterator", "decorator"]
},

{
"id": "decorator", "cat": "structural", "name": "Decorator",
"alias": "Wrap an object or function to add behaviour while keeping the same interface.",
"simple": "Your phone plus a case plus a screen guard plus a pop-socket. Each layer adds something, the phone inside is unchanged, and it is still a phone: you call and text exactly as before. You can add or remove layers in any order.",
"intent": """<p>A decorator wraps a component, exposes the <b>same interface</b>, and adds behaviour before/after delegating: caching, logging, retries, timing, auth checks, compression. Decorators stack, so behaviours combine without a subclass per combination.</p>
<p>Python has two forms. The <b>GoF object decorator</b> wraps an object (as <code>io</code> stacks buffering and text decoding over a raw file). The <b>@decorator syntax</b> wraps functions and classes: <code>@deco</code> above <code>def f</code> means <code>f = deco(f)</code>. Always use <code>functools.wraps</code> so the wrapper keeps the original name and docstring.</p>""",
"structure": """  @retry(3)                     call ->  retry wrapper
  @timed                                   -> timed wrapper
  @cache                                     -> cache wrapper
  def fetch_rate(cur): ...                     -> original fetch_rate
  (same signature at every layer)""",
"code": r'''
import functools, time, random

def timed(fn):
    @functools.wraps(fn)                      # keep name/docstring of fn
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            print(f"  {fn.__name__}{args} took {(time.perf_counter() - t0) * 1000:.1f} ms")
    return wrapper

def retry(times, exceptions=(ConnectionError,)):
    def deco(fn):                             # decorator factory: takes arguments
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    print(f"  attempt {attempt} failed: {e}")
                    if attempt == times: raise
        return wrapper
    return deco

random.seed(7)
@retry(times=3)
@timed
@functools.lru_cache(maxsize=128)
def fetch_rate(currency):
    """Call an exchange-rate API (flaky)."""
    time.sleep(0.02)
    if random.random() < 0.5:
        raise ConnectionError("upstream timeout")
    return {"USD": 83.1, "EUR": 90.4}[currency]

print("rate:", fetch_rate("USD"))
print("cached:", fetch_rate("USD"))           # served by lru_cache, no sleep
print(fetch_rate.__name__, "-", fetch_rate.__doc__)
''',
"pythonic": r'''
import io, gzip

# GoF object decorators in the stdlib: each layer has the same file interface
raw = io.BytesIO()
with gzip.GzipFile(fileobj=raw, mode="wb") as gz:           # adds compression
    with io.TextIOWrapper(gz, encoding="utf-8") as text:     # adds str -> bytes encoding
        text.write("order_id,total\n" * 1000)
print("compressed bytes:", len(raw.getvalue()))

raw.seek(0)
with io.TextIOWrapper(gzip.GzipFile(fileobj=raw), encoding="utf-8") as f:
    print("first line back:", f.readline().strip())

f = open(__import__("os").devnull)          # open() itself returns a stack of decorators
print(type(f).__name__, "->", type(f.buffer).__name__, "->", type(f.buffer.raw).__name__)
f.close()
''',
"pythonic_note": "Opening a text file gives you <code>TextIOWrapper</code> -> <code>BufferedReader</code> -> <code>FileIO</code>: three decorators, each adding one feature behind the same file interface.",
"examples": [
  {"where": "stdlib", "title": "<code>io</code> stack and <code>gzip.GzipFile(fileobj=...)</code>", "body": "<code>FileIO</code> does raw reads, <code>BufferedReader</code> adds buffering, <code>TextIOWrapper</code> adds decoding. <code>GzipFile</code> wraps any file object to add compression. Same read/write interface at each layer."},
  {"where": "stdlib", "title": "<code>functools.lru_cache</code>, <code>cache</code>, <code>wraps</code>; <code>contextlib.contextmanager</code>", "body": "<code>@lru_cache</code> adds memoization to any pure function in one line. <code>@contextmanager</code> turns a generator into a context manager. <code>@property</code>, <code>@staticmethod</code> and <code>@dataclass</code> use the same syntax."},
  {"where": "framework", "title": "Flask and Django view decorators", "body": "<code>@app.route('/orders')</code> registers a view; <code>@login_required</code>, Django's <code>@cache_page(60)</code>, <code>@require_POST</code> and <code>@csrf_exempt</code> wrap views to add auth, caching and method checks without editing the view body."},
  {"where": "framework", "title": "WSGI middleware such as Werkzeug <code>ProxyFix</code>", "body": "<code>app.wsgi_app = ProxyFix(app.wsgi_app)</code> wraps a WSGI app in another callable with the same signature that fixes client IPs behind a load balancer. Middleware stacks are decorator chains."},
  {"where": "production", "title": "Resilience wrappers: tenacity <code>@retry</code>, rate limiters, metrics", "body": "Service clients decorate outbound calls with <code>@retry(stop=stop_after_attempt(3), wait=wait_exponential())</code>, plus timing and Prometheus counters, keeping the business function focused on business logic."}
],
"use": ["Add cross-cutting behaviour (cache, retry, log, auth, timing) to many functions", "Combine optional features by stacking instead of subclassing each combination", "Add behaviour to objects at runtime"],
"avoid": ["Deep stacks that make tracebacks and debugging hard", "The added behaviour changes the interface or meaning: that is no longer a decorator"],
"pitfall": "Forgetting <code>@functools.wraps</code>: every decorated function is then called <code>wrapper</code>, breaking logs, docs, pytest names and Flask routes (Flask raises an error for duplicate endpoint names).",
"qa": [
  {"q": "What does <code>@decorator</code> syntax actually do?", "a": "<p><code>@d</code> above <code>def f</code> is sugar for <code>f = d(f)</code> after the function is defined. Stacked decorators apply bottom-up: <code>@a @b def f</code> is <code>f = a(b(f))</code>.</p>"},
  {"q": "How do you write a decorator that takes arguments?", "a": "<p>Add one more level: a factory that takes the arguments and returns the real decorator, which takes the function and returns the wrapper (see <code>retry(times=3)</code>).</p>"},
  {"q": "Python decorators vs the GoF Decorator pattern?", "a": "<p>GoF Decorator wraps an <b>object</b> with the same interface (like the <code>io</code> stack). Python's <code>@</code> syntax wraps <b>functions or classes</b> at definition time. Both add behaviour while preserving the interface; Python decorators can also register or replace things.</p>"},
  {"q": "What does <code>functools.wraps</code> do?", "a": "<p>It copies <code>__name__</code>, <code>__qualname__</code>, <code>__doc__</code>, <code>__module__</code> and <code>__dict__</code> from the wrapped function and sets <code>__wrapped__</code>, so introspection, docs and <code>inspect.signature</code> still work.</p>"}
],
"related": ["proxy", "adapter", "chain-of-responsibility", "composite"]
},

{
"id": "facade", "cat": "structural", "name": "Facade",
"alias": "One simple interface in front of a complex subsystem.",
"simple": "A hotel concierge. You say \"book me dinner and a taxi for 8 pm\". Behind the scenes they call the restaurant, the taxi company and update your bill. You talk to one person, not five departments.",
"intent": """<p>A facade offers a small, task-oriented API that coordinates many lower-level objects. It hides ordering rules, setup and error handling, so most callers get the common case in one call while experts can still reach the subsystem directly.</p>
<p>Python's most loved libraries are facades: <code>requests.get()</code> over urllib3 and <code>http.client</code>; <code>subprocess.run()</code> over <code>Popen</code>; <code>shutil</code> over <code>os</code>. In your own code, a service-layer function like <code>place_order()</code> is a facade over repositories, payment and messaging.</p>""",
"structure": """  client --> OrderFacade.place_order(cart, card)
                 |-- InventoryService.reserve()
                 |-- PaymentService.charge()
                 |-- InvoiceService.create()
                 '-- EmailService.send()        (order and rollback handled inside)""",
"code": r'''
class Inventory:
    def reserve(self, sku, qty): print(f"  reserve {qty} x {sku}"); return f"R-{sku}"
    def release(self, rid): print(f"  release {rid}")
class Payments:
    def charge(self, card, amount):
        if card.endswith("0000"): raise RuntimeError("card declined")
        print(f"  charge {amount:.2f} on ****{card[-4:]}"); return "PAY-77"
class Invoices:
    def create(self, order_id, amount): print(f"  invoice for {order_id}"); return f"INV-{order_id}"
class Mailer:
    def send(self, to, subject): print(f"  email {to}: {subject}")

class CheckoutFacade:
    """One call for the common case; hides order of steps and compensation."""
    def __init__(self):
        self.inv, self.pay, self.invoices, self.mail = Inventory(), Payments(), Invoices(), Mailer()

    def place_order(self, order_id, email, sku, qty, price, card):
        rid = self.inv.reserve(sku, qty)
        try:
            self.pay.charge(card, qty * price)
        except RuntimeError as e:
            self.inv.release(rid)                     # compensation hidden from caller
            return {"ok": False, "error": str(e)}
        inv = self.invoices.create(order_id, qty * price)
        self.mail.send(email, f"Order {order_id} confirmed")
        return {"ok": True, "invoice": inv}

shop = CheckoutFacade()
print(shop.place_order("O-1", "a@x.com", "SKU-9", 2, 499.0, "4111111111111111"))
print(shop.place_order("O-2", "b@x.com", "SKU-9", 1, 499.0, "4000000000000000"))
''',
"pythonic": r'''
import subprocess, sys, shutil, tempfile, pathlib

# subprocess.run is a facade over Popen + pipes + wait + error checking
r = subprocess.run([sys.executable, "-c", "print('hello from child')"],
                   capture_output=True, text=True, check=True, timeout=10)
print(r.stdout.strip(), "| exit", r.returncode)

# shutil is a facade over os, zipfile and tarfile
with tempfile.TemporaryDirectory() as d:
    src = pathlib.Path(d, "reports"); src.mkdir()
    (src / "q1.csv").write_text("a,b\n1,2\n")
    archive = shutil.make_archive(str(pathlib.Path(d, "backup")), "zip", src)
    print(pathlib.Path(archive).name, pathlib.Path(archive).stat().st_size > 0)
''',
"pythonic_note": "Before writing your own facade, check whether the stdlib already has one: <code>subprocess.run</code>, <code>shutil.copytree</code>, <code>shutil.make_archive</code>, <code>pathlib.Path.read_text</code>.",
"examples": [
  {"where": "stdlib", "title": "<code>subprocess.run()</code>", "body": "Added in 3.5 as a facade over <code>Popen</code>: it starts the process, wires pipes, waits, applies a timeout, and raises <code>CalledProcessError</code> with <code>check=True</code>. <code>Popen</code> is still there for streaming or interactive cases."},
  {"where": "stdlib", "title": "<code>shutil</code> and <code>pathlib</code>", "body": "<code>shutil.copytree</code>, <code>rmtree</code> and <code>make_archive</code> hide the recursion over <code>os.scandir</code>, permission copying and zip/tar details. <code>Path.read_text()</code> hides open, decode and close."},
  {"where": "framework", "title": "requests over urllib3 and http.client", "body": "<code>requests.get(url, params=..., timeout=5)</code> hides connection pooling, redirects, cookie handling, content decoding and JSON parsing. It became Python's most downloaded library largely because of this simple facade."},
  {"where": "framework", "title": "boto3 <code>s3.upload_file()</code>", "body": "One call that decides whether to use multipart upload, splits the file into parts, uploads them in parallel threads and retries failed parts, which would otherwise be dozens of low-level API calls."},
  {"where": "production", "title": "Service layer in web applications", "body": "Views and API handlers call <code>OrderService.place_order()</code>; the service coordinates repositories, payment gateway, events and emails. Controllers stay thin and the same logic is reused by CLI commands and background jobs."}
],
"use": ["A subsystem is complex and most callers need a few common operations", "You want a stable entry point while internals change", "Layering an application (service layer over infrastructure)"],
"avoid": ["The facade becomes a god object that knows everything; split it by use case", "Hiding things power users legitimately need; keep the subsystem accessible"],
"pitfall": "Facades that swallow errors to look simple (returning <code>None</code> on any failure). Hide complexity, not failures: raise clear exceptions or return explicit results.",
"qa": [
  {"q": "Facade vs Adapter?", "a": "<p>An Adapter makes one existing interface match another expected interface. A Facade defines a new, simpler interface over many objects. Adapter is about compatibility; Facade is about simplicity.</p>"},
  {"q": "Does a facade prevent access to the subsystem?", "a": "<p>No. It is a convenience layer. Clients who need fine control can still use the subsystem directly (as you can still use <code>Popen</code> instead of <code>run</code>).</p>"},
  {"q": "Give an example of a facade you wrote.", "a": "<p>A good answer names a real subsystem and the simplification: e.g. a <code>DeviceTestRunner.run(test_plan)</code> facade that powers the device, configures firmware, runs the workload, collects logs and powers down, so test authors write one call instead of 40 lines of setup.</p>"}
],
"related": ["adapter", "mediator", "singleton", "abstract-factory"]
},

{
"id": "flyweight", "cat": "structural", "name": "Flyweight",
"alias": "Share the common, immutable part of many similar objects to save memory.",
"simple": "A printing press doesn't cast a new letter \"e\" for every \"e\" in the newspaper. It has one \"e\" block and stamps it wherever needed. Only the position on the page is different each time.",
"intent": """<p>When you need millions of fine-grained objects, most of their data is often identical. Flyweight splits state into <b>intrinsic</b> (shared, immutable: font, sprite, species, category name) and <b>extrinsic</b> (per-use: position, quantity). A factory hands out one shared object per intrinsic value.</p>
<p>CPython itself does this: small integers from -5 to 256 are preallocated and shared, and strings can be interned. In your own code, combine a cached factory with <code>__slots__</code> on the per-instance objects.</p>""",
"structure": """ 1,000,000 Tree(x, y, type)     type -> TreeType("oak", texture, mesh)   <- 3 shared objects
                                         TreeType("pine", ...)
                                         TreeType("birch", ...)
 extrinsic: x, y (per tree)     intrinsic: name, texture, mesh (shared)""",
"code": r'''
import tracemalloc, functools, random

class TreeType:                                    # intrinsic, shared, immutable
    def __init__(self, name, color, texture):
        self.name, self.color, self.texture = name, color, texture

@functools.cache                                   # flyweight factory: one per key
def tree_type(name, color):
    return TreeType(name, color, texture=bytes(2_000))   # pretend 2 KB texture

class Tree:
    __slots__ = ("x", "y", "type")                # no per-instance __dict__
    def __init__(self, x, y, type_): self.x, self.y, self.type = x, y, type_

class FatTree:                                     # naive: every tree owns a texture
    def __init__(self, x, y, name, color):
        self.x, self.y, self.name, self.color = x, y, name, color
        self.texture = bytes(2_000)

kinds = [("oak", "green"), ("pine", "dark green"), ("birch", "white")]
random.seed(1)
N = 20_000

def measure(make):
    tracemalloc.start()
    forest = [make(random.random(), random.random(), *random.choice(kinds)) for _ in range(N)]
    cur, _ = tracemalloc.get_traced_memory(); tracemalloc.stop()
    return forest, cur / 1e6

_, fat_mb = measure(lambda x, y, n, c: FatTree(x, y, n, c))
forest, fly_mb = measure(lambda x, y, n, c: Tree(x, y, tree_type(n, c)))
print(f"naive:     {fat_mb:6.1f} MB")
print(f"flyweight: {fly_mb:6.1f} MB  ({fat_mb / fly_mb:.0f}x less)")
print("shared TreeType objects:", tree_type.cache_info().currsize)
''',
"pythonic": r'''
import sys

a, b = 256, int("256")
c, d = 257, int("257")
print("256 shared:", a is b, "| 257 shared:", c is d)   # CPython small-int cache (-5..256)

s1 = "".join(["order", "_status"])
s2 = "order_status"
print("equal:", s1 == s2, "| same object:", s1 is s2)
print("after intern:", sys.intern(s1) is sys.intern(s2))
''',
"pythonic_note": "CPython already shares small ints and many strings. <code>sys.intern()</code> lets you share strings explicitly, which helps when millions of records repeat the same keys. (Identity of ints and strings is an implementation detail: always compare values with <code>==</code>.)",
"examples": [
  {"where": "stdlib", "title": "CPython small-integer cache and <code>sys.intern()</code>", "body": "Integers -5..256 are preallocated singletons; identifiers and many literal strings are interned automatically, and <code>sys.intern()</code> interns any string so repeated values share memory and compare faster in dict lookups."},
  {"where": "stdlib", "title": "<code>re</code> compiled-pattern cache and <code>enum</code> members", "body": "<code>re.search(pattern, s)</code> keeps an internal cache of compiled patterns, so the same regex string is compiled once. Enum members are created once and shared by every reference."},
  {"where": "framework", "title": "pandas <code>category</code> dtype", "body": "<code>df['city'].astype('category')</code> stores each distinct string once plus small integer codes per row. A 10-million-row column with 50 cities can shrink from hundreds of MB to tens of MB."},
  {"where": "framework", "title": "<code>__slots__</code> in data-heavy libraries", "body": "Libraries that create huge numbers of small objects (ORM row objects, AST nodes, geometry points) use <code>__slots__</code> to drop the per-instance <code>__dict__</code>, the memory-saving companion to sharing intrinsic state."},
  {"where": "production", "title": "Games, maps and text editors", "body": "Games render forests and crowds from a few shared meshes/textures; map apps share icon sprites across thousands of pins; editors share glyph objects per character and font instead of one per keystroke."}
],
"use": ["Very large numbers of similar objects cause memory pressure", "Most object state can be made immutable and shared"],
"avoid": ["Object counts are small: complexity without benefit", "The shared part must be mutable per object"],
"pitfall": "Mutating a shared flyweight (<code>tree.type.color = 'red'</code>) changes every tree using it. Make intrinsic objects immutable (frozen dataclasses, tuples).",
"qa": [
  {"q": "Intrinsic vs extrinsic state?", "a": "<p>Intrinsic state is independent of context and can be shared (species, font, texture). Extrinsic state depends on context and is supplied per use (position, size, quantity).</p>"},
  {"q": "Why does <code>a is b</code> return True for 256 but False for 257?", "a": "<p>CPython preallocates integers from -5 to 256 and reuses them (a flyweight cache). Larger ints created at runtime are separate objects. It is an implementation detail: never use <code>is</code> to compare numbers.</p>"},
  {"q": "How would you cut memory for 10 million objects in Python?", "a": "<p>Use <code>__slots__</code>, share repeated values (flyweight / <code>sys.intern</code> / pandas categories), use tuples or namedtuples, or move to columnar structures (NumPy arrays, pandas, <code>array</code> module) instead of one object per record. Measure with <code>tracemalloc</code>.</p>"}
],
"related": ["singleton", "object-pool", "prototype"]
},

{
"id": "proxy", "cat": "structural", "name": "Proxy",
"alias": "A stand-in with the same interface that controls access to the real object.",
"simple": "A cheque is a proxy for money in your bank. You can hand it over like cash, but the bank checks your balance (protection) and only moves money when it's presented (lazy). The money itself stays safely in the vault (remote).",
"intent": """<p>A proxy has the same interface as the real subject and decides when and how to forward calls. Common kinds:</p>
<p><b>Virtual (lazy) proxy</b>: create an expensive object only when first used. <b>Protection proxy</b>: check permissions or make the object read-only. <b>Remote proxy</b>: represent an object in another process or machine. <b>Caching / logging proxy</b>: add caching or auditing on access. <b>Smart reference</b>: count references or hold weak references.</p>
<p>In Python, <code>__getattr__</code> makes generic proxies short: it is only called for attributes not found on the proxy itself, so everything else forwards to the target.</p>""",
"structure": """ client --> ReportProxy.render()  --(first use? load)--> RealReport.render()
                 |  same interface
                 '-- checks role, logs access, caches result""",
"code": r'''
import time

class SalesReport:                               # expensive real subject
    def __init__(self, year):
        print(f"  loading 2 GB of {year} sales data...")
        time.sleep(0.05)
        self.year, self.rows = year, 1_250_000
    def summary(self): return f"{self.year}: {self.rows:,} rows"
    def export(self, fmt): return f"{self.year}.{fmt} written"

class ReportProxy:
    """Virtual proxy (lazy load) + protection proxy (role check) + logging."""
    def __init__(self, year, user_role):
        self._year, self._role, self._real = year, user_role, None

    def _subject(self):
        if self._real is None:                   # created on first real use
            self._real = SalesReport(self._year)
        return self._real

    def __getattr__(self, name):                 # called only for missing attributes
        if name == "export" and self._role != "admin":
            raise PermissionError(f"role '{self._role}' cannot export")
        print(f"  audit: {self._role} called {name}")
        return getattr(self._subject(), name)

r = ReportProxy(2025, user_role="analyst")
print("proxy created, nothing loaded yet")
print(r.summary())
print(r.summary())                               # already loaded: no second load
try:
    r.export("csv")
except PermissionError as e:
    print("blocked:", e)
''',
"pythonic": r'''
import types, weakref

# protection proxy: a read-only view of a dict
_config = {"db_url": "postgres://prod", "debug": False}
CONFIG = types.MappingProxyType(_config)
try:
    CONFIG["debug"] = True
except TypeError as e:
    print("read-only:", e)
_config["debug"] = True                          # owner can still change the real dict
print("view sees update:", CONFIG["debug"])
print(type(int.__dict__).__name__)               # class namespaces are exposed this way

# smart reference: weakref.proxy doesn't keep the object alive
class Session: pass
s = Session(); p = weakref.proxy(s)
del s
try:
    p.anything
except ReferenceError as e:
    print("weak proxy:", e)
''',
"pythonic_note": "<code>types.MappingProxyType</code> (read-only view) and <code>weakref.proxy</code> are ready-made proxies. Every class's <code>__dict__</code> is a <code>mappingproxy</code>.",
"examples": [
  {"where": "stdlib", "title": "<code>types.MappingProxyType</code> and <code>weakref.proxy</code>", "body": "A mapping proxy is a read-only live view, used to expose internal registries safely. <code>weakref.proxy</code> behaves like the object but doesn't keep it alive, useful for caches and parent back-references."},
  {"where": "stdlib", "title": "<code>xmlrpc.client.ServerProxy</code> and <code>multiprocessing</code> managers", "body": "Remote proxies: calling <code>proxy.add(2, 3)</code> sends a request to another process or server. <code>multiprocessing.Manager().dict()</code> returns a proxy whose methods run in the manager process."},
  {"where": "framework", "title": "Flask <code>request</code>, <code>current_app</code>, <code>g</code> (Werkzeug <code>LocalProxy</code>)", "body": "These module-level names are proxies that resolve to the object for the current request context, which is why you can import <code>request</code> globally and still get the right one in each concurrent request."},
  {"where": "framework", "title": "Django <code>request.user</code> and SQLAlchemy lazy loading", "body": "Django's authentication middleware sets <code>request.user</code> to a <code>SimpleLazyObject</code>, so the user query only runs if the view touches it. SQLAlchemy relationships with <code>lazy='select'</code> load related rows only on first attribute access."},
  {"where": "production", "title": "API gateways and caching proxies", "body": "At system scale, NGINX, Envoy and CDNs are proxies with the same HTTP interface as the service behind them, adding auth, rate limiting, TLS and caching. Test code uses <code>unittest.mock</code> objects as stand-in proxies for real services."}
],
"use": ["Delay creating something expensive until needed", "Control access (permissions, read-only) without changing the real class", "Represent a remote or cross-process object locally", "Add caching, auditing or reference management transparently"],
"avoid": ["The indirection hides important latency (a remote call that looks like a local attribute)", "Simple cases where an explicit function call is clearer"],
"pitfall": "<code>__getattr__</code> does not intercept special methods: <code>len(proxy)</code>, <code>proxy[0]</code> and <code>str(proxy)</code> look up <code>__len__</code>/<code>__getitem__</code>/<code>__str__</code> on the type and bypass it. Define those explicitly if needed.",
"qa": [
  {"q": "Proxy vs Decorator?", "a": "<p>Both wrap an object with the same interface. A Decorator adds responsibilities and is usually stacked by the client. A Proxy controls access (lazy creation, permissions, remoteness) and often manages the real object's lifecycle itself.</p>"},
  {"q": "What is the difference between <code>__getattr__</code> and <code>__getattribute__</code>?", "a": "<p><code>__getattribute__</code> runs on every attribute access. <code>__getattr__</code> runs only when normal lookup fails. Proxies usually use <code>__getattr__</code> so their own attributes resolve normally.</p>"},
  {"q": "How does Flask make <code>request</code> a global yet per-request?", "a": "<p><code>request</code> is a Werkzeug <code>LocalProxy</code> bound to a context variable. Each access looks up the request object for the current context (thread or async task), so concurrent requests never see each other's data.</p>"}
],
"related": ["decorator", "adapter", "singleton"]
},

]
