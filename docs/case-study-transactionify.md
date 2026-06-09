# Case study — adopting the golden path in a real service (Transactionify)

> **What this is.** A real, independent service ([Transactionify](https://github.com/MauricioPereaA/transactionify)
> — a Python + AWS CDK payments API) adopting the Keystone golden path end to end.
> It is the dogfooding evidence behind the platform: not "the framework has tests",
> but "a service we didn't write picked up the golden path, and here is exactly what
> happened." The challenge's integration case study.

## TL;DR

1. Transactionify adopted the golden path with `devex adopt` — generated CI
   workflows, the PR template, `keystone.json`, and the shared conventions, with
   **zero changes to its application code**.
2. Running a real consumer surfaced **five concrete platform gaps**. Each was fixed
   as a small, reviewed inner-source PR in `keystone` — the platform got better
   *because* it was used, which is the whole point of an inner-source platform.
3. The standardized small-tests stage ran in CI **for the first time in this
   service's life** and immediately **caught six latent bugs** (its test suite had
   drifted from its own implementation). That is shift-left working: the catch
   happened on a PR, not in production.
4. The catch→fix loop is visible as two CI runs on the same PR: **red (6 caught) →
   green (fixed)**.

The deploy stage (sandbox → DORA telemetry on real AWS) is the next chapter — see
[Next: the deploy stage](#next-the-deploy-stage).

---

## 1. The adoption

Transactionify is a separate public repo (a fork of a reference payments service).
It uses Python (Lambda handlers + services) with an AWS CDK app, `pip`/`requirements.txt`
(not `uv`-native), and a hand-written `openapi.yaml`. Nothing about it was built for
Keystone — which is exactly why it's a useful test.

Adoption was one command's worth of setup (`devex adopt`), which dropped in:

- the generated **`pr-pipeline.yml`** and **`integration-pipeline.yml`** (from
  `@keystone/platform`, not hand-written),
- the **PR template** and **`keystone.json`** (`{service, language}`),
- a reference to the shared **`conventions.json`** (Work ID / branch / commit rules).

The service kept its own code; it inherited CI, conventions, and the DORA telemetry
contract.

## 2. What the golden path surfaced (the platform got better from real use)

A platform that only runs against textbook services isn't a golden path. Every gap
below was found by adopting Transactionify and fixed as a reviewed PR in `keystone`:

| # | Gap the real service exposed | Fix (merged PR) |
|---|---|---|
| 1 | Git-install of the framework produced no `dist/` (no build on install) | [#18 — FIN-308](https://github.com/MauricioPereaA/keystone/pull/18) `prepare` builds `dist` on install |
| 2 | The python toolchain assumed `uv`-native (`uv sync`); Transactionify is a `pip`/`requirements.txt` service | [#19 — FIN-309](https://github.com/MauricioPereaA/keystone/pull/19) toolchain supports pip **and** uv projects |
| 3 | The contract step hard-coded `openapi.json`; the service ships `openapi.yaml`. Plus an exit-status bug in the pip-install loop failed the step after a *successful* install | [#21 — FIN-311](https://github.com/MauricioPereaA/keystone/pull/21) auto-detect `openapi.yaml\|yml\|json`; fix the loop |
| 4 | The conventions gate ran `devex standards-check` on a `pull_request` checkout — a detached, shallow **merge ref** where the branch is `HEAD` and the commit is a synthetic merge. The gate was red for every consumer, regardless of the change | [#22 — FIN-312](https://github.com/MauricioPereaA/keystone/pull/22) + [#23 — FIN-313](https://github.com/MauricioPereaA/keystone/pull/23) resolve the branch from `GITHUB_HEAD_REF`; skip the unreachable commit |
| 5 | The API-contract step ran `schemathesis run`, which needs a **live URL** — unsatisfiable in pre-deploy small-tests (and never, in-process, for a serverless Lambda) | [#24 — FIN-314](https://github.com/MauricioPereaA/keystone/pull/24) split: validate the schema pre-deploy (server-less), fuzz the deployed URL post-deploy |

Two of these (4 and 5) were found only by running the pipeline **live** — they pass
the framework's own unit tests but fail on a real GitHub `pull_request` checkout. That
is the difference between "tested" and "dogfooded".

## 3. Shift-left in action: the catch→fix loop

Transactionify had **no CI running its Python tests** before adoption, so its suite
had silently drifted from its own code. The golden path's small-tests ran it for the
first time in CI.

### Act 1 — adopt → the pipeline catches 6 real bugs

The first green-gate run reached the test stage and stopped there
([run evidence](https://github.com/MauricioPereaA/transactionify/actions/runs/27232032733)):

```
✓ Validate conventions & resolve Work ID (devex)
✓ Install dependencies
✗ Unit + property-based tests   →   6 failed, 121 passed
- API contract tests            (skipped — job already red)
- deploy-sandbox                (skipped — needs small-tests)
```

The six failures were a genuine pre-existing defect: the suite mocked a removed
function (`query_by_pk`) and asserted a flat-list response, but `list_transactions`
had been refactored to **cursor pagination** (the design `openapi.yaml` describes).
The tests had rotted because nothing had been running them.

```
AttributeError: module '...services.transaction' does not have the attribute 'query_by_pk'
```

### Act 2 — realign the tests → green

The implementation was correct (paginated, matching the spec), so the fix was to
realign the six stale tests to the paginated contract (patch `query_by_pk_paginated`,
assert the `{transactions, has_more, next_cursor}` envelope, add a test for the
pagination branch) — **no application code changed**. The pipeline went green
([run evidence](https://github.com/MauricioPereaA/transactionify/actions/runs/27235803827)):

```
✓ Validate conventions & resolve Work ID (devex)
✓ Install dependencies
✓ Unit + property-based tests              →   128 passed
✓ API contract: validate OpenAPI schema
```

The catch and the fix are two runs on the same PR
([transactionify#1](https://github.com/MauricioPereaA/transactionify/pull/1)) — the
audit trail of shift-left value.

## 4. What this demonstrates against the challenge criteria

- **Convention over configuration** — a real service got the full golden path from
  `devex adopt`, not bespoke CI.
- **Packaging maturity** — `@keystone/platform` and `devex` install from Git into an
  unrelated repo; the install gaps that broke that (FIN-308/309) are closed.
- **Inner-source readiness** — every rough edge became a small reviewed PR that made
  the platform better for the *next* team, not a fork or a workaround.
- **Feedback loops** — the standardized pipeline caught latent bugs on a PR, the
  earliest place it could.
- **Consistency** — the contract step now means the same thing for every team
  (schema validation pre-deploy), and the DORA event is framework-emitted, not
  per-service.

## Next: the deploy stage

The PR pipeline's `deploy-sandbox` job is the remaining chapter and needs a real AWS
account:

- the generated deploy job pins a `pnpm` version (a gap the live run exposed — the
  next platform fix),
- GitHub **OIDC** role (no static keys) + **AWS Budgets** alarms before any deploy,
- `cdk deploy` → a real **`DoraEvent`** → `devex dora` → **post-deploy schemathesis
  fuzzing** (the other half of FIN-314, against the deployed URL) → `cdk destroy`.

That closes the loop from "a service adopts the golden path" to "its deploys feed the
shared DORA + audit stream on real infrastructure."
