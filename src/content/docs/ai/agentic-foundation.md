---
title: A model-agnostic, on-prem agent tier
description: How the DPS AI layer is built — model-agnostic ports, on-prem open models, and agents as tools rather than decision-makers.
sidebar:
  order: 1
---

The AI layer is a standalone **Python (FastAPI)** tier — deliberately *not*
in-JVM. The reasoning: Python is the AI mainstream, it draws a clean polyglot
boundary, and it keeps the agent loop under our own control rather than a
framework's.

## Three load-bearing decisions

### 1. Agents are tools, not decision-makers

This is the constraint everything else serves. In a compliance product, "the AI
decided to block this shipment" is legally unsaleable. So screening outcomes —
BLOCK / REVIEW / ALLOW — stay deterministic and rule-traceable. Agents *draft*,
*summarize*, and *accelerate*; a human owns every consequential action.

### 2. Model-agnostic by construction

The agent talks to a hexagonal `LlmPort` (a Python `Protocol`), with per-provider
adapters behind it. Under the port we use **LiteLLM** purely to normalize
provider HTTP — it's vendor-neutral, explicitly anti-lock-in, *not* a vendor SDK.
We **hand-roll the agent loop** rather than adopt LangChain, to keep control and
avoid framework lock-in. Because the agent speaks an OpenAI-compatible API, both
the *runner* (Ollama today) and the *model* are swappable per-agent with no
agent-code change.

> Runner vs. model: **Ollama** is the runner; **Qwen / Llama / DeepSeek** are
> models that run *on* it. The port makes both independently replaceable.

### 3. Self-hosted open models — provider independence and a privacy boundary

The first provider is an open-weights model (Qwen 2.5 7B) served via Ollama on a
self-hosted inference host. The decision is architectural, not operational:

- **A privacy boundary enforced by topology.** In a compliance domain,
  counterparty PII cannot leave the trust boundary. Self-hosting makes "no data
  egresses to a third-party LLM" a structural property of *where* inference runs —
  not a policy you have to trust.
- **Provider independence.** The model-agnostic `LlmPort` removes any coupling to
  a single vendor's API, pricing, rate limits, or deprecation schedule. Swapping
  runner or model is a config change, not a rewrite.
- **Reproducibility.** Self-hosted models are pinned by digest and recorded in
  each agent trace, so *which* model produced a given output is answerable for any
  past decision — a requirement of the [security baseline](/ai/agent-security/).

The honest trade-off: CPU-only inference is slow (tens of seconds for a short
draft), so the UX is async — and because model selection is per-agent behind the
port, a latency- or capability-sensitive agent swaps to a larger local or hosted
model with no code change. (Running open models locally also makes dev and demos
free — a welcome side effect, not the rationale.)

<figure class="diagram">
<svg role="img" aria-label="The model-agnostic LlmPort: a hand-rolled agent loop calls a typed LlmPort (a Python Protocol), backed by LiteLLM which normalizes provider HTTP. LiteLLM speaks an OpenAI-compatible API to Ollama, the runner, which runs an open model — Qwen, Llama, or DeepSeek. The Ollama runner and the model both sit inside a self-hosted trust boundary and are each swappable behind the port with no agent-code change; counterparty data never leaves the boundary." viewBox="0 0 860 282" width="100%" style="height:auto;max-width:860px"><defs><marker id="lpa" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-gray-4)"/></marker><marker id="lpg" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-accent)"/></marker></defs><text x="430" y="26" font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">One port — runner and model swap behind it; inference stays on-prem</text><rect x="24" y="100" width="150" height="58" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="99" y="127" font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Agent loop</text><text x="99" y="143" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">hand-rolled · FastAPI</text><rect x="222" y="100" width="140" height="58" rx="9" fill="var(--sl-color-accent-low)" stroke="var(--sl-color-accent)"/><text x="292" y="127" font-size="14" font-weight="600" fill="var(--sl-color-accent-high)" text-anchor="middle">LlmPort</text><text x="292" y="143" font-size="10.5" fill="var(--sl-color-accent-high)" text-anchor="middle">Python Protocol</text><rect x="410" y="100" width="164" height="58" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="492" y="127" font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">LiteLLM</text><text x="492" y="143" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">normalizes provider HTTP</text><line x1="174" y1="129" x2="222" y2="129" stroke="var(--sl-color-gray-4)" stroke-width="1.6" marker-end="url(#lpa)"/><line x1="362" y1="129" x2="410" y2="129" stroke="var(--sl-color-gray-4)" stroke-width="1.6" marker-end="url(#lpa)"/><text x="292" y="180" font-size="10" fill="var(--sl-color-accent-high)" text-anchor="middle">swap = config, not code</text><rect x="618" y="64" width="220" height="184" rx="11" fill="none" stroke="var(--sl-color-accent)" stroke-dasharray="4 4"/><text x="728" y="84" font-size="11" font-weight="600" fill="var(--sl-color-accent-high)" text-anchor="middle">self-hosted trust boundary</text><rect x="642" y="100" width="172" height="52" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="728" y="124" font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Ollama</text><text x="728" y="140" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">runner — swappable</text><rect x="642" y="178" width="172" height="52" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="728" y="202" font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Qwen · Llama · DeepSeek</text><text x="728" y="218" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">model — swappable</text><line x1="728" y1="152" x2="728" y2="178" stroke="var(--sl-color-gray-4)" stroke-width="1.6" marker-end="url(#lpa)"/><line x1="574" y1="127" x2="642" y2="124" stroke="var(--sl-color-gray-4)" stroke-width="1.6" marker-end="url(#lpa)"/><text x="604" y="112" font-size="9.5" fill="var(--sl-color-gray-3)" text-anchor="start">OpenAI-compatible</text></svg>
<figcaption>The agent depends only on the <code>LlmPort</code>. LiteLLM normalizes provider HTTP; the runner (Ollama) and the model both sit inside the self-hosted boundary and swap with a config change, not a rewrite.</figcaption>
</figure>

## Case study: the regulator-export drafter

The first agent is intentionally the lowest-risk surface: it drafts the
human-readable narrative cover for a regulator evidence package. Its pipeline is
the reusable shape every later agent inherits:

<figure class="diagram">
<svg role="img" aria-label="The drafter loop: tool call, ground, generate, validate; a passing draft becomes the AI narrative, a rejected or errored one falls back to a deterministic template; both produce the narrative cover, and the whole run is traced." viewBox="0 0 980 250" width="100%" style="height:auto;max-width:940px"><defs>
  <marker id="foa" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-gray-4)"/></marker>
  <marker id="fog" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-accent)"/></marker></defs><text x="490" y="38"  font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">The defensible loop — and the AI never degrades the output</text><rect x="16" y="84" width="140" height="52" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="86" y="107"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Tool call</text><text x="86" y="123"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">analyst's bearer</text><rect x="170" y="84" width="120" height="52" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="230" y="107"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Ground</text><text x="230" y="123"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">structured facts</text><rect x="304" y="84" width="124" height="52" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="366" y="107"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Generate</text><text x="366" y="123"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">LLM draft</text><rect x="442" y="84" width="132" height="52" rx="9" fill="var(--sl-color-accent-low)" stroke="var(--sl-color-accent)" /><text x="508" y="107"  font-size="14" font-weight="600" fill="var(--sl-color-accent-high)" text-anchor="middle">Validate</text><text x="508" y="123"  font-size="11" fill="var(--sl-color-accent-high)" text-anchor="middle">reject ungrounded #</text><line x1="156" y1="110" x2="170" y2="110" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#foa)"/><line x1="290" y1="110" x2="304" y2="110" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#foa)"/><line x1="428" y1="110" x2="442" y2="110" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#foa)"/><rect x="614" y="50" width="150" height="46" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="689" y="78"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">AI draft</text><rect x="614" y="126" width="150" height="46" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="689" y="146"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Template fallback</text><text x="689" y="162"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">deterministic</text><rect x="802" y="84" width="150" height="52" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="877" y="107"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Narrative cover</text><text x="877" y="123"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">never AI-degraded</text><line x1="574" y1="100" x2="612" y2="75" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#foa)"/><line x1="574" y1="120" x2="612" y2="147" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#foa)"/><text x="595" y="84"  font-size="10"  fill="var(--sl-color-gray-3)" text-anchor="start">pass</text><text x="595" y="138"  font-size="10"  fill="var(--sl-color-gray-3)" text-anchor="start">reject / error</text><line x1="764" y1="73" x2="800" y2="100" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#foa)"/><line x1="764" y1="149" x2="800" y2="122" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#foa)"/><rect x="16" y="198" width="936" height="38" rx="9" fill="none" stroke="var(--sl-color-accent)" stroke-dasharray="2 4"/><text x="484" y="221"  font-size="12" font-weight="600" fill="var(--sl-color-accent-high)" text-anchor="middle">Trace — the whole run recorded; proves the agent only summarized and decided nothing</text></svg>
<figcaption>The drafter's loop. A passing draft becomes the AI narrative; a rejected or errored one falls back to a deterministic template — so the export is never degraded by the AI.</figcaption>
</figure>

- **Tool call** — fetch the aggregated export package from an existing service,
  propagating the *analyst's own bearer token* (least-privilege — the agent acts
  as the user, not a god service account).
- **Ground** — build the prompt strictly from structured fields, and explicitly
  label the counterparty as the entity *screened* (not the screener), to kill a
  role-ambiguity the model otherwise stumbled on.
- **Validate** — a deterministic guard rejects any number in the draft that
  wasn't in the grounding facts. A hallucinated figure is worse than a plainer
  correct one.
- **Template fallback** — on a rejected draft *or* a model error/timeout, a
  deterministic, always-correct template takes over. The export is **never
  degraded by the AI**; the worst case is plainer prose.
- **Trace** — a structured record of the whole run, proving the agent only
  summarized an existing package and made no decision.

This validates the foundation end-to-end, fully self-hosted — and the
`validate` + `trace` + human-review steps are exactly where the
[agent-security baseline](/ai/agent-security/) plugs in.
