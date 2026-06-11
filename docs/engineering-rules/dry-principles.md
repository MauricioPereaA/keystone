# DRY Principles

**Scope:** Both (cross-cutting).

## When this rule applies

You're about to copy-paste code, write a second helper similar to an existing one, or re-implement a convention/telemetry/validation pattern by hand.

## The rule

1. **Check for an existing helper first.** Common ones here:
   - `devex.conventions.load_conventions()` — the shared source of truth (CLI).
   - `devex.validators.*` — branch/commit/PR validation (CLI).
   - `@keystone/platform/telemetry::buildEvent / serializeEvent` — the event contract (framework).
   - `@keystone/platform/workflows` generators — don't hand-write a workflow.
2. **The biggest DRY win is `conventions.json`.** A convention lives there once and is consumed by both packages. Re-typing a pattern in code is the anti-pattern this whole project exists to prevent.
3. **Factor out only with two real uses** — not "might be useful later". Premature abstraction costs more than duplication.
4. **Prefer composition/pure functions over inheritance.**

## Anti-DRY (duplicate on purpose)

- **Test arrangements** — factories/fixtures are shared; the *arrangement* of each test is written out for readability.
- **CLI (Python) and framework (TS) types** — they're separate languages; the shared contract is `conventions.json` + the documented event schema, not hand-synced type files. (Generating one from the other is a future improvement; don't hand-sync piecemeal.)

## Why

*Repeated* duplication of a known-correct pattern (the Work ID regex, the event shape) invites subtle bugs when one copy drifts. But premature shared abstractions across two languages create coupling that breaks the independent-distribution invariant (ADR-0001). The rule: reuse the shared source where it exists; duplicate once across language boundaries; extract within a language when you have evidence of a pattern.

## Examples

### Good — reuse the source of truth
```python
pattern = load_conventions()["commit"]["pattern"]
```

### Bad — reinvented in two places
```python
# ✗ now the CLI and the generated workflow can disagree on what a valid commit is
COMMIT_RE = r"^(feat|fix)(\(.+\))?: [A-Z]+-\d+ .+"
```
