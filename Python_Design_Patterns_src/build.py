"""Build the Python Design Patterns Field Reference page.

Usage (from this folder):
    python build.py            # run every snippet, write out/ pages
    python build.py --check    # run snippets only, report failures
    python build.py --out DIR  # write pages to DIR instead of ./out

Content lives in content/*.py. Each file defines PATTERNS = [ {...}, ... ].
Every `code` and `pythonic` snippet is executed in a fresh interpreter;
its stdout is embedded in the page as the "Output" block. A snippet that
raises or times out fails the build.
"""
import importlib.util, json, pathlib, subprocess, sys, textwrap

HERE = pathlib.Path(__file__).resolve().parent
CONTENT = HERE / "content"
OUT = HERE / "out"
for i, a in enumerate(sys.argv):
    if a == "--out":
        OUT = pathlib.Path(sys.argv[i + 1])
CAT_ORDER = ["creational", "structural", "behavioral", "pythonic"]
REQUIRED = ["id", "cat", "name", "alias", "simple", "intent", "code",
            "examples", "use", "avoid", "pitfall", "qa"]


def load_patterns():
    pats = []
    for f in sorted(CONTENT.glob("*.py")):
        spec = importlib.util.spec_from_file_location(f.stem, f)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        pats.extend(mod.PATTERNS)
    return pats


def run(code, label):
    code = textwrap.dedent(code).strip() + "\n"
    r = subprocess.run([sys.executable, "-X", "utf8", "-c", code],
                       capture_output=True, text=True, timeout=30, encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError(f"{label} failed:\n{r.stderr}")
    return code.rstrip("\n"), r.stdout.rstrip("\n")


def validate(p, ids):
    errs = [f"{p.get('id')}: missing {k}" for k in REQUIRED if not p.get(k)]
    if p.get("cat") not in CAT_ORDER:
        errs.append(f"{p['id']}: bad cat {p.get('cat')}")
    if len(p.get("examples", [])) < 4:
        errs.append(f"{p['id']}: needs >= 4 real-world examples")
    for ex in p.get("examples", []):
        if ex.get("where") not in ("stdlib", "framework", "production"):
            errs.append(f"{p['id']}: example '{ex.get('title')}' has bad where")
    for r in p.get("related", []):
        if r not in ids:
            errs.append(f"{p['id']}: related id '{r}' not found")
    return errs


def main():
    check_only = "--check" in sys.argv
    pats = load_patterns()
    ids = {p["id"] for p in pats}
    errs = [e for p in pats for e in validate(p, ids)]
    if len(ids) != len(pats):
        errs.append("duplicate ids")
    for p in pats:
        for key in ("code", "pythonic"):
            if p.get(key):
                try:
                    p[key], p[key + "_out"] = run(p[key], f"{p['id']}.{key}")
                except Exception as e:  # noqa: BLE001
                    errs.append(str(e))
    if errs:
        print("ERRORS:\n  " + "\n  ".join(errs))
        sys.exit(1)
    pats.sort(key=lambda p: CAT_ORDER.index(p["cat"]))
    n_ex = sum(len(p["examples"]) for p in pats)
    print(f"OK: {len(pats)} patterns, {n_ex} real-world examples, all snippets ran")
    if check_only:
        return
    data = json.dumps(pats, ensure_ascii=False).replace("</", "<\\/")
    tpl = (HERE / "template.html").read_text(encoding="utf-8")
    frag = tpl.replace("/*__DATA__*/[]", data)
    OUT.mkdir(exist_ok=True)
    (OUT / "Python_Design_Patterns_fragment.html").write_text(frag, encoding="utf-8")
    full = '<!DOCTYPE html>\n<html lang="en">\n<meta charset="UTF-8">\n' + frag
    (OUT / "Python_Design_Patterns_Field_Reference.html").write_text(full, encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
