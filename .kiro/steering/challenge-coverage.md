# Challenge Coverage — traceability matrix

> **Single source for "did we cover everything the challenge asks?"** Every
> deliverable, requirement, evaluation criterion, and interview point from the
> Shared Engineering Ecosystem challenge is mapped here to where it lives in the
> repo and its status. Claude Code: keep this in sync as you implement —
> flip 🟡/⬜ → ✅ and update the location when you finish a task.

**Status legend:** ✅ done · 🟡 scaffolded (stub/contract present, logic pending) · ⬜ not started

---

## 1. Deliverables — Ecosystem Prototype Repository

| # | Deliverable | Where | Status |
|---|---|---|---|
| A | Python CLI, `uv tool install git+…#subdirectory=` | `packages/devex-cli/` (`pyproject.toml`, self-contained), `README.md` | 🟡 packaging done + `standards-check` works; verify install after first push |
| B | TS Framework, `pnpm add github:…#path:` | `packages/platform-framework/` (`package.json` subpath exports) | 🟡 telemetry done; workflow/construct generators are stubs |
| C | Unit tests (CLI + framework) | `packages/devex-cli/tests/` (10: unit+PBT), `…/telemetry/telemetry.test.ts` (3) | ✅ |
| D | DORA telemetry: collection · standardization · reporting | contract `…/src/telemetry/`; collection = workflow `emitTelemetryStep`; reporting = `devex dora` | 🟡 contract ✅; collection + `devex dora` pending |
| E | README (architecture · install · usage · dev workflow) | `README.md` | ✅ |
| F | Consumption Guide (install · configure · extend · upgrade) | `docs/consumption-guide.md` | ✅ |
| G | Contribution Guide (inner-source) | `docs/contributing.md`, `CONTRIBUTING.md` | ✅ |

## 2. Deliverable — ADR PDF (≤ 2 pages)

| Section | Where | Status |
|---|---|---|
| Architecture diagram (CLI · framework · service repos · GH Actions · AWS · telemetry) | content in ADR-0001/0002 + the strategy doc diagram | 🟡 content ready; render PDF at project close |
| Homologation strategy (how 10+ teams adopt consistently) | `docs/consumption-guide.md`, ADR-0001 | ✅ written; fold into PDF |
| Scalability strategy (platform team not a bottleneck) | `docs/contributing.md` (inner-source), `/new-language` skill | ✅ written; fold into PDF |
| Shift-left strategy (validation closer to devs) | `devex standards-check` + hooks + `.claude/rules/` | ✅ written; fold into PDF |

## 3. Component A — Developer CLI

| Capability | Where | Status |
|---|---|---|
| ≥1 functional command (PoC minimum) | `standards-check` in `cli.py` | ✅ |
| Standardize git workflows (branch / PR prep / review) | `cli.py` `pr` (stub), `.kiro/specs/devex-cli/tasks.md` #9 | ⬜ |
| Automate conventions / bootstrap (`init` / `adopt`) | `cli.py` `init` (stub), tasks #7–8 | ⬜ |
| Branch / commit / Work ID validation | `validators.py` (+ tests) | ✅ |
| Local pipeline simulation | tasks #12 | ⬜ |
| Distribution: uv · git install · versioned · easy upgrade | `pyproject.toml`, `.claude/rules/releasing.md`, README | 🟡 |

## 4. Component B — Workflow Framework

| Capability | Where | Status |
|---|---|---|
| ≥1 shared artifact: type-safe GHA generator (Option B) | `…/workflows/generatePrPipeline` (stub) | 🟡 |
| ≥1 shared artifact: reusable CDK construct (Option A) | `…/constructs/GoldenService` (stub) | 🟡 |
| Shared pipeline stages / workflow defs / deploy patterns | `…/workflows/`, `conventions.json` `pipelines` | 🟡 |
| Shared telemetry hooks | `…/telemetry/` (contract ✅) + injected `emitTelemetryStep` | 🟡 |
| Distribution: pnpm · git install · multi-repo · reusable types | `package.json` exports, README | 🟡 |

## 5. Shared Engineering Conventions & Git Governance

| Requirement | Where | Status |
|---|---|---|
| Universal Work ID (branch / commit / PR) | `conventions/conventions.json`, `validators.py` | ✅ |
| Standardized PR template | `.github/pull_request_template.md` | ✅ |
| Two-reviewer approval rule | `conventions.json` `pullRequest.minReviewers`, `commit-and-pr.md`, branch protection (GH setting) | 🟡 (doc ✅; enable branch protection on the repo) |
| Convention enforcement via automation | local hooks + `pr-title.yml` + generated PR workflow | 🟡 |

## 6. CI/CD Framework Design

| Requirement | Where | Status |
|---|---|---|
| PR Pipeline — small tests (unit + PBT + API-contract) | `conventions.json` `pipelines.prPipeline`, `testing-conventions.md` | 🟡 (spec ✅; generator todo) |
| PR Pipeline — deploy sandbox → staging → production (CDK) | `aws-cdk.md`, `…/constructs/` | ⬜ |
| Integration Pipeline (on `main`: validate · prod deploy · metrics) | `conventions.json` `pipelines.integrationPipeline`, spec | ⬜ conceptual (impl = bonus D) |

## 7. DORA Metrics & Auditability

| Requirement | Where | Status |
|---|---|---|
| Single source of truth | `conventions.json` + `…/telemetry/` (ADR-0002) | ✅ design |
| 4 metrics comparable across Py/Go/Clojure/TS | `DoraEvent` contract; `devex dora` compute | 🟡 (contract ✅; compute pending) |
| Unified audit trail (who/what/when/why) | `DoraEvent` fields, `audit-logging.md` | ✅ design |
| SOC 2 support | `soc2.md` (CC6.1/6.6/7.2/7.3/8.1/9.2) | ✅ |

## 8. Bonus Deliverables

| Bonus | Where | Status |
|---|---|---|
| A — Local dev env (Docker Compose / LocalStack / Testcontainers) | — | ⬜ |
| B — Pre-push validation (git hooks / pre-commit) | `.pre-commit-config.yaml` ✅; `devex hooks install` (stub, task #10) | 🟡 |
| C — AI-assisted PR reviews (Amazon Q) | — | ⬜ |
| D — Integration Pipeline PoC (working impl) | `…/workflows/` | ⬜ |
| E — Kiro evidence (steering · specs · AI context) | `.kiro/steering/`, `.kiro/specs/` | ✅ |

## 9. Evaluation Criteria (how the work is judged)

| Criterion | How we address it | Where |
|---|---|---|
| Consistency (DORA comparable across 4 languages) | metric derived from one framework-emitted event, not per-language | ADR-0002, `audit-logging.md`, `/new-language` |
| Convention over Configuration | golden path is the generated default; `devex init` + framework generators | `boundaries.md` §4, README |
| Packaging Maturity | two independently versioned, Git-installable packages | `releasing.md`, both `README.md` |
| Feedback Loops | shift-left: local `standards-check` + hooks with the same rules as CI | `logging`/`testing` rules, `/preflight` |
| Inner-Source Readiness | contribution guide + `/new-language` (self-serve, contracts-only review) | `docs/contributing.md` |

## 10. Interview Readiness (post-submission)

| Point | Prep / where | Status |
|---|---|---|
| Architecture deep dive | thesis "standardize the source, not the metric"; CLI↔framework via `conventions.json`; ADRs | ✅ ready |
| Live demo | `init` → bad branch fails `standards-check` → fix → push → workflow → `devex dora` | 🟡 needs implemented commands |
| Installation walkthrough | `uv tool install …#subdirectory=` + `pnpm add …#path:` (test on clean machine) | 🟡 verify after push |
| Integration case study (Transactionify fork) | fork → `pnpm add @keystone/platform` → `devex adopt` → telemetry | ⬜ prepare before interview |

---

### How to use this file

1. Before starting a task, find its row here and in the matching `.kiro/specs/<feature>/tasks.md`.
2. When you finish, flip the status and (if the location changed) update it.
3. If a challenge requirement has **no row**, it was missed — add it and raise it.
