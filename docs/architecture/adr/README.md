# Architecture Decision Records (ADRs)

Every non-obvious technical fork is captured as an ADR before — or alongside — the code that implements it. This folder is the canonical record of *which path we picked and why*. Product scope lives separately in [`docs/prd/`](../../prd/).

> **Working with an AI agent?** The [`/prd` skill](../../../.claude/skills/prd/SKILL.md) scaffolds an ADR alongside a PRD when the feature involves a non-obvious technical choice. The ADR template is [`0000-template.md`](./0000-template.md).

---

## Index

| # | Title | Status | Hook |
|---|---|---|---|
| [0001](./0001-monorepo-topology-and-self-contained-cli.md) | Monorepo topology with a self-contained CLI | Accepted | Why one repo + why the CLI bundles conventions (reliable Git install) |
| [0002](./0002-language-agnostic-dora-event-source.md) | Language-agnostic DORA event as the single metric source | Accepted | Why metrics come from the pipeline event, not per-language instrumentation |
| [0003](./0003-git-governance-and-branch-protection.md) | Git governance — unified PR-title convention + branch-protection ruleset | Accepted | One Work-ID-anchored title rule (CLI-validated); ruleset-as-code for 2 reviewers |

> Add one row per ADR when it's created. Keep it sorted by number. The `/prd` skill updates this table when it scaffolds a paired ADR.

---

## When does a change need an ADR?

**Yes — write an ADR before (or with) the implementation** if any of:

- ✅ New data store, queue, search engine, or other backbone dependency.
- ✅ New auth model (e.g. switching from JWT to session cookies, adding SSO).
- ✅ New deployment target or runtime.
- ✅ Deviation from an existing rule in [`.claude/rules/`](../../../.claude/rules/).
- ✅ Choice between two reasonable libraries / patterns where the tradeoff isn't obvious.
- ✅ A choice that, if reversed in six months, would require a non-trivial migration.

**No ADR needed** for:

- ❌ A choice that's obvious in context (using the framework's built-in auth helpers).
- ❌ Implementation details inside an already-decided pattern.
- ❌ Bug fixes, refactors, or dependency bumps inside an established stack.

When in doubt: write the ADR. Three short sections; the value is the *alternatives considered* list, which forces you to articulate why you didn't take the other path.

---

## The flow

```
                ┌─────────────────────────────┐
                │  Technical fork appears in   │
                │  a PRD or a refactor         │
                └───────────────┬──────────────┘
                                │
                  ┌─────────────▼──────────────┐
                  │ Is the choice obvious      │
                  │ from existing rules / docs?│
                  └───┬─────────────────┬──────┘
                      │ Yes             │ No
                      ▼                 ▼
         ┌─────────────────────┐  ┌──────────────────────┐
         │ Just implement.     │  │ Draft an ADR from    │
         │ Reference an        │  │ 0000-template.md.    │
         │ existing ADR if     │  │ Pick the next 4-digit│
         │ relevant.           │  │ number.              │
         └─────────────────────┘  └──────────┬───────────┘
                                             │
                                             ▼
                              ┌──────────────────────────────────────┐
                              │ Status: Proposed → Accepted          │
                              │ (reviewer signs off on the decision) │
                              └──────────────┬───────────────────────┘
                                             │
                                             ▼
                              ┌──────────────────────────────────────┐
                              │ Implement against the ADR.           │
                              │ Reference ADR-NNNN in the PR body    │
                              │ and in the related PRD's             │
                              │ `related_adrs:` list.                │
                              └──────────────┬───────────────────────┘
                                             │
                                             ▼
                              ┌──────────────────────────────────────┐
                              │ Once Accepted, the ADR is FROZEN.    │
                              │ To change the decision, write a new  │
                              │ ADR that supersedes this one.        │
                              └──────────────────────────────────────┘
```

### Step-by-step for humans

1. **Draft from `0000-template.md`.** Save as `docs/architecture/adr/<NNNN>-<slug>.md` where `<NNNN>` is the next 4-digit number, `<slug>` is kebab-case (max 4 words).
2. **Fill all sections.** *Especially* "Alternatives considered" — at least two, each with a reason for rejection. An ADR without alternatives is just a description.
3. **Open a PR for the ADR.** Can land in the same PR as implementation (small decisions) or as a doc-only PR (larger decisions needing independent review).
4. **Get the ADR to `Accepted`.** A reviewer signs off on Context + Decision + Consequences.
5. **Reference the ADR.** Cross-link from the originating PRD (`related_adrs: [ADR-NNNN]`) and from any rule in `.claude/rules/` that the decision affects.

### Step-by-step for agents

When the [`/prd` skill](../../../.claude/skills/prd/SKILL.md) detects a non-obvious technical fork during the PRD interview, it asks: *"Does this introduce a new technical choice with multiple reasonable answers?"* If yes, it scaffolds the ADR alongside the PRD and cross-links them.

---

## Numbering

- Four-digit, zero-padded: `0001`, `0002`, … through `9999`.
- Separate sequence from PRDs (PRDs are 2-digit).
- **Numbers are stable once merged.** Renumbering a merged ADR is banned (history would lie).

## Status values

| Status | Meaning |
|---|---|
| `Proposed` | Drafted; awaiting reviewer sign-off. Not safe to implement against. |
| `Accepted` | Decision is in force. Implementation can start. **The body is now frozen** — never edit. |
| `Superseded` | Replaced by a later ADR (which lists this one in `supersedes:`). Body stays intact for history. |

## Supersedes vs related_adrs

- **`supersedes: ADR-NNNN`** — total replacement. The earlier ADR's `status` flips to `Superseded`. Use when the original decision is reversed.
- **`related_adrs: [ADR-NNNN, ...]`** — non-replacing relationship. Use when this ADR builds on or shares context with another.

---

## PRD vs ADR

| | PRD ([`docs/prd/`](../../prd/)) | ADR (this folder) |
|---|---|---|
| **Question it answers** | What are we building, for whom, and why? | We had a non-obvious technical choice — which path did we pick and why? |
| **Audience** | Product + engineering | Engineering + future maintainers |
| **Lifespan** | Lives until superseded by a later PRD | Lives forever; never edited after `Accepted`, only superseded |
| **Folder** | [`docs/prd/`](../../prd/) | [`docs/architecture/adr/`](.) |
| **Numbering** | `NN-` (2 digit) | `NNNN-` (4 digit) |
| **Triggered by** | Feature work / behavior change | Architectural fork-in-the-road |

---

## Related rules

- [`.claude/rules/prd-driven-development.md`](../../../.claude/rules/prd-driven-development.md) — agent contract.
- [`.claude/rules/boundaries.md`](../../../.claude/rules/boundaries.md) — the constraints an ADR can override only with explicit written waiver.
- [`.claude/rules/commit-and-pr.md`](../../../.claude/rules/commit-and-pr.md) — commit + PR conventions.
