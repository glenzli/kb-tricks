---
name: kb-update
description: "An incremental knowledge base maintenance skill that detects documentation rot via fingerprints and performs scoped updates, referencing kb-build for creation tasks."
---

# KB Update Goal
To keep an existing knowledge base fresh and accurate by detecting source code changes via Fingerprint diffing, performing scoped rewrites, and running targeted validation—without a full rebuild.

# Prerequisites
- A knowledge base previously built by the `kb-build` skill, with Fingerprint metadata in every KB file.
- The `kb-build/SKILL.md` must be accessible for referenced steps.

# Instructions

### Step 1: Fingerprint Diff
1.  Scan all KB files for their `fingerprint` YAML section.
2.  For each recorded source file, compare its `commit` ID against the current `git log --oneline -1 <file>`.
3.  Classify each KB file:
    -   **Fresh**: All fingerprints match → skip.
    -   **Stale**: One or more fingerprints mismatch → mark for update.
    -   **Orphaned**: A recorded source file no longer exists → mark for review/removal.

### Step 2: Impact Analysis
1.  For each **Stale** KB file, run `git diff <old_commit>..<current_commit> -- <source_file>` to understand the nature of the change.
2.  Classify the change scope:
    -   **Patch**: Signature/behavior unchanged, only internals modified → minor KB text update.
    -   **Breaking**: Public API signature, return type, or contract changed → KB rewrite of affected sections.
    -   **New Module**: Entirely new source files detected that are not covered by any KB file → requires new KB file creation.
3.  **Cascade Check**: Follow SSOT internal links in the stale KB file to identify other KB files that reference it. Mark those for review as well.

### Step 3: Scoped Rewrite / Creation
1.  **For Patch changes**: Update the affected paragraphs in the existing KB file. Preserve the overall document structure.
2.  **For Breaking changes**: Rewrite the affected sections. Update all SSOT cross-references that point to the changed definitions.
3.  **For New Modules**: → **Reference `kb-build/SKILL.md` Step 1 (Cognitive Mapping)** to determine if the new module is High-Signal. If yes, → **Reference `kb-build/SKILL.md` Step 2 (Structural Design)** to create the new KB file with proper hierarchy and Mermaid diagrams where applicable.

### Step 4: GLOSSARY Sync
1.  → **Reference `kb-build/SKILL.md` Step 4 (Semantic Trigger Glossary)**.
2.  Scan all updated/new KB files for terminology changes:
    -   **New terms**: Add to `GLOSSARY.md` with synonyms and KB section mapping.
    -   **Renamed terms**: Update existing entries, preserve old names as synonyms.
    -   **Removed terms**: Mark as deprecated rather than deleting (prevents broken retrieval paths).

### Step 5: Targeted Validation
1.  → **Reference `kb-build/SKILL.md` Step 5 (3-D Adversarial Validation)** for format and scoring rules.
2.  **Reduced Scope**: Design 1-2 questions **per changed KB file** (not 3-5 as in full build).
3.  At least one question must cover the **specific change** (e.g., "What is the new return type of `authenticate()`?").
4.  If a **New Module** was created, increase to 2-3 questions for that file to ensure adequate coverage.
5.  **Iteration**: Same rules as `kb-build` Step 5—if score < 95%, update and retry (up to 2 iterations).

### Step 6: Fingerprint Refresh
1.  Update the `fingerprint` section of **every** modified or newly created KB file with the current Git Commit IDs.
2.  Set `maintenance.status` to `"linked"`.
3.  For **Orphaned** KB files that were removed, ensure no dangling SSOT links remain in other KB files.

# Examples

## Example: A JWT signing algorithm was changed from HS256 to RS256
1.  **Diff**: `auth.ts` fingerprint mismatch detected. `git diff` shows `sign()` now uses `RS256` and accepts a `privateKey` parameter.
2.  **Impact**: **Breaking** — Public API signature changed. Cascade check finds `GLOSSARY.md` references "HS256".
3.  **Rewrite**: Update `api/authentication.md` to reflect new signing method and parameter. Update Mermaid sequence diagram.
4.  **Glossary**: Add "RS256", "Asymmetric Signing". Keep "HS256" as deprecated synonym.
5.  **Validate**: Ask: "What key type does `sign()` require now?" — Subagent must answer from KB only.
6.  **Fingerprint**: Refresh `auth.ts` commit ID.
