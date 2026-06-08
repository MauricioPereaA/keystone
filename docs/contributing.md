# Contribution Guide (inner-source)

Keystone is **inner-source**: any engineer on any of the 10+ teams can contribute
a change without going through the platform team as a gatekeeper. The platform
team owns the *contracts* (`conventions.json`, the telemetry schema, the public
package surfaces); everyone owns the *improvements*.

This guide covers the four most common contributions and the review process.

---

## Ground rules (apply to every contribution)

1. **PRD/ADR gate** (`.claude/rules/prd-driven-development.md`): a new feature or
   behavior change needs an approved PRD first; a non-obvious technical fork needs
   an ADR. Bug fixes, refactors, and docs are exempt.
2. **Work ID** in the branch, commit, and PR title (`conventions.json`).
3. **Small PRs** (< 400 LOC of meaningful diff), conventional-commit title.
4. **Two approvals + green CI**, squash-merge, no direct push to `main`
   (`.claude/rules/no-direct-push-to-main.md`). At least one approval must come
   from a platform-team maintainer when you touch a **contract** (see below).
5. **Tests required** for behavior changes; the fix's regression test must fail on
   the unfixed code.

---

## 1. Change a workflow / pipeline

**You're editing:** `packages/platform-framework/src/workflows/`.

- Modify the **generator**, never the generated YAML in consumer repos.
- Every deploy job MUST keep the `emitTelemetryStep` (ADR-0002) — a snapshot test
  asserts this; don't suppress it.
- Add/adjust a snapshot test for the emitted YAML.
- Because this is a cross-team contract, request a platform-team review.

## 2. Add support for a new language (Go / Clojure / …)

**You're editing:** the language switch in the workflow generator + (optionally)
the construct's runtime mapping.

- Run the **`/new-language` skill** — it walks the exact files and checklist.
- The key principle: you add a **test-toolchain mapping** (how "small-tests" runs
  for that language), **not** a new metric. DORA stays comparable because the
  telemetry event is unchanged (ADR-0002).
- Add a generator snapshot test for the new language and update the consumption
  guide's supported-languages note.

## 3. Add a new framework feature (construct / generator capability)

**You're editing:** `packages/platform-framework/src/{constructs,workflows}/`.

- Keep the public surface minimal — export through the relevant subpath barrel.
- New AWS resources MUST follow `.claude/rules/aws-cdk.md` (log retention, tags,
  no NAT) and pass `cdk-nag` (`AwsSolutionsChecks`) in CI.
- Add CDK assertion tests (`Template.fromStack`).

## 4. Change a convention

**You're editing:** `conventions/conventions.json` (the single source of truth).

- This is the highest-blast-radius change: it affects every team at once.
- Run `make sync-conventions` so the CLI's bundled copy matches; CI runs
  `make check-conventions` and fails on drift.
- A telemetry-schema change must be **additive** within a major `schemaVersion`;
  a breaking change requires an ADR and a coordinated major bump.
- Requires platform-team approval.

---

## Local loop before you push

```bash
make sync-conventions     # if you touched conventions.json
make check-conventions    # CI gate
make test                 # pytest + Hypothesis (CLI), Vitest (framework)
make lint                 # ruff + tsc --noEmit
devex standards-check     # branch + commit conventions
```

The `/preflight` skill runs this gate; `/open-pr` runs `/audit-check` (scans for
hard-coded conventions, missing telemetry steps, static AWS keys, drift) and marks
the PR Draft if it finds gaps.

---

## Review process

| Change type | Reviewers | Extra gate |
|---|---|---|
| App-only (no contract touched) | 2 engineers | CI green |
| Workflow generator / new language | 2, incl. 1 platform maintainer | snapshot tests + telemetry step present |
| New CDK construct | 2, incl. 1 platform maintainer | `cdk-nag` clean + CDK assertion tests |
| `conventions.json` / telemetry schema | 2, incl. 1 platform maintainer | drift check + ADR if breaking |

The goal: a team can land an improvement in hours, not by filing a platform-team
ticket and waiting. The platform team reviews contracts, not every line.
