---
name: ticket
description: Find or create a Linear ticket via the linear-server MCP for the work currently on the branch. Searches existing issues for a match first, then runs a short interview and creates a new one only if nothing fits. Returns the ticket ID + URL so the caller (usually /open-pr) can stamp the PR body. Invoked automatically by /open-pr when no ticket is detected on the branch — never opens a PR without one.
---

# ticket — find or create the Linear ticket for this branch

Use when:
- `/open-pr` couldn't detect a Linear ticket on the branch (no `ticket-NN` slug, no `Closes TICKET-NN` in commits) — this skill runs as a sub-step there.
- The user invokes `/ticket` directly to create a ticket before starting work.
- An agent needs a ticket reference for any context that requires one (commit body, PR description).

Do **not** use when:
- A ticket reference already exists. Re-confirming creates duplicate work; trust the branch name / commit message.
- The change is explicitly ticketless (Dependabot bumps, merge-commit cleanup, doc-only edits where the convention is `N/A — <reason>`). Surface the option and let the user decline.

## Inputs

Inferred from the current session — don't re-ask if you already know:
- **Branch name** — `git rev-parse --abbrev-ref HEAD`
- **Diff summary** — `git log origin/main..HEAD --oneline` + `git diff --stat origin/main...HEAD`
- **Recent user-provided context** — the request that started this conversation usually describes the work
- **Linked PRD** — if `docs/prd/NN-<slug>.md` was just authored, its title and overview seed the ticket

## Steps

### 1. Sanity-check the MCP

Confirm the linear-server MCP is reachable. If `mcp__linear-server__list_teams` errors, surface the message and stop — don't fall back to manual ticket creation in the browser, the user can run `/ticket` after wiring the MCP.

### 2. Search for an existing match before creating

Cheaper than a new ticket every time. Use the diff summary + branch slug as the search corpus.

- `mcp__linear-server__list_issues` with `query=<2–4 keywords from the work>` and `assignee=me` (the most common case) and `state=unstarted,started,in_progress`.
- If nothing matches, try without the assignee filter (the work might be assigned to someone else but still tracked).

If a candidate matches:
- Show the user: ticket ID, title, status, URL.
- Ask: *"Use TICKET-NN, or create a new one?"*
- If they pick the existing one, return that and stop.

### 3. Confirm a new ticket is needed

Don't create silently. Tell the user what you'll do:

> No matching Linear ticket found. I'll create a new one with title `<draft title>` on team `<team>`. Confirm or edit before I save?

Wait for confirmation. The user can also say "no, this is N/A" — in that case return `N/A — <reason>` and let `/open-pr` record it as a ticketless change.

### 4. Resolve the team

Tickets need a team. Resolution order:
- If the user has a default in their workflow (e.g. always `[CUSTOMIZE: your team name]`), respect it.
- Otherwise, `mcp__linear-server__list_teams` and ask the user to pick.
- Cache the choice in conversation; don't ask twice.

### 5. Run the short interview

Only ask what isn't already inferable. The defaults below are usually right.

| Field | How to fill | Default if user is silent |
|---|---|---|
| Title | One imperative line, ≤ 70 chars. Mirror the PR title style: `<type>(<scope>): <subject>`. | First line of the diff summary |
| Description | 2–4 sentence problem + intent. If a PRD exists, reference it (`Implements PRD-NN`). | Concatenated diff summary + branch slug |
| Team | Step 4. | — |
| Project | If the PRD lists a project, use that. Otherwise ask once; cache the answer. | None |
| Priority | 0=No / 1=Urgent / 2=High / 3=Medium / 4=Low | 3 (Medium) |
| Assignee | The current user (`mcp__linear-server__get_user` with `query="me"`). | self |
| Labels | Optional. If the PR title is `feat:` / `fix:` / `chore:`, mirror as a label. | none |

Keep the whole interview to **one or two prompts** — batch the questions, don't drip-feed.

### 6. Create the ticket

```text
mcp__linear-server__save_issue
  team: <id from step 4>
  title: <agreed title>
  description: <agreed description>
  priority: <0–4>
  assignee: me
  state: "Todo" | "In Progress"   # In Progress if work is already underway
  labels: [...]
  project: <id or null>
```

The MCP returns the ticket ID (`TICKET-NN`) and URL. Surface both back to the user immediately:

```
Created TICKET-NN: <title>
URL: https://linear.app/[your-team]/issue/TICKET-NN
```

### 7. Optional: rename the branch

If the branch is generic (`feat/foo`, `chore/cleanup`), offer to rename to the Linear convention `<user-handle>/ticket-NN-<slug>`:

```bash
git branch -m <user>/ticket-NN-<slug>
git push origin -u <user>/ticket-NN-<slug>
git push origin --delete <old-branch>   # only after the new push succeeds
```

Skip this step if the branch was already pushed and a PR is open against it (renaming would orphan the PR).

### 8. Return

The caller expects a structured result. Return as a single line:

```
TICKET=TICKET-NN  URL=https://linear.app/[your-team]/issue/TICKET-NN
```

…or, on user-declined creation:

```
TICKET=N/A  REASON=<the reason the user gave>
```

Calling skills (notably `/open-pr`) consume this directly to fill the `Linear ticket` field in the PR body.

## Hard rules

- **Never create a duplicate.** Always run step 2 first; always show the user the candidate matches before creating.
- **Never silently create.** The user sees the proposed title, description, and team before the MCP write happens.
- **Never invent ticket IDs.** Only use IDs the MCP returned in this session.
- **Never write fake `Closes TICKET-NN` lines** when the user explicitly chose ticketless. The PR convention is `N/A — <reason>`; honor it.
- **Don't rename a pushed branch with an open PR.** Linear conventions don't justify orphaning a PR.
- **One ticket per branch.** If the work spans multiple tickets, the branch should be split — surface that to the user instead of creating two and pretending one branch covers both.

## Why

The "PR with no Linear ticket" pattern erodes the SOC 2 change-management trail (`.claude/rules/soc2.md` §CC8.1: "ticket link in the PR template → traceable change history"). Manually flipping into the Linear UI mid-PR-flow is exactly the friction point that produces ticketless PRs in practice.

Wiring the MCP into `/open-pr` removes the friction. The user gets a 30-second interview instead of a tab switch, the ticket is created in the right team with the right context, and the PR body's `Linear ticket` field is correctly populated before the PR is opened. The audit trail is whole by default.

## Examples

### Good — search hit, no creation

```
$ /ticket
Searching Linear for matches to "feat/bulk-import"…
Found 1 candidate:
  TICKET-58 — feat(api): bulk-import records (state: started)
  https://linear.app/[your-team]/issue/TICKET-58

Use TICKET-58, or create a new ticket?
> use TICKET-58
TICKET=TICKET-58  URL=https://linear.app/[your-team]/issue/TICKET-58
```

### Good — interview + create

```
$ /ticket
No matching ticket. Proposed:
  Title:       feat(api): bulk-archive records endpoint
  Description: Implements PRD-03. Adds POST /api/records/bulk-archive…
  Team:        [CUSTOMIZE: your team name]
  Priority:    Medium
  Assignee:    me
Confirm? (yes / edit-title / edit-description / cancel)
> yes
Created TICKET-72: feat(api): bulk-archive records endpoint
URL: https://linear.app/[your-team]/issue/TICKET-72
TICKET=TICKET-72  URL=https://linear.app/[your-team]/issue/TICKET-72
```

### Good — explicit ticketless

```
$ /ticket
Searching Linear… no matches. This looks like a Dependabot bump — create a ticket anyway?
> no, N/A
TICKET=N/A  REASON=dependency bump (Dependabot grouped weekly PR)
```

### Bad — silent creation, dupe risk

```
$ /ticket
Created TICKET-73: foo                              # ✗ never showed the user, and TICKET-58 already exists
```
