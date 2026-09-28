# Additions for Fundamentals and Communication topics.
# Each topic: terms (term, definition), pitfalls (mistake, fix), qa (question, answer; blank line = new paragraph).
EXTRA = {

"what-are-microservices": dict(
 terms=[("Microservice", "An independently deployable service that owns one business capability and its data, and talks to others only through APIs or events."),
        ("Independent deployability", "The ability to release one service to production without coordinating a release of any other service. The single best test of whether you really have microservices."),
        ("Conway's Law", "Organizations design systems that mirror their communication structure, so service boundaries tend to follow team boundaries."),
        ("Two-pizza team", "Amazon's rule of thumb for a team small enough to be fed by two pizzas; each such team owns a few services end to end.")],
 pitfalls=[("Starting a new product with microservices before the domain is understood.", "Start with a well-modularized monolith and extract services once boundaries and scaling needs are clear."),
           ("Splitting by technical layer (a UI service, a logic service, a data service).", "Split by business capability, so one feature change touches one service."),
           ("Counting services as a measure of progress.", "Measure deployment frequency, lead time and failure rate; fewer, well-bounded services beat many chatty ones.")],
 qa=[("How do you know a microservices migration is actually working?", "Look at delivery and reliability metrics, not architecture diagrams: deployment frequency per team, lead time from commit to production, change failure rate and time to restore (the four DORA metrics). If teams still coordinate releases, share a database, or need a meeting to change an API, the split has not delivered independence.\n\nAlso check cost: cloud spend, on-call load and the number of cross-service incidents. A migration that doubles operational load without faster delivery is not working."),
     ("What organizational changes do microservices require?", "Teams must own services end to end (build, run, on-call), because independent deployment only works when the team that changes a service also operates it. That needs platform support (CI/CD templates, observability, service scaffolding) so each team does not rebuild infrastructure, and clear API ownership and versioning rules.\n\nWithout the org change you get a distributed monolith: many services, one release train.")]),

"monolith-soa-micro": dict(
 terms=[("Monolith", "One deployable unit containing all modules of the application, usually sharing one database."),
        ("Modular monolith", "A single deployable with strict internal module boundaries (separate packages, no shared tables, explicit interfaces), often the best starting point."),
        ("SOA", "Service-Oriented Architecture: enterprise-wide services integrated through a central Enterprise Service Bus that often holds routing and business logic."),
        ("ESB", "Enterprise Service Bus: middleware that routes, transforms and orchestrates messages between services; the 'smart pipe' that microservices avoid.")],
 pitfalls=[("Treating 'monolith' as a synonym for 'legacy mess'.", "A clean modular monolith is a valid, often better, architecture; the problem is poor modularity, not deployment granularity."),
           ("Re-creating an ESB with a shared gateway full of business rules.", "Keep gateways and brokers dumb (routing, auth, transport) and put business logic in services."),
           ("Migrating everything at once (big-bang rewrite).", "Extract incrementally with the strangler fig pattern, one capability at a time.")],
 qa=[("Amazon Prime Video moved one system from microservices back to a monolith. What is the lesson?", "Their video-quality monitoring pipeline was built from many serverless functions passing data through storage, and the per-call and data-transfer costs dominated. Merging the stages into one process cut cost sharply.\n\nThe lesson is not that microservices are wrong, but that boundaries should follow the cost and coupling of the workload. Components that exchange large amounts of data on every request usually belong in one process."),
     ("How would you decide between a modular monolith and microservices for a new product?", "Default to a modular monolith when the team is small, the domain is still changing, and there is no strong independent scaling or compliance need. Choose microservices when several teams need to release independently, parts of the system have very different scaling or reliability needs, or you need technology isolation.\n\nEither way, enforce module boundaries from day one (no cross-module table access), so extracting a service later is a deployment change, not a rewrite.")]),

"principles": dict(
 terms=[("Loose coupling", "Services can change and deploy without changing each other, because they depend only on stable contracts."),
        ("High cohesion", "Code that changes together lives together, so one business change touches one service."),
        ("Twelve-Factor App", "A set of 12 practices for cloud-native apps, such as config in the environment, stateless processes and disposability."),
        ("Disposability", "Processes start fast and shut down gracefully, so they can be scaled, moved or replaced at any time.")],
 pitfalls=[("Storing session state in service memory.", "Keep services stateless: put sessions in a shared store (Redis) or in signed tokens."),
           ("Baking environment-specific config into images.", "Build one image and inject config at deploy time (environment variables, config service, secrets manager)."),
           ("Ignoring graceful shutdown.", "Handle SIGTERM: stop accepting requests, finish in-flight work and close connections before exiting.")],
 qa=[("What does 'design for failure' mean in practice?", "Assume every network call can be slow, fail or return garbage. Put timeouts on every call, retry only idempotent operations with backoff, add circuit breakers and fallbacks, and make each service degrade gracefully instead of failing completely.\n\nThen prove it: chaos experiments that kill instances or inject latency should cause bounded, visible degradation, not an outage."),
     ("How does statelessness help scaling and deployments?", "When no request depends on which instance served the previous one, any instance can handle any request. That lets the platform add or remove instances freely (autoscaling), replace them during rolling deployments without draining user sessions, and restart crashed instances without data loss.\n\nState still exists, it just lives in databases, caches and queues that are designed to be durable and shared.")]),

"ddd": dict(
 terms=[("Bounded context", "A boundary within which a domain model and its language are consistent; the same word (Customer) may mean different things in different contexts."),
        ("Ubiquitous language", "The shared vocabulary that developers and domain experts use inside one bounded context, reflected directly in code."),
        ("Aggregate", "A cluster of objects treated as one unit for changes, with a single root that enforces its invariants; the unit of transactional consistency."),
        ("Context map", "A diagram of bounded contexts and the relationships between them (customer/supplier, conformist, anti-corruption layer).")],
 pitfalls=[("One service per entity (Customer service, Order service, Address service).", "Model around business capabilities and aggregates, not tables; entity services become chatty and tightly coupled."),
           ("Huge aggregates that lock too much data.", "Keep aggregates small and reference other aggregates by ID; use eventual consistency between them."),
           ("Letting another system's model leak into yours.", "Use an anti-corruption layer that translates at the boundary.")],
 qa=[("What is the difference between a bounded context and a microservice?", "A bounded context is a modeling boundary: one consistent model and language. A microservice is a deployment boundary. Often one bounded context maps to one service, but a large context can be split into several services for scaling, and a small team may keep several contexts in one deployable.\n\nThe rule to keep: a service should not span two bounded contexts, because it would have to reconcile two meanings of the same terms."),
     ("How do you run an event storming session to find service boundaries?", "Bring domain experts and engineers together, and put domain events (Order Placed, Payment Captured) on a timeline in orange stickies. Add the commands that cause them, the actors, the policies that react, and the aggregates that handle commands.\n\nClusters of events and aggregates that share language and change together suggest bounded contexts; places where the language shifts or a hand-off occurs suggest boundaries between services.")]),

"decomposition": dict(
 terms=[("Strangler fig", "Incrementally replacing a monolith by routing individual features to new services until the old system can be removed."),
        ("Decompose by business capability", "Split services along what the business does (billing, shipping) rather than technical layers."),
        ("Decompose by subdomain", "Split along DDD subdomains: core (competitive advantage), supporting and generic."),
        ("Change Data Capture (CDC)", "Streaming row-level changes from a database's transaction log (for example with Debezium) to keep other systems in sync.")],
 pitfalls=[("Extracting the service but leaving it on the monolith's database.", "Move data ownership too: give the new service its own schema and sync legacy consumers through events or CDC."),
           ("Starting with the most central, most coupled module.", "Start with an edge capability that has few dependencies and clear value, to learn the process safely."),
           ("No way to roll back routing.", "Put a routing layer (gateway or proxy) in front so traffic can switch back to the monolith instantly.")],
 qa=[("Walk through extracting one feature from a monolith safely.", "1. Put a proxy or gateway in front of the monolith. 2. Build the new service behind a feature flag, with its own data store. 3. Sync data: backfill history, then keep it current with CDC or dual reads. 4. Shadow traffic to compare responses without affecting users. 5. Shift a small percentage of real traffic, watch metrics, then ramp up. 6. Make the new service the source of truth and remove the old code and tables.\n\nEach step is reversible until the last one, which is what makes the migration safe."),
     ("How do you handle a feature that needs data from both the monolith and the new service during migration?", "Prefer having one side own the data and expose it through an API or events, never both writing the same table. During the transition the new service can call the monolith through an anti-corruption layer, or the monolith can consume events from the new service.\n\nAvoid distributed transactions; use sagas or reconcile asynchronously, and make the temporary coupling explicit so it can be removed later.")]),

"rest-grpc": dict(
 terms=[("REST", "Resource-oriented HTTP APIs using standard verbs (GET, POST, PUT, DELETE), status codes and usually JSON."),
        ("gRPC", "An RPC framework using HTTP/2 and Protocol Buffers, with generated clients, streaming and deadlines built in."),
        ("Protocol Buffers", "A compact binary, schema-first serialization format; fields are identified by numbers, which enables backward-compatible evolution."),
        ("Deadline", "In gRPC, the absolute time by which a call must finish; propagated to downstream calls so the whole chain respects one budget.")],
 pitfalls=[("Exposing gRPC directly to browsers.", "Browsers cannot speak native gRPC; use gRPC-Web, a REST or GraphQL gateway, or keep gRPC for internal traffic."),
           ("Reusing or renumbering protobuf field numbers.", "Never reuse a field number; mark removed fields as reserved."),
           ("Chatty APIs that need many calls to render one page.", "Design coarse-grained endpoints or add an aggregation layer (BFF).")],
 qa=[("How do you evolve a gRPC or protobuf API without breaking clients?", "Only make additive changes: add new fields with new numbers, add new RPC methods, and keep old ones until clients migrate. Never change a field's number or type, and mark deleted fields as reserved so they are not reused.\n\nFor breaking changes, create a new package version (v2) and run both side by side. Old clients ignore unknown fields, which is what makes additive changes safe."),
     ("What is HTTP/2 multiplexing and why does it matter for gRPC?", "HTTP/2 carries many concurrent request and response streams over one TCP connection, interleaving their frames. gRPC relies on it to run many calls and long-lived streams without opening a connection per call.\n\nA side effect is that connection-level (L4) load balancing does not spread load well, because one connection carries all of a client's calls; gRPC needs request-level (L7) load balancing, via a proxy, service mesh or client-side balancing.")]),

"async-messaging": dict(
 terms=[("Message broker", "Middleware that stores and delivers messages between producers and consumers (Kafka, RabbitMQ, SQS)."),
        ("Topic and partition", "In Kafka, a topic is a named stream split into partitions; order is guaranteed only within a partition."),
        ("Consumer group", "A set of consumers that share the work of a topic; each partition is read by one consumer in the group."),
        ("At-least-once delivery", "Every message is delivered one or more times; duplicates are possible, so consumers must be idempotent.")],
 pitfalls=[("Assuming messages arrive exactly once and in global order.", "Design idempotent consumers and choose a partition key that orders what really needs ordering (for example the order ID)."),
           ("Poison messages blocking a queue forever.", "Retry a bounded number of times, then move the message to a dead letter queue and alert."),
           ("Putting large payloads on the bus.", "Send a reference (URL or ID) to data in object storage, keeping messages small.")],
 qa=[("What is consumer lag and how do you act on it?", "Consumer lag is how far a consumer group is behind the latest offset in each partition. Rising lag means consumers process slower than producers write.\n\nResponses: scale out consumers (up to the number of partitions), increase partitions for future throughput, speed up processing (batching, fewer synchronous calls), and alert on lag in time rather than messages, because '10 minutes behind' is what the business cares about."),
     ("Events vs commands: what is the difference?", "A command asks one specific service to do something (ChargePayment) and can be rejected. An event states a fact that already happened (PaymentCharged), is published to anyone interested, and cannot be rejected.\n\nEvents give loose coupling because the publisher does not know its consumers; commands make responsibility explicit. Naming reflects this: commands are imperative, events are past tense.")]),

"api-gateway": dict(
 terms=[("API gateway", "A single entry point that routes external requests to services and handles cross-cutting concerns like authentication, rate limiting and TLS."),
        ("Edge service", "Any component at the boundary between the internet and internal services (gateway, CDN, WAF, load balancer)."),
        ("Request aggregation", "Combining calls to several services into one response for the client."),
        ("WAF", "Web Application Firewall: filters malicious HTTP traffic such as SQL injection or bot attacks before it reaches services.")],
 pitfalls=[("Putting business logic in the gateway.", "Keep the gateway to routing, auth, limits and translation; business rules belong in services."),
           ("One gateway team as a bottleneck for every route change.", "Use declarative, self-service route configuration owned by service teams, or per-domain gateways."),
           ("Gateway timeouts longer than the client's.", "Set gateway timeouts slightly below client timeouts and propagate deadlines downstream.")],
 qa=[("How does authentication typically work at the gateway?", "The gateway validates the incoming credential (usually a JWT from an identity provider): signature, issuer, audience and expiry. It rejects invalid requests early and forwards the verified identity to services, either the original token or a trimmed internal token with the claims services need.\n\nServices still enforce authorization for their own resources, because the gateway cannot know every business rule (zero trust: do not rely only on the perimeter)."),
     ("How do you scale and operate a gateway for high traffic?", "Run it stateless behind a load balancer across availability zones, autoscale on CPU and connections, and keep shared state (rate-limit counters) in a fast store like Redis.\n\nPut a CDN in front for cacheable content, enable connection reuse to backends, and monitor its own p99 latency and error rate separately from services, since a slow gateway looks like every service being slow.")]),

"bff": dict(
 terms=[("Backend for Frontend (BFF)", "A backend built for one specific client type (web, mobile, partner) that shapes APIs for that client's needs."),
        ("Over-fetching", "Receiving more data than the client needs, wasting bandwidth, especially on mobile."),
        ("Under-fetching", "Needing several calls to get enough data for one screen."),
        ("GraphQL", "A query language that lets clients request exactly the fields they need from a schema, often used as a BFF layer.")],
 pitfalls=[("A BFF per client that duplicates business logic.", "Keep BFFs to composition and formatting; put business rules in domain services."),
           ("One shared 'BFF' that serves every client.", "That is a general gateway again; create a BFF per client experience and let the owning frontend team maintain it."),
           ("BFF calling services sequentially.", "Fan out calls in parallel with timeouts and partial-response fallbacks.")],
 qa=[("Who should own a BFF?", "The team that owns the frontend it serves. The point of a BFF is that the web team can change the web API shape at the same speed as the web UI, without waiting on a central backend team.\n\nDomain services stay owned by backend teams, and the BFF depends on their stable contracts."),
     ("How does a BFF handle a slow or failing downstream service?", "Call downstream services in parallel with per-call timeouts, and design the response so optional parts can be missing: the product page still renders if recommendations time out.\n\nUse circuit breakers and cached fallbacks for non-critical data, and return clear partial-content markers so the client can show placeholders instead of an error page.")]),

"service-discovery": dict(
 terms=[("Service registry", "A database of available service instances and their network locations (Consul, Eureka, etcd, Kubernetes API)."),
        ("Self-registration", "Each instance registers itself with the registry on start-up and deregisters on shutdown."),
        ("Third-party registration", "The platform (for example Kubernetes) registers and removes instances automatically."),
        ("DNS-based discovery", "Resolving a service name to instance addresses via DNS, as Kubernetes Services do.")],
 pitfalls=[("Caching resolved addresses forever.", "Respect TTLs and refresh; stale addresses send traffic to terminated instances."),
           ("Registering instances before they are ready.", "Register or mark ready only after readiness checks pass."),
           ("Hard-coding hostnames in configuration.", "Use logical service names resolved by discovery.")],
 qa=[("How does service discovery work in Kubernetes?", "A Service object gives a stable virtual IP and DNS name (orders.default.svc.cluster.local). The control plane tracks the pods matching the Service's label selector in EndpointSlices, and kube-proxy (or a CNI like Cilium) routes traffic to the ready pods.\n\nPods that fail readiness probes are removed from the endpoints automatically, so discovery and health are linked."),
     ("What is a headless service and when is it used?", "A Kubernetes Service with no cluster IP (clusterIP: None). DNS returns the individual pod IPs instead of one virtual IP.\n\nIt is used when clients need to reach specific pods, for example StatefulSet members of a database cluster (kafka-0, kafka-1), or when the client does its own load balancing, as some gRPC clients do.")]),

"load-balancing": dict(
 terms=[("L4 load balancer", "Balances at the transport layer (TCP or UDP connections) without looking at HTTP content."),
        ("L7 load balancer", "Balances individual HTTP requests and can route on path, headers or cookies."),
        ("Least connections", "Sends each new request to the instance with the fewest active connections."),
        ("Power of two choices", "Pick two instances at random and send to the less loaded one; nearly as good as global least-loaded with far less coordination.")],
 pitfalls=[("Round-robin across instances of very different capacity.", "Use weighted or least-connections balancing."),
           ("Balancing long-lived connections (gRPC, WebSocket) at L4.", "Balance at L7 per request, or periodically recycle connections."),
           ("No health checks, so dead instances keep receiving traffic.", "Combine active health checks with passive outlier detection (eject instances that return errors).")],
 qa=[("What is outlier detection?", "Passive health checking: the load balancer watches real responses and temporarily ejects an instance that returns too many errors or is too slow, then gradually lets traffic back.\n\nIt catches problems active health checks miss (an instance that passes /health but fails real requests), and is available in Envoy, Istio and many cloud load balancers."),
     ("Where does load balancing happen in a typical microservices request?", "Usually at several layers: DNS or anycast spreads traffic across regions, a cloud L4/L7 load balancer spreads it across gateway instances, the gateway or ingress balances to services, and inside the cluster kube-proxy or a sidecar proxy balances between pods.\n\nEach layer needs its own health checks and timeouts, and client-side balancing is common for internal gRPC traffic.")]),
}
