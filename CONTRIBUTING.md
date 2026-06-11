# Contributing to Keystone

Keystone is **inner-source**: any engineer on any of the 10+ teams can land an
improvement without the platform team as a gatekeeper. The platform team owns the
*contracts* (`conventions.json`, the `DoraEvent` schema, the public package
surfaces); everyone owns the *improvements*.

## What you can contribute

| You want to… | Start here | Review gate |
|---|---|---|
| Change a generated workflow / pipeline | [`docs/contributing.md` §1](docs/contributing.md) | snapshot tests + telemetry step present |
| **Add a new language** (Go, Clojure, Rust, …) | **[`docs/runbooks/new-language.md`](docs/runbooks/new-language.md)** — includes a complete worked example (~20-line PR) | 1 maintainer (contract surface) |
| Add a framework feature (construct / generator) | [`docs/contributing.md` §3](docs/contributing.md) | `cdk-nag` clean + CDK assertion tests |
| Change a convention (highest blast radius) | [`docs/contributing.md` §4](docs/contributing.md) | drift check + RFC/ADR if breaking |

## Quick start

```bash
make install      # uv (CLI) + pnpm (framework)
make test         # pytest + Hypothesis, Vitest
make lint         # ruff + tsc --noEmit
devex standards-check
```

## Ground rules

- **Work ID** in branch, commit, and PR title (`conventions.json` — the CLI and CI
  enforce the same rules). No tracker access? Open an issue; a maintainer assigns one.
- **PRD/ADR gate** before feature work
  ([`docs/engineering-rules/prd-driven-development.md`](docs/engineering-rules/prd-driven-development.md));
  bug fixes, refactors, and docs are exempt.
- **Small PRs** (< 400 LOC), conventional-commit title, two approvals + green CI,
  squash-merge, never a direct push to `main`.

## Governance (the short version)

- **RFC process** — breaking changes to any of the four contract surfaces need an
  `RFC:` issue + draft ADR with a **5-business-day** comment window. Additive
  changes skip it entirely.
- **Maintainers rotate** — one platform engineer + one IC from a consuming team,
  quarterly. Contract PRs need one maintainer approval; everything else, any two
  engineers.
- **Deprecation** — a deprecated surface keeps working for **2 minor releases or
  6 months** (whichever is longer); consumers pin Git tags, so nothing changes
  silently.

Full detail — the four contribution walkthroughs, the local loop, the review
matrix, and the governance model: **[`docs/contributing.md`](docs/contributing.md)**.
