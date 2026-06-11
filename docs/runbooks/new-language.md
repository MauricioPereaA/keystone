# Runbook — add a new application language to the golden path

Use this when a team's service is written in a language the framework's workflow
generator doesn't yet have a small-tests toolchain for (Go, Clojure, …). The key
principle: **you add a test-toolchain mapping, never a new metric** — DORA stays
comparable because the telemetry event is identical across languages (ADR-0002).

## Principle

The `DoraEvent` is language-agnostic and framework-emitted. Adding a language must
NOT add a per-language metric or touch `telemetry/`. You add: (a) how small-tests
runs for the new language, and (b) optionally a Lambda runtime mapping for the
construct.

## Steps

### 1. Gate + spec
- Adding a language is a framework feature → confirm a PRD covers it (scaffold
  from `docs/prd/00-template.md` if not).
- If it introduces a non-obvious choice (e.g. a new test runner), record it in an
  ADR (`docs/architecture/adr/0000-template.md`).

### 2. Add the small-tests toolchain mapping
In `packages/platform-framework/src/workflows/`, extend the `language` union and
the `LANGUAGE_TOOLCHAINS` mapping:

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
Request a maintainer review (this touches a contract surface).

## Why

This is the inner-source path that lets a Go or Clojure team self-serve onto the
golden path without the platform team writing bespoke CI for them — and without
breaking DORA comparability, because the metric source never changes.

---

## Worked example — adding Rust, end to end

Everything below is the **complete** PR. Note what it does *not* touch: `telemetry/`,
the deploy jobs, the conventions gate. The metric source never changes.

### 1. Extend the `Language` union (1 line)

```ts
// packages/platform-framework/src/workflows/options.ts
export type Language = "python" | "go" | "clojure" | "typescript" | "rust";
```

The compiler now does the navigation for you: `LANGUAGE_TOOLCHAINS` is typed
`Record<Language, Toolchain>`, so `tsc` **fails** until the map has a `rust`
entry — the type system enumerates exactly what a contributor must extend.
There is no call-site left to find by hand.

### 2. Add the toolchain entry (~15 lines)

```ts
// packages/platform-framework/src/workflows/toolchains.ts
rust: {
  label: "Rust",
  setup: () => [
    new Step({ name: "Set up Rust", uses: "dtolnay/rust-toolchain@stable" }),
    new Step({ name: "Fetch crates", run: "cargo fetch" }),
  ],
  smallTests: () => [
    // proptest provides the property-based half of the category
    new Step({ name: "Unit + property-based tests", run: "cargo test --all-features" }),
    new Step({ name: "API contract tests", run: "cargo test --test contract" }),
  ],
},
```

The three small-test categories (unit · property-based · API-contract) are the
comparability rule — every language answers the same question, "did small-tests
pass", with the same meaning.

### 3. Extend the snapshot test (1 line)

```ts
// packages/platform-framework/src/workflows/workflows.test.ts
expect(workflowToYaml(generatePrPipeline({ repo: "x", language: "rust" }))).toContain("cargo test");
```

The existing comparability guard — *"injects a telemetry step into EVERY deploy
job"* — runs unchanged and now covers Rust too, because the deploy job is shared,
not per-language.

### 4. What a Rust team now gets from `devex init my-svc --language rust`

```yaml
small-tests:
  steps:
    - name: Validate conventions & resolve Work ID (devex)   # unchanged — same gate as every team
    - name: Set up Rust
      uses: dtolnay/rust-toolchain@stable
    - name: Unit + property-based tests
      run: cargo test --all-features
    - name: API contract tests
      run: cargo test --test contract
deploy-sandbox:                                              # unchanged — OIDC deploy + DoraEvent
```

### 5. Close the loop

Add `rust` to the supported-languages note in `docs/consumption-guide.md`, run
`make test`, open the PR (Work ID in branch/commit/title; one maintainer review —
this touches a contract surface). Total diff: **~20 lines plus one test line.**
That is the platform-team-is-not-a-bottleneck claim, made concrete.
