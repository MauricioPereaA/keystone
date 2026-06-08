---
name: new-language
description: Add a new application language (Go, Clojure, TypeScript, …) to the Keystone golden path so a team in that stack gets the same workflows, telemetry, and DORA comparability. Use when onboarding a polyglot team or extending the workflow generator's per-language support. The key principle — add a test-toolchain mapping, never a new metric.
---

# new-language — extend the golden path to another stack

Use when a team's service is written in a language the framework's workflow
generator doesn't yet have a small-tests toolchain for.

Do **not** use to change *what* a metric means — DORA stays comparable because
the telemetry event is identical across languages (ADR-0002). You are only
teaching the generator how to run "small-tests" for the new language.

## Principle

The DoraEvent is language-agnostic and framework-emitted. Adding a language must
NOT add a per-language metric or touch `telemetry/`. You add: (a) how small-tests
runs, and (b) optionally a Lambda runtime mapping for the construct.

## Steps

### 1. Gate + spec
- Adding a language is a framework feature → confirm a PRD covers it (or run `/prd`).
- If it introduces a non-obvious choice (e.g. a new test runner), note it in an ADR.

### 2. Add the small-tests toolchain mapping
In `packages/platform-framework/src/workflows/`, extend the `language` union and
the switch that selects the small-tests job:

| Language | Install + small-tests command (example) |
|---|---|
| python | `uv sync` → `uv run pytest` (+ Hypothesis PBT) |
| typescript | `pnpm install` → `pnpm test` (Vitest; fast-check for PBT) |
| go | `go mod download` → `go test ./...` (+ `testing/quick` or `gopter` for PBT) |
| clojure | `lein deps` → `lein test` (+ `test.check` for PBT) |

Each language MUST cover the three small-tests kinds the PR pipeline requires:
**unit · property-based · API-contract**.

### 3. Keep the telemetry step identical
The deploy jobs append the SAME `emitTelemetryStep` regardless of language. Do not
branch telemetry by language. A snapshot test must show the telemetry step present
for the new language too.

### 4. (Optional) construct runtime mapping
If services in this language run on Lambda, add the runtime to `GoldenService`
props (e.g. `provided.al2023` for Go/custom runtimes). Keep log retention + tags.

### 5. Tests
- Add a generator snapshot test for the new language (asserts the small-tests job
  + telemetry step).
- Run `make test`.

### 6. Docs
- Update the supported-languages note in `docs/consumption-guide.md`.
- Reference the PRD/ADR in the PR.

## Output

A PR that: extends the `language` union, adds the toolchain mapping, keeps
telemetry identical, adds a snapshot test, and updates the consumption guide.
Request a platform-team review (this touches a contract surface).

## Why

This is the inner-source path that lets a Go or Clojure team self-serve onto the
golden path without the platform team writing bespoke CI for them — and without
breaking DORA comparability, because the metric source never changes.
