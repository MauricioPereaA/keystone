# No magic numbers / magic strings

**Scope:** Both.

## When this rule applies

You're about to type a literal that has *meaning beyond its value* — a Work ID pattern, branch/commit regex, event name, environment name, exit code, retention period, page size.

## The rule

1. **Conventions come from `conventions.json` — the canonical source.** Never inline a Work ID/branch/commit/PR pattern in Python or TypeScript. Load it (`devex.conventions.load_conventions()` / read the bundled JSON). One definition, both consumers, zero drift.
2. **Telemetry vocabulary is a typed union**, not loose strings. The `DeploymentEvent` / `Environment` types in `@keystone/platform/telemetry` are the source; the CLI mirrors the allowed values from `conventions.json` (`telemetry.events`).
3. **Exit codes are named, not magic** (`0` pass / `1` validation / `2` config) — define them once in the CLI.
4. **Infra constants** (log retention days, env names `sandbox|staging|production`) come from one place — `conventions.json` `pipelines.environments` + the CDK construct defaults — never re-typed per construct.
5. **A literal is OK only if it's clearly named and isolated** (e.g. the default page size constant), with a one-line comment.

## Why

Rename "production" → "prod" in one place and three other call-sites still use the old string with no compile error. Centralizing gives grep-ability, one source of truth, and a type-checker that catches the typo. For this project specifically, a convention pattern duplicated in code is the single most likely cause of "passes locally, fails CI".

## Examples

### Good
```python
EVENTS = load_conventions()["telemetry"]["events"]   # from the source of truth
```
```ts
export type Environment = "sandbox" | "staging" | "production";  // typed, single definition
```

### Bad
```python
# ✗ pattern duplicated in code; drifts from conventions.json and from the framework
if re.match(r"^[A-Z]{2,5}-\d+$", work_id): ...
```
```ts
// ✗ stringly-typed env; a typo compiles and ships
if (env === "prod") deploy();   // should be a typed union value
```
