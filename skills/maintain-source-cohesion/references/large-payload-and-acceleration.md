# Large Payload And Acceleration Boundaries

Use this reference when a change moves image, audio, tensor, geometry, or other large buffers
through caches, previews, tiles, native bridges, GPUs, or other accelerators.

## Own The Payload Lifecycle

- Treat allocation, ownership, format, dimensions, stride, color or sample interpretation,
  synchronization, and release as one payload contract.
- Budget copies across the full producer-to-consumer path. Removing one obvious copy is not useful
  if encoding, bridge conversion, upload, or presentation immediately recreates it.
- Let zero-copy views borrow from a stable owner whose lifetime is explicit. A pointer plus length
  is not an ownership model.
- Keep immutable source data separate from mutable working state and presentation caches. Make each
  invalidation boundary name the identity it invalidates.
- Use byte or resource cost for admission and eviction, then enforce aggregate resident limits.
  Entry count alone does not bound memory when payload dimensions vary.
- Keep visibility, readiness, and residency distinct. Something may be visible but backed by stale
  data, ready but not admitted to memory, or resident but no longer current.

## Prepare Execution Once

- When planning and execution depend on the same parameters, prepare one opaque plan containing
  normalized inputs, chosen path, resource requirements, and provenance.
- Make query, cache lookup, scheduling, and execution consume that same plan. Re-deriving decisions
  independently creates capability and cache-key drift.
- Keep fallback selection and accelerated execution behind one semantic contract. Record which path
  produced an output so failures and performance regressions remain diagnosable.
- Keep portable fallback algorithms outside optional third-party adapters, and validate both
  dependency-present and dependency-absent builds.
- Cache compiled or prepared resources by their complete semantic identity, not a convenient subset
  of visible parameters.

## Preserve Authored Topology When Present

Apply this section only when a payload derives from authored continuous geometry or time-domain intent.

- Model authored input as paths, regions, envelopes, kernels, or other semantic primitives before
  sampling it into execution-specific points, frames, or tiles.
- Keep coordinate transforms explicit and invariant across preview scale, full resolution, tiles,
  crop, orientation, and display projection.
- Define overlap and boundary policy with the algorithm owner. Tiling must not introduce seams,
  truncate support regions, or change edge behavior.
- Keep sampling density an execution detail derived from scale and support radius, not persisted
  user intent unless the product contract explicitly requires it.

## Measure The Final Consumer

- Instrument admission, queueing, preparation, execution, transfer, conversion, and presentation
  separately. End-to-end latency cannot be inferred from kernel time alone.
- Measure interactive latency after warm-up as well as first-use latency, throughput, peak resident
  memory, copy volume, cancellation delay, and stale-result rate.
- Place diagnostics at the final consumer boundary so a fast producer cannot hide a blocked upload,
  conversion, or presentation path.
- Keep counters and provenance bounded and stable enough for automated comparison.

## Validate Parity And Pressure

- Keep deterministic portable tests for coordinate math, plan identity, admission, eviction,
  cancellation, and fallback behavior.
- On real accelerated hardware, compare representative outputs with an accepted reference using
  domain-appropriate tolerances. Include borders, tiles, odd dimensions, and large support regions.
- Exercise memory pressure, rapid supersession, resize or scale changes, and resource loss. Verify
  that stale work is rejected and resident memory returns within policy.
- Benchmark representative payloads through the final consumer. A synthetic kernel benchmark does
  not establish interactive performance.
