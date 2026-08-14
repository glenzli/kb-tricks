---
name: maintain-source-cohesion
description: Keep production and test code navigable through cohesive semantic ownership. Use when substantial behavior grows an existing owner, a new responsibility appears, code moves or splits, a large test suite or test topology changes, or work touches a controller, facade, service, bridge, persistence boundary, UI surface, system, or algorithm whose ownership may no longer fit. Skip small changes that do not pressure an ownership boundary.
---

# Maintain Source Cohesion

Use these principles to improve architectural judgment, not to impose a decomposition workflow.
Optimize for task-local context, stable ownership, and safe change boundaries rather than small files
or uniform structure.

A semantic owner is the narrowest stable module, component, service, type, package, or translation
unit that owns a behavior's state, lifecycle, invariants, mutation authority, and failure policy.

## Orient From the Repository

- Read the nearest `SKELETON.md` for durable boundaries and navigation. If it is absent, a legacy
  `DEV_SKELETON.md` may provide the same orientation.
- Treat skeletons as priors. Verify current behavior and dependency facts in source, tests, schemas,
  build graphs, and packaged artifacts.
- Let the root skeleton route to a subsystem and local source entries route to the owner. README may
  serve product or public documentation and is not required to be the internal navigation index.
- Add or update a nested `SKELETON.md` only when a large subsystem cannot expose its stable owners
  clearly through ordinary source entries in one or two hops.

## Judge the Ownership Boundary

Keep a large owner when it represents one cohesive domain, aggregate, pipeline, ABI surface, or
consistency boundary. Size, churn, contention, and reading cost are signals to investigate, not
automatic split criteria.

Reconsider the boundary when the change reveals one or more of these conditions:

- Independently cancellable jobs, state machines, lifecycles, or failure policies share one owner.
- Unrelated product work repeatedly changes the same controller, facade, registry, bridge, storage
  module, or application root.
- A normal change requires understanding distant regions or modifying tests for another concern.
- Validation, conversion, serialization, display math, or operating policy is duplicated across paths.
- A new UI region, protocol family, persistence concern, service, or algorithm stage has its own
  durable reason to evolve.
- A public entry has accumulated domain behavior instead of routing, composition, compatibility,
  lifecycle coordination, or delegation.

The current file location is weak evidence. Prefer boundaries derived from state ownership,
mutation authority, lifecycle, invariants, dependency closure, and error or rollback policy.

## Choose the Smallest Coherent Change

- Extend the current owner when the behavior shares its state and invariants.
- Give a genuinely new responsibility a semantic owner from the start when the boundary is clear.
- When existing concentration is exposed, extract the smallest complete responsibility that makes
  the requested change easier to own. Do not refactor unrelated hotspots for symmetry.
- Preserve behavior during a structural move when practical, then add the new behavior through the
  new boundary.
- If concurrency, migration risk, or an unstable contract makes extraction unsafe, use narrow
  temporary wiring without deepening the old owner's policy surface. Leave a boundary note only
  when it will materially help the next change.

Move an owner as a unit: state, invariants, helpers, operating policy, focused tests, terminal
lifecycle handling, and the public declarations that define the behavior. A declaration-only file,
forwarding chain, or wrapper whose implementation remains in the old hub is a navigation alias, not
a meaningful extraction.

When one operation atomically updates multiple models, projections, caches, or compatibility views,
let its consistency and rollback contract define one owner. Do not split that operation merely
because its data crosses several nouns or layers.

## Preserve Navigability

- Keep package entries, module declarations, registries, application roots, bridge facades, and
  top-level controllers readable as composition boundaries.
- Prefer responsibility names over `helpers`, `common`, `misc`, historical names, or numbered parts.
- Give each owner a direct dependency closure. Do not depend on an umbrella entry or lexical prelude
  to inject unrelated imports, types, macros, or helpers.
- Inspect call sites before promoting a helper. Establish one canonical owner before extracting
  shared validation, conversion, serialization, or policy.
- Remove unreachable implementations, stale navigation edges, obsolete names, and disabled
  reference code when they are owned by the current change. Version control owns old history.
- Update `SKELETON.md` only when a stable responsibility or navigation route was added, moved,
  renamed, or removed. Current mechanics stay in source.

## Preserve Contracts While Moving Code

- Preserve public APIs, schemas, ABI layouts, serialization, ordering, numeric behavior, identity,
  and supported runtime contracts unless the task explicitly changes them.
- Keep public signature types reachable through the intended surface after moving or re-exporting APIs.
- Make extracted owners compile or type-check from direct imports when the language permits.
- Update every maintained build, packaging, registration, generated-binding, and runtime graph that
  explicitly owns the moved file or component.
- Treat source reachability, test reachability, and packaged runtime reachability as distinct facts.

## Keep Tests With Their Evidence Owner

- Keep private-invariant tests with the semantic owner and public cross-owner behavior at the real
  integration boundary.
- Move focused tests with an extracted responsibility. Leave only facade and cross-owner contracts
  at the former boundary.
- Keep fixtures with the narrowest owner that consumes them; promote them only after genuine reuse.
- Do not expose production internals or duplicate production logic solely to make a test convenient.
- Preserve test registration, build metadata, runtime prerequisites, and runner reachability when a
  suite moves.

## Avoid False Modularity

- Do not split solely for line count, a preferred file shape, or document symmetry.
- Do not create one-file-per-function structures or fragments that must always be read and changed together.
- Keep tightly coupled encode/decode/validate/compile stages together unless one stage has an
  independent lifecycle or policy.
- Require an extracted owner to have a semantic name, owned behavior or state, and a concrete reason
  future work could change it independently.
- Prefer a few coarse owners over many passive forwarding layers.

## Load Detailed Guidance Only When the Boundary Is Active

- Read [async-ui.md](references/async-ui.md) for asynchronous controllers, state projection,
  declarative UI, localization, gestures, or packaged component boundaries.
- Read [native-cross-language.md](references/native-cross-language.md) for C/C++, Rust, FFI, ABI,
  translation units, embedded languages, generated bindings, or multiple build graphs.
- Read [large-payload-and-acceleration.md](references/large-payload-and-acceleration.md) for image,
  audio, tensor, or other large buffers; zero-copy views; caches; tiling; accelerator execution; or
  interactive preview pipelines.
- Read [test-topology-and-migration.md](references/test-topology-and-migration.md) for large suites,
  inline-test policy, legacy structural debt, disabled tests, or test-runner migration.

Do not load a reference merely because its technology exists in the repository.

## Validate in Proportion to the Boundary

- Exercise focused owner tests and the facade or cross-owner contract affected by the change.
- Check the compatibility properties the move could alter, including schema, ABI, ordering, numeric,
  serialization, and identity fixtures.
- Build or type-check production and test configurations through the new dependency boundary.
- For mechanical moves, compare named declarations, symbols, tests, and registrations; equal totals
  alone do not prove nothing was lost or duplicated.
- Exercise a real linked or packaged consumer when compile-only checks cannot prove reachability.
- Confirm that a likely follow-up change can be made primarily in the intended owner.

Keep exact topologies, named hotspots, project semantics, commands, generated artifacts, and
zero-debt gates in the repository that owns them. Report a keep/extract/defer decision only when it
helps explain a non-obvious boundary or handoff; it is not a ritual required for every edit.
