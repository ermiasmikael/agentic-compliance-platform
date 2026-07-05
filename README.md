# Agentic Compliance Platform — engineering case study

A curated, sanitized engineering case study of **PROVA**, a denied-party-screening
(sanctions / PEP / adverse-media) compliance platform I designed and built solo — told
AI-tier-forward, with a focus on building LLM-powered analyst tools that are *safe, grounded, and
auditable* enough for a regulated product. Check PROVA in action at: **[Infopole](https://infopole.org)**
is the company.

**Honest framing:** this is a deep, from-scratch engineering exercise — a production-*grade* platform
running on a private lab, not a shipped SaaS with paying customers. There are **no fabricated users or
metrics** here. What's on display is the breadth and the engineering judgment, built end to end by one
person: an event-driven microservice platform, a relationship-graph intelligence layer, and an agentic
AI tier designed against the OWASP LLM Top 10.

## Read the portfolio

The rendered articles are the portfolio. Read them on the live site:

**→ https://ermiasmikael.github.io/agentic-compliance-platform**

The site is an Astro Starlight build of the article sources in [`src/content/docs/`](src/content/docs/)
(architecture, applied-AI, ML, and decision deep-dives), with representative sanitized code excerpts in
[`code/`](code/). It deploys to GitHub Pages automatically on push to `main`.

## Build locally

```bash
npm install
npm run build   # outputs to dist/
npm run dev     # local preview
```
