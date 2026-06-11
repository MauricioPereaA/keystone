# No agent-driven push to `main`

**Scope:** Repo-wide. Applies to every assistant / autonomous agent operating in this working tree.

**See also:** [`commit-and-pr.md`](commit-and-pr.md) (the human-side conventions this rule enforces from the agent side), [`boundaries.md`](boundaries.md) §11 (no bypassed quality gates), [`prd-driven-development.md`](prd-driven-development.md) (the gate this push rule sits behind).

## When this rule applies

You are an AI agent (Claude Code, Codex, Cursor, GitHub Copilot CLI, or any equivalent) about to run any command that could land a commit on the `main` branch of this repository — directly or indirectly — including:

- `git push origin main` / `git push <remote> <local>:main` / any push whose ref ends in `:main`.
- `git push --force` / `--force-with-lease` to `main`, even from a feature branch that "just rebased onto main".
- `gh pr merge --admin`, `gh pr merge --bypass-checks`, `gh api … merge` with admin override.
- `git checkout main && git merge feature/x && git push` (a fast-forward push is still a push to main).
- Resetting `main` (`git reset --hard <sha> && git push -f`) for any reason — including "fixing a bad commit".
- Using a personal access token / SSH key with admin scope to bypass the GitHub UI workflow.

It does **not** apply to:

- Pushing a feature branch (`git push origin feat/foo`) — that's the canonical path.
- Reading from `main` (`git fetch`, `git log origin/main`, `git diff origin/main...HEAD`) — read-only is fine.
- Updating a feature branch with the latest `main` (`git pull --rebase origin main`).

## The rule

1. **Never push to `main` directly.** The only path a commit lands on `main` is: feature branch → PR → human review → squash-merge in the GitHub UI (or `gh pr merge --squash` after the human has approved the PR).

2. **Never force-push to `main` under any circumstance.** Even with explicit user instruction in conversation. Force-pushing rewrites history, voids the audit trail SOC 2 evidence collection depends on (per [`soc2.md`](soc2.md) §CC8.1), and breaks anyone who has fetched the old SHA. If the user asks for a force-push to `main`, surface this rule, explain the SOC 2 + collaborator cost, and propose a `git revert` PR instead.

3. **Never bypass branch protection or required checks.** No `--admin`, no `--bypass-checks`, no merging a PR with red CI ("I'll fix it after"). If a check is wrong, fix the check; if a check is irrelevant for the change, get the human to flip it off in the repo settings — never route around it.

4. **Never run `git push --no-verify` or `git commit --no-verify`** as part of the push pipeline. The pre-commit hooks are the in-context defense for secrets (`detect-private-key`), convention checks, and lint hygiene. Bypassing them in an automated context is a P0 trust regression. If a hook fails, fix the underlying cause (per [`commit-and-pr.md`](commit-and-pr.md) §"What never merges").

5. **The squash-merge step belongs to the human by default.** When you finish a PR, your job ends at "PR opened, CI green, awaiting review." Don't auto-merge. Two narrow exceptions:
   - The user explicitly typed "merge it" / "squash and merge" in this conversation referencing this specific PR, AND CI is green, AND the PR has at least one human approval (or the repo's required-review count is zero — most B2B repos require one).
   - The PR is a Dependabot patch-version security PR and the user has pre-authorized auto-merge of those in `CLAUDE.md` or a durable instruction.

   If neither applies, leave the PR open and tell the user it's ready.

6. **The escape valve is explicit, in writing, in the conversation.** A user can override this rule for one specific operation only. They MUST type something equivalent to: "I waive `no-direct-push-to-main` for this operation: <reason>." Vague approvals like "yeah do whatever you need to" do NOT count. The waiver applies to a single command, not "from now on."

7. **If you discover the rule was violated** (a previous turn pushed to `main`, an earlier agent run left a force-push in `git reflog`, etc.) — surface it immediately, before the next action. Don't hide it; don't try to silently fix it. The user needs to know.

## Why this rule exists

Three concrete failure modes it prevents:

- **Lost work from a force-push.** An agent that "rebases main onto its branch" and force-pushes destroys every commit pushed by anyone else since the agent's working copy was last fetched. The collaborator pulling the next morning sees their own work gone with no recovery path beyond `git reflog` on each laptop. Branch protection on the GitHub side is the durable defense; this rule is the in-context one for repos without it (private repos on the free tier — see §"State of branch protection" below).
- **SOC 2 change-management evidence breaks.** Auditors ask "show me the PR + reviewer + CI status for this production change." A direct-to-main push has no PR, no reviewer, and no CI gate. One bypass turns an evidence query from `SELECT * FROM merged_prs` into "let me explain this commit by hand." See [`soc2.md`](soc2.md) §CC8.1.
- **Quality gates become theater.** Every linter, every pre-commit hook, every required CI check is calibrated to the assumption that *every* code change passes through it. The first time an agent merges around the gates "because they're broken on this one PR," the team stops trusting the gates entirely. That's how `--no-verify` becomes the new default.

The cost of the rule is one extra PR per change and ~30 seconds of waiting for a human to click Merge. The cost of breaking it is an incident, an audit finding, or a teammate's lost commit.

## State of branch protection

GitHub branch protection on `main` is the durable, GitHub-side enforcement of this rule. [CUSTOMIZE: update this section with your repo's actual branch protection status — `[your-org]/[your-repo]`.] Two paths to harden if not yet enabled:

- **Cheap and immediate:** upgrade the org to GitHub Team / Pro and enable branch protection on `main` with: require PR, require 1 approval, require status checks (`CLI tests`, `Framework tests`, `Pre-commit`, `Lint title`), block force pushes, block deletion. Track in an ADR.
- **Free alternative:** GitHub Rulesets (available on free private repos in some org tiers) — same controls, different UI. Worth checking before paying for Pro.

Until either is in place, this rule is the only enforcement. That makes it more important, not less.

## Examples

### Good — feature branch → PR → wait for human

```bash
git switch -c chore/foo
# ... edits ...
git add path/to/file
git commit -m "chore(scope): foo"
git push -u origin chore/foo
gh pr create --title "..." --body "..."
# Tell the user: "PR opened at <url>, CI is running. Ready to merge after review."
# DO NOT run `gh pr merge` next.
```

### Good — user explicitly authorized a merge

> User: "Merge PR #142 once CI is green."

```bash
gh pr checks 142  # confirm green
gh pr merge 142 --squash --delete-branch
```

### Bad — auto-merge after CI

```bash
# ✗ The user did not say "merge it." Stop after `gh pr create`.
gh pr create --title "..." --body "..."
gh pr checks <num> --watch
gh pr merge <num> --squash --delete-branch
```

### Bad — direct push to main

```bash
# ✗ Never. Even for a one-line typo fix in a doc.
git switch main
git commit -am "docs: fix typo"
git push origin main
```

### Bad — force-push to "fix" a bad commit on main

```bash
# ✗ This destroys evidence + can erase teammate work. Open a revert PR.
git reset --hard <previous-sha>
git push --force origin main
```

### Bad — admin bypass on a red-CI PR

```bash
# ✗ The CI is red for a reason. Fix it before merging.
gh pr merge 142 --admin --squash
```

## Cross-refs

- [`commit-and-pr.md`](commit-and-pr.md) — the human-facing conventions ("What never merges" §) this rule enforces from the agent side.
- [`boundaries.md`](boundaries.md) §11 — the broader "no bypassed quality gates" rule.
- [`soc2.md`](soc2.md) §CC8.1 — change-management evidence requirements.
- [`prd-driven-development.md`](prd-driven-development.md) — the gate that fires before this one (no code without a PRD; this rule lives downstream of that).

## Escape valve

Match the format of [`boundaries.md`](boundaries.md) §"Escape valve":

1. User states the waiver in writing in the conversation, naming this rule and the reason.
2. Agent acknowledges the waiver, executes the single named operation, then resumes the rule for everything after.
3. The waiver does NOT extend to subsequent commands, future sessions, or "anything similar."

A waiver to "push this hotfix to main" does NOT cover "push the cleanup commit too" — that's a second waiver request.
