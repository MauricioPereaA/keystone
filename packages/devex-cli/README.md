# devex CLI

The developer-facing interface to the Keystone platform. Python, packaged with `uv`, self-contained, installable directly from Git.

## Install (from Git, no registry)

```bash
uv tool install "git+https://github.com/MauricioPereaA/keystone#subdirectory=packages/devex-cli"
# pin a version:
uv tool install "git+https://github.com/MauricioPereaA/keystone@v0.1.0#subdirectory=packages/devex-cli"
# upgrade across workstations:
uv tool upgrade devex-cli
```

> This package is intentionally **self-contained** (no monorepo workspace deps) so the Git subdirectory install resolves cleanly under `uv`. See ADR-0001.

## Usage

```bash
devex version
devex standards-check     # validate current branch + last commit vs conventions.json (shift-left)
devex init <service>      # bootstrap a new service onto the golden path  (scaffolded)
devex dora                # report the four DORA metrics from the event stream  (scaffolded)
```

## Develop

```bash
uv sync --extra dev
uv run pytest             # 10 tests: unit + property-based (PBT)
uv run ruff check .
```

The validators read the **same** `conventions.json` the CI workflows use — local "pass" means CI "pass". Implement the scaffolded commands against `.kiro/specs/devex-cli/tasks.md`.
