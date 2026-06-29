# Decision records (curated)

The platform is backed by ~40 Architecture Decision Records. Decision-making — *what was
considered, what was chosen, and why* — is the signal worth showing, so here's a curated, distilled
selection (full ADRs aren't all public; some carry lab-specific detail). Each entry: the decision,
the alternatives weighed, and the reasoning.

> The format itself is the habit: every non-trivial choice gets a written record with the rejected
> options and the tradeoff, so the *why* survives the decision.

## Agentic AI tier

**Python tier, not in-JVM (ADR-0035).** Considered keeping agents inside the Spring services.
Chose a separate Python/`uv` tier: Python is the AI mainstream, and model-agnosticism is cleaner
there. Cost: a polyglot boundary. Benefit: the AI stack evolves independently of the platform.

**Model-agnostic `LlmPort` + hand-rolled loops — no LangChain (ADR-0035).** Considered LangChain /
a framework. Chose a thin `Llm` Protocol with per-provider adapters (LiteLLM under it) and
hand-written agent loops. Reasoning: control, debuggability, owning the IP, and no framework churn;
the model/runner becomes a swappable adapter (→ on-prem Ollama in the lab).

**Security baseline *before* features (ADR-0037).** Considered building agent features first and
hardening later. Chose to build the OWASP-LLM-Top-10 enforcement layer (`agent-security`) first and
make every agent depend on it. Reasoning: in a regulated product, retrofitting security onto shipped
agent capability is how you ship vulnerabilities.

**Cite-or-abstain RAG (ADR-0038).** Considered standard "retrieve + generate." Chose to *reject* any
answer that cites an unretrieved source or makes uncited claims, forcing an abstention. Reasoning:
a confident wrong answer with a fake citation is worse than "I don't know" in compliance — and it
caught a real 7B-model fabrication.

**MCP closed allow-list + token propagation (ADR-0039).** Considered MCP's dynamic server discovery
+ a service-account token. Rejected both: dynamic discovery is the tool-poisoning / over-scope risk,
and a service account is the confused-deputy problem. Chose a fixed first-party allow-list with the
caller's bearer propagated and every call traced.

**Agents are tools, not decision-makers (cross-cutting).** The governing constraint: deterministic,
rule-traceable screening/case outcomes; agents only retrieve/draft/propose; a durable trace proves
non-autonomy. Reasoning: "the AI decided" is legally unsaleable to a compliance buyer.

## Platform

**Three-plane service layout (ADR-0031).** Considered a flat service tree and, separately, service
*consolidation* to cut cost. Chose data/operations/tenant planes without consolidating. Reasoning:
plane boundaries make the eventual cloud carve-up clean while keeping one-context-per-service.

**Keycloak Organizations for multi-tenancy (ADR-0019).** Considered realm-per-tenant. Chose KC
Organizations (one realm, org per tenant). Reasoning: realm-per-tenant doesn't scale operationally
(issuer trust, import, upgrades per realm); KC Orgs gives tenant isolation without the per-realm tax.

**Local-as-cloud-mirror; solve locally before migrating (ADR-0024/0025).** Considered building
straight for AWS. Chose to make the Proxmox lab mirror the AWS target shape so migration is a
substrate swap, not a redesign. Reasoning: solve the architecture where iteration is cheap.

**Transactional outbox over dual-write (platform-wide).** Considered emitting events directly from
services. Chose the outbox pattern (event row + domain change in one transaction; async relay).
Reasoning: a broker outage must never leave the DB and the event stream inconsistent.

**Postgres recursive-CTE graph, graph DB deferred (ADR-0032).** Considered a graph database
(Apache AGE / Neo4j) for the relationship graph. Chose Postgres recursive CTEs, with the graph-DB
decision gated on *measured* need. When a perf concern surfaced, it was load-tested and fixed with
indexes + a fan-out cap (p95 1.99s → 1.40s) — deferring the migration on evidence, not guesswork.
See [../architecture.md](../architecture.md#engineering-judgment-measured-not-asserted).

**Explainable, replayable compliance (ADR-0034).** Risk scores expose per-factor contributions;
policy changes can be simulated on historical traffic; watchlist versions are pinned for
time-travel replay. Reasoning: a regulator asks "why this decision, on that date" — the platform
must answer.
