---
title: Platform architecture overview
description: The hexagonal, event-driven, multi-tenant architecture behind the DPS screening platform.
sidebar:
  order: 1
---

DPS is a multi-tenant, event-driven SaaS platform for global trade-compliance
screening: it screens entities — people, companies, vessels, aircraft — against
sanctions watchlists, PEP databases, and adverse-media feeds, and manages the
full lifecycle of the compliance cases that result.

## Shape at a glance

- **~30 microservices**, each a strict **Hexagonal + DDD** bounded context.
- **Event-first** communication over a Kafka-compatible bus (Redpanda).
- **Java 21 / Spring Boot 3** backend; **React/TypeScript** SPAs; a **Python**
  agent tier for AI.
- **Schema-first**: every event is a JSON contract authored *before* code.
- Self-hosted on Proxmox today, with an AWS target (ECS Fargate + RDS +
  MSK/OpenSearch) designed so migration is a substrate swap, not a rewrite.

## How a screening flows

A request enters through a channel, gets matched and scored, and fans out over
the event bus — each downstream service reacting to events rather than being
called. Audit subscribes to *everything*.

<figure class="diagram">
<svg role="img" aria-label="A screening request enters from channels into the screening-engine, which reads watchlist-content and policy-engine, then publishes events to the Redpanda event bus; the bus fans out to scoring-engine, case-management, analytics, and notification, while audit-service subscribes to every topic." viewBox="0 0 920 480" width="100%" style="height:auto;max-width:920px">
  <defs>
    <marker id="f-ah" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-gray-4)"/></marker>
    <marker id="f-aha" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-accent)"/></marker>
  </defs>
  <rect x="350" y="22" width="220" height="46" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/>
  <text x="460" y="42" font-size="14.5" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Channels</text>
  <text x="460" y="58" font-size="11.5" fill="var(--sl-color-gray-3)" text-anchor="middle">Ad-hoc UI · API · Batch</text>
  <line x1="460" y1="68" x2="460" y2="104" stroke="var(--sl-color-gray-4)" stroke-width="1.6" marker-end="url(#f-ah)"/>
  <rect x="350" y="108" width="220" height="50" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/>
  <text x="460" y="129" font-size="14.5" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">screening-engine</text>
  <text x="460" y="145" font-size="11.5" fill="var(--sl-color-gray-3)" text-anchor="middle">5-tier match + ML augment</text>
  <rect x="60" y="110" width="200" height="46" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/>
  <text x="160" y="130" font-size="14.5" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">watchlist-content</text>
  <text x="160" y="146" font-size="11.5" fill="var(--sl-color-gray-3)" text-anchor="middle">BMPM search index</text>
  <rect x="660" y="110" width="200" height="46" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/>
  <text x="760" y="130" font-size="14.5" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">policy-engine</text>
  <text x="760" y="146" font-size="11.5" fill="var(--sl-color-gray-3)" text-anchor="middle">thresholds · jurisdictions</text>
  <line x1="350" y1="133" x2="268" y2="133" stroke="var(--sl-color-gray-4)" stroke-width="1.6" stroke-dasharray="5 4" marker-end="url(#f-ah)"/>
  <line x1="660" y1="133" x2="578" y2="133" stroke="var(--sl-color-gray-4)" stroke-width="1.6" stroke-dasharray="5 4" marker-end="url(#f-ah)"/>
  <text x="312" y="126" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">reads</text>
  <text x="616" y="126" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">reads</text>
  <line x1="460" y1="158" x2="460" y2="204" stroke="var(--sl-color-accent)" stroke-width="1.6" marker-end="url(#f-aha)"/>
  <text x="470" y="184" font-size="11" fill="var(--sl-color-accent)" text-anchor="start">publishes events</text>
  <rect x="60" y="208" width="800" height="54" rx="10" fill="var(--sl-color-accent-low)" stroke="var(--sl-color-accent)"/>
  <text x="460" y="230" font-size="15" font-weight="700" fill="var(--sl-color-accent-high)" text-anchor="middle">Redpanda event bus · DpsEventEnvelope</text>
  <text x="460" y="248" font-size="11.5" fill="var(--sl-color-accent-high)" text-anchor="middle">schema-first · idempotent consumers · transactional outbox</text>
  <g font-size="14.5" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">
    <rect x="60" y="322" width="178" height="50" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/>
    <text x="149" y="343">scoring-engine</text>
    <rect x="254" y="322" width="178" height="50" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/>
    <text x="343" y="343">case-management</text>
    <rect x="448" y="322" width="178" height="50" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/>
    <text x="537" y="343">analytics</text>
    <rect x="642" y="322" width="178" height="50" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/>
    <text x="731" y="343">notification</text>
  </g>
  <g font-size="11.5" fill="var(--sl-color-gray-3)" text-anchor="middle">
    <text x="149" y="361">explainable score</text>
    <text x="343" y="361">SLA · four-eyes</text>
    <text x="537" y="361">KPIs · read models</text>
    <text x="731" y="361">alerts · digests</text>
  </g>
  <g stroke="var(--sl-color-gray-4)" stroke-width="1.6" marker-end="url(#f-ah)">
    <line x1="149" y1="262" x2="149" y2="318"/>
    <line x1="343" y1="262" x2="343" y2="318"/>
    <line x1="537" y1="262" x2="537" y2="318"/>
    <line x1="731" y1="262" x2="731" y2="318"/>
  </g>
  <rect x="60" y="416" width="800" height="48" rx="10" fill="none" stroke="var(--sl-color-accent)" stroke-dasharray="2 4"/>
  <text x="460" y="445" font-size="13.5" font-weight="600" fill="var(--sl-color-accent-high)" text-anchor="middle">audit-service — immutable, append-only · subscribes to every topic</text>
  <path d="M58,235 L30,235 L30,440 L58,440" fill="none" stroke="var(--sl-color-accent)" stroke-width="1.4" marker-end="url(#f-aha)"/>
</svg>
<figcaption>One screening request, fanned out over the bus. Downstream services react to events; nothing is orchestrated by a central caller.</figcaption>
</figure>

A few rules keep the bus trustworthy: the JSON **schema lands first**; every
consumer is **idempotent** (duplicate delivery is expected); consumers hold **no
business logic and make no HTTP calls** — they delegate or publish a follow-up
event; and a **transactional outbox** commits each domain change and its event in
one transaction, so a broker outage can never leave them out of sync.

## Hexagonal, enforced — not aspirational

Every service follows the same package shape, and the dependency rule isn't a
guideline — it's checked mechanically in CI with **ArchUnit**.

<figure class="diagram">
<svg role="img" aria-label="Hexagonal dependency rule: api depends on application, application depends on domain, and infrastructure depends on domain. The domain depends on nothing. Enforced by ArchUnit in CI." viewBox="0 0 900 220" width="100%" style="height:auto;max-width:760px">
  <defs>
    <marker id="h-ah" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-gray-4)"/></marker>
    <marker id="h-aha" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-accent)"/></marker>
  </defs>
  <text x="450" y="32" font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">dependencies point inward — domain depends on nothing</text>
  <rect x="40" y="62" width="175" height="70" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/>
  <text x="127" y="92" font-size="14.5" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">api</text>
  <text x="127" y="110" font-size="11.5" fill="var(--sl-color-gray-3)" text-anchor="middle">HTTP adapter</text>
  <rect x="255" y="62" width="195" height="70" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/>
  <text x="352" y="92" font-size="14.5" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">application</text>
  <text x="352" y="110" font-size="11.5" fill="var(--sl-color-gray-3)" text-anchor="middle">use cases · orchestration</text>
  <rect x="490" y="52" width="185" height="90" rx="9" fill="var(--sl-color-accent-low)" stroke="var(--sl-color-accent)"/>
  <text x="582" y="92" font-size="14.5" font-weight="700" fill="var(--sl-color-accent-high)" text-anchor="middle">domain</text>
  <text x="582" y="110" font-size="11.5" fill="var(--sl-color-accent-high)" text-anchor="middle">pure business model</text>
  <rect x="715" y="62" width="175" height="70" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/>
  <text x="802" y="92" font-size="14.5" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">infrastructure</text>
  <text x="802" y="110" font-size="11.5" fill="var(--sl-color-gray-3)" text-anchor="middle">DB · Kafka · HTTP</text>
  <line x1="215" y1="97" x2="253" y2="97" stroke="var(--sl-color-gray-4)" stroke-width="1.6" marker-end="url(#h-ah)"/>
  <line x1="450" y1="97" x2="488" y2="97" stroke="var(--sl-color-gray-4)" stroke-width="1.6" marker-end="url(#h-ah)"/>
  <line x1="715" y1="97" x2="677" y2="97" stroke="var(--sl-color-accent)" stroke-width="1.6" marker-end="url(#h-aha)"/>
  <text x="450" y="180" font-size="12" fill="var(--sl-color-gray-3)" text-anchor="middle">enforced mechanically in CI by ArchUnit — the build fails on a violation</text>
</svg>
<figcaption>The domain is pure Java — zero Spring, JPA, or Kafka imports, ever. Infrastructure implements ports the domain declares; the domain never knows how.</figcaption>
</figure>

The payoff: business logic is testable in milliseconds with no Spring context,
and the framework details — which database, which broker — stay swappable behind
ports instead of leaking into the core.

## Multi-tenancy

Tenancy is modelled with **Keycloak Organizations** (one realm, an org per
tenant) rather than realm-per-tenant — chosen for operational simplicity at this
scale. Tenant identity is always resolved from the JWT, never trusted from client
input, and isolation is enforced at the application layer in every service.

## The compliance differentiator: time-travel audit

The platform can reconstruct *which rules and which watchlist versions applied on
any past date*. Screening results pin the watchlist source-version map at finalize
time; the immutable audit service records every domain event; and regulator
exports rebuild the exact snapshot for a date window. For a regulated buyer,
"show me what you knew, and when" is answerable by design.

## What this enables next

The same disciplines — typed contracts, queryable audit, clean ports — are what
make the [AI layer](/ai/agentic-foundation/) safe to add: agents consume
well-defined tool surfaces, and every action they take is traceable against the
same audit spine the rest of the platform already trusts.
