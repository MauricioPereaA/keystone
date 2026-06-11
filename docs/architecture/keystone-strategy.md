# Keystone — Architecture & Platform Strategy

**A Golden Path for 10+ independent, full-cycle engineering teams.** One thesis runs through every decision below: **we don't standardize the *metric* — we standardize the *source* of the metric.** Comparability, governance, and audit become structural properties of the platform, not conventions teams are asked to remember.

## Architecture

```
 +-----------------------------------------------------------------------+
 |             conventions/conventions.json   (single source of truth)   |
 |     Work ID . branch/commit/PR patterns . pipeline shape . telemetry  |
 +----------------------+----------------------------+-------------------+
              reads      |                            | reads
            +-----------v-----------+      +----------v------------------+
            |    devex  CLI (Py)    |      |   @keystone/platform (TS)   |
            | validate . init/adopt |      | workflow generators . CDK   |
            | hooks . dora . pr     |      | GoldenService . telemetry   |
            +-----------+-----------+      +----------+------------------+
   shift-left (local)   | scaffolds                  | generates
                        v                            v
        +------------------ consumer service repo (Py/Go/Clojure/TS) -----+
        |  GitHub Actions:   PR Pipeline  -->  Integration Pipeline       |
        |  small-tests (unit+PBT+contract) -> deploy (GitHub OIDC,        |
        |  no static keys) -> emit DoraEvent                              |
        +----------------------+----------------------------+------------+
                               v                            v
                  +-------------------------+    +--------------------------+
                  | AWS (CDK): Lambda .     |    |   DoraEvent stream       |
                  | API GW . DynamoDB .     |--->|   (CloudWatch / S3)      |
                  | CloudWatch (retention)  | emit +----------+-------------+
                  +-------------------------+               v
                                       devex dora (4 DORA metrics) + SOC 2 audit
```

The CLI (developer-side) and the framework (platform-side) **never import each other**; they integrate only through `conventions.json` and the documented `DoraEvent` schema. That is what lets each be versioned and Git-installed independently, and what guarantees local validation and CI enforcement can never drift.

## Homologation — how 10+ teams adopt consistently

- **Convention over configuration.** The golden path is the *default* that `devex init` (new service) and `devex adopt` (existing service) generate: PR template, CI workflows, hooks, and a `keystone.json`. Adoption is one command, not a migration project — if following the standard is harder than bypassing it, that is a platform bug.
- **One source, two consumers.** Every convention (Work ID `FIN-123`, branch/commit/PR patterns, pipeline shape, telemetry schema) is defined **once** in `conventions.json`. The CLI bundles a synced copy (CI fails on drift); the framework reads it to generate workflows. No pattern is hard-coded in Python or TypeScript.
- **Identical pipelines by construction.** Because the framework — not the application — generates CI and emits telemetry, every team's `small-tests`, deploy steps, and `DoraEvent` are identical regardless of language.

## Scalability — the platform team is not a bottleneck

- **Inner-source by design.** Rough edges become small reviewed PRs that improve the platform for the *next* team. Dogfooding the golden path on a real service (Transactionify) surfaced **six platform gaps**, each fixed as a merged inner-source PR — the platform got better *because* it was used.
- **Self-serve extension.** Adding a language is a contracts-only change behind one interface (`LANGUAGE_TOOLCHAINS`), documented as a `/new-language` recipe — no platform-team gatekeeping for the common case.
- **Independent, registry-less distribution.** Two SemVer-tagged packages install straight from Git (`uv tool install …#subdirectory=`, `pnpm add …#path:`). The framework ships a **prebuilt `dist/`** (ADR-0004) so installs are zero-config on any package manager.

## Shift-left — validation closer to the developer

- **Same rules, three places.** `devex standards-check` and the installed git hooks run the **exact** `conventions.json` rules the generated CI re-runs — a failure surfaces on the workstation, not on a PR an hour later.
- **Fail fast, act locally.** `devex pipeline run --local` simulates the pipeline before a push; the API-contract check validates the OpenAPI schema **pre-deploy** (server-less) and fuzzes the **deployed** URL post-deploy — a split that only emerged from a real adoption.

## Distribution, security & cost

GitHub **OIDC** for AWS — there is no long-lived key to leak. CDK constructs are **cdk-nag-clean** with enforced CloudWatch log retention, `project=keystone` tags, and `RemovalPolicy.DESTROY`; AWS Budgets alarms guard the trial account. The whole loop — generate → deploy → `DoraEvent` → `devex dora` — was run end-to-end on **real AWS** through OIDC, then torn down.

## Key decisions (full ADRs in `docs/architecture/adr/`)

| ADR | Decision | Why it matters |
|---|---|---|
| 0001 | Monorepo + **self-contained** CLI (bundles conventions) | One clone shows the wiring; Git installs resolve reliably |
| 0002 | **Single `DoraEvent`** emitted by generated CI | DORA comparability + SOC 2 audit are structural, not per-team |
| 0003 | Git governance — PR-title convention + ruleset-as-code | Two-reviewer change management is code-reviewable evidence |
| 0004 | Ship **prebuilt `dist/`** (no build-on-install) | Zero-config, package-manager-agnostic installs (registry-less) |

## Validated, not just designed

Transactionify (a real, independent Python + CDK service) adopted the golden path with zero application-code changes. Its first standardized CI run **caught six latent bugs** (red → green on one PR), the adoption drove **six platform fix PRs**, and it **deployed to a real AWS sandbox via OIDC**, emitting a real `DoraEvent` that `devex dora` read back to compute the four metrics. See `docs/case-study-transactionify.md`.
