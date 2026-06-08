# 02 — Local Setup

> Complete this on Day 1 before writing any code.
> If a step fails, fix the doc before continuing.

---

## Prerequisites

| Tool | Required version | Install |
|---|---|---|
| uv | ≥ 0.4 | https://docs.astral.sh/uv/ |
| Python | 3.12+ | managed by uv (`uv python install 3.12`) |
| Node.js | 20+ | https://nodejs.org |
| pnpm | 9+ | `corepack enable && corepack prepare pnpm@latest --activate` |
| gh CLI | any | https://cli.github.com |
| AWS CLI | v2 (only for deploys) | https://aws.amazon.com/cli/ |

```bash
make doctor   # verifies uv, node, pnpm are present
```

---

## Clone and bootstrap

```bash
git clone git@github.com:MauricioPereaA/keystone.git
cd keystone
make install      # uv sync (CLI) + pnpm install (framework)
```

`make install` installs both packages' dev dependencies. There is no Docker stack,
database, or seed step — Keystone is a CLI + a framework, not a running service.

---

## Verify it's working

```bash
make test                 # pytest + Hypothesis (CLI), Vitest (framework) — all green
make lint                 # ruff + tsc --noEmit
make check-conventions    # the CLI's bundled conventions copy is in sync
PYTHONPATH=packages/devex-cli/src python -m devex.cli version   # or `devex version` once installed
```

If `make check-conventions` fails, run `make sync-conventions`.

---

## Environment variables

Copy `.env.example` to `.env` and fill in any blanks:

```bash
cp .env.example .env
```

Keystone holds almost no runtime secrets — deploys use GitHub OIDC, not stored keys.

| Variable | Required for | Default safe? |
|---|---|---|
| `AWS_REGION` | CDK / deploy workflows | Yes (`us-east-1`) |
| `AWS_DEPLOY_ROLE_ARN` | Assuming the deploy role via OIDC | Set per account |
| `KEYSTONE_TELEMETRY_SINK` | Where deploy events are written | Yes (`cloudwatch`) |

See [`.claude/rules/environment-variables.md`](../../.claude/rules/environment-variables.md)
for the process of adding new ones (single entrypoint per package), and
[`docs/runbooks/github-aws-oidc.md`](../runbooks/github-aws-oidc.md) for the role setup.

---

## Common Makefile targets

```bash
make install            # install both packages
make test               # run all tests
make lint               # run all linters / typecheck
make sync-conventions   # copy canonical conventions.json into the CLI package data
make check-conventions  # CI gate: fail on conventions drift
make build              # build the framework (dist/)
make help               # see all available targets
```

---

## IDE setup

**VS Code** — recommended extensions:
- `charliermarsh.ruff` — Python lint/format (matches CI).
- `ms-python.python` — Python language support.
- `dbaeumer.vscode-eslint` / built-in TS — TypeScript checking (matches `tsc --noEmit`).

Point the Python interpreter at the CLI's uv environment (`packages/devex-cli/.venv`).

---

## Troubleshooting

**`uv tool install … #subdirectory=` fails with a marker/resolution error**
Upgrade uv. The CLI is self-contained (ADR-0001), so the subdirectory install must
resolve without workspace members.

**`pnpm add … #path:` not found**
Subdirectory installs need pnpm ≥ 9.

**`standards-check` passes locally but CI disagrees**
Your bundled conventions copy drifted — `make sync-conventions` (or `uv tool upgrade devex-cli`).

**Deploy job can't assume the AWS role**
Check the OIDC trust policy `sub` matches the repo and the workflow has `id-token: write`.
