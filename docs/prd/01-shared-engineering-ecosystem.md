---
title: Shared Engineering Ecosystem (Keystone)
number: 01
status: Approved
authors: [mauriceperea93@gmail.com]
created: 2026-06-08
updated: 2026-06-08
updates: null
supersedes: null
related_adrs: [ADR-0001, ADR-0002]
linear: []
---

## Overview

10+ independent, full-cycle engineering teams each reinvent CI/CD, infrastructure, and conventions. Practices diverge and DORA metrics aren't comparable because every team measures differently. We treat Developer Experience as a product; today that product is fragmented.

Keystone is a shared engineering ecosystem — a Golden Path — delivered as two independently versioned, Git-distributable packages: a Python `devex` CLI (developer-side) and a TypeScript `@keystone/platform` framework (platform-side). Both enforce one set of organizational conventions.

This PRD covers the PoC: prove the architectural integration, distribution strategy, and ecosystem "wiring" — not feature completeness.

## Goals

- One Golden Path adoptable by any team in three commands (install CLI, `init`, add framework).
- DORA metrics **comparable across Python, Go, Clojure, TypeScript** by construction.
- Both packages versioned, reusable, installable directly from Git (no registry).
- Make following standards easier than bypassing them (convention over configuration).
- Shorten defect-introduction-to-detection time (shift-left).

## Non-goals

- Production-grade telemetry collector or dashboards.
- Full implementation of every CLI command and CDK construct (PoC = vertical slice).
- Multi-cloud (AWS only).

## User stories

- As an engineer, I want local validation of branch/commit/PR conventions, so that I get feedback in seconds.
- As a platform engineer, I want to generate CI/CD workflows from typed code, so that pipelines are uniform and telemetry is automatic.
- As a team lead, I want comparable DORA metrics, so that I can benchmark my team fairly.
- As a contributor from another team, I want to add a feature via PR without platform-team hand-holding (inner-source).

## Functional requirements

1. The CLI MUST validate branch, commit, and PR title against `conventions.json` and run via git hooks (shift-left).
2. The CLI MUST bootstrap/adopt a service onto the golden path (`init` / `adopt`).
3. The framework MUST generate the PR Pipeline (small-tests → sandbox) as a type-safe artifact.
4. The framework MUST expose a language-agnostic DORA telemetry event and inject its emission into generated deploy stages.
5. Both packages MUST be installable directly from Git and independently versioned.
6. The ecosystem MUST enforce the Work ID, two-reviewer rule, and PR template.

## Non-functional requirements

- Testing: CLI ≥ 80% (pytest + Hypothesis), framework via Vitest + clean `tsc`.
- Security: GitHub OIDC → AWS (no static keys); no secrets/PII in logs or generated workflows; SOC 2 audit trail from the telemetry stream.
- Cost: demoable within an AWS trial (~$100) — serverless only, retention + teardown enforced (`.claude/rules/aws-cdk.md`).

## UX / API / Data notes

### UX
- CLI commands: `standards-check`, `init`, `pr`, `hooks install`, `dora`.

### API
- Framework subpaths: `@keystone/platform/{telemetry,workflows,constructs}`.
- Telemetry event: `{ event, workId, actor, repo, env, commitSha, commitTime, timestamp }`.

### Data
- `conventions/conventions.json` — single source of truth, bundled into the CLI wheel.

## Telemetry & success criteria

- Event stream of `deployment.*` records → four DORA metrics computed by `devex dora`.
- "Shipped" = a fork of Transactionify adopts Keystone, runs the generated PR pipeline, and emits comparable DORA telemetry.

## Rollout

Direct, no flag. Adoption is per-repo and opt-in via the CLI. Keystone dogfoods its own pipelines.

## Open questions

- (resolved) Monorepo vs multi-repo → ADR-0001 (monorepo).
- (resolved) How to make metrics comparable → ADR-0002 (single event source).

## Change log

- 2026-06-08 — Created + Approved (PR #pending)
