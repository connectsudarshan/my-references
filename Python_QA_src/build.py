"""Build the Python Interview Questions Reference page.

Usage (from this folder):
    python build.py            # run every snippet, write out/ pages
    python build.py --check    # validate + run snippets, no output files
    python build.py --only 7   # run snippets of section 7 only (fast iteration)

Content: content/sNN_*.py, each defining QUESTIONS = [Q(...), ...] using the
helper `Q(section, level, question, answer, code=None, run=True)`.
- level: "Easy" | "Moderate" | "Difficult"
- answer: plain text; `inline code` and **bold** are rendered; blank line = new paragraph
- code: a complete snippet; unless run=False it is executed in a fresh
  interpreter and its stdout (and a final traceback line, if it is meant
  to raise) is shown as the Output block.
"""
import json, pathlib, subprocess, sys, tempfile, textwrap, runpy

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"

SECTIONS = {
    1: "Python Basics & Syntax",
    2: "Data Types, Variables & Mutability",
    3: "Strings & Text",
    4: "Lists, Tuples, Dicts & Sets",
    5: "Functions, Arguments & Scope",
    6: "Object-Oriented Programming",
    7: "Inheritance, MRO & Polymorphism",
    8: "Dunder Methods & the Data Model",
    9: "Iterators, Generators & Comprehensions",
    10: "Decorators & Context Managers",
    11: "Exceptions & Error Handling",
    12: "Modules, Packages & Imports",
    13: "Memory Management & Garbage Collection",
    14: "Concurrency: GIL, Threads, Processes & asyncio",
    15: "Standard Library Essentials",
    16: "Type Hints & Modern Python (3.8 - 3.14)",
    17: "Metaprogramming: Descriptors, Metaclasses & __slots__",
    18: "Testing, Debugging & Logging",
    19: "Performance & Optimization",
    20: "Coding Problems (Interview-Round Style)",
    21: "Tricky Questions & Gotchas",
}
LEVELS = ("Easy", "Moderate", "Difficult")


class Q(dict):
    def __init__(self, section, level, question, answer, code=None, run=True, expect_error=False):
        super().__init__(section=section, level=level, question=question.strip(),
                         answer=textwrap.dedent(answer).strip(),
                         code=textwrap.dedent(code).strip() if code else "",
                         run=bool(code) and run, expect_error=expect_error)


def load():
    qs = []
    for f in sorted((HERE / "content").glob("s*.py")):
        ns = runpy.run_path(str(f), init_globals={"Q": Q})
        qs.extend(ns["QUESTIONS"])
    return qs


def execute(q):
    # run from a real file (not -c) so multiprocessing's spawn start method works
    with tempfile.TemporaryDirectory() as d:
        script = pathlib.Path(d, "snippet.py")
        script.write_text(q["code"] + "\n", encoding="utf-8")
        r = subprocess.run([sys.executable, "-X", "utf8", str(script)],
                           capture_output=True, text=True, timeout=120, encoding="utf-8",
                           cwd=d)
    out = r.stdout.rstrip("\n")
    if r.returncode != 0:
        if not q["expect_error"]:
            raise RuntimeError(r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "failed")
        last = r.stderr.strip().splitlines()[-1]
        out = (out + "\n" if out else "") + "Traceback (most recent call last): ...\n" + last
    elif q["expect_error"]:
        raise RuntimeError("expected an exception but the snippet succeeded")
    return out


def main():
    only = None
    if "--only" in sys.argv:
        only = int(sys.argv[sys.argv.index("--only") + 1])
    qs = load()
    errs = []
    for i, q in enumerate(qs):
        tag = f"s{q['section']} #{i + 1} {q['question'][:60]!r}"
        if q["section"] not in SECTIONS: errs.append(f"{tag}: bad section")
        if q["level"] not in LEVELS: errs.append(f"{tag}: bad level {q['level']}")
        if not q["answer"]: errs.append(f"{tag}: empty answer")
        q["output"] = ""
        if q["run"] and (only is None or q["section"] == only):
            try:
                q["output"] = execute(q)
            except Exception as e:  # noqa: BLE001
                errs.append(f"{tag}: {e}")
    qs.sort(key=lambda q: q["section"])          # stable: keeps file order inside a section
    for n, q in enumerate(qs, 1):
        q["num"] = n
        q["sectionTitle"] = SECTIONS[q["section"]]
        del q["run"], q["expect_error"]
    counts = {s: sum(1 for q in qs if q["section"] == s) for s in SECTIONS}
    print("per section:", counts)
    print("levels:", {l: sum(1 for q in qs if q["level"] == l) for l in LEVELS})
    print(f"total {len(qs)} questions, {sum(1 for q in qs if q['code'])} with code, "
          f"{sum(1 for q in qs if q['output'])} with executed output")
    if errs:
        print("ERRORS:\n  " + "\n  ".join(errs)); sys.exit(1)
    if "--check" in sys.argv or only is not None:
        return
    data = json.dumps(qs, ensure_ascii=False).replace("</", "<\\/")
    tpl = (HERE / "template.html").read_text(encoding="utf-8")
    frag = tpl.replace("/*__DATA__*/[]", data).replace("/*__SECTIONS__*/{}", json.dumps(SECTIONS))
    OUT.mkdir(exist_ok=True)
    (OUT / "Python_QA_fragment.html").write_text(frag, encoding="utf-8")
    full = '<!DOCTYPE html>\n<html lang="en">\n<meta charset="UTF-8">\n' + frag
    (OUT / "Python_Interview_Questions_Reference.html").write_text(full, encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
