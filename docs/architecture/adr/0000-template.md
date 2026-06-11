---
title: <decision name>
number: 0000
status: Proposed
authors: [your@email.com]
created: YYYY-MM-DD
updated: YYYY-MM-DD
supersedes: null         # ADR-NNNN if this fully replaces an earlier ADR
superseded_by: null      # ADR-NNNN if a later ADR replaces this one
related_prds: []         # [PRD-NN, ...]
related_adrs: []         # [ADR-NNNN, ...]
linear: []               # [TICKET-NN]
---

<!--
This is the canonical ADR template. Copy it as docs/architecture/adr/NNNN-<slug>.md.

Status lifecycle:  Proposed → Accepted → (later) Superseded
Once Accepted, an ADR is NEVER edited. To change the decision, write a new ADR
that declares `supersedes: ADR-NNNN`; flip the old ADR's `superseded_by:` and
status to `Superseded`. Body stays intact for history.

ADRs answer "we had a non-obvious technical fork — which path did we pick and why".
If the choice was obvious or there was only one reasonable path, you don't need
an ADR; document it in code or a PRD instead.
-->

## Context

<!--
2–3 paragraphs. The technical situation, the constraints, and why this decision
matters now. Include enough background that a reader six months from now can
judge whether the context still holds.

If this ADR was triggered by a PRD, reference it (PRD-NN) so the chain is clear.
-->

## Decision

<!--
One short paragraph. What we're doing. Active voice, present tense.
"We use X" / "We deploy Y to Z" — not "we will" / "we should".
-->

## Consequences

### Positive

<!-- What this unlocks. Be specific. -->
- ...

### Negative / tradeoffs

<!--
The price we're paying. An ADR with no negatives is suspicious — every real
choice has a cost. Be honest; future-you will thank present-you.
-->
- ...

### Follow-ups

<!--
Concrete actions this decision implies. Each item should be actionable
(open a ticket, update a runbook, write a migration). Date or owner if known.
-->
- ...

## Alternatives considered

<!--
At least two. Each with a one-line description and a one-line reason for
rejection. THIS is the value of an ADR — without alternatives, it's just a
description of the decision.
-->

- **<Option A>** — <description>. Rejected because <reason>.
- **<Option B>** — <description>. Rejected because <reason>.

## Change log

<!-- Append-only. One line per meaningful status transition. -->

- YYYY-MM-DD — Proposed (PR #NNN)
