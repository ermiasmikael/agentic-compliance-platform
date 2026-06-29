---
title: Rolling out an ML matcher without breaking screening
description: How DPS layers an ML matcher behind the deterministic engine and ships it shadow → canary → live behind a KPI guard with automatic rollback — plus the analyst-feedback loop that trains it.
sidebar:
  order: 1
---

The rule-based [screening engine](/architecture/platform-overview/) is explainable and
traceable, but it is also blunt: it generates false positives, and a human clears every
one. The obvious win is an ML matcher that learns from those clearances and quietly stops
surfacing the noise. The obvious danger is the asymmetry — a model that trims a few false
positives but suppresses *one true sanctions hit* isn't an improvement, it's a compliance
incident. You cannot ship a matcher the way you ship a recommender. The interesting
engineering isn't the model; it's the rollout.

The same principle that governs the [agent tier](/ai/agentic-foundation/) governs here:
**the ML assists, the deterministic system decides.** ML never silently becomes the
screening decision.

## The rule-based score stays the system of record

Inference is an *augmentation*, not a replacement. The screening evaluation runs the
deterministic five-tier matcher first and produces the explainable score; only then does
it consult the inference port. The ML output is layered onto a decision that already
stands on its own and is already fully traceable. Pull the model — or the whole inference
service — and screening still works, still explains itself, and still blocks. That
fail-safe is a precondition, not a feature.

## Shadow → canary → live

A model earns its way into the decision path one stage at a time. The matching controller
runs in one of three modes, per tenant:

- **Shadow.** The model scores live traffic alongside the rules, and every prediction is
  compared against the rule-based outcome — but its output *never touches the screening
  decision*. This is pure measurement: it accumulates the agreement signal and surfaces
  disagreements for inspection at zero risk. Every rollout starts here.
- **Canary.** The model influences a limited slice of traffic, still under the guard
  below, so a regression shows up on a small blast radius before it's everywhere.
- **Live.** Full participation — reached only after the canary holds.

Promotion is a deliberate, runbook-driven step, not an automatic graduation. Nothing
advances on a model's say-so.

## The KPI guard and automatic rollback

Each stage sits behind a guard watching a **rolling, per-tenant agreement window**.
Promotion is gated on two thresholds — a **minimum sample size** (default 200) so a
handful of lucky calls can't qualify a model, and a **minimum agreement rate** (default
80%) against the rule-based ground truth. If a live model's agreement decays below the
floor, the guard **rolls it back automatically** — reverting that tenant to rules and
emitting a `matching.rollout.rollback-triggered` event — and then holds a **cooldown**
(default 300s) so a borderline model can't flap in and out of the decision path. The
operator finds out *after* the system has already made itself safe, not before.

<figure class="diagram">
<svg role="img" aria-label="A model is promoted left to right through three stages — shadow (scores live traffic but never decides), canary (a limited slice), and live (full participation) — each promotion a deliberate runbook step. A KPI guard watches a rolling per-tenant agreement window (at least 200 samples, at least 80% agreement against the rule-based score) across the stages; when a live model's agreement decays the guard automatically rolls back to the deterministic rules and holds a 300-second cooldown. The deterministic rules remain the system of record." viewBox="0 0 760 300" width="100%" style="height:auto;max-width:760px"><defs><marker id="rv-a" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-gray-4)"/></marker><marker id="rv-r" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-accent)"/></marker></defs><text x="380" y="26" font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">A model earns its way in — and the guard can pull it back</text><rect x="30"  y="64" width="150" height="54" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="105" y="89"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Shadow</text><text x="105" y="106" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">scores, never decides</text><rect x="305" y="64" width="150" height="54" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="380" y="89"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Canary</text><text x="380" y="106" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">limited slice</text><rect x="570" y="64" width="150" height="54" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-accent)"/><text x="645" y="89"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Live</text><text x="645" y="106" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">full participation</text><line x1="180" y1="91" x2="305" y2="91" stroke="var(--sl-color-gray-4)" stroke-width="1.6" marker-end="url(#rv-a)"/><line x1="455" y1="91" x2="570" y2="91" stroke="var(--sl-color-gray-4)" stroke-width="1.6" marker-end="url(#rv-a)"/><text x="242" y="84" font-size="10" fill="var(--sl-color-gray-3)" text-anchor="middle">promote ▸ runbook</text><text x="512" y="84" font-size="10" fill="var(--sl-color-gray-3)" text-anchor="middle">promote ▸ runbook</text><line x1="105" y1="118" x2="105" y2="150" stroke="var(--sl-color-gray-5)" stroke-width="1.2" stroke-dasharray="3 3"/><line x1="380" y1="118" x2="380" y2="150" stroke="var(--sl-color-gray-5)" stroke-width="1.2" stroke-dasharray="3 3"/><line x1="645" y1="118" x2="645" y2="150" stroke="var(--sl-color-gray-5)" stroke-width="1.2" stroke-dasharray="3 3"/><rect x="30" y="150" width="690" height="46" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-accent)" stroke-dasharray="4 3"/><text x="375" y="170" font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">KPI guard — rolling per-tenant agreement window</text><text x="375" y="187" font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">≥ 200 samples · ≥ 80% agreement vs the rule-based score</text><rect x="24" y="228" width="266" height="46" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-accent)"/><text x="157" y="248" font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Deterministic rules</text><text x="157" y="264" font-size="10" fill="var(--sl-color-gray-3)" text-anchor="middle">system of record — still blocks if the model is pulled</text><path d="M720,196 L720,251 L296,251" fill="none" stroke="var(--sl-color-accent)" stroke-width="1.6" marker-end="url(#rv-r)"/><text x="512" y="243" font-size="10.5" fill="var(--sl-color-accent-high)" text-anchor="middle">agreement decays → auto-rollback + 300s cooldown</text></svg>
<figcaption>Promotion is a deliberate step forward; rollback is automatic. The deterministic rules stay the floor the model is measured against — and the fallback the moment it drifts.</figcaption>
</figure>

## Outcome proof, not just dashboards

The guard doesn't just act; it produces **evidence**. Rollout outcome-proof snapshots —
SLO gauges and agreement statistics — are published to Prometheus and onto Kafka, giving
a human-auditable record of how a model behaved in the decision path over time. It's the
same instinct as the platform's time-travel audit replay: a regulator (or an
engineer) can reconstruct *what the matcher was doing on a given day*, not just trust that
it was fine.

## Closing the loop: analyst decisions become training labels

The signal to train on is already being produced — every case a human dispositions
(`CONFIRMED_MATCH`, false positive, and so on) is a labeled example. The loop wires that
through end-to-end:

<figure class="diagram">
<svg role="img" aria-label="The feedback loop: a case disposition becomes a provenance-checked training label, a scheduled retrain runs on the executor, the promoted model lands in the registry, feeds inference and screening, and screening dispositions feed the next labels — a closed cycle." viewBox="0 0 726 252" width="100%" style="height:auto;max-width:720px"><defs>
  <marker id="mla" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-gray-4)"/></marker>
  <marker id="mlg" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-accent)"/></marker></defs><text x="363" y="28"  font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Analyst decisions train the matcher — a closed loop</text><rect x="24" y="48" width="160" height="48" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="104" y="69"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Case disposition</text><text x="104" y="85"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">confirmed / false-pos</text><rect x="212" y="48" width="130" height="48" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="277" y="69"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Training label</text><text x="277" y="85"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">provenance-checked</text><rect x="372" y="48" width="150" height="48" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="447" y="69"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Retrain</text><text x="447" y="85"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">SIMULATED / PROCESS</text><rect x="552" y="48" width="150" height="48" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="627" y="69"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Model registry</text><text x="627" y="85"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">one active / scope</text><rect x="552" y="178" width="150" height="48" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="627" y="199"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Inference</text><text x="627" y="215"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">score augment</text><rect x="330" y="178" width="180" height="48" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-accent)" /><text x="420" y="199"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Screening</text><text x="420" y="215"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">shadow first</text><line x1="184" y1="72" x2="212" y2="72" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#mla)"/><line x1="342" y1="72" x2="372" y2="72" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#mla)"/><line x1="522" y1="72" x2="552" y2="72" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#mla)"/><line x1="627" y1="96" x2="627" y2="178" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#mla)"/><line x1="552" y1="202" x2="510" y2="202" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#mla)"/><path d="M330,202 L104,202 L104,98" fill="none" stroke="var(--sl-color-accent)" stroke-width="1.6"  marker-end="url(#mlg)"/><text x="150" y="224"  font-size="10.5"  fill="var(--sl-color-accent-high)" text-anchor="start">new model re-enters at shadow</text><text x="363" y="244"  font-size="11"  fill="var(--sl-color-gray-3)" text-anchor="middle">Every analyst decision is a labeled example — the loop's training signal.</text></svg>
<figcaption>A new model never enters the decision path directly — it re-enters at shadow and earns its way forward.</figcaption>
</figure>

A training orchestrator ingests case decisions as labels, a scheduled policy decides when
enough new signal has accumulated to retrain, and an executor runs the job behind a
**pluggable runner** (a simulated runner for CI; a real OS-process runner for actual
training). Promoted artifacts land in a **model registry** that enforces **one active
model per scope** — versioned promotion and deprecation, never an ad-hoc swap. The
analyst's everyday work becomes the matcher's training set, and a new model re-enters
through *shadow* — back to the start of the staged rollout, never straight into the
decision.

## What's real, honestly

The **control plane is the built, load-bearing part**: the rollout modes, the KPI guard
and auto-rollback, the outcome-proof telemetry, the model-registry lifecycle, and the
feedback wiring from case decisions through to a registered model all exist and are tested
end-to-end. The matcher's *predictive lift* is an operational outcome that grows as real
disposition history accumulates — which is exactly why the machinery is built to promote
conservatively and roll back automatically rather than to trust a model on day one. The
discipline is the deliverable.
