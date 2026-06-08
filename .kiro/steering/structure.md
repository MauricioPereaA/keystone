# Structure Steering — Keystone

## Monorepo layout

```
keystone/
├── .kiro/steering/            # this context (product, tech, structure, conventions)
├── .kiro/specs/<feature>/     # requirements.md · design.md · tasks.md
├── conventions/conventions.json   # single source of truth
├── packages/devex-cli/        # Python CLI — self-contained, uv
│   └── src/devex/{cli,validators,conventions}.py · _data/conventions.json · tests/
├── packages/platform-framework/   # TS framework — pnpm
│   └── src/{telemetry,workflows,constructs}/ · *.test.ts
├── docs/{prd,architecture/adr,runbooks}/ · consumption-guide.md · contributing.md
└── .github/workflows/         # dogfooded pipelines
```

## Boundaries

- **`conventions/` is upstream of everything.** CLI and framework both read it; nothing writes it but humans.
- **The CLI never imports the framework and vice-versa.** They integrate only through `conventions.json` and the telemetry event schema (a documented contract), not through code.
- **`packages/devex-cli` declares no cross-package deps** (distribution invariant — ADR-0001).
- **Public surface only:** the framework exposes `telemetry`, `workflows`, `constructs` via `src/index.ts`. The CLI exposes the `devex` console script.

## Where things go

| Need | Location |
|---|---|
| A new convention (branch/commit/PR/Work ID rule) | `conventions/conventions.json` (then both consumers pick it up) |
| A new CLI command | `packages/devex-cli/src/devex/cli.py` + validator/helper module |
| A new shared pipeline stage | `packages/platform-framework/src/workflows/` |
| A new CDK pattern | `packages/platform-framework/src/constructs/` |
| A telemetry/DORA change | `packages/platform-framework/src/telemetry/` (bump schemaVersion) |
| A spec for new work | `.kiro/specs/<feature>/` + a PRD in `docs/prd/` |
| An architectural decision | `docs/architecture/adr/NNNN-*.md` |
