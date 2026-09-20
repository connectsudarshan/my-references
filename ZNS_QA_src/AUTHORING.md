# Authoring guide for the ZNS Q&A Study Guide

## Who this is for
Sudarshan K: 12+ years in storage/firmware, NVMe/ZNS/PCIe/SSD firmware validation. He is preparing for a **Principal SSD Firmware Validation Engineer** interview (Micron, Bengaluru). This page teaches ZNS from Basic to Principal, weighted to **SSD firmware validation and debug** (test design, fault injection, reading traces and logs, root-causing failures, automation). He already knows a lot, so Basic questions should still be crisp and Principal questions should be genuinely hard. Accuracy matters more than volume: a wrong number, register name or status code in an interview is costly.

## Files
- Topic directory: `/home/claude/zns/` (content goes in `/home/claude/zns/content/mNN.txt`, NN = two-digit module number).
- You write ONLY your own module file. Do not edit any other file (other authors write other modules in parallel; shell, build script, modules.json and diagram code belong to the lead).
- Style exemplars to read first (they belong to the finished PCIe page; match their voice, depth and formatting exactly): `/home/claude/pcie/content/m06.txt` and `/home/claude/pcie/content/m04.txt`. Skim `/home/claude/pcie/content/m16.txt` (NVMe over PCIe) and `/home/claude/pcie/content/m17.txt` (debug) too.
- The PCIe page already covers PCIe in depth (18 modules). Run `grep -h "^Q:" /home/claude/pcie/content/m*.txt` and read it. Do not re-teach PCIe: refer back ("see the PCIe page, Data Link module") and cover only the NVMe/ZNS side or the interaction.
- Read `/home/claude/zns/modules.json` and the list of modules below so you know what other authors cover. Do not overlap: when a topic straddles, cover the aspect that belongs to your module and name the other module.
- Validate your file with: `python3 /home/claude/study/build.py /home/claude/zns --check /home/claude/zns/content/mNN.txt`. Fix every ERROR. Do NOT run a full build.

## File format (one block per question, ids `N.01`, `N.02`, ... consecutive, no gaps)
```
# Module N: Title

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
- `fig=` is optional and must be exactly one of the diagram keys assigned to your module (the lead draws them after you finish). Use each assigned key on exactly one question, the one it illustrates best. If your module has no assigned key, omit `fig=`.
- Markdown tables must start at column 0 with `|`. Never put a table inside a bullet.
- A line starting with `- ` or `1. ` inside DEEP is a list item; keep lists short (3-7 items). Keep DEEP to roughly 120-260 words per question, more only for Scenario/Numeric/Debug questions.
- `FOLLOW:` items each contain exactly one `=>` separator.
- Lines beginning with `Q:`, `SHORT:`, `DEEP:`, `FOLLOW:`, `PITFALL:`, `VERIFY:` at column 0 are keywords, so never start an ordinary DEEP line with one of those words followed by a colon.
- Plain ASCII punctuation preferred. No em dashes. No emojis. Avoid the words "genuinely", "honestly", "straightforward". The `#` heading line uses a colon, not an em dash.

## Mix per module (14-17 questions)
Roughly: 3 Basic, 5 Intermediate, 5 Advanced, 3-4 Principal. Types: mostly Concept, but every module must include at least one each of Numeric (a worked calculation), Debug (reading registers/logs/traces/CQEs and reasoning), and Scenario (a triage or design situation), plus a Trap where natural, and Cross-layer where behavior spans layers (NVMe and PCIe, firmware and NAND, host and device). Weight examples toward SSD firmware validation and debug (nvme-cli, fio, dmesg, log pages, analyzers, fault injection, power loss, automation). Where a module's nature makes a required type unnatural (e.g. a pure concept module), include the closest realistic variant rather than forcing a fake one.

A good Principal question asks "how would you design / automate / root-cause / quantify X", and its answer contains a method, evidence to collect, decision criteria and a pitfall. A good Numeric question shows the arithmetic step by step and states assumptions.

## Accuracy rules (important)
- Only state facts you are confident about. For anything you are unsure of, either check it (WebSearch/WebFetch; load via ToolSearch if deferred) or hedge the wording and add a `VERIFY:` line naming exactly what to check in the NVMe Base Specification / NVMe Zoned Namespace Command Set Specification / NVM Command Set Specification / PCIe Base Specification. Put spec-sensitive numbers (opcodes, feature IDs, log page IDs, register offsets, bit positions, status code values, field widths) under VERIFY unless certain.
- Useful public sources when you check: nvmexpress.org (specs may not be fetchable), the Linux kernel source and documentation (kernel.org, include/linux/nvme.h is a very reliable source for NVMe opcodes, status codes, structures and field layouts), nvme-cli documentation and source (github.com/linux-nvme/nvme-cli), SPDK docs and headers (spdk/nvme_spec.h is reliable), zonedstorage.io (ZNS and Linux zoned storage), OCP Datacenter NVMe SSD specification, SNIA PTS.
- Re-derive every calculation with a quick python one-liner before writing it down. Show assumptions.
- NVMe spec generations: NVMe 1.x monolithic Base spec; NVMe 2.0 (2021) restructured into Base, command set specs (NVM, ZNS, KV), transport specs (PCIe, RDMA, TCP) and NVMe-MI. Features added after 2.0 (Flexible Data Placement, some log pages, newer sanitize and security features) must carry revision wording and a VERIFY line. Do not claim exact revision numbers you are unsure of.
- Do not invent register field names, log page fields or status names. If unsure of the exact name, describe the field in words and add VERIFY.
- Keep each question self-contained: a reader should be able to answer from SHORT and be corrected by DEEP.

## Deliverable and report
When your file passes `--check`, re-read it once for factual slips, then reply with a brief report (under 150 words): file written, question counts, any facts you were unsure of, and any suggested change to your assigned diagram (only if the brief's diagram description is misleading).


## Module list for this page
1. **Why Zoned Storage**: The problem with conventional SSDs (write amplification, over-provisioning, tail latency), the zoned model, SMR heritage, host-managed vs device-managed, and what ZNS trades away.
2. **ZNS Architecture & Command Set Basics**: Where ZNS sits in the NVMe 2.x command-set architecture: Command Set Identifier, the Zoned Namespace Command Set, Identify structures, and how the LBA space is divided.
3. **Zones, States & the Write Pointer**: Zone types, the write pointer, zone descriptor contents, the state machine (Empty, Open, Closed, Full, Read Only, Offline) and every transition that matters.
4. **Zone Management Commands**: Zone Management Send actions (Open, Close, Finish, Reset, Offline, Set Zone Descriptor Extension, Flush) and Zone Management Receive (Report Zones, filters), including Select All semantics.
5. **Zone Append**: Zone Append semantics: device-chosen placement, returned LBA, ZASL, concurrency and ordering, how it removes the single-writer-per-zone constraint, and its interaction with PI and metadata.
6. **Zone Resources: Active, Open & Excursions**: MAR and MOR limits, implicit open eviction, zone active excursions, zone information changed events, and how the host must budget resources.
7. **Errors, Status Codes & Read Rules**: Zone-specific status codes, read-above-write-pointer behaviour, boundary errors, read-only/offline zones, and how the host and a validator should react.
8. **ZNS Firmware & FTL Design**: How a ZNS controller maps zones to NAND, buffers writes, handles zone reset, finish, power loss and wear, and how much FTL complexity remains.
9. **Host Software Stack for Zoned Storage**: Linux zoned block layer, zone write plugging, filesystems and databases that use zones, libzbd, nvme-cli zns support, fio zbd mode, SPDK and xNVMe.
10. **ZNS Validation & Test Design**: Designing a ZNS test plan: state-machine coverage, boundary and resource tests, concurrency with Zone Append, power-loss and reset testing, data integrity and tooling.
11. **ZRWA, Simple Copy & Related Features**: Zone Random Write Area, explicit vs implicit flush, Simple Copy, zone descriptor extensions, and how ZNS compares with FDP and conventional namespaces.
12. **ZNS Scenarios & System Design**: Principal-level design and debug scenarios: host GC design, capacity planning, migration from conventional, failure recovery, and full-stack triage of zoned workloads.

## Relationship to the NVMe page
A separate NVMe page is being written in parallel (modules: NVMe Fundamentals & Architecture, Controller Registers & Initialization, Queues, Doorbells & Command Flow, PRPs, SGLs & Data Transfer, Admin Command Set, NVM Command Set (I/O Commands), Namespaces & Identify Structures, End-to-End Data Protection & Metadata, Status Codes, Errors & Recovery, Interrupts, Coalescing & Polling, Power Management & Thermal, Security & Data Sanitization, Reliability, Logs & Telemetry, Multi-Controller, Multipath & Virtualization, NVMe over Fabrics, Advanced NVMe Features, SSD Internals Behind NVMe, Performance & QoS, Host Software Stack & Tools, Validation Methodology & Test Design, Debug & Triage Scenarios). The ZNS page assumes NVMe basics (queues, PRPs, admin commands, status field, namespaces); refer to it briefly ("see the NVMe page") instead of re-teaching, and focus on what is specific to zones.
