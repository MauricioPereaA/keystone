# Product Requirements Documents (PRDs)

Every user-facing feature or behavior change is described by a PRD before code lands. This folder is the canonical record of *what we're building and why*. Architectural choices live separately in [`docs/architecture/adr/`](../architecture/adr/).

> **Working with an AI agent?** The agent's contract is in [`.claude/rules/prd-driven-development.md`](../../.claude/rules/prd-driven-development.md) and the scaffolding tool is the [`/prd` skill](../../.claude/skills/prd/SKILL.md). The agent will block on missing PRDs before writing feature code — by design.

---

## Index

| # | Title | Status | Hook |
|---|---|---|---|
| [01](./01-shared-engineering-ecosystem.md) | Shared Engineering Ecosystem (Keystone) | Approved | The PoC scope: CLI + framework + comparable DORA, all installable from Git |

> Add one row per PRD when it's created. Keep it sorted by number. The `/prd` skill updates this table automatically.

---

## When does a change need a PRD?

**Yes — write or update a PRD before coding** if any of:

- ✅ New feature or new user-facing flow.
- ✅ New endpoint with new behavior (not a refactor).
- ✅ Substantial change to an existing feature (new field, new screen, behavior change a user notices).
- ✅ New integration with an external service.
- ✅ A change that would surprise the user reading the existing PRD.

**No PRD needed** for:

- ❌ Bug fix without behavior change.
- ❌ Pure refactor.
- ❌ Dependency bump.
- ❌ Lint / format / CI tweaks.
- ❌ Doc-only edits.

When unsure, write the PRD. The cost of a 15-minute interview is much less than the cost of an undocumented feature.

---

## The flow

```
                ┌─────────────────────────────┐
                │  New work request arrives    │
                └───────────────┬──────────────┘
                                │
                  ┌─────────────▼──────────────┐
                  │ Does an existing PRD       │
                  │ cover this scope?          │
                  └───┬─────────────────┬──────┘
                      │ Yes             │ No
                      ▼                 ▼
        ┌─────────────────────┐   ┌──────────────────────┐
        │ Reference it.       │   │ Run /prd skill —     │
        │ If scope expanded,  │   │ structured interview │
        │ update the PRD      │   │ + scaffold from      │
        │ + Change log.       │   │ template.            │
        └──────────┬──────────┘   └──────────┬───────────┘
                   │                         │
                   ▼                         ▼
         ┌──────────────────────────────────────┐
         │ Status: Draft → Approved             │
         │ (PRD reviewed, scope agreed)         │
         └──────────────┬───────────────────────┘
                        │
                        ▼
         ┌──────────────────────────────────────┐
         │ Implement. Link PRD-NN in:           │
         │   - branch name (optional)           │
         │   - commit body                      │
         │   - PR description (mandatory)       │
         └──────────────┬───────────────────────┘
                        │
                        ▼
         ┌──────────────────────────────────────┐
         │ On merge:                            │
         │   - Status → Implemented             │
         │   - Change log line: PR #NNN         │
         └──────────────────────────────────────┘
```

### Step-by-step for humans

1. **Draft the PRD first.** Run `/prd` (or copy `00-template.md`). Fill the interview answers. Save as `docs/prd/NN-<slug>.md` where `NN` is the next available 2-digit number.
2. **Open a PR for the PRD alone** if the change is large enough to warrant separate review of the spec. For smaller features, the PRD can land in the same PR as the implementation — but the PRD must be reviewable independently.
3. **Get the PRD to `Approved`.** A reviewer signs off on scope, goals, non-goals, and any open questions.
4. **Implement.** Reference `PRD-NN` in the PR description (the PR template has a dedicated line).
5. **On merge.** Bump the PRD's `updated` date, set `status: Implemented`, append the merge to the Change log.

### Step-by-step for agents

The agent runs this gate **before writing code** for any feature work:

1. Search `docs/prd/` for keywords from the user's intent.
2. If a PRD covers the scope: read it, follow it, propose updates if the scope expanded.
3. If no PRD covers it: invoke `/prd`, run the interview, scaffold the doc, surface it to the user for approval.
4. Only after a PRD exists does the agent proceed to implementation.

The full contract is in [`.claude/rules/prd-driven-development.md`](../../.claude/rules/prd-driven-development.md).

---

## Numbering

- Two-digit, zero-padded: `00`, `01`, `02`, … through `99`.
- The skill picks the next number by listing this folder.
- Branches landing in parallel can collide — first to merge wins; the second renumbers.
- Numbers are stable once merged. Renumbering a merged PRD is banned (history would lie).

## Status values

| Status | Meaning |
|---|---|
| `Draft` | Authoring in progress. Open questions present. Not safe to implement against. |
| `Approved` | Scope is agreed. Open questions resolved. Implementation can start. |
| `Implemented` | Code merged to `main` matches this PRD. |
| `Superseded` | Replaced by a later PRD. The replacing PRD lists this one in `supersedes:`. Body stays intact for history. |

## Updates vs supersedes

- **`updates: PRD-NN`** — additive change. The earlier PRD remains valid; this one extends or refines a section.
- **`supersedes: PRD-NN`** — total replacement. The earlier PRD's `status` flips to `Superseded`.

---

## PRD vs ADR

| | PRD | ADR |
|---|---|---|
| **Question it answers** | What are we building, for whom, and why? | We had a non-obvious technical choice — which path did we pick and why? |
| **Audience** | Product + engineering | Engineering + future maintainers |
| **Lifespan** | Lives until superseded by a later PRD | Lives forever; never edited after `Accepted`, only superseded |
| **Folder** | [`docs/prd/`](.) | [`docs/architecture/adr/`](../architecture/adr/) |
| **Numbering** | `NN-` (2 digit) | `NNNN-` (4 digit) |
| **Triggered by** | Feature work | Architectural fork-in-the-road |

**Most PRDs reference existing ADRs.** **Some PRDs spawn a new ADR** when the feature requires a real technical choice. The `/prd` skill detects this and offers to scaffold both.

---

## Related rules

- [`.claude/rules/prd-driven-development.md`](../../.claude/rules/prd-driven-development.md) — agent contract (mandatory).
- [`.claude/rules/commit-and-pr.md`](../../.claude/rules/commit-and-pr.md) — commit + PR conventions.
- [`.claude/rules/boundaries.md`](../../.claude/rules/boundaries.md) — repo-wide hard rules.
