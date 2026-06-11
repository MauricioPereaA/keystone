# Commits & Pull Requests

**Scope:** Repo-wide (applies to every change in either stack).

**See also:** [`no-direct-push-to-main.md`](no-direct-push-to-main.md) — the agent-specific guardrail that complements this rule. This file describes *what* a clean commit/PR looks like; that file describes *what an AI agent must never do* (push to `main`, force-push, `--admin`-merge, `--no-verify`).

## When this rule applies

You're about to `git commit` or open a PR.

## The rule

### Commits

1. **Conventional-commits-lite**:
   ```
   <type>(<scope>): <short imperative>
   ```
   Types: `feat`, `fix`, `chore`, `refactor`, `test`, `docs`, `ci`, `perf`, `build`.
   Scope examples: `cli`, `framework`, `conventions`, `telemetry`, `workflows`, `constructs`, `ci`, `infra`. [CUSTOMIZE: use your own domain nouns.]

2. **Imperative mood**: "add Work ID commit validation", not "added" / "adds".

3. **Under 70 chars for the subject.** Body (wrapped at 72) is optional — add when the "why" isn't obvious from the diff.

4. **Small, focused commits.** A mixed "fix bug + reformat 200 lines" commit is unreviewable. Split them.

5. **No commented-out code.** `git` remembers; your editor doesn't need to.

6. **Never commit**:
   - `.env` files
   - `node_modules/`, `__pycache__/`, `.venv/`
   - Binary build artifacts
   - Real API keys or passwords (ever, even for dev)

### PRs

1. **Branch naming**: `<type>/<short-slug>` — e.g. `feature/FIN-123-add-validation`, `fix/TX-19-retry-timeout`, `chore/bump-ruff`.
2. **Small PRs**: target < 400 lines of diff (excluding generated files / lockfiles). Larger means breaking it up was possible and you didn't.
3. **Title**: same format as commit subject.
4. **Description template**:
   ```markdown
   ## What
   <one paragraph, what changed>

   ## Why
   <one paragraph, why — link to ticket / ADR / incident>

   ## How it was tested
   - [ ] Unit
   - [ ] Integration
   - [ ] Manual in browser / curl

   ## Checklist
   - [ ] Tests added/updated
   - [ ] Docs updated if applicable
   - [ ] No new env vars missing from `.env.example` / settings / docs
   - [ ] Migrations reviewed and reversible
   ```
5. **CI must be green** before requesting review.
6. **Two approvals** required to merge (`conventions.json` `pullRequest.minReviewers`, enforced by the main-protection ruleset — ADR-0003). Reviewers look for: correctness, tests, adherence to rules in `.claude/rules/`.
7. **Squash-merge**: one PR = one commit on `main`.
8. **Delete the branch** after merge.

### What never merges

- Force-push to `main`.
- Direct push to `main` (bypassing PR).
- `--no-verify` (skipping pre-commit). If a hook fails, fix the cause, don't bypass.
- Bumping a dep without updating the lockfile.
- A migration without the corresponding model change (and vice versa).
- A new env variable not documented per [environment-variables.md](environment-variables.md).

## Why

Conventions pay off over time. A year from now, `git log --oneline | grep feat` is only useful if everyone wrote real types; bisect only works if commits are atomic. Small PRs merge fast; big PRs languish, rebase painfully, and accumulate regressions.

Force-pushes to `main` lose history. `--no-verify` turns the pre-commit safety net into theater. The handful of "never merges" items are the bugs the team hits every six months in companies that don't enforce them.

## Examples

### Good — commit
```
feat(api): add project metrics endpoint

Returns item counts and completion rates per project over time.
Used by the dashboard chart. Fixes PROJ-42.
```

### Good — PR title + description
> **feat(projects): add project metrics endpoint**
>
> ## What
> New `GET /api/projects/{id}/metrics` returning item counts and completion rate over time.
>
> ## Why
> Dashboard chart (PROJ-42) needs this data for the trend visualization.
>
> ## How it was tested
> - [x] Unit test for the aggregation
> - [x] Integration test for the endpoint (happy path + 404 cross-user)
> - [x] Manual curl
>
> ## Checklist
> - [x] Tests added
> - [x] No new env vars
> - [x] No schema/migration changes

### Bad — commit
```
stuff
```
```
Updated files
```
```
WIP
```
All: reject at review. Amend before push.

### Bad — PR
- Title: "updates".
- No description.
- 1,400-line diff across three unrelated features.
- CI red with "well I'll fix it after review".

Reject; ask to split.
