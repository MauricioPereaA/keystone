# Keystone conventions (Amazon Q review rules)

Distilled from the canonical `docs/engineering-rules/` so Amazon Q reviews PRs against the
SAME conventions the CLI and CI enforce. Flag any PR that violates:

- **Work ID everywhere.** Every branch, commit subject, and PR title carries a Work
  ID matching `^[A-Z]{2,5}-\d+$` (e.g. `FIN-123`). Commit/PR-title shape is a
  conventional commit with the Work ID in the subject: `<type>(<scope>)?: <WORK-ID> <subject>`.
  Source: `conventions/conventions.json`, `docs/engineering-rules/commit-and-pr.md`.
- **Single source of truth.** Convention patterns (Work ID / branch / commit / PR /
  telemetry vocabulary) are defined ONCE in `conventions/conventions.json`. Never
  hard-code a regex/pattern in Python, TypeScript, or workflow YAML — read it from
  conventions (CLI) or mirror it via the typed telemetry contract (framework).
  Source: `docs/engineering-rules/boundaries.md` §1, `magic-values.md`.
- **Self-contained CLI.** `packages/devex-cli` declares no dependency on the
  framework (distribution invariant — ADR-0001). Flag any cross-package import.
- **One language-agnostic metric source.** DORA metrics derive from the single
  `DoraEvent` stream (ADR-0002), never per-language instrumentation.
- **PRD-first.** New features/behaviour need an approved PRD (`docs/prd/`); flag
  feature code that introduces user-visible behaviour with no referenced PRD.
