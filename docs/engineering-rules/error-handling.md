# Error handling

**Scope:** Both (split — CLI Python / Framework TS).

**See also:** [`logging-discipline.md`](logging-discipline.md), [`security.md`](security.md).

## When this rule applies

You're catching an exception, shelling out to git, generating a workflow, or doing anything that can fail.

## The rule

### CLI (Python)

1. **Never swallow silently.** A bare `except: pass` is banned. To ignore a specific failure, name it and log a `warning` with the reason.
2. **Fail fast with a clear, actionable message.** A failed validation prints the rule + an example and exits non-zero (so hooks and CI block). No stack traces to the user; detail only with `--verbose`.
3. **Validate `conventions.json` on load** (Pydantic). A malformed source-of-truth is a hard error, not a silent fallback.
4. **Isolate subprocess failures.** Wrap git calls; a non-zero git exit becomes a typed, logged error, not an unhandled `CalledProcessError`.
5. **Exit codes are the contract:** `0` pass, `1` validation failure, `2` usage/config error. Hooks and CI depend on these.

### Framework (TypeScript)

6. **Generators fail at build, not at runtime.** A malformed workflow/construct should be a compile-time type error or an explicit `throw` during generation — never emit invalid YAML/CDK.
7. **Throw `Error` with context, don't return `null`.** Callers (the CLI's `init`, CI) need to know what failed and why.
8. **Telemetry emission must not crash a deploy.** If the collector write fails, log the failure and continue — a deploy succeeding but its event being lost is recoverable; blocking the deploy on telemetry is not.

### Both

9. **Every caught error emits a structured log event** (`logging-discipline.md`). Catch-and-log-and-rethrow is one place, not three.
10. **Errors never leak secrets** (tokens, role ARNs are ok; credentials are not).

## Why

A swallowed exception in a CLI that gates commits is a future "it said it passed but CI failed". A generator that emits invalid-but-not-crashing YAML pushes the failure all the way to CI runtime, defeating the compile-time-validation premise of the framework.

## Examples

### Good — CLI
```python
try:
    conv = load_conventions()
except (FileNotFoundError, ValidationError) as exc:
    log.error("conventions.invalid", error=str(exc))
    raise typer.Exit(code=2)
```

### Good — framework
```ts
if (!options.repo) throw new Error("generatePrPipeline: 'repo' is required (stamped into telemetry)");
```

### Bad
```python
# ✗ silent — the CLI says nothing, the hook passes, CI later fails
try: run_checks()
except Exception: pass
```
