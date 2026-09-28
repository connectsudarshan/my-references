"""Upgrade CPP_Design_Patterns_Field_Reference.html in place with extras.py.

    python apply.py          # compile-check all patterns, then patch the page
    python apply.py --check  # compile-check only

Adds per pattern: definition (participants, consequences), 2 more real-world
examples, a modern C++ alternative and 3 interview questions. Existing content
is kept. Re-running is safe: previously injected blocks are replaced.
"""
import json, os, pathlib, re, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
PAGE = HERE.parent / "CPP_Design_Patterns_Field_Reference.html"
sys.path.insert(0, str(HERE))
from extras import EXTRAS  # noqa: E402

HEADERS = "".join(f"#include <{h}>\n" for h in (
    "iostream", "memory", "string", "vector", "map", "unordered_map", "mutex", "functional",
    "algorithm", "list", "stack", "queue", "variant", "sstream", "cstdint", "cmath"))
FIXES = [("root->print();", "root->print(0);   // defaults bind to the STATIC type: Directory::print has none")]


def patterns_from(html):
    js = re.search(r'<script id="pattern-data">([\s\S]*?)</script>', html).group(1)
    code = f"{js}\nprocess.stdout.write(JSON.stringify(PATTERNS.map(p=>({{id:p.id,code:p.code}}))));"
    r = subprocess.run(["node", "-"], input=code, capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(r.stdout)


def compiles(code):
    """Usage section inside main(); fall back to all-global when it only defines functions."""
    m = re.search(r"^// .*usage.*$", code, re.M | re.I)
    variants = [code] if not m else [code[:m.start()] + "\nint main() {\n" + code[m.start():] + "\nreturn 0;\n}\n", code]
    for src in variants:
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "t.cpp")
            pathlib.Path(f).write_text(HEADERS + src + ("" if "int main" in src else "\nint main() { return 0; }\n"))
            r = subprocess.run(["g++", "-std=c++17", "-fsyntax-only", "-Wall", f], capture_output=True, text=True)
            if r.returncode == 0:
                return True, ""
            last = next((l for l in r.stderr.splitlines() if "error" in l), r.stderr[:120])
    return False, last[last.find("error"):][:110]


CSS = """
/* --- upgrade: definition, modern C++, interview questions --- */
.defn{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:14px;}
.defn-box{padding:14px 16px;border-radius:6px;border:1px solid var(--line-soft);background:var(--bg-panel);}
.defn-box h4{margin:0 0 8px 0;font-size:12px;font-family:'IBM Plex Mono',monospace;letter-spacing:0.06em;color:var(--cat-creational);}
.defn-box ul{margin:0;padding-left:16px;font-size:13.5px;color:var(--text-dim);line-height:1.6;}
.defn-box code,.modern code,.qa-a code,.examples code{background:rgba(255,255,255,0.07);padding:1px 5px;border-radius:3px;font-size:0.9em;color:#ffd199;font-family:'IBM Plex Mono',monospace;}
.modern{padding:14px 18px;border-radius:6px;border:1px solid rgba(159,223,159,0.3);background:rgba(159,223,159,0.06);font-size:14px;line-height:1.7;}
.qa-list{display:flex;flex-direction:column;gap:10px;}
.qa-list details{background:var(--bg-panel);border:1px solid var(--line-soft);border-radius:6px;}
.qa-list summary{cursor:pointer;padding:12px 16px;font-weight:600;font-size:14.5px;list-style:none;}
.qa-list summary::-webkit-details-marker{display:none;}
.qa-list summary::before{content:'Q  ';font-family:'IBM Plex Mono',monospace;color:var(--accent);font-size:12px;}
.qa-list summary:focus-visible{outline:2px solid var(--accent);outline-offset:-2px;}
.qa-a{padding:0 16px 14px 16px;font-size:14px;line-height:1.7;color:var(--text-dim);}
@media(max-width:900px){.defn{grid-template-columns:1fr;}}
/* --- end upgrade --- */
"""

JS = """<script id="pattern-extras">
const EXTRAS = __EXTRAS__;
PATTERNS.forEach(p => {
  const x = EXTRAS[p.id]; if (!x) return;
  p.participants = x.participants; p.consequences = x.consequences; p.modern = x.modern; p.qa = x.qa;
  p.examples = p.examples.concat(x.moreExamples);
});
function mdInline(s){ return String(s).replace(/`([^`]+)`/g, (m, c) => '<code>' + c.replace(/</g,'&lt;').replace(/>/g,'&gt;') + '</code>'); }
function renderDefinition(p){
  if (!p.participants) return '';
  return `<div class="section-label">DEFINITION: PARTICIPANTS AND CONSEQUENCES</div>
    <div class="defn"><div class="defn-box"><h4>PARTICIPANTS</h4><ul>${p.participants.map(x=>`<li>${x}</li>`).join('')}</ul></div>
    <div class="defn-box"><h4>CONSEQUENCES</h4><ul>${p.consequences.map(x=>`<li>${x}</li>`).join('')}</ul></div></div>`;
}
function renderModern(p){
  return p.modern ? `<div class="section-label">MODERN C++ ALTERNATIVE</div><div class="modern">${mdInline(p.modern)}</div>` : '';
}
function renderQA(p){
  if (!p.qa) return '';
  return `<div class="section-label">INTERVIEW QUESTIONS (${p.qa.length})</div><div class="qa-list">` +
    p.qa.map(x => `<details><summary>${mdInline(x.q)}</summary><div class="qa-a">${mdInline(x.a)}</div></details>`).join('') + '</div>';
}
</script>
"""

PATCHES = [
    ('<p class="intent">${p.intent}</p>', '<p class="intent">${p.intent}</p>\n    ${renderDefinition(p)}'),
    ('<pre><code class="language-cpp">${escapeHtml(p.code)}</code></pre>\n    </div>',
     '<pre><code class="language-cpp">${escapeHtml(p.code)}</code></pre>\n    </div>\n    ${renderModern(p)}'),
    ('    <div class="footer-nav">\n      <button onclick="navigate(\'${prevNext.prev',
     '    ${renderQA(p)}\n\n    <div class="footer-nav">\n      <button onclick="navigate(\'${prevNext.prev'),
    ("each with a working C++17 implementation and 2–3 real production examples of where the pattern actually shows up",
     "each with a working C++17 implementation (compile-checked with g++), a formal definition (participants and consequences), 5 real production examples, the modern C++ alternative and interview questions"),
]


def main():
    html = PAGE.read_text(encoding="utf-8")
    for old, new in FIXES:
        html = html.replace(old, new)
    missing = [p for p in patterns_from(html) if p["id"] not in EXTRAS]
    if missing: sys.exit(f"extras missing for {[p['id'] for p in missing]}")
    print("compile check (g++ -std=c++17):")
    bad = 0
    for p in patterns_from(html):
        ok, err = compiles(p["code"])
        bad += not ok
        print(f"  {p['id']:24} {'OK' if ok else 'FAIL ' + err}")
    if bad: sys.exit(f"{bad} pattern(s) failed to compile")
    if "--check" in sys.argv: return

    html = re.sub(r"\n/\* --- upgrade: definition.*?/\* --- end upgrade --- \*/\n", "\n", html, flags=re.S)
    html = re.sub(r'<script id="pattern-extras">.*?</script>\n', "", html, flags=re.S)
    html = html.replace("</style>", CSS + "</style>", 1)
    extras_json = json.dumps(EXTRAS, ensure_ascii=False).replace("</", "<\\/")
    html = html.replace("<script>\nconst CATS = {", JS.replace("__EXTRAS__", extras_json) + "<script>\nconst CATS = {", 1)
    for old, new in PATCHES:
        if new in html: continue
        if old not in html: sys.exit(f"patch anchor not found: {old[:60]!r}")
        html = html.replace(old, new, 1)
    PAGE.write_text(html, encoding="utf-8")
    n_ex = sum(3 + len(v["moreExamples"]) for v in EXTRAS.values())
    print(f"patched {PAGE.name}: {len(EXTRAS)} patterns, {n_ex} examples, {sum(len(v['qa']) for v in EXTRAS.values())} interview questions")


if __name__ == "__main__":
    main()
