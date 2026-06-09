# SETUP.md — Getting started

Keystone is a monorepo with two independently distributable packages plus a
shared conventions source and an agent operating system (`.claude/`). This guide
gets both packages running locally.

## Prerequisites

```bash
make doctor      # checks uv, node, pnpm
```

Install: `uv` (Python 3.12+), Node 24 (Active LTS, matches CI), `pnpm` 9+. For deploys you'll also want
the AWS CLI configured and a GitHub OIDC role (see `docs/runbooks/github-aws-oidc.md`).

## Install & test both packages

```bash
make install          # uv sync (CLI) + pnpm install (framework)
make test             # pytest + Hypothesis (CLI) and Vitest (framework)
make lint             # ruff + tsc --noEmit
```

Or per package:

```bash
cd packages/devex-cli && uv sync --extra dev && uv run pytest
cd packages/platform-framework && pnpm install && pnpm test && pnpm lint
```

## Single source of truth

`conventions/conventions.json` is consumed by both packages. The CLI bundles a
synced copy; keep it in sync:

```bash
make sync-conventions     # copy canonical → CLI package data
make check-conventions    # CI gate: fail on drift
```

## How this repo is organized

- `conventions/` — the single source of truth (Work ID, branch/commit/PR, telemetry schema).
- `packages/devex-cli/` — the Python CLI (`devex`).
- `packages/platform-framework/` — the TypeScript framework (`@keystone/platform`).
- `.kiro/{steering,specs}/` — Spec-Driven Development context + per-feature specs.
- `docs/{prd,architecture/adr,runbooks}/` — specs, decisions, ops.
- `.claude/` — the agent operating system: `rules/` (read before acting) + `skills/` (slash commands).

## Working with an AI agent

Open the repo in Claude Code (or any agent that reads `AGENTS.md`). It will load
`CLAUDE.md` → `.claude/rules/` → `.kiro/steering/`. The PRD gate
(`.claude/rules/prd-driven-development.md`) fires before any feature work; use the
`/prd` skill to scaffold a spec, then implement against `.kiro/specs/<feature>/tasks.md`.

## Install from Git (consumers)

```bash
uv tool install "git+https://github.com/MauricioPereaA/keystone#subdirectory=packages/devex-cli"
pnpm add "github:MauricioPereaA/keystone#path:/packages/platform-framework"
```
