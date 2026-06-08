# 03 — PRD-Driven Flow

> Read this before you start any feature work.
> The short version: no code without a PRD.

---

## Why we do this

Features that ship without a written spec cause two problems:

1. **Scope disagreements show up in code review**, where they're expensive to fix. "Should this delete cascade?" is a one-minute question before coding and a three-hour diff conversation at review.
2. **The feature becomes undocumented the moment the PR merges.** Six months later, nobody knows if the behavior is intentional or accidental.

The PRD process is the fix: agree on scope in writing *before* implementation.

---

## The gate (applies to every feature)

Before writing any feature code, the agent (and humans) check:

1. Does a PRD in `docs/prd/` already cover this scope?
   - **Yes, and the work fits** → reference it in the PR description; proceed.
   - **Yes, but the work expands it** → extend the existing PRD or create a new one that declares `updates: PRD-NN`.
   - **No** → stop; run `/prd` to draft one; get approval; then implement.

The gate does NOT fire for bug fixes, pure refactors, dependency bumps, lint/CI tweaks, or doc-only edits.

---

## What a PRD contains

Every PRD (`docs/prd/NN-slug.md`) answers:

| Section | Question |
|---|---|
| Problem | What breaks for the user today? |
| Functional requirements | What must the system do? |
| Non-goals | What explicitly won't we do? |
| Success metrics | How do we know it worked? |
| Open questions | What is still unresolved? |

See [`docs/prd/00-template.md`](../prd/00-template.md) for the full template.

---

## Numbering and status

- PRDs are numbered sequentially: `00`, `01`, `02`, … (2-digit, zero-padded).
- `PRD-00` is the chain root (foundations, constraints, vocabulary). Every other PRD inherits from it.
- **Status values**: `Draft` → `Approved` → `Implemented` → `Superseded`.
- Never implement against a PRD still in `Draft`. Wait for `Approved`.

---

## Linking PRDs to PRs

The PR template has a dedicated **Linked PRD** line. Fill it in; a missing PRD reference is a blocker for the reviewer.

On merge:
1. Bump the PRD's `updated:` to the merge date.
2. Flip `status: Approved` → `status: Implemented`.
3. Append a Change log line: `YYYY-MM-DD — Implemented (PR #NNN)`.

---

## Architectural decisions (ADRs)

If a feature requires a **non-obvious technical choice** (new data store, new auth model, new library category, deviation from an existing rule), an ADR is required alongside the PRD.

ADRs live in `docs/architecture/adr/` and follow 4-digit numbering (`0001`, `0002`, …). Once `Accepted`, they are frozen — never edited, only superseded by a new ADR.

The `/prd` skill detects when an ADR is warranted and offers to scaffold both documents at once.

---

## The `/prd` skill

Running `/prd` starts a structured interview and scaffolds the PRD document from the canonical template. It:

1. Asks about the problem, users, and scope.
2. Detects whether an ADR is also needed.
3. Writes `docs/prd/NN-slug.md` (and optionally `docs/architecture/adr/NNNN-slug.md`).
4. Updates the PRD index table in `docs/prd/README.md`.

You can also draft a PRD manually from `docs/prd/00-template.md` — the skill just automates the structured interview.

---

## Example: what the gate looks like in practice

**User:** "Add a way to bulk-export user data as CSV."

**Agent (before touching any code):**
1. Searches `docs/prd/` — no file matches "export" or "CSV".
2. This is a new user-facing flow — a PRD is required.
3. Runs `/prd` to draft `docs/prd/03-bulk-export.md`.
4. Surfaces the draft for review: "Draft PRD ready. Confirm scope before I implement?"
5. After approval, implements against the approved PRD.

**User:** "Fix the typo in the error message on the login page."

**Agent:**
- Bug fix, no behavior change → gate doesn't apply → implement directly.
