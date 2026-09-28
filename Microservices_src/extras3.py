# Additions for Observability, Security, Operations and Interview Toolkit topics.
EXTRA = {

"logging": dict(
 terms=[("Structured logging", "Emitting logs as key-value records (usually JSON) instead of free text, so they can be filtered and aggregated."),
        ("Correlation ID", "An ID attached to a request at the edge and passed to every service, so all its log lines can be found together."),
        ("Log aggregation", "Shipping logs from all instances to a central store (Elasticsearch, Loki, CloudWatch) for search."),
        ("Log level", "Severity of a log line (DEBUG, INFO, WARN, ERROR), used to control volume and alerting.")],
 pitfalls=[("Logging personal data, tokens or passwords.", "Mask or drop sensitive fields at the logging library, and audit log output."),
           ("Writing logs to local files inside containers.", "Log to stdout and let the platform collect and ship logs."),
           ("DEBUG logging everywhere in production.", "Log at INFO by default, sample high-volume events, and allow dynamic level changes for troubleshooting.")],
 qa=[("How do you control logging costs at scale?", "Log less but better: structured events with useful fields, no per-item logs inside hot loops, sampling for successful high-volume requests, shorter retention for verbose data, and tiered storage for older logs.\n\nMove numeric signals into metrics (much cheaper) and use traces for request-level detail; logs should explain what metrics and traces cannot."),
     ("How do logs, metrics and traces work together during an incident?", "Metrics tell you something is wrong (error rate or p99 alert). Traces show where in the call chain the time or errors are. Logs from the specific spans explain why (the exception, the bad input).\n\nLinking them is key: put trace IDs in log lines and use exemplars that attach trace IDs to metric samples, so you can jump from a latency spike to example traces to their logs.")]),

"tracing": dict(
 terms=[("Trace", "The complete record of one request's path through the system, made of spans."),
        ("Span", "One timed operation within a trace (an HTTP call, a database query), with a parent span, attributes and status."),
        ("W3C Trace Context", "The standard traceparent and tracestate headers for propagating trace IDs across services."),
        ("OpenTelemetry", "The vendor-neutral standard and SDKs for generating traces, metrics and logs.")],
 pitfalls=[("Losing trace context across async hops (queues, thread pools).", "Propagate context in message headers and use instrumented executors."),
           ("Sampling so aggressively that errors are never kept.", "Use tail-based sampling that keeps all errors and slow traces while sampling normal ones."),
           ("High-cardinality span names (with IDs in them).", "Use route templates (GET /orders/{id}) as names and put IDs in attributes.")],
 qa=[("Head-based vs tail-based sampling?", "Head-based sampling decides at the start of a trace (for example keep 1 percent), which is cheap but may drop the interesting failing requests. Tail-based sampling buffers complete traces in a collector and decides after seeing them, so it can keep all errors and slow traces.\n\nTail sampling needs more collector memory and all spans of a trace routed to the same collector, but gives far better debugging value per stored trace."),
     ("What does an OpenTelemetry Collector do?", "It receives telemetry from applications, processes it (batching, filtering, sampling, attribute redaction, enrichment with Kubernetes metadata) and exports it to one or more back ends.\n\nIt decouples applications from vendors: switching from Jaeger to another back end is a collector config change, not an application change.")]),

"metrics": dict(
 terms=[("SLI", "Service Level Indicator: a measured quantity of service health, such as the share of requests under 300 ms."),
        ("SLO", "Service Level Objective: the target for an SLI over a window, such as 99.9 percent of requests under 300 ms over 30 days."),
        ("Error budget", "The allowed amount of unreliability (100 percent minus the SLO), spent on releases and experiments."),
        ("RED and USE", "RED (Rate, Errors, Duration) for services; USE (Utilization, Saturation, Errors) for resources.")],
 pitfalls=[("Alerting on every CPU spike.", "Alert on symptoms users feel (SLO burn rate), and use resource metrics for diagnosis."),
           ("Metrics labels with unbounded values (user ID, order ID).", "Keep label cardinality bounded; put IDs in logs and traces."),
           ("Averaging percentiles across instances.", "Aggregate histograms, then compute percentiles.")],
 qa=[("What is burn-rate alerting?", "Alerting on how fast the error budget is being consumed rather than on raw error rates. A burn rate of 1 uses the budget exactly over the SLO window; a burn rate of 14 would exhaust a 30-day budget in about 2 days.\n\nGoogle's SRE workbook recommends multi-window alerts, for example page when both the 1-hour and 5-minute burn rates exceed 14, which catches fast outages quickly and ignores short blips."),
     ("How much downtime does 99.9 percent availability allow?", "About 43 minutes per 30-day month (0.1 percent of 43,200 minutes) or about 8.8 hours per year. 99.99 percent allows about 4.3 minutes per month.\n\nThe numbers show why each extra nine is expensive: 99.99 percent leaves no room for manual recovery, so it requires automated failover and very safe deployments.")]),

"auth": dict(
 terms=[("Authentication (AuthN)", "Verifying who the caller is."),
        ("Authorization (AuthZ)", "Deciding what the verified caller may do."),
        ("OAuth 2.0", "A framework for delegated authorization using access tokens issued by an authorization server."),
        ("OpenID Connect (OIDC)", "An identity layer on top of OAuth 2.0 that adds an ID token describing the authenticated user.")],
 pitfalls=[("Accepting JWTs without checking the algorithm, issuer or audience.", "Pin allowed algorithms, and validate signature, iss, aud and exp on every request."),
           ("Long-lived access tokens.", "Keep access tokens short (minutes) and use refresh tokens with rotation."),
           ("Doing all authorization at the gateway.", "Check coarse access at the edge and fine-grained permissions inside each service.")],
 qa=[("What is the token exchange or token relay pattern?", "When service A calls service B on behalf of a user, it should not simply forward a broad user token everywhere. With token exchange (RFC 8693) A trades the incoming token for a new one scoped to B's audience and the needed permissions.\n\nThis limits the damage of a leaked token and lets B verify it was meant for B, not for some other service."),
     ("Where should fine-grained authorization logic live?", "Close to the data it protects, inside the owning service, because only it knows ownership rules (can this user edit this order). Centralized policy engines such as Open Policy Agent can hold the rules while services call them with context, keeping policies consistent and auditable.\n\nThe gateway handles only coarse checks such as 'is authenticated' and 'has scope orders:read'.")]),

"service-security": dict(
 terms=[("mTLS", "Mutual TLS: both client and server present certificates, so each side authenticates the other and traffic is encrypted."),
        ("Zero trust", "Never trusting a request because of its network location; every call is authenticated and authorized."),
        ("SPIFFE", "A standard for workload identity (spiffe://domain/workload) used to issue certificates to services."),
        ("Secrets manager", "A system (Vault, AWS Secrets Manager) that stores, rotates and audits credentials.")],
 pitfalls=[("Secrets in environment variables baked into images or Git.", "Inject secrets at runtime from a secrets manager and scan repositories for leaks."),
           ("Long-lived static certificates.", "Issue short-lived certificates automatically (mesh or SPIFFE) and rotate them."),
           ("Flat networks where any pod can call any pod.", "Add network policies and service-level authorization, not just encryption.")],
 qa=[("How does a service mesh provide mTLS automatically?", "The mesh control plane acts as a certificate authority and issues each workload a short-lived certificate tied to its identity (for example its Kubernetes service account). Sidecar or node proxies use these certificates for mTLS on every connection and rotate them automatically.\n\nPolicies can then allow or deny calls by workload identity (orders may call payments) instead of by IP address."),
     ("What are dynamic secrets?", "Credentials generated on demand for each client with a short lease, for example Vault creating a database user that expires in an hour. If a secret leaks it becomes useless quickly, and each credential can be traced to one workload.\n\nThis replaces long-lived shared passwords, which are hard to rotate and impossible to attribute.")]),

"docker": dict(
 terms=[("Image", "An immutable, layered file-system snapshot plus metadata, used to start containers."),
        ("Container", "A running process isolated with Linux namespaces and limited with cgroups, started from an image."),
        ("Layer", "Each Dockerfile instruction creates a cached layer; unchanged layers are reused between builds."),
        ("Registry", "A service that stores and distributes images (Docker Hub, ECR, GCR, Harbor).")],
 pitfalls=[("Running containers as root.", "Add a non-root USER, drop Linux capabilities and use a read-only root file system where possible."),
           ("Using the latest tag in production.", "Pin versions or image digests so deployments are reproducible."),
           ("Large images with build tools and secrets inside.", "Use multi-stage builds, minimal base images, and never copy secrets into layers.")],
 qa=[("How do you make Docker builds fast and cache-friendly?", "Order instructions from least to most frequently changing: copy dependency manifests (package.json, requirements.txt) and install dependencies before copying source code, so code changes do not invalidate the dependency layer. Use a .dockerignore to keep the build context small, and BuildKit cache mounts for package caches.\n\nIn CI, push and reuse cache layers from the registry so every build does not start cold."),
     ("How do you secure the container supply chain?", "Use trusted minimal base images, scan images for vulnerabilities (Trivy, Grype) in CI, generate an SBOM, sign images (Sigstore cosign) and enforce signature and policy checks at admission in the cluster.\n\nRebuild images regularly to pick up base-image patches, not only when code changes.")]),

"kubernetes": dict(
 terms=[("Pod", "The smallest deployable unit: one or more containers sharing network and storage."),
        ("Deployment", "Manages a ReplicaSet of stateless pods and performs rolling updates."),
        ("Service", "A stable virtual IP and DNS name that load-balances to matching pods."),
        ("Requests and limits", "Requests reserve CPU and memory for scheduling; limits cap what a container can use.")],
 pitfalls=[("No resource requests, so the scheduler overpacks nodes.", "Set requests from measured usage and limits that protect the node, especially for memory."),
           ("Single-replica deployments for important services.", "Run at least two replicas across zones with a PodDisruptionBudget."),
           ("Tight CPU limits causing throttling latency.", "Watch CPU throttling metrics; many teams set CPU requests but no CPU limit.")],
 qa=[("What happens when a container exceeds its memory limit versus its CPU limit?", "Memory is not compressible: exceeding the memory limit gets the container OOM-killed and restarted. CPU is compressible: exceeding the CPU limit makes the kernel throttle the container, which shows up as latency, not crashes.\n\nThat difference is why memory limits are essential while CPU limits need care to avoid hidden latency."),
     ("What is a PodDisruptionBudget?", "A policy stating how many pods of an application may be down at once during voluntary disruptions such as node drains and cluster upgrades (for example minAvailable: 2).\n\nIt stops maintenance from taking down all replicas at the same time; it does not protect against involuntary failures such as a node crash.")]),

"service-mesh": dict(
 terms=[("Service mesh", "An infrastructure layer that handles service-to-service traffic: mTLS, retries, timeouts, routing and telemetry."),
        ("Data plane", "The proxies (for example Envoy) that carry the actual traffic."),
        ("Control plane", "The component that configures the proxies and issues certificates (for example istiod)."),
        ("Sidecar", "A proxy container running next to each application container in the same pod.")],
 pitfalls=[("Adopting a mesh before having the problems it solves.", "Start with libraries and platform basics; adopt a mesh when many services need uniform mTLS, traffic policy and telemetry."),
           ("Configuring retries in both the application and the mesh.", "Choose one layer for retries to avoid multiplied attempts."),
           ("Ignoring the sidecar's resource and latency cost.", "Budget CPU and memory for proxies and measure the added latency (typically sub-millisecond to a few milliseconds per hop).")],
 qa=[("What is sidecar-less (ambient) mesh?", "Istio's ambient mode moves the per-pod sidecar out: a shared per-node proxy (ztunnel) handles mTLS and L4 traffic, and optional waypoint proxies handle L7 features for services that need them. Cilium offers a similar eBPF-based approach.\n\nThe benefit is lower resource overhead and no sidecar injection or restarts; the trade-off is a newer model and different failure domains."),
     ("How does a mesh enable canary releases?", "The mesh routes traffic by weights or headers between versions of the same service, for example 95 percent to v1 and 5 percent to v2, or all requests with a test header to v2. Tools like Flagger or Argo Rollouts shift weights automatically based on metrics and roll back on errors.\n\nBecause routing is done by proxies, the application code does not change.")]),

"config": dict(
 terms=[("Externalized configuration", "Keeping configuration outside the code and image, supplied at deploy or run time."),
        ("ConfigMap", "A Kubernetes object holding non-secret configuration, mounted as files or environment variables."),
        ("Feature flag", "A runtime switch that turns functionality on or off without redeploying."),
        ("Dynamic configuration", "Configuration changes picked up by running services without a restart.")],
 pitfalls=[("Feature flags that are never removed.", "Give each flag an owner and an expiry, and delete it after full rollout."),
           ("Configuration changes with no review or rollback.", "Treat config as code: version it, review it and deploy it through a pipeline."),
           ("Secrets stored in ConfigMaps.", "Use Secrets or a secrets manager with encryption and access control.")],
 qa=[("Why are configuration changes a common cause of outages, and how do you make them safe?", "They often bypass the testing and staged rollout that code changes get, and one bad value can affect every instance at once. Make them safe the same way as code: validation (schemas), review, staged rollout (one region or canary first), automatic health checks and fast rollback.\n\nMany major cloud outages have been triggered by global configuration pushes, which is why progressive config rollout matters."),
     ("What kinds of feature flags exist?", "Release flags (hide unfinished features, short-lived), experiment flags (A/B tests), ops flags or kill switches (turn off expensive features under load) and permission flags (enable features per customer or plan).\n\nThey have different lifetimes and owners, so tracking the kind helps keep flag debt under control.")]),

"deploy-strategies": dict(
 terms=[("Rolling update", "Gradually replacing old instances with new ones."),
        ("Blue-green deployment", "Running two full environments and switching traffic from the old (blue) to the new (green) at once."),
        ("Canary release", "Sending a small share of traffic to the new version and increasing it while metrics stay healthy."),
        ("Expand and contract", "Making backward-compatible schema changes in steps: add the new, migrate, then remove the old.")],
 pitfalls=[("Deploying code and a breaking schema change together.", "Use expand and contract so old and new versions work with the schema during the rollout."),
           ("Canary judged by eye.", "Define automated success metrics (error rate, latency, business KPIs) and roll back automatically."),
           ("Blue-green without handling in-flight work and caches.", "Drain connections, warm caches and plan for long-running jobs before switching.")],
 qa=[("What are the DORA metrics?", "Four measures of delivery performance from the DevOps Research and Assessment research: deployment frequency, lead time for changes, change failure rate and time to restore service.\n\nThey balance speed and stability, and they are a good way to judge whether a microservices setup is actually improving delivery."),
     ("How do you roll back when a release included a database migration?", "Design so you rarely need to: with expand and contract, the old code version still works with the expanded schema, so rolling back is just redeploying the old code. Destructive steps (dropping columns) happen only in a later release, after the new version has proven stable.\n\nIf data was transformed, keep the old data until the contract step, or have a tested forward-fix plan.")]),

"testing": dict(
 terms=[("Test pyramid", "Many fast unit tests, fewer integration tests, and very few end-to-end tests."),
        ("Contract test", "A test that checks a provider still satisfies the expectations (contract) recorded by its consumers, for example with Pact."),
        ("Test double", "A stand-in for a real dependency: stub, mock, fake or spy."),
        ("Testcontainers", "A library that starts real dependencies (databases, brokers) in containers for integration tests.")],
 pitfalls=[("Relying mainly on end-to-end tests across all services.", "They are slow and flaky; push most checks down to unit, component and contract tests."),
           ("Mocks that drift from the real service.", "Use consumer-driven contracts or run the real dependency in Testcontainers."),
           ("No testing in production at all.", "Add synthetic monitoring, canaries and feature-flagged dark launches.")],
 qa=[("What is a component test in microservices?", "A test of one service in isolation, running as a real process with its real database (often via Testcontainers) but with other services replaced by stubs. It checks the service's behaviour through its API without the cost and flakiness of a full environment.\n\nTogether with contract tests it gives most of the confidence of end-to-end tests at a fraction of the cost."),
     ("How do you test asynchronous, event-driven flows?", "Publish an event into a real or containerized broker, then assert on the outcome with a polling wait (for example Awaitility) rather than fixed sleeps. Use contract tests for event schemas too (Pact supports message contracts), and test idempotency by delivering the same event twice.\n\nIn production, trace IDs across events make it possible to verify that flows complete end to end.")]),

"scaling": dict(
 terms=[("Horizontal scaling", "Adding more instances of a service."),
        ("Vertical scaling", "Giving an instance more CPU or memory."),
        ("HPA", "Horizontal Pod Autoscaler: scales pod counts in Kubernetes based on CPU, memory or custom metrics."),
        ("Sharding", "Splitting data across several databases or partitions by a key so each holds a part.")],
 pitfalls=[("Autoscaling stateless services while the database is the bottleneck.", "Find the real bottleneck first; adding app instances can overload a shared database further."),
           ("Scaling on CPU for I/O-bound or queue-driven workloads.", "Scale on queue length, lag or request rate (for example with KEDA)."),
           ("No scale-down stabilization.", "Use cooldowns or stabilization windows to avoid flapping.")],
 qa=[("What is KEDA and when would you use it?", "Kubernetes Event-Driven Autoscaling: it scales deployments on external signals such as Kafka consumer lag, queue depth or cron schedules, and can scale to zero when there is no work.\n\nIt suits consumers and batch workers, whose load is better described by pending work than by CPU."),
     ("How do you scale the database layer in a microservices system?", "In order of effort: optimize queries and indexes, add caching, use read replicas for read-heavy workloads, split data by service (which microservices already do), partition large tables, and finally shard by a key or move to a distributed database.\n\nWrites are the hard part; reads scale much more easily with replicas and caches.")]),

"anti-patterns": dict(
 terms=[("Distributed monolith", "Services that must be deployed together because they are tightly coupled, combining the costs of both styles."),
        ("Chatty services", "Services that exchange many small synchronous calls to complete one operation."),
        ("Shared database anti-pattern", "Several services reading and writing the same tables, coupling their schemas and releases."),
        ("Nanoservices", "Services so small that their overhead outweighs their usefulness.")],
 pitfalls=[("Fixing a distributed monolith by adding more services.", "Merge tightly coupled services back together, then re-split along real business boundaries."),
           ("A shared 'common' library containing domain models.", "Share only technical utilities; each service owns its own domain model."),
           ("Synchronous call chains five or more services deep.", "Collapse the chain, use asynchronous events, or keep local copies of needed data.")],
 qa=[("How do you detect a distributed monolith?", "Signs: services must be released in a specific order or together; one feature change touches many services; services share database tables; an outage in one service takes down most others; and teams need cross-team meetings for routine changes.\n\nThe fix is usually to redraw boundaries around business capabilities and merge services that always change together."),
     ("What is the 'entity service' anti-pattern?", "Creating one service per database entity (CustomerService, AddressService, OrderLineService) that only offers CRUD. Every business operation then needs several synchronous calls, and business logic ends up in the callers.\n\nServices should own business capabilities with behaviour (Checkout, Billing), not thin wrappers around tables.")]),

"system-design": dict(
 terms=[("Idempotent checkout", "A checkout endpoint that uses an idempotency key so double clicks or retries create only one order."),
        ("Reservation", "Temporarily holding stock for an order with an expiry, released if payment fails or times out."),
        ("Back-of-the-envelope estimate", "Quick sizing (requests per second, storage, bandwidth) to justify design choices."),
        ("Read path vs write path", "Designing the high-volume browsing (read) path separately from the correctness-critical ordering (write) path.")],
 pitfalls=[("Jumping to a service list before clarifying requirements.", "Start with functional and non-functional requirements, scale numbers and consistency needs."),
           ("Synchronous calls from checkout to every downstream service.", "Accept the order, return 202, and complete payment, stock and notifications through a saga."),
           ("No story for failure.", "For each component, say what happens when it is slow or down, and how data is reconciled.")],
 qa=[("Do a back-of-the-envelope estimate for the order platform.", "Assume 10 million daily users, 20 page views each, and 2 percent placing an order. Reads: 200 million page views per day, about 2,300 per second on average and perhaps 10 times that at peak (around 23,000 per second), which calls for CDN and caching. Writes: 200,000 orders per day, about 2.3 per second on average, maybe 50 per second at a flash-sale peak, easily handled by a partitioned relational database.\n\nThe numbers show the design priority: the read path needs horizontal scale and caching, the write path needs correctness (idempotency, sagas) more than raw throughput."),
     ("How do you handle a flash sale where demand far exceeds stock?", "Put a queue or virtual waiting room in front of checkout to admit users at a controlled rate, keep stock counters in a fast atomic store (Redis DECR or conditional database updates) to prevent overselling, reserve stock with an expiry, and serve the product page from cache.\n\nRate limit per user to stop bots, and scale the read path ahead of time based on the known event date.")]),
}
