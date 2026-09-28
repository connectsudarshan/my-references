DEEP = {

296: D("C++11 introduced `<thread>` for `std::thread`, together with `<mutex>`, `<condition_variable>`, `<atomic>` and `<future>`, and a formal memory model for multithreaded programs.",
"""Before C++11, threading relied on platform APIs (pthreads, Win32) and the language had no memory model, so compiler optimizations could break seemingly correct code.

Later additions: `<shared_mutex>` (C++14/17), `std::jthread` and `std::stop_token`, `<semaphore>`, `<latch>`, `<barrier>` and atomic `wait`/`notify` (C++20), and parallel algorithms with execution policies (C++17). C++26 adds `std::execution` (senders/receivers).""",
"Mixing raw pthread calls with `std::thread` objects on the same threads without understanding lifetime rules, e.g. detaching via pthread APIs.",
["What did the C++11 memory model add? => A definition of data races and happens-before, so correct multithreaded code has defined behaviour on every platform.",
 "Which synchronization primitives did C++20 add? => Semaphores, latches, barriers, `jthread`/stop tokens and atomic wait/notify."]),

297: D("You create a thread by constructing a `std::thread` (or C++20 `std::jthread`) with a callable and its arguments; the thread starts running immediately.",
"""Example: `std::thread t(runTest, deviceId, std::ref(results));`. Arguments are **copied** (decay-copied) into the thread's storage, so references need `std::ref`, and passing pointers to locals requires the locals to outlive the thread.

Every `std::thread` must be joined or detached before its destructor runs, or `std::terminate` is called; `std::jthread` joins automatically. For task-based parallelism, prefer thread pools or `std::async` over raw threads per task.""",
"Passing a local variable to a thread by reference (via `std::ref` or a lambda capture) and returning from the function before the thread finishes, leaving a dangling reference.",
["Why do references need `std::ref` when passed to `std::thread`? => Arguments are copied into internal storage; `std::ref` wraps a reference so the thread receives the original.",
 "What happens if a joinable `std::thread` is destroyed? => `std::terminate` is called."]),

298: D("`join()` blocks until the thread finishes; `detach()` lets the thread run independently, and its resources are released automatically when it ends.",
"""A joinable thread must be joined or detached before destruction. Joining is the default choice: it ensures the thread finishes before the objects it uses are destroyed and lets you observe completion.

Detached threads are risky: they may still run while static objects are destroyed at program exit, and you can't wait for them or know when they finish. Use them only for truly independent work with no references to shorter-lived data. `std::jthread` avoids the choice by joining in its destructor and supporting cooperative cancellation.""",
"Detaching a worker thread that uses a logger or other global, which is destroyed at program exit while the thread still writes to it.",
["Can you join a thread twice? => No; after `join()` the thread isn't joinable, and joining again throws `std::system_error`.",
 "Why is `std::jthread` safer? => It joins automatically in its destructor and supports stop requests."]),

299: D("A race condition is a bug where the program's result depends on the relative timing of threads (or events), e.g. two threads doing check-then-act or read-modify-write on shared state without proper synchronization.",
"""Examples: two threads incrementing a counter (lost updates), checking `if (!initialized) initialize();` concurrently (double init), or a test harness reading a device status while another thread changes it.

Race conditions can exist even without data races (e.g. two atomic operations that must be done together). Fixes: make compound operations atomic under one lock, use atomic read-modify-write (`fetch_add`, compare-exchange), or restructure so data has a single owner (message passing).""",
"Replacing a mutex with separate atomics for two related values; each access is atomic, but the pair can still be observed in an inconsistent state.",
["Can a program with no data races still have race conditions? => Yes; atomic operations can still interleave in ways that break higher-level invariants.",
 "How do you make check-then-act safe? => Perform the check and the action under the same lock, or use a single atomic compare-exchange."]),

300: D("A mutex (mutual exclusion) is a synchronization object that only one thread can hold at a time; code between `lock()` and `unlock()` (the critical section) runs exclusively, and unlocking makes changes visible to the next locker.",
"""Types: `std::mutex`, `std::recursive_mutex` (same thread can lock again), `std::timed_mutex`, and `std::shared_mutex` (many readers or one writer). Always lock through RAII (`std::lock_guard`, `std::unique_lock`, `std::scoped_lock`).

Keep critical sections short, don't call unknown code (callbacks, logging) while holding locks, and document which data each mutex protects. Contended mutexes can put threads to sleep, so for tiny operations atomics may be cheaper.""",
"Protecting data with a mutex in one function but reading it without the mutex elsewhere \"because it's only a read\"; unsynchronized reads concurrent with writes are data races.",
["When is `std::shared_mutex` appropriate? => Read-mostly data where many readers can proceed concurrently and writes are rare.",
 "Why avoid calling callbacks while holding a lock? => The callback might take other locks (deadlock risk) or block for a long time."]),

301: D("A deadlock is a state where threads wait for each other forever, typically because each holds a lock the other needs; common causes are inconsistent lock ordering, holding a lock while waiting on another resource, and self-deadlock on non-recursive mutexes.",
"""The four Coffman conditions (mutual exclusion, hold and wait, no preemption, circular wait) must all hold; breaking any one prevents deadlock.

Practical prevention: a global lock ordering, `std::scoped_lock(m1, m2)` (C++17) which locks multiple mutexes with a deadlock-avoidance algorithm, not holding locks while calling external code or blocking I/O, timeouts with `try_lock_for`, and preferring message passing over shared locks.

Diagnosis: dump all thread stacks (gdb `thread apply all bt`, Visual Studio parallel stacks) and look for threads blocked in `lock`.""",
"Two functions locking `deviceMutex` then `resultsMutex` in one place and the reverse in another; under load they eventually deadlock.",
["How does `std::scoped_lock` prevent deadlock? => It locks several mutexes together using a deadlock-avoidance algorithm (like `std::lock`).",
 "How do you find a deadlock in a hung process? => Dump every thread's stack and look for threads waiting on locks held by each other."]),

302: D("`std::lock_guard` is an RAII wrapper that locks a mutex in its constructor and unlocks it in its destructor, guaranteeing the unlock on every exit path including exceptions.",
"""Manual `lock()`/`unlock()` fails when a function returns early or throws between them, leaving the mutex locked and deadlocking every other thread.

`lock_guard` is minimal (no unlock-before-scope-end, no deferred locking). C++17's `std::scoped_lock` generalizes it to multiple mutexes and is the recommended default; `std::unique_lock` adds flexibility when needed.""",
"Writing `std::lock_guard<std::mutex>(m);` without a variable name: it creates a temporary that unlocks immediately at the end of the statement.",
["What's wrong with `std::lock_guard<std::mutex>(m);`? => It's an unnamed temporary destroyed at the end of the statement, so nothing is protected.",
 "`lock_guard` vs `scoped_lock`? => `scoped_lock` (C++17) can lock several mutexes deadlock-free and is otherwise equivalent."]),

303: D("`std::unique_lock` is a movable RAII lock that supports deferred locking, try-locking, timed locking, manual unlock/relock and ownership transfer; `std::lock_guard` only locks at construction and unlocks at destruction.",
"""`unique_lock` is required for `std::condition_variable::wait` (which must unlock and relock the mutex internally), for locking later (`std::defer_lock`), for timed attempts (`try_lock_for`), and for returning a lock from a function.

The flexibility costs a small overhead (it tracks whether it owns the lock). Use `lock_guard`/`scoped_lock` by default and `unique_lock` when you need its features.""",
"Using `unique_lock` everywhere by default; it's slightly heavier and its flexibility (manual unlock) makes lock scope harder to read.",
["Why does `condition_variable::wait` need `unique_lock`? => It must unlock the mutex while waiting and relock it before returning.",
 "What does `std::defer_lock` do? => Creates the lock object without locking, so you can lock later (e.g. with `std::lock` on several locks)."]),

304: D("A condition variable lets threads wait efficiently until another thread signals that some condition on shared data may have become true, avoiding busy-waiting.",
"""Pattern: the waiter locks a mutex and calls `cv.wait(lock, [&]{ return !queue.empty(); });`; the producer modifies the data under the same mutex and calls `cv.notify_one()` or `notify_all()`.

Always wait with a **predicate** (handles spurious wakeups and missed notifications), change the shared state under the mutex, and use `notify_one` when one waiter suffices. For shutdown, set a stop flag under the lock and `notify_all`. C++20 adds `std::condition_variable_any::wait` with `std::stop_token`.""",
"Notifying without changing the shared state under the mutex, or waiting without a predicate, which leads to lost wakeups and threads sleeping forever.",
["What is a lost wakeup? => A notification sent before the waiter starts waiting; without a predicate check the waiter sleeps forever.",
 "`notify_one` vs `notify_all`? => `notify_one` wakes one waiter (e.g. one new work item); `notify_all` wakes all (e.g. shutdown)."]),

305: D("`std::atomic<T>` provides indivisible operations (load, store, exchange, fetch_add, compare-exchange) on a single variable without data races, often implemented with lock-free CPU instructions.",
"""For simple shared counters, flags and pointers, atomics avoid mutex overhead and can't deadlock. `std::atomic<int>::fetch_add` compiles to a single `lock xadd` on x86.

Limits: atomicity applies to single operations on one variable; invariants involving several variables still need a mutex. `is_lock_free()` tells whether a given atomic uses a hidden lock (e.g. large structs). Default memory ordering is sequentially consistent; weaker orderings are for experts.""",
"Using `std::atomic<int> x; x = x + 1;` expecting an atomic increment; it's an atomic load followed by an atomic store, so updates can be lost. Use `++x` or `fetch_add`.",
["Is `x = x + 1` atomic for `std::atomic<int> x`? => No, it's a separate load and store; `x++` or `fetch_add(1)` is atomic.",
 "When would an atomic not be lock-free? => For types too large for the CPU's atomic instructions; check `is_lock_free()`."]),

306: D("`std::async` runs a callable (possibly on another thread) and returns a `std::future<T>` through which you later obtain the result with `get()`, which also rethrows any exception the task threw.",
"""It's the simplest way to run a task and get its result: `auto f = std::async(std::launch::async, computeCrc, block); ... auto crc = f.get();`.

Gotcha: the future returned by `std::async` **blocks in its destructor** until the task finishes, so `std::async(...)` without storing the future runs synchronously. Other tools: `std::promise` (set a value from any thread), `std::packaged_task` (wrap a callable for a thread pool), and `std::shared_future` for multiple readers.""",
"Calling `std::async(std::launch::async, task);` without keeping the returned future; the temporary's destructor waits, so tasks run one after another.",
["Why does discarding `std::async`'s future serialize work? => That future's destructor blocks until the task completes.",
 "How do exceptions travel through a future? => The task's exception is stored and rethrown by `future.get()`."]),

307: D("`std::launch::async` runs the task on a new thread immediately; `std::launch::deferred` runs it lazily on the calling thread when `get()` or `wait()` is called; the default (both flags) lets the implementation choose.",
"""With the default policy you can't rely on concurrency: the task might be deferred and never run if nobody calls `get()`, and `thread_local` variables differ depending on where it runs. `wait_for` on a deferred future returns `std::future_status::deferred` rather than timing out, which can create infinite loops in polling code.

Specify `std::launch::async` explicitly when you need real parallelism.""",
"Polling `while (f.wait_for(10ms) != std::future_status::ready)` with the default policy; if the task was deferred, the status is `deferred` forever.",
["What can happen to a deferred task nobody waits on? => It never runs.",
 "Why specify `std::launch::async` explicitly? => To guarantee the task runs concurrently on another thread."]),

308: D("A spurious wakeup is when a thread waiting on a condition variable returns from `wait` even though no notification was sent (or the condition isn't actually true), which the standard explicitly permits.",
"""Spurious wakeups come from how OS primitives are implemented (signals, futex behaviour); additionally, another thread may have consumed the item between notification and wakeup. Either way, the waiter must recheck the condition.

Always use the predicate overload `cv.wait(lock, pred)`, which loops internally: `while (!pred()) cv.wait(lock);`.""",
"`cv.wait(lock); process(queue.front());` without re-checking, which pops from an empty queue after a spurious wakeup.",
["How does the predicate overload handle spurious wakeups? => It loops until the predicate is true.",
 "Besides spurious wakeups, why must you recheck? => Another waiter may have consumed the state change first."]),

309: D("`std::call_once` with a `std::once_flag` guarantees a function runs exactly once even if many threads call it concurrently; other callers wait until it completes.",
"""Use it for lazy one-time initialization of shared resources (loading a device database, initializing a library). If the function throws, the flag isn't set and a later call retries.

For initializing a single object, a function-local `static` (\"magic static\", thread-safe since C++11) is simpler and usually implemented equally efficiently.""",
"Implementing one-time init with a plain `bool initialized` flag checked without synchronization, which races and can initialize twice.",
["What happens if the `call_once` function throws? => The flag remains unset, and the next caller tries again.",
 "What's a simpler alternative for lazy singletons? => A function-local static variable (thread-safe initialization since C++11)."]),

310: D("`thread_local` gives each thread its own instance of a variable, created when the thread first uses it (or at thread start) and destroyed when the thread exits.",
"""Uses: per-thread caches, random number generators, error context, allocation arenas and per-thread counters aggregated later, all without locking.

Costs and caveats: access may involve a TLS lookup (cheap on most platforms), destructors run at thread exit (which can be tricky for detached threads or thread pools where threads live long), and `thread_local` in dynamically loaded libraries has platform-specific limitations.""",
"Storing request-specific context in a `thread_local` inside a thread pool, and forgetting that the next task on the same thread sees the previous task's leftover value.",
["When are `thread_local` objects destroyed? => When their thread exits.",
 "Why are `thread_local` values risky in thread pools? => Threads are reused across tasks, so state leaks between tasks unless reset."]),

311: D("Concurrency is structuring a program as multiple tasks that can make progress in overlapping time periods; parallelism is actually executing multiple tasks at the same instant on multiple cores.",
"""A single-core system can be concurrent (interleaving threads or async I/O) but not parallel. Concurrency is about design (handling many things, e.g. many devices or connections); parallelism is about speed (doing CPU work faster).

C++ provides both: threads and async/futures for concurrency, parallel algorithms (`std::sort(std::execution::par, ...)`) and thread pools for parallelism. Coroutines (C++20) help write concurrent I/O-bound code without one thread per task.""",
"Adding threads to I/O-bound code expecting CPU speedups, or to CPU-bound code with a shared lock that serializes all work anyway.",
["Can you have concurrency without parallelism? => Yes, e.g. interleaved tasks on a single core or an event loop.",
 "How do you parallelize `std::sort` in C++17? => Pass an execution policy: `std::sort(std::execution::par, v.begin(), v.end())`."]),

312: D("The C++11 memory model defines how threads interact through memory: what a data race is (undefined behaviour), and which writes a read may observe, via \"happens-before\" relationships created by synchronization (mutexes, atomics, thread start/join).",
"""Before C++11, compilers and CPUs could legally reorder memory operations in ways that broke multithreaded code, and the language didn't say what was allowed, so portable lock-free code was impossible.

The model gives two guarantees: data-race-free programs behave sequentially consistently when using default atomics and locks, and atomics with explicit memory orders give precise, portable control over visibility for performance-critical code. It maps to each CPU's own model (strong on x86, weak on ARM and POWER).""",
"Assuming code tested on x86 is correct on ARM; x86's strong ordering hides missing synchronization that ARM exposes.",
["What is happens-before? => An ordering guarantee: if A happens-before B, B observes A's effects; it's established by synchronization.",
 "Why do bugs appear on ARM but not x86? => ARM allows more reordering, so missing acquire/release semantics become visible."]),

313: D("Memory orderings specify how an atomic operation orders surrounding memory accesses: `relaxed` guarantees only atomicity; `acquire`/`release` create one-way synchronization between a writer and a reader; `acq_rel` does both; `seq_cst` (default) adds a single global order of all sequentially consistent operations.",
"""Common pattern (message passing): the producer writes data, then `ready.store(true, std::memory_order_release)`; the consumer does `while (!ready.load(std::memory_order_acquire));` then reads the data safely. Release/acquire guarantees the data writes are visible.

`relaxed` suits counters where only the final total matters. `consume` exists but is discouraged (compilers treat it as acquire). Use `seq_cst` unless profiling shows a need and you can prove correctness; weaker orderings are a common source of subtle bugs.""",
"Using `memory_order_relaxed` for a \"data is ready\" flag, allowing the consumer to see the flag before the data on weakly ordered CPUs.",
["When is `memory_order_relaxed` enough? => For statistics counters or IDs where no other data depends on the ordering.",
 "What does release/acquire guarantee? => Everything written before the release store is visible after the matching acquire load."]),

314: D("False sharing occurs when threads write to different variables located on the same cache line, causing the line to ping-pong between cores and destroying performance even though no data is logically shared.",
"""Typical victims: arrays of per-thread counters, adjacent atomics in a struct, or a producer index and consumer index next to each other in a ring buffer.

Mitigation: align hot per-thread data to cache-line boundaries with `alignas(std::hardware_destructive_interference_size)` (or `alignas(64)`), pad structures, accumulate in thread-local variables and combine at the end. Measure with `perf c2c` (Linux) or VTune.""",
"Putting a lock-free queue's head and tail indices in adjacent members, so producer and consumer threads constantly invalidate each other's cache lines.",
["How do you align a struct to a cache line? => `struct alignas(64) Counter { std::atomic<uint64_t> n; };` or use `std::hardware_destructive_interference_size`.",
 "Why does false sharing hurt even with atomics? => The cache coherence protocol transfers the whole line on every write, regardless of which bytes changed."]),

315: D("A lock-free data structure guarantees that, among all threads operating on it, at least one makes progress in a finite number of steps, even if others are suspended; it uses atomic operations (usually compare-exchange) instead of mutexes.",
"""Progress guarantees hierarchy: **wait-free** (every thread finishes in bounded steps) > **lock-free** (system-wide progress) > **obstruction-free** > blocking (mutex-based, where a descheduled lock holder blocks everyone).

Benefits: no deadlocks, no priority inversion, robustness when threads are preempted, sometimes better scalability. Costs: much harder to write and verify (ABA problem, memory reclamation, memory ordering), and not automatically faster than a well-designed mutex under low contention. Use proven libraries (Boost.Lockfree, Folly, moodycamel) rather than writing your own.""",
"Writing a custom lock-free queue for performance without benchmarks, introducing subtle memory-reclamation bugs while a mutex would have been fast enough.",
["Is lock-free always faster than a mutex? => No; it avoids blocking, but contention and complex atomics can make it slower.",
 "What's wait-free? => Every operation completes in a bounded number of steps regardless of other threads."]),

316: D("The ABA problem occurs in compare-and-swap loops when a value changes from A to B and back to A between a thread's read and its CAS, so the CAS succeeds even though the structure changed in between.",
"""Classic case: a lock-free stack pops node A, gets preempted; other threads pop A, pop B, push A back (reusing the freed memory); the first thread's CAS on head succeeds with a stale `next` pointer, corrupting the stack.

Solutions: tagged pointers (a version counter updated with each change, using double-width CAS), hazard pointers or epoch-based reclamation (so nodes aren't reused while referenced), or garbage-collected/reference-counted nodes.""",
"Freeing and reusing nodes immediately in a lock-free stack or queue, which makes ABA corruption likely under load.",
["How do tagged pointers solve ABA? => A counter changes on every modification, so an A-B-A sequence changes the tag and the CAS fails.",
 "Why does safe memory reclamation help? => Nodes can't be reused while another thread may still reference them, so A can't reappear at the same address."]),

317: D("Priority inversion is when a high-priority thread waits for a lock held by a low-priority thread, while a medium-priority thread preempts the low-priority one, effectively blocking the high-priority thread indefinitely.",
"""The famous example is the 1997 Mars Pathfinder resets. It matters in real-time systems and firmware (RTOS tasks) and in audio/game threads.

Mitigations: **priority inheritance** mutexes (the lock holder temporarily inherits the waiter's priority; POSIX `PTHREAD_PRIO_INHERIT`, most RTOSes support it), priority ceiling protocols, keeping critical sections short, avoiding shared locks between priority levels, and lock-free handoff queues.""",
"Sharing one mutex between an interrupt-driven high-priority task and a low-priority logging task in an RTOS without priority inheritance enabled.",
["What fixed Mars Pathfinder's resets? => Enabling priority inheritance on the offending mutex.",
 "What is priority inheritance? => The low-priority lock holder runs at the waiting high-priority task's priority until it releases the lock."]),

318: D("A mutex provides exclusive ownership (only the locking thread should unlock it); a semaphore is a counter allowing up to N concurrent acquisitions and can be released by any thread, making it suitable for signaling and resource counting.",
"""C++20 adds `std::counting_semaphore<N>` and `std::binary_semaphore`. Uses: limiting concurrency (at most 4 threads using the lab's analyzers), producer/consumer slot counting, and signaling between threads (one thread `release()`s, another `acquire()`s).

Unlike mutexes, semaphores don't protect data invariants by themselves and don't support priority inheritance; use them for counting and signaling, mutexes for mutual exclusion.""",
"Using a binary semaphore as a mutex: any thread can release it, so a bug can \"unlock\" a critical section owned by another thread.",
["Can a thread release a semaphore it didn't acquire? => Yes, which makes semaphores good for signaling but weaker as locks.",
 "How do you limit concurrent access to 4 resources? => `std::counting_semaphore<4> sem(4);` with `acquire`/`release` around use."]),

319: D("A data race is formally two conflicting accesses to the same memory location from different threads, at least one a write, not both atomic, and not ordered by happens-before; it's undefined behaviour. A race condition is a broader logic bug where outcome depends on timing.",
"""A data race is a language-level violation: the compiler may assume it never happens, so racy code can be miscompiled (e.g. a loop reading a non-atomic flag may never see updates). A race condition is a design-level bug that can exist even with correct atomics or locks.

ThreadSanitizer (`-fsanitize=thread`) detects data races at runtime; race conditions need design review and stress testing.""",
"Spinning on a plain `bool stop` flag set by another thread; it's a data race, and the optimizer may hoist the load out of the loop so it never exits. Use `std::atomic<bool>`.",
["Which tool detects data races? => ThreadSanitizer (`-fsanitize=thread`).",
 "Why can a data race break code even on x86? => The compiler can reorder, cache or eliminate non-atomic accesses, regardless of CPU ordering."]),

320: D("`std::jthread` (C++20) is a thread that automatically joins in its destructor and has built-in cooperative cancellation through `std::stop_token`/`request_stop()`.",
"""With `std::thread`, forgetting to join (e.g. due to an exception) calls `std::terminate`. `std::jthread` requests stop and joins on destruction, making it RAII-safe.

The thread function can take a `std::stop_token` as its first parameter and check `stop_requested()`, or register a `std::stop_callback`, or pass the token to `std::condition_variable_any::wait` so waits are interrupted when stop is requested.""",
"Using `std::jthread` but never checking the stop token in a long-running loop; the destructor's join then blocks forever.",
["How does a `jthread` function learn it should stop? => Accept a `std::stop_token` parameter and check `stop_requested()`.",
 "What does the `jthread` destructor do? => Calls `request_stop()` and then `join()`."]),

321: D("A thread pool is a fixed set of worker threads that take tasks from a shared queue, avoiding the cost and oversubscription of creating a new thread per task.",
"""Creating a thread costs microseconds and memory (stack); thousands of short-lived threads thrash the scheduler. A pool sized to the hardware (`std::thread::hardware_concurrency()`) or to the I/O workload reuses threads, bounds concurrency, and centralizes shutdown and error handling.

Design points: task queue (mutex + condition variable, or lock-free), futures for results (`std::packaged_task`), graceful shutdown, exception propagation, and avoiding tasks that block waiting for other tasks in the same pool (deadlock by starvation). Libraries: Boost.Asio thread_pool, Intel oneTBB, and C++26 `std::execution`.""",
"Submitting tasks that wait on the results of other tasks in the same fixed-size pool; when all workers wait, nothing runs and the pool deadlocks.",
["How big should a thread pool be? => About the number of cores for CPU-bound work; larger for I/O-bound work that mostly waits.",
 "How do tasks return results? => Wrap them in `std::packaged_task` and hand the caller the associated `std::future`."]),

322: D("Double-checked locking checks a pointer without a lock, locks, checks again, and initializes if still null; it's tricky because without atomics and proper ordering, another thread can see the pointer before the object's construction is visible.",
"""Pre-C++11 implementations were broken: the compiler or CPU could publish the pointer before the constructor's writes. A correct C++11 version uses `std::atomic<T*>` with acquire loads and a release store.

But usually you don't need it: a function-local static (`static Config& instance() { static Config c; return c; }`) is thread-safe since C++11 and compilers implement it efficiently; `std::call_once` is the other standard option.""",
"Writing double-checked locking with a plain pointer (no atomic), which is a data race and can expose a partially constructed object.",
["What's the simplest thread-safe lazy singleton in C++11? => A function-local static variable.",
 "What memory ordering does correct DCLP need? => An acquire load for the first check and a release store when publishing."]),

323: D("Concurrent reads of a `std::vector` are safe, but if **any** thread modifies it (push_back, resize, even writing different elements while another thread resizes), accesses race; reallocation also invalidates what readers are using.",
"""Standard library guarantee: concurrent calls to `const` member functions on the same object are safe; any non-const call concurrent with any other access needs synchronization. Writing **different elements** from different threads is safe only if no thread changes the vector's size or capacity (except `std::vector<bool>`, whose bits share bytes).

Patterns: protect with a mutex (or `shared_mutex` for read-mostly), give each thread its own vector and merge, or pre-size the vector and let each thread write its own index range.""",
"Having worker threads `push_back` results into one shared vector \"because each thread adds different items\"; reallocation makes it a data race.",
["Is it safe for threads to write different elements of a pre-sized vector? => Yes, if no thread resizes it (and it isn't `vector<bool>`).",
 "What does the standard guarantee for const member functions? => Concurrent const calls on the same object don't race."]),

324: D("A hazard pointer is a per-thread published pointer that marks a node as \"in use\"; before freeing a retired node, a thread checks that no hazard pointer references it, providing safe memory reclamation for lock-free data structures.",
"""Lock-free structures can't simply `delete` removed nodes because other threads may still be reading them. With hazard pointers, a reader publishes the pointer it's about to dereference and re-validates; a remover puts nodes on a retire list and frees only those not protected by any hazard pointer.

Alternatives: epoch-based reclamation (RCU-like, cheaper reads, but a stalled thread blocks reclamation) and reference counting. Hazard pointers and RCU are being standardized in C++26 (`<hazard_pointer>`, `<rcu>`).""",
"Freeing nodes from a lock-free structure immediately after unlinking them, causing use-after-free in concurrent readers (and ABA issues).",
["Hazard pointers vs epoch-based reclamation? => Hazard pointers bound unreclaimed memory but cost per-access publication; epochs make reads cheaper but a stalled thread delays all reclamation.",
 "Are hazard pointers in the standard? => They're added in C++26."]),

325: D("Concurrent output to `std::cout` from multiple threads doesn't cause a data race (the standard streams are synchronized when `sync_with_stdio` is true), but characters and parts of lines from different threads may interleave.",
"""Each `<<` is a separate operation, so `std::cout << \"device \" << id << \" done\\n\";` from two threads can mix fragments. Solutions: build the whole line in a `std::ostringstream` or `std::format` string and write it with one call, use C++20 `std::osyncstream(std::cout)` which emits its buffer atomically, or route logs through a single logging thread or a thread-safe logger (spdlog).

Calling `std::ios::sync_with_stdio(false)` improves performance but removes the guarantee for concurrent access.""",
"Debug printing from worker threads with chained `<<`, producing garbled log lines that hide the actual sequence of events.",
["What does `std::osyncstream` do? => Buffers output and writes it to the underlying stream atomically when destroyed or flushed.",
 "What does `sync_with_stdio(false)` change for threads? => Concurrent use of the standard streams is no longer guaranteed to be free of data races."]),
}
