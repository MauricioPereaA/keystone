---
name: prd
description: Run a structured interview to scaffold a Product Requirements Document (PRD) at docs/prd/NN-<slug>.md, or — when the change involves a non-obvious technical fork — an Architecture Decision Record (ADR) at docs/architecture/adr/NNNN-<slug>.md. Reads the canonical template, picks the next number, fills the front-matter and sections from the user's answers, and updates docs/prd/README.md's index. The PRD-driven-development rule MUST invoke this skill before any feature work — see .claude/rules/prd-driven-development.md.
---

# prd — scaffold a PRD (and optionally an ADR) via interview

Use when:
- The user asks for a feature / behavior change and no existing PRD covers it.
- The user explicitly invokes `/prd` to start a new spec.
- The PRD-driven-development rule fires and routes the agent here.

Do **not** use when:
- The change is a bug fix without behavior change, a pure refactor, a dependency bump, a lint/CI tweak, or a docs-only edit. The PRD gate doesn't apply (`.claude/rules/prd-driven-development.md` §scope).

## Inputs

Gathered through the interview below. Don't ask anything you can already infer from the user's request — the goal is the shortest path to a concrete spec, not a checklist drill.

## Steps

### 1. Read the rule and template

- `.claude/rules/prd-driven-development.md` — your contract.
- `docs/prd/00-template.md` — the canonical structure; copy this verbatim and fill in.
- `docs/prd/README.md` — the index you'll update at the end.
- `docs/prd/01-shared-engineering-ecosystem.md` — exemplar of a filled PRD; mirror its tone (concise, declarative, no marketing).

### 2. Detect prior coverage

Before assuming this is a new PRD:

```bash
ls docs/prd/
grep -ril "<keyword>" docs/prd/
```

For each candidate:
- Read it end-to-end (it's short by design).
- Decide with the user: *new PRD*, *update existing PRD* (extend a section + Change log), or *supersede* (rare; reserved for full reimaginings).

If a candidate covers the scope, **don't run the full interview** — just propose the update and stop. The skill is for new PRDs.

### 3. Decide the doc type

- **PRD only** — new feature or behavior change, no architectural fork.
- **PRD + ADR** — feature includes a non-obvious technical choice (new dep category, new data store, new auth model, new deployment target, deviation from an existing rule).
- **ADR only** — pure architectural decision with no user-facing change (rare; usually a refactor justification).

If you're unsure, ask the user one question: *"Does this introduce a new technical choice with multiple reasonable answers?"* Yes → PRD + ADR. No → PRD only.

### 4. Run the interview

Ask **one question at a time**. Keep each question focused. Skip any question whose answer is already clear from the conversation.

| Question | Why we ask |
|---|---|
| **Title** — one short line (≤ 60 chars). | Goes into front-matter and the index row. |
| **Problem** — what's broken or missing today? Why now? | Becomes Overview ¶1. |
| **Goal** — one sentence: what does success look like? | Becomes Goals (top bullet) and Telemetry success criterion. |
| **Non-goals** — what's explicitly out of scope? Top 2–3. | Becomes Non-goals. Cuts scope drift early. |
| **Primary user story** — As a [User], I want X, so that Y. | Becomes User stories (top entry). |
| **Top functional requirements** — 3–5 numbered, testable items. | Becomes Functional requirements. |
| **NFR exceptions** — any deviations from the defaults (security / testing / AWS-cost / conventions)? | Becomes Non-functional requirements. Most PRDs answer "all defaults apply". |
| **UX / API / Data hints** — link to wireframes; rough endpoint paths; new models/fields. | Becomes UX/API/Data section. High level only. |
| **Linear ticket** | Becomes `linear:` front-matter. Optional but encouraged. |
| **Updates / supersedes** — does this revise an earlier PRD? | Becomes `updates:` or `supersedes:` front-matter. |
| **Open questions** — what's still TBD that blocks Approved? | Becomes Open questions. Empty when status flips to Approved. |
| **Need an ADR?** — only if step 3 didn't resolve it. | Triggers ADR scaffold below. |

The interview should fit in **5–10 minutes**. If it's running longer, the change is probably big enough to split into multiple PRDs — surface that to the user.

### 5. Pick the number

```bash
ls docs/prd/ | grep -E '^[0-9]{2}-' | sort | tail -1
```

The next number is `previous + 1`, zero-padded to 2 digits. If two branches are open in parallel, the one that merges second renumbers — don't try to reserve a number ahead of merge.

### 6. Render the PRD

Copy `docs/prd/00-template.md` to `docs/prd/<NN>-<slug>.md` where `<slug>` is kebab-case derived from the title (max 4 words, no stop words: "the", "a", "for", "of"). Fill in:

- Every front-matter field (use today's date for `created` and `updated`; status starts at `Draft`).
- Every section. **Don't leave `...` placeholders** — if a section truly doesn't apply, write `N/A — <reason>`.
- Reference related ADRs by ID (`ADR-0002`) — these populate from the user's answers and the existing PRDs you read.
- Change log: one line, today's date: `YYYY-MM-DD — Created (PR #pending)` (the PR number gets backfilled when the PR opens).

### 7. Update the index

In `docs/prd/README.md`, add one row to the index table, sorted by number:

```markdown
| [NN](./NN-<slug>.md) | <Title> | Draft | <one-line hook> |
```

The hook is a max-15-word teaser — what a reader gets if they click. Match the existing rows' tone.

### 8. Optionally scaffold the ADR

Only if step 3 said "PRD + ADR":

```bash
ls docs/architecture/adr/ | grep -E '^[0-9]{4}-' | sort | tail -1
```

Copy `docs/architecture/adr/0000-template.md` to `docs/architecture/adr/<NNNN>-<slug>.md` (4-digit numbering, separate sequence from PRDs). Fill in:

- **Context** — the technical situation (sourced from the PRD's Overview).
- **Decision** — what we're doing.
- **Consequences** — positive / negative / follow-ups.
- **Alternatives considered** — at least two, each with a reason for rejection. *This is the value of an ADR* — without alternatives, it's just a description.

Cross-link: the PRD's `related_adrs:` lists the new ADR; the ADR's Context references the PRD by number.

### 9. Surface for approval

Don't proceed to implementation. Stop and tell the user:

```
Drafted PRD-<NN> at docs/prd/<NN>-<slug>.md (status: Draft).
[If ADR: Drafted ADR-<NNNN> at docs/architecture/adr/<NNNN>-<slug>.md.]

Review the draft and reply with:
  - "approved" → I'll set status to Approved and start implementing
  - "edit X to say Y" → I'll revise
  - "split this" → the scope is too big; I'll break it into multiple PRDs
```

The user owns scope. Never flip a PRD to `Approved` unilaterally.

### 10. Stop short of committing

Hand off to `commit` / `open-pr`. The PRD itself can land in a docs-only PR (when the spec is large enough to merit independent review) or in the same PR as the implementation (small features). Default: same PR, but the PRD must be reviewable on its own — read top-to-bottom without the diff.

## Hard rules

- **No code edits before the PRD exists.** This skill exists precisely so the agent does specs first. If you've already written code, stop and back out — the PRD documents intent *before* implementation.
- **No empty sections.** `N/A — <reason>` beats blank. A blank section signals "I forgot to think about this".
- **No marketing voice.** PRDs are engineering specs, not pitch decks. Be declarative.
- **No solutioning in Overview / Goals.** Save technical choices for the UX/API/Data section. The Overview is *what + why*, not *how*.
- **No silent renumbering.** If you discover a number collision (parallel PRs both using `04`), don't shuffle — surface to the user and ask which renumbers.
- **No deletion of PRD content.** PRDs are append-only history. To replace one, supersede it; the old text stays.

## Output format

When the skill finishes, summarize for the user in ≤ 5 lines:

```
PRD-<NN>: <Title>
Status: Draft
File: docs/prd/<NN>-<slug>.md
Index updated: docs/prd/README.md
[ADR-<NNNN>: <Title> — docs/architecture/adr/<NNNN>-<slug>.md]
Next: review the draft and reply "approved" to unblock implementation.
```

## Why

Without this skill, the agent and the user negotiate scope through the diff — which is the worst possible time. Every PRD authored through this interview is a 5–10-minute conversation that prevents 30 minutes of PR-review back-and-forth and an unbounded amount of "wait, that's not what I meant" rework.

The interview structure exists for a reason: every question maps to a section, every section maps to a class of bug it prevents. Skipping a question is fine when the answer is obvious — skipping a *section* is how features ship without a way to verify them.

The split between PRD and ADR keeps each doc useful. PRDs are read by product + engineering for "what are we doing"; ADRs are read by engineering for "why this technical path". Conflating them produces docs too long for one audience and too vague for the other.
