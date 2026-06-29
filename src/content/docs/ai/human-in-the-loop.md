---
title: Human-in-the-loop & the agent trace
description: How DPS lets an agent take consequential actions without ever deciding — propose-don't-perform, a durable four-eyes approval queue, and a three-sink trace that proves what the agent did.
sidebar:
  order: 5
---

A read-only agent is easy to defend: the worst it can do is say something wrong, and
[grounding](/ai/rag-layer/) handles that. A *write* tool is different. The moment an
agent can assign a case, change a disposition, or move money, "the agent decided" stops
being a figure of speech — and in a compliance product, that sentence is unsaleable. The
whole [foundation](/ai/agentic-foundation/) rests on agents being *tools analysts use,
not decisions the system makes*. Write tools are where that principle has to be enforced
in code, not asserted in a README.

The answer is two mechanisms working together: **propose-don't-perform** with a durable
human approval, and a **trace that proves the human, not the agent, decided.**

<figure class="diagram">
<svg role="img" aria-label="Sequence: the analyst proposes an assignment to the copilot, which writes a pending proposal to the durable approval queue and assigns nothing; a different supervisor approves, the copilot resolves it under the four-eyes rule and calls case-management with the bearer, and the action is traced." viewBox="0 0 928 322" width="100%" style="height:auto;max-width:920px"><defs>
  <marker id="hia" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-gray-4)"/></marker>
  <marker id="hig" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-accent)"/></marker></defs><text x="464" y="30"  font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Propose → durable queue → four-eyes approval → traced action</text><rect x="10" y="46" width="124" height="40" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="72" y="63"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Analyst</text><text x="72" y="79"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">proposer</text><line x1="72" y1="86" x2="72" y2="302" stroke="var(--sl-color-gray-5)" stroke-dasharray="3 4" stroke-width="1.2"/><rect x="218" y="46" width="124" height="40" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="280" y="63"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Copilot</text><text x="280" y="79"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">MCP client</text><line x1="280" y1="86" x2="280" y2="302" stroke="var(--sl-color-gray-5)" stroke-dasharray="3 4" stroke-width="1.2"/><rect x="418" y="46" width="124" height="40" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="480" y="63"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Approval queue</text><text x="480" y="79"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">durable</text><line x1="480" y1="86" x2="480" y2="302" stroke="var(--sl-color-gray-5)" stroke-dasharray="3 4" stroke-width="1.2"/><rect x="606" y="46" width="124" height="40" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="668" y="63"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Supervisor</text><text x="668" y="79"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">approver</text><line x1="668" y1="86" x2="668" y2="302" stroke="var(--sl-color-gray-5)" stroke-dasharray="3 4" stroke-width="1.2"/><rect x="794" y="46" width="124" height="40" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="856" y="63"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">case-mgmt</text><text x="856" y="79"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">+ audit</text><line x1="856" y1="86" x2="856" y2="302" stroke="var(--sl-color-gray-5)" stroke-dasharray="3 4" stroke-width="1.2"/><line x1="72" y1="110" x2="280" y2="110" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#hia)"/><text x="176" y="102"  font-size="10.5"  fill="var(--sl-color-gray-3)" text-anchor="middle">propose assignment</text><line x1="280" y1="150" x2="480" y2="150" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#hia)"/><text x="380" y="142"  font-size="10.5"  fill="var(--sl-color-gray-3)" text-anchor="middle">PENDING + approval_id</text><text x="480" y="176"  font-size="10.5"  fill="var(--sl-color-accent-high)" text-anchor="middle">nothing assigned yet</text><line x1="668" y1="214" x2="280" y2="214" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#hia)"/><text x="474" y="206"  font-size="10.5"  fill="var(--sl-color-gray-3)" text-anchor="middle">approve  (≠ proposer)</text><line x1="280" y1="252" x2="480" y2="252" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#hia)"/><text x="380" y="244"  font-size="10.5"  fill="var(--sl-color-gray-3)" text-anchor="middle">resolve · four-eyes</text><line x1="280" y1="290" x2="856" y2="290" stroke="var(--sl-color-accent)" stroke-width="1.6"  marker-end="url(#hig)"/><text x="568" y="282"  font-size="10.5"  fill="var(--sl-color-accent-high)" text-anchor="middle">assign (bearer) · traced</text></svg>
<figcaption>The agent only ever proposes. A different human approves under four-eyes, and the assignment — carrying the user's bearer — is traced.</figcaption>
</figure>

## Propose, don't perform

The first write tool — `assign_case` on the `mcp-case-action` server — does not assign a
case. It **proposes** one. The call persists a `PENDING` proposal to a durable,
tenant-scoped approval queue, returns an `approval_id`, and changes nothing else. The
agent has no path that assigns on its own; the only way a proposal becomes an assignment
is a second, human call.

That inversion is the whole game. The agent's authority is reduced to *drafting an
intent*. A human — looking at the proposal, the case, and the agent's reasoning — is the
one who acts. The model can be wrong, jailbroken, or prompt-injected through a tool
result, and the blast radius is still just "a proposal a human will read and reject."

## Four-eyes, enforced where the identity is

Approval is **four-eyes**: the approver must be a different human than the proposer.
Self-approval is refused (`409`), not merely discouraged. Because the downstream
case-management assign is idempotent, the atomic queue resolve is the single-winner —
two approvers racing can't double-assign.

Where each gate lives matters more than that it exists. The full chain is:

```
SPA → admin-console BFF → copilot (MCP client) → mcp-case-action → admin-console → case-management
        coarse: case.view                                              fine: case.assign + four-eyes
```

The Java BFF (`admin-console`) does the **coarse** gate — `case.view` — and proxies. It
can't speak MCP and it stays stateless. The Python copilot is the closed-allow-list MCP
*client*. The **fine** gate — `case.assign` plus the four-eyes rule — is enforced
*downstream, on the caller's propagated bearer*, by the real case service. The agent tier
never holds an ambient service account and never makes the authorization decision; it
carries the user's own token the whole way (the
[confused-deputy](/ai/mcp-tools/) defense), and the platform's existing permission model
does the rest. A refusal — self-approval, a missing case, an expired proposal, a caller
without `case.assign` — surfaces as `409 status=refused`, not a silent success.

## The queue is durable, shared, and not in the BFF

The approval queue can't live in the stateless aggregator that fronts it — a proposal
made now must survive for a different supervisor to approve an hour later, from a
different session. So the queue lives in the **agent tier**: an `ApprovalStore` backed by
Postgres (`agent_trace.agent_approvals`), the same database as the trace. The proposer
can withdraw their own; a supervisor can approve or reject any.

Proposals don't live forever. One not decided within a TTL (default 48h) ages out to
`EXPIRED` — via a **lazy sweep** on the next list/approve call, not a scheduler. A stale
proposal can't be silently approved days later when its context has moved on, and there's
no cron to operate or to fail quietly.

## The trace exists to prove the agent didn't decide

Every agent run writes a durable trace, and every MCP call — server, tool, arguments,
result digest — is recorded into it. This is the inverse of typical LLM observability:
the point isn't to debug the model, it's to **produce evidence**. When a regulator asks
"did your AI make this call?", the honest, defensible answer is a record showing the agent
*proposed* and a named human *approved*.

A trace fans out to **three sinks, each failure-isolated**, so losing one never blocks the
run or loses the record:

- **MinIO** — the full run body (object storage; bodies can be large).
- **Postgres** — a queryable index row.
- **Kafka** (`dps.agent.events`) — consumed by the platform's immutable
  [audit service](/architecture/platform-overview/), so agent activity lands in the same
  append-only lineage as every other domain event.

<figure class="diagram">
<svg role="img" aria-label="One agent run fans out to three failure-isolated sinks. The agent run — request, tool calls, prompts, verdicts, and the human decision — is written to MinIO as the full run body in object storage, to Postgres as a queryable index row, and to Kafka on the dps.agent.events topic, which is consumed by the immutable audit service so agent activity lands in the same append-only lineage as every other event. Losing one sink never blocks the run or loses the record." viewBox="0 0 824 262" width="100%" style="height:auto;max-width:824px"><defs><marker id="tsa" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-gray-4)"/></marker><marker id="tsg" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-accent)"/></marker></defs><text x="412" y="26" font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">One agent run → three failure-isolated sinks → immutable audit</text><rect x="24" y="104" width="168" height="58" rx="9" fill="var(--sl-color-accent-low)" stroke="var(--sl-color-accent)"/><text x="108" y="131" font-size="14" font-weight="600" fill="var(--sl-color-accent-high)" text-anchor="middle">Agent run</text><text x="108" y="147" font-size="10.5" fill="var(--sl-color-accent-high)" text-anchor="middle">tools · prompts · decision</text><rect x="360" y="48" width="210" height="46" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="465" y="69" font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">MinIO</text><text x="465" y="85" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">full run body · object store</text><rect x="360" y="110" width="210" height="46" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="465" y="131" font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Postgres</text><text x="465" y="147" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">queryable index row</text><rect x="360" y="172" width="210" height="46" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="465" y="200" font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Kafka · dps.agent.events</text><line x1="192" y1="128" x2="360" y2="71" stroke="var(--sl-color-gray-4)" stroke-width="1.6" marker-end="url(#tsa)"/><line x1="192" y1="133" x2="360" y2="133" stroke="var(--sl-color-gray-4)" stroke-width="1.6" marker-end="url(#tsa)"/><line x1="192" y1="138" x2="360" y2="195" stroke="var(--sl-color-accent)" stroke-width="1.6" marker-end="url(#tsg)"/><rect x="618" y="172" width="182" height="46" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-accent)"/><text x="709" y="193" font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Immutable audit</text><text x="709" y="209" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">same append-only lineage</text><line x1="570" y1="195" x2="618" y2="195" stroke="var(--sl-color-accent)" stroke-width="1.6" marker-end="url(#tsg)"/><text x="412" y="246" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">each sink failure-isolated — losing one never blocks the run or loses the record</text></svg>
<figcaption>A run fans out to three independent sinks; the Kafka event lands the agent’s activity in the same immutable audit lineage as every other domain event.</figcaption>
</figure>

MCP results are **digested, not dumped** — a retrieval result can be hundreds of KB, and
the trace needs the fact of the call, not a copy of the corpus.

## Red-teaming the tool surface

The defenses above are only as good as the proof that they hold. A separate, test-only
**tool-poisoning eval harness** treats each shipped server's tool description as an
attack surface: it mutates the description to smuggle instructions and asserts behavior
can't change across all three layers — **detection** (the injection scan flags it),
**containment** (output validators reject ungrounded or out-of-contract results), and
**gate** (the HITL approval still stands). Each first-party server's real
`TOOL_DESCRIPTION` is asserted clean in the same suite. The harness never deploys; it's a
standing regression test that the [closed allow-list](/ai/mcp-tools/) and the propose-only
contract can't be talked out of.

---

The shape generalizes past case assignment: any consequential agent action becomes
*propose → durable queue → four-eyes human approval → traced to immutable audit*. The
agent gets more useful; the human keeps the decision; and there's a record to prove it.
