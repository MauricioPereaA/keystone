# Logging discipline & error tracking

**Scope:** Both (split). The bans apply to everyone.

**See also:** [`error-handling.md`](error-handling.md), [`security.md`](security.md), [`audit-logging.md`](audit-logging.md).

## When this rule applies

Any code that runs outside tests. In other words: always, except inside `tests/` / `*.test.ts`.

## The rule

### A. Hard bans

| Stack | Banned | Use instead |
|---|---|---|
| CLI (Python) | `print(...)` for diagnostics, `pdb`/`breakpoint()` | structured logger; Rich `console` for *intended user output* only |
| CLI | `logging.basicConfig` ad-hoc | the project logger helper |
| Framework (TS) | `console.log/debug/info` for diagnostics | a thin `logger` wrapper |
| Both | committed `debugger;` / `breakpoint()` | a local breakpoint, never committed |

Narrow exception: the CLI legitimately writes **user-facing output** (a `standards-check` ✓/✗ table, a `dora` report) via Rich — that's product output, not a diagnostic log. Keep the two separate.

### B. Every caught error emits a structured event

1. A `catch`/`except` that doesn't re-raise MUST log. To intentionally ignore, log at `warning` with the reason.
2. **Levels:** `debug` (rare), `info` (state transitions worth tracking), `warning` (recoverable anomaly), `error` (operation failed, user impact), `critical` (data/contract integrity at risk).
3. **Event names are dotted, lowercase** `<noun>.<verb>` / `<noun>.<state>` — same convention as the telemetry events (`conventions.invalid`, `git.checkout_failed`, `workflow.generated`).
4. **Attach context as key=value, never f-string the message:** `log.error("git.failed", cmd=cmd, code=rc)` — not `log.error(f"git {cmd} failed {rc}")`.
5. **Include enough to debug without re-running:** what op, which repo/branch, what failed, a correlation handle.

### C. Sensitive data never reaches a log

6. Never log credentials, tokens, full file contents, or PII. IDs only (`actor` principal, `workId`, `repo`).
7. The telemetry `DoraEvent` follows the same rule — it's a log that ships to a collector (`audit-logging.md`).

### D. No diagnostic leftovers

8. No commented-out log calls. No "TODO: remove this log" without a ticket id.
9. Log because you'd want it during an incident, not "just in case" — noise hides signal and costs CloudWatch ingest.

## Why

`print`/`console.log` bypass structure entirely: no level, no event name, no correlation, nothing to grep across runs. A swallowed error two weeks ago is half of every "it used to work". And a credential in CloudWatch is a compliance incident — IDs-only is the durable defense.

## Examples

### Good
```python
log.warning("git.detached_head", branch="HEAD")          # named, structured
console.print("[red]✗[/] branch invalid: 'foo'")           # intended user output
```

### Bad
```python
print(f"checking {branch} with token {token}")             # ✗ print + secret + f-string
```
