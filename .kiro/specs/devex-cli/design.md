# Design — devex CLI

## Architecture

```
devex (Typer app)
├── cli.py            # command surface: version, standards-check, init, pr, hooks, dora
├── validators.py     # pure functions: validate_branch / validate_commit / validate_pr_title
├── conventions.py    # loads bundled _data/conventions.json (importlib.resources, cached)
└── _data/conventions.json   # build-time copy of /conventions/conventions.json
```

Commands are thin; logic lives in pure, testable modules. Git interaction is isolated in a small `_git()` helper (subprocess) so validators stay I/O-free.

## Key decisions

- **Self-contained packaging (ADR-0001).** `conventions.json` is bundled as package data via Hatch `force-include`. `make sync-conventions` copies the canonical file before build; CI fails on drift. No uv-workspace membership → reliable Git subdirectory install.
- **Single source of truth.** Patterns come only from `conventions.json`; no regex is hard-coded in Python.
- **Typer** for the command surface (type-hint native, good help output); **Rich** for pass/fail rendering.

## Data flow — standards-check

`_git(rev-parse --abbrev-ref HEAD)` and `_git(log -1 --pretty=%s)` → `validate_branch` / `validate_commit` (regex from conventions) → Rich ✓/✗ lines → exit code.

## DORA computation (R5)

Read NDJSON events → group by repo/env → derive:
- deployment_frequency = count of `deployment.succeeded` in window
- lead_time = `timestamp − commit_time` per deploy, summarized (median)
- change_failure_rate = (failed + rolled_back) / total
- mttr = mean(failed → next succeeded) per repo/env

## Error handling

Invalid conventions file → fail fast with a clear message. Non-zero exit on any validation failure (so hooks/CI block). No stack traces to the user; structured detail only with `--verbose`.

## Testing strategy

- Unit: table-driven cases for each validator (valid + invalid).
- PBT (Hypothesis): any well-formed `type/<WORK-ID>-<slug>` passes; any subject lacking a Work ID fails.
- CLI smoke: `devex version`, `standards-check` exit codes.
