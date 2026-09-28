# Additions for Data Management and Resilience topics.
EXTRA = {

"db-per-service": dict(
 terms=[("Database per service", "Each service owns its data store, and no other service reads or writes it directly."),
        ("Polyglot persistence", "Choosing different database types per service (relational, document, key-value, search) to fit each workload."),
        ("API composition", "Answering a query by calling several services and joining the results in memory."),
        ("Materialized view", "A read-optimized copy of data from several services, kept up to date by consuming their events.")],
 pitfalls=[("Reporting jobs that read every service's database directly.", "Feed a data warehouse or lake through events or CDC, and keep service databases private."),
           ("Foreign keys across service boundaries.", "Reference other services' entities by ID and validate through APIs or events."),
           ("Splitting the database before splitting the code.", "Separate schemas and ownership first, move to physically separate databases once access patterns are clean.")],
 qa=[("How do you keep reference data (like product names) available to many services?", "Let the owning service publish change events, and have consumers keep a local read-only copy of the fields they need. This avoids a synchronous call on every request and survives the owner being down.\n\nAccept that copies are eventually consistent, and include version numbers or timestamps so consumers ignore out-of-order updates."),
     ("What are the operational costs of database per service?", "More databases to provision, back up, patch, monitor and secure; harder cross-service queries and reporting; eventual consistency to handle in code; and more complex local development and testing.\n\nManaged database services, standard templates and a shared data platform for analytics reduce the cost, and a shared database server with separate schemas and credentials is a reasonable middle step.")]),

"saga": dict(
 terms=[("Saga", "A sequence of local transactions across services, where each step publishes an event or command that triggers the next, and failures trigger compensating steps."),
        ("Compensating transaction", "A business action that semantically undoes an earlier step (refund a payment), not a database rollback."),
        ("Choreography", "Services react to each other's events with no central coordinator."),
        ("Orchestration", "A central orchestrator tells each service what to do and tracks the saga's state.")],
 pitfalls=[("Forgetting that intermediate states are visible.", "Model explicit states (PENDING, CONFIRMED, CANCELLED) and use semantic locks or checks so other operations do not act on half-finished sagas."),
           ("Compensations that can fail with no plan.", "Make compensations idempotent and retryable, and route persistent failures to a manual-handling queue."),
           ("Long choreographed chains nobody can follow.", "Switch to orchestration (for example Temporal or AWS Step Functions) once a flow involves more than a few steps.")],
 qa=[("What is a pivot transaction in a saga?", "The step after which the saga can no longer be compensated and must complete, for example shipping the parcel or sending money to an external bank. Steps before it are compensatable; steps after it must be retryable until they succeed.\n\nOrdering matters: put risky, compensatable checks (reserve stock, authorize payment) before the pivot, and guaranteed-to-succeed steps after it."),
     ("How does a workflow engine like Temporal help implement sagas?", "It persists the orchestration state durably, so the workflow code survives crashes and resumes where it stopped. Retries, timeouts and compensation logic are written as ordinary code, and every step is recorded for audit and debugging.\n\nThe trade-off is a new piece of infrastructure and the need to write deterministic workflow code, but it removes most hand-rolled state-machine and retry logic.")]),

"cqrs": dict(
 terms=[("CQRS", "Command Query Responsibility Segregation: separate models (and often stores) for writes and for reads."),
        ("Command model", "The write side, which validates and applies changes while enforcing business rules."),
        ("Read model / projection", "A denormalized view built for specific queries, updated from write-side events."),
        ("Projection lag", "The time between a write and its appearance in the read model.")],
 pitfalls=[("Applying CQRS to simple CRUD screens.", "Use it only where read and write needs clearly differ; otherwise it adds complexity for no gain."),
           ("Users not seeing their own change right after saving.", "Return the updated data from the command, read your own writes from the write store, or wait on a version number."),
           ("No way to rebuild a broken read model.", "Keep events or a change log so projections can be rebuilt from scratch.")],
 qa=[("How do you rebuild or add a new read model in production?", "Create the new projection alongside the old one, replay historical events (or a CDC snapshot plus log) into it, let it catch up with live events, verify counts and samples, then switch queries to it and drop the old one.\n\nThis only works if the event history is retained and projections are idempotent, which is why those are design requirements from the start."),
     ("How do you choose storage for read models?", "Pick per query pattern: a search engine (Elasticsearch, OpenSearch) for full-text and faceted search, a key-value or document store for 'get by ID' views, a columnar store for analytics, a cache for hot data.\n\nThe freedom to choose different stores per view is one of the main benefits of CQRS.")]),

"event-sourcing": dict(
 terms=[("Event sourcing", "Storing the sequence of state-changing events as the source of truth and deriving current state by replaying them."),
        ("Event store", "An append-only store of events per aggregate stream, with optimistic concurrency on the stream version."),
        ("Snapshot", "A saved state at some version, so replay starts from the snapshot instead of the first event."),
        ("Upcasting", "Converting old event versions into the current schema when reading them.")],
 pitfalls=[("Changing or deleting past events to fix bugs.", "Events are immutable; append correcting events instead."),
           ("Storing personal data in events and then needing to erase it (GDPR).", "Keep personal data outside the events, or encrypt it per user and delete the key (crypto-shredding)."),
           ("No schema versioning for events.", "Version event types and upcast old versions on read.")],
 qa=[("How do you handle concurrent updates to the same aggregate?", "With optimistic concurrency: the command handler loads the stream at version N, decides, and appends new events with 'expected version N'. If someone else appended first, the store rejects the write and the handler reloads and retries or reports a conflict.\n\nThis gives consistency within one aggregate without locks; consistency across aggregates is handled with sagas and eventual consistency."),
     ("What are the main costs of event sourcing?", "A learning curve, event schema evolution forever (old events never go away), eventual consistency for queries (it almost always comes with CQRS), more complex debugging and data fixes, and privacy handling for immutable data.\n\nIt pays off where the history itself has business value: audit, finance, bookings, or domains where you need to answer 'what was the state at time T'.")]),

"outbox-idempotency": dict(
 terms=[("Dual-write problem", "Writing to a database and publishing a message are two separate operations, and one can succeed while the other fails."),
        ("Transactional outbox", "Writing the outgoing message into an outbox table in the same database transaction as the business change, and publishing it afterwards."),
        ("Message relay", "The process that reads the outbox (by polling or CDC) and publishes to the broker."),
        ("Idempotency key", "A unique ID sent with a request or message so repeated deliveries are processed only once.")],
 pitfalls=[("Publishing the event before committing the transaction.", "Only publish from the outbox after commit, or the event may describe a change that was rolled back."),
           ("Letting the outbox table grow forever.", "Delete or archive published rows and index the table for the relay's query."),
           ("Idempotency keys with no expiry or scope.", "Store keys with the result and a retention period, scoped per client or operation.")],
 qa=[("How do you implement idempotency for a payment API like Stripe's?", "The client sends an Idempotency-Key header. The server stores the key with the request fingerprint and the eventual response. A retry with the same key returns the stored response without charging again; a request with the same key but different parameters is rejected.\n\nThe key record and the business change must be written atomically, or a crash between them breaks the guarantee."),
     ("Polling relay vs CDC for the outbox: trade-offs?", "Polling is simple and needs no extra infrastructure, but adds query load and some latency. CDC (for example Debezium reading the write-ahead log) gives low latency and no polling load, but adds a connector to operate and depends on database log access.\n\nBoth deliver at least once, so consumers must be idempotent either way.")]),

"cap": dict(
 terms=[("Consistency (CAP)", "Every read returns the most recent write or an error (linearizability)."),
        ("Availability (CAP)", "Every request to a non-failing node receives a non-error response."),
        ("Partition tolerance", "The system keeps working even when the network drops messages between nodes."),
        ("PACELC", "Extends CAP: if Partitioned, choose Availability or Consistency; Else (normal operation), choose Latency or Consistency.")],
 pitfalls=[("Saying a distributed system can choose 'CA'.", "Partitions happen, so the real choice is what to do during one: stay consistent (refuse some requests) or stay available (accept stale or conflicting data)."),
           ("Treating consistency as all-or-nothing per system.", "Choose per operation: strong consistency for payments and stock, eventual consistency for feeds and counters."),
           ("Ignoring latency in normal operation.", "Use PACELC thinking: strong consistency across regions costs latency even without partitions.")],
 qa=[("What does PACELC add to CAP, and how do real databases fit?", "CAP only describes behaviour during a partition. PACELC adds the everyday trade-off: without partitions, you still trade latency against consistency.\n\nDynamoDB and Cassandra are usually described as PA/EL (available and low-latency, eventually consistent by default, with tunable stronger reads), while Spanner and traditional single-leader databases lean PC/EC (consistent, paying latency)."),
     ("What is read-your-writes consistency and how do you provide it?", "A guarantee that after a user writes, their own subsequent reads see that write, even if other users may still see older data.\n\nOptions: route that user's reads to the leader for a short time, read from a replica only if it has caught up to the write's version or timestamp, or return the written data directly from the write request.")]),

"caching": dict(
 terms=[("Cache-aside", "The application reads from the cache, loads from the database on a miss, and populates the cache itself."),
        ("TTL", "Time to live: how long a cache entry stays valid before expiring."),
        ("Cache stampede", "Many requests missing the same key at once and all hitting the database."),
        ("Hit ratio", "The share of reads served from the cache; the main measure of cache effectiveness.")],
 pitfalls=[("Caching without an invalidation plan.", "Decide per key: TTL, delete on write, or event-driven invalidation."),
           ("All keys expiring at the same moment.", "Add random jitter to TTLs."),
           ("Treating the cache as the source of truth.", "The system must work, more slowly, with an empty cache.")],
 qa=[("What are the main cache eviction policies?", "LRU (least recently used) evicts the item not accessed for the longest time and suits most workloads. LFU (least frequently used) keeps popular items even if not accessed recently. TTL-based expiry removes items by age.\n\nRedis offers approximated LRU and LFU policies (allkeys-lru, allkeys-lfu, volatile-*); pick based on whether popularity or recency predicts future reads."),
     ("How do you handle a hot key that overloads one cache node?", "Replicate the hot key under several suffixed names and pick one at random on reads, add a small in-process (local) cache in front of the distributed cache, or use read replicas.\n\nDetect hot keys with the cache's own tooling (for example redis-cli --hotkeys) or client-side metrics, because they often appear suddenly with traffic spikes.")]),

"circuit-breaker": dict(
 terms=[("Circuit breaker", "A proxy that stops calling a failing dependency for a while, failing fast instead of waiting on timeouts."),
        ("Closed / Open / Half-open", "Closed passes calls through; Open rejects immediately; Half-open lets a few trial calls test recovery."),
        ("Failure-rate threshold", "The share of failed or slow calls in a sliding window that trips the breaker."),
        ("Fallback", "The alternative response returned when the call is rejected or fails (cached data, default value, graceful error).")],
 pitfalls=[("One breaker for all endpoints of a dependency.", "Use breakers per dependency and per critical operation, so one bad endpoint does not block healthy ones."),
           ("Thresholds evaluated on too few calls.", "Set a minimum number of calls in the window before the breaker can trip."),
           ("Counting client errors (400s) as failures.", "Count timeouts, 5xx and connection errors, not caller mistakes.")],
 qa=[("How would you tune a circuit breaker?", "Start from measured behaviour: the dependency's normal error rate and p99 latency. Set the failure threshold well above normal (for example 50 percent in a window of the last 100 calls, with a minimum of 20), treat calls slower than a slow-call threshold as failures, and choose an open duration long enough for recovery (tens of seconds).\n\nThen test with fault injection and watch breaker state metrics in production, adjusting to avoid both flapping and slow detection."),
     ("What is the difference between a circuit breaker in the application and in a service mesh?", "A library breaker (Resilience4j, Polly) runs in the caller's code, can use business-aware fallbacks, and sees exceptions. A mesh breaker (Envoy outlier detection and connection limits) needs no code changes and applies uniformly across languages, but can only see network-level signals and cannot return a business fallback.\n\nMany systems use both: the mesh for uniform protection, the library where a meaningful fallback exists.")]),

"retry-timeout": dict(
 terms=[("Timeout", "The maximum time a caller waits for a response before giving up."),
        ("Exponential backoff", "Increasing the wait between retries (for example 100 ms, 200 ms, 400 ms) to give the dependency time to recover."),
        ("Jitter", "Randomizing retry delays so many clients do not retry in synchronized waves."),
        ("Retry budget", "A cap on retries as a share of total requests (for example 10 percent), limiting how much retries can amplify load.")],
 pitfalls=[("Retrying at every layer of a call chain.", "Retry at one layer (usually closest to the failure or the edge) to avoid multiplicative retry storms."),
           ("Retrying non-idempotent operations.", "Retry only idempotent calls, or add idempotency keys first."),
           ("No overall deadline.", "Propagate a deadline so retries stop when the caller no longer needs the answer.")],
 qa=[("Why are nested retries dangerous? Give numbers.", "If each of four layers retries a failing call 3 times (4 attempts each), the bottom service receives up to 4 x 4 x 4 x 4 = 256 attempts for one user request. During an outage that multiplies load exactly when the service is weakest and prevents recovery.\n\nRetry at one layer, use budgets, and let circuit breakers stop retries when a dependency is clearly down."),
     ("What is hedging and when is it useful?", "Sending a duplicate request to another replica if the first has not answered within a short delay (for example the p95 latency), and using whichever response arrives first.\n\nIt cuts tail latency for idempotent reads, as described in Google's 'The Tail at Scale', at the cost of a few percent extra load. It must not be used for non-idempotent writes.")]),

"bulkhead": dict(
 terms=[("Bulkhead", "Isolating resources per dependency or workload so one failure cannot exhaust shared resources."),
        ("Thread-pool bulkhead", "A dedicated, bounded executor for calls to one dependency."),
        ("Semaphore bulkhead", "A limit on concurrent calls to a dependency, without separate threads."),
        ("Load shedding", "Rejecting excess requests early (with 503 or 429) instead of queuing them until everything is slow.")],
 pitfalls=[("Unbounded queues in front of bounded pools.", "Bound queues too; a full queue should fail fast, not grow latency without limit."),
           ("Sizing pools by guesswork.", "Size from Little's law: concurrency = throughput x latency, plus headroom, then verify under load."),
           ("Bulkheads without timeouts.", "A stuck call still holds its slot; always pair bulkheads with timeouts.")],
 qa=[("How do you size a bulkhead using Little's law?", "Required concurrency is roughly throughput times latency. If the Payment dependency handles 200 requests per second at a p99 of 250 ms, you need about 200 x 0.25 = 50 concurrent slots, plus headroom for spikes, say 60 to 70.\n\nIf the pool fills anyway, that signals the dependency's latency has grown, which is exactly the situation the bulkhead should contain."),
     ("How do bulkheads apply beyond thread pools?", "At the infrastructure level: separate Kubernetes node pools or namespaces with resource quotas for critical and batch workloads, dedicated clusters or cells for large tenants, separate connection pools per database, and separate queues per priority.\n\nThe principle is the same: a failure or overload in one compartment must not consume resources the others need.")]),

"rate-limiting": dict(
 terms=[("Rate limiting", "Restricting how many requests a client can make in a period."),
        ("Token bucket", "Tokens refill at a fixed rate up to a capacity; each request spends a token, allowing short bursts."),
        ("Sliding window", "Counting requests over a rolling time window to avoid the burst at fixed-window boundaries."),
        ("Throttling", "Slowing or rejecting requests once a limit is reached; often used interchangeably with rate limiting.")],
 pitfalls=[("Per-instance limits behind a load balancer.", "Use a shared store (Redis with atomic scripts) or divide the global limit by instance count."),
           ("Returning 500 instead of 429.", "Return 429 Too Many Requests with a Retry-After header so clients can back off correctly."),
           ("Limiting only by IP.", "Limit by API key, user or tenant as well; many users can share an IP behind NAT.")],
 qa=[("How would you design a distributed rate limiter?", "Keep counters in Redis keyed by client and window, updated atomically with a Lua script (for example a sliding-window log or token bucket). The gateway calls it on each request, with a small local cache or approximate counting to cut latency.\n\nDecide the failure mode explicitly: fail open (allow traffic if Redis is down) for availability, or fail closed for protection-critical APIs, and monitor the limiter's own latency."),
     ("Rate limiting vs load shedding vs backpressure?", "Rate limiting enforces per-client quotas (fairness and abuse protection). Load shedding drops work when the service itself is overloaded, regardless of which client sent it. Backpressure signals upstream producers to slow down (for example a full queue or reactive streams demand).\n\nA robust system uses all three: quotas at the edge, shedding in services, and backpressure in pipelines.")]),

"health-checks": dict(
 terms=[("Liveness probe", "Checks whether the process is alive; failing it makes Kubernetes restart the container."),
        ("Readiness probe", "Checks whether the instance can serve traffic; failing it removes the pod from load balancing without restarting it."),
        ("Startup probe", "Gives slow-starting containers time to start before liveness checks begin."),
        ("Graceful degradation", "Continuing to serve reduced functionality when a dependency is unhealthy.")],
 pitfalls=[("Liveness probes that check the database.", "A database outage then restarts every pod in a loop; keep liveness to the process itself."),
           ("Readiness that fails on every dependency blip.", "Fail readiness only for dependencies without which the instance cannot serve anything useful."),
           ("Probes with timeouts shorter than a GC pause.", "Tune timeouts and failure thresholds so one slow response does not trigger a restart.")],
 qa=[("What is a startup probe and when do you need one?", "A probe that runs first and disables liveness and readiness checks until it succeeds. It is for applications that take a long time to start (JVM warm-up, cache loading, migrations).\n\nWithout it you must make the liveness initial delay very long, which also delays detecting real hangs; with it, liveness can stay aggressive after start-up."),
     ("How does a readiness probe interact with a rolling deployment?", "Kubernetes only counts a new pod as available once it passes readiness, and only then continues terminating old pods (governed by maxUnavailable and maxSurge). A broken new version that never becomes ready stalls the rollout instead of replacing healthy pods.\n\nThat makes a meaningful readiness check a deployment safety feature, not just a load-balancing one.")]),
}
