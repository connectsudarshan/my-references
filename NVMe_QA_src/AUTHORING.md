# Authoring guide for the NVMe Q&A Study Guide

## Who this is for
Sudarshan K: 12+ years in storage/firmware, NVMe/ZNS/PCIe/SSD firmware validation. He is preparing for a **Principal SSD Firmware Validation Engineer** interview (Micron, Bengaluru). This page teaches NVMe from Basic to Principal, weighted to **SSD firmware validation and debug** (test design, fault injection, reading traces and logs, root-causing failures, automation). He already knows a lot, so Basic questions should still be crisp and Principal questions should be genuinely hard. Accuracy matters more than volume: a wrong number, register name or status code in an interview is costly.

## Files
- Topic directory: `/home/claude/nvme/` (content goes in `/home/claude/nvme/content/mNN.txt`, NN = two-digit module number).
- You write ONLY your own module file. Do not edit any other file (other authors write other modules in parallel; shell, build script, modules.json and diagram code belong to the lead).
- Style exemplars to read first (they belong to the finished PCIe page; match their voice, depth and formatting exactly): `/home/claude/pcie/content/m06.txt` and `/home/claude/pcie/content/m04.txt`. Skim `/home/claude/pcie/content/m16.txt` (NVMe over PCIe) and `/home/claude/pcie/content/m17.txt` (debug) too.
- The PCIe page already covers PCIe in depth (18 modules). Run `grep -h "^Q:" /home/claude/pcie/content/m*.txt` and read it. Do not re-teach PCIe: refer back ("see the PCIe page, Data Link module") and cover only the NVMe/ZNS side or the interaction.
- Read `/home/claude/nvme/modules.json` and the list of modules below so you know what other authors cover. Do not overlap: when a topic straddles, cover the aspect that belongs to your module and name the other module.
- Validate your file with: `python3 /home/claude/study/build.py /home/claude/nvme --check /home/claude/nvme/content/mNN.txt`. Fix every ERROR. Do NOT run a full build.

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
1. **NVMe Fundamentals & Architecture**: Why NVMe replaced AHCI/SATA, the host, NVM subsystem, controller and namespace model, the NVMe specification family, and a first tour of queues and commands.
2. **Controller Registers & Initialization**: BAR0 register map, CAP/VS/CC/CSTS, the enable and ready handshake, admin queue setup, shutdown and reset, NSSR, CMB and PMR.
3. **Queues, Doorbells & Command Flow**: Submission and completion queues as rings, doorbells, phase tags, command identifiers, the 64-byte SQE and 16-byte CQE, arbitration and the life of one command.
4. **PRPs, SGLs & Data Transfer**: How the controller finds host memory: PRP entries and lists, chaining, alignment rules, SGL descriptor types, MDTS and the numbers you should derive by hand.
5. **Admin Command Set**: Identify (CNS values), Create/Delete I/O queues, Get/Set Features, Get Log Page, Abort, Async Event Request, firmware commands and the admin queue's role.
6. **NVM Command Set (I/O Commands)**: Read, Write, Flush, Compare, Write Zeroes, Dataset Management, Verify, Copy, Write Uncorrectable and the semantics that matter for data integrity.
7. **Namespaces & Identify Structures**: NSIDs, private and shared namespaces, namespace management and attachment, NSZE/NCAP/NUSE, LBA formats, identifiers and thin provisioning.
8. **End-to-End Data Protection & Metadata**: LBA metadata, extended vs separate metadata, Protection Information types 1 to 3, guard/app/reference tags, PRACT and PRCHK, and how validators exploit them.
9. **Status Codes, Errors & Recovery**: The CQE status field, generic and command-specific codes, error and timeout handling, abort, controller reset hierarchy, and what a robust host or validator does on failure.
10. **Interrupts, Coalescing & Polling**: How completions reach the host: MSI-X vector mapping to CQs, vector 0, interrupt coalescing, INTMS/INTMC, masking, and polled I/O.
11. **Power Management & Thermal**: NVMe power states, APST, non-operational states, thermal throttling and thresholds, how they interact with PCIe ASPM/L1 substates and D-states, and how to validate them.
12. **Security & Data Sanitization**: Security Send/Receive and TCG, Format NVM and Sanitize semantics, crypto erase, write protection, boot partitions, RPMB, and how to validate erase guarantees.
13. **Reliability, Logs & Telemetry**: SMART/Health, Error, Firmware Slot and Persistent Event logs, telemetry, endurance reporting, self-test, and turning log fields into numbers.
14. **Multi-Controller, Multipath & Virtualization**: Multi-controller NVM subsystems, dual-port SSDs, namespace sharing, ANA, reservations, SR-IOV virtualization support and NVMe-MI basics.
15. **NVMe over Fabrics**: Fabrics architecture: capsules, transports (RDMA, TCP, FC), Connect and discovery, queues over fabrics, keep-alive and multipath, and what changes versus PCIe.
16. **Advanced NVMe Features**: HMB, CMB/PMR, Streams and Directives, Flexible Data Placement, Key Value and other command sets, Copy, Computational Storage and the 2.x command-set architecture.
17. **SSD Internals Behind NVMe**: What the firmware does between a doorbell and NAND: FTL mapping, garbage collection, write amplification, over-provisioning, wear leveling, ECC, power-loss protection and how each shows up at the NVMe interface.
18. **Performance & QoS**: IOPS, bandwidth and latency relationships, queue depth and Little's law, steady state and preconditioning, tail latency, fio design, and where PCIe/firmware/NAND each cost time.
19. **Host Software Stack & Tools**: Linux and Windows NVMe drivers, blk-mq and multipath, nvme-cli, sysfs, tracing, SPDK, io_uring passthrough and the tools a validation engineer scripts against.
20. **Validation Methodology & Test Design**: How to design a principal-level validation strategy: protocol conformance, negative and stress tests, fault injection, power-loss testing, data integrity, automation and metrics.
21. **Debug & Triage Scenarios**: Principal-level end-to-end scenarios: controller fatal status, timeouts, hangs, data miscompares, performance regressions, link and reset problems, and how to structure the investigation.
