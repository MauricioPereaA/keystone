# Keystone — Shared Engineering Ecosystem

> A Golden Path for 10+ independent, full-cycle engineering teams. Keystone standardizes the SDLC so every team — regardless of stack or domain — follows the same engineering conventions and reports **comparable DORA metrics**.

This is a Proof of Concept. The focus is architecture, platform thinking, standardization, and developer experience — not feature completeness.

## The core idea

We don't standardize the *metric*. We standardize the *source of the metric*.

The framework owns CI/CD workflow generation, so every team emits an **identical, language-agnostic telemetry event** on every deploy — whether the service is Python, Go, Clojure, or TypeScript. DORA metrics are derived from that one event stream, which is why they're truly comparable. The same event is the SOC 2 audit record (who / what / when / why), with the **Work ID** (`FIN-123`) as the "why" link.

## Two distributable packages

| Package | Lang / tool | Role |
|---|---|---|
| [`devex` CLI](packages/devex-cli) | Python / `uv` | Developer-side. Local validation (shift-left), git workflow abstractions, project bootstrap. |
| [`@keystone/platform`](packages/platform-framework) | TypeScript / `pnpm` | Platform-side. Type-safe GitHub Actions generators, AWS CDK constructs, DORA telemetry contract. |

Both consume one **single source of truth**: [`conventions/conventions.json`](conventions/conventions.json) — Work ID, branch/commit/PR patterns, pipeline shape, telemetry schema. The CLI validates locally with the exact rules the generated CI enforces. Zero drift.

## Install (directly from Git — no registry needed)

```bash
# CLI
uv tool install "git+https://github.com/MauricioPereaA/keystone#subdirectory=packages/devex-cli"

# Framework
pnpm add "github:MauricioPereaA/keystone#path:/packages/platform-framework"
```

## Repo layout

```
keystone/
├── .kiro/                     # Spec-Driven Development evidence
│   ├── steering/              #   persistent AI context (product, tech, structure, conventions)
│   └── specs/                 #   per-feature requirements / design / tasks
├── conventions/               # ★ single source of truth (CLI + framework consume this)
├── packages/
│   ├── devex-cli/             # Python CLI (uv)
│   └── platform-framework/    # TypeScript framework (pnpm)
├── docs/
│   ├── prd/                   # Product Requirements Documents
│   ├── architecture/adr/      # Architecture Decision Records
│   ├── consumption-guide.md   # how teams install / configure / extend / upgrade
│   └── contributing.md        # inner-source contribution guide
├── .claude/                   # agent operating system (rules + skills) that builds this repo
└── .github/workflows/         # dogfooding: Keystone runs its own generated pipelines
```

## Development workflow (Spec-Driven)

1. **Spec before code.** A PRD (`docs/prd/`) and, for technical forks, an ADR (`docs/architecture/adr/`) precede implementation. The `/prd` skill scaffolds them via interview.
2. **Steering files** (`.kiro/steering/`) give the AI agent persistent context; **specs** (`.kiro/specs/`) drive each feature.
3. **Convention over configuration.** `devex init` generates a repo where the golden path is the default; the framework generates the workflows.
4. **Shift-left.** `devex standards-check` + git hooks fail fast on the workstation, with the same rules CI uses.
5. **Governance.** Conventional commits with Work ID, two-reviewer rule, no direct push to `main`.

## Per-package quickstart

```bash
# CLI
cd packages/devex-cli && uv sync --extra dev && uv run pytest

# Framework
cd packages/platform-framework && pnpm install && pnpm test && pnpm lint
```

## Documentation

- **Architecture & strategy (2-page ADR PDF):** [`docs/architecture/keystone-strategy.pdf`](docs/architecture/keystone-strategy.pdf) — the single-page-pair overview (diagram + homologation / scalability / shift-left strategies). Source: [`keystone-strategy.md`](docs/architecture/keystone-strategy.md); regenerate with `make adr-pdf`.
- **Architecture Decision Records:** [`docs/architecture/adr/`](docs/architecture/adr/) (0001 monorepo · 0002 DORA source · 0003 git governance · 0004 prebuilt dist).
- **Consumption guide:** [`docs/consumption-guide.md`](docs/consumption-guide.md)
- **Contribution (inner-source) guide:** [`docs/contributing.md`](docs/contributing.md)
- **Integration case study (real adoption):** [`docs/case-study-transactionify.md`](docs/case-study-transactionify.md)
- **AWS conventions & cost guardrails:** [`.claude/rules/aws-cdk.md`](.claude/rules/aws-cdk.md)
