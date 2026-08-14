# Skills

Source-first skills:

- `skeleton-init`: create `SKELETON.md`, `REVIEW_SKELETON.md`, and `AGENTS.md` from the maintained
  bundle-level templates.
- `skeleton-refresh`: update durable orientation only.
- `skeleton-audit`: find bloat, stale claims, and source-first violations.
- `maintain-source-cohesion`: apply architectural judgment to semantic ownership and task-local navigation.
- `review-skeleton`: review source and diffs with project preferences.

They supplement model judgment and do not replace source reading. New projects use `SKELETON.md`;
skills recognize `DEV_SKELETON.md` only as a legacy fallback during migration.

Keep skill directories intact. `skeleton-init` additionally requires the repository or plugin
bundle's top-level `templates/` directory.
