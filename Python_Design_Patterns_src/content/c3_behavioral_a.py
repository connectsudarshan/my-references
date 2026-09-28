PATTERNS = [

{
"id": "chain-of-responsibility", "cat": "behavioral", "name": "Chain of Responsibility",
"alias": "Pass a request along a chain of handlers; each handles it, passes it on, or stops it.",
"simple": "Calling customer support: the bot tries first; if it can't help, you go to a level-1 agent, then to a specialist, then to a manager. You just made one call; the chain decided who dealt with it.",
"intent": """<p>Instead of one big function with every check, you build a chain of small handlers. Each handler looks at the request and either handles it, modifies it and passes it on, or stops the chain (for example, returns 401). The sender doesn't know which handler finished the job, and handlers can be reordered or added through configuration.</p>
<p>Web middleware is the everyday Python form: each middleware wraps the next one and can short-circuit. Exception handling is also a chain: an exception travels up the call stack until some <code>except</code> handles it.</p>""",
"structure": """ request -> [RequestId] -> [Auth] -> [RateLimit] -> [Validate] -> view
                            |           |
                     401 & stop    429 & stop      (each can short-circuit)
 response flows back through the same chain in reverse""",
"code": r'''
import time
from typing import Callable

Handler = Callable[[dict], dict]

def request_id(next_: Handler) -> Handler:
    counter = iter(range(1000, 10**6))
    def handle(req):
        req["id"] = next(counter)
        resp = next_(req)
        resp["headers"]["X-Request-ID"] = str(req["id"])   # runs on the way back
        return resp
    return handle

def auth(next_: Handler) -> Handler:
    def handle(req):
        if req.get("token") != "secret":
            return {"status": 401, "body": "unauthorized", "headers": {}}   # stop here
        return next_(req)
    return handle

def rate_limit(limit_per_sec: int):
    def mw(next_: Handler) -> Handler:
        hits = []
        def handle(req):
            now = time.monotonic()
            hits[:] = [t for t in hits if now - t < 1]
            if len(hits) >= limit_per_sec:
                return {"status": 429, "body": "slow down", "headers": {}}
            hits.append(now)
            return next_(req)
        return handle
    return mw

def view(req):
    return {"status": 200, "body": f"orders for {req['user']}", "headers": {}}

def build_chain(endpoint, middlewares):
    for mw in reversed(middlewares):          # first in list = outermost
        endpoint = mw(endpoint)
    return endpoint

app = build_chain(view, [request_id, auth, rate_limit(2)])
for token in ["secret", "wrong", "secret", "secret"]:
    r = app({"user": "riya", "token": token})
    print(r["status"], r["body"], r["headers"])
''',
"pythonic": r'''
import logging, io

# stdlib chain: a record goes to the logger's handlers, then propagates to parent loggers
buf = io.StringIO()
root = logging.getLogger(); root.handlers[:] = []
h = logging.StreamHandler(buf); h.setFormatter(logging.Formatter("root handler got: %(name)s %(message)s"))
root.addHandler(h)

app_log = logging.getLogger("shop")
svc_log = logging.getLogger("shop.payments")      # child of "shop", grandchild of root
svc_log.warning("card declined")                  # no handler on shop.payments -> passed up the chain
logging.getLogger("shop.payments").propagate = False
svc_log.warning("this one stops at shop.payments")
print(buf.getvalue().strip())
''',
"pythonic_note": "The <code>logging</code> hierarchy is a chain: records propagate from <code>shop.payments</code> to <code>shop</code> to the root logger unless <code>propagate = False</code> stops them.",
"examples": [
  {"where": "stdlib", "title": "<code>logging</code> propagation", "body": "A record is offered to the handlers of its logger, then to each ancestor's handlers. Setting <code>propagate = False</code> ends the chain; this is how libraries avoid double-logging."},
  {"where": "stdlib", "title": "<code>urllib.request.OpenerDirector</code>", "body": "<code>build_opener()</code> chains handlers (<code>ProxyHandler</code>, <code>HTTPRedirectHandler</code>, <code>HTTPBasicAuthHandler</code>, <code>HTTPSHandler</code>), ordered by <code>handler_order</code>. Each gets a chance to process the request or the error."},
  {"where": "framework", "title": "Django middleware / ASGI (Starlette, FastAPI) middleware", "body": "Each middleware receives <code>get_response</code> (the rest of the chain). <code>SecurityMiddleware</code>, <code>SessionMiddleware</code>, <code>AuthenticationMiddleware</code> and <code>CsrfViewMiddleware</code> run in order, and any can return a response early."},
  {"where": "framework", "title": "Scrapy downloader and spider middlewares", "body": "Requests pass through retry, user-agent, cookies and proxy middlewares; each can modify, drop or replace the request or response."},
  {"where": "production", "title": "Approval workflows and support escalation", "body": "Expense approvals (team lead up to 10k, manager up to 1 lakh, director above), fraud checks (rules engine then ML model then manual review) and ticket escalation are chains where each level decides or forwards."}
],
"use": ["Several independent checks/transformations apply in sequence", "The set or order of handlers should be configurable", "Any handler may need to stop processing early"],
"avoid": ["Every request must be handled by exactly one specific handler: a dict dispatch is clearer", "Long chains where it is hard to see which handler ran (add logging/tracing)"],
"pitfall": "Order bugs: putting rate limiting before authentication lets anonymous floods consume a real user's quota; putting a caching middleware before auth can serve one user's page to another. Order is part of the design.",
"qa": [
  {"q": "How is web middleware an example of Chain of Responsibility?", "a": "<p>Each middleware wraps the next and decides whether to call it. It can modify the request before, the response after, or return early (401, 429, cached response). The view only sees requests that passed the whole chain.</p>"},
  {"q": "Chain of Responsibility vs Decorator?", "a": "<p>The structure is similar (wrappers), but a decorator always delegates and adds behaviour, while a chain handler may <b>stop</b> the request. Middleware is effectively both.</p>"},
  {"q": "What happens if no handler handles the request?", "a": "<p>You must define it: a default final handler (404), an exception, or silently dropping. Leaving it undefined is a common bug.</p>"}
],
"related": ["decorator", "command", "observer"]
},

{
"id": "command", "cat": "behavioral", "name": "Command",
"alias": "Turn a request into an object so it can be queued, logged, retried or undone.",
"simple": "At a restaurant the waiter writes your order on a ticket. The ticket can wait in a queue, be handed to any cook, be cancelled, or be kept for the bill. The ticket is the command: the request itself, written down.",
"intent": """<p>A command object packages an action with everything needed to run it later: the receiver, the method and the arguments. Once a request is an object you can <b>queue</b> it (task queues), <b>schedule</b> it, <b>log</b> it, <b>retry</b> it, send it over the network, and <b>undo</b> it (if it also stores how to reverse itself).</p>
<p>In Python, any callable is already a command: a function, a lambda, a <code>functools.partial</code>, or an object with <code>__call__</code>. Use a class when you need extra methods such as <code>undo()</code> or a serializable description.</p>""",
"structure": """ Invoker (button, queue, scheduler)  --calls-->  Command.execute()
                                                     | knows receiver + args
 history stack: [Insert("Hi"), Bold(0,2), Delete(3)]  --> undo(): pop().undo()""",
"code": r'''
from dataclasses import dataclass, field

class Document:                         # receiver
    def __init__(self): self.text = ""

@dataclass
class Insert:
    doc: Document; pos: int; s: str
    def execute(self): d = self.doc; d.text = d.text[:self.pos] + self.s + d.text[self.pos:]
    def undo(self):    d = self.doc; d.text = d.text[:self.pos] + d.text[self.pos + len(self.s):]

@dataclass
class Delete:
    doc: Document; pos: int; n: int
    removed: str = field(default="", init=False)
    def execute(self):
        d = self.doc; self.removed = d.text[self.pos:self.pos + self.n]
        d.text = d.text[:self.pos] + d.text[self.pos + self.n:]
    def undo(self):
        d = self.doc; d.text = d.text[:self.pos] + self.removed + d.text[self.pos:]

class Editor:                           # invoker keeps history
    def __init__(self, doc): self.doc, self.undo_stack, self.redo_stack = doc, [], []
    def run(self, cmd):
        cmd.execute(); self.undo_stack.append(cmd); self.redo_stack.clear()
    def undo(self):
        cmd = self.undo_stack.pop(); cmd.undo(); self.redo_stack.append(cmd)
    def redo(self):
        cmd = self.redo_stack.pop(); cmd.execute(); self.undo_stack.append(cmd)

doc = Document(); ed = Editor(doc)
ed.run(Insert(doc, 0, "Hello world"));   print(repr(doc.text))
ed.run(Insert(doc, 5, ", dear"));        print(repr(doc.text))
ed.run(Delete(doc, 0, 7));               print(repr(doc.text))
ed.undo();                               print("undo ->", repr(doc.text))
ed.undo();                               print("undo ->", repr(doc.text))
ed.redo();                               print("redo ->", repr(doc.text))
print("history:", [type(c).__name__ for c in ed.undo_stack])
''',
"pythonic": r'''
import functools, queue, threading

# any callable is a command; functools.partial binds the arguments now, runs later
def send_email(to, subject): return f"sent '{subject}' to {to}"

jobs = queue.Queue()
jobs.put(functools.partial(send_email, "a@x.com", "Welcome"))
jobs.put(functools.partial(send_email, "b@x.com", "Invoice INV-42"))
jobs.put(lambda: 1 / 0)                         # a failing command
jobs.put(None)                                  # sentinel: stop worker

def worker():
    while (cmd := jobs.get()) is not None:
        try:
            print("ok  ", cmd())
        except Exception as e:
            print("fail", type(e).__name__, "-> would retry or dead-letter")

t = threading.Thread(target=worker); t.start(); t.join()
''',
"pythonic_note": "A queue of callables plus a worker thread is a tiny task queue. Celery and RQ do the same across machines by serializing the command (task name + arguments) into a message.",
"examples": [
  {"where": "stdlib", "title": "<code>concurrent.futures.Executor.submit(fn, *args)</code>, <code>sched</code>, <code>threading.Timer</code>", "body": "All take a callable plus arguments to execute later or elsewhere. <code>sched.scheduler.enter(delay, priority, action, argument)</code> is a command scheduler in the stdlib."},
  {"where": "stdlib", "title": "IDLE's undo system (<code>idlelib/undo.py</code>)", "body": "IDLE, the editor shipped with Python, records <code>InsertCommand</code> and <code>DeleteCommand</code> objects with <code>do</code>, <code>undo</code> and <code>redo</code>, grouped by <code>CommandSequence</code>: the classic Command-for-undo design."},
  {"where": "framework", "title": "Celery / RQ tasks", "body": "<code>send_invoice.delay(order_id)</code> serializes the command (task name and arguments) into a message on RabbitMQ or Redis. Any worker executes it, with retries, ETA scheduling and result tracking."},
  {"where": "framework", "title": "Django migrations", "body": "Each migration is a list of operation objects (<code>AddField</code>, <code>RunPython</code>, ...) with <code>database_forwards</code> and <code>database_backwards</code>. That is why <code>migrate app 0007</code> can roll the schema back: commands with undo."},
  {"where": "production", "title": "Audit logs and event-sourced systems", "body": "Banking and admin systems store every command (<code>TransferMoney(from, to, amount, by_user)</code>) before executing it, giving an audit trail and the ability to replay or compensate operations."}
],
"use": ["Operations must be queued, scheduled, retried or run on another machine", "You need undo/redo or an audit log of actions", "UI elements should trigger actions without knowing the receiver"],
"avoid": ["A direct function call is all you need: don't wrap every call in a class", "Undo is required but actions have external side effects that cannot be reversed (emails sent)"],
"pitfall": "Undo that re-computes from current state instead of storing what it changed. The Delete command above records <code>removed</code> during <code>execute()</code>; without it, undo cannot restore the text.",
"qa": [
  {"q": "How would you implement undo/redo?", "a": "<p>Represent each action as a command with <code>execute()</code> and <code>undo()</code>. Keep an undo stack and a redo stack: running a new command pushes to undo and clears redo; undo pops from undo, reverses and pushes to redo. Alternatively store Memento snapshots when reversing is hard.</p>"},
  {"q": "Why is Command less visible in Python?", "a": "<p>Functions are first-class objects, so a callable (function, lambda, <code>functools.partial</code>, bound method) already is a command. Classes are needed only for extra behaviour such as undo, serialization or metadata.</p>"},
  {"q": "How does Celery relate to the Command pattern?", "a": "<p>A task call is turned into a message containing the task name and arguments (the command), put on a broker queue (invoker), and executed by a worker (receiver side), with retries and scheduling.</p>"}
],
"related": ["memento", "strategy", "chain-of-responsibility", "observer"]
},

{
"id": "interpreter", "cat": "behavioral", "name": "Interpreter",
"alias": "Represent a small language's grammar as classes and evaluate sentences by walking the tree.",
"simple": "A recipe card is a tiny language: \"if dough is sticky then add flour\". A cook reads each line and acts on it. An interpreter is the cook for your own mini-language.",
"intent": """<p>For a <b>small, stable language</b> (business rules, filters, search queries, config expressions), define one class per grammar rule: literals, variables, <code>and</code>, <code>or</code>, comparisons. A parser turns text into a tree of these nodes, and each node's <code>evaluate(context)</code> computes its value, calling its children.</p>
<p>It lets non-programmers write rules (stored in a DB, changed without deploys) safely, instead of using <code>eval()</code>. For bigger languages use a parser library (Lark, pyparsing) or Python's own <code>ast</code>.</p>""",
"structure": """  "country == 'IN' and total > 1000 or vip == true"
              Or
            /    \\
          And     Eq(vip, true)
         /   \\
  Eq(country,'IN')  Gt(total, 1000)       evaluate(ctx) recurses down the tree""",
"code": r'''
import re
from dataclasses import dataclass

# ---- grammar as classes (the Interpreter pattern)
@dataclass
class Lit:  value: object
@dataclass
class Var:  name: str
@dataclass
class Cmp:  op: str; left: object; right: object
@dataclass
class And:  left: object; right: object
@dataclass
class Or:   left: object; right: object

OPS = {"==": lambda a, b: a == b, "!=": lambda a, b: a != b,
       ">": lambda a, b: a > b, "<": lambda a, b: a < b, ">=": lambda a, b: a >= b}

def evaluate(node, ctx):
    match node:                                     # structural pattern matching (3.10+)
        case Lit(v):          return v
        case Var(name):       return ctx[name]
        case Cmp(op, l, r):   return OPS[op](evaluate(l, ctx), evaluate(r, ctx))
        case And(l, r):       return evaluate(l, ctx) and evaluate(r, ctx)
        case Or(l, r):        return evaluate(l, ctx) or evaluate(r, ctx)

# ---- tiny recursive-descent parser: or_expr := and_expr ('or' and_expr)*
TOKEN = re.compile(r"\s*(?:(\d+\.?\d*)|'([^']*)'|(true|false)\b|(and|or)\b|(==|!=|>=|>|<)|([A-Za-z_]\w*))")

def tokenize(text):
    pos, out = 0, []
    while pos < len(text.rstrip()):
        m = TOKEN.match(text, pos)
        if not m: raise SyntaxError(f"bad input at {pos}: {text[pos:]!r}")
        num, s, boolean, kw, op, name = m.groups()
        out.append(("num", float(num)) if num else ("str", s) if s is not None else
                   ("bool", boolean == "true") if boolean else ("kw", kw) if kw else
                   ("op", op) if op else ("name", name))
        pos = m.end()
    return out

def parse(text):
    toks = tokenize(text); i = 0
    def peek(): return toks[i] if i < len(toks) else (None, None)
    def atom():
        nonlocal i
        kind, val = toks[i]; i += 1
        return Var(val) if kind == "name" else Lit(val)
    def comparison():
        nonlocal i
        left = atom()
        if peek()[0] == "op":
            op = toks[i][1]; i += 1
            return Cmp(op, left, atom())
        return left
    def and_expr():
        nonlocal i
        node = comparison()
        while peek() == ("kw", "and"): i += 1; node = And(node, comparison())
        return node
    def or_expr():
        nonlocal i
        node = and_expr()
        while peek() == ("kw", "or"): i += 1; node = Or(node, and_expr())
        return node
    tree = or_expr()
    if i != len(toks):
        raise SyntaxError(f"unexpected token {toks[i]}")
    return tree

rule = parse("country == 'IN' and total > 1000 or vip == true")   # stored in DB by ops team
print(rule)
orders = [{"country": "IN", "total": 2500, "vip": False},
          {"country": "US", "total": 9000, "vip": False},
          {"country": "US", "total": 10,   "vip": True}]
for o in orders:
    print(o, "-> free shipping:", evaluate(rule, o))
''',
"pythonic": r'''
import ast, operator

# Python's own parser + a whitelist evaluator: safe arithmetic without eval()
OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
       ast.Div: operator.truediv, ast.USub: operator.neg}

def calc(expr: str, **vars):
    def ev(n):
        match n:
            case ast.Expression(body): return ev(body)
            case ast.Constant(value=v) if isinstance(v, (int, float)): return v
            case ast.Name(id=name) if name in vars: return vars[name]
            case ast.BinOp(l, op, r) if type(op) in OPS: return OPS[type(op)](ev(l), ev(r))
            case ast.UnaryOp(op, x) if type(op) in OPS: return OPS[type(op)](ev(x))
        raise ValueError(f"not allowed: {ast.dump(n)[:40]}")
    return ev(ast.parse(expr, mode="eval"))

print(calc("price * qty * (1 - discount)", price=499, qty=3, discount=0.1))
try:
    calc("__import__('os').system('rm -rf /')")
except ValueError as e:
    print("rejected:", e)
print(ast.literal_eval("{'retries': 3, 'hosts': ['a', 'b']}"))   # stdlib safe literal interpreter
''',
"pythonic_note": "Reuse Python's parser (<code>ast.parse</code>) and interpret only the node types you whitelist. <code>ast.literal_eval</code> is the stdlib's safe interpreter for literals. Never <code>eval()</code> user input.",
"examples": [
  {"where": "stdlib", "title": "<code>re</code>, <code>fnmatch</code>, <code>string.Template</code>", "body": "Regular expressions are a language: <code>re.compile</code> parses the pattern and compiles it into code for the regex engine. <code>fnmatch.translate</code> turns shell globs into regexes; <code>string.Template</code> interprets <code>$name</code> placeholders."},
  {"where": "stdlib", "title": "<code>ast</code> and <code>ast.literal_eval</code>", "body": "<code>ast.parse</code> turns source into a node tree; <code>literal_eval</code> safely interprets only literals (numbers, strings, lists, dicts), which is why it is the safe replacement for <code>eval</code> on config strings."},
  {"where": "framework", "title": "Jinja2, SQLAlchemy expressions, pandas <code>query()</code>", "body": "Jinja2 parses templates into an AST and compiles them to Python. SQLAlchemy builds expression trees (<code>User.age > 30</code>) that are rendered per SQL dialect. <code>df.query('price > 100 and region == \"IN\"')</code> interprets a filter language."},
  {"where": "framework", "title": "Parser libraries: Lark, pyparsing, SymPy", "body": "Lark and pyparsing build interpreters for larger DSLs from a grammar. SymPy represents math expressions as trees (<code>Add</code>, <code>Mul</code>, <code>Symbol</code>) and evaluates, simplifies or differentiates them."},
  {"where": "production", "title": "Rules engines for pricing, fraud and alerting", "body": "Ops or risk teams write rules like <code>amount > 50000 and country != 'IN'</code> in an admin UI; the service parses them into a tree once and evaluates each transaction, so rule changes need no deployment. Alert rules in monitoring tools (PromQL) are interpreted the same way."}
],
"use": ["A small language changes often and must be edited by non-developers", "Rules must be stored as data and evaluated safely", "The grammar is simple and stable"],
"avoid": ["The grammar is large: use a parser generator (Lark) or an existing language", "Performance-critical evaluation of complex expressions: compile to Python or SQL instead"],
"pitfall": "Using <code>eval()</code> as the interpreter. Even with <code>{'__builtins__': {}}</code> it can be escaped. Parse and evaluate only an explicit whitelist of node types.",
"qa": [
  {"q": "When is the Interpreter pattern a good fit?", "a": "<p>For small DSLs such as business rules, filters, query syntax or feature-flag conditions, where the grammar is simple, rules are data, and safety matters more than raw speed.</p>"},
  {"q": "How do you safely evaluate a user-supplied expression in Python?", "a": "<p>Parse it with <code>ast.parse(mode='eval')</code> and walk the tree, allowing only whitelisted nodes (constants, names from a given dict, specific operators). For literals only, use <code>ast.literal_eval</code>. Never use <code>eval</code>.</p>"},
  {"q": "How does Interpreter relate to Composite and Visitor?", "a": "<p>The expression tree is a Composite (And/Or contain sub-expressions). Evaluation can live in each node (classic Interpreter) or in a separate Visitor / <code>match</code> function, which makes adding new operations (pretty-print, to-SQL) easier.</p>"}
],
"related": ["composite", "visitor", "strategy"]
},

{
"id": "iterator", "cat": "behavioral", "name": "Iterator",
"alias": "Access elements of a collection one by one without exposing how it is stored.",
"simple": "A TV remote's \"next channel\" button. You don't need to know how channels are stored or numbered inside the TV; you just press next until you've seen what you want.",
"intent": """<p>An iterator gives sequential access with one operation, "give me the next item", and hides whether items come from a list, a tree, a file, a database cursor or a paginated API. It is <b>lazy</b>: items are produced on demand, so you can stream data far larger than memory, or even infinite sequences.</p>
<p>Iterator is built into Python: an <b>iterable</b> has <code>__iter__()</code> returning an <b>iterator</b>, which has <code>__next__()</code> and raises <code>StopIteration</code> at the end. <code>for</code> loops, comprehensions, <code>zip</code>, <code>sum</code> and unpacking all use this protocol. Generators (<code>yield</code>) are the easiest way to write one.</p>""",
"structure": """ for order in OrdersApi(customer):     <- iterable
     ...                                   iter() -> iterator; next() -> item
   page 1 [o1 o2 o3] -> page 2 [o4 o5] -> StopIteration
   (next page fetched only when the loop reaches it)""",
"code": r'''
class OrdersApi:
    """Iterable over a paginated REST API: callers never see pages."""
    PAGES = {None: (["o1", "o2", "o3"], "p2"), "p2": (["o4", "o5"], "p3"), "p3": (["o6"], None)}

    def __init__(self, customer): self.customer = customer

    def _fetch(self, cursor):
        print(f"  GET /customers/{self.customer}/orders?cursor={cursor}")
        return self.PAGES[cursor]

    def __iter__(self):                          # generator = iterator for free
        cursor = None
        while True:
            items, cursor = self._fetch(cursor)
            yield from items
            if cursor is None:
                return

class Countdown:
    """The explicit protocol, without a generator."""
    def __init__(self, start): self.n = start
    def __iter__(self): return self
    def __next__(self):
        if self.n <= 0: raise StopIteration
        self.n -= 1
        return self.n + 1

print(list(Countdown(3)))

from itertools import islice
print("first 4 only:")
print(list(islice(OrdersApi("C-9"), 4)))         # page 3 is never requested
''',
"pythonic": r'''
import itertools

def read_log(lines):                             # imagine: open("huge.log") -> 50 GB
    for line in lines:
        yield line.rstrip()

logs = (f"2026-09-28 {'ERROR' if i % 4 == 0 else 'INFO'} request {i}" for i in itertools.count())
errors = (l for l in read_log(logs) if " ERROR " in l)     # nothing has run yet
for line in itertools.islice(errors, 3):                   # pulls just enough items
    print(line)

pairs = zip(["a", "b", "c"], itertools.count(1))
print(dict(pairs))
print(list(itertools.batched(range(7), 3)))                # Python 3.12+
''',
"pythonic_note": "Generator expressions and <code>itertools</code> let you process infinite or huge streams lazily. <code>itertools.batched</code> (3.12+) chunks any iterator, useful for bulk database inserts.",
"examples": [
  {"where": "stdlib", "title": "The iterator protocol and generators", "body": "Files iterate lines, dicts iterate keys, <code>range</code> is lazy, <code>os.scandir</code> yields directory entries, <code>csv.reader</code> yields rows. All work in <code>for</code> loops because they implement <code>__iter__</code>/<code>__next__</code>."},
  {"where": "stdlib", "title": "<code>itertools</code>", "body": "<code>islice</code>, <code>chain</code>, <code>groupby</code>, <code>pairwise</code>, <code>batched</code>, <code>tee</code> and <code>count</code> compose iterators without building lists, the foundation of memory-efficient data processing in pure Python."},
  {"where": "framework", "title": "Django <code>QuerySet.iterator(chunk_size=2000)</code>", "body": "Streams rows from the database cursor instead of loading every model instance into memory at once, which is essential for exports and data migrations over millions of rows."},
  {"where": "framework", "title": "boto3 paginators and pandas <code>read_csv(chunksize=...)</code>", "body": "<code>s3.get_paginator('list_objects_v2').paginate(Bucket=b)</code> hides continuation tokens. <code>pd.read_csv(path, chunksize=100_000)</code> returns an iterator of DataFrames for files larger than RAM."},
  {"where": "production", "title": "ETL jobs and log processing", "body": "Nightly jobs stream records from an API or file, transform them with generators and write in batches. Memory stays flat whether the input has ten thousand or ten billion rows."}
],
"use": ["Traversing a collection whose structure should stay hidden (tree, API, DB)", "Data is large, remote or infinite and should be produced lazily", "You want the same loop code to work over many sources"],
"avoid": ["You need random access or <code>len()</code> repeatedly: materialize a list", "The same data must be iterated many times: an iterator is exhausted after one pass"],
"pitfall": "Iterating an iterator twice: the second loop silently gets nothing. <code>gen = (x for x in data); sum(gen); max(gen)</code> fails with an empty sequence. Make the class an iterable (new iterator per <code>__iter__</code>) or use <code>itertools.tee</code>/a list.",
"qa": [
  {"q": "Iterable vs iterator?", "a": "<p>An iterable has <code>__iter__()</code> and can be looped over many times (list, dict, a class like <code>OrdersApi</code>). An iterator has <code>__next__()</code>, keeps position and is consumed once; its <code>__iter__</code> returns itself. <code>iter(iterable)</code> gives a fresh iterator.</p>"},
  {"q": "What is the advantage of generators?", "a": "<p>They produce values lazily with little memory, keep local state between <code>yield</code>s automatically, and make pipeline code simple. <code>yield from</code> delegates to a sub-iterator.</p>"},
  {"q": "How would you process a 50 GB log file in Python?", "a": "<p>Iterate the file object line by line (it is already a lazy iterator), filter and transform with generators, aggregate incrementally (counters), and write results in batches. Never call <code>read()</code> or <code>readlines()</code> on it.</p>"}
],
"related": ["pipeline", "composite", "visitor"]
},

{
"id": "mediator", "cat": "behavioral", "name": "Mediator",
"alias": "Objects talk to a central coordinator instead of referencing each other directly.",
"simple": "Planes don't radio each other to decide who lands first. They all talk to the control tower, which knows the runways and tells each plane when to land. Add a new plane and nothing changes for the others.",
"intent": """<p>When many objects interact, direct references create a tangled web (N x N connections). A mediator centralizes the interaction rules: components notify the mediator about events, and the mediator decides who else needs to act. Components become reusable because they only know the mediator.</p>
<p>Typical examples: a form dialog where widgets enable/disable each other, a chat room, a workflow coordinator, an air-traffic or resource scheduler. At system scale, a message broker plays the mediator role between services.</p>""",
"structure": """  Without:  A <-> B <-> C <-> D  (everyone knows everyone)
  With:          A   B
                  \\ /
               [Tower]      components -> notify(event) -> mediator decides
                  / \\
                 C   D""",
"code": r'''
class ControlTower:                              # the mediator
    def __init__(self, runways):
        self.free = list(runways)
        self.waiting = []

    def request_landing(self, plane):
        if self.free:
            runway = self.free.pop(0)
            plane.clear_to_land(runway)
        else:
            self.waiting.append(plane)
            plane.hold(len(self.waiting))

    def runway_vacated(self, runway):
        if self.waiting:
            self.waiting.pop(0).clear_to_land(runway)
        else:
            self.free.append(runway)

class Plane:                                     # colleague: knows only the tower
    def __init__(self, code, tower): self.code, self.tower = code, tower
    def approach(self):              self.tower.request_landing(self)
    def clear_to_land(self, rw):     print(f"{self.code}: cleared to land on {rw}"); self.runway = rw
    def hold(self, pos):             print(f"{self.code}: holding, position {pos}")
    def taxi_off(self):              print(f"{self.code}: left {self.runway}"); self.tower.runway_vacated(self.runway)

tower = ControlTower(["09L", "09R"])
planes = [Plane(c, tower) for c in ["AI101", "6E202", "UK303", "QP404"]]
for p in planes: p.approach()
planes[0].taxi_off()
planes[1].taxi_off()
''',
"pythonic": r'''
import queue, threading

# stdlib mediator between threads: producers and consumers never reference each other
jobs = queue.Queue(maxsize=3)                  # coordinates hand-off and back-pressure
def producer(name, n):
    for i in range(n): jobs.put(f"{name}-{i}")
def consumer(done):
    while (item := jobs.get()) is not None:
        done.append(item); jobs.task_done()

done = []
c = threading.Thread(target=consumer, args=(done,)); c.start()
ps = [threading.Thread(target=producer, args=(n, 3)) for n in ("scanner", "upload")]
for p in ps: p.start()
for p in ps: p.join()
jobs.join(); jobs.put(None); c.join()
print(sorted(done))
''',
"pythonic_note": "<code>queue.Queue</code> mediates between threads: producers and consumers only know the queue, which also applies back-pressure when <code>maxsize</code> is reached.",
"examples": [
  {"where": "stdlib", "title": "<code>queue.Queue</code> / <code>asyncio.Queue</code>", "body": "Producers and consumers never hold references to each other; the queue coordinates hand-off, blocking and back-pressure. Adding more consumers changes nothing for producers."},
  {"where": "stdlib", "title": "<code>asyncio</code> event loop", "body": "Coroutines don't wake each other up directly. They await futures, and the event loop, as the central coordinator, watches sockets and timers and resumes the right task when its I/O is ready."},
  {"where": "framework", "title": "Qt / tkinter dialogs", "body": "In a PyQt or tkinter form, the dialog class usually acts as the mediator: widgets emit signals (\"country changed\") and the dialog updates the state list, enables the submit button and validates, so widgets stay reusable."},
  {"where": "framework", "title": "Workflow orchestrators: Airflow, Prefect", "body": "Tasks declare dependencies; the scheduler decides when each runs based on the others' results. Tasks never call each other, which makes them independently retryable."},
  {"where": "production", "title": "Message brokers between microservices", "body": "Services publish to Kafka or RabbitMQ instead of calling each other; the broker routes messages, buffers spikes and lets new consumers join without changing producers."}
],
"use": ["Many objects interact in complex ways and direct references are becoming a web", "You want components reusable in other contexts", "Interaction rules should live in one place"],
"avoid": ["Only two or three objects interact simply", "The mediator starts containing all business logic (a god object)"],
"pitfall": "The mediator grows into a giant class that everything depends on. Split it by use case (one mediator per dialog or workflow) and keep domain logic in the components.",
"qa": [
  {"q": "Mediator vs Observer?", "a": "<p>Observer is one-to-many broadcast: the subject doesn't know or care what observers do. Mediator encapsulates <b>how</b> a group of objects interact: it receives events and actively decides who does what. Mediators are often implemented using observer-style notifications.</p>"},
  {"q": "Mediator vs Facade?", "a": "<p>A Facade simplifies access to a subsystem for outside clients; subsystem objects don't know the facade. A Mediator coordinates peers, and those peers do know and talk to the mediator.</p>"},
  {"q": "What is the main risk of Mediator?", "a": "<p>Centralizing too much: the mediator becomes a complex, hard-to-test god object. Keep it focused on coordination.</p>"}
],
"related": ["observer", "facade", "command"]
},

{
"id": "memento", "cat": "behavioral", "name": "Memento",
"alias": "Capture an object's internal state as a snapshot so it can be restored later.",
"simple": "Saving a video game before the boss fight. The save file captures everything you need, and if you lose you reload it. You never need to know how the game stores health or inventory internally.",
"intent": """<p>A memento is an opaque snapshot of an object's state. The <b>originator</b> creates it (<code>save()</code>) and restores from it (<code>restore(m)</code>). A <b>caretaker</b> (undo history, checkpoint manager) stores mementos without looking inside. Encapsulation is preserved: only the originator understands the snapshot.</p>
<p>Use it for undo, checkpoints, transactions and "what-if" experiments. Compared to Command-based undo it is simpler (just restore) but can use more memory, so store diffs or limit history for large states.</p>""",
"structure": """ Originator (Editor)  --save()-->  Memento (frozen snapshot)  --> Caretaker.history [m1, m2, m3]
 Originator.restore(history.pop())   <- caretaker never reads the memento's contents""",
"code": r'''
from dataclasses import dataclass
import copy

@dataclass(frozen=True)
class CartMemento:                               # opaque, immutable snapshot
    _items: tuple
    _coupon: str | None

class ShoppingCart:                              # originator
    def __init__(self): self.items, self.coupon = {}, None
    def add(self, sku, qty): self.items[sku] = self.items.get(sku, 0) + qty
    def apply_coupon(self, code): self.coupon = code
    def save(self) -> CartMemento:
        return CartMemento(tuple(sorted(self.items.items())), self.coupon)
    def restore(self, m: CartMemento):
        self.items, self.coupon = dict(m._items), m._coupon
    def __repr__(self): return f"Cart({self.items}, coupon={self.coupon})"

class History:                                   # caretaker
    def __init__(self, limit=20): self._stack, self._limit = [], limit
    def push(self, m): self._stack = (self._stack + [m])[-self._limit:]
    def pop(self): return self._stack.pop()

cart, history = ShoppingCart(), History()
history.push(cart.save()); cart.add("SKU-1", 2)
history.push(cart.save()); cart.add("SKU-2", 1); cart.apply_coupon("DIWALI20")
print("now:        ", cart)
cart.restore(history.pop()); print("undo:       ", cart)
cart.restore(history.pop()); print("undo again: ", cart)

# "what-if": try a change on a snapshot, keep the original safe
checkpoint = cart.save()
cart.add("SKU-9", 100)
print("experiment: ", cart)
cart.restore(checkpoint); print("rolled back:", cart)
''',
"pythonic": r'''
import random, pickle

# stdlib memento 1: the RNG's internal state (625 numbers) as an opaque object
state = random.getstate()
first = [random.randint(1, 100) for _ in range(5)]
random.setstate(state)                      # restore the snapshot
again = [random.randint(1, 100) for _ in range(5)]
print(first, first == again)

# stdlib memento 2: __getstate__/__setstate__ control what a snapshot contains
class Session:
    def __init__(self, user): self.user, self.cache, self.conn = user, {"k": 1}, object()
    def __getstate__(self):  return {"user": self.user}          # snapshot omits cache + live connection
    def __setstate__(self, s): self.__init__(s["user"])          # rebuilt fresh on load
blob = pickle.dumps(Session("riya"))
restored = pickle.loads(blob)
print(restored.user, restored.cache, len(blob), "bytes")
''',
"pythonic_note": "<code>random.getstate()</code>/<code>setstate()</code> is a textbook memento in the stdlib. <code>__getstate__</code>/<code>__setstate__</code> let a class decide what goes into a pickle snapshot.",
"examples": [
  {"where": "stdlib", "title": "<code>random.getstate()</code> / <code>setstate()</code>", "body": "Returns the generator's entire internal state as an opaque object. Simulations and tests save it to replay exactly the same random sequence later."},
  {"where": "stdlib", "title": "<code>pickle</code> with <code>__getstate__</code> / <code>__setstate__</code>", "body": "The object decides what its snapshot contains (for example dropping a socket or a cache) and how to rebuild itself. <code>copyreg</code> customizes this for classes you don't own."},
  {"where": "framework", "title": "PyTorch <code>state_dict()</code> / <code>load_state_dict()</code>", "body": "Training checkpoints save the model's and optimizer's state dicts every epoch. After a crash, or to roll back a diverging run, you restore the last good snapshot without touching the model's code."},
  {"where": "framework", "title": "Django <code>transaction.atomic()</code> savepoints", "body": "A nested <code>atomic()</code> block creates a database savepoint; if the block raises, the database rolls back to that snapshot while the outer transaction continues."},
  {"where": "production", "title": "Undo history, drafts and game saves", "body": "Document editors, form wizards (\"back\" restores previous answers), configuration tools (\"revert to last applied config\") and games keep bounded histories of snapshots."}
],
"use": ["Undo, rollback, checkpoints or \"what-if\" experiments", "State must be restored without exposing internals to the caller"],
"avoid": ["State is huge and changes often: store diffs or use Command-based undo", "State includes external effects (sent emails, charged cards) that restoring memory cannot undo"],
"pitfall": "Shallow snapshots: saving <code>self.items</code> (the same dict) instead of a copy means later edits change the \"snapshot\" too. The example stores an immutable tuple for that reason.",
"qa": [
  {"q": "Memento vs Command for undo?", "a": "<p>Memento stores full state snapshots: simple and reliable, but memory-heavy. Command stores the operation and its inverse: memory-light, but every command needs a correct <code>undo()</code>. They are often combined: a command keeps a memento of the part it changes.</p>"},
  {"q": "How does Memento preserve encapsulation?", "a": "<p>The caretaker stores the memento but never reads or modifies it; only the originator knows its structure. In Python this is by convention (underscore fields, frozen dataclass) rather than enforced.</p>"},
  {"q": "How would you implement checkpointing for a long-running job?", "a": "<p>Periodically serialize the essential state (position in input, partial aggregates, RNG state, model weights) atomically to durable storage (write temp file, then rename). On start, load the latest checkpoint if present and resume from there.</p>"}
],
"related": ["command", "prototype", "state"]
},

]
