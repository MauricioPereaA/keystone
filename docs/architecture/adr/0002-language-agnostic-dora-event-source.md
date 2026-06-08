---
title: Language-agnostic DORA event as the single metric source
number: 0002
status: Accepted
authors: [mauriceperea93@gmail.com]
created: 2026-06-08
updated: 2026-06-08
supersedes: null
superseded_by: null
related_prds: [PRD-01]
related_adrs: [ADR-0001]
linear: []
---

## Context

The platform must report DORA metrics that are comparable across teams written in Python, Go, Clojure, and TypeScript (PRD-01). If each team instruments its own metrics, definitions drift (what counts as a "deployment"? when does lead time start?) and cross-team comparison becomes meaningless. We need comparability to be structural, not a convention teams are asked to follow.

## Decision

We make the **CI/CD workflow the single source of telemetry**. `@keystone/platform` owns workflow generation, and every generated deploy stage emits one **identical, language-agnostic event** (`deployment.started|succeeded|failed|rolled_back`) carrying `workId, actor, repo, env, commitSha, commitTime, timestamp`. The four DORA metrics are derived downstream from this one stream. The app's language is irrelevant because the metric comes from the pipeline event, not the application runtime. The same event is the SOC 2 audit record (who/what/when/why), with `workId` as the "why".

## Consequences

### Positive
- DORA metrics are comparable by construction — no per-language instrumentation, no definition drift.
- Audit trail and metrics share one pipeline; SOC 2 evidence is a query over the event stream.
- Swapping the collector (CloudWatch/S3 → DynamoDB/Kinesis/Datadog) changes the sink only, not the contract.

### Negative / tradeoffs
- Metrics are only as good as workflow adoption — a team hand-rolling its own workflow escapes the source (mitigated: `devex init` generates workflows; convention-over-configuration).
- A schema change is a cross-team contract change; requires additive-only discipline + `schemaVersion`.

### Follow-ups
- Pin `schemaVersion` and document the additive-change policy in the contribution guide.
- Implement the `emitTelemetryStep` injected into every generated deploy job.

## Alternatives considered

- **Per-language metric libraries (SDK per stack)** — flexible. Rejected: guarantees definition drift and 4× maintenance; defeats comparability.
- **Parse VCS/host APIs after the fact (e.g. GitHub Deployments API)** — no code in pipelines. Rejected: ties metrics to one host's data model, weaker "why"/audit linkage, harder to standardize across future hosts.

## Change log

- 2026-06-08 — Proposed + Accepted (PR #pending)
