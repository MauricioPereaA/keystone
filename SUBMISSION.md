# SUBMISSION — Reviewer's Guide

> **Keystone** is a shared engineering ecosystem (a Golden Path) for 10+ independent, full-cycle teams: a Python `devex` CLI for developers, a TypeScript `@keystone/platform` framework for service repos, one source of truth (`conventions.json`), and one telemetry contract (`DoraEvent`). The thesis: **we don't standardize the metric — we standardize the *source* of the metric**, so DORA comparability, governance, and SOC 2 audit are structural properties, not policies.

This document is the evaluation entry point: a ~30-minute reading path, the challenge-to-deliverable map, the design decisions worth interrogating, the evidence index, and an honest account of what is open.

---

## The 30-minute review path

| # | Read | What it proves | ~min |
|---|---|---|---|
| 1 | [`README.md`](README.md) | The thesis, the two packages, the architecture diagram (Mermaid, renders inline) | 3 |
| 2 | [`docs/architecture/keystone-strategy.pdf`](docs/architecture/keystone-strategy.pdf) | **The 2-page ADR deliverable** — architecture + homologation / scalability / shift-left strategies, migration triggers | 5 |
| 3 | [`docs/case-study-transactionify.md`](docs/case-study-transactionify.md) | A **real, separate service** adopted the golden path: 6 latent bugs caught on the first CI run, 6 platform gaps fixed upstream, real AWS deploy via OIDC | 7 |
| 4 | [`conventions/conventions.json`](conventions/conventions.json) + [`packages/devex-cli/src/devex/validators.py`](packages/devex-cli/src/devex/validators.py) | The single source of truth and a consumer that hard-codes nothing | 3 |
| 5 | [`packages/platform-framework/src/telemetry/index.ts`](packages/platform-framework/src/telemetry/index.ts) + [`workflows/steps.ts`](packages/platform-framework/src/workflows/steps.ts) | The `DoraEvent` contract and the framework-emitted telemetry step every deploy job gets | 5 |
| 6 | [`packages/platform-framework/src/constructs/golden-service.ts`](packages/platform-framework/src/constructs/golden-service.ts) | The CDK construct teams inherit: log retention, tags, `RemovalPolicy`, cdk-nag clean | 3 |
| 7 | [`docs/architecture/adr/`](docs/architecture/adr/) | Four real ADRs (0001 monorepo/self-contained CLI · 0002 single DORA source · 0003 git governance · 0004 prebuilt dist), each with alternatives considered | 4 |

Deeper, if time allows: [`docs/consumption-guide.md`](docs/consumption-guide.md) (how a team installs/extends/upgrades), [`docs/contributing.md`](docs/contributing.md) (inner-source governance: RFCs, maintainers, deprecation; the [`new-language` runbook](docs/runbooks/new-language.md) ends with a worked ~20-line example), and [`.kiro/steering/challenge-coverage.md`](.kiro/steering/challenge-coverage.md) (the full requirement-by-requirement traceability matrix).

## Challenge → deliverable map

| Challenge asks | Delivered | Where / evidence |
|---|---|---|
| Python CLI, installable via `uv` from Git | ✅ 10 commands; clean-machine install verified (bundled conventions run green) | `packages/devex-cli/`, [§Verify](#verify-it-yourself) |
| TS framework, installable via `pnpm` from Git | ✅ zero-config install (prebuilt `dist/`, ADR-0004, CI freshness gate) | `packages/platform-framework/` |
| Unit tests, both packages | ✅ **86 Python** (pytest + Hypothesis PBT; 87% current coverage, CI floor ≥80%) + **31 TypeScript** (Vitest, snapshots, CDK assertions) | CI [`ci.yml`](.github/workflows/ci.yml), dogfooded on this repo |
| DORA: collection · standardization · reporting | ✅ one framework-emitted `DoraEvent`; **all four metrics computable** by `devex dora` (`commitTime` is first-class) | ADR-0002, `telemetry/`, `dora.py` |
| 2-page ADR PDF | ✅ rendered + committed | [`keystone-strategy.pdf`](docs/architecture/keystone-strategy.pdf) |
| README · Consumption guide · Contribution guide | ✅ | root + `docs/` |
| Shared conventions & git governance | ✅ Work ID everywhere; PR template; two-reviewer ruleset **applied and active** on `main` (shipped as code: `make protect-main`) | `conventions.json`, ADR-0003 |
| PR pipeline (small-tests → deploy) + Integration pipeline | ✅ generated per language; sandbox deploy **ran live via OIDC**; staging→prod generated, not run live (cost cap) | run [27309574910](https://github.com/MauricioPereaA/transactionify/actions/runs/27309574910) |
| Bonus A–E | ✅ LocalStack dev env · git hooks · Amazon Q reviews (live on PR #17) · Integration-pipeline generator · Kiro steering/specs | `.kiro/steering/challenge-coverage.md` §8 |

## Design decisions worth interrogating

1. **`conventions.json` is a runtime source of truth, not documentation.** Both packages read it (the CLI bundles a synced copy; CI fails on drift). No Work-ID regex exists in Python or TypeScript code — drift is structurally impossible. We deliberately did **not** hand-mirror typed schemas across the two languages; the cross-language contract is the JSON plus the documented event shape (see `docs/engineering-rules/dry-principles.md` for why).
2. **DORA comes from the pipeline, not the application** (ADR-0002). The framework generates every deploy job and injects the telemetry step, so a Python team and a Go team emit byte-identical events. `devex dora` derives all four metrics downstream.
3. **The CLI is self-contained** (ADR-0001) — no workspace deps, conventions bundled — because `uv` Git-subdirectory installs break otherwise. This was a tooling-reality decision, not a style choice.
4. **The framework ships a prebuilt `dist/`** (ADR-0004). Build-on-install failed a real clean-room test (pnpm ≥ 11.5 blocks git-dep build scripts). The committed artifact + a CI freshness gate is the registry-less equivalent of publishing a built package.
5. **Contract testing is split pre/post deploy** (FIN-314). A real adoption proved pre-deploy live-fuzzing is unsatisfiable (no URL exists yet): schema validation runs server-less in small-tests; fuzzing targets the deployed URL.
6. **Cost guardrails are platform properties**: every log group has retention, every resource is tagged, `RemovalPolicy.DESTROY` on PoC state, cdk-nag (`AwsSolutionsChecks`) gates synth — designed against a hard $100-trial-account constraint and verified by deploying and tearing down on real AWS.

## Evidence index

- **Real adoption, shift-left catch:** first standardized CI run on Transactionify — [red, 6 latent bugs caught](https://github.com/MauricioPereaA/transactionify/actions/runs/27232032733) → [green after realigning tests only](https://github.com/MauricioPereaA/transactionify/actions/runs/27235803827) ([adoption PR](https://github.com/MauricioPereaA/transactionify/pull/1); zero app-code changes).
- **Real AWS deploy via OIDC (no static keys):** [run 27309574910](https://github.com/MauricioPereaA/transactionify/actions/runs/27309574910) — `npm ci` → `npx cdk deploy` → real `deployment.succeeded` DoraEvent (verbatim JSON in the case study). Stack verified live (API answered through its Lambda authorizer), then destroyed to zero resources under a $5 AWS Budgets alarm.
- **Cross-language DORA loop on real AWS:** TS `buildEvent`/`serializeEvent` → construct-provisioned CloudWatch log group → read back → `devex dora` computed the four metrics.
- **Inner-source loop:** six platform gaps from the adoption, each a merged PR — [#18 FIN-308](https://github.com/MauricioPereaA/keystone/pull/18), [#19 FIN-309](https://github.com/MauricioPereaA/keystone/pull/19), [#21 FIN-311](https://github.com/MauricioPereaA/keystone/pull/21), [#22](https://github.com/MauricioPereaA/keystone/pull/22)+[#23 FIN-312/313](https://github.com/MauricioPereaA/keystone/pull/23), [#24 FIN-314](https://github.com/MauricioPereaA/keystone/pull/24), [#26 FIN-316](https://github.com/MauricioPereaA/keystone/pull/26). Three were findable only by running the pipeline live.
- **AI-assisted review (Bonus C):** Amazon Q reviewing against `.amazonq/rules`, live on [keystone PR #17](https://github.com/MauricioPereaA/keystone/pull/17).

## Honest scope — open edges, each with its trigger and fix

Nothing below blocks the platform's claims; all are documented where they were found and have a concrete next PR.

1. **CI telemetry lands in the run summary today.** The deploy job emits the real `DoraEvent` to `$GITHUB_STEP_SUMMARY`; the CloudWatch sink exists (the `GoldenService` construct provisions it, and the round-trip through it is proven). *Fix:* add a `put-log-events` write to `emitTelemetryStep` using the deploy job's OIDC credentials. *Trigger:* the first team consuming `devex dora` from the shared stream instead of run logs.
2. **Post-deploy fuzzing not yet wired** (the other half of FIN-314). *Fix:* a `schemathesis run --url <stack output>` step appended to the deploy job. *Trigger:* lands with the same PR as #1.
3. **The generator assumes the trunk is `main`.** The case study hit this once (service trunk was `master`; quick-fixed by renaming). *Fix:* a `trunkBranch` field in `keystone.json` threaded into both pipeline generators. *Trigger:* a second adopting service with a non-`main` trunk.
4. **GitHub merge commits fail the conventions gate on trunk pushes** (observed once, on the case-study repo — it correctly skipped the deploys). *Fix:* skip the commit check on protected-branch pushes, exactly as FIN-313 does for `pull_request` checkouts. *Trigger:* already fired; queued as the next CLI patch.
5. **staging → production promotion is generated but was not run live** — a deliberate cost decision on a personal AWS account; the sandbox leg of the same generated job is proven end-to-end.
6. **Two-reviewer enforcement is live with an admin-bypass escape hatch.** The ruleset (`.github/rulesets/main-protection.json`, applied via `make protect-main`) is **active on `main`**: 2 approvals + 4 required status checks, force-push/deletion blocked. Repo admins can bypass — every bypass is recorded by GitHub, which is itself audit evidence; in an org, the bypass list shrinks to break-glass only.

## Verify it yourself

```bash
# Full local gate (same as CI): 86 + 31 tests, lint, conventions drift
make install && make test && make lint && make check-conventions

# Clean-machine installs, straight from Git — no registry, no config
uv tool install "git+https://github.com/MauricioPereaA/keystone#subdirectory=packages/devex-cli"
devex --version && devex standards-check

pnpm add "github:MauricioPereaA/keystone#path:/packages/platform-framework"  # zero-config: prebuilt dist (ADR-0004)
```

*Author: Mauricio Perea · mauriceperea93@gmail.com*
