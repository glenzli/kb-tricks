---
name: moe-cr
description: "A Mixture-of-Experts code review skill that dispatches diffs to specialized expert prompts in parallel, cross-checks against knowledge bases, and produces a risk-rated aggregated report."
---

# MoE-CR Goal
To perform a rigorous, multi-dimensional code review by routing code changes through specialized expert prompts, each constrained to a single review dimension, and aggregating their findings into a unified, risk-rated report.

# Instructions

### Step 1: Router — Context Analysis & Expert Activation
1.  **Collect the Diff**: Obtain the code changes to review (e.g., `git diff`, PR diff).
2.  **Detect Project Paradigm**: Inspect manifest files (`package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`, etc.) and directory structure to determine the project type (e.g., REST API, CLI tool, compiler, game engine, data pipeline).
3.  **Check KB Presence**: Determine if a knowledge base built by `kb-build` exists for this project.
4.  **Activate Experts**:
    -   **Always**: Layer 1 (all 6 Base Experts).
    -   **Always**: Layer 2 (1 Domain Expert, dynamically generated).
    -   **Conditional**: Layer 3 (KB Expert) — only if a KB exists.

---

### Step 2: Layer 1 — Base Expert Group (Parallel Execution)

Execute all 6 experts **in parallel**. Each expert receives the same diff but is constrained to review ONLY its designated dimension. If no findings, return empty.

#### Expert 1: Architecture
- **Focus**: Layering violations, improper coupling, dependency direction, separation of concerns.
- **Constraint**: Do NOT comment on naming, performance, or security. Only structural design.

#### Expert 2: Logic Boundary
- **Focus**: Off-by-one errors, null/undefined paths, unhandled edge cases, state machine transitions, race conditions.
- **Constraint**: Do NOT comment on style or architecture. Only correctness of logic flow.

#### Expert 3: Security
- **Focus**: Injection vectors, authentication/authorization bypass, secret exposure, unsafe deserialization, SSRF, path traversal.
- **Constraint**: Do NOT comment on performance or readability. Only attack surface.

#### Expert 4: Performance
- **Focus**: N+1 queries, unnecessary allocations, blocking I/O in hot paths, missing caching opportunities, algorithmic complexity.
- **Constraint**: Do NOT comment on security or naming. Only runtime efficiency.

#### Expert 5: Testability
- **Focus**: Hidden dependencies, global state, tight coupling that prevents mocking, missing test hooks, untestable private logic.
- **Constraint**: Do NOT comment on performance or architecture. Only ease of testing.

#### Expert 6: Maintainability
- **Focus**: Naming clarity, code duplication, cyclomatic complexity, magic numbers, readability, documentation gaps.
- **Constraint**: Do NOT comment on correctness or security. Only long-term maintainability.

#### Unified Output Format (ALL Experts)
Every finding MUST use this format:
```
[Severity: Critical|High|Medium|Low] [File:Line] 
Finding: <concise description>
Suggestion: <actionable fix>
```

---

### Step 3: Layer 2 — Domain Expert (Dynamic Generation)

1.  Based on the paradigm detected in Step 1, the Router generates a **single focused review prompt**. Do NOT use a pre-built template; generate dynamically.
2.  **Example prompts by paradigm**:
    -   **REST API**: "As a REST API design expert, review route naming, HTTP verb semantics, status code usage, and resource modeling."
    -   **Compiler/Interpreter**: "As a language implementation expert, review AST traversal correctness, visitor pattern usage, and pass ordering."
    -   **Data Pipeline**: "As a data engineering expert, review idempotency, backpressure handling, and schema evolution safety."
3.  The Domain Expert uses the same unified output format as Layer 1.

---

### Step 4: Layer 3 — KB Expert (Conditional: requires `kb-build` KB)

> Skip this step entirely if no KB exists for the project.

1.  **Fingerprint Lookup**: Identify which KB documents are linked to the changed source files via `fingerprint` metadata.
2.  **Chain Tracing**: Follow SSOT internal links from those KB documents to discover the full knowledge chain affected by this diff.
3.  **Cross-Check Audit**: For each knowledge chain touched, classify the impact:

    **Direct Impact** (the changed code's own documented flow):
    -   Does the diff alter a flow or contract that the KB documents for **this specific file**?
    -   Example: Changing `sign()` parameters in `auth.ts`, and the KB documents `auth.ts`'s signing flow.
    -   → **Auto-update**: `KB-Action: UPDATE` — the KB is definitively stale.

    **Indirect Impact** (related flows not directly changed):
    -   Does the diff **potentially break or affect** a contract/flow documented for **other modules** that depend on the changed code?
    -   Example: Changing `validateToken()` return type, and a separate KB doc records a downstream `rbacMiddleware` that consumes that return value.
    -   → **User decision**: `KB-Action: REVIEW` — flag in the report for human judgment.

4.  **KB Freshness Warning**: If the Fingerprint Commit IDs are already stale (mismatch before this review), note this as a caveat — the cross-check may be based on outdated knowledge.
5.  **Output**:
    -   Use the same unified format as Layer 1.
    -   Append a `KB-Action` field with the appropriate level:
    ```
    # Direct impact — auto-update
    [Severity: High] [src/auth.ts:42]
    Finding: sign() signature changed; KB documents old signature.
    Suggestion: Update KB to reflect new RS256 + privateKey parameter.
    KB-Action: UPDATE api/authentication.md

    # Indirect impact — user review
    [Severity: Medium] [src/auth.ts:42]
    Finding: validateToken() return type changed; downstream rbacMiddleware 
             documented in KB may be affected.
    Suggestion: Verify rbacMiddleware still handles new return shape.
    KB-Action: REVIEW api/auth-flow.md (indirect: rbac dependency chain)
    ```

---

### Step 5: Aggregator — Merge, Deduplicate & Rate

1.  **Collect** all expert outputs (Layer 1 + Layer 2 + Layer 3 if active).
2.  **Deduplicate**: If multiple experts flagged the same `[File:Line]`, merge into a single finding. Preserve the highest severity and combine suggestions.
3.  **Conflict Resolution**: When experts contradict each other, resolve by priority:
    ```
    Security > Correctness (Logic Boundary) > Performance > Maintainability
    ```
    Document the conflict and the resolution rationale in the report.
4.  **Risk Rating**: Assign an overall risk level based on the highest-severity unresolved finding:

    | Highest Finding | Overall Risk | Merge Recommendation |
    |----------------|-------------|---------------------|
    | Critical | 🔴 Critical | **Block merge** |
    | High | 🟠 High | Block merge, needs fix |
    | Medium | 🟡 Medium | Merge with follow-up |
    | Low | 🟢 Low | Merge OK |
    | None | ✅ Clean | Merge OK |

5.  **Final Report Structure**:
    ```markdown
    # Code Review Report
    ## Risk: [🔴|🟠|🟡|🟢|✅] [Level]
    ## Summary
    <1-2 sentence overview>
    ## Critical & High Findings
    <grouped findings>
    ## Medium & Low Findings
    <grouped findings>
    ## KB Impact (if applicable)
    <KB-Action items for kb-update>
    ## Conflicts Resolved
    <expert disagreements and resolutions>
    ```

# Examples

## Example: Reviewing a PR that adds rate limiting to an Auth API
1.  **Router**: Detects Node.js REST API (`package.json`), KB exists.
2.  **Layer 1** (parallel):
    -   *Architecture*: "Rate limiter is implemented inside the controller instead of as middleware." `[Medium]`
    -   *Security*: No findings (rate limiting improves security).
    -   *Performance*: "Redis lookup on every request without connection pooling." `[High]`
    -   *Logic Boundary*: "Rate limit counter resets on server restart (in-memory fallback)." `[High]`
    -   *Testability*: No findings.
    -   *Maintainability*: No findings.
3.  **Layer 2** (Domain — REST API): "Rate limit headers (`X-RateLimit-Remaining`) not set in response." `[Medium]`
4.  **Layer 3** (KB Expert): KB documents `Request → AuthMiddleware → Controller` flow. The new rate limiter is inserted but **not reflected in the KB chain**. `[KB-Action: UPDATE api/auth-flow.md]`. Cross-check finds no contract breakage.
5.  **Aggregator**: Risk = 🟠 High. 2 High findings (Redis pooling + in-memory fallback), 2 Medium findings. KB needs update.
