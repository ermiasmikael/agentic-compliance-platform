---
title: "Decision deep-dives — AI / agentic tier"
---

Each entry is a real decision from the project, in the format it was actually reasoned through:
the problem, the options weighed *with their pros and cons*, the choice, and the tradeoff accepted.
These are distilled from the project's ADRs (numbers referenced) and rewritten to be public-safe.

See also the design write-ups under [Applied AI](/ai/agentic-foundation/) for *how* these were built;
this page is the *why this and not that*.

---

## RAG + tool-use over fine-tuning a model (ADR-0015)

**Problem.** A single developer runs the platform; human-in-the-loop support displaces engineering
time. I wanted a self-service AI surface grounded in operational truth (runbooks, ADRs, event
contracts, docs) that could also answer "state of the system" questions.

**Options.**
- **Train/fine-tune a specialized LLM.** Pro: a bespoke model sounds like the "real" AI answer.
  Con: training-data curation, an eval harness, drift monitoring, and specialized-model inference are
  each multi-month efforts; for one engineer the leverage is *negative*. And the domain knowledge
  changes daily (sanctions lists, runbooks revise) — a frozen model is stale the day it ships.
- **Retrieval-augmented generation + tool use.** Pro: embedding fresh docs + retrieving beats a
  frozen model for knowledge that moves; *tool use* beats memorization for "what's the state of X
  right now." Con: you own a retrieval pipeline and must defend it against bad grounding.

**Decision.** RAG + tool use. The governing insight: **most "we need a custom LLM" intuitions are
actually retrieval problems.** Build the retrieval/grounding/tooling rigor, keep the model swappable.

**Tradeoff accepted.** No bespoke-model "wow"; in exchange, answers track reality and the system is
maintainable by one person. Revisit only if a genuine non-retrieval use case appears (its own ADR).

---

## Python agent tier, model-agnostic, no LangChain (ADR-0035)

**Problem.** Where do the agents live, and what do they build on? The platform is Java/Spring; the
AI ecosystem is Python.

**Options.**
- **In-JVM (Spring AI).** Pro: path of least resistance on the JVM — ships an Ollama client,
  structured tool-call decoding, chat-memory primitives; no new language in the stack. Con: keeps the
  AI work tied to the platform's release cadence and to the JVM AI ecosystem, which trails Python.
- **A framework (LangChain / LangGraph / LlamaIndex), Python.** Pro: better agent ergonomics out of
  the box. Con: a heavy abstraction over something I wanted to *understand and own*; framework churn;
  and it still drags Python into the stack — so I pay the polyglot cost either way.
- **Hand-rolled loops behind a model-agnostic port, Python.** Pro: full control of the agent loop
  (debuggable, owned IP), and a thin `Llm` Protocol with per-provider adapters (LiteLLM under it)
  means the model/runner is a swappable adapter. Con: a polyglot boundary (separate CI path, images,
  health story) and I write the loop myself.

**Decision.** A separate Python tier with hand-rolled loops behind a model-agnostic `Llm` port. The
polyglot cost is paid once and bought real control + anti-lock-in; the model became an on-prem Ollama
adapter with zero code change to swap.

**Tradeoff accepted.** Two CI/CD paths and a language boundary, in exchange for owning the agent loop
and never being locked to one vendor or framework. ([overview](/ai/agentic-foundation/))

---

## Security baseline *before* agent features (ADR-0037)

**Problem.** In what order do you build agent capability and agent security?

**Options.**
- **Features first, harden later.** Pro: visible progress sooner. Con: in a regulated product,
  retrofitting injection defense, output validation, and HITL onto already-shipped capability is how
  vulnerabilities ship; security becomes a patch, not a property.
- **A composable security baseline first, every agent depends on it.** Pro: each new agent *inherits*
  deny-by-default authz, data-marking, injection scanning, output validation, HITL, and tracing. Con:
  upfront work before the first flashy feature; a small per-call latency cost from the filters.

**Decision.** Build `agent-security` first (mapped to the OWASP LLM Top 10) and make it a dependency
of every agent. An agent is never trusted to "be careful"; the controls sit *around* the model.

**Tradeoff accepted.** Slower to the first demo, paid back as every subsequent agent being safe by
construction. ([security](/ai/agent-security/))

---

## Cite-or-abstain as a hard output contract (ADR-0038)

**Problem.** An LLM answering compliance questions can produce a fluent, confident, *wrong* answer —
or invent a citation. What stops that from reaching an analyst?

**Options.**
- **Standard retrieve-then-generate, trust the model to ground.** Pro: simplest. Con: the model will
  occasionally cite a source that wasn't retrieved or state uncited claims; a fabricated citation is
  worse than silence in compliance.
- **Reject any answer that isn't grounded — force an abstention.** Pro: a confident wrong answer can't
  reach the user; "I don't know" is an acceptable, honest output. Con: more abstentions; a validator
  to build and maintain.

**Decision.** A `CitationValidator` runs *after* generation: a cited source that wasn't retrieved →
reject; claims with neither a citation nor an explicit abstention token → reject. It composes with
the `agent-security` output validators (e.g. reject ungrounded numbers) as one chain.

**Tradeoff accepted.** Some answerable questions get a cautious abstention; in exchange the system
never emits a sourced-looking lie. This caught a real fabricated-citation failure from a 7B model.
([rag](/ai/rag-layer/), [code](/code/))

---

## MCP: closed allow-list + token propagation (ADR-0039)

**Problem.** MCP gives agents a clean tool surface — and a fresh set of foot-guns (tool poisoning,
over-broad scope, the confused-deputy problem).

**Options (two axes).**
- **Server trust — dynamic discovery vs. fixed allow-list.** Dynamic discovery scales to many tools
  but is exactly the tool-poisoning / over-scope risk a compliance product can't take. A fixed
  first-party allow-list is less flexible but bounded and auditable.
- **Identity — service account vs. propagated user bearer.** A service account is simplest but is the
  confused-deputy problem (the server acts with ambient authority). Propagating the caller's bearer
  means the server acts *as the user*, so downstream authz + tenant scoping apply to the real
  identity.

**Decision.** Closed first-party allow-list (the client's server dict *is* the allow-list; off-list
calls are refused before any network I/O) **and** the caller's bearer propagated on every call, with
every call digested into the agent trace (size + hash, never raw payload). MCP sits *behind* typed
tool ports, so a direct-HTTP adapter and an MCP adapter coexist per tool.

**Tradeoff accepted.** No discoverable, open-ended tool ecosystem; in exchange, bounded auditable
agent↔tool plumbing with no confused deputy. A tool-poisoning red-team harness asserts a mutated tool
description can't change behavior. ([mcp](/ai/mcp-tools/), [code](/code/))

---

## Write-capable agent tools + provable non-autonomy (ADR-0018)

**Problem.** Read-only agents are easy; the moment an agent can *change* state (assign a case), you
need to prove the human — not the model — decided, and you need a separate audit line for
agent-mediated writes.

**Options.**
- **Add a `sideEffect` flag to the existing tool-invocation event.** Pro: one event type. Con: read
  events and write events care about different things (a write needs target resource + outcome); a
  flag muddies "show me every change the agent ever made."
- **A distinct `agent.action.recorded` event for state-changes.** Pro: "every change an agent made"
  is a clean query; the write-event schema evolves independently. Con: a second event type to emit
  and consume.

**Decision.** A distinct write-event type, **plus** layered authorization: the agent never elevates
privilege — the human's own bearer must already carry the permission, the downstream service
enforces it, and a denied attempt is still audited (attempt recorded, state unchanged). The first
write tool only *proposes*; a different human approves (four-eyes).

**Tradeoff accepted.** More audit plumbing, in exchange for being able to *prove* to a regulator that
the agent proposed and a human decided. The durable trace exists precisely to demonstrate the agent
did not decide.

---

## ML rollout: shadow → canary → live, gated and reversible (ADR-0009 / 0011 / 0012)

**Problem.** How do you introduce ML scoring into a screening path where a wrong call has compliance
consequences, on constrained CPU-only hardware, without ever risking customer outcomes?

**Options.**
- **Binary on/off for ML.** Pro: trivial. Con: no way to measure the model against the rules before
  it affects anyone; flip-the-switch is all-or-nothing risk.
- **Explicit graduated modes (DISABLED → SHADOW → CANARY → LIVE).** Pro: SHADOW runs the model on
  100% of traffic with the rule engine still authoritative, so agreement rate and latency are
  measured *before* any decision is handed over; CANARY exposes a deterministic hash-bucketed slice.
  Con: more rollout machinery and config to operate.

**Decision.** The graduated modes, with **deterministic** canary hashing (same entity always lands in
the same bucket — no flapping), a three-state model lifecycle (one ACTIVE model per scope, atomic
promotion, permanent DEPRECATED), and a KPI guard that auto-rolls-back below an agreement threshold.
The rule engine stays authoritative until the model earns promotion.

**Tradeoff accepted.** Accuracy gains arrive incrementally rather than big-bang, in exchange for
zero-risk introduction and immediate, observable rollback. ML never silently owns an outcome.
