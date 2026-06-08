# Requirements — @keystone/platform

## Introduction

`@keystone/platform` is the reusable TypeScript framework that standardizes CI/CD and infrastructure so teams consume shared artifacts instead of reinventing them. It owns workflow generation (which makes telemetry uniform), AWS CDK patterns, and the DORA telemetry contract.

## Requirements

### R1 — Type-safe workflow generation
**User story:** As a platform engineer, I want to generate GitHub Actions workflows from typed code, so that malformed pipelines fail at compile time, not in CI.

- WHEN `generatePrPipeline(options)` is called, THE SYSTEM SHALL return a workflow with small-tests (unit + property-based + API-contract) and deploy-sandbox stages.
- WHERE the app language varies (python/go/clojure/typescript), THE SYSTEM SHALL select the correct test toolchain behind one interface.
- THE SYSTEM SHALL inject the telemetry hook into deploy stages so every generated pipeline emits the standard event.

### R2 — Reusable CDK construct
**User story:** As a service team, I want a golden-path construct, so that I don't wire Lambda + API Gateway by hand.

- WHEN the `GoldenService` construct is instantiated, THE SYSTEM SHALL provision a Lambda behind a REST API Gateway with standard tags.
- THE SYSTEM SHALL provision the telemetry log group WITH an enforced retention period (no infinite-retention default).

### R3 — DORA telemetry contract
**User story:** As the platform team, I want one language-agnostic event schema, so that DORA metrics are comparable across all teams.

- THE SYSTEM SHALL expose `buildEvent` / `serializeEvent` and a typed `DoraEvent` carrying who/what/when/why (`actor`, `repo`+`env`, `timestamp`, `workId`).
- THE SYSTEM SHALL version the schema; changes SHALL be additive within a major `schemaVersion`.

### R4 — Integration Pipeline (conceptual; impl optional/bonus)
- WHEN code reaches `main`, THE SYSTEM SHALL generate a pipeline that promotes staging → production and emits metrics.

### R5 — Distribution
- THE SYSTEM SHALL be installable via `pnpm add github:<org>/keystone#path:/packages/platform-framework`, consumable by multiple repos, exposing reusable types and templates.

## Non-functional

- Tests: Vitest. `tsc --noEmit` clean. ESM output with `.d.ts` declarations.
- No secrets in generated workflows; use GitHub OIDC → AWS (no long-lived keys).
