# Architecture

**Scope:** Repo-wide (monorepo). Sections call out CLI vs Framework.

## When this rule applies

You're adding a file, deciding where something lives, or importing across a boundary.

## The rule

### Monorepo layering

```
conventions/conventions.json     ← single source of truth (upstream of everything)
        │ read by
        ├── packages/devex-cli/          (Python) — bundles a synced copy as package data
        └── packages/platform-framework/ (TypeScript) — reads it to generate workflows
```

- **`conventions/` is upstream of both packages.** Humans edit it; code only reads it. A convention (Work ID, branch/commit/PR pattern, telemetry schema) is defined **once** here.
- **The CLI and the framework never import each other.** They integrate only through (a) `conventions.json` and (b) the documented telemetry event schema. No code dependency in either direction.
- **`devex-cli` declares no cross-package / workspace dependency** (distribution invariant — ADR-0001). The conventions file is bundled into the wheel via Hatch `force-include`, synced by `make sync-conventions`.

### CLI internal layering (`packages/devex-cli/src/devex/`)

```
cli.py         ← command surface (Typer). Thin: parse args, call logic, render.
  └── validators.py / <feature>.py   ← pure logic, no I/O where possible
        └── conventions.py            ← loads bundled conventions.json (cached)
```

- Commands are thin; logic lives in pure, testable modules. Git/subprocess I/O is isolated in one helper so validators stay I/O-free.
- No regex or convention pattern is hard-coded in Python — it comes from `conventions.json`.

### Framework internal layering (`packages/platform-framework/src/`)

```
index.ts        ← public surface (barrel)
├── telemetry/   ← the DoraEvent contract (no deps on the others)
├── workflows/   ← generators (github-actions-workflow-ts); may use telemetry
└── constructs/  ← CDK constructs; may use telemetry
```

- Public surface is the three subpath exports (`@keystone/platform/{telemetry,workflows,constructs}`) + the barrel. Nothing else is reachable by consumers.
- `telemetry/` is the most-depended-on module and depends on nothing internal — keep it that way.

### Config / env

- Only the documented config entrypoints read the environment (see `environment-variables.md`). Everything else receives config as arguments.

## Why

Boundaries keep changes local. The single most important one — `conventions.json` upstream of both packages — is what guarantees local validation and CI enforcement never drift. The "CLI and framework don't import each other" rule is what lets each be versioned and Git-installed independently (ADR-0001).

## Examples

### Good
```python
# devex/validators.py — reads the shared source, no hard-coded pattern
from devex.conventions import load_conventions
pattern = load_conventions()["branch"]["pattern"]
```

### Bad
```python
# ✗ hard-coded convention; drifts from conventions.json and from CI
if not re.match(r"^(feature|fix)/[A-Z]+-\d+", branch): ...
```

### Bad
```ts
// ✗ the framework importing the CLI (or vice-versa) — breaks independent distribution
import { validateBranch } from "../../devex-cli/...";
```
