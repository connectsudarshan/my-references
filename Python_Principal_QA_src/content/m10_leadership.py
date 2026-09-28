MODULE = dict(id=10, title="Technical Leadership & System Design",
              desc="How a Principal engineer decides and influences: rewrite requests, risky pull requests, org-wide standards, end-to-end results pipelines, silent-failure postmortems, mentoring and language choices.")

QUESTIONS = [

P("Scenario", "The team wants to rewrite the 8-year-old Python test framework from scratch. How do you respond?",
short="""Start from the problems, not the proposal: list the concrete pains (slow runs, flaky infra, hard to add devices, no typing), measure them, and check which are architectural and which are fixable locally. Usually I'd recommend an incremental "strangler" migration: define the target architecture, build new pieces behind stable interfaces, and move suites over in waves with measurable milestones. A full rewrite is justified only when the core model is wrong and incremental change costs more.""",
deep="""Why rewrites fail: the old system encodes years of hardware quirks and edge cases nobody documented; the rewrite takes 2-3x longer than planned; feature work freezes; and the new system ships with fewer capabilities and new bugs, while validation of product firmware can't pause.

How I'd run the decision:

1. **Problem inventory** with data: runtime per suite, flake rate, time to onboard a new device type, bug counts by framework area, developer survey.
2. **Options**: (a) targeted fixes, (b) incremental re-architecture (strangler), (c) rewrite. Estimate cost, risk and time-to-value for each.
3. **Recommendation** in a short design doc/ADR, reviewed by stakeholders (test engineers, firmware teams, lab ops).
4. **Execution for (b)**: new HAL and results layer first, adapters so old tests run on the new core, migrate one product line as a pilot, track "percent of tests on new core" and the pain metrics, keep a fixed end date for the old system.

Leadership aspects: acknowledge the team's frustration (it's valid data), make the trade-offs visible, and keep ownership with the team: they should own the migration plan, not receive it.""",
follow=(
"The team insists and management supports a rewrite anyway. What do you do? => Disagree and commit, but de-risk: insist on a parity test suite (the old framework's verdicts on the same builds as acceptance criteria), a pilot scope, shipping in slices, and a checkpoint where the plan is re-evaluated with data.",
"How do you measure whether the migration is succeeding? => Share of tests on the new core, flake rate and runtime per suite, time to add a device type, and developer satisfaction, reviewed monthly.",
),
pitfall="Approving or rejecting the rewrite on taste or seniority. Both the team's pain and the rewrite risk need evidence, and the decision should be written down with its reasoning.",
signals="You separate problems from the proposed solution, gather data, compare options including incremental migration, write the decision down, and handle the people side (buy-in, disagree-and-commit).",
),

P("Code review", "A PR adds threads to speed up a test suite by running 8 device tests in parallel inside one process. What do you look for?",
short="""Correctness under concurrency before speed: shared mutable state (module globals, class attributes, caches, the results list), thread safety of the device SDK and logging context, per-device isolation of fixtures, error propagation from threads (exceptions in `Thread` targets are silently printed, not raised), timeouts and cancellation, and how results and logs are attributed to each device. Then check the speed claim with measurements and whether asyncio or processes fit better.""",
deep="""Concrete review checklist:

- **Error propagation**: `threading.Thread(target=...)` swallows exceptions into stderr; the test run may report success. Prefer `ThreadPoolExecutor` and call `future.result()` (re-raises), or `concurrent.futures.wait` with explicit error handling.
- **Shared state**: `results.append` is fine but `counter += 1`, dict check-then-set, and shared config mutation aren't; look for module-level state in helpers.
- **Library thread safety**: vendor SDK handles, serial ports and some CLI wrappers are not thread-safe; one handle per device, or serialize access.
- **Context**: logs must carry the device ID (contextvars), otherwise interleaved lines are useless.
- **Timeouts**: a hung device thread can't be killed; every blocking call needs a timeout; the pool shutdown must not wait forever.
- **Resource limits**: 8 parallel tests may exceed host limits (PCIe bandwidth, CPU for verification, power supply).
- **Measurement**: before/after wall-clock on the real rack, and whether the work is I/O-bound (threads fine) or CPU-bound (processes needed).

Tone: acknowledge the valuable goal, mark the silent-exception issue as blocking with a small reproducer, suggest the executor pattern.""",
code=r'''
import threading, concurrent.futures as cf

def device_test(sn):
    if sn == "SN003":
        raise RuntimeError(f"{sn}: read-back mismatch at LBA 0x7f00")
    return f"{sn}: PASS"

# As submitted: exceptions in Thread targets never reach the caller
results = []
def target(sn): results.append(device_test(sn))
threading.excepthook = lambda args: None             # (hide the default stderr print for this demo)
ts = [threading.Thread(target=target, args=(f"SN00{i}",)) for i in range(1, 5)]
[t.start() for t in ts]; [t.join() for t in ts]
print("threads version: suite looks green ->", len(results), "results, no error raised")

# Suggested: executor + future.result() re-raises and attributes failures
with cf.ThreadPoolExecutor(max_workers=8, thread_name_prefix="dev") as ex:
    futures = {ex.submit(device_test, f"SN00{i}"): f"SN00{i}" for i in range(1, 5)}
    for fut in cf.as_completed(futures):
        try:
            print("  ", fut.result(timeout=60))
        except Exception as e:
            print("   FAIL", futures[fut], "->", e)
''',
follow=(
"The author says the SDK is thread-safe because it didn't crash in their test run. Is that enough? => No; races are probabilistic. Check vendor documentation, look for shared global state in the SDK, and stress test with many iterations; if unsure, isolate one SDK handle per device or use processes.",
"When would you suggest asyncio or processes instead? => asyncio if the work is mainly waiting on subprocesses/sockets and you want clean timeouts; processes if verification is CPU-heavy or the SDK isn't thread-safe.",
),
pitfall="Approving because the suite got faster and stayed green, when in fact failures in worker threads were silently dropped.",
signals="You prioritize silent-failure and shared-state risks, check library thread safety, context and timeouts, demand measurements, and give a concrete safer pattern.",
),

P("Scenario", "How would you establish Python engineering standards across 8 teams without becoming a bottleneck?",
short="""Automate what can be automated, and write down the few decisions that can't. Provide shared tooling (a project template, pre-commit config, Ruff/mypy/pytest settings, CI templates) so the standard is the default; keep a short living guideline for design decisions; record significant choices as ADRs; build a small guild of champions from each team who own the standards with you; and measure adoption instead of policing individual PRs.""",
deep="""Principles:

- **Paved road over rulebook**: a `cookiecutter`/`copier` template with packaging, lint, typing, tests and CI already wired; teams adopting it get compliance for free. Updates propagate via template updates or shared CI configs.
- **Automate style**: formatting and most lint rules are enforced by tools, so human review focuses on design. No debates about quotes or line length.
- **Decide once, document why**: ADRs for things like "asyncio for orchestration", "Pydantic at boundaries", "no pickle for interchange". Link them from the guideline.
- **Guild/champions**: one engineer per team in a monthly forum proposing and reviewing changes; standards become shared ownership, not a Principal's decree.
- **Adoption metrics**: repos on the template, CI gate coverage, typing ratchet progress, dependency freshness.
- **Escape hatches**: documented, time-limited exceptions, so teams aren't blocked by edge cases.
- **Teach**: short internal talks and examples of real bugs the standards would have prevented; that persuades better than rules.""",
follow=(
"A senior engineer on another team refuses to adopt the type checker. How do you handle it? => Understand the objection (noise, slow tooling, legacy code), offer a lower-friction start (only new modules, relaxed config), show concrete value from their own bug history, and involve their team's champion; escalate only if it blocks shared work.",
"How do you keep standards from going stale? => Review them twice a year in the guild, retire rules nobody values, and let tool upgrades (new Ruff rules, Python versions) drive incremental updates through the template.",
),
pitfall="Publishing a 40-page style guide and personally reviewing every PR for compliance. It doesn't scale and creates resentment.",
signals="You rely on automation and templates, record decisions with reasons, share ownership through champions, measure adoption, and plan for exceptions and evolution.",
),

P("Design", "Design an end-to-end system for collecting, storing and analysing results from thousands of test runs per day across labs.",
short="""Tests emit versioned, structured result events (run, device, firmware, test, verdict, metrics, artifact links) to a durable ingestion path (message queue or HTTP collector with local spooling), a consumer validates and writes them to a relational store for queries (PostgreSQL) plus object storage for large artifacts (logs, traces, dumps), and dashboards and triage tools read from there. Design for schema evolution, idempotent ingestion, and traceability to exact code and firmware.""",
deep="""Clarify: volume (runs/day, artifact sizes), latency needs (live dashboards vs next-morning reports), retention, and consumers (firmware devs, managers, lab ops).

Components:

- **Event schema**: a versioned JSON (or Protobuf) document with a `schema_version`, a stable unique `result_id` (for idempotency), and context: framework commit, firmware build, device serial and model, host, config hash, seed.
- **Producer side**: the framework writes events to a local spool first (durable if the network is down), then ships them. Never lose results because the collector was unavailable.
- **Ingestion**: a collector service or queue (Kafka/RabbitMQ/SQS). Consumers validate against the schema, upsert by `result_id`, and send invalid events to a dead-letter queue with alerts.
- **Storage**: PostgreSQL (or a warehouse) for structured results and trends; object storage for artifacts, referenced by URL and checksum; retention policies by artifact type.
- **Analysis**: dashboards (pass rate by firmware build, new failures, flake rates), automatic triage (group failures by signature: error message hash + test + firmware area), and links from each failure to logs.
- **Evolution**: additive schema changes are backward compatible; breaking changes bump the version and consumers support N and N-1.""",
code=r'''
import json, uuid, hashlib

SCHEMA_VERSION = 2
def result_event(run_id, device, fw, test, verdict, metrics, error=None):
    signature = hashlib.sha1(f"{test}|{(error or '').split(' at ')[0]}".encode()).hexdigest()[:10] if error else None
    return {"schema_version": SCHEMA_VERSION, "result_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{run_id}/{device}/{test}")),
            "run_id": run_id, "device": device, "firmware": fw, "test": test, "verdict": verdict,
            "metrics": metrics, "error": error, "failure_signature": signature}

REQUIRED = {"schema_version", "result_id", "run_id", "device", "firmware", "test", "verdict"}
def ingest(store, event):
    missing = REQUIRED - event.keys()
    if missing: return f"dead-letter: missing {sorted(missing)}"
    if event["schema_version"] not in (1, 2): return "dead-letter: unknown schema"
    store[event["result_id"]] = event                         # upsert: re-sent events don't duplicate
    return "stored"

store = {}
events = [result_event("n-0928", "SN001", "2.1.7", "trim_basic", "PASS", {"iops": 612000}),
          result_event("n-0928", "SN002", "2.1.7", "pwr_loss", "FAIL", {}, "stale data at LBA 0x1f40"),
          result_event("n-0928", "SN009", "2.1.7", "pwr_loss", "FAIL", {}, "stale data at LBA 0x88a0")]
for e in events + [events[0], {"device": "SN003"}]:
    print(ingest(store, e))
sigs = {e["failure_signature"] for e in store.values() if e["failure_signature"]}
print(len(store), "unique results |", len(sigs), "failure signature(s) -> one triage ticket for both drives")
print(json.dumps(events[1])[:120] + "...")
''',
follow=(
"How do you avoid losing results when the collector is down during a 3-day run? => Local durable spool (append-only file or SQLite) on the test host, background shipper with retries, and idempotent `result_id`s so re-sending is safe.",
"How would you automatically group thousands of failures into a few triage items? => Normalize error messages (strip addresses, LBAs, timestamps), hash with test name and firmware component into a signature, and group by signature across devices and runs.",
),
pitfall="Parsing JUnit XML or console logs after the fact as the only results source: context (firmware, device, config) gets lost and every consumer writes its own fragile parser.",
signals="You clarify requirements, design a versioned schema with idempotency and traceability, handle offline producers, validation and dead letters, split structured data from artifacts, and add automated triage.",
),

P("Scenario", "The nightly regression silently stopped running for a week before anyone noticed. You lead the postmortem. What happens?",
short="""Run a blameless postmortem: build the timeline from logs and scheduler history, find the root cause and the contributing factors (why it broke, and why nobody noticed for a week), assess impact (which firmware builds shipped without regression coverage), and agree on actions with owners and dates. The most important fix is usually **detection**: a dead-man's-switch alert that fires when expected results don't arrive, plus making failures loud instead of silent.""",
deep="""Structure of the postmortem:

1. **Timeline**: last successful run, the change or event that broke it (expired credential, scheduler config change, full disk, a Python dependency update), the moment it was noticed and how.
2. **Root cause and contributing factors**: e.g. "the cron job ran but the orchestrator exited 0 after failing to reserve devices", "results dashboard showed the last successful run without a date warning", "alerts only fired on test failures, not on absence of runs".
3. **Impact**: which builds were not regression-tested; decide whether to re-run the missed coverage on those builds now.
4. **Actions**, each with an owner and due date (typical list below).
5. **Blameless culture**: focus on system gaps; the person who made the config change helps design the safeguard.

Typical actions:

- dead-man's switch: alert if no completed nightly results within 26 hours
- non-zero exit codes for infrastructure failures and an explicit BLOCKED status
- dashboard shows "last run: N hours ago" in red when stale
- credential expiry monitoring
- a synthetic canary test that must always run and pass""",
code=r'''
from datetime import datetime, timedelta, timezone

def dead_mans_switch(last_completed: datetime, now: datetime, max_age=timedelta(hours=26)):
    age = now - last_completed
    status = "ALERT: nightly results missing" if age > max_age else "ok"
    return f"last nightly completed {age.total_seconds() / 3600:5.1f} h ago -> {status}"

now = datetime(2026, 9, 28, 9, 0, tzinfo=timezone.utc)
print(dead_mans_switch(datetime(2026, 9, 28, 3, 40, tzinfo=timezone.utc), now))
print(dead_mans_switch(datetime(2026, 9, 21, 3, 40, tzinfo=timezone.utc), now))

def orchestrator_exit_code(reserved_devices, results):
    if reserved_devices == 0: return 3          # infrastructure failure must NOT look like success
    if any(r == "FAIL" for r in results): return 1
    return 0
print("exit code when no devices could be reserved:", orchestrator_exit_code(0, []))
''',
follow=(
"How do you decide whether to re-run the missed week of coverage? => Check which firmware builds were released or promoted during the gap, prioritize those, and run the regression on them now; document the residual risk for builds you can't cover.",
"How do you make sure postmortem actions actually get done? => Track them as tickets with owners and dates, review them in a recurring meeting, and close the postmortem only when detection actions are verified (e.g. by deliberately triggering the alert).",
),
pitfall="Stopping at the immediate cause (\"the credential expired, renewed it\") without fixing why a week passed before anyone noticed.",
signals="You run it blameless, separate root cause from detection gaps, assess product impact, and produce owned actions centred on monitoring for absence of success.",
),

P("Scenario", "A talented engineer keeps writing very clever Python (metaclasses, dynamic attribute magic) that others struggle to maintain. How do you handle it?",
short="""Address it through shared standards and specific examples, not personal criticism. In review, ask what problem the cleverness solves and show a simpler alternative (a dataclass, a plain function, `__init_subclass__`, explicit registration); agree on a team principle like "optimize for the reader, magic needs a design note"; and channel their talent into the places where abstractions pay off, such as core framework APIs with tests and documentation.""",
deep="""Approach:

- **Private conversation first**: acknowledge their skill; explain the team cost (onboarding, debugging, bus factor) with concrete incidents (a bug that took two days because attribute access was dynamic).
- **Criteria, not taste**: agree with the team on when advanced features are justified: they must remove significant duplication, have tests, type hints that still work (metaclass magic often defeats type checkers and IDEs), and a short design note.
- **Offer simpler equivalents**: `__init_subclass__` instead of a metaclass for registration; `dataclasses`/`attrs` instead of generated `__init__`; explicit dispatch tables instead of `getattr(self, f"handle_{x}")`; descriptors only for repeated field validation.
- **Growth path**: ask them to lead the core framework's extension API, where careful abstraction design is the job, pairing with others and writing docs, which makes their work maintainable by design.
- **Review culture**: "Could a new team member debug this at 2 a.m.?" becomes a standard review question for everyone, not a rule aimed at one person.""",
code=r'''
# Clever: metaclass + dynamic attributes (hard to read, invisible to type checkers and IDEs)
class AutoRegister(type):
    registry = {}
    def __new__(m, name, bases, ns):
        cls = super().__new__(m, name, bases, ns)
        m.registry[name.lower().removesuffix("test")] = cls
        return cls
class Base(metaclass=AutoRegister):
    def __getattr__(self, item):                     # silently invents attributes
        return lambda *a: f"{item}{a}"
class TrimTest(Base): pass
print("clever:", AutoRegister.registry, TrimTest().anything(1))   # typos never fail!

# Simple: explicit, typed, same capability
REGISTRY: dict[str, type] = {}
class Test:
    def __init_subclass__(cls, *, name: str, **kw):
        super().__init_subclass__(**kw); REGISTRY[name] = cls
class Trim(Test, name="trim"):
    def run(self, lba: int) -> str: return f"trim at {lba}"
print("simple:", REGISTRY, Trim().run(8))
try:
    Trim().rn(8)
except AttributeError as e:
    print("typo caught:", e)
''',
follow=(
"What if the clever code is genuinely the best technical solution? => Then keep it, but make it maintainable: isolate it in one well-named module, add thorough tests, type stubs or `Protocol`s for users, and a design note explaining how it works.",
"How do you measure whether this improved? => Review turnaround and back-and-forth on that area, bugs traced to it, and how quickly other engineers can make changes there.",
),
pitfall="Publicly criticizing the engineer's style, or banning features outright; both push away strong engineers and don't create shared judgment.",
signals="You keep it constructive and specific, use team-agreed criteria rather than taste, offer simpler equivalents, and redirect the engineer's strengths to where they add value.",
),

P("Design", "When would you choose a language other than Python for part of the test infrastructure, and how do you integrate it?",
short="""Keep Python for orchestration, test logic and analysis (fast to write, huge ecosystem, readable by validation engineers). Move a component to Go, Rust or C/C++ when measurements show Python can't meet a hard requirement: microsecond-level I/O timing, very high command rates, memory-safe native device access, or a small static binary for constrained targets. Integrate through narrow boundaries: an extension module (PyO3/pybind11), a CLI with JSON output, or a service with a typed API.""",
deep="""Decision criteria:

- **Requirement, not preference**: latency jitter (Python's GC and interpreter overhead matter at microsecond scales), throughput (millions of small operations per second), memory footprint, deployment constraints (no interpreter on the target), or an existing library only available natively.
- **Team skills and ownership**: who maintains the Rust component in two years? Is there a second person who knows it?
- **Integration cost**: extension modules give the lowest overhead but need wheels per platform and careful API design (batch calls, release the GIL); a CLI or service boundary is simpler to deploy and debug but costs serialization and process overhead.
- **Examples**: a high-rate I/O workload generator in Rust or C (like `fio`), driven by Python which configures runs and analyses results; a Go daemon for device pool leasing across labs, called over HTTP from Python.

Reversibility: keep the boundary small and well-tested (contract tests from the Python side) so the native part can be replaced or retired.""",
follow=(
"Why is `fio` driven from Python a good pattern? => The tight I/O loop runs natively with precise timing, while Python handles configuration, orchestration, result parsing (`--output-format=json`) and analysis: each language does what it's good at.",
"How do you keep the native component from becoming a single point of knowledge? => Pairing, documentation, a narrow API with contract tests from Python, and hiring or training at least two maintainers before it becomes critical.",
),
pitfall="Rewriting in Rust/Go because it's \"faster\" without measuring, or keeping a pure-Python hot loop that can never meet a hard timing requirement.",
signals="You tie language choice to measured requirements and team capacity, pick an integration boundary with its trade-offs, and keep the decision reversible.",
),

]
