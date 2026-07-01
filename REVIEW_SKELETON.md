# Review Skeleton

## Review Priorities

- Preserve source-first behavior.
- Reject attempts to rebuild a persistent KB or implementation mirror.
- Keep skills concise and task-shaped.
- Keep templates generic enough to copy into unrelated repositories.
- Prefer clear constraints over broad frameworks.
- Prefer no tooling over low-value tooling.

## Red Lines

- Do not add a CLI package without a clear, current need.
- Do not add long-lived module/class/function summaries.
- Do not add test/onboarding workflows as completeness filler.
- Do not treat skeleton files as proof of implementation facts.
- Do not preserve old `dev-cycle` or `.dev-cycle/context` compatibility.

## Review Method

1. Read `DEV_SKELETON.md` and this file.
2. Inspect the actual diff and source files.
3. Lead with concrete findings and file references.
4. Flag over-detail, stale-document risk, trigger ambiguity, and scope creep.
5. Treat missing tests as acceptable unless code tooling is reintroduced.

## Verification Expectations

- For documentation and skill changes, check naming, trigger descriptions, stale terminology, and internal links.
- For template changes, check that templates remain source-first and do not invite implementation mirrors.
- For any reintroduced tooling, require tests and a clear reason the LLM cannot do the task directly from source.
