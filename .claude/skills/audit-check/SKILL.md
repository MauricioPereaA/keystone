---
name: audit-check
description: Scan the current diff for Keystone platform gaps — hard-coded conventions that should come from conventions.json, generated deploy jobs missing the telemetry step, static AWS keys instead of OIDC, CDK resources missing log retention/tags, silent error swallowing, and conventions.json drift. Surfaces a punch list; does not auto-fix.
---

# audit-check — Keystone platform gap scanner

Read-only scan. Used standalone (`/audit-check`) and invoked by `open-pr` to decide whether to mark a PR as Draft.

## Inputs

By default, scan `git diff main...HEAD`. If the branch isn't ahead of main, fall back to `git diff --staged`. Accept an optional path argument to narrow.

## Checks

### 1. Hard-coded conventions (ADR-0001 / boundaries §1)
Flag any regex or literal in `packages/**` that duplicates a pattern owned by `conventions.json` (Work ID `[A-Z]{2,5}-\d+`, branch/commit/PR patterns, env names, event names). These must be loaded from the source of truth, not inlined.
- Flag: `"hard-coded convention: <file>:<line> — load from conventions.json"`.

### 2. Conventions drift
If `conventions/conventions.json` changed but `packages/devex-cli/src/devex/_data/conventions.json` did not (or vice-versa), the bundled copy is stale.
- Flag: `"conventions drift — run make sync-conventions"`.

### 3. Telemetry coverage (ADR-0002)
For any change under `packages/platform-framework/src/workflows/**` that adds or edits a deploy job, confirm the `emitTelemetryStep` (DoraEvent emission) is present in every deploy job.
- Flag: `"deploy job without telemetry step: <file>"`.

### 4. AWS auth = OIDC, never static keys (security §4)
In any generated or committed workflow, flag `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` in `secrets:`/`env:`. The only acceptable auth is `aws-actions/configure-aws-credentials` with a role ARN.
- Flag: `"static AWS credentials — use OIDC role"`.

### 5. CDK cost guardrails (aws-cdk §6–9)
For new `logs.LogGroup` without an explicit `retention`, or any new construct without `project=keystone` tags, or a `NatGateway` anywhere.
- Flag: `"log group without retention / missing tag / NAT gateway: <file>:<line>"`.

### 6. Silent error swallowing (error-handling / logging-discipline)
`except: pass` / empty `catch {}` without a logged reason; `print(...)` or `console.log(...)` used as diagnostics.
- Flag: `"silent catch / stray print|console.log: <file>:<line>"`.

### 7. Secrets / PII in telemetry or logs (security §10)
Any log or DoraEvent field carrying tokens, credentials, emails, or raw payloads.
- Flag: `"possible secret/PII in log/event: <file>:<line>"`.

## Output

A punch list grouped by check, each item `file:line — issue`. End with a one-line verdict: `READY` (no findings) or `NEEDS WORK (<n> findings)`. Do not auto-fix; `open-pr` uses the verdict to decide Draft vs ready.
