#!/usr/bin/env bash
# Dev helper: apply deep dives, syntax-check the page, commit one section.
# usage: bash CPP_QA_src/step.sh <section-number> "<commit title>" "<body>"
set -e
cd "$(dirname "$0")/.."
python CPP_QA_src/apply_deep.py
python -c "import re;s=open('500_CPP_Interview_Questions_Reference.html',encoding='utf-8').read();open('_c.js','w',encoding='utf-8').write('\n'.join(re.findall(r'<script(?: id=\"\w+\")?>(.*?)</script>',s,re.S)))"
node --check _c.js && rm -f _c.js
rm -rf CPP_QA_src/__pycache__
git add 500_CPP_Interview_Questions_Reference.html "CPP_QA_src/deep/s$(printf %02d "$1").py"
git commit -q -m "$2" -m "$3" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git log --oneline -1
