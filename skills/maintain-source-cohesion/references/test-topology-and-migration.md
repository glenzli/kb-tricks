# Test Topology And Migration

Use this reference when tests obscure production ownership, live inline in growing implementation
files, form a multi-responsibility suite, depend on legacy structure, or require a gradual topology
migration.

## Respect Local Test Shape

- Follow language-native mechanisms and the repository's maintained test conventions unless the
  task explicitly changes that policy.
- Do not impose one physical layout, inline-test cap, or migration gate from this reference. Keep
  those choices in the repository that owns their costs and enforcement.
- Reconsider the current shape when tests obscure the production owner, require unrelated fixtures
  or setup, or repeatedly force one concern to change another concern's suite.
- Keep private-invariant tests adjacent to the production owner. Put public cross-owner behavior in
  integration locations that consume the real product boundary.
- Let the production owner declare its adjacent tests. Registration from a distant facade is
  ownership drift unless the test deliberately exercises that facade.
- Organize suites by production responsibility, not `misc`, `more_tests`, numbered parts, or broad
  labels such as `contract` and `integration`.

## Preserve Real Reachability

- Never make an integration test source-include, path-import, or independently compile a private
  production implementation. Consume the real build/import boundary.
- Treat production code reached only through tests as a product-reachability question. Register it
  under a real owner, move a genuine prototype to an explicit incubation/test-support location, or
  remove obsolete code.
- Do not make a private implementation public solely for tests. Give a durable internal contract
  narrow test visibility or keep its tests adjacent.
- Keep ignored external-fixture tests compilable and state the exact prerequisite and invocation.
  A permanently false compile condition is hidden dead code, not an ignored contract.
- Remove obsolete assertions, disabled runners, commented registrations, and permanently false test
  branches during the contract migration. Version control is the archive.
- Audit lexical visibility when moving nested tests. Relocate the test or grant the narrowest
  internal visibility; never widen the public API to preserve accidental access.

## Keep Test Support Owned

- Keep fixtures, builders, and harnesses with the narrowest test responsibility that consumes them.
  Promote them only after several semantic owners genuinely reuse them.
- Let fixtures construct inputs and record observable effects. Keep pass/fail conclusions in the
  consuming test instead of hiding assertions in shared mutable support.
- Import production contracts and fixtures directly. Do not recreate an umbrella prelude through
  wildcard imports or a generic support module.
- Test production-owned validators, parsers, normalizers, and policy directly through narrow
  internal visibility. Do not copy their implementation into test support.
- Split a mixed test into an adjacent unit contract and a higher-level cross-owner contract when it
  combines local invariants with orchestration, persistence, or aggregate behavior.

## Respect Repository-Owned Migration Policy

- Introduce or enforce a cap, baseline, ratchet, or history requirement only when the repository
  explicitly owns that migration policy. Do not create enforcement tooling merely because legacy
  test debt exists.
- When an active policy tracks legacy exceptions, identify exact items rather than granting a
  reusable count allowance, and shrink the exception set as debt is removed.
- Validate against the review base or history required by the local contract. If that evidence is
  unavailable, report the gap instead of inventing a weaker comparison.
- Keep migration policy, exceptions, commands, and checker implementation in the repository. Apply
  cohesion review to the checker so enforcement does not become another generic hub.

## Split Suites Without Losing Contracts

- Review a split when a suite spans independent responsibilities, repeatedly conflicts with
  unrelated changes, obscures production entry points, or is larger than the implementation it
  verifies. Treat size as a signal, not an automatic threshold.
- Move focused tests with the production responsibility in the same change. Preserve only facade and
  deliberate cross-owner contracts at the old boundary.
- Inventory test functions and runner registrations before and after. Every test must have one owner
  and remain reachable.
- Migrate compile definitions, generated fixtures, dependencies, environment variables, platform
  gates, labels, timeouts, and runner registration with each extracted executable or suite.
- Inspect the generated test registry when build files can overwrite properties through repeated
  assignment.
- Compile both production and test configurations. Test-only imports can hide an invalid production
  dependency, while production-only builds can miss the inverse test closure.
