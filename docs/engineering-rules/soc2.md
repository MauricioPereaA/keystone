# SOC 2 controls

**Scope:** Repo-wide (process + both packages + infra).

**See also:** [`audit-logging.md`](audit-logging.md), [`security.md`](security.md), [`commit-and-pr.md`](commit-and-pr.md), [`no-direct-push-to-main.md`](no-direct-push-to-main.md).

## When this rule applies

You're touching the SOC 2 evidence surface: change management (PRs), access to AWS, the audit trail, secret handling, or dependencies.

## Trust Services Criteria → our implementation

### CC6.1 — Logical access (least privilege)
- AWS access via GitHub OIDC with a repo-scoped, least-privilege deploy role (`security.md` §4–5). No static keys, no shared service accounts.
- No human has standing prod credentials; deploys go through CI.

### CC6.6 — Encryption in transit / at rest
- HTTPS to AWS APIs (SDK default). At-rest encryption is the managed service's responsibility (Lambda/DynamoDB/S3/CloudWatch). Document any KMS choices in an ADR when prod-bound.
- Secrets in `.env` (dev, gitignored) / AWS Secrets Manager (prod). `.env.example` only in source.

### CC7.2 / CC7.3 — Monitoring & incident evidence
- Every deploy emits a `DoraEvent` (`audit-logging.md`). The stream answers "who changed what, when, why" — `why` is the Work ID linking to the tracked unit of work.
- Distinct event types (`deployment.failed`, `rolled_back`) make failure/MTTR queryable.
- No silent exceptions (`error-handling.md`).

### CC8.1 — Change management
- All changes go through a PR to `main`; **direct push and force-push to `main` are banned** (`no-direct-push-to-main.md`).
- Conventional-commit titles + **Work ID** give a traceable, ticket-linked history.
- **Two-reviewer approval**; CI must be green (small-tests: unit + PBT + contract).
- The PR pipeline + branch protection are the enforcement; the generated workflow re-runs the same `conventions.json` checks the developer ran locally.

### CC9.2 — Vendor / dependency management
- Lockfiles committed (`uv.lock`, `pnpm-lock.yaml`); CI installs frozen.
- New third-party integrations need an ADR (data shared, auth model).

## What the auditor will ask → where it lives

| Question | Answer |
|---|---|
| "Who can deploy to prod?" | OIDC deploy role; trust policy scoped to this repo. |
| "How are changes reviewed?" | Squash-merge ⇒ every `main` commit has a PR with ≥2 approvals + green CI. |
| "How do you log deploys / changes?" | `DoraEvent` stream (`audit-logging.md`). |
| "Who changed what, when, why?" | Same stream; `why` = Work ID. |
| "Secret rotation?" | `docs/runbooks/secret-rotation.md`; OIDC means no key to rotate for deploys. |

## Why

SOC 2 is a continuous evidence surface. Building the controls into paths that already exist — one telemetry event per deploy, PR-only changes, OIDC, lockfiles — means evidence collection is a query, not an interview reconstruction.

## Examples

### Good — change-management trail
```
PR #42 — feat(api): FIN-123 add payment validation
  ├── 2 approvals · CI green (unit + PBT + contract)
  ├── squash-merge → main
  └── DoraEvent: deployment.succeeded workId=FIN-123 actor=ci env=production
```

### Bad
```
# ✗ direct push to main: no PR, no review, no CI gate — unanswerable in an audit
git push origin main
```
