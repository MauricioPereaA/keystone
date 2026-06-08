---
date: YYYY-MM-DD
title: "[Short title — what broke]"
severity: P0 | P1 | P2
status: Draft | Final
author: "[name]"
---

# YYYY-MM-DD — [Short title]

## Summary

[1–3 sentences. What broke, how long it was broken, and what the user impact was.
Write this first so an executive can read just the summary and understand the event.]

---

## Timeline

All times in [timezone].

| Time | Event |
|---|---|
| HH:MM | Incident began / first alert fired |
| HH:MM | [First response action] |
| HH:MM | Root cause identified |
| HH:MM | Mitigation deployed |
| HH:MM | Service restored |
| HH:MM | Post-mortem meeting |

---

## Root cause

[The first thing that went wrong — not the last symptom, the first cause. Work backwards
from the failure using "why" until you hit something that could have been prevented.

Good: "A migration added a NOT NULL column without a default; the deploy ran the migration
before restarting the old binary, which tried to insert rows missing the new column."

Bad: "The server was down." (That's the symptom, not the cause.)]

---

## Impact

- **Duration:** [N minutes / hours]
- **Users affected:** [all / subset — describe the subset]
- **Data affected:** [none / describe what was corrupted or lost]
- **Revenue impact:** [none / estimate if applicable]

---

## Detection

[How was the incident discovered? Alert, user report, health-check failure, engineer noticed?
If it was a user report and not an alert, note that — alerting may need improvement.]

---

## Response

[A narrative of what the responders did. Include dead ends and incorrect hypotheses —
they're useful for the next person who faces a similar incident.]

---

## What went well

- [Something that worked as expected — a runbook that was accurate, an alert that fired fast, etc.]
- [Keep this honest; it's not a pat-on-the-back section, it's a "keep doing this" section.]

---

## What went wrong

- [Something that slowed the response — missing runbook, late alert, wrong assumption, etc.]

---

## Action items

| Action | Owner | Due date | Status |
|---|---|---|---|
| [Preventive measure or process fix] | [@person] | [YYYY-MM-DD] | Open |
| [Monitoring / alerting improvement] | [@person] | [YYYY-MM-DD] | Open |
| [Documentation update] | [@person] | [YYYY-MM-DD] | Open |

---

## Related

- ADR: [link if this triggers an architectural change]
- PR: [link to the fix PR]
- Runbook: [link if a runbook was updated or created]
