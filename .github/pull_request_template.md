<!--
  Keystone PR template — fill every section. If a section truly doesn't apply,
  write "N/A — <reason>" rather than deleting it.

  Rules of engagement:
    • Work ID required in the PR title: "[FIN-123] …" or "FIN-123: …".
    • Conventional-commit type (feat / fix / chore / refactor / test / docs / ci / perf / build).
    • Target < 400 LOC of meaningful diff. Larger means it should have been split.
    • Two approvals + green CI before merge; squash-merge keeps `main` one-PR-one-commit.

  Full conventions: docs/engineering-rules/commit-and-pr.md
-->

## Work ID

<!-- The tracked unit of work this PR closes. Required (the audit "why"). -->

Closes FIN-

## Context

<!-- One short paragraph: the problem this PR solves and the outcome. -->

## Linked PRD / ADR

<!--
  Feature/behavior changes require a PRD before code lands; architectural choices require an ADR.
    - Rule:  docs/engineering-rules/prd-driven-development.md
  Paste PRD-NN and/or ADR-NNNN. For non-feature PRs (bug fix, refactor, dep bump, CI/docs), write "N/A — <reason>".
-->

PRD- / ADR-

## What changed and why

<!-- Bullet the meaningful changes and the reason behind each. -->

-

## Conventions impact

<!-- Did this touch conventions/conventions.json or the telemetry schema? -->

- [ ] N/A — no change to conventions or the DoraEvent schema, OR
- [ ] `conventions.json` changed AND the CLI bundled copy is in sync (`make check-conventions`), OR
- [ ] Telemetry schema changed additively (`schemaVersion` bumped; ADR if breaking)

## AWS / cost impact

<!-- Per docs/engineering-rules/aws-cdk.md. Backend/infra PRs only. -->

- [ ] N/A — no infra change, OR
- [ ] New CDK resources have log retention + `project=keystone` tags, no NAT gateways, and `cdk destroy` verified

## Tests

<!-- A fix without a regression test is incomplete. Cite the suite (`make test`, file path). -->

- [ ] Unit / property-based / contract tests added or updated and passing locally (`make test`)
- [ ] N/A — no behavior change (refactor / docs / dep bump)
