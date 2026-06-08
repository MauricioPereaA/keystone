# Rules Index

Map a task to the rule that covers it. Each rule declares its **scope**; if it doesn't match what you're touching, skip it.

| Task | File | Scope |
|---|---|---|
| **About to add or change a feature** | [prd-driven-development.md](prd-driven-development.md) | **Repo-wide (gate)** |
| Hard rules that always apply | [boundaries.md](boundaries.md) | Repo-wide |
| Understand package/folder boundaries | [architecture.md](architecture.md) | Repo-wide |
| About to duplicate code / a convention | [dry-principles.md](dry-principles.md) | Both |
| Use a literal pattern / status / magic value | [magic-values.md](magic-values.md) | Both |
| Write a commit / open a PR | [commit-and-pr.md](commit-and-pr.md) | Repo-wide |
| About to `git push` or merge to `main` | [no-direct-push-to-main.md](no-direct-push-to-main.md) | Repo-wide |
| Cut a release / version a package | [releasing.md](releasing.md) | Repo-wide |
| Write tests (CLI or framework) | [testing-conventions.md](testing-conventions.md) | Both (split) |
| Catch an error / log an event | [error-handling.md](error-handling.md) | Both (split) |
| Log discipline — no `print`/`console.*`, every error tracked | [logging-discipline.md](logging-discipline.md) | Both (split) |
| Add / change an environment variable | [environment-variables.md](environment-variables.md) | Both |
| Anything touching secrets, auth, or input validation | [security.md](security.md) | Both (split) |
| Emit or change a DORA / audit telemetry event | [audit-logging.md](audit-logging.md) | Framework |
| Write CDK / generate a deploy workflow / touch AWS | [aws-cdk.md](aws-cdk.md) | Infra |
| Verify against SOC 2 controls | [soc2.md](soc2.md) | Repo-wide |

## Scope legend

- **CLI** — applies inside `packages/devex-cli/` (Python).
- **Framework** — applies inside `packages/platform-framework/` (TypeScript).
- **Infra** — CDK constructs + generated deploy workflows (AWS).
- **Both (split)** — separate sections per package; follow the one that matches.
- **Both** — same process in both packages.
- **Repo-wide** — applies to any change.

## Reading order on first contact

1. `CLAUDE.md` (root) — project overview + invariants.
2. `prd-driven-development.md` — the gate before code.
3. `boundaries.md` — constraints that never bend.
4. `architecture.md` — the mental model (monorepo + conventions).
5. `dry-principles.md` — the mindset.
6. Then the task-specific rule when you pick up work.

## Rule structure

Each file has five parts: **Scope · When this rule applies · The rule · Why · Examples.** Don't add a rule without all five.
