---
title: Grounded retrieval (RAG)
description: How the DPS agent tier approaches retrieval-augmented generation — hybrid search, self-hosted embeddings, citation-or-abstain, and the RAG-specific security surface.
sidebar:
  order: 3
---

The export drafter works on structured data. The next agent — a case-investigation
copilot — has to answer questions whose answers live in *prose*: "what does OFAC's
guidance say about facilitation?", "which licence exception applies here?", "how
have we dispositioned similar matches before?". Retrieval-augmented generation is
how an agent answers those grounded in real passages instead of hallucinating.

## Grounding is the safety mechanism, not a feature

In a compliance setting an un-cited AI answer is worthless and a fabricated one is
dangerous. So RAG here isn't "make the model smarter" — it's a control. It turns
the copilot from *ask the model* into *find the passage, summarize it, and show me
where it came from*. That shape — retrieve, then answer only from what was
retrieved, with citations — is the defensible posture the domain requires, and it
extends the drafter's existing guard: "reject ungrounded numbers" becomes "reject
unsupported claims."

## Architecture

Three decisions, each reusing what the platform already runs:

- **Self-hosted embeddings, behind a port.** An `EmbeddingPort` (a Python
  `Protocol`, sibling to the `LlmPort`) with a self-hosted first adapter — an
  embedding model served via Ollama on the inference host. Same rationale as the
  [agent foundation](/ai/agentic-foundation/): provider independence and an on-prem
  privacy boundary. Embeddings *invert back to their source text*, so keeping them
  on-prem is a privacy property, not a cost choice. The model + its digest are
  pinned, so an index is always tied to the exact embedder that built it.
- **Hybrid retrieval over OpenSearch.** A `knowledge-chunks` index with both a
  dense vector field and the BM25 text field; retrieval fuses kNN + keyword scores.
  This matters: pure vector search misses the *exact* tokens compliance depends on
  — programme codes, statute numbers, entity names — while keyword-only misses
  paraphrase. Reusing OpenSearch (already running for watchlist search) avoids
  standing up a separate vector database.
- **Provenance and as-of dates.** Every chunk carries its source, section anchor,
  jurisdiction, and **effective date** — so retrieval can answer "what did the
  guidance say *on* date X," the same time-travel property the rest of the platform
  provides, and so any single source is traceable and purgeable.

The generation pipeline extends the drafter's:

<figure class="diagram">
<svg role="img" aria-label="The RAG pipeline: a query is embedded on-prem, hybrid-retrieved from OpenSearch with a tenant filter that fails closed, generated from retrieved passages only, then validated; a supported answer is cited, an unsupported one abstains with not found." viewBox="0 0 972 200" width="100%" style="height:auto;max-width:950px"><defs>
  <marker id="raa" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-gray-4)"/></marker>
  <marker id="rag" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-accent)"/></marker></defs><text x="486" y="30"  font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Retrieve, then answer only from what was retrieved — or abstain</text><rect x="16" y="70" width="104" height="52" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="68" y="101"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Query</text><rect x="136" y="70" width="128" height="52" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="200" y="93"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Embed</text><text x="200" y="109"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">nomic · on-prem</text><rect x="280" y="70" width="180" height="52" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-accent)" /><text x="370" y="93"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Hybrid retrieve</text><text x="370" y="109"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">kNN + BM25 · tenant filter</text><rect x="476" y="70" width="150" height="52" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="551" y="93"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Generate</text><text x="551" y="109"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">from retrieved only</text><rect x="642" y="70" width="150" height="52" rx="9" fill="var(--sl-color-accent-low)" stroke="var(--sl-color-accent)" /><text x="717" y="93"  font-size="14" font-weight="600" fill="var(--sl-color-accent-high)" text-anchor="middle">Cite-or-abstain</text><text x="717" y="109"  font-size="11" fill="var(--sl-color-accent-high)" text-anchor="middle">validator</text><line x1="120" y1="96" x2="136" y2="96" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#raa)"/><line x1="264" y1="96" x2="280" y2="96" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#raa)"/><line x1="460" y1="96" x2="476" y2="96" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#raa)"/><line x1="626" y1="96" x2="642" y2="96" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#raa)"/><rect x="812" y="38" width="144" height="44" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="884" y="57"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Cited answer</text><text x="884" y="73"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">with source ids</text><rect x="812" y="116" width="144" height="44" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)" /><text x="884" y="135"  font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Abstain</text><text x="884" y="151"  font-size="11" fill="var(--sl-color-gray-3)" text-anchor="middle">'not found'</text><line x1="792" y1="86" x2="810" y2="62" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#raa)"/><line x1="792" y1="106" x2="810" y2="134" stroke="var(--sl-color-gray-4)" stroke-width="1.6"  marker-end="url(#raa)"/><text x="730" y="56"  font-size="10"  fill="var(--sl-color-gray-3)" text-anchor="start">supported</text><text x="730" y="150"  font-size="10"  fill="var(--sl-color-gray-3)" text-anchor="start">unsupported</text><text x="370" y="140"  font-size="10.5"  fill="var(--sl-color-accent-high)" text-anchor="middle">missing filter → fails closed</text></svg>
<figcaption>Retrieval is tenant-scoped and fails closed. The model answers only from retrieved passages, with citations — or it abstains.</figcaption>
</figure>

If no retrieved chunk supports an answer, the agent returns *"not found in the
knowledge base"* rather than answering from parametric memory. Abstaining is a
feature.

## RAG is mostly a security problem

This is the part worth dwelling on — retrieval is the single largest attack
surface the agent tier adds, and it maps cleanly onto the
[security baseline](/ai/agent-security/):

- **Indirect prompt injection (OWASP LLM01).** A retrieved document is untrusted
  free text — it can contain "ignore your instructions." So retrieved content is
  *data-marked* and delimited, never interpreted as instructions, and the answer
  must cite it. The first corpus is also curated and closed (below), which bounds
  this from day one.
- **Corpus poisoning (LLM04).** Knowledge enters only from trusted, reviewed
  sources; every chunk's provenance is recorded so a bad source can be traced and
  removed. No unvetted or user-supplied content lands in a shared index.
- **Vector & embedding weaknesses (LLM08).** The load-bearing one in a multi-tenant
  product: **every tenant-scoped retrieval carries a tenant filter, and a missing
  filter fails closed** — no query can ever return another tenant's chunks. The
  vector store is treated as sensitive data (because embeddings reconstruct text),
  access-controlled, with no secrets or PII embedded into shared indices.

<figure class="diagram">
<svg role="img" aria-label="Tenant-scoped retrieval fails closed. Top lane: a query carrying tenant equals A, derived from the bearer, goes through hybrid retrieve with the tenant filter applied and returns tenant A chunks plus the public corpus, cited. Bottom lane: a query whose tenant filter is missing goes through hybrid retrieve with no tenant predicate and returns the empty set — it fails closed and never returns another tenant's chunks." viewBox="0 0 812 256" width="100%" style="height:auto;max-width:812px"><defs><marker id="tia" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-gray-4)"/></marker><marker id="tig" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="var(--sl-color-accent)"/></marker></defs><text x="406" y="26" font-size="13" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Every retrieval carries a tenant filter — a missing one fails closed</text><rect x="24" y="66" width="162" height="52" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="105" y="90" font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Query · tenant = A</text><text x="105" y="106" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">filter from bearer</text><rect x="300" y="66" width="176" height="52" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-accent)"/><text x="388" y="90" font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Hybrid retrieve</text><text x="388" y="106" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">kNN + BM25 · filtered</text><rect x="604" y="66" width="184" height="52" rx="9" fill="var(--sl-color-accent-low)" stroke="var(--sl-color-accent)"/><text x="696" y="90" font-size="14" font-weight="600" fill="var(--sl-color-accent-high)" text-anchor="middle">Tenant A + public</text><text x="696" y="106" font-size="10.5" fill="var(--sl-color-accent-high)" text-anchor="middle">cited</text><line x1="186" y1="92" x2="300" y2="92" stroke="var(--sl-color-gray-4)" stroke-width="1.6" marker-end="url(#tia)"/><line x1="476" y1="92" x2="604" y2="92" stroke="var(--sl-color-accent)" stroke-width="1.6" marker-end="url(#tig)"/><rect x="24" y="182" width="162" height="52" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="105" y="206" font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Query · filter missing</text><text x="105" y="222" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">bug / omission</text><rect x="300" y="182" width="176" height="52" rx="9" fill="var(--sl-color-gray-6)" stroke="var(--sl-color-gray-5)"/><text x="388" y="206" font-size="14" font-weight="600" fill="var(--sl-color-text)" text-anchor="middle">Hybrid retrieve</text><text x="388" y="222" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">no tenant predicate</text><rect x="604" y="182" width="184" height="52" rx="9" fill="var(--sl-color-accent-low)" stroke="var(--sl-color-accent)"/><text x="696" y="206" font-size="14" font-weight="600" fill="var(--sl-color-accent-high)" text-anchor="middle">∅ empty</text><text x="696" y="222" font-size="10.5" fill="var(--sl-color-accent-high)" text-anchor="middle">fails closed</text><line x1="186" y1="208" x2="300" y2="208" stroke="var(--sl-color-gray-4)" stroke-width="1.6" marker-end="url(#tia)"/><line x1="476" y1="208" x2="604" y2="208" stroke="var(--sl-color-gray-4)" stroke-width="1.6" marker-end="url(#tia)"/><text x="406" y="156" font-size="10.5" fill="var(--sl-color-gray-3)" text-anchor="middle">the vector store is sensitive data — embeddings reconstruct text; no query crosses the tenant line</text></svg>
<figcaption>Tenant scope comes from the bearer and is applied at retrieval; a missing filter returns nothing rather than another tenant’s chunks — the isolation fails closed.</figcaption>
</figure>

A faithfulness/citation eval — does every claim trace to a retrieved chunk? — gates
changes, and doubles as the adversarial surface for an injection/poisoning
red-team.

## Lowest-risk corpus first

Following the same principle as the [first agent](/ai/agentic-foundation/), the
first corpus is **curated public regulatory and guidance text** — high value, no
PII, and a closed ingestion source, so poisoning and tenant-isolation risk are
minimal while the pipeline and controls are proven. Tenant-private corpora — case
history, a tenant's own procedures — are a deliberate later slice, because they
add PII handling and hard per-tenant isolation on top.
