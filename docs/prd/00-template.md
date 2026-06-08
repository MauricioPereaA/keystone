---
title: <feature name>
number: NN
status: Draft
authors: [your@email.com]
created: YYYY-MM-DD
updated: YYYY-MM-DD
updates: null            # PRD-NN if this revises an earlier PRD
supersedes: null         # PRD-NN if this fully replaces an earlier PRD
related_adrs: []         # [ADR-0002, ...]
linear: []               # [TICKET-NN]
---

<!--
This is the canonical PRD template. Copy it as docs/prd/NN-<slug>.md.
The /prd skill scaffolds from this file automatically — you usually don't
copy by hand.

Status lifecycle:  Draft → Approved → Implemented → (later) Superseded
Bump "updated" and append to the Change log on every meaningful edit.
Never delete content from a PRD; supersede with a new PRD instead.
-->

## Overview

<!-- 2–3 paragraphs. Problem first, then intent. No solutioning yet. -->

## Goals

<!-- What does success look like? Measurable where possible. -->
- ...

## Non-goals

<!-- Explicit scope cuts. Just as important as goals. -->
- ...

## User stories

<!-- Format: As a <role>, I want <capability>, so that <outcome>. -->
- As a [User], I want ..., so that ...

## Functional requirements

<!--
Numbered, testable. Each one should map to an acceptance criterion or test.
"The system MUST/MAY/SHOULD ..." style helps keep them concrete.
-->

1. ...
2. ...

## Non-functional requirements

<!--
The defaults below are inherited from .claude/rules/. Only call out exceptions
or stricter bars. If everything is "default", write "All defaults apply".

Defaults inherited:
  - security: GitHub OIDC (no static keys), no secrets/PII in logs (.claude/rules/security.md)
  - audit/telemetry: deploys emit the standard DoraEvent (.claude/rules/audit-logging.md)
  - testing: CLI ≥80% (pytest + Hypothesis), framework via Vitest + clean tsc (.claude/rules/testing-conventions.md)
  - AWS cost: log retention + tags, no NAT, cdk-nag clean (.claude/rules/aws-cdk.md)
-->

- All defaults apply.

## UX / API / Data notes

<!--
High-level only — implementation details belong in code.
  - UX: link to wireframes / Figma, or a 1-paragraph description per screen
  - API: method + path + payload shape (one line each)
  - Data: new models / fields / migrations expected
-->

### UX
- ...

### API
- ...

### Data
- ...

## Telemetry & success criteria

<!--
What event do we log? What does "this shipped successfully" look like 30 days
post-launch? Tie back to Goals.
-->

- ...

## Rollout

<!--
Feature flag? Staged? Direct? Migration order? Backfill?
Default for MVP: direct rollout, no flag, single PR.
-->

- ...

## Open questions

<!--
Things that block "Approved". Each should have an owner or a deadline.
Empty when status reaches Approved.
-->

- ...

## Change log

<!-- Append-only. One line per meaningful change. -->

- YYYY-MM-DD — Created (PR #NNN)
