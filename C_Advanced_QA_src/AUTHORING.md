# Authoring guide for the C Advanced (OS, Threads & Concurrency) Q&A Study Guide

## Who this is for
Sudarshan K: 12+ years in storage/firmware, preparing for a **Principal SSD Firmware Validation Engineer** interview (Micron, Bengaluru). This is the advanced companion to the "C Language" page (`/home/claude/c/`), covering OS concepts, POSIX threads, synchronization, the memory model, and concurrency, with real pthreads code, not just definitions. Accuracy matters more than volume: a wrong claim about a POSIX guarantee, or concurrency code that does not actually demonstrate what it claims, is worse than no answer.

## Files
- Topic directory: `/home/claude/cadv/` (content goes in `/home/claude/cadv/content/mNN.txt`, NN = two-digit module number).
- You write ONLY your own module file(s). Do not edit any other file.
- Read `/home/claude/cadv/modules.json` and the module list below so you know what other authors cover. The sibling "C Language" page (`/home/claude/c/modules.json`) already covers plain-C pointers, memory layout for a single thread, and the `volatile` qualifier for hardware registers; do not re-teach those, refer back in one sentence ("see the C Language page, module 7") and cover only the multi-threaded angle.
- Validate your file with: `python3 /home/claude/study/build.py /home/claude/cadv --check /home/claude/cadv/content/mNN.txt`. Fix every ERROR. Do NOT run a full build.

## Grounding sources (read before writing, use for every spec-sensitive claim)
- `/home/claude/spec/posix14.txt`: 60 concatenated POSIX.1 man3p pages (the actual POSIX Programmer's Manual text, IEEE Std 1003.1, via the man-pages-posix project), covering pthreads, semaphores, mmap, fork/exec/wait, signals, scheduling, and more. Each page is delimited by a line `=====PAGE: <name>.3p=====`. Use `grep -n "=====PAGE: pthread_mutex" /home/claude/spec/posix14.txt` to find your function's page, then read that whole page's text (RATIONALE and APPLICATION USAGE sections often contain the exact gotcha a question should ask about).
- `/home/claude/spec/c11_n1570.txt`: the C11 draft standard. Use it for `<stdatomic.h>` (clause 7.17) and the memory model (clause 5.1.2.4) in module 7, and for anything else that is language-level rather than POSIX-level.
- If a function you need is not among the 60 fetched pages, either reason from a closely related one you do have (e.g. `pthread_mutex_lock` behavior generalizes from what you have on `pthread_mutex_init`) or hedge with a `VERIFY:` naming "POSIX.1-2017, <function>()" rather than inventing the exact wording.
- Where Linux differs from bare POSIX (a real and common interview angle: Linux mutexes, robust mutexes, `pthread_mutexattr_setrobust`, `sched_setaffinity`, real-time throttling), you may say so, clearly labeled "Linux:", but keep POSIX as the primary, cited reference.

## Real code requirement (this is what makes this page different from a generic OS/threads FAQ)
- Every question whose SHORT or DEEP promises "here is the code" must contain a real, complete-enough C snippet inside a ```c fenced block, and you must actually compile and run it before finalizing the question: `gcc -std=c11 -Wall -Wextra -pthread -o /tmp/test_mNN_X /tmp/test_mNN_X.c && /tmp/test_mNN_X`. For a race-condition demo, run it a few times (or in a loop) to actually observe the race before claiming it happens; say what you actually observed.
- Prefer complete, runnable examples with a `main()` that creates the threads/processes, joins them, and prints a result a reader can check.
- For a question demonstrating a bug (race, deadlock, lost wakeup), show the broken version's real behavior (or a description of what you observed running it, since a deadlock will hang -- describe how you confirmed it, e.g. "it hung; killed with Ctrl-C, jstack-equivalent was a backtrace showing both threads in pthread_mutex_lock"), then the fixed version, and confirm the fixed version actually runs correctly.
- Note the compile line only if it is load-bearing (e.g. needs `-pthread`, or `-latomic` on some platforms for stdatomic).

## File format (identical to the C Language page)
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
- Types (exact): `Concept`, `Numeric`, `Scenario`, `Debug`, `Cross-layer`, `Trap`. (`Cross-layer` here means "spans user code and kernel/OS behavior", e.g. a mutex call and what the scheduler does underneath; `Trap` means a classic concurrency gotcha such as a lost wakeup or a spurious wakeup.)
- `fig=` is optional and must be exactly one of the diagram keys assigned to your module. Use it once, on the question it illustrates best.
- Plain ASCII punctuation. No em dashes. No emojis. Avoid the words "genuinely", "honestly", "straightforward".

## Mix per module (18-22 questions)
Roughly: 2-3 Basic, 5-6 Intermediate, 6-7 Advanced, 4-5 Principal (this page skews slightly more advanced than the C Language page, matching an interviewer's expectation that concurrency questions come later and harder). Include real code wherever the topic is code-shaped (most of it). Include at least one Numeric (e.g. context-switch or lock-contention overhead reasoning with real or well-known reference numbers, clearly hedged as approximate), one Debug (a race, deadlock, or memory-ordering bug to find), and one Scenario or Trap.

A good Principal question asks the reader to design or debug a concurrent system end to end and states a concrete method (what to instrument, what tool to reach for, what invariant to check) plus a pitfall.

## Deliverable and report
When your file(s) pass `--check`, re-read once for factual slips and code that only "looks" right, then reply with a brief report (under 150 words): file(s) written, question counts, which code snippets you actually compiled and ran (by question id), any facts you were unsure of, and any suggested change to your assigned diagram.

## Module list for this page
1. Processes vs Threads & Process Memory Layout
2. Process Control: fork, exec, wait, signals
3. POSIX Threads: Creation, Joining & Attributes
4. Mutexes & Critical Sections
5. Condition Variables & Signaling
6. Semaphores, Read-Write Locks & Barriers
7. Memory Model, Atomics & Ordering
8. Deadlock, Livelock, Starvation & Priority Inversion
9. Classic Concurrency Problems
10. Thread-Safety Patterns & Lock-Free Basics
11. OS Scheduling & Real-Time Concurrency
12. Inter-Process Communication
13. Virtual Memory & mmap
14. Interrupts, ISRs & Embedded Concurrency
15. Debugging Concurrency & Principal-Level Design

(Full scope text for each is in `/home/claude/cadv/briefs.json`.)
