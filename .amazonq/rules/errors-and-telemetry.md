# Errors, logging & telemetry (Amazon Q review rules)

Distilled from `docs/engineering-rules/error-handling.md`, `logging-discipline.md`,
`audit-logging.md`. Flag any PR that:

- **Swallows errors silently.** No bare `except: pass` / empty `catch`. Every caught
  error logs a structured event (dotted `noun.verb` name + key=value context) or
  re-raises. Use the structured logger — never `print()` (CLI) or `console.log`
  (framework) for diagnostics. Rich `console` is for intended user output only.
- **Hides failures from the user.** CLI fails fast with an actionable message and
  the right exit code (0 ok / 1 validation / 2 config) — no raw stack traces to the
  user; malformed telemetry lines are skipped, not fatal.
- **Forks the telemetry shape.** Deploy stages emit the one `DoraEvent` from
  `@keystone/platform/telemetry`, carrying the four W's (actor / repo+env /
  timestamp / workId). Schema changes are additive within a major `schemaVersion`;
  a breaking change needs an ADR. The same event row is the SOC 2 audit record.
