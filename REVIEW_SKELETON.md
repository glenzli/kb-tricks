# Review Skeleton

## Review Priorities

- Preserve source-first behavior.
- Reject persistent KBs and implementation mirrors.
- Keep `SKELETON.md` a bounded semantic map rather than an exhaustive source inventory.
- Keep skills concise.
- Keep broadly triggered skill cores generic; move stack-specific guidance to conditional references.
- Keep templates generic enough to copy into unrelated repositories.
- Prefer clear constraints over broad frameworks.
- Prefer no tooling over low-value tooling.

## Block

- CLI, indexers, or automation without a current need that prompts cannot meet.
- Long-lived module, class, function, API, or current-behavior summaries.
- Requiring README files to carry internal navigation when `SKELETON.md` is the better owner.
- Test, onboarding, release, or multi-agent workflows added as completeness filler.
- Stack-specific field notes copied into a broadly triggered skill core without a loading boundary.
- Claims that treat skeletons as proof of implementation facts.
- Project-defining red lines hidden only in risk patterns instead of `Block`.

## Review Method

1. Read `SKELETON.md` and this file.
2. Inspect the actual diff and source files.
3. Lead with concrete findings and file references.
4. Flag over-detail, stale-document risk, trigger ambiguity, and scope creep.
5. Require tests only when code tooling is reintroduced.

## Verification Expectations

- Skill changes: check names, trigger descriptions, stale terminology, concise instructions,
  reference links, duplicated guidance, UI metadata, and implicit-invocation policy.
- Template changes: check source-first language and copyability.
- Tooling changes: require tests and a clear reason the LLM cannot do the task directly from source.
