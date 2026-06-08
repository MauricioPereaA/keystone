---
name: preflight
description: Run the full local quality gate (conventions sync, lint, typecheck, tests) for both packages and report pass/fail. Used as the gate by the commit and open-pr skills; can also be invoked directly before pushing.
---

# Preflight — full local quality gate

Run before any commit or PR. Exercises the same checks CI runs, in a deterministic order. Each step prints a clear PASS/FAIL line so a stop-and-fix loop is cheap.

## Steps (in order — stop on first failure)

1. **Sanity**
   - `git rev-parse --abbrev-ref HEAD` — confirm we are NOT on `main`. If we are, abort: `"refusing to preflight on main; create a feature branch first"`.
   - `git status --short` — note untracked/modified files (the `commit` skill stages them; flag anything unexpected).

2. **Conventions in sync** — `make check-conventions`
   - On failure, suggest `make sync-conventions` and stop.

3. **CLI lint** — `cd packages/devex-cli && uv run ruff check .`
   - On failure, surface the first 30 lines and stop.

4. **CLI tests** (if the diff touches `packages/devex-cli/`) — `cd packages/devex-cli && uv run pytest -q`
   - Includes unit + property-based (Hypothesis).

5. **Framework typecheck** — `cd packages/platform-framework && pnpm lint` (`tsc --noEmit`).

6. **Framework tests** (if the diff touches `packages/platform-framework/`) — `cd packages/platform-framework && pnpm test`.

7. **Pre-commit hooks** — `pre-commit run --all-files` (whitespace, secrets, actionlint, conventions drift).

8. **Standards check** — `devex standards-check` (branch + commit conventions), or run the validators directly if `devex` isn't installed.

9. **Final report** — a summary table step → PASS/FAIL/SKIPPED, then one of:
   - `"PREFLIGHT GREEN — safe to /commit or /open-pr"`
   - `"PREFLIGHT RED — fix the failures above before committing"`

## Hard rules

- **Never run `--no-verify`** or any flag that bypasses a hook. If a hook fails, fix the cause.
- **Never auto-fix silently.** Suggest `uv run ruff check --fix` / `make sync-conventions`; the user runs it.
- **Never push** during preflight — read-only checks only.
- **Don't reorder steps.** Cheap checks (conventions, lint) before tests.

## Why

Catching a ruff or conventions-drift failure in seconds locally beats a multi-minute CI round trip. Preflight is the gate the `commit` and `open-pr` skills wrap, so its rules apply to every artifact those skills create.
