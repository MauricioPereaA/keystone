# Tech Steering — Keystone

## Stack

| Area | Choice |
|---|---|
| CLI language / packaging | Python 3.12 · `uv` (tool install + tool upgrade from Git) |
| CLI framework | Typer (Click-based) + Rich; Pydantic for schema validation |
| Framework language / packaging | TypeScript 5 (ESM) · `pnpm` (Git subdirectory install via `#path:`) |
| Workflow generation | `github-actions-workflow-ts` (compile-time-validated GitHub Actions) |
| Infrastructure as Code | AWS CDK v2 (TypeScript) |
| App runtime (services) | AWS Lambda; API via Amazon API Gateway (REST) |
| Telemetry sink (PoC) | NDJSON → CloudWatch Logs / S3 (always-free tier) |
| Tests | CLI: pytest + Hypothesis (PBT). Framework: Vitest. |
| Lint | Ruff (Python) · `tsc --noEmit` (TS) |

## Hard technical invariants

1. **`devex-cli` is self-contained** — no monorepo workspace dependencies; `conventions.json` is bundled as package data. This keeps `uv tool install git+...#subdirectory=` reliable (uv has known marker-resolution issues with workspace members). See ADR-0001.
2. **`conventions.json` is the single source of truth** — both packages read it. Never duplicate a pattern; reference the file.
3. **The telemetry event schema is a contract** — additive changes only; bump `schemaVersion`. The four DORA metrics derive from it. See ADR-0002.
4. **Workflows are generated, never hand-written** — teams call the generator (directly or via `devex init`).

## AWS cost discipline (trial account, ~$100)

The serverless stack (Lambda + API Gateway + DynamoDB + CloudWatch) is ~$0/month at PoC scale. Money leaks come from forgotten resources, not compute:

- **No NAT Gateways** (≈$32/mo each) — keep Lambdas out of private subnets needing NAT.
- **Set CloudWatch Logs retention on every log group** (default is forever). Use 30 days.
- **`cdk destroy` after every demo.** Tag all resources `project=keystone` for cleanup + cost attribution.
- **Prefer HTTP API** where the challenge allows ($1/M) over REST ($3.50/M) — though the reference uses REST API Gateway.
- **Set an AWS Budgets alarm** at $25 / $50.

Full rules: `.claude/rules/aws-cdk.md`.

## Polyglot future

Services may be Python, Go, Clojure, or TypeScript. The CLI and telemetry contract are language-agnostic; only the framework's per-language test toolchain selection (`uv` / `go test` / `lein` / `vitest`) varies, behind one workflow generator interface.
