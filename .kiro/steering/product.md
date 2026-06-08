# Product Steering — Keystone

> Persistent context for any AI agent or engineer working on Keystone. Loaded first, always.

## Problem

10+ independent, full-cycle engineering teams each reinvent CI/CD, infrastructure wiring, and engineering conventions. The result: inconsistent practices, and DORA metrics that can't be compared across teams because each team measures differently. Developer Experience is treated as a product here, and today that product is fragmented.

## What Keystone is

A shared engineering ecosystem — a **Golden Path** — composed of two independently versioned, Git-distributable packages:

- **`devex` CLI** (Python/uv): the developer-facing interface. Standardizes git workflows, automates conventions, bootstraps projects, runs local validations.
- **`@keystone/platform`** (TypeScript/pnpm): the reusable workflow + infrastructure framework. Generates CI/CD pipelines, AWS CDK patterns, and the telemetry contract.

## The non-negotiable principle

**Standardize the source of the metric, not the metric.** The framework generates every team's workflows, so every team emits one identical, language-agnostic telemetry event. DORA metrics derive from that single stream → comparable across Python, Go, Clojure, TypeScript. The same event is the SOC 2 audit record.

## Success criteria (how we're judged)

1. **Consistency** — DORA metrics comparable across all four languages.
2. **Convention over configuration** — easier to follow standards than to bypass them.
3. **Packaging maturity** — both packages versioned, reusable, easy to install from Git.
4. **Feedback loops** — shorter time between defect introduction and detection (shift-left).
5. **Inner-source readiness** — another team can contribute a feature without heavy platform-team support.

## Reference service

**Transactionify** — a transaction-processing microservice (AWS CDK + Lambda + Python + API Gateway). The Integration Case Study adopts Keystone onto a fork of it.

## Out of scope (PoC)

Feature completeness, production-grade collectors, multi-cloud. The Integration Pipeline is conceptual unless the bonus is pursued.
