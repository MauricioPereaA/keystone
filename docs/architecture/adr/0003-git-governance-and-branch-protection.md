---
title: Git governance — unified PR-title convention + branch-protection ruleset
number: 0003
status: Accepted
authors: [mauriceperea93@gmail.com]
created: 2026-06-08
updated: 2026-06-08
supersedes: null
superseded_by: null
related_prds: [PRD-01]
related_adrs: [ADR-0001, ADR-0002]
linear: []
---

## Context

The challenge requires Git Governance: a mandatory **Work ID** on every branch,
commit, and PR title, a **two-reviewer** approval rule, and a standardized PR
template. The scaffold shipped two *contradictory* PR-title rules: `conventions.json`
`pullRequest.titlePattern` wanted a bracketed Work-ID prefix (`[FIN-123] …`), while
the CI linter (`.github/workflows/pr-title.yml`, via `amannn/action-semantic-pull-request`)
wanted a Conventional Commit (`feat(scope): …`). No single title can satisfy both,
and the CI comment itself notes squash-merge stamps the PR title onto `main` as the
commit subject — so the title must *be* a valid commit subject.

Separately, server-side enforcement of the two-reviewer rule (GitHub branch
protection / rulesets) is gated behind a paid plan for **private** repositories.
This repo is currently a free private repo, so neither classic branch protection
nor rulesets can be enabled via the API today (both return HTTP 403 "Upgrade to
GitHub Pro or make this repository public").

## Decision

**One Work-ID-anchored convention spans branch, commit, and PR title.** A PR title
uses the *same* shape as a commit subject — `<type>(<scope>)?: <WORK-ID> <subject>`
— because squash-merge turns it into that commit. `conventions.json`
`pullRequest.titlePattern` is aligned to the commit pattern, and CI validates the
title by invoking `devex check-pr-title` (which reads `conventions.json`) rather
than a regex hard-coded in YAML — keeping the single source of truth intact
(`boundaries.md` §1). The untrusted title is passed via an env var, never
interpolated into the shell (`security.md` §8). Dependabot PRs, which carry no
Work ID by design, are exempted.

For the two-reviewer rule, we **commit the branch-protection ruleset as code**
(`.github/rulesets/main-protection.json` + `scripts/apply-branch-protection.sh`,
runnable via `make protect-main`) so enforcement is one command away the moment
the repo is made public or upgraded to GitHub Pro/Team. Until then, the rule is
enforced procedurally (PR template, `commit-and-pr.md`, the agent-side
`no-direct-push-to-main.md`).

## Consequences

### Positive

- A single convention family (branch / commit / PR title), all anchored on the
  Work ID — zero drift, and the PR title is always a valid `main` commit subject.
- CI and local validation share one source of truth (`conventions.json` via the
  `devex` CLI); changing the rule in one place updates both.
- Branch protection is captured as reviewable, version-controlled code — applying
  it is auditable and reproducible (SOC 2 CC8.1), not a click-trail in a UI.

### Negative / tradeoffs

- No server-side two-reviewer enforcement until the repo is public or on a paid
  plan; until then the rule depends on discipline + the agent guardrail.
- A solo repo cannot literally satisfy "two reviewers" (you can't approve your own
  PR), so the owner merges via bypass — real enforcement begins when collaborators
  exist.
- The CI title check installs/uses `uv` + the CLI, marginally slower than a pure
  marketplace action — accepted for the single-source-of-truth guarantee.

### Follow-ups

- Run `make protect-main` once the repo is public or upgraded; verify with
  `gh api repos/<owner>/<repo>/rulesets`.
- Add `required_status_checks` to the ruleset once the CLI/framework test workflows
  land (Phase 3), so green CI is required alongside the two approvals.

## Alternatives considered

- **Keep `[FIN-123] …` PR titles, drop the Conventional-Commit linter.** Rejected:
  squash-merge would put a non-conventional subject on `main`, breaking
  `git log --oneline | grep feat` and the commit convention.
- **Keep the Conventional-Commit linter with a hard-coded Work-ID regex in
  `pr-title.yml`.** Rejected: hard-coding a convention pattern in CI duplicates the
  source of truth and will drift — the exact anti-pattern this project exists to
  prevent (`boundaries.md` §1).
- **Make the repo public now to unlock free rulesets.** Rejected *as a default* —
  left to the owner's choice; the committed ruleset makes enabling it trivial
  whenever they decide.

## Change log

- 2026-06-08 — Proposed + Accepted (PR #pending)
