---
title: AI agent security baseline
description: A six-pillar agent security control set aligned to the OWASP LLM Top 10, gating the rest of the AI roadmap.
sidebar:
  order: 2
---

Before the agent fleet grows — retrieval (RAG), tool standardization (MCP), a
multi-tool investigation copilot — the platform stands up a **security baseline**
that every agent inherits. In a compliance product this isn't optional polish:
an unsecured LLM is a liability, while a least-privilege, injection-resistant,
human-gated, fully-audited agent tier is a feature you can sell.

The controls map almost one-to-one onto the **OWASP LLM Top 10 (2025)** and
**MITRE ATLAS** — the vocabulary an auditor (and a security reviewer) already
speaks.

<figure class="diagram">
<svg role="img" aria-label="Defense in depth across the request lifecycle: untrusted input passes an injection filter, the agent and LLM run with the user's bearer and a pinned digest, output is validated, a human-in-the-loop gate guards effects; a durable trace feeds the audit service, over a foundation of supply-chain and model-integrity controls." viewBox="0 0 940 270" width="100%" style="height:auto;max-width:920px"><defs>
  <marker id="sea" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-gray-4)"/></marker>
  <marker id="seg" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-accent)"/></marker></defs><text x="470" y="38"  font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Defense in depth — six pillars across the request lifecycle (OWASP LLM Top 10)</text><rect x="20" y="78" width="132" height="54" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="86" y="102"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Untrusted input</text><text x="86" y="118"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">docs · notes · tool output</text><rect x="174" y="78" width="124" height="54" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="236" y="102"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Injection filter</text><text x="236" y="118"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">② data-marked</text><rect x="320" y="78" width="150" height="54" rx="9" fill="var(--sl-color-accent-low)" stroke="var(--sl-color-accent)" /><text x="395" y="102"  font-size="14" font-weight="600" fill="var(--sl-color-accent-high)" text-anchor="middle">Agent + LLM</text><text x="395" y="118"  font-size="11" fill="var(--sl-color-accent-high)" text-anchor="middle">① user bearer · digest</text><rect x="492" y="78" width="140" height="54" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="562" y="102"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Output validation</text><text x="562" y="118"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">② grounded / cited</text><rect x="654" y="78" width="122" height="54" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="715" y="102"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">HITL gate</text><text x="715" y="118"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">③ propose→approve</text><rect x="798" y="78" width="120" height="54" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="858" y="102"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Effect</text><text x="858" y="118"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">tenant-scoped</text><line x1="152" y1="105" x2="174" y2="105" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#sea)"/><line x1="298" y1="105" x2="320" y2="105" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#sea)"/><line x1="470" y1="105" x2="492" y2="105" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#sea)"/><line x1="632" y1="105" x2="654" y2="105" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#sea)"/><line x1="776" y1="105" x2="798" y2="105" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#sea)"/><rect x="20" y="170" width="898" height="42" rx="9" fill="var(--sl-color-accent-low)" stroke="var(--sl-color-accent)"/><text x="469" y="196"  font-size="11.5" font-weight="600" fill="var(--sl-color-accent-high)" text-anchor="middle">④ Durable trace → immutable audit — request · tool calls · prompts · model digest · verdicts · human decision</text><rect x="20" y="222" width="898" height="34" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="250" y="243"  font-size="11"  fill="var(--sl-color-gray-3)" text-anchor="middle">⑤ Supply-chain — CVE scan · lockfile · SBOM</text><text x="690" y="243"  font-size="11"  fill="var(--sl-color-gray-3)" text-anchor="middle">⑥ Model integrity — label provenance · drift guard</text></svg>
<figcaption>Each pillar sits at a point in the request lifecycle. The trace spans the whole run; supply-chain and model integrity are the foundation underneath.</figcaption>
</figure>

## The six pillars

### 1. Identity, RBAC & least-privilege — *LLM06 Excessive Agency*

Agents carry the **requesting user's own token** and inherit exactly their
permissions — never an ambient "god" service account. Each agent is a
first-class principal with a bounded scope, and every tool declares its required
permission and allowed caller profiles, deny-by-default. Write tools are
tenant-scoped only.

### 2. Prompt-injection defense & output handling — *LLM01 / LLM05*

Untrusted content — retrieved documents, adverse-media text, case notes — is
delimited and labelled as **data, never instructions**. Inputs pass an injection
filter before entering a prompt; outputs are validated before they're rendered,
persisted, or used as tool arguments. Model output is **never** executed as code
or passed unchecked as a tool argument. (The drafter's "reject ungrounded
numbers" guard is the first instance of this output-validation stage.)

### 3. Sandboxing & human-in-the-loop — *LLM06*

A standard *draft / propose → human approves → effect* gate sits in front of any
consequential action; nothing side-effecting auto-executes. Autonomy is tiered —
read-only drafters run light, anything with side-effects requires audited human
approval — and process-forking tools run sandboxed with resource and time caps.

### 4. Logging, traceability & audit — *cross-cutting*

Every run emits a complete structured trace: the request, each tool call with
arguments and a result digest, the prompts, the model and its pinned digest,
the raw output, validation verdicts, the human decision, and the final action.
Traces are durable and surfaced to the immutable audit service — the artefact
that proves an agent *only summarized* and *what it was shown*.

### 5. Supply-chain & dependency auditing — *LLM03*

Dependency CVE scanning, lockfile pinning, and SBOMs extend to the Python agent
tier; LLM client/runner dependencies and (later) MCP servers are vetted; and
model digests are pinned and recorded in the trace so "which model produced this"
is auditable.

### 6. Model integrity: drift & poisoning — *LLM04*

The analyst-decision → training-label feedback loop is treated as a **poisoning
vector**: labels carry provenance and pass anomaly checks before ingest, and no
single actor can dominate the training signal. Drift is monitored beyond a single
agreement-rate metric, with a shadow → canary → live rollout, a KPI guard, and
automated rollback as the safety net.

## A shared layer, not per-agent diligence

These controls live in a **reusable enforcement layer** — identity/permission
resolution, the injection filter, the output validator, the human-in-the-loop
gate, the trace recorder — so a new agent composes them by default. Security is a
property of the platform, not of each author remembering to add it.

<figure class="diagram">
<svg role="img" aria-label="A shared enforcement layer: three agents — the export drafter, the investigation copilot, and the first-party MCP servers — all compose one agent security layer made of five controls: identity and RBAC, an injection filter, an output validator, a human-in-the-loop gate, and a trace recorder. The layer yields deny-by-default, least-privilege, injection-resistant, fully-audited behavior as a property of the platform, not of each author." viewBox="0 0 820 292" width="100%" style="height:auto;max-width:820px"><defs><marker id="sla" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-gray-4)"/></marker><marker id="slg" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-accent)"/></marker></defs><text x="410" y="26" font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Security is composed by default — one layer, every agent</text><rect x="24" y="56" width="210" height="46" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="129" y="77" font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Export drafter</text><text x="129" y="93" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">read-only</text><rect x="305" y="56" width="210" height="46" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="410" y="77" font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Investigation copilot</text><text x="410" y="93" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">RAG + write tools</text><rect x="586" y="56" width="210" height="46" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="691" y="77" font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">MCP servers</text><text x="691" y="93" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">export · retrieval · case-action</text><line x1="129" y1="102" x2="129" y2="146" stroke="var(--sl-color-gray-4)" stroke-width="1.6" marker-end="url(#sla)"/><line x1="410" y1="102" x2="410" y2="146" stroke="var(--sl-color-gray-4)" stroke-width="1.6" marker-end="url(#sla)"/><line x1="691" y1="102" x2="691" y2="146" stroke="var(--sl-color-gray-4)" stroke-width="1.6" marker-end="url(#sla)"/><rect x="24" y="146" width="772" height="72" rx="11" fill="var(--sl-color-accent-low)" stroke="var(--sl-color-accent)"/><text x="410" y="165" font-size="13" font-weight="600" fill="var(--sl-color-accent-high)" text-anchor="middle">Agent security layer — composed by default</text><rect x="41" y="178" width="138" height="30" rx="7" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="110" y="197" font-size="11" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">identity · RBAC</text><rect x="191" y="178" width="138" height="30" rx="7" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="260" y="197" font-size="11" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">injection filter</text><rect x="341" y="178" width="138" height="30" rx="7" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="410" y="197" font-size="11" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">output validator</text><rect x="491" y="178" width="138" height="30" rx="7" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="560" y="197" font-size="11" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">HITL gate</text><rect x="641" y="178" width="138" height="30" rx="7" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="710" y="197" font-size="11" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">trace recorder</text><line x1="410" y1="218" x2="410" y2="242" stroke="var(--sl-color-gray-4)" stroke-width="1.6" marker-end="url(#sla)"/><rect x="24" y="242" width="772" height="36" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="410" y="264" font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">deny-by-default · least-privilege · injection-resistant · fully audited — a platform property, not each author’s diligence</text></svg>
<figcaption>A new agent inherits the controls by composing the shared layer — identity, injection filtering, output validation, the human gate, and tracing — rather than re-implementing them.</figcaption>
</figure>

## Why it gates the roadmap

RAG and MCP both *widen* the attack surface — retrieval introduces indirect
injection and corpus poisoning (LLM01/LLM04/LLM08); MCP redraws the tool boundary
(tool poisoning, confused-deputy, over-broad scope, LLM06). Landing the baseline
first means those capabilities arrive *into* a secured tier instead of being
retrofitted afterward — cheaper, and the right message for a compliance product.
