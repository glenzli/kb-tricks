---
name: kb-query
description: "Answer repository questions with KB routing, existing-docs/source fallback, explicit provenance, and isolated inference."
---

# KB Query

Use when the user asks how the repository works, where to look, or why a
behavior exists.

## Hard Rules

- KB is routing/context, not authority.
- Every factual answer line must mark source type: `[KB]`, `[Source Fallback]`, or `[Existing Docs]`.
- Inference must be isolated under uncertainty and marked `[Inference]`.
- Do not scan the whole KB; route through glossary, index, manifest, and links.
- If KB is stale, dirty, draft, or missing, say so.

## Routing

Use available fast paths:

- `.agent/kb/index.json`
- `.agent/kb/GLOSSARY.md`
- `KB_PLAN.md`
- `kb docs --summary-json`
- SSOT links from relevant KB docs

## Steps

1. Parse the user question and likely terms.
2. Find candidate KB docs through glossary/index/manifest.
3. Read only relevant KB sections.
4. Follow links only when needed.
5. Check freshness from frontmatter and audit/index if available.
6. If KB is incomplete, read relevant existing docs.
7. If factual API/logic details remain unclear, read precise source sections.
8. Separate facts from inference.
9. Lint with `kb query-lint` when drafting a reusable answer.

## Output

```markdown
## Answer
<facts with source markers>

## Uncertainty & Inference
<none or clearly marked inference>

## Citations
- KB: ...
- Source: ...
- Existing Docs: ...

## KB Status
<fresh / stale / dirty / missing coverage>
```
