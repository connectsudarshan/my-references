MODULE = dict(id=9, title="Security, Packaging & Delivery",
              desc="Unsafe deserialization, injection and path traversal, secrets in logs, supply-chain security, distributing tools to lab machines, and CI/CD quality gates for Python.")

QUESTIONS = [

P("Trap", "Is it safe to load test results or configs that other machines saved with `pickle`?",
short="""Only if you fully trust whoever could have written the file. Unpickling can execute arbitrary code: an object's `__reduce__` tells pickle to call any function (like `os.system`) with any arguments during load. For data exchanged between machines, teams or over networks, use data-only formats (JSON, TOML, Protocol Buffers, Parquet/Arrow) and validate them; if you must use pickle between your own processes, sign the payload with HMAC and verify before loading.""",
deep="""Same class of risk: `yaml.load` without `SafeLoader`, `eval`/`exec` on config text, `torch.load` of untrusted checkpoints (older versions without `weights_only=True`), `marshal`, `shelve` (pickle-based), and `numpy.load(allow_pickle=True)`.

Guidance:

- Data interchange: JSON (with schema validation), TOML for config, Protobuf/Avro for typed messages, Parquet/Arrow for bulk data.
- Internal caches between trusted processes: pickle is acceptable, but add HMAC-SHA256 signing with a secret key and compare with `hmac.compare_digest` before unpickling, so a tampered file is rejected.
- Treat shared lab file systems as untrusted: many people and scripts can write there.
- Static analysis flags these (Bandit `B301`, Ruff `S301`).""",
code=r'''
import pickle, hmac, hashlib, json

class Malicious:
    def __reduce__(self):                              # called during pickling; replayed on load
        return (print, ("!!! arbitrary code ran during pickle.loads() -- this could be os.system(...)",))

payload = pickle.dumps(Malicious())
pickle.loads(payload)                                  # just loading the "result file" executes code

KEY = b"lab-shared-secret"
def dump_signed(obj):
    data = pickle.dumps(obj)
    return hmac.new(KEY, data, hashlib.sha256).digest() + data
def load_signed(blob):
    sig, data = blob[:32], blob[32:]
    if not hmac.compare_digest(sig, hmac.new(KEY, data, hashlib.sha256).digest()):
        raise ValueError("signature mismatch: refusing to unpickle")
    return pickle.loads(data)

good = dump_signed({"device": "SN001", "verdict": "PASS"})
print("signed load:", load_signed(good))
try:
    load_signed(good[:32] + payload)                   # attacker swaps the body
except ValueError as e:
    print("tampered:", e)
print("preferred for interchange:", json.dumps({"device": "SN001", "verdict": "PASS"}))
''',
follow=(
"How is `yaml.load` dangerous and what's the fix? => The full loader can construct arbitrary Python objects; use `yaml.safe_load` (or `yaml.load(..., Loader=yaml.SafeLoader)`), which only builds plain data types.",
"Why `hmac.compare_digest` instead of `==`? => It compares in constant time, avoiding timing side channels that could leak how many leading bytes of a signature matched.",
),
pitfall="Pickling test artifacts to a shared NFS directory and loading them in a CI job with elevated credentials: anyone who can write that directory can run code in CI.",
signals="You explain the `__reduce__` mechanism, list similar risky loaders, choose data-only formats for interchange, and know HMAC signing plus constant-time comparison for trusted-but-verified cases.",
),

P("Concept", "How do you prevent command injection and path traversal in lab tooling that takes user or config input?",
short="""Never build shell commands from strings: call `subprocess.run([...])` with an argument list and no `shell=True`; validate inputs against allow-lists (device names matching `^nvme\\d+n?\\d*$`, known test names). For file paths from users or configs, resolve them (`Path.resolve()`) and verify they stay inside the allowed base directory (`is_relative_to`), rejecting absolute paths and `..` escapes. Run tools with least privilege.""",
deep="""Injection examples in test infrastructure: a device name from a web form like `nvme0; rm -rf /`, a report name used in a shell `tar` command, a log path `../../etc/passwd` requested from an artifact server.

Defences:

- **Argument lists**: the OS receives each argument as-is; shell metacharacters have no meaning. If you truly need a shell pipeline, use `shlex.quote` for every piece, but prefer chaining `subprocess` calls in Python.
- **Allow-list validation**: regex or set membership for identifiers; reject rather than sanitize.
- **Path containment**: `(base / user_path).resolve()` then `resolved.is_relative_to(base.resolve())`. Resolve follows symlinks, so a symlink pointing outside is caught too.
- **Archives**: extracting tarballs from devices or vendors: use `tarfile` extraction filters (`filter="data"`, default since 3.14) to block absolute paths, `..` and dangerous links; for zip, check each member path.
- **Least privilege**: most tools don't need root; wrap the few privileged operations in a small audited helper.""",
code=r'''
import pathlib, re, subprocess, sys, tempfile

DEVICE_RE = re.compile(r"^nvme\d+(n\d+)?$")
def smart_log(device: str):
    if not DEVICE_RE.fullmatch(device):
        raise ValueError(f"invalid device name {device!r}")
    # list form: even if validation were missing, ';' would be a literal character, not a command separator
    return subprocess.run([sys.executable, "-c", "import sys; print('would run: nvme smart-log', sys.argv[1])", f"/dev/{device}"],
                          capture_output=True, text=True, check=True).stdout.strip()

for dev in ("nvme0", "nvme0; rm -rf /"):
    try: print(smart_log(dev))
    except ValueError as e: print("rejected:", e)

ARTIFACTS = pathlib.Path(tempfile.mkdtemp()) / "artifacts"
(ARTIFACTS / "run42").mkdir(parents=True); (ARTIFACTS / "run42" / "smart.json").write_text("{}")
def safe_artifact(rel: str) -> pathlib.Path:
    p = (ARTIFACTS / rel).resolve()
    if not p.is_relative_to(ARTIFACTS.resolve()):
        raise PermissionError(f"path escapes artifact root: {rel!r}")
    return p
for rel in ("run42/smart.json", "../../../etc/passwd", "/etc/passwd"):
    try: print("serve", safe_artifact(rel).name)
    except PermissionError as e: print("blocked:", e)
''',
follow=(
"Is `shlex.quote` enough to make `shell=True` safe? => It correctly quotes for POSIX shells if applied to every interpolated value, but it's easy to miss one, and it doesn't apply to Windows `cmd.exe`; argument lists remove the whole class of bug.",
"Why check containment after `resolve()` rather than looking for `..` in the string? => Encodings, absolute paths, symlinks and platform-specific separators bypass string checks; resolving gives the real target to compare.",
),
pitfall="Validating with a deny-list (\"reject if it contains ';'\"). Attackers use `&&`, `|`, backticks, `$()` or newlines; allow-lists and argument lists are robust.",
signals="You use argument lists, allow-list validation, resolve-and-contain for paths including symlinks and archives, and least privilege.",
),

P("Concept", "How do you keep secrets (API tokens, BMC passwords) out of code, logs and test reports?",
short="""Load secrets at runtime from a secret manager or environment injected by CI/orchestration, never from the repository; keep them in objects that don't print their value (a `Secret` wrapper whose `repr` is `***`); add a logging filter that redacts known secret patterns and values; scrub artifacts before upload; scan repositories and CI logs for leaked secrets; and rotate anything that leaks.""",
deep="""Where secrets leak in practice:

- Tracebacks and debug logs printing function arguments or HTTP headers.
- Test reports that dump the full config or environment.
- Command lines: `tool --password xyz` is visible in `ps` output and in process logs; prefer environment variables, files with restricted permissions, or stdin.
- Committed `.env` files and notebooks.

Controls:

- **Source**: HashiCorp Vault, cloud secret managers, or CI secret variables; short-lived credentials where possible.
- **Type**: a `Secret` class (or Pydantic `SecretStr`) with `__repr__`/`__str__` masking and an explicit `.reveal()`.
- **Logging**: a filter replacing registered secret values and patterns (`Bearer [A-Za-z0-9._-]+`, `password=...`) in messages and arguments.
- **Detection**: gitleaks/trufflehog in pre-commit and CI; GitHub secret scanning.
- **Response**: revoke and rotate immediately; deleting the commit doesn't help once pushed.""",
code=r'''
import logging, re, sys

class Secret:
    def __init__(self, value): self._v = value
    def reveal(self): return self._v
    def __repr__(self): return "Secret('***')"
    __str__ = __repr__

class RedactFilter(logging.Filter):
    PATTERNS = [re.compile(r"(Bearer\s+)[A-Za-z0-9._\-]+"), re.compile(r"(password=)\S+", re.I)]
    def __init__(self, secrets): super().__init__(); self.secrets = [s.reveal() for s in secrets]
    def filter(self, record):
        msg = record.getMessage()
        for s in self.secrets: msg = msg.replace(s, "***")
        for p in self.PATTERNS: msg = p.sub(r"\1***", msg)
        record.msg, record.args = msg, ()
        return True

bmc_pw = Secret("Sup3r-S3cret!")
h = logging.StreamHandler(sys.stdout); h.addFilter(RedactFilter([bmc_pw]))
h.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
log = logging.getLogger("lab"); log.addHandler(h); log.setLevel(logging.INFO)

config = {"bmc_host": "10.0.4.17", "bmc_password": bmc_pw}
log.info("connecting with config %s", config)                          # repr hides it
log.info("raw request headers: Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.abc.def")
log.info("legacy tool args: ipmitool -H 10.0.4.17 password=%s", bmc_pw.reveal())   # accidental reveal still redacted
''',
follow=(
"A token was committed to a public repo and removed in the next commit. Are you safe? => No. It's in history and may already be harvested within minutes; revoke and rotate it immediately, then clean history if needed.",
"How do you pass a password to a CLI tool without exposing it in the process list? => Environment variable, a file readable only by the user, or stdin, depending on what the tool supports; never a command-line argument.",
),
pitfall="Logging the full configuration or `os.environ` at startup \"for debugging\", which ships every credential into log aggregation where many people can read it.",
signals="You cover sources, masking types, log redaction, process-list exposure, detection tooling and the rotate-on-leak response.",
),

P("Design", "How do you secure the Python dependency supply chain for internal tools?",
short="""Pin everything with a lock file that includes **hashes** (`uv lock`, `pip-compile --generate-hashes`, Poetry), install with hash checking, pull from an internal mirror/proxy index, protect against dependency confusion by reserving or namespacing internal package names, scan for known vulnerabilities (`pip-audit`, OSV), review new dependencies, generate an SBOM, and update regularly via automated PRs (Renovate/Dependabot) that run the full test suite.""",
deep="""Threats: typosquatting (`reqeusts`), dependency confusion (a public package with the same name as your internal one and a higher version), compromised maintainer accounts, malicious install-time code in `setup.py`, and known CVEs in transitive dependencies.

Controls:

- **Lock and hash**: every transitive dependency pinned to an exact version and artifact hash; `pip install --require-hashes`. Reproducible across lab machines.
- **Index configuration**: a single internal index (Artifactory, Nexus, devpi) that proxies PyPI; never combine `--extra-index-url` with public PyPI for internal names, which enables dependency confusion.
- **Prefer wheels**: `--only-binary :all:` where possible avoids executing sdist build scripts.
- **Vulnerability scanning** in CI with `pip-audit`; policy for severity and time to fix.
- **Review**: new dependencies need justification (maintenance, license, size); fewer dependencies are a security feature.
- **Provenance**: prefer packages with trusted publishing and attestations (PEP 740); publish internal packages the same way.
- **SBOM** (CycloneDX/SPDX) per release for audits.""",
code=r'''
import hashlib, pathlib, tempfile

# What a hashed lock entry protects: the exact artifact you tested is the one you install.
wheel = pathlib.Path(tempfile.mkdtemp()) / "acme_hal-2.4.1-py3-none-any.whl"
wheel.write_bytes(b"PK\x03\x04 ...pretend wheel contents...")
locked_hash = "sha256:" + hashlib.sha256(wheel.read_bytes()).hexdigest()
print("requirements.txt line:")
print(f"  acme-hal==2.4.1 --hash={locked_hash[:23]}...")

def verify(path, expected):
    actual = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    return "OK" if actual == expected else "HASH MISMATCH: install refused"
print("clean artifact   :", verify(wheel, locked_hash))
wheel.write_bytes(wheel.read_bytes() + b"# injected")          # tampered mirror or compromised upload
print("tampered artifact:", verify(wheel, locked_hash))
''',
follow=(
"What is dependency confusion and how do you prevent it? => An installer resolves your internal package name from the public index because a public package with that name (and higher version) exists. Prevent with a single proxy index that serves internal names only from the internal repo, and by registering placeholder names publicly.",
"A critical CVE lands in a transitive dependency on Friday evening. What's the process? => Check exposure (is the vulnerable code path used?), bump via the lock file, run CI, roll out through the normal pipeline quickly, and document; the ability to do this fast is why automated update PRs and good tests matter.",
),
pitfall="`pip install -r requirements.txt` with unpinned or range-pinned versions on every lab machine: each machine gets a different, untested set of packages.",
signals="You identify concrete threats, and answer with hashes, a single controlled index, scanning, review, provenance and SBOMs, plus an update process.",
),

P("Scenario", "How do you distribute a Python test tool to 300 lab machines with different OS images, reliably?",
short="""Build once, deploy the same artifact everywhere: package as a wheel with pinned dependencies and install into an isolated environment (`uv tool install`/`pipx`, or a venv provisioned by config management), or ship a self-contained artifact (a container image, a PEX/shiv/`zipapp` bundle plus a pinned interpreter) where machines differ. Version it, roll out in rings (canary machines first), make rollback one command, and have the tool report its version in every result.""",
deep="""Options and trade-offs:

- **Wheel + lock file into a venv** (via Ansible/Salt or `uv`): clean, small, fast updates; requires a compatible Python on every machine.
- **Container image**: the most reproducible (interpreter, libs, tools like nvme-cli pinned); needs device access configuration (`--device /dev/nvme0`, privileges) and a container runtime on lab hosts.
- **Self-contained zip app** (`zipapp`, shiv, PEX): one file that runs with any compatible interpreter; good for pure-Python tools; native dependencies complicate it.
- **Frozen executables** (PyInstaller): no Python needed on the target, but larger artifacts and more antivirus/debugging friction.

Rollout practice: semantic versions; a canary ring (5 machines) runs the new version on real workloads before the fleet; compare verdict distributions; keep the previous version installed for instant rollback; the tool logs its version, commit and dependency hash into every result so any result can be traced to exact code.""",
code=r'''
import pathlib, subprocess, sys, tempfile, zipapp

src = pathlib.Path(tempfile.mkdtemp()) / "labtool"
(src / "labtool").mkdir(parents=True)
(src / "labtool" / "__init__.py").write_text('__version__ = "3.2.0"\n')
(src / "labtool" / "cli.py").write_text(
    "import sys, platform\nfrom labtool import __version__\n"
    "def main():\n    print(f'labtool {__version__} on Python {platform.python_version()} args={sys.argv[1:]}')\n")
(src / "__main__.py").write_text("from labtool.cli import main\nmain()\n")

target = src.parent / "labtool-3.2.0.pyz"
zipapp.create_archive(src, target, interpreter="/usr/bin/env python3")   # one-file artifact
print("built:", target.name, f"({target.stat().st_size} bytes)")
out = subprocess.run([sys.executable, str(target), "--device", "nvme0"], capture_output=True, text=True).stdout
print("run  :", out.strip())
''',
follow=(
"When would you choose containers over venvs for lab tools? => When machines differ a lot, when the tool depends on native binaries (nvme-cli, vendor utilities) that must be version-pinned together, or when many tools with conflicting dependencies share a host.",
"How do you make sure old results can be reproduced with the exact tool version? => Keep every released artifact in the internal registry indefinitely, record version plus lock hash in results, and never overwrite a published version.",
),
pitfall="`git pull` on each lab machine followed by `pip install -r requirements.txt`: machines drift apart, network hiccups leave half-updated installs, and rollback is guesswork.",
signals="You compare distribution options with trade-offs, insist on build-once immutable artifacts, staged rollout with rollback, and traceability of results to tool versions.",
),

P("Design", "What quality gates would you put in CI for a large Python codebase, and how do you keep CI fast?",
short="""Fast, automated, blocking gates on every PR: formatter and linter (Ruff), type checking (mypy/pyright) with a ratchet, unit tests with coverage on changed code, dependency and security scans (pip-audit, Bandit rules), and build/packaging checks; slower integration and hardware-in-the-loop suites on merge or nightly. Keep it fast with caching, test selection by impact, parallelism (`pytest -n auto`), and a time budget per stage.""",
deep="""Stage design:

1. **Pre-commit (seconds)**: Ruff format + lint (replaces flake8, isort, pyupgrade and many plugins, very fast), secrets scan.
2. **PR gate (target under 10 minutes)**: type check, unit tests with simulated devices, coverage threshold on changed lines (diff coverage), `pip-audit`, build wheels, import-linter architecture contracts.
3. **Merge/nightly**: integration tests, HIL suite on a canary rack, performance benchmarks with regression detection, full matrix of Python versions.

Keeping it fast:

- Cache dependency installs (uv is dramatically faster than pip) and tool caches (mypy, Ruff).
- Run independent jobs in parallel; `pytest-xdist` inside test jobs.
- Test impact analysis: run tests related to changed packages first (or only, with a full run nightly).
- Watch CI duration as a metric; flaky tests are quarantined, not retried silently.

Governance: gates are defined centrally (shared CI templates) so 50 repos don't drift; exceptions are explicit and time-limited.""",
code=r'''
# pyproject.toml excerpt (shown as data) -- the configuration most gates hang off
PYPROJECT = """
[tool.ruff]
line-length = 100
target-version = "py312"
[tool.ruff.lint]
select = ["E", "F", "B", "UP", "S", "PERF", "SIM", "I"]   # bugs, upgrades, security, perf
[tool.mypy]
python_version = "3.12"
warn_unused_ignores = true
[[tool.mypy.overrides]]
module = ["acme.core.*", "acme.hal.*"]
strict = true
[tool.pytest.ini_options]
addopts = "-q -n auto --strict-markers --cov=acme --cov-fail-under=80"
markers = ["hil: needs real hardware", "slow: > 60 s"]
"""
import tomllib
cfg = tomllib.loads(PYPROJECT)
print("ruff rule families:", cfg["tool"]["ruff"]["lint"]["select"])
print("strict typing for :", cfg["tool"]["mypy"]["overrides"][0]["module"])
print("pytest defaults   :", cfg["tool"]["pytest"]["ini_options"]["addopts"])
''',
follow=(
"Developers complain CI takes 45 minutes. What do you do first? => Measure where the time goes per stage, then cache installs, parallelize, move slow suites off the PR path to merge/nightly, and fix or quarantine the slowest and flakiest tests.",
"How do you roll out a new strict lint rule to a large codebase? => Enable it with a baseline of existing violations (or per-file ignores), fail only on new violations, and fix the backlog gradually or with autofix where safe.",
),
pitfall="Making every check blocking on day one across 50 repositories. Teams add blanket ignores to get unblocked and the gates lose credibility.",
signals="You layer gates by speed and cost, name concrete tools, keep CI fast with caching, parallelism and impact analysis, and introduce new rules with baselines.",
),

]
