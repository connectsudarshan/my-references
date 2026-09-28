"""Compile-check the code snippets of 500_CPP_Interview_Questions_Reference.html with g++."""
import json, os, re, subprocess, sys, tempfile, concurrent.futures as cf
HDRS = """algorithm any array atomic bitset cassert chrono cmath condition_variable cstdint cstdio cstdlib cstring
deque exception forward_list fstream functional future initializer_list iomanip iostream iterator limits list map
memory mutex new numeric optional queue random set shared_mutex span sstream stack stdexcept string string_view thread
tuple type_traits typeinfo typeindex unordered_map unordered_set utility variant vector concepts ranges compare
coroutine format regex""".split()
PRE = "".join(f"#include <{h}>\n" for h in HDRS) + "using namespace std::string_literals;\n"
def attempt(src, extra_main):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "t.cpp")
        open(f, "w", encoding="utf-8").write(PRE + src + ("\nint main(){return 0;}\n" if extra_main else "\n"))
        r = subprocess.run(["g++", "-std=c++20", "-fsyntax-only", "-w", f], capture_output=True, text=True, encoding="utf-8", errors="replace")
        errs = [l.split("error:", 1)[1].strip() for l in r.stderr.splitlines() if "error:" in l]
        return r.returncode == 0, errs
def check(s):
    code = s["code"]; has_main = re.search(r"\bint\s+main\s*\(", code)
    ok, e1 = attempt(code, not has_main)
    if ok: return s["num"], "OK", []
    if not has_main:
        ok2, e2 = attempt("int main(){\n" + code + "\nreturn 0;}\n", False)
        if ok2: return s["num"], "OK-in-main", []
        e1 = e1 if len(e1) <= len(e2) else e2
    return s["num"], "FAIL", e1[:3]
snips = json.load(open(os.path.join(os.path.dirname(__file__), "_snippets.json"), encoding="utf-8"))
with cf.ThreadPoolExecutor(8) as ex:
    res = sorted(ex.map(check, snips))
json.dump(res, open(os.path.join(os.path.dirname(__file__), "_results.json"), "w"))
from collections import Counter
print(Counter(r[1] for r in res))

# ---- third attempt: split top-level definitions from statements ----
DEF = re.compile(r"^\s*(#|class\b|struct\b|union\b|enum\b|namespace\b|template\b|using\b|typedef\b|extern\b|static_assert\b|concept\b|inline\b|constexpr\b|consteval\b|\[\[)"
                 r"|^\s*[\w:<>,\*&\s~\[\]]+?\b[\w:~<>=!+\-*/\[\]()]+\s*\([^;]*\)\s*(const|noexcept|override|final|volatile|&|&&|->\s*[\w:<>]+|\s)*\s*(\{|=\s*(default|delete|0)\s*;|$)")
def split(code):
    glob, stmts, chunk, depth = [], [], [], 0
    for line in code.splitlines():
        chunk.append(line)
        depth += line.count("{") - line.count("}")
        if depth <= 0 and (line.rstrip().endswith((";", "}")) or line.strip().startswith(("#", "//")) or not line.strip()):
            text = "\n".join(chunk); first = next((l for l in chunk if l.strip() and not l.strip().startswith("//")), "")
            (glob if DEF.search(first) or first.strip().startswith("#") else stmts).append(text)
            chunk, depth = [], 0
    if chunk: stmts.append("\n".join(chunk))
    return "\n".join(glob), "\n".join(stmts)
def check3(s):
    g, st = split(s["code"])
    ok, errs = attempt(g + "\nint main(){\n" + st + "\nreturn 0;}\n", False)
    return s["num"], ("OK-split" if ok else "FAIL"), errs[:3]
if "--retry" in sys.argv:
    fails = {r[0] for r in res if r[1] == "FAIL"}
    with cf.ThreadPoolExecutor(8) as ex:
        res2 = {n: (st, e) for n, st, e in ex.map(check3, [s for s in snips if s["num"] in fails])}
    res = [[n, *res2[n]] if n in res2 else [n, st, e] for n, st, e in res]
    json.dump(res, open(os.path.join(os.path.dirname(__file__), "_results.json"), "w"))
    print("after split attempt:", Counter(r[1] for r in res))
    for n, st, e in res:
        if st == "FAIL": print(f"Q{n:3} {e[0][:100] if e else ''}")
