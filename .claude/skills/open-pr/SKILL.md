---
name: open-pr
description: Push the current branch and open a GitHub PR using the project template. Auto-fills the Linear ticket link, summary, and testing checklist; verifies SOC 2 audit logs and OWASP sanitization on any data-handling change before marking the PR ready for review.
---

# open-pr — push, create, prefill, verify

This skill exists so a `/open-pr` invocation produces a branch, a push, and a PR that wouldn't be rejected by review on procedural grounds. The body uses `.github/pull_request_template.md` as the skeleton; required fields are pre-filled from the diff.

## Steps

1. **Branch guard** — `git rev-parse --abbrev-ref HEAD`. If on `main`, abort with: `"refusing to open a PR from main; create a feature branch first"`. Names should follow `<type>/<short-slug>` per `.claude/rules/commit-and-pr.md` (e.g. `feat/new-feature`, `fix/bug-fix`, or the Linear-suggested `<user>/<ticket-n>-<slug>`).

2. **Up-to-date check** — `git fetch origin main`. If the branch is more than 5 commits behind `main`, surface a warning and ask whether to rebase first (do not auto-rebase without confirmation).

3. **Preflight** — invoke the `preflight` skill. RED ⇒ abort. The PR must not exist if the gate fails locally.

4. **Detect the Linear ticket**:
   - From the branch name (`username/ticket-12-…` → `TICKET-12`).
   - Or scan recent commit messages for `Closes TICKET-\d+`.
   - **If neither present, invoke the [`ticket`](../ticket/SKILL.md) skill.** It searches Linear via MCP for an existing match and, if none fits, runs a short interview and creates one. Capture its return line — `TICKET=TICKET-NN URL=...` or `TICKET=N/A REASON=...` — and use it to fill the `Linear ticket` section.
   - Never open a PR with an empty `Linear ticket` field. The PR template's two valid states are `Closes TICKET-NN` (a real ticket) or `N/A — <reason>` (the user explicitly declined). Anything else fails review.

5. **Read the template** — load `.github/pull_request_template.md` verbatim. Use it as the PR body skeleton.

6. **Auto-fill what is derivable**:
   - **Summary** — write a 2–4 sentence paragraph from `git log <main>..HEAD --oneline` and `git diff --stat main...HEAD`.
   - **Linear ticket** — `Closes TICKET-NN`.
   - **Testing steps** — list the manual reproduction steps the user mentioned in chat; default to "covered by tests in `<paths-touched>`" if none.
   - **Migration & schema safety** — auto-tick `N/A` only if no convention/telemetry/infra file changed.
   - **[CUSTOMIZE: add any project-specific checklist items to auto-fill here.]**

7. **SOC 2 + OWASP verification** — required when the diff touches any data-handling logic:
   - **Heuristic for "data-handling"**: diff touches `conventions/conventions.json`, `packages/platform-framework/src/{workflows,constructs,telemetry}/**`, or any generated workflow.
   - **Audit-log check** — invoke the `audit-check` skill. If it reports platform gaps (hard-coded conventions, missing telemetry step, static AWS keys, drift), **do not mark the PR ready**. Instead:
     - Mark the PR as `Draft` (`gh pr create --draft`).
     - Add a body section: `### Pending: SOC 2 audit trail` with the list of missing call sites.
   - **OWASP sanitization check** — grep the diff for these red flags and surface each as a body callout if present:
     - `dangerouslySetInnerHTML` on user-provided content
     - `Model.objects.raw(` with f-string interpolation
     - `subprocess.run(.*shell=True)`
     - New `httpx` / `requests` calls without an explicit `timeout=`
     - New `<input>` accepting file uploads without size/MIME validation
   - If any red flag fires, open as Draft until addressed.

8. **Push** — `git push -u origin <branch>`. **Never `--force` to `main` or any branch that doesn't belong to the current author.** `--force-with-lease` is acceptable on the user's own feature branch only with explicit ask.

9. **Create the PR** — use `gh pr create` with HEREDOC body so formatting survives. Title is the conventional-commit subject of the most-recent (or only) commit; truncate to ≤70 chars. Default base: `main`.

   ```bash
   gh pr create \
     --base main \
     --title "<conventional-commit subject>" \
     --body "$(cat <<'EOF'
   <prefilled template body>
   EOF
   )" \
     ${DRAFT_FLAG}
   ```

10. **Print the PR URL** — `gh pr view --json url -q .url`. End with one of:
    - `"PR #N opened — Draft (pending: <reasons>)"`
    - `"PR #N opened — ready for review"`

## Hard rules

- **No commits on `main`. No PRs from `main` to anywhere.**
- **No `--force` push to `main`.** Refuse even on user request; warn explicitly.
- **No `--admin` merge.** PRs go through the same review path as everyone else.
- **Never bypass branch protection** (e.g. with admin tokens). If `gh` reports protection failure, surface the message — do not retry with elevated flags.
- **Never delete a section** of the PR template. If a section truly does not apply, fill it with `N/A — <reason>`.
- **Never open a PR with an empty `Linear ticket` field.** The valid states are a real `Closes TICKET-NN` (sourced from branch / commits / `/ticket`) or `N/A — <reason>` after the user explicitly declined ticket creation. The `/ticket` skill is the canonical path; never call the Linear MCP inline here.
- **Audit/OWASP gaps make the PR a Draft.** A green PR title with a red audit gap is exactly the failure mode this skill exists to prevent.

## SOC 2 audit (of the skill itself)

Print every operation before executing it (`git push origin <branch>`, `gh pr create …`). The user sees the full sequence; the GitHub audit log captures the API side.

## Why

A consistent, auto-prefilled PR is the difference between a 2-minute review setup and a 20-minute back-and-forth on procedural fields. The Draft-on-gap pattern surfaces a SOC 2 / OWASP regression *before* a reviewer has to catch it — which is the regime the audit logging and OWASP rules in `.claude/rules/` were designed for.
