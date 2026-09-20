# Authoring guide for the PCIe Q&A Study Guide (Phase 2, modules 7-18)

## Who this is for
Sudarshan K: 12+ years in storage/firmware, NVMe/ZNS/PCIe/SSD firmware validation. He is preparing for a **Principal SSD Firmware Validation Engineer** interview (Micron, Bengaluru). The page teaches PCIe from Basic to Principal, weighted to **SSD/NVMe validation and debug**. Accuracy matters more than volume: a wrong number or wrong register name in an interview is costly.

## Files
- Working directory: `/home/claude/pcie/`
- You write ONLY your own module files: `content/mNN.txt` (NN = two digits). Do not edit any other file (other authors are writing other modules in parallel; `shell.html`, `build.py`, `gen_diagrams.py` are owned by the lead).
- Style exemplars to read first: `content/m06.txt` (Data Link Layer) and `content/m04.txt` (LTSSM). Skim `content/m01.txt` too. Match their voice, depth and formatting exactly.
- To avoid repeating what modules 1-6 already cover, run `grep -h "^Q:" content/m0[1-6].txt` and read the list before you plan questions. Refer back briefly ("covered in the Data Link module") instead of re-teaching.
- Validate your files with: `python3 build.py --check content/mNN.txt` (from `/home/claude/pcie`). Fix every ERROR. Do NOT run the full `python3 build.py` (the lead does that).

## File format (one block per question, ids `N.01`, `N.02`, ... consecutive)
```
# Module N — Title

@@ N.01 | Basic | Concept | fig=<key> | tags=tag1,tag2
Q: question text (one line)
SHORT: the 30-second answer, 1-3 sentences, <= 460 characters (hard limit 500)
DEEP:
paragraphs, "- " bullets (nest with 2-space indent), "1. " numbered lists, | tables |, ``` code fences ```, `inline code`, **bold**
FOLLOW:
- follow-up question => brief answer (one line each; 2 per question)
PITFALL: one common mistake (one line)
VERIFY: spec-sensitive facts to double check (optional, one line)
```
- Levels (exact): `Basic`, `Intermediate`, `Advanced`, `Principal`.
- Types (exact): `Concept`, `Numeric`, `Scenario`, `Debug`, `Cross-layer`, `Trap`.
- `fig=` is optional and must be one of the diagram keys assigned to your module in your brief (the lead draws them). Use each assigned key on exactly one question, the one it illustrates best. Existing keys you may also reuse if truly apt: topology, lane, gens, stack, encap, pam4, ltssm, recovery, eq, eqphases, replay, dllp.
- Markdown tables must start at column 0 with `|`. Do not put a table inside a bullet.
- A line starting with `- ` or `1. ` inside DEEP is a list item; keep DEEP lists short (3-7 items). Keep DEEP to roughly 120-260 words per question, more only for Scenario/Numeric/Debug.
- `FOLLOW:` items each contain exactly one `=>` separator.
- Lines beginning with `Q:`, `SHORT:`, `DEEP:`, `FOLLOW:`, `PITFALL:`, `VERIFY:` at column 0 are keywords, so never start an ordinary DEEP line with one of those words followed by a colon.
- Plain ASCII punctuation preferred. No em dashes. No emojis. Avoid the words "genuinely", "honestly", "straightforward".

## Mix per module (15-18 questions)
Roughly: 3 Basic, 5 Intermediate, 5 Advanced, 3-4 Principal. Types: mostly Concept, but every module must include at least one each of Numeric (a worked calculation), Debug (reading registers/traces/counters and reasoning), and Scenario (a triage or design situation), plus a Trap where natural, and Cross-layer where a behavior spans layers or spans PCIe and NVMe. Weight examples toward SSD/NVMe validation and debug (NVMe over PCIe, link-up regressions, error injection, counters, analyzer traces, host tools like lspci/setpci/nvme-cli/fio on Linux and Windows equivalents).

A good Principal question asks "how would you design/automate/root-cause/quantify X", and its answer contains a method, evidence to collect, decision criteria and a pitfall. A good Numeric question shows the arithmetic step by step and states assumptions.

## Accuracy rules (important)
- Only state facts you are confident about. For anything you are unsure of, either check it with WebSearch/WebFetch (load via ToolSearch if deferred), or hedge the wording and add a `VERIFY:` line naming exactly what to check in the PCIe Base Specification or NVMe Base Specification. Put spec-sensitive numbers (timeouts, bit positions, register offsets, capability IDs, encodings) under VERIFY unless certain.
- Re-derive every calculation with a quick python one-liner before writing it down. Show assumptions.
- Cite spec generations correctly (Gen3 8 GT/s and 128b/130b; Gen4 16; Gen5 32; Gen6 64 GT/s PAM4 and FLIT; Gen7 128 GT/s). Cite "PCIe Base 6.x" for Gen6 features. NVMe: mention NVMe Base Specification 2.x where relevant.
- Do not invent register field names. If unsure of the exact name, describe the field in words.
- Config space is 4 KB total (256 B legacy + extended). Registers are named as in the spec (e.g. Device Control, Link Control, Link Status 2, AER Uncorrectable Error Status).
- Keep each question self-contained: a reader should be able to answer from SHORT and be corrected by DEEP.
- Do not overlap with other Phase 2 modules; if a topic straddles, cover the aspect that belongs to your module and mention the other module by name.

## Deliverable and report
When your files pass `--check`, re-read them once for factual slips, then reply with a brief report (under 150 words): files written, question counts, any facts you were unsure of, and any suggested change to the assigned diagram (only if the brief's diagram description is misleading).
