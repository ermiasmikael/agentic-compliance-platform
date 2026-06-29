# The agentic AI tier

LLM-powered tools for compliance analysts — designed so they're **safe, grounded, and auditable**
enough to live in a regulated product. This page is the map; the security / RAG / MCP pages go deep.

## The load-bearing constraint

> **Agents are tools analysts use, not decisions the system makes.**

Screening outcomes (BLOCK / REVIEW / ALLOW) and case dispositions stay **deterministic and
rule-traceable**. The agents *retrieve*, *draft*, and *propose* — they never decide. Every agent
run is written to an immutable, durable trace whose job is to **prove the agent didn't decide**.

This isn't a nice-to-have. "The AI decided to clear this sanctioned party" is legally unsaleable to
a compliance buyer. The constraint shaped every choice below.

## Shape of the tier

A separate, polyglot tier — **Python (FastAPI), not in-JVM** — chosen deliberately (Python is the
AI mainstream; model-agnosticism is cleaner there). Standalone `uv` packages:

| Package | Role |
|---|---|
| `agent-llm` | Model-agnostic `Llm` Protocol + a LiteLLM adapter (→ on-prem Ollama). Runner + model swappable per agent. |
| `agent-security` | The enforcement layer every agent composes: deny-by-default authz, instruction/data separation, prompt-injection heuristics, output validators, HITL gate, identity, durable trace. |
| `agent-rag` | Retrieval: hybrid kNN + BM25 over OpenSearch (tenant-isolated), on-prem embeddings, **cite-or-abstain**. |
| `agent-mcp` | The MCP tool surface: a **closed allow-list** client (no dynamic discovery), bearer propagation, traced calls. |
| `agent-redteam` | A tool-poisoning eval harness (test-only) — proves a mutated tool description can't change behavior. |

Deployed agents (FastAPI, internal-only, reached through a BFF that propagates the user's bearer):

- **case-investigation copilot** — grounded Q&A (RAG → data-marked grounding → cite-or-abstain) *and*
  the MCP client for HITL case-action writes.
- **regulator-export drafter** — drafts a regulator narrative strictly from a structured evidence
  package; rejects any number not in the package (no hallucinated figures); a human reviews/edits
  before issue.

## Model-agnostic by construction

The agent loop talks to a `Llm` Protocol ([`code/llm_port.py`](../../code/llm_port.py)) — never a
provider SDK. The model and even the runner are swappable per agent behind an adapter. In the lab
that's **LiteLLM → Ollama on-prem** (qwen2.5 on CPU): $0 in model fees, and counterparty PII never
leaves the network — a selling point, not just a cost choice. Swapping to a hosted model is an
adapter + config change, no agent-code edit. The loops are **hand-rolled (no LangChain)** for
control and to own the IP.

## The copilot request flow

```mermaid
sequenceDiagram
  participant A as Analyst (SPA)
  participant BFF as admin-console (BFF)
  participant COP as Copilot (FastAPI)
  participant SEC as agent-security
  participant RAG as agent-rag
  participant OS as OpenSearch (tenant-isolated)
  participant LLM as Llm port -> Ollama
  participant TR as Durable trace

  A->>BFF: ask(question)  [bearer]
  BFF->>COP: ask  [bearer propagated]
  COP->>SEC: caller_from_bearer + injection scan (input)
  COP->>RAG: retrieve(question, tenant from bearer)
  RAG->>OS: hybrid kNN + BM25 (tenant filter)
  OS-->>RAG: chunks (+ source ids)
  COP->>LLM: complete(data-marked grounding prompt)
  LLM-->>COP: draft answer
  COP->>SEC: validate_all (cite-or-abstain, ungrounded-number, ...)
  SEC-->>COP: findings (reject -> abstain) 
  COP-->>BFF: grounded answer or abstention
  COP->>TR: AgentTrace (3 sinks; proves what ran)
```

Note what's enforced *around* the model: tenant isolation from the bearer (not a tool param),
injection scanning, grounded-only prompting, output validation that can force an abstention, and a
durable trace of the whole run.

## The five decisions behind it

Distilled from the ADRs (full set in [`../decisions/`](../decisions/)):

- **ADR-0035 — foundation:** Python tier; model-agnostic `LlmPort` + LiteLLM; hand-rolled loops.
- **ADR-0036 — export drafter:** ground strictly from structured data; reject ungrounded numbers;
  deterministic template fallback so the export is never *degraded* by the AI; HITL review.
- **ADR-0037 — security baseline:** the OWASP-LLM-Top-10 enforcement layer (see [security](security.md)).
- **ADR-0038 — RAG:** hybrid retrieval, cite-or-abstain (see [rag](rag.md)).
- **ADR-0039 — MCP:** closed allow-list, token propagation, tool-poisoning red-team (see [mcp](mcp.md)).

## Why this is the interesting part

It demonstrates the parts of AI-application engineering that are hard precisely *because* there's a
model in the loop: grounding, prompt-injection and tool-poisoning defense, the confused-deputy
problem, human-in-the-loop with provable non-autonomy, and vendor-neutral design — applied to a
domain where getting it wrong has legal consequences.
