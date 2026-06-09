---
name: commit
description: Stage and commit the current changes safely. Runs preflight (lint + tests), enforces the project's conventional-commit style, and writes a "Title \n\n Description" message with NO Co-authored-by trailer. Aborts cleanly if any quality gate fails.
---

# commit — gated, conventional, atomic

This skill exists so a `/commit` invocation produces a single, atomic, lint-clean commit that wouldn't be rejected by CI. It does not push.

## Inputs

If the user passed text after `/commit`, treat it as the high-level intent (e.g. `"add bulk-import endpoint"`). If empty, infer intent from `git diff --staged` plus `git diff`.

## Steps

1. **Branch guard** — `git rev-parse --abbrev-ref HEAD`. If on `main`, abort with: `"refusing to commit to main; create a feature branch first (git checkout -b <type>/<slug>)"`. Do not proceed.

2. **Preflight** — invoke the `preflight` skill. If it returns RED, abort and surface the failures verbatim. **Never bypass with `--no-verify`.**

3. **Inspect the diff** — `git status --short`, `git diff`, `git diff --staged`, `git log --oneline -5`. Read enough to understand:
   - The single logical change in the diff (if there are two unrelated changes, ask the user to split before committing).
   - The conventional-commit type: `feat`, `fix`, `chore`, `refactor`, `test`, `docs`, `ci`, `perf`, `build`.
   - The scope: `api`, `core`, `frontend`, `auth`, `ci`, `docker`, `claude-rules`, … [CUSTOMIZE: use your domain nouns] (keep it short; see `.claude/rules/commit-and-pr.md`).

4. **Sensitive-file check** — refuse to stage files matching: `.env*` (except `.env.example`), `*.key`, `*.pem`, `id_rsa*`, `credentials*.json`, `service-account*.json`. If the user explicitly listed one, surface a warning and require the literal word `confirm` before proceeding.

5. **Stage** — by default `git add -A`. If the user named specific files, stage only those. Verify with `git status --short` after staging.

6. **Compose the message** — strict format:
   ```
   <type>(<scope>): <subject under 70 chars, imperative, lowercase first letter after the colon>

   <Body wrapped at ~72 chars. Explain WHY, not WHAT — the diff shows the
   what. Bullet lists OK. Reference ticket if known: "Closes TICKET-NN".>
   ```
   - **No `Co-authored-by` trailer. No `Signed-off-by` trailer. No emojis** (unless the user explicitly asked for them in this conversation).
   - **No "🤖 Generated with …" footer.**
   - Body is optional only when the subject is genuinely self-explanatory (`docs: fix typo`, `chore(deps): bump axios to 1.7.7`).

7. **Commit** — use a HEREDOC so the body formatting survives:
   ```bash
   git commit -m "$(cat <<'EOF'
   <type>(<scope>): <subject>

   <body>
   EOF
   )"
   ```
   - **Never `--amend`** without explicit user instruction. Pre-commit failure means a NEW commit after fixing.
   - **Never `--no-verify` / `-n`.** If a hook fires after preflight passed, that's a real signal — surface it and stop.

8. **Post-commit** — `git status` to confirm clean. Print a one-line summary: `"committed <hash> on <branch>: <subject>"`. **Do NOT push** — pushing is the user's call.

## Failure handling

| Symptom | Action |
|---|---|
| Preflight RED | Abort. Surface the failing step. Do not stage. |
| Pre-commit hook auto-fixes a file | The commit aborts; re-stage and create a NEW commit (never `--amend`). |
| Pre-commit hook flags a real issue | Abort. Surface the message. User fixes the cause. |
| User asks to bypass a hook | Refuse. Point at `.claude/rules/boundaries.md` §11 ("No bypassed quality gates"). |
| Diff contains two unrelated changes | Stop. Ask the user to split before continuing. |
| Trying to commit to `main` | Abort with the branch-guard message. |

## Why

Atomic, gated, conventional commits are the substrate everything else depends on: bisect works, `git log --oneline | grep feat` is meaningful, squash-merges produce clean `main` history, and reviewers see one logical change at a time. Bypassing the gate even once corrupts that substrate.

## Examples

### Good message
```
feat(api): FIN-123 add payment validation endpoint

POST /api/payments/validate accepts a payment payload and returns a
field-level validation result. Validates schema, amount bounds, and
currency; emits the standard DoraEvent audit record. Covered by unit
+ property-based tests.

Closes FIN-123.
```

### Bad message
```
feat: stuff

Co-Authored-By: Claude <noreply@anthropic.com>
🤖 Generated with Claude Code
```
