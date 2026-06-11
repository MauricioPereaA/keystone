# Hard boundaries

**Scope:** Repo-wide.

**See also:** [`security.md`](security.md), [`architecture.md`](architecture.md), [`aws-cdk.md`](aws-cdk.md).

## When this rule applies

Always. Each constraint prevents a category of bug or a contract violation the project can't recover from cleanly.

## The constraints

### 1. Single source of truth for conventions
Every convention (Work ID, branch/commit/PR pattern, pipeline shape, telemetry schema) is defined **once** in `conventions/conventions.json`. Never hard-code a pattern in Python or TypeScript. The CLI's bundled copy is synced from the canonical file; CI fails on drift.

### 2. The CLI is self-contained (distribution invariant — ADR-0001)
`packages/devex-cli` declares no monorepo/workspace dependency. This is what keeps `uv tool install git+...#subdirectory=` reliable. Don't add a cross-package import "for convenience".

### 3. One language-agnostic telemetry source (ADR-0002)
DORA metrics derive from the single `DoraEvent` stream emitted by framework-generated workflows. Never compute metrics per-language or instrument them in application code. Schema changes are additive within a major `schemaVersion`.

### 4. Convention over configuration
The golden path is the default that `devex init` generates and the framework emits. If following a standard is harder than bypassing it, that's a bug in the platform.

### 5. PRD before feature code
No new feature/behavior without an approved PRD (`prd-driven-development.md`). Bug fixes, refactors, and docs are exempt.

### 6. Auth via GitHub OIDC — never static keys
Generated workflows assume an AWS role through OIDC. No `AWS_ACCESS_KEY_ID` secrets anywhere (`security.md`, `aws-cdk.md`).

### 7. Errors are visible
No silent `except: pass` / empty `catch`. Every caught error is logged as a structured event (`error-handling.md`, `logging-discipline.md`). Every deploy/mutation emits the standard telemetry event.

### 8. AWS cost guardrails
No AWS resource without a log-retention policy and `project=keystone` tag. No NAT gateways. `cdk destroy` after demos (`aws-cdk.md`).

### 9. Secrets
Never commit `.env`, real keys, or passwords (even for dev). `.env.example` only. Read config through the documented entrypoints.

### 10. No bypassed quality gates
No `--no-verify`, no `git commit -n`, no merging red CI. Fix the cause.

### 11. No push to `main`
Feature branch + PR + human review + two approvals. No force-push to `main` (`no-direct-push-to-main.md`).

### 12. No leftover template domain
This repo is **AWS + Keystone**. No GCP/Terraform, no "Platonica", no Django/React/tenant references.

## Why

These are the cumulative result of incidents the project chooses never to live through: convention drift, broken Git installs, non-comparable metrics, leaked secrets, silent failures, a runaway AWS bill. If a rule feels restrictive, that's intended — raise it in review before working around it.

## Escape valve

To break a rule: name it and the reason in writing in the PR, get explicit reviewer sign-off, and capture it as an ADR if it sets a precedent. Never break a rule silently.
