# Project Skeleton

## Purpose and Boundaries

Why this project exists, what it intentionally does not do, and any scope boundary an unfamiliar
maintainer should know before reading source.

## Source Authority

Name authoritative artifact categories such as source, tests, configuration, schemas, generated
outputs, release artifacts, or maintained public documentation.

## Repository Map

List only stable concerns and the entry that routes to their semantic owner. Keep this map bounded;
do not inventory modules, classes, functions, APIs, or current behavior.

| Concern | Stable entry | Ownership boundary |
| --- | --- | --- |
| Example concern | `path/to/entry` | Durable responsibility, not an implementation summary |

## Architectural Priors

Durable choices and tradeoffs that source alone may not explain, while leaving context-dependent
decisions to the maintainer.

## Project Invariants

Constraints that future work must preserve. State policy and ownership boundaries, not today's
mechanics.

## Navigation Scope

The root skeleton should normally route a task to its likely owner in one or two hops. Add a nested
`SKELETON.md` only for a subsystem whose local ownership cannot be navigated clearly from source
entries alone. README files may serve other audiences and are not required navigation artifacts.

## Refresh Boundary

Update this file when durable purpose, boundaries, authority, ownership, navigation, invariants, or
architectural priors change. Routine implementation changes should not update it.

## Contract

Orientation only. Verify current facts against authoritative project artifacts.
