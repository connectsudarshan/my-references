MODULE = dict(id=5, title="Designing Large Python Codebases",
              desc="Structure, boundaries and contracts for code many teams share: layering and enforced dependencies, typing strategy, library API design and deprecation, version migrations, configuration, plugins and code review.")

QUESTIONS = [

P("Design", "You own a 200,000-line Python test-automation codebase used by 10 teams. How do you structure it so it stays maintainable?",
short="""Split it into layers with one-way dependencies: a small **core** (runner integration, logging, config, results), a **hardware abstraction layer** (device drivers behind interfaces), reusable **test libraries** (workloads, verifiers), and **tests** that use only the libraries. Package layers separately or as a monorepo with enforced import rules, give each area an owner (CODEOWNERS), and gate changes with typing, linting and fast unit tests of the framework itself.""",
deep="""Principles:

- **Dependency direction**: tests -> test libraries -> HAL interfaces <- drivers; core is used by all and depends on nothing above it. Tests never import a vendor SDK directly, so swapping hardware or simulating it doesn't touch thousands of tests.
- **Enforce, don't document**: `import-linter` contracts (layers, forbidden imports) or a small AST checker in CI. Architecture that isn't enforced erodes within months.
- **Packaging**: separate installable packages (`acme-core`, `acme-hal`, `acme-nvme`) with semantic versions if teams release independently; a monorepo with a single lock file if they deploy together. Either way, one build and CI definition.
- **Ownership**: CODEOWNERS per package, a small platform team owning core APIs, an RFC/ADR process for breaking changes.
- **Quality gates**: Ruff + formatter, mypy/pyright strict on core and HAL, unit tests with simulated devices (seconds, on every PR), HIL tests nightly.
- **Discoverability**: typed public APIs with docstrings, generated docs, examples, and a "golden path" template for writing new tests.

Migration strategy for an existing tangle: measure the current import graph, define target layers, add the linter in "report only" mode, then ratchet (no new violations; fix existing ones team by team).""",
code=r'''
import ast, pathlib, tempfile, textwrap

RULES = {"tests": {"forbidden": ("vendor_sdk", "acme.drivers")}}       # tests must use acme.hal only

def violations(root):
    found = []
    for path in root.rglob("*.py"):
        layer = path.relative_to(root).parts[0]
        forbidden = RULES.get(layer, {}).get("forbidden", ())
        for node in ast.walk(ast.parse(path.read_text())):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else \
                    [node.module] if isinstance(node, ast.ImportFrom) and node.module else []
            for n in names:
                if n.startswith(forbidden):
                    found.append(f"{path.relative_to(root).as_posix()}:{node.lineno} imports {n}")
    return found

root = pathlib.Path(tempfile.mkdtemp())
(root / "tests").mkdir()
(root / "tests" / "test_trim.py").write_text(textwrap.dedent("""
    from acme.hal import Device            # allowed: interface layer
    import vendor_sdk                      # forbidden: bypasses the HAL
    from acme.drivers.nvme import raw_cmd  # forbidden
"""))
for v in violations(root): print("VIOLATION", v)
''',
follow=(
"Monorepo or many repositories? => Monorepo when teams change shared code together often and want atomic changes and one CI; multi-repo when components have independent release cycles and owners. For a test framework shared by 10 teams, a monorepo with per-package ownership usually wins.",
"How do you introduce layering into a codebase that already violates it everywhere? => Snapshot current violations as an allowlist, fail CI only on new ones, and burn down the allowlist with owners and deadlines.",
),
pitfall="A shared `utils.py` that everything imports and that imports everything: it creates cycles and makes every change risky. Split by domain and keep the core small.",
signals="You define layers with dependency direction, enforce them automatically, cover packaging, ownership and quality gates, and give a migration path for an existing codebase.",
),

P("Design", "What is your typing strategy for a large Python codebase?",
short="""Gradual and ratcheted: type public APIs and new code first, run mypy or pyright in CI with strict settings on core packages and looser settings elsewhere, and never let coverage go backwards. Use `Protocol`s at boundaries for flexibility, precise types (`TypedDict`, `Literal`, `NewType`) for data, and runtime validation (Pydantic/attrs validators) only where untrusted data enters the system.""",
deep="""Why it pays off at scale: types document contracts between teams, let IDEs navigate 200k lines, and catch whole classes of bugs (None handling, wrong argument order, renamed fields) before hardware time is wasted.

Practices:

- **Per-module strictness**: `[[tool.mypy.overrides]]` with `strict = true` for core/HAL; `check_untyped_defs` elsewhere to start.
- **Ratchet**: track the number of errors or untyped functions; CI fails if it increases.
- **Boundaries**: accept `Protocol`s (structural typing) so tests can pass fakes without inheritance; return concrete types.
- **Data**: `TypedDict` for JSON payloads, frozen dataclasses for internal value objects, `Literal`/`Enum` for states, `NewType` for IDs that must not be mixed (`SerialNumber` vs `Lba`).
- **Avoid `Any` leaks**: `disallow_any_generics`, wrap untyped third-party libraries in typed adapters, add stubs.
- **Runtime validation at the edges only**: config files, API responses, CLI input. Inside the system trust the types.""",
code=r'''
from typing import Protocol, NewType, Literal, TypedDict

SerialNumber = NewType("SerialNumber", str)
Lba = NewType("Lba", int)
Verdict = Literal["PASS", "FAIL", "BLOCKED"]

class BlockDevice(Protocol):                       # any driver or fake with these methods fits
    serial: SerialNumber
    def write(self, lba: Lba, data: bytes) -> None: ...
    def read(self, lba: Lba, length: int) -> bytes: ...

class ResultRecord(TypedDict):
    serial: SerialNumber
    test: str
    verdict: Verdict

class FakeDrive:                                   # no inheritance needed
    def __init__(self, sn: str): self.serial, self._blocks = SerialNumber(sn), {}
    def write(self, lba: Lba, data: bytes) -> None: self._blocks[lba] = data
    def read(self, lba: Lba, length: int) -> bytes: return self._blocks.get(lba, b"\0" * length)[:length]

def write_read_verify(dev: BlockDevice, lba: Lba) -> ResultRecord:
    pattern = lba.to_bytes(8, "little") * 64
    dev.write(lba, pattern)
    ok = dev.read(lba, len(pattern)) == pattern
    return {"serial": dev.serial, "test": "wrv", "verdict": "PASS" if ok else "FAIL"}

print(write_read_verify(FakeDrive("S3EVNX0K"), Lba(2048)))
''',
follow=(
"A team says typing slows them down. How do you respond? => Agree to start with public APIs and core packages, show bugs types caught (e.g. a `None` crash that cost a night of hardware time), keep strictness lower in exploratory test code, and invest in good stubs so the friction is low.",
"mypy or pyright? => Either works; pyright is faster and powers VS Code's Pylance, mypy has more plugins (e.g. for Django/SQLAlchemy). Pick one for CI to avoid conflicting results, and let developers use whatever IDE integration they like.",
),
pitfall="Annotating everything as `Any` or `dict` to silence errors. It gives false confidence while providing none of the benefit.",
signals="You describe gradual adoption with a ratchet, Protocols at boundaries, precise data types, runtime validation only at edges, and handle the human side of adoption.",
),

P("Concept", "How do you design and evolve the public API of an internal Python library that 10 teams depend on?",
short="""Keep the public surface small and explicit (`__all__`, underscore-prefixed internals), make optional parameters **keyword-only**, return stable types, version with semantic versioning, and change things through a **deprecation cycle**: warn with `DeprecationWarning` (correct `stacklevel`), document the replacement, keep both for at least one release, and remove it in a major version. Contract tests protect consumers.""",
deep="""Design rules that reduce future breaking changes:

- `def run_workload(device, *, pattern="random", qd=32, duration_s=60)`: keyword-only options can be added or reordered without breaking callers.
- Accept broad input types (Protocols, `Iterable`), return specific ones.
- Don't expose internal data structures (return copies or frozen objects).
- Avoid module-level mutable state and import-time side effects.
- Raise documented exception types from a library-specific hierarchy.

Evolution:

- **Deprecation**: `warnings.warn(msg, DeprecationWarning, stacklevel=2)` so the warning points to the caller's line; `@warnings.deprecated` (3.13+, PEP 702) also informs type checkers.
- Make CI of consumer teams run with `-W error::DeprecationWarning` for your package so they notice early.
- Maintain a changelog and a migration guide; offer a codemod (LibCST) for mechanical renames across repositories.""",
code=r'''
import warnings, functools

def renamed_kwarg(old, new, remove_in):
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if old in kwargs:
                warnings.warn(f"{fn.__name__}({old}=...) is deprecated; use {new}=... "
                              f"(removal in {remove_in})", DeprecationWarning, stacklevel=2)
                kwargs[new] = kwargs.pop(old)
            return fn(*args, **kwargs)
        return wrapper
    return deco

@renamed_kwarg("queue_depth", "qd", remove_in="v5.0")
def run_workload(device, *, pattern="random", qd=32, duration_s=60):
    return f"{device}: {pattern} QD{qd} for {duration_s}s"

warnings.simplefilter("always")
with warnings.catch_warnings(record=True) as w:
    print(run_workload("nvme0", queue_depth=64))           # old caller still works
    print("warning:", w[0].message, "| points at line", w[0].lineno)
try:
    run_workload("nvme0", "sequential")                    # positional option: rejected
except TypeError as e:
    print("TypeError:", e)
''',
follow=(
"Why does `stacklevel=2` matter? => With the default of 1 the warning points at the library line that called `warn`, which is useless to the consumer; 2 points at the caller's code that needs changing.",
"How do you find all callers across 30 repositories before removing an API? => Code search (Sourcegraph/GitHub search), usage telemetry from the deprecation warning path, and failing consumer CI when warnings are escalated to errors.",
),
pitfall="Removing or renaming a function in a minor release because \"nobody uses it\", breaking another team's nightly run on hardware.",
signals="You design for evolution (keyword-only, small surface), know the deprecation mechanics including stacklevel, and give a process for finding and migrating consumers.",
),

P("Scenario", "Plan the migration of 50 internal repositories from Python 3.8 to 3.13.",
short="""Inventory first (repos, owners, dependencies, C extensions, removed stdlib modules like `distutils`, `imp`, `asynchat`), then add the new version to every CI matrix in report-only mode, fix dependencies and code with automated tools (`pyupgrade`/Ruff rules, codemods), migrate the shared libraries first, then consumers in waves with canaries, and finally drop 3.8. Track progress on a dashboard and time-box it.""",
deep="""Phases:

1. **Discovery**: script over all repos to collect Python versions, lock files, dependencies without wheels for 3.13, uses of removed modules (`distutils`, `imp`, `asyncore`, `asynchat`, `smtpd` removed in 3.12; `cgi`, `crypt`, `telnetlib`, `pipes` and other "dead batteries" removed in 3.13), and deprecated behaviours.
2. **Foundation**: upgrade base images and CI runners; publish internal packages as multi-version wheels; update shared framework code first because everyone depends on it.
3. **CI matrix**: add 3.13 as a non-blocking job everywhere; fix failures; make it blocking.
4. **Automated fixes**: Ruff `UP` rules (pyupgrade), `setuptools`/`packaging` in place of `distutils`, codemods for API changes; run with `-W error::DeprecationWarning` to surface upcoming breaks.
5. **Rollout**: migrate low-risk repos first, then critical ones with canary runs (e.g. one lab rack) and a rollback plan (keep 3.8 images for a limited time).
6. **Close out**: remove 3.8 from CI and base images; document the next upgrade cadence (e.g. yearly, N-1 policy) so it never becomes a big bang again.""",
code=r'''
import ast, sys, pathlib, tempfile, importlib.util

REMOVED = {"distutils": "3.12", "imp": "3.12", "asynchat": "3.12", "asyncore": "3.12", "smtpd": "3.12",
           "cgi": "3.13", "crypt": "3.13", "telnetlib": "3.13", "pipes": "3.13", "nntplib": "3.13"}

def scan(repo):
    hits = []
    for f in repo.rglob("*.py"):
        for node in ast.walk(ast.parse(f.read_text(), filename=str(f))):
            mods = [a.name for a in node.names] if isinstance(node, ast.Import) else \
                   [node.module] if isinstance(node, ast.ImportFrom) and node.module else []
            for m in mods:
                top = m.split(".")[0]
                if top in REMOVED:
                    hits.append(f"{f.name}:{node.lineno} uses {top} (removed in {REMOVED[top]})")
    return hits

repo = pathlib.Path(tempfile.mkdtemp())
(repo / "setup_tools.py").write_text("from distutils.version import LooseVersion\nimport pipes, json\n")
(repo / "lab.py").write_text("import telnetlib\nimport asyncio\n")
for h in sorted(scan(repo)): print(h)
print("running on", sys.version.split()[0], "| telnetlib importable:", importlib.util.find_spec("telnetlib") is not None)
''',
follow=(
"A critical dependency has no 3.13 wheel. What are your options? => Upgrade to a newer version, find a maintained fork or alternative, build and host the wheel internally, contribute the fix upstream, or isolate that component on the old interpreter behind a process/API boundary temporarily.",
"How do you avoid the next migration being this painful? => An explicit support policy (e.g. support the latest two Python versions), CI testing against the next release candidate each autumn, and Renovate/Dependabot keeping dependencies current.",
),
pitfall="Upgrading everything at once in one weekend, or migrating consumers before the shared framework supports the new version.",
signals="You start with automated discovery, sequence shared code first, use CI matrices and waves with canaries and rollback, and set a policy to prevent future big-bang upgrades.",
),

P("Code review", "Review this code from a pull request. What do you flag, in what order, and how do you phrase it?",
short="""Priority order: correctness and safety first (SQL injection, resource leak, swallowed exceptions, mutable default argument), then reliability (no timeout, no retry policy), then design (hidden global state, mixing I/O and logic), then style. Phrase comments as specific, explained suggestions with the fix, and separate blocking issues from optional nits.""",
deep="""The snippet under review (shown commented out in the example):

- `def save_results(results, cache={}):` mutable default: `cache` is shared across all calls.
- `conn = sqlite3.connect(DB)` without closing, and without a transaction boundary.
- `f"INSERT ... VALUES ('{r['name']}', ...)"`: SQL injection and quoting bugs (a test name with an apostrophe breaks it).
- `except Exception: pass`: failures disappear; the nightly report silently misses results.
- Per-row inserts instead of `executemany` in one transaction: slow.

How a Principal reviews:

- Lead with a short summary ("Two blocking issues: SQL injection and swallowed errors; the rest are suggestions").
- Explain why each matters with a concrete failure scenario, and propose the fix.
- Label comments: **blocking**, **suggestion**, **nit**. Automate nits with a formatter and linter instead of commenting on them.
- If the same issue recurs across the team, fix the system: a Ruff rule (`B006` for mutable defaults, `S608` for SQL string building, `S110`/`BLE001` for broad or silent excepts), a helper API, or a guideline.""",
code=r'''
import sqlite3, tempfile, os, logging

DB = os.path.join(tempfile.mkdtemp(), "results.db")
log = logging.getLogger("results")

# --- BEFORE (as submitted) -------------------------------------------------
# def save_results(results, cache={}):
#     conn = sqlite3.connect(DB)
#     for r in results:
#         try:
#             conn.execute(f"INSERT INTO runs VALUES ('{r['name']}', '{r['verdict']}')")
#         except Exception:
#             pass
#     conn.commit()

# --- AFTER -----------------------------------------------------------------
def save_results(results: list[dict], db_path: str = DB) -> int:
    rows = [(r["name"], r["verdict"]) for r in results]
    conn = sqlite3.connect(db_path)
    try:
        with conn:                                          # transaction: commit or rollback
            conn.execute("CREATE TABLE IF NOT EXISTS runs (name TEXT, verdict TEXT)")
            conn.executemany("INSERT INTO runs VALUES (?, ?)", rows)   # parameterized + batched
    finally:
        conn.close()                                        # sqlite3's `with` does NOT close
    log.info("saved %d results", len(rows))
    return len(rows)

n = save_results([{"name": "trim_o'neil_case", "verdict": "PASS"}, {"name": "fw_update", "verdict": "FAIL"}])
conn = sqlite3.connect(DB)
print(n, "rows saved:", conn.execute("SELECT * FROM runs").fetchall()); conn.close()
''',
follow=(
"The author pushes back that `except Exception: pass` is needed because some results are malformed. What do you suggest? => Validate explicitly, count and log malformed records with enough context, store them in a rejects table, and fail the run if the reject rate exceeds a threshold.",
"How do you keep reviews from becoming a bottleneck with 10 teams? => Automate style and common bugs in CI, keep PRs small, have clear ownership (CODEOWNERS), and use a shared checklist so reviewers focus on design and correctness.",
),
pitfall="Leaving 25 comments of equal weight, mostly formatting, and missing the SQL injection. Or approving because \"it works on my machine\".",
signals="You prioritize by impact, explain failure scenarios, propose concrete fixes (including the subtle `sqlite3` context manager not closing the connection), label severity, and turn recurring findings into automation.",
),

P("Design", "How do you design configuration for a framework that runs in labs, CI and on developer laptops?",
short="""Layered, typed and validated: defaults in code, overridden by a config file per environment, then environment variables, then CLI flags. Load once at startup into an immutable, validated object (dataclass or Pydantic), fail fast with clear errors, keep secrets out of files (vault/env injection), and log the effective configuration (with secrets redacted) for reproducibility.""",
deep="""Requirements to clarify: How many environments? Who edits config (engineers, lab admins)? Must a test run be reproducible months later?

Design:

- **Precedence**: defaults < file (`lab.toml`, `ci.toml`) < environment variables (`ACME_...`) < CLI arguments. `collections.ChainMap` expresses this naturally.
- **Schema and validation**: one typed schema (frozen dataclasses with `__post_init__` checks, or Pydantic settings). Validate types, ranges and cross-field rules at startup, reporting all errors at once.
- **Immutability**: pass the config object down (dependency injection); no global mutable settings module that tests patch.
- **Secrets**: from environment/secret manager, never committed; redact when logging.
- **Reproducibility**: write the resolved config and its source for each key into the run's result bundle.
- **Formats**: TOML (`tomllib` in stdlib) for humans; avoid executing Python files as config.""",
code=r'''
import os, tomllib
from collections import ChainMap
from dataclasses import dataclass, fields

@dataclass(frozen=True)
class RunConfig:
    lab: str
    queue_depth: int
    duration_s: int
    api_token: str = ""
    def __post_init__(self):
        errors = []
        if not 1 <= self.queue_depth <= 1024: errors.append("queue_depth must be 1..1024")
        if self.duration_s <= 0: errors.append("duration_s must be > 0")
        if errors: raise ValueError("; ".join(errors))
    def redacted(self):
        return {f.name: ("***" if "token" in f.name and getattr(self, f.name) else getattr(self, f.name)) for f in fields(self)}

DEFAULTS = {"lab": "local", "queue_depth": 32, "duration_s": 60}
file_cfg = tomllib.loads('lab = "bangalore-rack-7"\nduration_s = 3600\n')
os.environ["ACME_QUEUE_DEPTH"] = "128"; os.environ["ACME_API_TOKEN"] = "s3cr3t"
env_cfg = {k[5:].lower(): v for k, v in os.environ.items() if k.startswith("ACME_")}
cli_cfg = {"duration_s": 600}

merged = ChainMap(cli_cfg, env_cfg, file_cfg, DEFAULTS)
types = {f.name: f.type for f in fields(RunConfig)}
cfg = RunConfig(**{k: (int(v) if types[k] is int else v) for k, v in merged.items() if k in types})
print("effective:", cfg.redacted())
print("source of duration_s:", next(n for n, m in zip(["cli", "env", "file", "defaults"], merged.maps) if "duration_s" in m))
try:
    RunConfig(lab="x", queue_depth=0, duration_s=-1)
except ValueError as e:
    print("ValueError:", e)
''',
follow=(
"Why not just use a global `settings.py` module? => Global mutable config makes tests order-dependent (they patch it), hides dependencies, and can't represent two configurations at once (e.g. two labs in one process).",
"How do you handle config for 200 devices with per-device overrides? => A device inventory (file or database) with defaults per model and per-device overrides, validated with the same schema, referenced by ID from run configs.",
),
pitfall="Reading `os.environ` deep inside library functions. Configuration then becomes invisible, untestable and different on every machine.",
signals="You define precedence, validation, immutability, secret handling and reproducibility, and relate it to testability.",
),

P("Design", "How would you build an extensible plugin system so teams can add device types and reports without editing core code?",
short="""Define a small interface (an ABC or `Protocol`) per extension point, and discover implementations through a registry: `__init_subclass__` or a decorator for in-repo plugins, and packaging **entry points** (`importlib.metadata.entry_points(group=...)`) for separately installed packages. Validate plugins at load time, version the plugin API, and isolate plugin failures so one bad plugin can't break the run.""",
deep="""Design points:

- **Extension points**: e.g. `acme.devices` (device drivers), `acme.reporters` (report writers), `acme.checks` (post-test validators). Each has a documented interface and API version.
- **Discovery**: entry points declared in each plugin's `pyproject.toml`: `[project.entry-points."acme.reporters"] junit = "acme_junit:JUnitReporter"`. The core loads them lazily by name. This is how pytest (`pytest11`) and many CLIs work.
- **Validation**: check the class implements the interface and supports the core's plugin API version; fail with a clear message naming the plugin package.
- **Isolation**: wrap plugin calls with error handling and timeouts; mark the plugin failed and continue; optionally run untrusted plugins in a subprocess.
- **Configuration**: enable/disable plugins per environment; don't load everything installed blindly.
- **Testing**: a plugin test kit (fixtures and a contract test suite) that plugin authors run in their CI.""",
code=r'''
from importlib.metadata import entry_points

PLUGIN_API = 2
REGISTRY: dict[str, type] = {}

def reporter(name):
    def deco(cls):
        if getattr(cls, "api_version", None) != PLUGIN_API:
            raise TypeError(f"reporter {name!r} targets API {getattr(cls, 'api_version', '?')}, core is {PLUGIN_API}")
        REGISTRY[name] = cls; return cls
    return deco

@reporter("summary")
class SummaryReporter:
    api_version = 2
    def write(self, results): return f"{sum(r['ok'] for r in results)}/{len(results)} passed"

@reporter("flaky")
class BrokenReporter:
    api_version = 2
    def write(self, results): raise RuntimeError("bug in plugin")

try:
    @reporter("legacy")
    class OldReporter:
        api_version = 1
except TypeError as e:
    print("rejected at load:", e)

for ep in entry_points(group="acme.reporters"):       # separately installed packages
    REGISTRY.setdefault(ep.name, ep.load())

results = [{"ok": True}, {"ok": False}, {"ok": True}]
for name, cls in REGISTRY.items():
    try:
        print(f"{name}: {cls().write(results)}")
    except Exception as e:                              # isolate plugin failures
        print(f"{name}: FAILED ({e}) - run continues")
''',
follow=(
"How do you evolve the plugin interface without breaking every plugin at once? => Version the API, support N and N-1 simultaneously via adapters, emit deprecation warnings for old plugins, and publish the contract test suite for the new version early.",
"Security concern with entry points? => Loading a plugin executes its code with full privileges; only install plugins from your internal index, pin them, and review them like any dependency.",
),
pitfall="Discovering plugins by importing every module in a directory at startup: slow, fragile, and one import error breaks the whole framework.",
signals="You define extension points with versioned interfaces, use entry points for discovery, validate and isolate plugins, and provide a way for plugin authors to test against the contract.",
),

]
