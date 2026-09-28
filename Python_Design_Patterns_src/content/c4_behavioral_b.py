PATTERNS = [

{
"id": "observer", "cat": "behavioral", "name": "Observer (Publish / Subscribe)",
"alias": "When one object changes, every subscribed listener is notified automatically.",
"simple": "You subscribe to a YouTube channel. When a new video is uploaded, every subscriber gets a notification. The creator doesn't phone each person, and you can unsubscribe any time.",
"intent": """<p>A <b>subject</b> keeps a list of <b>observers</b> (callbacks) and notifies them when something happens. The subject doesn't know what observers do, so you can add features (send email, update search index, write audit log) without changing the code that raised the event.</p>
<p>In Python an observer is usually just a callable. Two practical concerns matter in real code: <b>memory leaks</b> (the subject's list keeps observers alive, so long-lived subjects often hold weak references) and <b>error isolation</b> (one failing observer shouldn't stop the others).</p>""",
"structure": """ Order.mark_paid()  --emit("order_paid", order)-->  EventBus
                                                    |-> send_receipt(order)
                                                    |-> update_inventory(order)
                                                    '-> analytics.track(order)""",
"code": r'''
from collections import defaultdict
import weakref

class EventBus:
    def __init__(self):
        self._subs = defaultdict(list)

    def subscribe(self, event, fn):
        # bound methods are stored weakly so a dead object doesn't leak
        ref = weakref.WeakMethod(fn) if hasattr(fn, "__self__") else (lambda f=fn: f)
        self._subs[event].append(ref)
        return lambda: self._subs[event].remove(ref)          # unsubscribe handle

    def emit(self, event, **payload):
        for ref in list(self._subs[event]):
            fn = ref()
            if fn is None:                                     # observer was garbage-collected
                self._subs[event].remove(ref); continue
            try:
                fn(**payload)
            except Exception as e:                             # isolate failures
                print(f"  observer {fn.__name__} failed: {e}")

bus = EventBus()

def send_receipt(order_id, total): print(f"  email receipt for {order_id} ({total})")
def fraud_check(order_id, total):
    if total > 50_000: raise RuntimeError("manual review needed")

class Analytics:
    def track(self, order_id, total): print(f"  analytics: +{total} revenue")

bus.subscribe("order_paid", send_receipt)
bus.subscribe("order_paid", fraud_check)
a = Analytics()
stop_analytics = bus.subscribe("order_paid", a.track)

print("order O-1 paid"); bus.emit("order_paid", order_id="O-1", total=1200)
print("order O-2 paid"); bus.emit("order_paid", order_id="O-2", total=75_000)
del a                                                          # analytics object goes away
print("order O-3 paid"); bus.emit("order_paid", order_id="O-3", total=300)
''',
"pythonic": r'''
import asyncio

# stdlib observer 1: asyncio futures notify callbacks when done
async def main():
    loop = asyncio.get_running_loop()
    fut = loop.create_future()
    fut.add_done_callback(lambda f: print("callback A got", f.result()))
    fut.add_done_callback(lambda f: print("callback B got", f.result()))
    loop.call_later(0.01, fut.set_result, "payment confirmed")
    await fut
asyncio.run(main())

# stdlib observer 2: a property that notifies listeners on change
class Thermostat:
    def __init__(self): self._t, self.listeners = 21.0, []
    @property
    def temp(self): return self._t
    @temp.setter
    def temp(self, v):
        old, self._t = self._t, v
        for fn in self.listeners: fn(old, v)
t = Thermostat()
t.listeners.append(lambda old, new: print(f"temp {old} -> {new}"))
t.temp = 24.5
''',
"pythonic_note": "Callbacks are just callables in a list. The stdlib uses this in <code>asyncio.Future.add_done_callback</code>, <code>tkinter.Variable.trace_add</code> and <code>atexit.register</code>.",
"examples": [
  {"where": "stdlib", "title": "<code>asyncio.Future.add_done_callback</code>, <code>atexit.register</code>", "body": "Futures notify every registered callback when their result arrives. <code>atexit.register(fn)</code> subscribes functions to the interpreter-exit event."},
  {"where": "stdlib", "title": "<code>tkinter</code> variable traces", "body": "<code>StringVar.trace_add('write', callback)</code> calls every observer when the value changes, so labels and buttons can react to an entry field without polling."},
  {"where": "framework", "title": "Django signals (<code>post_save</code>, <code>pre_delete</code>, <code>request_finished</code>)", "body": "<code>@receiver(post_save, sender=Order)</code> runs your function after any <code>Order.save()</code>, for cache invalidation, search indexing or audit logs, without editing the model. Receivers are held weakly by default."},
  {"where": "framework", "title": "Blinker (Flask signals), Qt signals/slots, watchdog", "body": "Flask emits <code>request_started</code> and <code>template_rendered</code> through Blinker. PyQt/PySide connect widget signals to slots. <code>watchdog</code>'s <code>Observer</code> notifies handlers when files change."},
  {"where": "production", "title": "Domain events, webhooks and pub/sub", "body": "\"OrderPaid\" is published once; receipt, loyalty points, analytics and warehouse services each subscribe. Across processes the same idea uses Redis pub/sub, Kafka topics or webhooks (GitHub, Stripe)."}
],
"use": ["Several parts of the system must react to a change, and the list will grow", "The source of the event shouldn't depend on the reactors", "UI updates, cache invalidation, audit trails, integrations"],
"avoid": ["Order of reactions matters or reactions must be one transaction: call them explicitly", "Chains of events triggering events become impossible to follow (\"event spaghetti\")"],
"pitfall": "Memory leaks from strong references: a long-lived subject keeps every subscribed object alive forever. Unsubscribe explicitly, or store <code>weakref.WeakMethod</code> / use libraries that hold weak references (Django signals do by default).",
"qa": [
  {"q": "How would you implement Observer in Python?", "a": "<p>Keep a list (or dict of lists per event) of callables; <code>subscribe</code> appends and returns an unsubscribe function; <code>emit</code> calls each one, catching exceptions so one bad observer doesn't break the rest. Use weak references for bound methods if subjects live long.</p>"},
  {"q": "Observer vs Pub/Sub?", "a": "<p>In classic Observer, observers register directly with the subject. In Pub/Sub, a broker (event bus, Kafka) sits in between, so publishers and subscribers don't know each other, and delivery can be asynchronous and cross-process.</p>"},
  {"q": "What are the risks of Django signals?", "a": "<p>Hidden control flow (a <code>save()</code> triggers code in other apps), no transaction awareness by default (use <code>transaction.on_commit</code> for side effects like emails), and <code>bulk_create</code>/<code>update()</code> skip them. Many teams prefer explicit service-layer calls for core logic.</p>"}
],
"related": ["mediator", "chain-of-responsibility", "command"]
},

{
"id": "state", "cat": "behavioral", "name": "State",
"alias": "An object changes its behaviour when its internal state changes, via one class per state.",
"simple": "A traffic light: the same \"next\" button makes it go green to yellow, yellow to red, red to green. What \"next\" does depends on the current colour. Each colour knows only its own rule.",
"intent": """<p>When a method is full of <code>if self.status == ...</code> checks, and the same checks repeat in every method, move each state's behaviour into its own class. The context object delegates to its current state object, and states decide the transitions. Invalid actions in a state become explicit errors instead of silent bugs.</p>
<p>This is a <b>finite state machine</b>. For simple cases, a transition table (dict of allowed moves) is enough; the State pattern shines when each state has substantial behaviour.</p>""",
"structure": """ Order.pay() --> self.state.pay(order)
   Pending --pay--> Paid --ship--> Shipped --deliver--> Delivered
      '--cancel--> Cancelled <--cancel-- Paid (refund)
   Shipped.cancel() -> error: already shipped""",
"code": r'''
class OrderState:
    name = "?"
    def pay(self, order):     raise ValueError(f"cannot pay when {self.name}")
    def ship(self, order):    raise ValueError(f"cannot ship when {self.name}")
    def deliver(self, order): raise ValueError(f"cannot deliver when {self.name}")
    def cancel(self, order):  raise ValueError(f"cannot cancel when {self.name}")

class Pending(OrderState):
    name = "PENDING"
    def pay(self, order):    order.log("payment captured"); order.state = Paid()
    def cancel(self, order): order.log("cancelled, nothing to refund"); order.state = Cancelled()

class Paid(OrderState):
    name = "PAID"
    def ship(self, order):   order.log("handed to courier"); order.state = Shipped()
    def cancel(self, order): order.log("refund issued"); order.state = Cancelled()

class Shipped(OrderState):
    name = "SHIPPED"
    def deliver(self, order): order.log("delivered, ask for review"); order.state = Delivered()

class Delivered(OrderState): name = "DELIVERED"
class Cancelled(OrderState): name = "CANCELLED"

class Order:                                   # context
    def __init__(self, oid): self.oid, self.state = oid, Pending()
    def log(self, msg): print(f"  {self.oid} [{self.state.name}] {msg}")
    def __getattr__(self, action):             # delegate pay/ship/... to the state
        return lambda: getattr(self.state, action)(self)

o = Order("O-17")
for action in ["pay", "ship", "cancel", "deliver", "pay"]:
    try:
        getattr(o, action)()
    except ValueError as e:
        print(f"  {o.oid} rejected {action}: {e}")
print("final state:", o.state.name)
''',
"pythonic": r'''
from enum import Enum

class Status(Enum):
    PENDING = "pending"; PAID = "paid"; SHIPPED = "shipped"; CANCELLED = "cancelled"

# for simple lifecycles, a transition table is clearer than classes
TRANSITIONS = {
    (Status.PENDING, "pay"): Status.PAID,
    (Status.PENDING, "cancel"): Status.CANCELLED,
    (Status.PAID, "ship"): Status.SHIPPED,
    (Status.PAID, "cancel"): Status.CANCELLED,
}

def apply(status, event):
    try:
        return TRANSITIONS[(status, event)]
    except KeyError:
        raise ValueError(f"{event!r} not allowed in {status.name}") from None

s = Status.PENDING
for ev in ["pay", "ship"]:
    s = apply(s, ev); print(ev, "->", s.name)
try:
    apply(s, "cancel")
except ValueError as e:
    print(e)
''',
"pythonic_note": "An <code>Enum</code> plus a transition dict covers most business workflows. Switch to state classes when each state carries real behaviour.",
"examples": [
  {"where": "stdlib", "title": "<code>asyncio.Future</code> / <code>Task</code> states", "body": "A future is PENDING, then either FINISHED or CANCELLED. <code>set_result()</code> on a finished future raises <code>InvalidStateError</code>, the state machine rejecting an illegal transition."},
  {"where": "stdlib", "title": "<code>http.client.HTTPConnection</code>", "body": "Internally tracks idle, request-started and request-sent states; calling <code>putheader()</code> or <code>getresponse()</code> in the wrong state raises <code>CannotSendHeader</code> / <code>ResponseNotReady</code>."},
  {"where": "framework", "title": "django-fsm, transitions, python-statemachine", "body": "Libraries that declare states and allowed transitions on models: <code>@transition(field=state, source='paid', target='shipped')</code> guards methods so a shipped order can't be paid twice, and can emit signals on each transition."},
  {"where": "framework", "title": "TCP-like protocol handlers in asyncio / Twisted", "body": "Protocol implementations (SMTP, FTP, custom device protocols) move through states such as connected, authenticated and in-transfer, accepting different commands in each."},
  {"where": "production", "title": "Order, payment, KYC and device lifecycles", "body": "E-commerce orders, loan applications, support tickets and hardware test rigs (idle, powering-on, running-workload, collecting-logs, failed) are modelled as state machines, often persisted as a status column with guarded transitions."}
],
"use": ["Behaviour depends heavily on a status field and <code>if/elif</code> on it repeats across methods", "Illegal transitions must be rejected reliably", "Workflows with clear lifecycles"],
"avoid": ["Two or three states with trivial behaviour: an enum and a dict are enough", "Transitions depend on many external factors that don't belong to states"],
"pitfall": "Updating the status without checking the transition (<code>order.status = 'shipped'</code> anywhere in the code). Route every change through one guarded method, and in databases use conditional updates (<code>UPDATE ... WHERE status='paid'</code>) to avoid race conditions.",
"qa": [
  {"q": "State vs Strategy?", "a": "<p>Same structure (context delegates to an object), different intent. Strategy is chosen by the client and rarely changes; State objects change themselves as the context moves through its lifecycle, and each state knows its successors.</p>"},
  {"q": "How do you model an order lifecycle in a web app?", "a": "<p>An enum status column, a transition table or state classes enforcing allowed moves, one service method per event (<code>pay</code>, <code>ship</code>), atomic conditional DB updates to prevent double transitions, and an event emitted on each transition for other parts of the system.</p>"},
  {"q": "Where does the transition logic live?", "a": "<p>Either inside states (each state sets the next: flexible, decentralized) or in a central table (easy to see and validate the whole machine). Tables are easier to review; state classes are better when states have rich behaviour.</p>"}
],
"related": ["strategy", "memento", "command"]
},

{
"id": "strategy", "cat": "behavioral", "name": "Strategy",
"alias": "Define a family of interchangeable algorithms and pick one at runtime.",
"simple": "Going to the airport: car, metro or cab. The goal is the same; you pick the strategy based on traffic, budget and luggage, and you can switch tomorrow without changing where you're going.",
"intent": """<p>Put each variant of an algorithm behind the same interface and let the caller (or config) choose. The code that uses the algorithm stays the same, and adding a new variant means adding one function or class, not editing a growing <code>if/elif</code> chain.</p>
<p>In Python, the simplest strategy is <b>a function</b> passed as an argument: <code>sorted(key=...)</code> is Strategy. Use classes when a strategy has configuration or several related methods, and a <code>typing.Protocol</code> to describe the interface.</p>""",
"structure": """ Checkout(shipping=ExpressShipping())  ->  shipping.cost(order)
                  StandardShipping | ExpressShipping | FreeOver(999) | a plain function
 all share:  cost(order) -> float""",
"code": r'''
from dataclasses import dataclass
from typing import Protocol

@dataclass
class Order:
    total: float
    weight_kg: float
    pincode: str

class ShippingStrategy(Protocol):
    def cost(self, order: Order) -> float: ...

class Standard:
    def cost(self, o): return 40 + 10 * o.weight_kg

class Express:
    def __init__(self, surcharge=99): self.surcharge = surcharge
    def cost(self, o): return Standard().cost(o) * 2 + self.surcharge

class FreeOver:
    def __init__(self, threshold, fallback): self.threshold, self.fallback = threshold, fallback
    def cost(self, o): return 0.0 if o.total >= self.threshold else self.fallback.cost(o)

def metro_flat(o): return 25.0               # a plain function works too

class FunctionStrategy:                       # adapt a function to the interface
    def __init__(self, fn): self.fn = fn
    def cost(self, o): return self.fn(o)

def checkout(order: Order, shipping: ShippingStrategy):
    return round(order.total + shipping.cost(order), 2)

order = Order(total=850, weight_kg=2.5, pincode="560001")
for name, s in {"standard": Standard(), "express": Express(),
                "free over 999": FreeOver(999, Standard()),
                "free over 500": FreeOver(500, Standard()),
                "metro flat": FunctionStrategy(metro_flat)}.items():
    print(f"{name:14} -> pay {checkout(order, s)}")
''',
"pythonic": r'''
import hashlib, json
from datetime import date
from decimal import Decimal

people = [("Riya", 31), ("Arjun", 25), ("Meera", 42)]
print(sorted(people, key=lambda p: p[1]))            # strategy = the key function
print(max(people, key=lambda p: len(p[0])))

def encode_extra(o):                                 # strategy for unknown types
    if isinstance(o, (date, Decimal)): return str(o)
    raise TypeError(type(o))
print(json.dumps({"on": date(2026, 9, 28), "amt": Decimal("9.99")}, default=encode_extra))

for algo in ("md5", "sha256"):                       # algorithm chosen by name
    print(algo, hashlib.new(algo, b"invoice-42").hexdigest()[:16])
''',
"pythonic_note": "Passing a function is the Strategy pattern. <code>key=</code>, <code>default=</code> and <code>hashlib.new(name)</code> are all strategies in the stdlib.",
"examples": [
  {"where": "stdlib", "title": "<code>sorted(key=)</code>, <code>min/max(key=)</code>, <code>json.dumps(default=, cls=)</code>", "body": "The sorting algorithm is fixed; the comparison strategy is a function you pass. <code>json</code> lets you plug in how unknown types are encoded."},
  {"where": "stdlib", "title": "<code>hashlib.new(name)</code>, <code>shutil.make_archive(format=)</code>, <code>zipfile.ZipFile(compression=)</code>", "body": "Choose the hashing, archive or compression algorithm by parameter. The calling code is identical for SHA-256 or BLAKE2, zip or gztar, ZIP_DEFLATED or ZIP_LZMA."},
  {"where": "framework", "title": "scikit-learn estimators and PyTorch optimizers", "body": "Any estimator with <code>fit</code>/<code>predict</code> plugs into <code>Pipeline</code>, <code>cross_val_score</code> or <code>GridSearchCV</code>; switching <code>LogisticRegression</code> for <code>RandomForestClassifier</code> is one line. PyTorch training loops swap <code>SGD</code> for <code>AdamW</code> the same way."},
  {"where": "framework", "title": "requests <code>auth=</code>, Django <code>PASSWORD_HASHERS</code>", "body": "<code>requests.get(url, auth=HTTPBasicAuth(u, p))</code> or a custom <code>AuthBase</code> subclass plugs in how requests are signed. Django hashes passwords with the first strategy in <code>PASSWORD_HASHERS</code> (PBKDF2, Argon2, bcrypt) and can verify older ones."},
  {"where": "production", "title": "Pricing, discounts, shipping and payment selection", "body": "E-commerce platforms choose a discount strategy per campaign, a shipping calculator per courier, and a payment provider per country, often configured from the database so business teams can switch without a deploy."}
],
"use": ["Several variants of an algorithm exist and are chosen at runtime or by config", "You want to remove <code>if/elif</code> branching on a \"type\" or \"mode\" parameter", "Variants should be testable in isolation"],
"avoid": ["There is one algorithm and no realistic second one", "Variants differ by a constant: pass the value, not a strategy"],
"pitfall": "Strategies that need different inputs. If <code>Express</code> needs the pincode and <code>Standard</code> doesn't, pass the whole context object (the order) rather than growing a list of optional parameters.",
"qa": [
  {"q": "How is Strategy implemented idiomatically in Python?", "a": "<p>Pass a function (or any callable) as a parameter, or look it up in a dict by name. Use classes (with a <code>Protocol</code> interface) when strategies need configuration or several methods.</p>"},
  {"q": "Strategy vs Template Method?", "a": "<p>Strategy uses <b>composition</b>: the whole algorithm is swapped by passing a different object. Template Method uses <b>inheritance</b>: the skeleton is fixed in a base class and subclasses override steps. Strategy is more flexible at runtime.</p>"},
  {"q": "How does Strategy support the Open/Closed Principle?", "a": "<p>New behaviour is added by writing a new strategy, without modifying the code that uses strategies. The context is closed for modification but open for extension.</p>"}
],
"related": ["state", "template-method", "command", "bridge"]
},

{
"id": "template-method", "cat": "behavioral", "name": "Template Method",
"alias": "A base class fixes the steps of an algorithm; subclasses fill in specific steps.",
"simple": "Every tea and coffee recipe follows the same routine: boil water, brew, pour into cup, add extras. Tea brews leaves and adds lemon; coffee brews grounds and adds milk. The routine is fixed; only two steps differ.",
"intent": """<p>The base class has a non-overridden method (the template) that calls steps in a fixed order. Some steps are abstract (subclasses must implement them), some have defaults (hooks subclasses may override). This guarantees the invariant parts (validation, logging, transactions, cleanup) always run, while letting subclasses customize the rest.</p>
<p>Frameworks are built on it: you subclass and override <code>handle()</code>, <code>setUp()</code>, <code>get_queryset()</code>, and the framework calls them at the right time ("don't call us, we'll call you", the Hollywood principle).</p>""",
"structure": """ Importer.run(path)            # template: fixed order, not overridden
   rows = self.read(path)      # abstract: CsvImporter / JsonImporter
   rows = self.validate(rows)  # hook with default
   rows = self.transform(rows) # hook with default (no-op)
   self.save(rows)             # shared implementation
   self.report()""",
"code": r'''
import csv, io, json
from abc import ABC, abstractmethod

class Importer(ABC):
    def run(self, source):                       # the template method
        rows = self.read(source)
        good = [r for r in rows if self.is_valid(r)]
        good = [self.transform(r) for r in good]
        self.save(good)
        print(f"  {type(self).__name__}: {len(good)}/{len(rows)} rows imported")

    @abstractmethod
    def read(self, source) -> list[dict]: ...    # required step

    def is_valid(self, row):                     # hook with a sensible default
        return bool(row.get("email"))

    def transform(self, row):                    # hook: no-op by default
        return row

    def save(self, rows):                        # shared, invariant step
        for r in rows: print("    INSERT", r)

class CsvImporter(Importer):
    def read(self, source): return list(csv.DictReader(io.StringIO(source)))
    def transform(self, row): return {**row, "email": row["email"].lower()}

class JsonImporter(Importer):
    def read(self, source): return json.loads(source)
    def is_valid(self, row): return super().is_valid(row) and row.get("age", 0) >= 18

CsvImporter().run("name,email\nRiya,RIYA@X.COM\nNo Email,\n")
JsonImporter().run('[{"name":"Arjun","email":"a@x.com","age":17},{"name":"Meera","email":"m@x.com","age":30}]')

try:
    Importer()
except TypeError as e:
    print("ABC guard:", e)
''',
"pythonic": r'''
from collections.abc import Mapping

class EnvConfig(Mapping):
    """Implement 3 abstract methods; Mapping's template methods give you the rest."""
    def __init__(self, raw): self._d = {k.lower(): v for k, v in raw.items()}
    def __getitem__(self, key): return self._d[key.lower()]
    def __iter__(self): return iter(self._d)
    def __len__(self): return len(self._d)

cfg = EnvConfig({"DB_URL": "postgres://db", "DEBUG": "0"})
print(cfg.get("db_url"), "db_url" in cfg, list(cfg.keys()), dict(cfg.items()))   # all inherited
print(cfg == {"db_url": "postgres://db", "debug": "0"})
''',
"pythonic_note": "<code>collections.abc</code> is Template Method at its best: implement <code>__getitem__</code>, <code>__iter__</code> and <code>__len__</code>, and <code>Mapping</code> supplies <code>get</code>, <code>keys</code>, <code>items</code>, <code>__contains__</code> and <code>__eq__</code> built on top of them.",
"examples": [
  {"where": "stdlib", "title": "<code>socketserver.BaseRequestHandler</code>", "body": "The server calls <code>setup()</code>, <code>handle()</code>, <code>finish()</code> in order for each connection; you override <code>handle()</code> only. <code>http.server.BaseHTTPRequestHandler</code> goes further, dispatching to your <code>do_GET</code>/<code>do_POST</code>."},
  {"where": "stdlib", "title": "<code>unittest.TestCase</code>, <code>threading.Thread.run</code>, <code>html.parser.HTMLParser</code>", "body": "The test runner calls <code>setUp</code>, the test, <code>tearDown</code>; <code>Thread.start()</code> calls your <code>run()</code>; <code>HTMLParser.feed()</code> calls your <code>handle_starttag</code>/<code>handle_data</code> hooks."},
  {"where": "stdlib", "title": "<code>collections.abc</code> mixin methods", "body": "<code>Mapping</code>, <code>Sequence</code>, <code>MutableSet</code> and friends define concrete methods in terms of a few abstract ones, and refuse instantiation until those are provided."},
  {"where": "framework", "title": "Django class-based views", "body": "<code>View.dispatch()</code> routes to <code>get()</code>/<code>post()</code>; <code>ListView</code> calls <code>get_queryset()</code>, <code>get_context_data()</code> and <code>get_template_names()</code>, each overridable. You customize a list page by overriding one hook."},
  {"where": "production", "title": "ETL jobs, report generators, device test sequences", "body": "A base job class fixes extract, validate, transform, load, notify, with retries and metrics in the template; each data source only implements <code>extract()</code>. Hardware test frameworks fix power-on, configure, run, collect logs, power-off."}
],
"use": ["Several classes share the same algorithm structure with small differences", "Invariant steps (validation, logging, cleanup) must always run in order", "Building a framework or base class others extend"],
"avoid": ["Variation is better passed as a function (Strategy): it avoids inheritance", "Deep hierarchies where subclasses override hooks of hooks"],
"pitfall": "Subclasses overriding the template method itself, or forgetting <code>super()</code> in a hook with a default. Keep the template non-overridden by convention (and document it), and use <code>@abstractmethod</code> for required steps.",
"qa": [
  {"q": "What is the Hollywood principle?", "a": "<p>\"Don't call us, we'll call you.\" The base class or framework controls the flow and calls your overridden methods at the right time. Template Method is its classic implementation.</p>"},
  {"q": "What is a hook method?", "a": "<p>A step in the template with a default implementation (often empty) that subclasses may override to customize behaviour, unlike abstract steps which they must implement.</p>"},
  {"q": "How do ABCs help?", "a": "<p><code>abc.ABC</code> with <code>@abstractmethod</code> prevents instantiating a subclass that hasn't implemented required steps, so a missing step fails at construction time instead of mid-run.</p>"}
],
"related": ["strategy", "factory-method", "mixin"]
},

{
"id": "visitor", "cat": "behavioral", "name": "Visitor",
"alias": "Add new operations over a set of classes without changing those classes.",
"simple": "A tax inspector visits a factory, a shop and a farm. Each business opens its doors, and the inspector applies the right rules for each type. Next month a health inspector visits the same places with different rules, and the businesses didn't change at all.",
"intent": """<p>You have a stable set of node types (AST nodes, shapes, document elements) but keep adding operations (evaluate, pretty-print, export, lint). Instead of adding a method to every class for every operation, put each operation in a visitor class with one method per node type.</p>
<p>Classic Visitor uses <b>double dispatch</b>: <code>node.accept(visitor)</code> calls <code>visitor.visit_Circle(self)</code>. Python usually skips <code>accept</code>: <code>ast.NodeVisitor</code> dispatches by the class name (<code>visit_</code> + name), and <code>functools.singledispatch</code> dispatches on the argument's type.</p>""",
"structure": """ elements: Heading, Paragraph, Image, Table      (stable)
 visitors: HtmlExporter, WordCounter, Linter        (keep growing)
 visitor.visit(node) -> getattr(self, "visit_" + type(node).__name__)(node)""",
"code": r'''
from dataclasses import dataclass

@dataclass
class Heading:   text: str; level: int
@dataclass
class Paragraph: text: str
@dataclass
class Image:     src: str; alt: str

class Visitor:
    def visit(self, node):                       # dispatch by class name (like ast.NodeVisitor)
        method = getattr(self, "visit_" + type(node).__name__, self.generic_visit)
        return method(node)
    def generic_visit(self, node):
        raise NotImplementedError(type(node).__name__)

class HtmlExporter(Visitor):
    def visit_Heading(self, n):   return f"<h{n.level}>{n.text}</h{n.level}>"
    def visit_Paragraph(self, n): return f"<p>{n.text}</p>"
    def visit_Image(self, n):     return f'<img src="{n.src}" alt="{n.alt}">'

class WordCounter(Visitor):
    def visit_Heading(self, n):   return len(n.text.split())
    def visit_Paragraph(self, n): return len(n.text.split())
    def visit_Image(self, n):     return 0

class AccessibilityLinter(Visitor):             # a NEW operation, zero changes to nodes
    def visit_Heading(self, n):   return None
    def visit_Paragraph(self, n): return None
    def visit_Image(self, n):     return None if n.alt else f"image {n.src} has no alt text"

doc = [Heading("Q3 Report", 1), Paragraph("Revenue grew 18 percent."),
       Image("chart.png", ""), Paragraph("Churn fell to 2 percent.")]

print("\n".join(HtmlExporter().visit(n) for n in doc))
print("words:", sum(WordCounter().visit(n) for n in doc))
print("lint:", [msg for n in doc if (msg := AccessibilityLinter().visit(n))])
''',
"pythonic": r'''
import ast
from functools import singledispatch

# stdlib Visitor 1: a tiny security linter over Python's own AST
SOURCE = """
import os, subprocess
def run(cmd, data):
    result = eval(data)
    subprocess.call(cmd, shell=True)
    return os.system("ls")
"""
class DangerFinder(ast.NodeVisitor):
    def visit_Call(self, node):
        name = ast.unparse(node.func)
        if name in {"eval", "exec", "os.system"}:
            print(f"line {node.lineno}: call to {name}")
        if any(k.arg == "shell" and getattr(k.value, "value", False) for k in node.keywords):
            print(f"line {node.lineno}: {name} with shell=True")
        self.generic_visit(node)                 # keep walking into children
DangerFinder().visit(ast.parse(SOURCE))

# stdlib Visitor 2: singledispatch picks the implementation by argument type
@singledispatch
def to_json(obj): raise TypeError(type(obj))
@to_json.register
def _(obj: int): return str(obj)
@to_json.register
def _(obj: list): return "[" + ",".join(to_json(x) for x in obj) + "]"
@to_json.register
def _(obj: str): return '"' + obj + '"'
print(to_json([1, "a", [2, 3]]))
''',
"pythonic_note": "<code>ast.NodeVisitor</code> is how real linters work, and <code>functools.singledispatch</code> gives you type-based dispatch without an <code>accept()</code> method on every class.",
"examples": [
  {"where": "stdlib", "title": "<code>ast.NodeVisitor</code> / <code>ast.NodeTransformer</code>", "body": "Subclass and define <code>visit_FunctionDef</code>, <code>visit_Call</code> and so on; <code>generic_visit</code> walks children. <code>NodeTransformer</code> returns replacement nodes to rewrite code."},
  {"where": "stdlib", "title": "<code>functools.singledispatch</code> / <code>singledispatchmethod</code>", "body": "Register one implementation per type for a generic function; <code>singledispatchmethod</code> does the same for methods. It is the Pythonic Visitor when you can't add methods to the classes, such as <code>int</code>, <code>datetime</code> or a third-party type."},
  {"where": "framework", "title": "pylint, flake8 plugins, Bandit, LibCST", "body": "pylint checkers define <code>visit_call</code>, <code>visit_functiondef</code> over the astroid tree. Bandit's security checks run over the AST with a node visitor. LibCST offers <code>CSTVisitor</code>/<code>CSTTransformer</code> for codemods that keep formatting."},
  {"where": "framework", "title": "docutils / Sphinx translators", "body": "Sphinx builds a document tree once; HTML, LaTeX, man-page and text writers are visitors with <code>visit_paragraph</code>/<code>depart_paragraph</code> methods for every node type."},
  {"where": "production", "title": "Compilers, query planners, document exporters", "body": "A document model exported to PDF, DOCX and HTML; a query AST that is type-checked, optimized and turned into SQL in separate passes; a config tree validated and then rendered. Each pass is a visitor."}
],
"use": ["The set of node types is stable but operations keep being added", "Operations need type-specific logic across a tree (Composite)", "You want each operation's code in one place"],
"avoid": ["New node types are added often: every visitor must then be updated", "Only one or two operations: a method on each class is simpler"],
"pitfall": "Forgetting <code>self.generic_visit(node)</code> inside an <code>ast.NodeVisitor</code> method: the visitor then stops descending, silently missing nested calls (for example an <code>eval</code> inside a function inside a class).",
"qa": [
  {"q": "What is double dispatch?", "a": "<p>Choosing the method based on the runtime types of two objects: the element (via <code>element.accept(visitor)</code>) and the visitor (via <code>visitor.visit_X(element)</code>). Python replaces it with name-based lookup or <code>singledispatch</code>.</p>"},
  {"q": "What is the Visitor trade-off?", "a": "<p>Adding a new operation is easy (one new visitor). Adding a new element type is hard (every visitor needs a new method). Pick Visitor when types are stable and operations grow.</p>"},
  {"q": "How would you write a custom lint rule for Python code?", "a": "<p>Parse with <code>ast.parse</code>, subclass <code>ast.NodeVisitor</code>, implement <code>visit_&lt;NodeType&gt;</code> methods that inspect nodes and record findings with line numbers, and call <code>generic_visit</code> to keep traversing. Package it as a flake8 or Ruff plugin for CI.</p>"}
],
"related": ["composite", "interpreter", "iterator"]
},

]
