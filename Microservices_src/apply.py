"""Merge Microservices_src/extras*.py into 'Microservices Interview Reference.html'.

Adds per topic: Key terms (after 'In simple words'), Common pitfalls (after the use/avoid boxes)
and extra interview questions (appended to the topic's list). Idempotent: re-running replaces
the previous injection.  Run from the repository root:  python Microservices_src/apply.py
"""
import glob, html, json, os, re, runpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "Microservices Interview Reference.html")

CSS = """
/* --- ms extra --- */
.terms{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:0 0 6px 0;}
.term{padding:11px 14px;border-radius:6px;border:1px solid var(--line-soft);background:var(--bg-panel);}
.term b{display:block;font-size:13.5px;color:var(--accent);margin-bottom:3px;}
.term span{font-size:13.5px;line-height:1.55;color:var(--text-dim);}
.pitfalls{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:10px;}
.pitfalls li{padding:12px 16px;border-radius:6px;border:1px solid var(--line-soft);border-left:3px solid var(--bad);background:var(--bg-panel);}
.pitfalls .pm{font-size:14px;font-weight:600;margin:0 0 4px 0;}
.pitfalls .pf{font-size:13.5px;line-height:1.6;color:var(--text-dim);margin:0;}
.pitfalls .pf::before{content:'Fix: ';color:var(--good);font-weight:600;}
@media (max-width:700px){.terms{grid-template-columns:1fr;}}
/* --- end ms extra --- */
"""

JS = """<script id="ms-extra">
const MS_EXTRA = __DATA__;
TOPICS.forEach(t => { const e = MS_EXTRA[t.id]; if (!e) return;
  t.terms = e.terms; t.pitfalls = e.pitfalls; t.qa = (t.qa || []).concat(e.qa); });
</script>
"""

TERMS_JS = ("/*ms-extra-terms*/if(t.terms&&t.terms.length){h+='<div class=\"section-label\">KEY TERMS</div><div class=\"terms\">'+"
            "t.terms.map(x=>'<div class=\"term\"><b>'+x[0]+'</b><span>'+x[1]+'</span></div>').join('')+'</div>';}\n  ")
PIT_JS = ("/*ms-extra-pitfalls*/if(t.pitfalls&&t.pitfalls.length){h+='<div class=\"section-label\">COMMON PITFALLS</div><ul class=\"pitfalls\">'+"
          "t.pitfalls.map(x=>'<li><p class=\"pm\">'+x[0]+'</p><p class=\"pf\">'+x[1]+'</p></li>').join('')+'</ul>';}\n  ")


def inline(s):
    s = html.escape(s, quote=False)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", s)


def main():
    data = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "Microservices_src", "extras*.py"))):
        for tid, d in runpy.run_path(f)["EXTRA"].items():
            assert tid not in data, f"duplicate topic {tid}"
            data[tid] = {
                "terms": [[inline(a), inline(b)] for a, b in d["terms"]],
                "pitfalls": [[inline(a), inline(b)] for a, b in d["pitfalls"]],
                "qa": [{"q": inline(q), "a": "".join("<p>" + inline(p.strip()) + "</p>" for p in a.split("\n\n"))}
                       for q, a in d["qa"]],
            }
    page = open(PAGE, encoding="utf-8").read()
    # strip previous injection
    page = re.sub(r"\n/\* --- ms extra --- \*/.*?/\* --- end ms extra --- \*/\n", "\n", page, flags=re.S)
    page = re.sub(r'<script id="ms-extra">.*?</script>\n', "", page, flags=re.S)
    page = re.sub(r"/\*ms-extra-(terms|pitfalls)\*/.*?\n  ", "", page)
    # inject
    page = page.replace("</style>", CSS + "</style>", 1)
    anchor = "<script>\nconst CATS"
    assert page.count(anchor) == 1, "CATS script anchor not found"
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = page.replace(anchor, JS.replace("__DATA__", blob) + anchor)
    a1 = "'<div class=\"section-label\">DETAILED EXPLANATION</div><div class=\"intent\">'+t.intent+'</div>';\n\n  "
    a2 = "if(t.qa && t.qa.length){"
    assert page.count(a1) == 1 and page.count(a2) == 1, "renderer anchors not found"
    page = page.replace(a1, a1 + TERMS_JS).replace(a2, PIT_JS + a2)
    open(PAGE, "w", encoding="utf-8", newline="\n").write(page)
    n = sum(len(d["qa"]) for d in data.values())
    print(f"extras applied to {len(data)} topics: {sum(len(d['terms']) for d in data.values())} terms, "
          f"{sum(len(d['pitfalls']) for d in data.values())} pitfalls, {n} questions")


if __name__ == "__main__":
    main()
