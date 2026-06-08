# 04 — Agents, Skills, and Rules

> How this project is configured to work with AI coding agents (Claude Code, Codex, Cursor, etc.).
> Read this before your first pairing session with an agent.

---

## The three-layer configuration

```
CLAUDE.md / AGENTS.md      ← project overview + mandatory conventions
.claude/rules/*.md          ← task-specific rules (read before doing a task)
.claude/skills/*.md         ← slash commands that automate gate-heavy flows
```

**`CLAUDE.md`** is the entry point. An agent that reads it end-to-end before making changes will know the domain vocabulary, the stack and where things live, the invariants (self-contained CLI, single `DoraEvent` source, conventions defined once), and what never merges (no direct push to `main`, no `--no-verify`).

**`AGENTS.md`** mirrors `CLAUDE.md` for agents that read `AGENTS.md` instead of `CLAUDE.md` (Codex, Cursor, Copilot CLI, Gemini CLI). It's the single bridge — there is one canonical rules home, `.claude/rules/`, so the two never drift.

---

## Rules — one file per task pattern

Before doing a task, the agent (and you, as a reviewer) should check whether a rule file covers it. The index is at [`.claude/rules/00-index.md`](../../.claude/rules/00-index.md).

Each rule file has five sections: **Scope · When this rule applies · The rule · Why · Examples.** If your change doesn't match a rule's scope, skip it.

The most important rules to know on day one:

| Rule | Why it matters |
|---|---|
| `prd-driven-development.md` | Gates all feature work; fires before every other rule |
| `boundaries.md` | The hard constraints that never bend (single source of truth, self-contained CLI, one telemetry source) |
| `no-direct-push-to-main.md` | The agent never pushes directly to `main` |
| `aws-cdk.md` | Serverless + cost guardrails ($100 trial): log retention, no NAT, `cdk destroy`, cdk-nag |
| `audit-logging.md` | The single `DoraEvent` that feeds DORA metrics and the SOC 2 audit trail |
| `commit-and-pr.md` | Work ID everywhere; conventional commits; small PRs; two reviewers; CI green |

---

## Skills — slash commands

Skills are invoked in the agent chat with `/<skill-name>`. Each skill reads the relevant rules before acting, so you don't have to remember them.

| Skill | What it does |
|---|---|
| `/prd` | PRD interview → scaffolds `docs/prd/NN-slug.md` (and an ADR when there's a technical fork) |
| `/preflight` | Lint → typecheck → tests for both packages, stop on first fail |
| `/commit` | Preflight → stage → conventional commit with Work ID |
| `/open-pr` | Preflight → push → `gh pr create` → `/audit-check` → open PR |
| `/audit-check` | Read-only diff scan for Keystone platform gaps (hard-coded conventions, missing telemetry step, static AWS keys, conventions drift) |
| `/new-language` | Add a new app language (Go/Clojure/…) to the golden path — a test-toolchain mapping, never a new metric |
| `/ticket` | Find or create a tracked Work ID for the current branch |

`bash-defensive-patterns` is a reference skill (defensive shell scripting), not a slash command. Skills live in `.claude/skills/`.

---

## The PRD gate (the most important constraint)

The agent will not write feature code without a PRD that covers the scope. If you ask for a feature and no PRD exists, the agent will pause, explain the gate, offer to run `/prd`, and wait for your approval before implementing. Bug fixes, refactors, and dep bumps skip the gate. See [`03-prd-driven-flow.md`](./03-prd-driven-flow.md).

---

## The no-push-to-main rule

The agent will never push or force-push to `main`, merge with `--admin`/bypassed CI, or use `--no-verify`. The only path to `main` is: feature branch → PR → two approvals → squash-merge. To override one specific operation, type the explicit waiver: "I waive `no-direct-push-to-main` for this operation: [reason]." Vague approvals don't count.

---

## Working with the agent effectively

- **Start a session:** state the goal; the agent checks `CLAUDE.md` + relevant rules first.
- **Feature work:** let the agent run the PRD gate (or reference an existing PRD / `.kiro/specs/`).
- **Implementation:** the per-feature `tasks.md` under `.kiro/specs/<feature>/` is the running checklist — `[x]` done, `[ ]` to do.
- **Before a PR:** `/preflight` catches what CI will; `/open-pr` handles push + PR + audit in one step.
