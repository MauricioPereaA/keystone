---
title: Monorepo topology with a self-contained CLI package
number: 0001
status: Accepted
authors: [mauriceperea93@gmail.com]
created: 2026-06-08
updated: 2026-06-08
supersedes: null
superseded_by: null
related_prds: [PRD-01]
related_adrs: [ADR-0002]
linear: []
---

## Context

Keystone ships two independently versioned packages — a Python CLI (`uv`) and a TypeScript framework (`pnpm`) — both installable directly from Git with no registry (PRD-01). We must decide how to lay out the source: one repository or two. Separately, Git-based installs of a sub-package from a monorepo have tooling caveats: `uv` has known marker-resolution failures when installing a package that participates in a `uv` workspace, while `pnpm` (≥9) installs subdirectories cleanly via `#path:`.

## Decision

We use a **single monorepo** with two independently versioned packages under `packages/`, sharing one `conventions/conventions.json`. The CLI package is **self-contained**: it declares no monorepo/workspace dependencies and bundles `conventions.json` as package data (Hatch `force-include`), kept in sync by `make sync-conventions` with a CI drift check.

## Consequences

### Positive
- The ecosystem's "wiring" (shared conventions, one event contract) is demonstrable in a single clone — exactly what the PoC is judged on.
- `uv tool install git+...#subdirectory=packages/devex-cli` and `pnpm add github:...#path:/packages/platform-framework` both resolve reliably.
- One PR can evolve a convention and both consumers atomically.

### Negative / tradeoffs
- Less faithful to a real multi-team production setup (where packages often live in separate repos).
- Bundling `conventions.json` into the CLI introduces a sync step (mitigated by the CI drift check).
- Independent versioning inside a monorepo needs discipline (tags like `cli-v0.1.0` / `framework-v0.1.0`).

### Follow-ups
- Add `make sync-conventions` + a CI job asserting the bundled copy equals the canonical file.
- Document per-package tag conventions in the consumption guide.

## Alternatives considered

- **Two separate repos** — most production-faithful. Rejected for the PoC: doubles install/demo friction and hides the ecosystem integration the challenge wants to see in one place.
- **Monorepo with the CLI as a `uv` workspace member** — cleaner local dev. Rejected: triggers `uv` marker-resolution failures on Git subdirectory installs, breaking the install walkthrough.

## Change log

- 2026-06-08 — Proposed + Accepted (PR #pending)
