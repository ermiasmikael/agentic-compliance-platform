---
title: "Decision deep-dives — platform & infrastructure"
---

Real decisions from the project, in problem → options-with-pros/cons → choice → tradeoff form.
Distilled from the ADRs (numbers referenced) and rewritten to be public-safe (no infra
addresses, hostnames, credentials, or business figures).

---

## Multi-tenancy: Keycloak Organizations, not realm-per-tenant (ADR-0019)

**Problem.** The starting model — one Keycloak realm holding every tenant's users, isolated only by a
`tenantId` attribute — enforces isolation only in application code (one missing `WHERE` clause from a
leak) and can't deliver per-tenant federation (SAML/OIDC), MFA policy, or branding. The target
segment (individual exporters → mid-market freight forwarders) needs self-service user management and,
eventually, per-org SSO.

**Options.**
- **Status quo (shared realm + attribute).** Pro: already works. Con: every "we need SAML / branded
  login / MFA policy / user management" request becomes a blocker on the first real customer.
- **Realm-per-tenant.** Pro: hard cryptographic isolation, native per-tenant admin. Con: operationally
  absurd at the low end (a realm per hobbyist user); and it forces a new issuer per tenant onto ~28
  services — every signup becomes an N-service config change.
- **Keycloak Organizations (one realm, N orgs).** Pro: native per-org admin scope, per-org SAML, per-org
  branding, with the operational simplicity of one realm. Con: a younger Keycloak feature; some rough
  edges at scale.
- **Custom scoped-admin UI on the shared realm.** Pro: full control. Con: isolation is again *our*
  code (one bug from a leak), and it re-implements for free what Keycloak already ships (SSO, policy,
  email templates).

**Decision.** Keycloak Organizations: one realm, one org per customer, `tenantId` = org id. Tier is a
*plan attribute*, not an auth boundary. A realm carve-out stays available as an escape hatch for a
future regulated customer needing hard isolation — without forcing every customer through that cost.

**Tradeoff accepted.** Betting on a younger KC feature, mitigated by the carve-out escape hatch. Avoids
both the leak-prone shared realm and the operationally untenable realm-per-tenant.

---

## Tenant routing: single hostname, org from the token (ADR-0021)

**Problem.** With one realm to authenticate against, how does the SPA know which tenant to render, and
what URL does each customer see?

**Options.**
- **Per-tenant subdomain (`{tenant}.app…`).** Pro: a "your own URL" sales line. Con: wildcard DNS +
  wildcard cert is heavier ops, and under KC Orgs it buys *nothing* functional — per-org branding comes
  from the login theme regardless of URL. It's cosmetic complexity that's hard to walk back once sold.
- **Per-tenant URL path (`/t/{tenant}/…`).** Pro: single hostname. Con: every route/link must encode
  the tenant, and now the tenant lives in *two* places (URL and token) that can diverge.
- **Single hostname, tenant resolved from the JWT `organization` claim.** Pro: trivial edge config,
  one cert per hostname, no DNS step to onboard (just create the org); one source of truth. Con: no
  "your own URL" talking point.

**Decision.** Single hostname; org context comes from the token post-login. The tenant lives in exactly
one place — the session.

**Tradeoff accepted.** Forgo the vanity-URL sales line (revisit if a regulated customer demands it) for
a materially simpler, single-source-of-truth routing model that survives the eventual cloud move
unchanged.

---

## Local-as-cloud-mirror: decide now, don't defer to migration (ADR-0025)

**Problem.** The platform runs pre-revenue on a private lab with intent to move to AWS later. The
tempting default is "we'll fix that on the cloud."

**Options.**
- **Build now, refactor on AWS.** Pro: expedient locally. Con: migration becomes the moment everything
  gets reconsidered — i.e. a re-architecture, not a move; wrong-shaped artifacts now guarantee it.
- **Build for AWS only, skip the lab investment.** Pro: no double work. Con: no budget pre-revenue, and
  the first real test of the architecture happens in production — the worst possible place.
- **Add a cloud-portability abstraction layer.** Pro: "same code, either substrate." Con: the
  abstractions are themselves work and hide the substrate differences that bite; standard interfaces
  (Postgres, Kafka, OIDC, S3-compatible) already give the portability that matters.
- **Make the lab mirror the cloud target service-for-service.** Pro: migration becomes a substrate
  swap (same images, same env-var shapes, point at managed equivalents, cut DNS); the lab smoke *is*
  the production smoke. Con: requires the discipline to refuse expedient-but-non-portable choices now.

**Decision.** The lab *is* the target architecture on a different substrate. Every architectural
question is decided now, in writing (an ADR), and validated locally; divergences from the cloud target
must be called out explicitly.

**Tradeoff accepted.** More up-front discipline (no "TODO: fix on prod"), bought a migration that's a
rehearsed substrate swap rather than a multi-month rebuild.

---

## No service consolidation pre-migration (ADR-0026)

**Problem.** ~28 services, one per bounded context. Consolidating to ~14 would cut a real chunk off the
monthly cloud baseline. Should cost win?

**Options.**
- **Consolidate to ~14.** Pro: meaningful monthly saving pre-revenue. Con: unwinds the
  one-context-per-service rule that drives the whole architecture (hexagonal layout, schema ownership,
  ArchUnit boundaries, deploy-per-service); breaks the ML rollout pipeline's separate units; co-locates
  conflicting runtime profiles (a sync aggregator + an event-sourced read-model + async report
  generation) in one JVM; couples deploy cadence; and is *asymmetrically hard to reverse*.
- **Consolidate only the "cheap" Phase-5 scaffolds.** Con: those scaffolds become load-bearing as the
  product commercializes; locking their shape now is premature.
- **Scale-to-zero on low-traffic services.** Pro: recovers cost without merging anything. Partially
  adopted for non-hot-path services.
- **Decide after migration, on real traffic.** The right *practice* once on the cloud — but the framing
  question ("consolidate to hit a lower tier?") already has a clear answer: no.

**Decision.** Don't consolidate. The savings are real but trade against architectural integrity, the ML
rollout boundaries, runtime-profile isolation, deploy decoupling, and reversibility. Cost is funded by
customer revenue at migration time, not by compromising the architecture. Use scale-to-zero where it
fits.

**Tradeoff accepted.** A higher pre-revenue baseline, in exchange for keeping the architecture (and the
option to consolidate later) intact. Re-evaluate a *specific* service only if it proves genuinely
uneconomic in production.

---

## Watchlist ingest: split the service + a source-provider plugin pattern (ADR-0013)

**Problem.** One service was doing three incompatible jobs: daily batch ingest from authorities, the
low-latency screening read path, and event publication. They have different runtime profiles, failure
modes, and security boundaries (outbound to the public internet vs. internal-only).

**Options.**
- **Keep the monolith.** Pro: one service. Con: a bursty ingest failure or resource spike can take down
  the screening hot path; adding an authority means touching core code.
- **Split out an ingest service with a per-source plugin SPI.** Pro: ingest failures can't reach the
  read path; a new authority becomes a one-class plugin (`metadata/cron/fetch/parse`); swapping the
  data vendor becomes config. Con: one more service to operate; an eventual-consistency window between
  the source-of-truth store and the search projection.

**Decision.** Split it. Ingest owns outbound fetch + parse + diff + archive + event emission; the
content service becomes a query/projection layer. New authorities are plugins.

**Side decision — name search engine.** Considered Postgres trigram, Elasticsearch, and OpenSearch.
Chose **OpenSearch with a Beider-Morse phonetic analyzer** because transliteration ("Vladimir" /
"Владимир") defeats pure lexical matching, the license fits the stack, and hybrid lexical+vector lives
in one engine. Cost: an OpenSearch component to operate; Postgres `ILIKE` is the graceful-degradation
fallback during an outage.

**Tradeoff accepted.** More moving parts and an eventual-consistency window, in exchange for an isolated
hot path, pluggable sources, and transliteration-tolerant matching.

---

## Relationship graph: Postgres recursive CTEs, graph DB deferred *on evidence* (ADR-0032)

**Problem.** The entity relationship graph (ownership / control edges, for N-hop "indirect exposure"
queries) raised the classic question: does this need a graph database?

**Options.**
- **Adopt a graph DB (Neo4j / Apache AGE) now.** Pro: purpose-built traversal. Con: a new datastore to
  run, back up, secure, and migrate into — a large commitment made on a *hunch* about scale.
- **Postgres recursive CTEs, gate the graph-DB decision on measured need.** Pro: no new datastore;
  reuses the existing operational story. Con: recursive CTEs can get expensive on hub nodes — *if* the
  data demands it.

**Decision.** Postgres recursive CTEs, with the graph-DB decision explicitly conditional on
measurement. When a perf concern surfaced, I instrumented it (a percentile-histogram timer tagged by
operation + hop depth), load-tested it (found worst-case 3-hop p95 at the budget, and that cost was
*fan-out* bound, not depth bound), fixed it cheaply (composite indexes + a per-hop fan-out cap), and
**re-measured** (p95 ~1.99s → ~1.40s). The migration stayed deferred — on evidence.

**Tradeoff accepted.** Recursive CTEs aren't a graph engine, but the measured loop showed they don't
need to be yet. The judgment on display: *instrument → measure → cheapest effective fix → re-measure →
defer the big rewrite until the data demands it.*
([architecture](/architecture/platform-overview/))

---

## Edge hardening: skip oauth2-proxy, per-vhost certs and cookies (ADR-0016)

**Problem.** Before exposing the SPAs publicly: where does TLS terminate, do we add an auth proxy, and
how are cookies scoped between two SPAs on different subdomains?

**Options.**
- **Deploy oauth2-proxy in front of the SPAs.** Pro: enforces a valid session before serving the
  bundle. Con: the SPA bundle is *public JavaScript* — hiding it protects nothing (secrets live in
  backends, gated by per-service JWT validation); it adds cookies to scope, a health endpoint, and a
  rotation playbook for little value floor.
- **Skip it; rely on per-service JWT validation.** Pro: less to operate, simpler cookie story. Con:
  revisit if a static asset ever needs auth-gating (e.g. a customer PDF from object storage).
- **Wildcard cert vs. per-vhost certs.** A wildcard is marginally cheaper to manage, but a per-vhost
  cert means compromise of one key doesn't grant the other vhost; renewal is automated either way, so
  the ops argument for wildcard mostly evaporates.
- **Parent-domain cookie vs. per-vhost cookie.** A parent-domain cookie enables cross-SPA SSO but risks
  an admin token leaking to the tenant SPA via a misconfigured domain — a real privilege-leak.

**Decision.** Skip oauth2-proxy (backends already validate JWTs); per-vhost certs; per-vhost cookies
with `SameSite=Lax`; TLS terminates at the reverse proxy; internal service-to-service stays plain HTTP
inside the trust boundary.

**Tradeoff accepted.** No cross-SPA SSO and a future revisit if static assets need gating, in exchange
for a smaller attack surface and a much simpler cookie model — because the value floor of the proxy was
low given JWT-at-every-service.

---

## Honourable mentions (catalogued, not expanded here)

These were real options-weighed decisions too; see [the catalog](/decisions/) for the full set:

- **Dedicated inference VM + workload-class split** (ADR-0017) — isolate LLM/ML compute from the
  stateless business services; accepted in principle, *deferred* until hardware, with a simulated-LLM
  fallback so nothing blocked.
- **Platform-admin app + second realm split** (ADR-0014) — two diverging audiences → two apps + two
  realms now, paying ~2× ingress/CI overhead to avoid a painful realm migration later.
- **Tenant + member lifecycle with grace windows** (ADR-0028) — *tombstone, never hard-delete* members,
  because a denied-party-screening audit trail must still name who decided a case three years ago.
- **Source provenance + tier model** (ADR-0029) — one unified table with a per-entity provenance array
  ("OFAC direct, corroborated by an aggregator") rather than separate tables per source tier, to keep
  the screening hot path a single query.
- **Two-track product strategy** (ADR-0033) and **dynamic issuer trust deferral** (ADR-0020) — choosing
  *what not to build yet*, with explicit activation triggers.
