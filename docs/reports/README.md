# Reports

This folder holds post-incident and post-mortem reports. Each file covers one significant event — an outage, a data issue, a security finding, or a process failure.

Reports are **permanent record** — never deleted, never edited after the initial write. If a conclusion changes, write a follow-up report that references the original.

---

## Index

[CUSTOMIZE: Add one row per report when it's created. Keep sorted by date.]

| Date | Title | Status |
|---|---|---|

---

## When to write a report

Write a report when any of the following happened:

- **Production outage** longer than 5 minutes (even if self-healed).
- **Data loss or corruption** — any amount, any scope.
- **Security incident** — breach, unauthorized access, credential exposure.
- **Process failure** — a deploy that had to be rolled back, a migration that corrupted rows, a CI gate that was bypassed and caused a regression.
- **Near-miss** — something that *could have* been severe, where the learning is worth preserving even though nothing bad happened.

Bug fixes, routine deploy failures, and expected errors do not need reports.

---

## Report format

Use [`YYYY-MM-DD-template.md`](./YYYY-MM-DD-template.md) as the starting point. File name: `YYYY-MM-DD-short-slug.md`.

A report that takes more than 2 hours to write is too long. Focus on:
1. What happened (facts, timeline).
2. Why it happened (root cause — the *first* cause, not the last symptom).
3. What we're doing so it doesn't happen again (action items with owners and dates).

---

## How reports relate to ADRs

If an incident reveals that an architectural decision was wrong, the corrective action may produce a new ADR that supersedes the old one. Link both directions: the report references the ADR, and the new ADR mentions the incident report that triggered it.
