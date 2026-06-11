# PRD-driven development

**Scope:** Repo-wide. This rule fires *before* any code-writing rule.

**See also:** [`docs/prd/README.md`](../prd/README.md) (human flow), [`commit-and-pr.md`](commit-and-pr.md), [`boundaries.md`](boundaries.md), [`docs/architecture/adr/`](../architecture/adr/).

## When this rule applies

Before writing any code that:

- Adds a new feature or new user-facing flow.
- Adds a new endpoint with new behavior (not a refactor of an existing one).
- Substantially changes an existing feature (new field, new screen, behavior change a user notices).
- Adds a new integration with an external service.
- Deviates from an existing rule in `docs/engineering-rules/`.

If the request is a bug fix without behavior change, a pure refactor, a dependency bump, a lint/format/CI tweak, or a docs-only edit, **skip this rule entirely** and proceed.

## The rule

1. **Run the gate before touching code.** When the user asks for feature work, the very first action is the PRD check, not a `Read` of the implementation file. Code edits made before the gate clears are out-of-spec by construction.

2. **Search for an existing PRD that covers the scope.**
   - List `docs/prd/` and skim titles.
   - Grep for keywords from the user's request across `docs/prd/`.
   - If a candidate exists, read it end-to-end before deciding.

3. **One of three outcomes:**

   **a. A PRD covers this scope and the new work fits inside it.**
   - Reference the PRD by number in your response and in the eventual PR description.
   - Bump `updated:` and append a Change log line if the work materially extends the doc (new functional requirement, new endpoint listed, new screen described).
   - Proceed to implementation.

   **b. A PRD partially covers this scope but the work expands it.**
   - Decide with the user: extend the existing PRD, or create a new PRD that declares `updates: PRD-NN`.
   - For most additive changes, extending is right. For reimaginings or large new surfaces, a new PRD is right.
   - Don't make this call unilaterally — the user owns the scope decision.

   **c. No PRD covers this scope.**
   - **Stop.** Do not write feature code yet.
   - Scaffold the PRD from `docs/prd/00-template.md` (a structured interview: scope, users, functional requirements).
   - Surface the draft PRD to the user for review. Wait for `Approved` (or explicit go-ahead) before implementing.

4. **Architectural choices need an ADR, not a PRD.** If the request implies a non-obvious technical fork (new data store, new auth model, new deployment target, deviation from an existing rule, new dependency category), an ADR is required *in addition to* the PRD. Scaffold both together (ADR template: `docs/architecture/adr/0000-template.md`).

5. **Reference the PRD in the PR.** The PR template has a dedicated `Linked PRD` line. The agent fills it in; the human reviewer treats a missing PRD as a blocker.

6. **Update PRD status on merge.** When the PR that implements a PRD merges to `main`:
   - Bump `updated:` to the merge date.
   - Flip `status:` from `Approved` to `Implemented`.
   - Append a Change log line: `YYYY-MM-DD — Implemented (PR #NNN)`.

7. **Never silently skip the gate.** If the user pushes back ("just make the change"), surface the rule and ask: *"This is a behavior change. Do you want me to draft a PRD first, or are you explicitly waiving the gate? If waived, I'll add a one-line note to the PR explaining why."* The escape valve from [`boundaries.md`](boundaries.md) applies — explicit waiver, in writing, on the PR.

## What the gate looks like in practice

> User: "Add a way for users to bulk-archive old projects."
>
> Agent: *Before reading the projects code*, I check `docs/prd/` for an existing PRD covering project archival. None found. Bulk-archival is a new user-facing flow — this needs a PRD before I implement. Running `/prd` now to draft `docs/prd/03-project-bulk-archive.md`. The interview will take about 5 minutes; once you approve the draft I'll implement against it.

vs.

> User: "Fix the off-by-one in the scoring threshold; it should be `<= 6.0`, not `< 6.0`."
>
> Agent: This is a bug fix that changes a documented threshold. Behavior changes for users (more records flagged at exactly 6.0). PRD-00 §Functional requirements references the threshold — I'll bump its `updated:` and append a Change log line, then implement. Not a new PRD; this is an additive update to an existing one.

vs.

> User: "Rename `items` to `itemRows` in a CLI helper for clarity."
>
> Agent: Pure refactor — no behavior change, no user-visible diff. Skipping the PRD gate; proceeding directly.

## Why

Three concrete failure modes this rule prevents:

- **Scope drift discovered in review.** Without a PRD, "add bulk-archive" can mean "soft delete + restore UI + retention policy + audit purge" or "set a flag and hide from the list" — the reviewer and implementer find out they disagree on PR #142, lines 800–1200. The PRD makes the scope decision *before* anyone writes code.
- **Undocumented features in production.** A feature that ships without a PRD has no canonical "why". Six months later, a new contributor doesn't know if the behavior is intentional or accidental, and the answer lives only in Slack scrollback (which won't survive an audit).
- **SOC 2 change-management evidence.** "How did this change get reviewed?" needs an answer beyond "the PR diff". The PRD is the answer: scope was approved before implementation, by a named author, on a known date.

The cost is one short interview per feature. The savings compound on every feature after the first.

## Examples

### Good — agent runs the gate

User: *"Build a feature that lets users export a project's data as a PDF."*

Agent's first response (before any `Read` on the codebase):
1. List `docs/prd/`. No file matches "export", "pdf", or "data".
2. Confirm scope with user: "I don't see a PRD for data exports. Running `/prd` to draft `docs/prd/04-data-export.md`."
3. Run the interview. Save the PRD as Draft.
4. Surface for approval: "Draft PRD ready at `docs/prd/04-data-export.md`. Confirm scope before I implement?"
5. After user approves, implement against the PRD.

### Good — extending an existing PRD

User: *"Add a `notes` field to the Record model that users can edit before submitting."*

Agent:
1. Search `docs/prd/`. PRD-02 covers Records.
2. Read PRD-02. The `notes` field isn't there but fits cleanly into "Records lifecycle: review before submit".
3. Update PRD-02: append a functional requirement, bump `updated:`, append to Change log.
4. Implement.

### Bad — coding before the PRD exists

User: *"Build the bulk-archive thing."*

Agent dives into a CLI command file, designs a new `devex` subcommand on the spot, implements it, opens a PR with no PRD reference. Reviewer asks "is this archival reversible? does it cascade to items? does it appear in the audit log?" — answers were never agreed. PR sits for two days while the spec is reverse-engineered from the diff.

The cost of skipping the gate is the cost of that two-day round-trip, every time.

## Escape valve

Same as [`boundaries.md`](boundaries.md): explicit user waiver in writing on the PR, with the reason. Never silent.
