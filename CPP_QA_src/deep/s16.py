DEEP = {

411: D("The preprocessor is the first translation phase: it processes directives (`#include`, `#define`, `#if`, `#pragma`), expands macros and removes comments, producing a single translation unit that the compiler proper then parses.",
"""It works on tokens, not C++ semantics: no types, scopes or namespaces. `#include` pastes file contents; `#if`/`#ifdef` select code for platforms or build configurations; predefined macros like `__FILE__`, `__LINE__`, `__cplusplus`, `_WIN32` give context.

View the output with `g++ -E file.cpp`. Heavy preprocessor use slows builds and hides code from tools; modern C++ replaces most uses with `constexpr`, templates, `if constexpr` and modules.""",
"Using `#ifdef` branches that are rarely compiled (e.g. for another platform), so they silently rot and fail when finally built. Build every configuration in CI.",
["How do you see preprocessed output? => `g++ -E` or `cl /P`.",
 "What does `__cplusplus` indicate? => The language standard version the compiler is using (e.g. 202002L for C++20)."]),

412: D("A header guard (`#ifndef X_H / #define X_H ... #endif`) or `#pragma once` ensures a header's contents are included only once per translation unit, preventing redefinition errors when the header is included through several paths.",
"""Without guards, including `a.h` and `b.h` that both include `common.h` defines everything in `common.h` twice (class redefinition errors). Guard macro names must be unique across the project (e.g. include path components).

`#pragma once` is non-standard but supported by all major compilers and avoids name clashes; it can misbehave in unusual setups (the same file reached through different paths or copies on network drives).""",
"Copy-pasting a header and forgetting to change the guard macro, so the second header silently becomes empty when both are included.",
["What's the risk of `#pragma once`? => Rare edge cases where the same file is seen under different paths or copies.",
 "Do guards prevent ODR violations across translation units? => No, only multiple inclusion within one translation unit."]),

413: D("`#include <file>` searches the system and configured include directories; `#include \"file\"` searches first relative to the including file's directory (and implementation-defined user paths), then falls back to the angle-bracket search.",
"""Convention: angle brackets for standard and third-party libraries (`<vector>`, `<fmt/format.h>`), quotes for your project's headers. Compiler flags add directories: `-I` for both forms, `-iquote` for quote-only, `-isystem` for system headers (which also suppresses warnings from them).

Include-order problems are best avoided by making every header self-contained (it compiles on its own) and including what you use.""",
"Using quotes for third-party headers that also exist with the same name locally, accidentally picking up the wrong file.",
["What does `-isystem` change? => Adds a directory treated as a system path, suppressing warnings from its headers.",
 "How do you ensure a header is self-contained? => Include it first in its own `.cpp` file (or compile it alone) so missing includes show up."]),

414: D("Static linking copies library code into the executable at build time; dynamic linking leaves references resolved at load or run time against shared libraries (`.so`, `.dll`, `.dylib`).",
"""Static: self-contained binary, no dependency problems at deployment, possible whole-program optimizations; but larger binaries, and every library fix requires relinking and redistributing.

Dynamic: smaller executables, shared memory pages between processes, libraries can be updated independently (security fixes); but \"DLL hell\" and ABI compatibility concerns, loader overhead, and deployment must ship the right versions.

Firmware and embedded tools usually link statically; desktop and server systems commonly use shared libraries for system components.""",
"Updating a shared library with an incompatible ABI (changed class layout) without rebuilding clients, causing crashes at runtime rather than link errors.",
["What is DLL hell? => Conflicts from applications requiring different, incompatible versions of the same shared library.",
 "How are shared library symbols resolved at runtime? => By the dynamic loader, at startup or lazily on first call (PLT/GOT on ELF)."]),

415: D("The linker combines object files and libraries into an executable or library, resolving symbol references to definitions, laying out sections and applying relocations; \"undefined reference\" means a used symbol had no definition in any linked input.",
"""Common causes of undefined references: a `.cpp` not compiled or linked, a missing library (`-lfoo`), wrong library order for static libraries (dependents must come before dependencies with GNU ld), a function declared but never defined, template definitions not visible, mismatched `extern \"C\"`, and C++ ABI mismatches (e.g. `std::__cxx11::string`).

\"Multiple definition\" errors come from defining non-inline functions or variables in headers. Tools: `nm -C`, `objdump`, `-Wl,--verbose`, and `ldd` for shared libraries.""",
"Listing static libraries in the wrong order on the GNU linker command line (`-lcore -lutils` when `core` needs `utils` is right; the reverse fails).",
["Why does library order matter with GNU ld? => It resolves symbols in one pass, only pulling objects from libraries to satisfy currently undefined symbols.",
 "How do you inspect which symbols an object defines? => `nm -C file.o` (demangled)."]),

416: D("A compile-time error is found while compiling one translation unit (syntax, types, name lookup, template instantiation); a linker error is found when combining translation units (missing or duplicate definitions, unresolved symbols).",
"""Compile errors point to a source line; link errors point to symbols, often mangled names, because the problem spans files: a declaration without a definition, a definition in more than one place, or a library not provided.

Recognizing the stage speeds up debugging: `undefined reference to 'Device::reset()'` means look for where `reset` should be defined and whether it's compiled and linked, not at the call site.""",
"Staring at the call site of a function for a linker error when the fix is adding the missing `.cpp` to the build.",
["How do you tell a linker error apart? => It mentions symbols and object files (\"undefined reference\", \"LNK2019\"), not a source line.",
 "Can templates cause linker errors? => Yes, when their definitions aren't visible and nothing instantiates them."]),

417: D("`extern \"C\"` gives functions C language linkage: no name mangling and the C calling convention, so C code (or any C ABI consumer) can call C++ functions and C++ can declare C functions.",
"""Common pattern for headers shared with C: `#ifdef __cplusplus extern \"C\" { #endif ... #ifdef __cplusplus } #endif`. Plugin and DLL interfaces often use `extern \"C\"` factory functions because the C ABI is stable across compilers.

Restrictions: `extern \"C\"` functions can't be overloaded, and exceptions must not escape into C callers.""",
"Letting a C++ exception propagate out of an `extern \"C\"` callback into C code, which is undefined behaviour and usually crashes.",
["Why can't `extern \"C\"` functions be overloaded? => Without mangling, overloads would have the same symbol name.",
 "Why do plugin APIs use `extern \"C\"`? => The C ABI is stable across compilers and versions, unlike C++ name mangling and class layouts."]),

418: D("A static library (`.a`, `.lib`) is an archive of object files copied into the executable at link time; a shared library (`.so`, `.dll`, `.dylib`) is a separate binary loaded at runtime and shared among processes.",
"""Static libraries: the linker pulls only needed object files; no runtime dependencies. Shared libraries: need symbol export control (`__declspec(dllexport)`, `-fvisibility=hidden` with attributes), position-independent code (`-fPIC`), versioning (sonames on Linux) and careful ABI management.

On Windows, a DLL comes with an import library (`.lib`) used at link time. `dlopen`/`LoadLibrary` load shared libraries explicitly for plugins.""",
"Building a shared library without controlling symbol visibility, exporting thousands of internal symbols and making the ABI surface (and load time) unnecessarily large.",
["What does `-fvisibility=hidden` do? => Hides symbols by default so only explicitly marked ones are exported.",
 "What is an import library on Windows? => A `.lib` containing stubs used to link against a DLL."]),

419: D("A name with internal linkage is visible only within its translation unit (`static` functions and variables at namespace scope, anything in an unnamed namespace, `const` namespace-scope variables by default); a name with external linkage can be referenced from other translation units.",
"""Functions and non-const global variables have external linkage by default. `inline` functions and variables have external linkage but may be defined in several units.

Use internal linkage for helpers that shouldn't be part of a file's interface: it prevents accidental ODR clashes with identically named helpers elsewhere, and lets the compiler optimize more (it knows all uses).""",
"Defining helper functions like `parseLine` with external linkage in two `.cpp` files, causing duplicate-symbol link errors or, worse, silent ODR violations for inline versions.",
["Do `const` globals have internal linkage? => Yes, at namespace scope in C++ (unless declared `extern` or `inline`).",
 "Why does internal linkage help optimization? => The compiler knows all uses, so it can inline, specialize or remove unused functions."]),

420: D("An unnamed namespace (`namespace { ... }`) gives everything inside it internal linkage, like `static`, but also works for types, templates and class definitions.",
"""`static` can't be applied to a class definition, so two `.cpp` files each defining `struct Helper` in the global namespace violate the ODR (possibly silently). Wrapping helpers in an unnamed namespace makes each unique to its file.

Modern style prefers unnamed namespaces in `.cpp` files for file-local code. Never put an unnamed namespace in a header: every including file gets its own copy, which bloats and can cause subtle ODR issues with inline functions referring to it.""",
"Putting an unnamed namespace in a header, creating a separate copy of its contents in every translation unit.",
["Can `static` give a class internal linkage? => No; use an unnamed namespace for types.",
 "Why avoid unnamed namespaces in headers? => Each translation unit gets distinct entities, duplicating code and risking ODR violations."]),

421: D("Include What You Use means each file should directly include the headers that declare everything it uses, and nothing more, rather than relying on transitive includes.",
"""Benefits: headers can be refactored without breaking unrelated files (if `a.h` stops including `<string>`, files relying on it transitively break), dependencies are explicit, and unnecessary includes that slow builds are removed.

Tools: the `include-what-you-use` tool (Clang-based), clangd's unused-include diagnostics, and clang-tidy `misc-include-cleaner`. Pair with forward declarations in headers to minimize dependencies.""",
"Code that compiles only because some unrelated header happened to include `<vector>`; an innocent cleanup elsewhere breaks the build.",
["What tools support IWYU? => The `include-what-you-use` tool, clangd, and clang-tidy's include cleaner.",
 "How does IWYU relate to build times? => Removing unnecessary includes reduces the code each translation unit must parse."]),

422: D("Link-Time Optimization (LTO) delays optimization until link time, when the compiler can see all translation units together, enabling cross-file inlining, dead-code elimination, devirtualization and constant propagation.",
"""Without LTO, each `.cpp` is optimized in isolation; a small function defined in another file can't be inlined. With `-flto` (GCC/Clang) or `/GL` + `/LTCG` (MSVC), object files contain intermediate representation and the linker invokes the optimizer on the whole program.

Benefits: typically a few percent to over 10% speed and smaller binaries. Costs: longer link times and memory (ThinLTO in Clang scales better), and harder debugging of some issues. It can also expose ODR violations that were previously hidden.""",
"Enabling LTO only in release builds and then discovering ODR violations or undefined behaviour that manifests only under cross-module inlining; test LTO builds too.",
["What is ThinLTO? => Clang's scalable LTO variant that does most work in parallel per module with summary-based cross-module optimization.",
 "What does LTO enable that per-file optimization can't? => Inlining and optimization across translation unit boundaries."]),

423: D("A forward declaration (`class Device;`) introduces a name without its definition, letting headers use pointers and references to it without including its full header; an `#include` brings in the complete definition and all of its own dependencies.",
"""Forward declarations reduce compile-time coupling: changing `device.h` then only recompiles files that actually include it. They also break include cycles.

You need the full definition to create objects, use members, know `sizeof`, inherit from the type, or hold it by value. Standard library types generally must not be forward-declared yourself (`namespace std` additions are undefined behaviour); use `<iosfwd>` for stream types.""",
"Forward-declaring standard library classes like `class std::string;` yourself, which is undefined behaviour; include the header (or `<iosfwd>` for streams).",
["When is a forward declaration not enough? => When you need the size, members, base class relationship or by-value use of the type.",
 "How do forward declarations help pImpl? => The header only needs `struct Impl;` and a `unique_ptr<Impl>`."]),

424: D("An ABI (Application Binary Interface) is the binary-level contract between compiled code: calling conventions, name mangling, object layout, vtable layout, exception handling and standard library type layouts; shared libraries must keep it stable for clients built against older versions to keep working.",
"""ABI-breaking changes include adding or reordering data members of exported classes, adding virtual functions, changing function signatures or inline function bodies relied upon by clients, and changing standard library versions with different layouts (e.g. libstdc++'s C++11 `std::string` ABI change).

Techniques for stability: pImpl, C interfaces for plugins, symbol versioning, and tools like `abi-compliance-checker`/`libabigail`. C++ mandates no single ABI; on Linux the Itanium C++ ABI is the de facto standard, MSVC has its own.""",
"Adding a data member to a class exported from a shared library in a minor release, crashing every client compiled against the old layout.",
["Is adding a new non-virtual member function an ABI break? => Usually not; adding data members or virtual functions usually is.",
 "Which ABI do GCC and Clang use on Linux? => The Itanium C++ ABI."]),

425: D("A precompiled header (PCH) is a compiler-specific binary snapshot of parsing a set of commonly included headers, reused by every translation unit instead of re-parsing those headers each time.",
"""Large, rarely changing headers (standard library, Boost, Windows headers, vendor SDKs) dominate compile time; putting them in a PCH can cut build times substantially. CMake supports it with `target_precompile_headers`.

Drawbacks: changing anything in the PCH rebuilds everything, over-large PCHs hide missing includes (files compile only because the PCH provides headers), and PCHs are compiler- and flag-specific. C++20 modules and header units are the standard successor.""",
"Putting frequently edited project headers into the PCH, so every edit triggers a full rebuild.",
["What belongs in a precompiled header? => Stable, heavily used external headers, not frequently changing project headers.",
 "What's the standardized successor to PCHs? => C++20 modules and header units."]),
}
