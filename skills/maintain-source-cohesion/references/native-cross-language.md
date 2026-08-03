# Native And Cross-Language Boundaries

Use this reference for C/C++, Rust, FFI, ABI, translation units, embedded languages, generated
bindings, or repositories with several maintained build graphs.

## Preserve Public Contracts

- Keep a centralized declarative ABI, wire schema, or ordered variant registry together when its
  namespace, field order, membership, generated header, or type identity is the auditable contract.
  Extract behavior-rich conversion and lifecycle policy behind it instead of fragmenting declarations.
- Treat PIMPL, opaque storage, a namespace, or one facade class as encapsulation, not proof of
  cohesion. Inventory protocol families, lifecycles, and consumer fan-out.
- Before splitting an interleaved public hub, create a complete ownership ledger for types,
  functions, overloads, aliases, constants, and forward declarations.
- Audit every type in public signatures after a move. Requests, results, errors, callbacks, and
  aliases must remain nameable through the intended public surface.
- Use declarations without definitions only where the language safely permits incomplete types.
  Require complete owners for by-value state, variants, optionals, and inline behavior.
- Keep a complete sum type with the family it closes over when ordering or membership affects
  persistence, ABI, wire identity, or exhaustive dispatch.
- Let the owner of a complete sum type also own exhaustive dispatch and representation-specific
  validation. Do not make every workflow reopen the aggregate with parallel visits.

## Complete Compilation Ownership

- Move declarations, out-of-line implementation, private helpers, and focused validation to the
  same semantic owner.
- Expose the smallest responsibility-named internal contract between translation units. Do not
  recreate a hub as `internal`, `common`, or `helpers`.
- Re-audit linkage when file-local or anonymous-namespace helpers become cross-unit operations.
  Qualify exported names and keep implementation mechanics private.
- Re-audit relative visibility after adding a module or namespace level. Package-private,
  `protected`, friendship, and parent-relative visibility describe positions in the old tree.
- Require every new production unit to compile from direct includes or imports without declaration
  order, textual include tricks, umbrella preludes, or transitive dependencies.
- Keep compatibility or umbrella headers as stable public indexes when needed, but make production
  implementations consume narrow responsibility-named headers.
- Treat an embedded shader, SQL program, generated-language block, or other independently evolving
  DSL as its own language owner even when hosted in one native source file.

## Own Bridge Contracts

- Give a large bidirectional bridge mapping one projection owner before splitting workflows around
  it. Cover nested identities, bounded collections, optional fields, geometry, and history metadata.
- Give cross-language values explicit presence and units. Do not let default values hide fields that
  one route forgot to populate.
- Keep structural boundary validation separate from route-dependent capability negotiation. The
  selected backend owns executability and provider policy.

## Validate Every Build Graph

- Update every explicit source list, generated-binding dependency, rerun manifest, IDE project,
  packaging target, and registration table that consumes the moved unit.
- Make compilation and dependency tracking consume one executable source manifest within each build
  graph. Use a fail-closed set comparison when two maintained graphs describe the same native library.
- Force a clean link through every maintained orchestration graph. An incremental build can retain
  stale objects or exercise only one manifest.
- Link at least one real consumer after adding a native unit behind a language bridge. Type checking
  and compile-only validation cannot expose an omitted object file.
- Give cross-language DTO and codec mappings a production-linked contract test at the mapping layer.
  Lower-level tests do not prove optionality, units, enum values, identities, and every field survive
  the host projection.
- For serialization, hashing, content addressing, or identity moves, compare canonical bytes and
  stable digest fixtures, not only behavioral equivalence.
- Compare declaration and symbol multisets before and after structural moves. Distinguish definitions
  from intentional forward declarations.
