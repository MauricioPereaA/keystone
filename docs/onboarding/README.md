# Onboarding

Welcome. This folder is the human-readable on-ramp to this project. Read it before you write code.

The goal: in **2–3 hours of reading + 1 hour of setup** you should be able to clone the repo, run it locally, understand what we're building, and ship a small PR without surprising anyone.

If something here is wrong or stale, fix it in the same PR as your other change. Onboarding docs rot fast.

---

## How to read this folder

```
First day      → 01 → 02
First feature  → 01 → 03 → 04
First PR       → 03 → 04
```

If you only have 30 minutes, read these two:
1. **[01 — Project context](./01-project-context.md)** — what we build and for whom
2. **[04 — Agents, skills, and rules](./04-agents-skills-and-rules.md)** — how we collaborate with AI agents

---

## Index

| # | Topic | When you need it |
|---|---|---|
| [01](./01-project-context.md) | Project context | Day 1 |
| [02](./02-local-setup.md) | Local setup | Day 1 |
| [03](./03-prd-driven-flow.md) | PRD-driven flow | Before any feature work |
| [04](./04-agents-skills-and-rules.md) | Agents, skills, and rules | Before collaborating with AI agents |

---

## Where this folder fits

Onboarding is the **front door**. Three other doc surfaces sit behind it:

- **[`docs/prd/`](../prd/)** — *what we're building, for whom, and why* (one PRD per feature)
- **[`docs/architecture/adr/`](../architecture/adr/)** — *we had a fork; here's the path we took* (one ADR per non-obvious decision)
- **[`docs/runbooks/`](../runbooks/)** — *how to operate this in production*

Plus two agent-facing surfaces at the repo root:
- **[`CLAUDE.md`](../../CLAUDE.md)** — full agent bootstrap (the canonical agent context)
- **[`AGENTS.md`](../../AGENTS.md)** — the same context for non-Claude agents
- **[`.claude/rules/`](../../.claude/rules/)** — task-pattern rules (read the relevant one before doing the task)

You'll see these referenced from many onboarding docs. They're the source of truth; onboarding is the tour guide.
