---
name: cycle-onboard
description: "Generate a focused onboarding path for a new developer or agent from fresh project context."
---

# Cycle Onboard

Use when a new contributor, maintainer, or AI agent needs a guided entry path.

## Hard Rules

- Warn if KB is stale, dirty, draft-only, or missing important areas.
- Prefer maintained docs when they already explain user-facing behavior.
- Do not present KB as authority.
- Keep the result short enough to be useful.

## Steps

1. Run or consult `kb-audit` summary if available.
2. Read `KB_PLAN.md`, `GLOSSARY.md`, fresh KB docs, and existing docs listed in config.
3. Skip `deprecated` tasks and prefer docs targets for `merged-into-docs`.
4. Order reading from foundations to dependent modules.
5. Summarize each topic in 2-3 sentences.
6. Add a small comprehension check.

## Output

Create or propose `.agent/kb/ONBOARDING.md`:

- KB/docs freshness warning.
- Recommended reading order.
- Key concepts.
- Role-specific notes when requested.
- 3-5 comprehension questions with reference answers.

