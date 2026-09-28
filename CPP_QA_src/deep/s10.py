DEEP = {

276: D("Exception handling is C++'s mechanism for reporting errors by throwing an object that transfers control to the nearest matching handler up the call stack, destroying local objects along the way.",
"""It separates error detection (deep in the code) from error handling (where there's enough context), and works with constructors and operators, which can't return error codes. With RAII, cleanup is automatic.

Modern implementations use table-based \"zero-cost\" exceptions: no runtime cost on the non-throwing path, but throwing is expensive (microseconds) and adds binary size for unwind tables. Hence: use exceptions for exceptional conditions, not normal control flow.

Some domains (hard real-time, some firmware, game engines) disable exceptions (`-fno-exceptions`) and use error codes, `std::expected` (C++23) or `std::optional`.""",
"Using exceptions for expected outcomes like \"key not found\" in a hot loop, paying the high throw cost repeatedly.",
["What does \"zero-cost exceptions\" mean? => No overhead when nothing is thrown; the cost is paid only when an exception is actually thrown.",
 "What's an alternative in exception-free codebases? => Error codes, `std::optional`, or `std::expected<T, E>` (C++23)."]),

277: D("The keywords are `try` (a block whose exceptions may be caught), `catch` (a handler for a type of exception), `throw` (raise or rethrow an exception) and `noexcept` (declare or test that a function doesn't throw).",
"""Related library pieces: `std::exception` and its hierarchy, `std::exception_ptr` with `std::current_exception` and `std::rethrow_exception` (moving exceptions across threads), `std::nested_exception` and `std::throw_with_nested` (adding context), and `std::terminate`.

The old dynamic exception specifications (`throw(A, B)`) were deprecated in C++11 and removed in C++17 (and `throw()` in C++20); use `noexcept` instead.""",
"Using `throw()` exception specifications from old code; they're removed in modern standards and should become `noexcept`.",
["How do you pass an exception from a worker thread to the main thread? => Capture it with `std::current_exception()` into a `std::exception_ptr`, then `std::rethrow_exception` (or use `std::future`).",
 "What replaced dynamic exception specifications? => `noexcept`."]),

278: D("If an exception propagates out of `main` (or a thread's function) without being caught, `std::terminate` is called, which by default calls `std::abort`; whether the stack is unwound first is implementation-defined.",
"""Consequences: destructors of local objects may not run, so files aren't flushed and resources aren't released cleanly. Many implementations don't unwind at all in this case, preserving the stack for a core dump, which helps debugging.

Good practice: catch exceptions at thread boundaries and at the top of `main`, log them with context, and return a failure exit code. A custom handler can be installed with `std::set_terminate` for last-resort logging.""",
"Letting exceptions escape from `std::thread` functions; the whole process terminates immediately.",
["What happens if an exception escapes a `std::thread` function? => `std::terminate` is called, ending the process.",
 "Why might unwinding not happen for uncaught exceptions? => It's implementation-defined; skipping it preserves the stack for debugging."]),

279: D("Yes: a `try` block can have several `catch` handlers; they're checked in order and the first one whose type matches the thrown exception handles it.",
"""Order from most specific to most general: `catch (const TimeoutError&)` before `catch (const DeviceError&)` before `catch (const std::exception&)` before `catch (...)`. A base-class handler placed first would catch derived exceptions and make later handlers unreachable (compilers warn).

Matching allows derived-to-base conversions and qualification adjustments, but not arithmetic or user-defined conversions (throwing `int` isn't caught by `catch (long)`).""",
"Putting `catch (const std::exception&)` before more specific handlers, so the specific ones never run.",
["Does `catch (long)` catch a thrown `int`? => No; handler matching doesn't apply arithmetic conversions.",
 "Which order should handlers appear in? => Most derived (specific) first, most general last."]),

280: D("`catch (...)` is a catch-all handler that matches any exception type, including types not derived from `std::exception`.",
"""Uses: last-resort handlers at thread and module boundaries (e.g. C API wrappers that must not let exceptions escape into C code), cleanup-then-rethrow (`catch (...) { rollback(); throw; }`), and translating unknown exceptions into error codes.

Inside `catch (...)` you don't know the type; `std::current_exception()` can capture it for later rethrow or logging by rethrowing inside nested try blocks.""",
"Swallowing all exceptions with an empty `catch (...) {}`, hiding bugs and leaving the program in an unknown state.",
["How do you learn what was caught in `catch (...)`? => Rethrow it inside a nested `try` with typed handlers, or capture with `std::current_exception()`.",
 "Why is `catch (...)` needed at C API boundaries? => Exceptions must not propagate through C frames; it converts them to error codes."]),

281: D("Exception propagation is the process of an exception moving from the `throw` point up through enclosing scopes and callers until a matching handler is found, destroying local objects in each exited scope.",
"""A function without a matching handler lets the exception pass through automatically, which is why intermediate layers usually don't need any exception-handling code: RAII cleans up, and only layers that can **do** something (retry, translate, report) catch.

Propagation through a `noexcept` function calls `std::terminate`. Across threads, exceptions don't propagate automatically; use `std::exception_ptr` or `std::future`.""",
"Catching and rethrowing at every layer \"just to log\", producing duplicated log lines for one error. Log once where it's handled, and add context with nested exceptions.",
["Do intermediate functions need try/catch to let exceptions pass? => No, propagation is automatic.",
 "What happens if an exception propagates through a `noexcept` function? => `std::terminate` is called."]),

282: D("Stack unwinding is the destruction of automatic objects in each scope an exception leaves, in reverse order of construction, while the runtime searches for a handler.",
"""Unwinding is what makes RAII exception-safe: lock guards unlock, files close, smart pointers free memory. It uses unwind tables generated by the compiler (DWARF CFI on Linux, SEH tables on Windows x64).

If a destructor throws during unwinding, `std::terminate` is called. Objects that were only partly constructed have only their completed subobjects destroyed.""",
"Throwing from a destructor that may run during unwinding, which terminates the program.",
["What mechanism tells the runtime how to unwind frames? => Compiler-generated unwind tables (e.g. DWARF CFI, Windows x64 SEH tables).",
 "Why must destructors not throw during unwinding? => Two active exceptions at once can't be handled, so `std::terminate` is called."]),

283: D("The standard exception hierarchy is rooted at `std::exception`, with major branches `std::logic_error` (programming errors like `invalid_argument`, `out_of_range`) and `std::runtime_error` (conditions detectable only at runtime like `system_error`, `overflow_error`), plus others like `std::bad_alloc` and `std::bad_cast`.",
"""`what()` returns a description. `std::system_error` carries a `std::error_code` for OS errors (with `errno` values), useful for file and device operations.

Your own exceptions should usually derive from `std::runtime_error` (or `logic_error`) so generic handlers catching `const std::exception&` still work, and carry structured data (device serial, command, status code) as members, not just a message.""",
"Throwing strings or ints (`throw \"failed\";`), which generic `std::exception` handlers can't catch and which carry no structure.",
["What's `std::system_error` for? => Reporting OS/system errors with a `std::error_code` and category.",
 "Why derive custom exceptions from `std::runtime_error`? => So existing `catch (const std::exception&)` handlers work and `what()` is available."]),

284: D("Catch by `const` reference to avoid slicing derived exceptions to the base type, avoid an extra copy, and keep polymorphic `what()` and dynamic type information.",
"""`catch (std::exception e)` copies and slices: a `TimeoutError` becomes a plain `std::exception`, losing its data and overridden `what()`. `catch (const std::exception& e)` binds to the original object.

Throw by value (`throw TimeoutError{...};`), catch by const reference. Catching by pointer requires the thrower to allocate and someone to delete, which is error-prone.""",
"`catch (std::runtime_error e)` in a handler and then rethrowing with `throw e;`, which throws the sliced copy instead of the original.",
["What's the difference between `throw;` and `throw e;` in a handler? => `throw;` rethrows the original object; `throw e;` throws a copy of `e`'s static type (sliced).",
 "Why not throw pointers? => Ownership of the allocated exception becomes unclear, leading to leaks."]),

285: D("Exception safety describes what a function guarantees if an exception occurs; the levels are no-throw, strong (commit or rollback), basic (valid state, no leaks) and none.",
"""- **No-throw** (`noexcept`): never fails; required for destructors, swaps, move operations used by containers.
- **Strong**: if an exception occurs, state is as before the call (transactional), e.g. `std::vector::push_back` when moves are `noexcept`.
- **Basic**: invariants hold and nothing leaks, but state may have changed; the minimum acceptable level.
- **No guarantee**: resources may leak or invariants break; avoid.

Techniques: RAII (basic for free), copy-and-swap and \"do the work on a copy then commit with a non-throwing swap\" (strong), and `noexcept` operations for commit steps.""",
"Updating members one by one where a later step can throw, leaving objects half-modified (breaking even the basic guarantee if invariants depend on consistency).",
["How do you achieve the strong guarantee? => Do all throwing work on a copy, then commit with non-throwing operations such as `swap`.",
 "Which guarantee does `std::vector::push_back` provide? => Strong, if the element's move constructor is `noexcept` (or it's copyable)."]),

286: D("`noexcept` declares that a function won't throw; if it does, `std::terminate` is called. The `noexcept(expr)` operator tests at compile time whether an expression is declared non-throwing.",
"""Benefits: optimizers can omit unwinding paths, and more importantly library code chooses faster strategies based on it: `std::vector` moves elements during reallocation only if the move constructor is `noexcept`.

Mark move constructors, move assignments, swaps, destructors (implicitly noexcept) and simple accessors `noexcept`. Conditional `noexcept(noexcept(T(std::declval<T&&>())))` propagates guarantees in generic code. Since C++17, `noexcept` is part of the function type.""",
"Omitting `noexcept` on a custom type's move constructor, making `std::vector<T>` copy every element on reallocation.",
["What happens if a `noexcept` function throws? => `std::terminate` is called; the exception doesn't propagate.",
 "Is `noexcept` part of the function type? => Yes, since C++17 (function pointers can be noexcept-qualified)."]),

287: D("Yes: inside a handler, a bare `throw;` rethrows the currently handled exception object unchanged, preserving its dynamic type.",
"""This is used when a handler performs partial cleanup or logging and lets higher layers handle the rest. Contrast `throw e;` which throws a copy of `e` with its static type (slicing derived exceptions).

To add context while preserving the original, use `std::throw_with_nested(ContextError(\"while reading SMART log\"))` and later `std::rethrow_if_nested` to walk the chain. `throw;` outside any handler calls `std::terminate`.""",
"Writing `catch (const std::exception& e) { log(e); throw e; }`, which loses the derived type of the original exception.",
["How do you add context to an exception without losing the original? => `std::throw_with_nested` inside the handler.",
 "What does `throw;` do outside a handler? => Calls `std::terminate`."]),

288: D("A function-try-block wraps a function's entire body, and for constructors also its member initializer list, in a `try` so exceptions thrown while initializing bases and members can be caught.",
"""Syntax: `Widget::Widget(int n) try : buf_(n), dev_(open()) { ... } catch (const std::exception& e) { log(e); }`.

For constructors, the handler **cannot** swallow the exception: when it ends, the exception is automatically rethrown, because the object failed to construct. It's useful for logging or translating the exception type. For ordinary functions it's rarely needed.""",
"Expecting a constructor's function-try-block handler to recover and produce a usable object; the exception is always rethrown.",
["Can a constructor's function-try-block suppress the exception? => No, it's rethrown when the handler completes.",
 "What can you catch with it that a normal try inside the body can't? => Exceptions from base-class and member initializers."]),

289: D("Throwing from a destructor is bad practice because destructors are implicitly `noexcept` (so a throw calls `std::terminate`), and even if allowed, a throw during stack unwinding terminates the program.",
"""Destructors are called in cleanup situations (unwinding, container destruction, `delete`) where there's no sensible place to handle a second error. Standard containers also require non-throwing destructors.

Pattern: provide an explicit, throwing `close()`/`commit()` for callers who need to know about errors, and have the destructor call it in a try/catch, logging failures.""",
"Flushing a buffered file in a destructor and letting an I/O exception escape, which terminates the program.",
["Are destructors noexcept by default? => Yes, since C++11 (unless a member or base has a potentially-throwing destructor).",
 "How do you report errors during cleanup? => Offer an explicit `close()` that can throw, and make the destructor best effort."]),

290: D("Exception-neutral code lets exceptions thrown by user-supplied code (element constructors, comparators, callbacks) propagate unchanged to the caller, while keeping its own objects in a valid state and leaking nothing.",
"""Generic libraries can't know what a user type will throw, so they neither catch-and-swallow nor translate exceptions; they rely on RAII and careful ordering to provide at least the basic guarantee (and often strong) while letting the exception through.

The STL is exception-neutral: if a `T` copy constructor throws inside `vector::insert`, the exception reaches the caller and the vector remains valid.""",
"A generic container that catches exceptions from element operations and returns `false`, hiding the real error type from callers.",
["Why shouldn't generic code catch and translate exceptions? => It can't know how to handle them, and translation loses information callers need.",
 "What guarantee must exception-neutral code still provide? => At least the basic guarantee: no leaks and valid invariants."]),

291: D("`std::terminate` is the C++ handler invoked when exception handling fails (uncaught exception, throw from `noexcept`, etc.); it calls the installed terminate handler, which by default calls `std::abort`. `std::abort` immediately ends the process abnormally without running destructors or `atexit` handlers.",
"""`std::set_terminate` lets you install a handler (for logging or crash reporting), which must not return. `std::abort` raises `SIGABRT`, typically producing a core dump.

Other exits: `std::exit` runs static destructors and `atexit` handlers but not local destructors; `std::quick_exit` runs only `at_quick_exit` handlers; `std::_Exit` does nothing.""",
"Calling `std::exit` from deep inside a function expecting RAII cleanup of locals; only static objects are destroyed.",
["What does `std::set_terminate` allow? => Installing a last-resort handler, e.g. to log the exception before aborting.",
 "Which exit function runs static destructors? => `std::exit` (not `abort`, `_Exit` or `quick_exit`)."]),

292: D("Containers can only offer the strong exception guarantee while moving elements if the move operations can't throw; so they use `std::move_if_noexcept`, moving `noexcept`-movable elements and copying otherwise.",
"""During `std::vector` reallocation, if a move constructor threw halfway, the source elements would already be moved-from and the original vector couldn't be restored. Copying preserves the originals, so the vector falls back to copying when moves might throw (and the type is copyable).

Therefore mark move constructors and move assignment `noexcept` whenever they genuinely can't throw (they usually just steal pointers). A `static_assert(std::is_nothrow_move_constructible_v<T>)` catches regressions.""",
"A class with a user-declared destructor and no move constructor, or a move constructor without `noexcept`: every vector growth copies all elements.",
["What does `std::move_if_noexcept` return? => An rvalue if the move constructor is noexcept (or the type isn't copyable), otherwise an lvalue so a copy is made.",
 "How do you verify your type moves without throwing? => `static_assert(std::is_nothrow_move_constructible_v<T>);`."]),

293: D("RAII is what makes exception safety practical: because destructors run during stack unwinding, every resource owned by an RAII object is released automatically on any exit path, including exceptions.",
"""Without RAII, each function would need try/catch blocks to release resources on every error path, which is error-prone and verbose. With RAII, the basic guarantee (no leaks) comes almost for free, and higher-level guarantees are built on it.

Examples: `std::lock_guard` releases a mutex when an exception propagates; `std::unique_ptr` frees memory; a transaction RAII object rolls back in its destructor unless `commit()` was called (\"scope guard\" pattern).""",
"Acquiring a resource and storing it in a raw variable, then calling functions that may throw before the resource is wrapped; the resource leaks on the exception path.",
["What is a scope guard? => An RAII object that runs a cleanup action (like rollback) on scope exit unless dismissed.",
 "Which guarantee does RAII give almost automatically? => The basic guarantee: no resource leaks."]),

294: D("Throwing exceptions across shared-library boundaries works reliably only if both sides use a compatible compiler, C++ runtime and ABI, with RTTI for the exception type visible to both; across different compilers or runtimes, or through C interfaces, it's unsafe.",
"""Risks: the catching side may not recognize the type (type_info comparison fails if the class isn't exported consistently or has duplicate RTTI), different runtimes may use incompatible unwinding or allocation, and C code between the frames has no unwind information.

Guidelines: don't let exceptions cross module boundaries with a C ABI (plugins, `extern \"C\"` APIs); catch at the boundary and convert to error codes. Within one product built with one toolchain, exporting exception classes properly (visibility attributes, `__declspec(dllexport)`) makes it work.""",
"Throwing a C++ exception out of a callback called by a C library; unwinding through C frames is undefined and typically crashes.",
["Why must exception classes be exported from shared libraries? => So both modules agree on the type's RTTI and `catch` can match it.",
 "What's the safe design for plugin APIs? => A C ABI returning error codes, with exceptions caught at the boundary."]),

295: D("`std::uncaught_exceptions()` (C++17) returns how many exceptions are currently in flight (thrown but not yet caught) in the current thread, allowing destructors to tell whether they're running because of stack unwinding.",
"""Main use: scope guards and transaction objects that should commit on normal exit but roll back on exceptional exit. Record the count in the constructor; in the destructor, if the count increased, an exception is propagating.

It replaced the deprecated (and removed in C++20) `std::uncaught_exception()` (singular, returning bool), which gave wrong answers when destructors ran during unwinding of an unrelated exception.""",
"Using the old `std::uncaught_exception()` (bool) in code that may run during another exception's unwinding; it misreports and was removed in C++20.",
["How does a scope guard use `uncaught_exceptions`? => It stores the count at construction and compares it in the destructor to decide commit vs rollback.",
 "Why was the singular version removed? => It couldn't distinguish \"this scope is failing\" from \"some unrelated exception is unwinding\"."]),
}
