# Contributing to Keystone

Keystone is inner-source — any engineer on any team can contribute. The full
guide (the four common contribution types, the local loop, and the review
process) lives at **[`docs/contributing.md`](docs/contributing.md)**.

Quick start:

```bash
make install      # uv (CLI) + pnpm (framework)
make test         # pytest + Hypothesis, Vitest
make lint         # ruff + tsc --noEmit
devex standards-check
```

Before any feature work, read [`.claude/rules/prd-driven-development.md`](.claude/rules/prd-driven-development.md)
(PRD/ADR gate) and [`.claude/rules/commit-and-pr.md`](.claude/rules/commit-and-pr.md)
(Work ID, conventional commits, two-reviewer rule).
