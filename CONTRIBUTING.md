# Contributing to Keystone

Keystone is inner-source — any engineer on any team can contribute. The full
guide (the four common contribution types, the local loop, the review process,
and the governance model — RFCs for breaking contract changes, rotating
maintainers, deprecation policy) lives at **[`docs/contributing.md`](docs/contributing.md)**.

Quick start:

```bash
make install      # uv (CLI) + pnpm (framework)
make test         # pytest + Hypothesis, Vitest
make lint         # ruff + tsc --noEmit
devex standards-check
```

Before any feature work, read [`docs/engineering-rules/prd-driven-development.md`](docs/engineering-rules/prd-driven-development.md)
(PRD/ADR gate) and [`docs/engineering-rules/commit-and-pr.md`](docs/engineering-rules/commit-and-pr.md)
(Work ID, conventional commits, two-reviewer rule).
