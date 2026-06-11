# Contribution Guide (inner-source)

Keystone is **inner-source**: any engineer on any of the 10+ teams can contribute
a change without going through the platform team as a gatekeeper. The platform
team owns the *contracts* (`conventions.json`, the telemetry schema, the public
package surfaces); everyone owns the *improvements*.

This guide covers the four most common contributions and the review process.

---

## Ground rules (apply to every contribution)

1. **PRD/ADR gate** (`docs/engineering-rules/prd-driven-development.md`): a new feature or
   behavior change needs an approved PRD first; a non-obvious technical fork needs
   an ADR. Bug fixes, refactors, and docs are exempt.
2. **Work ID** in the branch, commit, and PR title (`conventions.json`). No access
   to the tracker? Open a GitHub issue describing the change — a maintainer assigns
   the Work ID that anchors your branch/commits/PR.
3. **Small PRs** (< 400 LOC of meaningful diff), conventional-commit title.
4. **Two approvals + green CI**, squash-merge, no direct push to `main`
   (`docs/engineering-rules/no-direct-push-to-main.md`). At least one approval must come
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

- Follow the **[`new-language` runbook](runbooks/new-language.md)** — it walks the exact files and checklist, and ends with a **complete worked example (adding Rust, ~20-line PR)**.
- The key principle: you add a **test-toolchain mapping** (how "small-tests" runs
  for that language), **not** a new metric. DORA stays comparable because the
  telemetry event is unchanged (ADR-0002).
- Add a generator snapshot test for the new language and update the consumption
  guide's supported-languages note.

## 3. Add a new framework feature (construct / generator capability)

**You're editing:** `packages/platform-framework/src/{constructs,workflows}/`.

- Keep the public surface minimal — export through the relevant subpath barrel.
- New AWS resources MUST follow `docs/engineering-rules/aws-cdk.md` (log retention, tags,
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
make build                # touched framework src/? rebuild AND COMMIT dist/ —
                          # the shipped artifact (ADR-0004); CI fails on a stale dist
pnpm --dir packages/platform-framework test -- -u   # changed generator output on
                          # purpose? refresh snapshots, then REVIEW the snapshot diff
```

CI re-runs this exact gate; the PR template's checklist covers the audit items
(hard-coded conventions, missing telemetry steps, static AWS keys, drift).

---

## Review process

| Change type | Reviewers | Extra gate |
|---|---|---|
| App-only (no contract touched) | 2 engineers | CI green |
| Workflow generator / new language | 2, incl. 1 maintainer | snapshot tests + telemetry step present |
| New CDK construct | 2, incl. 1 maintainer | `cdk-nag` clean + CDK assertion tests |
| `conventions.json` / telemetry schema | 2, incl. 1 maintainer | drift check + RFC/ADR if breaking |

The goal: a team can land an improvement in hours, not by filing a platform-team
ticket and waiting. The platform team reviews contracts, not every line.

---

## Governance: RFCs, maintainers, deprecation

Inner-source only scales if the *process* is as explicit as the code. Three rules
keep the platform team out of the critical path without losing control of the
contracts.

### RFC process — for breaking contract changes only

The platform has exactly four contract surfaces: the `conventions.json` schema,
the telemetry `schemaVersion` (major), the CLI command/exit-code contract, and the
framework's public exports. A **breaking** change to any of them requires an RFC:

1. Open an issue titled `RFC: <change>` describing the break, who it affects, and
   the migration path. Draft the ADR alongside it (`docs/architecture/adr/0000-template.md`).
2. **5-business-day comment window**, announced to all consuming teams. Silence is
   consent; objections are resolved in the issue, not in DMs.
3. The accepted ADR records the outcome; the implementing PR links both. Per
   [`releasing.md`](../docs/engineering-rules/releasing.md), a breaking telemetry change is
   a coordinated **major** bump.

Additive changes (new command, new generator option, new event field within the
major) skip the RFC — the review table above is enough. Most contributions never
need one; that's the point.

### Maintainer model — rotating, not gatekept

Two maintainers at any time: **one platform engineer + one IC from a consuming
team**, the consumer seat rotating quarterly. Contract-touching PRs need one
maintainer approval (see table); everything else needs any two engineers. The
rotation is what keeps "platform review" from meaning "platform bottleneck" — and
gives consumer teams a standing voice in the contracts they live under.

### Deprecation & upgrade policy

- A deprecated surface keeps working for **2 minor releases or 6 months,
  whichever is longer**, with a warning at the point of use and a CHANGELOG entry
  naming the replacement.
- Removal ships only in a major, behind the RFC above.
- Consumers pin Git tags (`cli-vX.Y.Z` / `framework-vX.Y.Z`), so nothing changes
  under a team silently — upgrading is always an explicit tag bump, and a
  published tag is never reused ([`releasing.md`](../docs/engineering-rules/releasing.md)).
- A `conventions.json` change that alters validation ripples as at least a CLI
  minor; when both packages must move in lockstep, they release together.
