# 01 — Project Context

> This is the page a new engineer reads on Day 1 before anything else.

---

## What we're building

10+ independent, full-cycle engineering teams each reinvent CI/CD, infrastructure wiring, and engineering conventions. Practices diverge, and DORA metrics can't be compared across teams because everyone measures differently. We treat Developer Experience as a product — and today that product is fragmented.

**Keystone** is a shared engineering ecosystem (a Golden Path) that standardizes the SDLC across all those teams. It's two independently versioned, Git-distributable packages plus one shared source of truth, so every team — whatever its language — follows the same conventions and reports comparable metrics.

This is a Proof of Concept: the goal is architecture, platform thinking, standardization, and developer experience — not feature completeness.

---

## Who it's for

| User type | What they do in the product |
|---|---|
| Service engineer | Uses the `devex` CLI daily: validate locally, branch, open PRs, bootstrap services. |
| Platform engineer | Maintains the contracts (`conventions.json`, telemetry schema, framework surfaces). |
| Team lead | Reads comparable DORA metrics across teams. |

---

## What we're NOT building

- A production-grade telemetry collector or dashboards (PoC uses NDJSON → CloudWatch/S3).
- Every CLI command and CDK construct fully implemented (PoC = a connected vertical slice).
- Multi-cloud — AWS only.

---

## The domain vocabulary

Full table in [`CLAUDE.md` §1](../../CLAUDE.md) and [`.kiro/steering/conventions.md`](../../.kiro/steering/conventions.md). The short version:

| Term | What it means |
|---|---|
| `devex` | The developer-facing Python CLI. |
| `@keystone/platform` | The TypeScript platform framework. |
| `conventions.json` | Single source of truth — Work ID, branch/commit/PR patterns, telemetry schema. |
| Work ID (`FIN-123`) | Mandatory in branch/commit/PR; the audit "why". |
| DoraEvent | The language-agnostic deploy event; source of all DORA metrics. |

---

## The tech stack

Full details in [`CLAUDE.md` §4](../../CLAUDE.md). The short version: a Python 3.12 CLI (uv · Typer · Pydantic · pytest + Hypothesis); a TypeScript 5 framework (pnpm · github-actions-workflow-ts · AWS CDK v2 · Vitest); deploying serverless to AWS (Lambda + API Gateway), authenticated by GitHub OIDC.

---

## How the system fits together

```
devex CLI ──reads──▶ conventions.json ◀──reads── @keystone/platform
                                                       │ generates
                                                       ▼
                              GitHub Actions workflows ──deploy(CDK)──▶ AWS
                                                       │ emit
                                                       ▼
                                  DoraEvent stream ──▶ DORA metrics + SOC 2 audit
```

The CLI validates locally with the same `conventions.json` the generated CI enforces (zero drift). The framework owns workflow generation, so every team emits the identical telemetry event — which is what makes DORA metrics comparable (ADR-0002).

---

## What "done" looks like

PoC phase. The exit criteria: both packages install from Git, the CLI validates conventions locally, the framework exposes the telemetry contract + a workflow generator, DORA telemetry is demonstrable, and a fork of Transactionify can adopt the ecosystem. Track implementation in the per-feature `.kiro/specs/<feature>/tasks.md` checklists.

---

## Where to find things

| Question | Answer |
|---|---|
| What are we building / why? | [`docs/prd/01-shared-engineering-ecosystem.md`](../prd/01-shared-engineering-ecosystem.md) |
| Why did we choose X? | [`docs/architecture/adr/`](../architecture/adr/) |
| How does a team adopt it? | [`docs/consumption-guide.md`](../consumption-guide.md) |
| How do I contribute? | [`docs/contributing.md`](../contributing.md) |
| What's the agent contract? | [`CLAUDE.md`](../../CLAUDE.md) + [`.claude/rules/`](../../.claude/rules/) |
