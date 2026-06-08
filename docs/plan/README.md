# Build Plan

This folder contains the sequential build plan for this project. Each document covers one phase of development and is meant to be read in order.

The plan documents answer **how to build** the project. The *what* and *why* live in [`docs/prd/`](../prd/). The *non-obvious technical decisions* live in [`docs/architecture/adr/`](../architecture/adr/).

---

## Index

[CUSTOMIZE: Add a row per phase doc as you create them. Keep sorted by number.]

| # | Phase | Status | Scope |
|---|---|---|---|
| [00](./00-overview.md) | Overview — repo layout, stack rationale, phase map | Draft | Read first |

---

## Conventions

- **One doc per phase.** A phase ends when its exit criteria are met and a real user could complete the primary workflow.
- **Phase 0 is always infrastructure.** Auth, core data model, CI, dev environment. Nothing user-facing until Phase 0 is done.
- **Docs are written before implementation.** A plan doc that's written after the fact is a changelog, not a plan.
- **Cross-reference PRDs.** Each phase doc should list the PRDs it implements. Each PRD should reference the phase it belongs to.

---

## Creating a phase doc

Copy `docs/prd/00-template.md` as a starting point — or scaffold from scratch with these sections:

1. **Goal** — one sentence on what this phase delivers.
2. **Exit criteria** — the observable conditions that mark the phase complete.
3. **What we're building** — the features and components in scope.
4. **Out of scope** — what explicitly comes later.
5. **Technical notes** — any decisions or constraints specific to this phase.
6. **Related PRDs** — the PRDs this phase implements.
7. **Completion checklist** — a checklist of tasks within the phase.
