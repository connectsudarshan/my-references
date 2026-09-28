DEEP = {

426: D("`-O0` disables optimization (fast compiles, easy debugging); `-O1` enables basic optimizations; `-O2` enables nearly all optimizations that don't trade size for speed (the usual release level); `-O3` adds aggressive ones like more inlining and vectorization, which may increase code size.",
"""Related levels: `-Os` optimizes for size, `-Oz` (Clang) more so, `-Og` optimizes while keeping debuggability, and `-Ofast` enables `-O3` plus non-standard-conforming floating-point shortcuts (`-ffast-math`).

`-O3` isn't always faster than `-O2` (code bloat can hurt instruction caches); measure. Higher optimization also exposes undefined behaviour more often, so test release builds with sanitizers and warnings. Embedded firmware frequently uses `-Os` to fit flash.""",
"Using `-Ofast` for numeric validation code, which may break IEEE semantics (NaN checks optimized away, reassociation changing results).",
["What does `-Og` offer? => Optimizations that don't interfere with debugging, a middle ground for development builds.",
 "Why can `-O3` be slower? => Aggressive inlining and unrolling increase code size and instruction-cache misses."]),

427: D("`std::vector` stores elements contiguously, so iteration is cache-friendly and prefetchable, while `std::list` scatters nodes across the heap, causing cache misses, pointer chasing and per-node allocation; in practice vector wins even where list has better Big-O.",
"""A cache miss costs on the order of 100 cycles, far more than shifting a few elements. Bjarne Stroustrup's well-known benchmark shows vector outperforming list for insert-in-sorted-position workloads up to very large sizes, because finding the position (linear search) dominates and vector search is much faster.

List still wins for huge elements that are expensive to move, when iterators must stay stable, or for O(1) splicing. Otherwise default to vector.""",
"Choosing `std::list` for a work queue because \"insertion is O(1)\", then iterating it every cycle with poor cache behaviour; `std::deque` or a ring buffer is faster.",
["Why do asymptotic complexities mislead here? => They ignore constant factors like cache misses and allocation costs.",
 "When is `std::list` genuinely better? => Stable iterators are required, elements are huge or non-movable, or you need O(1) splicing."]),

428: D("Loop unrolling replicates the loop body several times per iteration, reducing loop-control overhead (increments, comparisons, branches) and exposing more instruction-level parallelism and vectorization opportunities.",
"""Compilers unroll automatically at `-O2`/`-O3` (and with `-funroll-loops` or `#pragma GCC unroll N`). Benefits are largest for small bodies with independent iterations.

Costs: bigger code (instruction-cache pressure), and diminishing or negative returns for large bodies. Manual unrolling in source is rarely needed with modern compilers and often makes code harder to read; prefer letting the compiler do it, and check assembly (Compiler Explorer) when it matters.""",
"Hand-unrolling loops in source \"for speed\" while the compiler already did it, making code harder to maintain with no gain.",
["How can you request unrolling for a specific loop? => `#pragma GCC unroll N` (GCC/Clang) or `#pragma unroll`.",
 "Why can unrolling help vectorization? => It exposes independent operations that can be packed into SIMD instructions."]),

429: D("Cache locality is how well a program's memory accesses reuse data already in fast CPU caches; spatial locality means accessing nearby addresses (the rest of a cache line), temporal locality means re-accessing the same data soon.",
"""Caches load whole lines (typically 64 bytes). Sequential array traversal uses every byte loaded (spatial) and triggers hardware prefetching; working repeatedly on a small data set keeps it in L1/L2 (temporal).

Practical techniques: contiguous containers, iterating in memory order (row-major for C++ 2D arrays), structure-of-arrays for hot fields, blocking/tiling large computations, and keeping hot data small (avoid padding and cold fields in hot structs).""",
"Iterating a row-major 2D array column by column, touching a new cache line on every access.",
["Why does loop order matter for 2D arrays? => C++ stores arrays row-major, so the inner loop should walk columns within a row.",
 "What is loop tiling (blocking)? => Processing data in blocks that fit in cache to maximize reuse before eviction."]),

430: D("Branch prediction is the CPU guessing the outcome of conditional branches to keep its pipeline full; a misprediction flushes speculative work, costing roughly 10-20 cycles on modern CPUs.",
"""Predictable branches (loop conditions, rarely taken error checks) cost almost nothing. Unpredictable ones (data-dependent comparisons on random data) can dominate: the classic example is summing values above a threshold, several times faster when the data is sorted.

Mitigations: branchless code (conditional moves, arithmetic tricks, `std::min`/`std::max`), sorting or partitioning data, lookup tables, and `[[likely]]`/`[[unlikely]]` (C++20) hints for layout. Profile with hardware counters (`perf stat -e branch-misses`).""",
"Adding `[[likely]]` everywhere without measurement; wrong hints can make performance worse.",
["How do you measure branch mispredictions? => Hardware performance counters, e.g. `perf stat -e branch-misses`.",
 "Why is processing sorted data sometimes much faster? => Branches on the data become predictable."]),

431: D("Profiling measures where a program spends time or resources (which functions, lines, cache misses) to find bottlenecks; benchmarking measures how fast a specific piece of code or system is under controlled conditions to compare alternatives or track regressions.",
"""Workflow: profile the real workload first (perf, VTune, Visual Studio profiler, Tracy, gperftools) to find hotspots; then benchmark candidate improvements precisely (Google Benchmark, Catch2 benchmarks, `hyperfine` for whole programs), keeping inputs realistic and controlling noise (CPU frequency, warmup, repetitions).

Micro-benchmarks can mislead: the compiler may optimize away unused results (use `benchmark::DoNotOptimize`), caches may be unrealistically warm, and gains may not matter end-to-end.""",
"Optimizing a function because a micro-benchmark shows it can be 3x faster, when the profiler shows it's 0.5% of total runtime.",
["Why use `DoNotOptimize` in Google Benchmark? => To prevent the compiler from eliminating computations whose results aren't used.",
 "Sampling vs instrumenting profilers? => Sampling periodically records the stack (low overhead); instrumentation records every call (precise but distorting)."]),

432: D("Premature optimization is optimizing code before knowing it's a bottleneck, usually at the cost of clarity and correctness; Knuth's quote continues that we should still not pass up opportunities in the critical 3%.",
"""Harm: complex, error-prone code in places that don't matter, time spent on micro-tuning instead of features or correctness, and optimizations that measurements would show are useless (or negative).

Not premature: choosing appropriate algorithms and data structures up front (O(n log n) vs O(n²)), avoiding needless copies (pass by `const&`), designing for data locality in known-hot paths, and setting performance budgets. The key is measurement-driven work.""",
"Replacing clear code with hand-written bit tricks in cold configuration-parsing code, making it unmaintainable for no measurable gain.",
["What isn't considered premature optimization? => Sensible algorithm and data-structure choices and avoiding obvious waste.",
 "How do you decide what to optimize? => Profile the real workload and focus on the measured hotspots."]),

433: D("Passing large objects by value copies them (possibly allocating and copying heap data), while passing by `const&` passes only an address; for large or heap-owning types, `const&` avoids that cost.",
"""Guidelines: pass cheap types (built-ins, small trivially copyable structs up to ~2-3 words, views like `std::string_view`/`std::span`) by value; pass larger or heap-owning types (`std::string`, `std::vector`, big structs) by `const&` when only reading.

Exception: \"sink\" parameters that will be stored: take by value and `std::move` into the member, so rvalue arguments are moved rather than copied. Passing by value can also help the optimizer by avoiding aliasing concerns for small types.""",
"Passing `std::vector<Sample>` by value to a function called per test iteration, copying megabytes each time.",
["When is pass-by-value better even for strings? => For sink parameters that are stored; callers can move temporaries in.",
 "Why pass `string_view` by value? => It's just a pointer and length; copying it is cheaper than an extra indirection."]),

434: D("Data-oriented design organizes code around the data and how it's transformed and accessed in memory, optimizing for cache use and bulk processing, whereas classic object-oriented design organizes code around objects encapsulating their own data and behaviour.",
"""OOP often yields arrays of pointers to heap objects with virtual methods, processed one object at a time: poor locality and branchy code. DOD groups data by access pattern (arrays of plain values, structure-of-arrays), processes entities in batches, and separates hot and cold data.

It's widely used in game engines (entity-component systems), simulations and high-throughput data processing. It complements OOP: interfaces at module boundaries, data-oriented internals in hot loops.""",
"Modelling millions of small entities as individually heap-allocated polymorphic objects in a hot update loop.",
["What is an entity-component system? => A design storing components in contiguous arrays by type and processing them in systems, instead of objects with virtual methods.",
 "What does hot/cold splitting mean? => Keeping frequently accessed fields together and moving rarely used fields elsewhere to reduce cache footprint."]),

435: D("Array-of-Structures stores complete records one after another (`struct P{float x,y,z;}; P ps[N];`); Structure-of-Arrays stores each field in its own array (`struct Ps{float x[N], y[N], z[N];};`).",
"""AoS is natural when you access whole records together (one particle at a time with all fields). SoA wins when loops touch only some fields across many records: memory traffic includes only the needed fields and the data is ideally laid out for SIMD (load 8 consecutive `x` values into one register).

Hybrid AoSoA (small fixed-size blocks of SoA) balances locality and SIMD. In measurement data (e.g. latency samples with many metadata fields), SoA lets analytics scan one column efficiently.""",
"Using AoS for a large dataset where the hot loop reads only one field, dragging all other fields through the cache.",
["Why is SoA SIMD-friendly? => Consecutive values of the same field are contiguous, so one vector load fetches several elements.",
 "When is AoS better? => When code usually accesses all fields of one record together."]),

436: D("SIMD executes one instruction on multiple data elements at once (e.g. 8 floats with AVX2, 16 with AVX-512, 4 with NEON); C++ code can use it through compiler auto-vectorization, intrinsics, SIMD libraries, or parallel algorithms.",
"""Options:

- **Auto-vectorization** at `-O2`/`-O3` for simple loops over contiguous data without aliasing or dependencies (check with `-fopt-info-vec` or Clang `-Rpass=loop-vectorize`).
- **Intrinsics** (`<immintrin.h>`, `arm_neon.h`): full control, not portable.
- **Libraries**: `std::experimental::simd` (standardized as `std::simd` in C++26), xsimd, Highway, Eigen.
- `std::execution::unseq` (C++20) and `par_unseq` allow vectorized algorithm execution.

Enablers: SoA layout, aligned data, `__restrict`, avoiding branches in loops, and target flags (`-march=...`).""",
"Expecting the compiler to vectorize a loop that calls a non-inlined function or has pointer-aliasing ambiguity; check the vectorization report.",
["How do you check whether a loop vectorized? => Compiler reports (`-fopt-info-vec`, `-Rpass=loop-vectorize`) or inspecting assembly.",
 "What does `std::execution::unseq` allow? => Vectorized execution of an algorithm on one thread (C++20)."]),

437: D("In hot loops, virtual calls prevent inlining and related optimizations, add an indirect branch that may mispredict when types vary, and usually come with heap-allocated, scattered objects that hurt cache locality.",
"""A single virtual call is cheap, but per-element dispatch in a loop over millions of objects adds up: no vectorization across the call, indirect branch misses when object types alternate, and pointer chasing through a `vector<Base*>`.

Mitigations: batch work per virtual call (process a whole buffer), group objects by concrete type (so the branch is predictable and loops can be specialized), `final` for devirtualization, templates/CRTP for static dispatch, or `std::variant` with contiguous storage.""",
"Calling a virtual `process(sample)` per sample in a multi-million-sample loop instead of `processBatch(span)` once per buffer.",
["Why does sorting objects by type help virtual-call performance? => Consecutive calls go to the same target, so the branch predictor succeeds.",
 "How does batching help? => It amortizes one virtual call over many elements and lets the implementation's inner loop be optimized."]),

438: D("False sharing happens when threads write to independent variables that share a cache line, causing the line to bounce between cores; you detect it with profilers that report cache-line contention and fix it by separating the data onto different lines.",
"""Symptoms: a multithreaded loop that scales badly (or gets slower with more threads) despite no locks or shared data. Detection: Linux `perf c2c` (shows contended lines and the code touching them), Intel VTune memory access analysis, or experimentally by padding structures and measuring.

Fixes: `alignas(std::hardware_destructive_interference_size)` for per-thread counters, per-thread accumulation merged at the end, and separating producer/consumer indices in queues.""",
"Assuming a contention problem must involve locks; with false sharing, adding padding fixes scaling without changing any logic.",
["Which Linux tool finds false sharing? => `perf c2c`.",
 "Why does performance get worse with more threads? => More cores fight over the same cache line, increasing coherence traffic."]),

439: D("\"Zero-cost\" exception handling means no runtime cost on the non-throwing path (no checks in normal execution), but it isn't free: throwing is expensive (heap allocation of the exception, table lookups, unwinding, often microseconds), binaries grow with unwind tables, and it can limit some optimizations.",
"""Costs: throw/catch may take thousands of cycles, involves dynamic memory and sometimes a global lock in older runtimes (`dl_iterate_phdr`), which can hurt heavily multithreaded code that throws frequently. Unwind tables add binary size, relevant for firmware.

Guidance: use exceptions for rare, genuinely exceptional errors; use error codes, `std::optional` or `std::expected` for expected failures in hot paths; measure if exceptions appear in profiles. Some projects use `-fno-exceptions` for size or determinism.""",
"Using exceptions to signal \"device not ready, retry\" in a polling loop that fails thousands of times per second.",
["What makes throwing expensive? => Allocating the exception object, searching unwind tables, and unwinding frames.",
 "What's a good alternative for frequent, expected failures? => `std::expected` or error codes."]),

440: D("Prefetching loads data into the cache before it's needed to hide memory latency; hardware prefetchers do this automatically for regular access patterns, and programmers can hint it with builtins like `__builtin_prefetch(addr)` (GCC/Clang) or `_mm_prefetch` (x86).",
"""Hardware prefetchers excel at sequential and strided access. Software prefetching helps for irregular but predictable patterns: traversing linked structures, hash-table probes, or gather operations, where you can compute an address a few iterations ahead.

It must be tuned: prefetching too late gives no benefit, too early may evict useful data, and extra instructions cost cycles. Often the better fix is to restructure data to be contiguous so hardware prefetching works. Measure with cache-miss counters before and after.""",
"Adding prefetch hints to a sequential array loop that the hardware prefetcher already handles, adding instructions with no benefit.",
["When does software prefetching help most? => Irregular but predictable access patterns like linked structures or hash probes.",
 "What's usually better than manual prefetching? => Restructuring data to be contiguous so hardware prefetchers work."]),
}
