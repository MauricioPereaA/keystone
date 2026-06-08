# Conventions Steering — Keystone

> Human-readable mirror of `conventions/conventions.json`. The JSON is canonical and machine-read; this file explains it. If they disagree, the JSON wins — fix this file.

## Universal Work ID

Every change links to a tracked unit of work via a Work ID like `FIN-123` (`^[A-Z]{2,5}-\d+$`). Mandatory in branch names, commit messages, and PR titles. It is the **"why"** in the audit trail.

## Branch naming

`type/<WORK-ID>-<kebab-slug>` — e.g. `feature/FIN-123-add-payment-validation`.
Types: `feature | fix | chore | docs | refactor | test | ci | perf | build`. `main` is protected.

## Commit messages

Conventional-commit type + optional scope, Work ID in the subject:
`feat(api): FIN-123 add payment validation`. Subject ≤ 72 chars.

## Pull requests

Work ID in the title: `[FIN-123] …` or `FIN-123: …`. Standardized template required. **Two-reviewer approval** rule. No direct push to `main`; no force-push to `main`.

## Pipelines

- **PR Pipeline** (on PR open/update): small-tests (unit + property-based + API-contract) → deploy-sandbox. Fast feedback, no prod.
- **Integration Pipeline** (on push to `main`): small-tests → staging → production → emit-metrics.
- Environments: `sandbox → staging → production`, promoted via AWS CDK.

## Telemetry / DORA

One language-agnostic event (`deployment.started|succeeded|failed|rolled_back`) carries `work_id, actor, repo, env, commit_sha, commit_time, timestamp`. The four DORA metrics (deployment frequency, lead time, change failure rate, MTTR) derive from this single stream. Comparable across all languages because the framework — not the app — emits it.

## Enforcement chain (shift-left → CI)

1. `devex hooks install` → pre-commit/pre-push run `devex standards-check` locally.
2. The framework-generated PR workflow re-runs the same checks in CI.
3. Branch protection enforces the two-reviewer rule.

Local and CI use the **same** `conventions.json`, so "passes locally" ⇒ "passes CI".
