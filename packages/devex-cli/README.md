# devex CLI

The developer-facing interface to the Keystone platform. Python, packaged with `uv`, self-contained, installable directly from Git.

## Install (from Git, no registry)

```bash
uv tool install "git+https://github.com/MauricioPereaA/keystone#subdirectory=packages/devex-cli"
# pin a version:
uv tool install "git+https://github.com/MauricioPereaA/keystone@cli-v0.1.0#subdirectory=packages/devex-cli"
# upgrade across workstations:
uv tool upgrade devex-cli
```

> This package is intentionally **self-contained** (no monorepo workspace deps) so the Git subdirectory install resolves cleanly under `uv`. See ADR-0001.

## Usage

```bash
devex version
devex standards-check       # validate current branch + last commit vs conventions.json (shift-left)
devex check-pr-title "…"    # validate a PR title (used by CI — single source of truth)
devex workid                # print the Work ID for the current change
devex init <service>        # bootstrap a new service onto the golden path
devex adopt                 # add Keystone artifacts to an existing repo (never overwrites app code)
devex pr [--dry-run]        # open a PR (Work ID enforced in the title) via gh
devex hooks install         # install pre-commit/pre-push shift-left hooks
devex pipeline run --local  # simulate the PR pipeline's small-tests stage locally
devex dora                  # report the four DORA metrics from the event stream
```

## Develop

```bash
uv sync --extra dev
uv run pytest --cov=devex --cov-fail-under=80   # unit + property-based (PBT); coverage floor 80%
uv run ruff check .
```

The validators read the **same** `conventions.json` the CI workflows use — local "pass" means CI "pass". The roadmap and remaining tasks live in `.kiro/specs/devex-cli/tasks.md`.
