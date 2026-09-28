"""Build the Python Principal Engineer Interview Guide.

Usage (from this folder):
    python build.py            # run every snippet, write out/ pages
    python build.py --check    # validate + run snippets, no output files
    python build.py --only 3   # run only module 3's snippets (fast iteration)

Content: content/mNN_*.py files. Each defines MODULE = dict(id, title, desc) and
QUESTIONS = [P(...), ...] using

    P(type, question, short, deep, code=None, follow=(), pitfall="", signals="",
      run=True, expect_error=False, level="Principal")

- type: Concept | Design | Scenario | Debug | Trap | Code review
- level: Advanced | Principal
- short: the 30-second answer; deep: the full explanation (markdown-ish:
  blank line = paragraph, "- " bullets, "1. " numbered, `code`, **bold**)
- follow: tuple of "question => answer" strings
- code is executed in a fresh interpreter from a temp file; stdout is shown.
"""
import json, pathlib, runpy, subprocess, sys, tempfile, textwrap

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
TYPES = ("Concept", "Design", "Scenario", "Debug", "Trap", "Code review")
LEVELS = ("Advanced", "Principal")


class P(dict):
    def __init__(self, type, question, short, deep, code=None, follow=(), pitfall="",
                 signals="", run=True, expect_error=False, level="Principal"):
        super().__init__(
            type=type, level=level, question=question.strip(),
            short=textwrap.dedent(short).strip(), deep=textwrap.dedent(deep).strip(),
            code=textwrap.dedent(code).strip() if code else "",
            follow=[f.strip() for f in follow], pitfall=pitfall.strip(), signals=signals.strip(),
            run=bool(code) and run, expect_error=expect_error)


def load():
    modules, qs = [], []
    for f in sorted((HERE / "content").glob("m*.py")):
        ns = runpy.run_path(str(f), init_globals={"P": P})
        m = ns["MODULE"]
        modules.append(m)
        for q in ns["QUESTIONS"]:
            q["module"] = m["id"]
            qs.append(q)
    return modules, qs


def execute(q):
    with tempfile.TemporaryDirectory() as d:
        script = pathlib.Path(d, "snippet.py")
        script.write_text(q["code"] + "\n", encoding="utf-8")
        r = subprocess.run([sys.executable, "-X", "utf8", str(script)], capture_output=True,
                           text=True, timeout=180, encoding="utf-8", cwd=d)
    out = r.stdout.rstrip("\n")
    if r.returncode != 0:
        last = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "failed"
        if not q["expect_error"]:
            raise RuntimeError(last)
        out = (out + "\n" if out else "") + "Traceback (most recent call last): ...\n" + last
    elif q["expect_error"]:
        raise RuntimeError("expected an exception but the snippet succeeded")
    return out


def main():
    only = int(sys.argv[sys.argv.index("--only") + 1]) if "--only" in sys.argv else None
    modules, qs = load()
    errs = []
    for q in qs:
        tag = f"m{q['module']} {q['question'][:60]!r}"
        if q["type"] not in TYPES: errs.append(f"{tag}: bad type {q['type']}")
        if q["level"] not in LEVELS: errs.append(f"{tag}: bad level {q['level']}")
        if len(q["short"]) > 520: errs.append(f"{tag}: short answer too long ({len(q['short'])})")
        if not q["deep"] or not q["pitfall"] or not q["signals"]: errs.append(f"{tag}: missing deep/pitfall/signals")
        if len(q["follow"]) < 2: errs.append(f"{tag}: needs 2+ follow-ups")
        for f in q["follow"]:
            if "=>" not in f: errs.append(f"{tag}: follow-up without '=>'")
        q["output"] = ""
        if q["run"] and (only is None or q["module"] == only):
            try:
                q["output"] = execute(q)
            except Exception as e:  # noqa: BLE001
                errs.append(f"{tag}: {e}")
    qs.sort(key=lambda q: q["module"])
    for n, q in enumerate(qs, 1):
        q["num"] = n
        del q["run"], q["expect_error"]
    print({m["id"]: sum(q["module"] == m["id"] for q in qs) for m in modules})
    print(f"total {len(qs)} questions, {sum(bool(q['code']) for q in qs)} with code, "
          f"{sum(bool(q['output']) for q in qs)} with executed output")
    if errs:
        print("ERRORS:\n  " + "\n  ".join(errs)); sys.exit(1)
    if "--check" in sys.argv or only is not None:
        return
    data = json.dumps({"modules": modules, "questions": qs}, ensure_ascii=False).replace("</", "<\\/")
    data = data.replace("�", "\\ufffd")          # keep decoded-garbage demo output as an escape
    tpl = (HERE / "template.html").read_text(encoding="utf-8")
    frag = tpl.replace("/*__DATA__*/{}", data)
    OUT.mkdir(exist_ok=True)
    (OUT / "Python_Principal_fragment.html").write_text(frag, encoding="utf-8")
    full = '<!DOCTYPE html>\n<html lang="en">\n<meta charset="UTF-8">\n' + frag
    (OUT / "Python_Principal_Engineer_Interview_Guide.html").write_text(full, encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
