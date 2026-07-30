---
name: maintain-source-cohesion
description: Keep production and test code navigable through cohesive semantic ownership and growth-triggered boundary review. Use when adding substantial behavior or tests to an existing module, introducing a responsibility, refactoring or moving code, splitting a large or high-churn owner, or changing controllers, services, UI, bridges, persistence, systems, or algorithms whose current boundary may no longer fit.
---

# Maintain Source Cohesion

Optimize for task-local context and stable semantic ownership, not small files.

A semantic owner is the narrowest stable module, component, service, type, package, or translation
unit that owns a behavior's state, lifecycle, invariants, and failure policy.

## Contract

- Keep a large owner when it contains one cohesive domain, pipeline, ABI surface, or aggregate root.
- Split responsibilities that have independent lifecycles, policies, dependencies, or reasons to change.
- Prefer a few coarse semantic owners over thin wrappers or one-file-per-function structure.
- Make a typical change require one primary owner plus at most a few contract files.
- Keep tightly coupled encode/decode/validate/compile stages together unless one stage evolves independently.
- Keep controllers, public entries, registries, and application roots focused on routing, composition,
  lifecycle, compatibility, and delegation.
- Preserve public APIs, schemas, ABI layouts, serialization, ordering, numeric behavior, and supported
  runtime contracts during structural moves.
- Use size, churn, contention, and reading cost as review signals, never automatic split criteria.
- Respect the repository's language-native module mechanisms and established public boundaries.
- Keep extraction bounded to the responsibility exposed by the current work.

## Run a Growth Review

Before adding substantial code to an existing owner:

1. State its current responsibility in one sentence.
2. Map the responsibilities touched by the change: state, lifecycle, interaction, orchestration,
   validation, persistence, protocol, rendering, algorithm, or presentation.
3. Classify the change:
   - **Cohesive extension:** extend the current owner.
   - **New responsibility:** create a semantic owner and wire it through the current entry.
   - **Exposed boundary:** extract the smallest complete existing responsibility that gives the
     change a stable owner.
4. Decide explicitly to keep, extract, or defer. Do not let the current file location decide.

Review extraction when:

- The owner cannot be described without joining unrelated domains.
- It contains independently cancellable jobs, state machines, lifecycles, or failure policies.
- A normal change requires reading distant unrelated regions or changing unrelated tests.
- Unrelated product work repeatedly modifies the same file.
- A facade, compatibility layer, bridge, test target, or persistence module has become a generic hub.
- The same validation, conversion, serialization, display math, or policy exists in several paths.
- A new UI region, service, protocol family, storage concern, or algorithm stage would deepen an
  already concentrated owner.

## Make the Code Tree the Index

- Let root documentation route to subsystems, local entry points route to semantic owners, and module
  names answer likely maintenance questions.
- Keep package and application entries readable as executable indexes: exports, registration,
  composition, and concise navigation before implementation.
- Use the nearest code-owned README or module documentation only for ownership, boundary intent, and
  the next navigation step. Leave current mechanics in source.
- Update the nearest index when adding, extracting, renaming, or removing a responsibility.
- Prefer responsibility names over `helpers`, `common`, `misc`, historical names, or numbered parts.
- Give every production owner a direct dependency closure. Do not rely on an umbrella entry or
  lexical prelude to inject unrelated imports, types, macros, or helpers.
- Remove unreachable implementations, disabled reference code, and stale navigation edges. Version
  control owns obsolete history.
- Keep navigation layered: root indexes answer "which subsystem?"; local indexes answer "which owner?".

## Refactor During the Change

- Put a genuinely new responsibility in its own owner from the start.
- When the change exposes a stable boundary, move the minimal complete responsibility instead of
  adding another branch to the hub.
- Preserve behavior while moving code, then add new behavior in the new owner when practical.
- Move state, invariants, helpers, operating policy, focused tests, and terminal lifecycle handling
  together. Do not leave half an owner behind.
- Move public declarations with their implementation and private behavior. A declaration-only split
  whose implementation remains in the old hub is a navigation alias.
- Derive boundaries from mutation authority, lifecycle, invariants, and failure policy, not shared
  nouns, numeric types, UI labels, or current call proximity.
- Establish one canonical owner before extracting duplicated validation, conversion, or policy.
- When one operation atomically updates several models, projections, or compatibility views, let
  its consistency and rollback contract define one owner.
- Inspect all call sites before promoting a helper. Delete dormant branches or call an existing
  owner instead of creating a generic shared abstraction.
- Keep public signature types reachable through the intended public surface after moving or
  re-exporting APIs.
- Make every extracted owner compile or type-check from its direct imports when the language permits.
- If concurrent work or migration risk makes extraction unsafe, do not deepen the concentration.
  Record the intended boundary and use the narrowest temporary wiring.

## Load Detailed Guidance Only When Needed

- Read [async-ui.md](references/async-ui.md) for asynchronous controllers, state projection,
  declarative UI, localization, gestures, or packaged component boundaries.
- Read [native-cross-language.md](references/native-cross-language.md) for C/C++, Rust, FFI, ABI,
  translation units, embedded languages, native resources, or multiple build graphs.
- Read [large-payload-and-acceleration.md](references/large-payload-and-acceleration.md) for image,
  audio, tensor, or other large buffers; zero-copy views; caches; tiling; GPU or accelerator
  execution; or interactive preview pipelines.
- Read [test-topology-and-migration.md](references/test-topology-and-migration.md) for large test
  suites, inline-test policy, legacy structural debt, disabled tests, or test-runner migration.

Do not load a reference merely because its technology is present. Load it when the current change
touches that boundary.

## Place Tests by Responsibility

- Treat tests as part of the owner's navigation and maintenance cost.
- Keep private-invariant tests adjacent to their semantic owner and public cross-owner behavior at
  the real integration boundary.
- Move focused tests with an extracted responsibility. Leave only facade and cross-owner contracts
  at the former boundary.
- Keep fixtures with the narrowest owner that consumes them. Promote them only after genuine reuse.
- Do not expose production internals or duplicate production logic solely to make a test convenient.
- Distinguish production reachability from test reachability. Test-only use does not prove a
  production path is live.
- Keep test registration, build metadata, runtime prerequisites, and runner reachability intact
  when moving or splitting a suite.

## Avoid False Modularity

- Do not split solely to satisfy a line count.
- Do not create passive forwarding chains, one file per function, or several fragments that must
  always be read and changed together.
- Keep code together when it shares invariants, data lifetime, error policy, or one algorithmic pipeline.
- Require every extracted owner to have a semantic name, owned behavior or state, and a concrete
  reason future work would change it independently.

## Validate the Boundary

- Run focused tests for the moved owner and its public facade or cross-owner contract.
- Verify public APIs, schemas, ABI, serialization, ordering, numeric behavior, and identity fixtures
  that the move could affect.
- Compile or type-check both production and test configurations through the new dependency boundary.
- Update every maintained build, packaging, registration, generated-binding, and runtime graph that
  owns an explicit file or component list.
- For mechanical moves, compare owned declarations, symbols, tests, and registrations before and
  after. Equal totals are insufficient if one item disappeared and another was duplicated.
- Exercise a real linked or packaged consumer when compile-only checks cannot prove reachability.
- Search for stale duplicate implementations, obsolete helpers, old names, and split ownership.
- Confirm that a likely follow-up change can be made primarily in the new owner.

Finish by reporting whether the growth review kept the owner whole, extracted a responsibility, or
deferred a split for a concrete safety reason.

Treat the implementation as incomplete when it adds a distinct responsibility to an already
concentrated owner without either extracting it or explaining why extraction is currently unsafe.

Keep reusable boundary principles in this skill. Put exact file topologies, commands, named
hotspots, product semantics, generated artifacts, and zero-debt gates in the repository that owns
them.
