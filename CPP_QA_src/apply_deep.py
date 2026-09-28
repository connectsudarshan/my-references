"""Merge deep-dive additions (deep/sNN.py) into 500_CPP_Interview_Questions_Reference.html.

    python apply_deep.py

Each deep/sNN.py defines DEEP = {question_number: D(definition, explanation, pitfall, follow)}.
Existing questions, answers and code are untouched; the page shows the additions in
extra blocks (Definition, Deep dive, Pitfall, Follow-ups). Re-running replaces the
previously injected block, so it is safe to run after every new section.
Text supports `code`, **bold** and blank-line paragraphs.
"""
import json, pathlib, re, runpy, sys

HERE = pathlib.Path(__file__).resolve().parent
PAGE = HERE.parent / "500_CPP_Interview_Questions_Reference.html"


def D(definition, explanation, pitfall, follow):
    for f in follow:
        assert "=>" in f, f"follow-up without '=>': {f[:40]}"
    return {"d": definition.strip(), "x": explanation.strip(), "p": pitfall.strip(), "f": [f.strip() for f in follow]}


CSS = """
/* --- deep upgrade --- */
.deep-def{margin:0 0 16px 0;padding:12px 16px;border-radius:6px;border:1px solid rgba(126,200,227,0.35);background:rgba(126,200,227,0.07);font-size:15px;line-height:1.65;}
.deep-lbl{display:block;font-family:'IBM Plex Mono',monospace;font-size:10.5px;letter-spacing:0.08em;margin-bottom:4px;}
.deep-def .deep-lbl{color:#7ec8e3;}
.deep-x{margin-top:18px;font-size:15px;line-height:1.75;color:var(--text);}
.deep-x p{margin:0 0 10px 0;}
.deep-x .deep-lbl,.deep-f .deep-lbl{color:var(--accent);}
.deep-pit{margin-top:16px;padding:12px 16px;border-radius:6px;border:1px solid rgba(255,157,157,0.35);background:rgba(255,157,157,0.06);font-size:14px;line-height:1.65;}
.deep-pit .deep-lbl{color:#ff9d9d;}
.deep-f{margin-top:18px;}
.deep-f details{background:var(--bg-panel);border:1px solid var(--line-soft);border-radius:6px;margin-top:8px;}
.deep-f summary{cursor:pointer;padding:10px 14px;font-weight:600;font-size:14px;}
.deep-f summary:focus-visible{outline:2px solid var(--accent);outline-offset:-2px;}
.deep-f .fa{padding:0 14px 12px 14px;font-size:14px;line-height:1.65;color:var(--text-dim);}
.deep-def code,.deep-x code,.deep-pit code,.deep-f code{background:rgba(255,255,255,0.07);padding:1px 5px;border-radius:3px;font-size:0.9em;color:#ffd199;font-family:'IBM Plex Mono',monospace;}
/* --- end deep upgrade --- */
"""

JS = """<script id="qdeep">
const DEEP = __DEEP__;
QUESTIONS.forEach(q => { if (DEEP[q.num]) q.deep = DEEP[q.num]; });
function deepInline(s){
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/`([^`]+)`/g,'<code>$1</code>').replace(/\\*\\*([^*]+)\\*\\*/g,'<strong>$1</strong>');
}
function deepParas(s){ return String(s).split(/\\n\\s*\\n/).map(p => '<p>' + deepInline(p.replace(/\\n/g,' ')) + '</p>').join(''); }
function renderDeepTop(q){
  return q.deep ? `<div class="deep-def"><span class="deep-lbl">DEFINITION</span>${deepInline(q.deep.d)}</div>` : '';
}
function renderDeepBottom(q){
  if (!q.deep) return '';
  const f = q.deep.f.map(x => { const [a, b] = x.split('=>'); return `<details><summary>${deepInline(a.trim())}</summary><div class="fa">${deepInline(b.trim())}</div></details>`; }).join('');
  return `<div class="deep-x"><span class="deep-lbl">DEEP DIVE</span>${deepParas(q.deep.x)}</div>` +
         `<div class="deep-pit"><span class="deep-lbl">COMMON PITFALL</span>${deepInline(q.deep.p)}</div>` +
         `<div class="deep-f"><span class="deep-lbl">LIKELY FOLLOW-UPS</span>${f}</div>`;
}
</script>
"""

PATCHES = [
    ('<div class="q-answer">${renderAnswer(q.answer)}</div>\n      ${codeHtml}',
     '${renderDeepTop(q)}\n      <div class="q-answer">${renderAnswer(q.answer)}</div>\n      ${codeHtml}\n      ${renderDeepBottom(q)}'),
]


def main():
    deep = {}
    for f in sorted((HERE / "deep").glob("s*.py")):
        part = runpy.run_path(str(f), init_globals={"D": D})["DEEP"]
        dup = set(part) & set(deep)
        if dup: sys.exit(f"{f.name}: duplicate question numbers {sorted(dup)}")
        deep.update(part)
    html = PAGE.read_text(encoding="utf-8")
    html = re.sub(r"\n/\* --- deep upgrade --- \*/.*?/\* --- end deep upgrade --- \*/\n", "\n", html, flags=re.S)
    html = re.sub(r'<script id="qdeep">.*?</script>\n', "", html, flags=re.S)
    html = html.replace("</style>", CSS + "</style>", 1)
    payload = json.dumps(deep, ensure_ascii=False).replace("</", "<\\/")
    anchor = '<script id="qdata">'
    end = html.index("</script>", html.index(anchor)) + len("</script>\n")
    html = html[:end] + JS.replace("__DEEP__", payload) + html[end:]
    for old, new in PATCHES:
        if new in html: continue
        if old not in html: sys.exit(f"patch anchor not found: {old[:60]!r}")
        html = html.replace(old, new, 1)
    PAGE.write_text(html, encoding="utf-8")
    print(f"applied deep dives for {len(deep)} of 500 questions")


if __name__ == "__main__":
    main()
