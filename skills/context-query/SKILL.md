---
name: context-query
description: "Answer repository questions with Context routing, existing-docs/source fallback, explicit provenance, and isolated inference."
---

# Context Query

Use when the user asks how the repository works, where to look, or why a
behavior exists.

## Hard Rules

- Context is routing/context, not authority.
- Every factual answer line must mark source type: `[Context]`, `[Source Fallback]`, or `[Existing Docs]`.
- Inference must be isolated under uncertainty and marked `[Inference]`.
- Do not scan the whole Context; route through glossary, index, manifest, and links.
- If Context is stale, dirty, draft, or missing, say so.

## Routing

Use available fast paths:

- `.dev-cycle/context/index.json`
- `.dev-cycle/context/GLOSSARY.md`
- `CONTEXT_PLAN.md`
- `dev-cycle context docs --summary-json`
- SSOT links from relevant Context docs

## Steps

1. Parse the user question and likely terms.
2. Find candidate Context docs through glossary/index/manifest.
3. Read only relevant Context sections.
4. Follow links only when needed.
5. Check freshness from frontmatter and audit/index if available.
6. If Context is incomplete, read relevant existing docs.
7. If factual API/logic details remain unclear, read precise source sections.
8. Separate facts from inference.
9. Lint with `dev-cycle context query-lint` when drafting a reusable answer.

## Output

```markdown
## Answer
<facts with source markers>

## Uncertainty & Inference
<none or clearly marked inference>

## Citations
- Context: ...
- Source: ...
- Existing Docs: ...

## Context Status
<fresh / stale / dirty / missing coverage>
```
