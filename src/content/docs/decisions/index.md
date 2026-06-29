---
title: "Decision records"
---

The platform is backed by ~40 Architecture Decision Records. The decision-making — *what was
considered, what was chosen, and why* — is the signal worth showing, so this section is built to
demonstrate the rigor, not just the conclusions.

> **The habit:** every non-trivial choice got a written record with the rejected options, their
> pros/cons, and the tradeoff accepted — so the *why* survives the decision. That discipline is the
> point as much as any individual call.

## How to read this

- **[`ai-tier.md`](/decisions/ai-tier/)** — deep-dives on the AI / agentic decisions, each as
  *problem → options-with-pros/cons → choice → tradeoff*.
- **[`platform.md`](/decisions/platform/)** — the same treatment for the platform & infrastructure decisions.
- The **catalog below** lists the full decision set, names the alternatives each one weighed, and links
  to the deep-dive where one exists. (Full original ADRs aren't all public — some carry lab-specific
  detail; these are distilled and sanitized.)

---

## Catalog

### AI / agentic tier

| # | Decision | Alternatives weighed | Deep-dive |
|---|---|---|---|
| 0035 | Python agent tier, model-agnostic port, **no LangChain** | in-JVM (Spring AI) · a Python framework · hand-rolled behind a port | [ai-tier](/decisions/ai-tier/#python-agent-tier-model-agnostic-no-langchain-adr-0035) |
| 0015 | RAG + tool-use **over fine-tuning** a model | train/fine-tune a specialized LLM · RAG + tools | [ai-tier](/decisions/ai-tier/#rag--tool-use-over-fine-tuning-a-model-adr-0015) |
| 0037 | Agent **security baseline before features** | features-first-harden-later · baseline-first | [ai-tier](/decisions/ai-tier/#security-baseline-before-agent-features-adr-0037) |
| 0038 | **Cite-or-abstain** as a hard output contract | trust-the-model grounding · reject-if-ungrounded | [ai-tier](/decisions/ai-tier/#cite-or-abstain-as-a-hard-output-contract-adr-0038) |
| 0039 | MCP: **closed allow-list + token propagation** | dynamic discovery vs allow-list · service account vs user bearer | [ai-tier](/decisions/ai-tier/#mcp-closed-allow-list--token-propagation-adr-0039) |
| 0018 | **Write-capable** agent tools + provable non-autonomy | flag on existing event vs distinct write event; layered authz | [ai-tier](/decisions/ai-tier/#write-capable-agent-tools--provable-non-autonomy-adr-0018) |
| 0036 | Export-drafter as the **thin first agent** | a richer first agent vs a minimal prose-only, single-tool, HITL one | — |
| 0009/0011/0012 | ML rollout: **shadow → canary → live**, gated + reversible | binary on/off vs graduated modes; deterministic vs random canary | [ai-tier](/decisions/ai-tier/#ml-rollout-shadow--canary--live-gated-and-reversible-adr-0009--0011--0012) |
| 0010 | **CPU-first** inference + lightweight registry MVP | GPU inference vs CPU-first; feature-rich vs lightweight | — |

### Platform & infrastructure

| # | Decision | Alternatives weighed | Deep-dive |
|---|---|---|---|
| 0019 | Multi-tenancy via **Keycloak Organizations** | shared realm · realm-per-tenant · KC Orgs · custom scoped UI | [platform](/decisions/platform/#multi-tenancy-keycloak-organizations-not-realm-per-tenant-adr-0019) |
| 0021 | Tenant routing: **single hostname**, org from token | per-tenant subdomain · per-tenant path · single hostname | [platform](/decisions/platform/#tenant-routing-single-hostname-org-from-the-token-adr-0021) |
| 0025 | **Local-as-cloud-mirror**: decide now, don't defer | build-now-refactor-later · AWS-only · abstraction layer · mirror | [platform](/decisions/platform/#local-as-cloud-mirror-decide-now-dont-defer-to-migration-adr-0025) |
| 0026 | **No service consolidation** pre-migration | consolidate to ~14 · partial · scale-to-zero · decide-later | [platform](/decisions/platform/#no-service-consolidation-pre-migration-adr-0026) |
| 0013 | Watchlist **ingest split** + source-provider plugin SPI | monolith vs split; trigram vs Elasticsearch vs OpenSearch BMPM | [platform](/decisions/platform/#watchlist-ingest-split-the-service--a-source-provider-plugin-pattern-adr-0013) |
| 0032 | Relationship graph: **Postgres CTEs**, graph DB deferred *on evidence* | graph DB now vs CTEs + measure | [platform](/decisions/platform/#relationship-graph-postgres-recursive-ctes-graph-db-deferred-on-evidence-adr-0032) |
| 0016 | Edge hardening: **skip oauth2-proxy**, per-vhost certs/cookies | deploy proxy vs skip; wildcard vs per-vhost; cookie scope | [platform](/decisions/platform/#edge-hardening-skip-oauth2-proxy-per-vhost-certs-and-cookies-adr-0016) |
| 0014 | Platform-admin **app + second realm split** | one codebase/realm vs two apps + two realms | [platform](/decisions/platform/#honourable-mentions-catalogued-not-expanded-here) |
| 0017 | Dedicated **inference VM** + workload-class split (deferred) | all-on-one-host vs dedicated ML host | [platform](/decisions/platform/#honourable-mentions-catalogued-not-expanded-here) |
| 0028 | Tenant/member lifecycle: **tombstone, never hard-delete** | hard-delete · 30/60/90-day grace · disable-flag-only | [platform](/decisions/platform/#honourable-mentions-catalogued-not-expanded-here) |
| 0029 | Source **provenance + tier model** (unified table) | separate tables per tier vs one table + provenance array | [platform](/decisions/platform/#honourable-mentions-catalogued-not-expanded-here) |
| 0024 | AWS target architecture (substrate map) | lift-and-shift EC2 · full serverless · stay-on-lab · managed-services map | — |
| 0027 | Public exposure: **DNS-only + TLS at the reverse proxy** | CDN-proxy modes · TLS at firewall · double-hop TLS | — |
| 0020 | Dynamic issuer trust **deferred** with an activation trigger | build-now · identity-brokering · static-list-now | — |
| 0022 | Tenant signup: **self-service + operator-driven**, both | operator-only · self-service-only · magic-link · temp-password | — |
| 0023 | Tenant team-management: **custom UI for the 95%** | embed KC console · custom-everything · direct-to-KC-API | — |
| 0031 | **Three-plane** architecture (data / operations / tenant) | flat tree · consolidation · planes-as-labels | — |
| 0033 | **Two-track** product strategy (operations + intelligence data) | single-track focus · parallel two-track | — |

> The "no deep-dive" rows are real options-weighed ADRs too; they're catalogued here for breadth and
> distilled in the deep-dive files where they're most instructive (several appear under *honourable
> mentions* in [platform.md](/decisions/platform/#honourable-mentions-catalogued-not-expanded-here)).

---

## A few patterns worth naming

Reading across the set, the same judgment shows up repeatedly:

- **Defer the expensive option behind an explicit trigger, not a vibe.** Graph DB (0032), dynamic
  issuer trust (0020), Tier-A direct ingest (0029/0030), the dedicated ML VM (0017), service
  consolidation (0026) — each was *decided* to wait, with the condition that would change the answer
  written down.
- **Decide on evidence where you can measure.** The graph-perf call (0032) was load-tested, not argued.
- **In a compliance product, auditability beats convenience.** Tombstoning over hard-delete (0028),
  provable agent non-autonomy (0018), cite-or-abstain (0038), provenance arrays (0029).
- **Don't pay for hypothetical futures — but don't foreclose them either.** Single-hostname routing
  (0021) keeps the carve-out option; no-consolidation (0026) keeps the consolidate-later option.
