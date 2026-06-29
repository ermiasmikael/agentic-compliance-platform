---
title: The agent tool surface (MCP)
description: How DPS standardizes agent tools with the Model Context Protocol — kept behind typed ports, closed to a vetted allow-list, and hardened against tool poisoning and confused-deputy.
sidebar:
  order: 4
---

The drafter calls one tool. The copilot will call several — knowledge retrieval,
screening lookup, case lookup, audit search, policy lookup. Hand-rolling a typed
port, an HTTP adapter, and auth wiring for each tool, in each agent, is repetitive
glue that drifts. The Model Context Protocol (MCP) standardizes that surface: tools
are described, discovered, and invoked the same way everywhere.

But a compliance product can't adopt MCP in its permissive, discover-anything
default. The interesting engineering is in *how* it's adopted, not *that* it is.

<figure class="diagram">
<svg role="img" aria-label="MCP behind the agent's typed tool port: the agent calls a typed Protocol port, backed by an MCP adapter (or a coexisting direct-HTTP adapter), which calls a closed allow-list client that refuses off-list servers, reaching first-party MCP servers and the internal service APIs; the caller's bearer is propagated end-to-end." viewBox="0 0 900 244" width="100%" style="height:auto;max-width:880px"><defs>
  <marker id="mca" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-gray-4)"/></marker>
  <marker id="mcg" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-accent)"/></marker></defs><text x="450" y="34"  font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">MCP behind the agent's typed ports, gated by a closed allow-list</text><rect x="20" y="70" width="140" height="52" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="90" y="93"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Agent</text><text x="90" y="109"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">hand-rolled loop</text><rect x="180" y="70" width="150" height="52" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="255" y="93"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Typed tool port</text><text x="255" y="109"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">Protocol · agent-facing</text><rect x="350" y="70" width="120" height="52" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="410" y="101"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">MCP adapter</text><rect x="490" y="70" width="160" height="52" rx="9" fill="var(--sl-color-accent-low)" stroke="var(--sl-color-accent)" /><text x="570" y="93"  font-size="14" font-weight="600" fill="var(--sl-color-accent-high)" text-anchor="middle">Closed allow-list</text><text x="570" y="109"  font-size="11" fill="var(--sl-color-accent-high)" text-anchor="middle">refuses off-list</text><rect x="670" y="70" width="200" height="52" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="770" y="93"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">First-party MCP servers</text><text x="770" y="109"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">export · retrieval · case-action</text><line x1="160" y1="96" x2="180" y2="96" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#mca)"/><line x1="330" y1="96" x2="350" y2="96" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#mca)"/><line x1="470" y1="96" x2="490" y2="96" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#mca)"/><line x1="650" y1="96" x2="670" y2="96" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#mca)"/><rect x="350" y="150" width="120" height="30" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" stroke-dasharray="5 4"/><text x="410" y="170"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">direct-HTTP</text><line x1="410" y1="122" x2="410" y2="150" stroke="var(--sl-color-gray-4)" stroke-width="1.6" stroke-dasharray="5 4" marker-end="url(#mca)"/><text x="478" y="169"  font-size="10"  fill="var(--sl-color-gray-3)" text-anchor="start">coexists, config-selected</text><rect x="670" y="150" width="200" height="30" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="770" y="170"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Internal service APIs</text><line x1="770" y1="122" x2="770" y2="150" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#mca)"/><text x="450" y="214"  font-size="11"  fill="var(--sl-color-gray-3)" text-anchor="middle">Caller's bearer propagated end-to-end — the server acts as the user, never a service account (no confused-deputy).</text></svg>
<figcaption>MCP is an adapter behind the agent's typed port — interchangeable with a direct-HTTP one. The closed allow-list and bearer propagation are the two non-negotiables.</figcaption>
</figure>

## A protocol, not a framework

MCP is an open, multi-vendor specification — the "HTTP for tools" — not a model SDK
and not an agent framework. Adopting it does **not** reintroduce the framework
lock-in the [foundation](/ai/agentic-foundation/) deliberately avoided: the agent
loop stays hand-rolled, the `LlmPort` stays, and MCP only governs how *tools* are
exposed and called. It's the tool-side analogue of using a vendor-neutral client on
the model side — interoperability, not dependency.

Concretely, **MCP lives behind the agent's typed tool ports as an adapter.** The
agent depends on a `Protocol` port (as the drafter depends on `RegulatorExportTool`);
whether that port is backed by a direct-HTTP adapter or an MCP client is an
infrastructure detail the agent never sees. So the two coexist during migration,
and the explicit, typed contract stays the agent-facing boundary instead of leaning
on MCP's dynamic, stringly-typed tool list.

## Closed, not open

Agents connect only to a **vetted, allow-listed set of first-party MCP servers** —
each one a thin wrapper over an existing internal service API. There is **no dynamic
discovery of arbitrary or third-party servers** in the product tier. Discoverability
is a developer convenience; at runtime, in a regulated product, the tool set must be
a known, reviewed quantity.

## The MCP-specific threats — and the defenses

MCP widens the surface in ways generic tool-calling doesn't, and each maps onto the
[security baseline](/ai/agent-security/):

- **Tool poisoning / rug-pull.** A tool's *description* is read by the model to
  decide when to call it — so a malicious or silently-mutated description can inject
  instructions. Defense: tool descriptions are part of the **trusted prompt
  surface** — first-party only, version-pinned, and reviewed/diffed like code; never
  fetched from an untrusted server at runtime.
- **Confused-deputy.** A server acting with more authority than its caller. Defense:
  **token propagation** — the MCP server acts *as the requesting user*, carrying
  their token, never an ambient service account; per-tool authorization at the
  server enforces the same gates as the rest of the platform.
- **Over-broad scope (OWASP LLM06, excessive agency).** Each tool declares the
  *minimum* permission and allowed caller; deny-by-default; write tools are
  tenant-scoped only.
- **Injection via tool results.** A tool's *output* — retrieval results, lookups —
  is untrusted data, exactly like retrieved text, so it's data-marked and never
  treated as instructions.

Consequential (write) tools sit behind the human-in-the-loop gate; every call —
server, tool, arguments, result digest — is recorded in the agent trace; and server
dependencies are pinned and scanned. The two non-negotiables: **token propagation**
(no confused-deputy) and the **closed first-party tool set** (no poisoning from
untrusted servers).

<figure class="diagram">
<svg role="img" aria-label="MCP widens the attack surface and each threat maps to a control. Tool poisoning or rug-pull, where a mutated description injects instructions, is met by treating descriptions as a trusted prompt surface: first-party, version-pinned, diffed like code. Confused-deputy, a server acting with more authority than its caller, is met by token propagation so the server acts as the user with per-tool authorization. Over-broad scope (LLM06 excessive agency) is met by least-privilege: minimum permission, deny-by-default, writes tenant-scoped. Injection via tool results, where tool output is untrusted data, is met by data-marking so it is never treated as instructions." viewBox="0 0 812 300" width="100%" style="height:auto;max-width:812px"><defs><marker id="tda" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-gray-4)"/></marker><marker id="tdg" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-accent)"/></marker></defs><text x="406" y="26" font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">MCP widens the surface — each threat maps to a control</text><text x="174" y="50" font-size="11" font-weight="600" fill="var(--sl-color-gray-3)" text-anchor="middle">Threat</text><text x="625" y="50" font-size="11" font-weight="600" fill="var(--sl-color-accent-high)" text-anchor="middle">Control</text><rect x="24" y="62" width="300" height="44" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="174" y="82" font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Tool poisoning / rug-pull</text><text x="174" y="98" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">a mutated description injects instructions</text><rect x="470" y="62" width="308" height="44" rx="9" fill="var(--sl-color-accent-low)" stroke="var(--sl-color-accent)"/><text x="624" y="82" font-size="13" font-weight="600" fill="var(--sl-color-accent-high)" text-anchor="middle">Descriptions = trusted prompt surface</text><text x="624" y="98" font-size="10.5" fill="var(--sl-color-accent-high)" text-anchor="middle">first-party · version-pinned · diffed like code</text><line x1="324" y1="84" x2="470" y2="84" stroke="var(--sl-color-accent)" stroke-width="1.6" marker-end="url(#tdg)"/><rect x="24" y="120" width="300" height="44" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="174" y="140" font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Confused-deputy</text><text x="174" y="156" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">server acts with more authority than its caller</text><rect x="470" y="120" width="308" height="44" rx="9" fill="var(--sl-color-accent-low)" stroke="var(--sl-color-accent)"/><text x="624" y="140" font-size="13" font-weight="600" fill="var(--sl-color-accent-high)" text-anchor="middle">Token propagation</text><text x="624" y="156" font-size="10.5" fill="var(--sl-color-accent-high)" text-anchor="middle">acts as the user · per-tool authz</text><line x1="324" y1="142" x2="470" y2="142" stroke="var(--sl-color-accent)" stroke-width="1.6" marker-end="url(#tdg)"/><rect x="24" y="178" width="300" height="44" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="174" y="198" font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Over-broad scope · LLM06</text><text x="174" y="214" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">excessive agency</text><rect x="470" y="178" width="308" height="44" rx="9" fill="var(--sl-color-accent-low)" stroke="var(--sl-color-accent)"/><text x="624" y="198" font-size="13" font-weight="600" fill="var(--sl-color-accent-high)" text-anchor="middle">Least-privilege</text><text x="624" y="214" font-size="10.5" fill="var(--sl-color-accent-high)" text-anchor="middle">min permission · deny-by-default · writes tenant-scoped</text><line x1="324" y1="200" x2="470" y2="200" stroke="var(--sl-color-accent)" stroke-width="1.6" marker-end="url(#tdg)"/><rect x="24" y="236" width="300" height="44" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="174" y="256" font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Injection via tool results</text><text x="174" y="272" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">tool output is untrusted data</text><rect x="470" y="236" width="308" height="44" rx="9" fill="var(--sl-color-accent-low)" stroke="var(--sl-color-accent)"/><text x="624" y="256" font-size="13" font-weight="600" fill="var(--sl-color-accent-high)" text-anchor="middle">Data-marked</text><text x="624" y="272" font-size="10.5" fill="var(--sl-color-accent-high)" text-anchor="middle">never treated as instructions</text><line x1="324" y1="258" x2="470" y2="258" stroke="var(--sl-color-accent)" stroke-width="1.6" marker-end="url(#tdg)"/></svg>
<figcaption>Each MCP-specific threat lands on an existing baseline control — the closed allow-list and bearer propagation being the two non-negotiables.</figcaption>
</figure>

## Read-only first, then write

The pattern was proven read-only first, to keep the human-in-the-loop and sandboxing
surface small while the protocol, auth propagation, and tracing were shaken out. Two
read tools moved behind first-party MCP servers, each still behind its typed port: the
**regulator-export** tool (proving the pattern on the known-good drafter surface) and
**knowledge-retrieval** (the [RAG layer](/ai/rag-layer/), inheriting its tenant-scope
and data-marking).

The first **write** tool — `assign_case` — then landed on the same rails: token
propagated end-to-end, every call traced, and the consequential action held behind a
human gate. Because a write tool can cause side-effects, it gets its own contract —
*propose, don't perform* — backed by a durable four-eyes approval queue and a trace
that proves a human, not the agent, decided. That's the subject of
[human-in-the-loop & the agent trace](/ai/human-in-the-loop/).
