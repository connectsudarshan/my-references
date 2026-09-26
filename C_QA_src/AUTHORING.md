# Authoring guide for the C Language Q&A Study Guide

## Who this is for
Sudarshan K: 12+ years in storage/firmware, preparing for a **Principal SSD Firmware Validation Engineer** interview (Micron, Bengaluru). This page teaches C from Basic to Principal, weighted toward embedded/firmware-relevant C (memory, pointers, bit manipulation, undefined behavior, low-level data layout) and includes the classic coding-round questions with real code, not just conceptual Q&A. Accuracy matters more than volume: a wrong claim about the C standard, or code that does not actually compile and behave as described, is worse than no answer.

## Files
- Topic directory: `/home/claude/c/` (content goes in `/home/claude/c/content/mNN.txt`, NN = two-digit module number).
- You write ONLY your own module file(s). Do not edit any other file.
- Read `/home/claude/c/modules.json` and the module list below so you know what other authors cover. Do not overlap: a related but different-purpose topic exists on the sibling "C Advanced" page (`/home/claude/cadv/modules.json`) covering OS/threads/concurrency -- if your module touches threading, memory ordering across threads, or process concepts, mention it in one sentence and point there rather than re-teaching it. `volatile` for a single-threaded hardware register (this page, module 7) is different from the multi-threaded memory model (the other page's module 7); do not conflate them.
- Validate your file with: `python3 /home/claude/study/build.py /home/claude/c --check /home/claude/c/content/mNN.txt`. Fix every ERROR. Do NOT run a full build.

## Grounding sources (read before writing, use for every spec-sensitive claim)
- `/home/claude/spec/c11_n1570.txt`: the ISO/IEC 9899:201x (C11) draft standard, N1570, full text (~34500 lines). This is the primary source for language semantics: type rules, operator behavior, undefined/unspecified/implementation-defined behavior, the preprocessor, and the standard library's documented contracts. Use `grep -n "6.5.3"` style section-number searches, or `grep -n -i "keyword"`, then read the surrounding text with `sed -n 'A,Bp'`. For your assigned modules, read the applicable clauses in full rather than only grep-jumping to isolated hits; C11 is long overall but any one module's relevant clauses are a small, boundable slice (typically a handful of numbered sections) -- read that slice completely.
- Where a question needs POSIX (not ISO C) content -- for example any pthreads, signals, or OS-facing function -- that belongs on the C Advanced page, not here; if you must reference it briefly, add a `VERIFY:` naming "POSIX.1-2017" and move on.
- Where C17 or C23 changed something relevant (a small number of cases: e.g. C23 added `nullptr`, removed K&R-style function definitions, added `#embed`), you may mention it in one sentence for currency, clearly labeled "C17/C23:", but keep C11 as the primary reference since it is what most toolchains and interviewers still assume.
- Do not invent a clause number. If you cite one, verify it by grepping the text file for that exact number.

## Real code requirement (this is what makes this page different from a generic C FAQ)
- Every question whose SHORT or DEEP promises "here is the code" must contain a real, complete-enough C snippet inside a ```c fenced block, and that snippet must actually compile and (where it produces output) run correctly. Before finalizing a question with code, write the snippet to a scratch file under `/tmp` and compile it: `gcc -std=c11 -Wall -Wextra -o /tmp/test_mNN_X /tmp/test_mNN_X.c` (add `-lpthread` etc. only if truly needed; this page should need no threading). Fix any warning your own text claims should not exist; a warning that is the point of the question (e.g. demonstrating UB) may be explained rather than silenced.
- Code inside the page should be realistic and minimal: a runnable `main()` or a clearly-labeled standalone function, not a truncated fragment that would not actually compile if pasted. Prefer showing a small `main()` with a `printf` of the result so a reader can verify it themselves.
- For a question that demonstrates undefined behavior, still compile it (compilers usually accept it), and say what you actually observed with your toolchain plus that the standard leaves it undefined -- never claim a specific UB outcome is guaranteed.
- Note the compiler and flags you tested with in the DEEP text only if it is load-bearing (e.g. "compiled with gcc -std=c11 -Wall"); do not clutter every question with a boilerplate compiler line.

## File format (one block per question, ids `N.01`, `N.02`, ... consecutive, no gaps)
```
# Module N: Title

@@ N.01 | Basic | Concept | fig=<key> | tags=tag1,tag2
Q: question text (one line)
SHORT: the 30-second answer, 1-3 sentences, <= 460 characters (hard limit 500)
DEEP:
paragraphs, "- " bullets (nest with 2-space indent), "1. " numbered lists, | tables |, ```c code fences```, `inline code`, **bold**
FOLLOW:
- follow-up question => brief answer (one line each; 2 per question)
PITFALL: one common mistake (one line)
VERIFY: spec-sensitive facts to double check (optional, one line)
```
- Levels (exact): `Basic`, `Intermediate`, `Advanced`, `Principal`.
- Types (exact): `Concept`, `Numeric`, `Scenario`, `Debug`, `Cross-layer`, `Trap`. (`Cross-layer` here means "spans language and hardware/OS", e.g. volatile+registers, alignment+cache lines; `Trap` means a classic gotcha/UB question.)
- `fig=` is optional and must be exactly one of the diagram keys assigned to your module. Use it once, on the question it illustrates best.
- Markdown tables must start at column 0 with `|`. Never put a table inside a bullet.
- Code fences: use ```c for C code. Never put a `Q:`/`SHORT:`/`DEEP:`/etc. keyword-looking line inside a fence unless it is genuinely inside the fence (fences are tracked correctly by the build script as long as every ``` is on its own line).
- Plain ASCII punctuation. No em dashes. No emojis. Avoid the words "genuinely", "honestly", "straightforward".

## Mix per module (16-20 questions)
Roughly: 3 Basic, 5-6 Intermediate, 5-6 Advanced, 3-4 Principal. Every module should include real code wherever the topic is code-shaped (most of them). Include at least one Numeric (a worked calculation: sizeof/alignment math, bit math, pointer arithmetic math), one Debug (reading a crash, a sanitizer report, or a subtly wrong snippet and finding the bug), and one Scenario or Trap where natural. Weight examples toward embedded/firmware realism (register access, protocol structs, ISR constraints) where the module allows it.

A good Principal question asks the reader to design, review, or root-cause something and states a concrete method plus a pitfall, not just a definition.

## Deliverable and report
When your file(s) pass `--check`, re-read once for factual slips and code that only "looks" right, then reply with a brief report (under 150 words): file(s) written, question counts, which code snippets you actually compiled and ran (by question id), any facts you were unsure of, and any suggested change to your assigned diagram.

## Module list for this page
1. Types, Storage Classes, Scope & Linkage
2. Operators, Expressions & Sequence Points
3. Control Flow & Program Structure
4. Pointers Deep Dive
5. Arrays, Strings & Memory Layout
6. Structures, Unions & Bit-Fields
7. Type Qualifiers: const, volatile, restrict
8. Dynamic Memory Management
9. The Preprocessor & Macros
10. Undefined Behavior & Standard Compliance
11. Bit Manipulation & Numeric Representation
12. Function Pointers & C-Style Polymorphism
13. Compilation, Linking & the Build Pipeline
14. Standard Library Internals
15. Core Data Structures & Algorithms in C
16. Debugging, Tooling & Sanitizers
17. Embedded, Firmware & Secure Coding in C
18. Principal-Level Systems Design in C

(Full scope text for each is in `/home/claude/c/briefs.json`.)
