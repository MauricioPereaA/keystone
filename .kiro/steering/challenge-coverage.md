# Challenge Coverage — traceability matrix

> **Single source for "did we cover everything the challenge asks?"** Every
> deliverable, requirement, evaluation criterion, and interview point from the
> Shared Engineering Ecosystem challenge is mapped here to where it lives in the
> repo and its status. Claude Code: keep this in sync as you implement —
> flip 🟡/⬜ → ✅ and update the location when you finish a task.

**Status legend:** ✅ done · 🟡 partial (in place; live run / verification pending) · ⏸️ deferred to the validation phase · ⬜ not started

## Build status (snapshot)

The **core + bonuses are built, tested, and dogfooded**:

- **CLI** (`devex`): `standards-check`, `check-pr-title`, `workid`, `init`, `adopt`, `pr`, `hooks install`, `pipeline run --local`, `dora` — 84 tests, 87% coverage.
- **Framework** (`@keystone/platform`): telemetry contract, type-safe PR + Integration workflow generators (Option B), `GoldenService` CDK construct (Option A, cdk-nag clean) — 31 tests, `tsc` + build clean; ships a prebuilt `dist/` for zero-config Git installs (ADR-0004).
- **Governance / CI**: single `conventions.json`; dogfooded `ci.yml` (CLI tests + framework tests + conventions drift) + `pr-title.yml`; two-reviewer ruleset-as-code (ADR-0003).
- **Bonuses**: A (LocalStack dev env) ✅ · B (git hooks) ✅ · C (Amazon Q reviews, live against `.amazonq/rules`) ✅ · D (Integration Pipeline generator) ✅.
- **Dogfooded on a real service**: Transactionify adopted the golden path; its live pipeline caught 6 latent bugs, the adoption surfaced six platform gaps, all fixed by inner-source PRs (FIN-308/309/311/312-313/314/316), and it was deployed to a real AWS sandbox via GitHub OIDC (case study Act 3). See [`docs/case-study-transactionify.md`](../../docs/case-study-transactionify.md).

**The AWS deploy phase is done (✅):** the reference `GoldenService` deployed to a real sandbox and the cross-language DORA loop was closed end-to-end (TS `buildEvent`/`serializeEvent` → CloudWatch → `devex dora`); **Transactionify deployed to a real AWS sandbox through a least-privilege GitHub OIDC role** (no static keys), emitting a real `DoraEvent` ([run 27309574910](https://github.com/MauricioPereaA/transactionify/actions/runs/27309574910)). Every stack was `cdk destroy`'d under an AWS Budgets cap. **Clean-machine install verified** for both packages (`uv tool install git+…` runs the bundled conventions; `pnpm add …` is zero-config after FIN-317). **Remaining:** the ADR PDF render. Known open edges (documented in the case study, not blockers): post-deploy schemathesis fuzzing, shipping the CI `DoraEvent` to the CloudWatch sink, and the trunk-promotion gate (configurable trunk branch + skip the commit check on a protected-branch push).

---

## 1. Deliverables — Ecosystem Prototype Repository

| # | Deliverable | Where | Status |
|---|---|---|---|
| A | Python CLI, `uv tool install git+…#subdirectory=` | `packages/devex-cli/` (`pyproject.toml`, self-contained), `README.md` | ✅ clean-machine `uv tool install` verified (bundled `conventions.json` runs `standards-check` green) |
| B | TS Framework, `pnpm add github:…#path:` | `packages/platform-framework/` (`package.json` subpath exports) | ✅ telemetry + workflow + construct generators implemented (rows 49–52) |
| C | Unit tests (CLI + framework) | `packages/devex-cli/tests/` (71: unit + PBT + CLI smokes), framework `*.test.ts` (22: telemetry + workflows + CDK) | ✅ |
| D | DORA telemetry: collection · standardization · reporting | contract `…/src/telemetry/`; collection = workflow `emitTelemetryStep`; reporting = `devex dora` | ✅ contract + collection (emitTelemetryStep) + reporting (`devex dora`) |
| E | README (architecture · install · usage · dev workflow) | `README.md` | ✅ |
| F | Consumption Guide (install · configure · extend · upgrade) | `docs/consumption-guide.md` | ✅ |
| G | Contribution Guide (inner-source) | `docs/contributing.md`, `CONTRIBUTING.md` | ✅ |

## 2. Deliverable — ADR PDF (≤ 2 pages)

Rendered: [`docs/architecture/keystone-strategy.pdf`](../../docs/architecture/keystone-strategy.pdf) (2 pages) from [`keystone-strategy.md`](../../docs/architecture/keystone-strategy.md) (Mermaid architecture diagram + ADR-style strategy doc; rendered locally, source committed).

| Section | Where | Status |
|---|---|---|
| Architecture diagram (CLI · framework · service repos · GH Actions · AWS · telemetry) | `keystone-strategy.{md,pdf}` §Architecture (ASCII flow) | ✅ rendered (2-page PDF) |
| Homologation strategy (how 10+ teams adopt consistently) | `keystone-strategy.pdf` §Homologation; `docs/consumption-guide.md`, ADR-0001 | ✅ in the PDF |
| Scalability strategy (platform team not a bottleneck) | `keystone-strategy.pdf` §Scalability; `docs/contributing.md`, `new-language` runbook | ✅ in the PDF |
| Shift-left strategy (validation closer to devs) | `keystone-strategy.pdf` §Shift-left; `devex standards-check` + hooks + `docs/engineering-rules/` | ✅ in the PDF |

## 3. Component A — Developer CLI

| Capability | Where | Status |
|---|---|---|
| ≥1 functional command (PoC minimum) | `standards-check` in `cli.py` | ✅ |
| Standardize git workflows (branch / PR prep / review) | `cli.py` `pr` (Work ID enforced from commit + template, via gh) | ✅ |
| Automate conventions / bootstrap (`init` / `adopt`) | `cli.py` `init` + `adopt`, `scaffold.py` (shell-out to framework generator + fallback) | ✅ |
| Branch / commit / Work ID validation | `validators.py` (+ tests) | ✅ |
| Local pipeline simulation | `cli.py` `pipeline run --local` + `pipeline.py` | ✅ |
| Distribution: uv · git install · versioned · easy upgrade | `pyproject.toml`, `docs/engineering-rules/releasing.md`, README | ✅ clean-room `uv tool install git+…#subdirectory=` verified; bundled conventions load |

## 4. Component B — Workflow Framework

| Capability | Where | Status |
|---|---|---|
| ≥1 shared artifact: type-safe GHA generator (Option B) | `…/workflows/` `generatePrPipeline` + `generateIntegrationPipeline` | ✅ |
| ≥1 shared artifact: reusable CDK construct (Option A) | `…/constructs/GoldenService` (Lambda + REST API GW + retention LogGroups + tags + cdk-nag clean) | ✅ |
| Shared pipeline stages / workflow defs / deploy patterns | `…/workflows/` (per-language toolchains, OIDC, telemetry) | ✅ |
| Shared telemetry hooks | `…/telemetry/` (contract ✅) + injected `emitTelemetryStep` in every deploy job | ✅ |
| Distribution: pnpm · git install · multi-repo · reusable types | `package.json` exports + committed prebuilt `dist/` (ADR-0004; no build-on-install, CI freshness gate) | ✅ zero-config `pnpm add …` from Git verified clean-room (npm/pnpm/yarn, incl. pnpm ≥ 11.5) |

## 5. Shared Engineering Conventions & Git Governance

| Requirement | Where | Status |
|---|---|---|
| Universal Work ID (branch / commit / PR) | `conventions/conventions.json`, `validators.py` | ✅ |
| Standardized PR template | `.github/pull_request_template.md` | ✅ |
| Two-reviewer approval rule | `conventions.json` `pullRequest.minReviewers`, `commit-and-pr.md`, ruleset-as-code (`.github/rulesets/main-protection.json` + `make protect-main`), ADR-0003 | ✅ ruleset **active** on `main` (2 approvals + required checks + no force-push; admin bypass recorded) |
| Convention enforcement via automation | `pr-title.yml` (→ `devex check-pr-title`) + `ci.yml` (CLI/Framework tests + conventions drift) + local hooks + generated PR workflow | ✅ |

## 6. CI/CD Framework Design

| Requirement | Where | Status |
|---|---|---|
| PR Pipeline — small tests (unit + PBT + API-contract) | `…/workflows/generatePrPipeline` + per-language toolchains | ✅ (generator emits it) |
| PR Pipeline — deploy sandbox → staging → production (CDK) | `…/constructs/GoldenService` + generated OIDC deploy jobs | ✅ sandbox deployed live via OIDC (transactionify, run 27309574910); 🟡 staging→production promotion not run (cost) |
| Integration Pipeline (on `main`: validate · prod deploy · metrics) | `…/workflows/generateIntegrationPipeline` | 🟡 (generator ✅ — bonus D; triggered live on `main`, surfaced the merge-commit conventions-gate edge — documented in the case study) |

## 7. DORA Metrics & Auditability

| Requirement | Where | Status |
|---|---|---|
| Single source of truth | `conventions.json` + `…/telemetry/` (ADR-0002) | ✅ design |
| 4 metrics comparable across Py/Go/Clojure/TS | `DoraEvent` contract; `devex dora` compute (freq · lead time · CFR · MTTR) | ✅ contract + compute, verified end-to-end on real AWS (TS emit → CloudWatch → `devex dora`) |
| Unified audit trail (who/what/when/why) | `DoraEvent` fields, `audit-logging.md` | ✅ design |
| SOC 2 support | `soc2.md` (CC6.1/6.6/7.2/7.3/8.1/9.2) | ✅ |

## 8. Bonus Deliverables

| Bonus | Where | Status |
|---|---|---|
| A — Local dev env (Docker Compose / LocalStack / Testcontainers) | `docker-compose.yml` (LocalStack) + `make localstack-up/down` + `docs/runbooks/local-dev-env.md` | ✅ |
| B — Pre-push validation (git hooks / pre-commit) | `.pre-commit-config.yaml` ✅ + `devex hooks install` (native pre-commit/pre-push) | ✅ |
| C — AI-assisted PR reviews (Amazon Q) | `.amazonq/rules/*.md` (mapped from `docs/engineering-rules/`) + `docs/runbooks/amazon-q-reviews.md` | ✅ installed + reviewing PRs against `.amazonq/rules` (verified on PR #17) |
| D — Integration Pipeline PoC (working impl) | `…/workflows/generateIntegrationPipeline` (+ snapshot/structure tests) | 🟡 generator ✅; triggered live on `main` (surfaced the merge-commit conventions-gate edge — documented in the case study) |
| E — Kiro evidence (steering · specs · AI context) | `.kiro/steering/`, `.kiro/specs/` | ✅ |

## 9. Evaluation Criteria (how the work is judged)

| Criterion | How we address it | Where |
|---|---|---|
| Consistency (DORA comparable across 4 languages) | metric derived from one framework-emitted event, not per-language | ADR-0002, `audit-logging.md`, `docs/runbooks/new-language.md` |
| Convention over Configuration | golden path is the generated default; `devex init` + framework generators | `boundaries.md` §4, README |
| Packaging Maturity | two independently versioned, Git-installable packages; clean-room install verified both ways; framework ships prebuilt `dist/` (zero-config, ADR-0004) | `releasing.md`, ADR-0004, both `README.md` |
| Feedback Loops | shift-left: local `standards-check` + `devex hooks install` run the SAME `conventions.json` the dogfooded `ci.yml` enforces | `ci.yml`, `devex hooks`, the `make` local gate |
| Inner-Source Readiness | contribution guide + the `new-language` runbook (self-serve, contracts-only review) | `docs/contributing.md` |

## 10. Interview Readiness (post-submission)

| Point | Prep / where | Status |
|---|---|---|
| Architecture deep dive | thesis "standardize the source, not the metric"; CLI↔framework via `conventions.json`; ADRs | ✅ ready |
| Live demo | `init` → bad branch fails `standards-check` → fix → push → workflow → `devex dora` | ✅ run end-to-end live (transactionify PR pipeline deployed to AWS sandbox via OIDC; real `DoraEvent` → `devex dora`) |
| Installation walkthrough | `uv tool install …#subdirectory=` + `pnpm add …#path:` (test on clean machine) | ✅ both verified clean-room from public Git (CLI runs bundled conventions; framework installs zero-config) |
| Integration case study (Transactionify fork) | [`docs/case-study-transactionify.md`](../../docs/case-study-transactionify.md): fork → `devex adopt` → generated CI ran live; surfaced six platform gaps (FIN-308/309/311/312-313/314/316, all fixed), caught 6 latent bugs (red→green on transactionify#1), and deployed to real AWS sandbox via OIDC (Act 3) | ✅ adoption + small-tests + deploy stage done & evidenced (run 27309574910) |

---

### How to use this file

1. Before starting a task, find its row here and in the matching `.kiro/specs/<feature>/tasks.md`.
2. When you finish, flip the status and (if the location changed) update it.
3. If a challenge requirement has **no row**, it was missed — add it and raise it.
