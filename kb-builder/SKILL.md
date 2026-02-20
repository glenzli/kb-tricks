---
name: kb-builder
description: "An advanced skill for building highly efficient, agent-consumable, and validated knowledge bases using a cognitive-mapping pipeline."
---

# KB Builder Goal
To create a high-signal, low-maintenance knowledge base that acts as a **Cognitive Map** for codebases, focusing on stable interfaces and verified through a rigorous 3-D adversarial audit.

# Instructions

### Step 1: Cognitive Mapping & Paradigm Analysis
1.  Analyze the repository to identify "High Signal" vs "High Noise" logic.
    -   **KB Inclusion (High Signal)**: Cross-module contracts, implicit state transitions, design trade-offs (the "Why"), and Public API stability.
    -   **KB Exclusion (High Noise)**: Self-explanatory logic, boilerplate, and transient internal implementation details.
2.  Draft an outline prioritizing the **Cognitive Map**—how components interact rather than just what they are.

### Step 2: Adaptive Structural Design
1.  Design a hierarchical structure (e.g., `api/`, `flows/`, `models/`).
2.  **Visual Interaction**: For complex Public API chains or interaction logic, **MUST** include Mermaid diagrams to visualize data flow/dependency.
3.  Keep granularity balanced: Aim for 1 KB file per 1-3 related core source files to minimize maintenance "blast radius".

### Step 3: Redundancy-free Indexing (SSOT)
1.  Maintain a "Single Source of Truth" (SSOT). Use internal Markdown links to reference stable definitions instead of duplicating them.

### Step 4: Semantic Trigger Glossary
1.  Generate `GLOSSARY.md` as a **Semantic Trigger List** for Retrieval Agents.
2.  Include technical jargon, project-specific keywords, and **synonyms** that a user might use in a query.
3.  Map each term to its corresponding section in the KB.

### Step 5: 3-Dimensional Adversarial Validation (The Loop)
1.  **Question Design**: The Main Agent (with code access) designs 3-5 questions across three dimensions:
    -   **Architectural**: "How to extend X without breaking Y?"
    -   **Design Intent**: "Why was pattern Z chosen for this module?"
    -   **Boundary/Edge**: "What happens when input A violates contract B?"
2.  **Subagent Execution**: The Subagent (KB access **ONLY**) must answer. The Main Agent must ensure the Subagent cannot access source code during this step.
3.  **Mandatory Citations**: Subagent MUST provide citations (file path and line numbers) from the KB.
4.  **Anti-Hallucination Scoring**:
    -   **95%+ Score Required**: Points are deducted for information that is correct but *not in the KB* (detected general knowledge usage).
5.  **Iteration**: If validation fails, update the KB to fill the informational gap and repeat (up to 3 iterations).

### Step 6: Fingerprinting & Maintenance (Traceability)
1.  Include a "Fingerprint" section at the end of **EVERY** KB file.
2.  List source files and their **Git Commit ID** at the time of creation.
3.  **Maintenance Note (Reader Guidance)**: If a future reading skill detects a Commit ID mismatch:
    -   **Warning**: Mark the document as "Potentially Outdated".
    -   **fallback**: Proactively re-read the source code to supplement the KB content.
4.  **Example Format**:
    ```yaml
    ---
    fingerprint:
      - file: "/src/core/engine.py"
        commit: "7d8e9f0a"
    maintenance:
      status: "linked"
      strategy: "code-supplemental"
    ---
    ```

# Examples

## Example: Documenting an "Authentication & Authz System"
1.  **Mapping**: Identify `login()`, `validateToken()`, and `rbacMiddleware` as High-Signal. Ignore internal salt-generation helpers.
2.  **Diagram**: Include a Mermaid sequence diagram showing the `Request -> Middleware -> JWT Verify -> Controller` flow.
3.  **Glossary**: Include "JWT", "Bearer Token", "Claims", and "Role-Based Access Control".
4.  **Audit**: 
    -   *Arch*: "How do I add a new 'SuperAdmin' role?"
    -   *Design*: "Why are we using asymmetric (RS256) instead of symmetric (HS256) signing?"
    -   *Boundary*: "What happens if the Public Key is rotated while a token is still active?"
