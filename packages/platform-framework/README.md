# @keystone/platform

Reusable platform framework: type-safe GitHub Actions workflow generators, AWS CDK constructs, and the DORA telemetry contract. TypeScript, packaged with `pnpm`, installable directly from Git.

## Install (from Git, no registry)

```bash
pnpm add "github:MauricioPereaA/keystone#path:/packages/platform-framework"
# pin a tag + path (works for forks too):
pnpm add "MauricioPereaA/keystone#v0.1.0&path:/packages/platform-framework"
```

> Subdirectory install via `#path:` requires pnpm ≥ 9.

## Usage

```ts
import { buildEvent, serializeEvent } from "@keystone/platform/telemetry";
import { generatePrPipeline } from "@keystone/platform/workflows";
import { GOLDEN_SERVICE_DEFAULTS } from "@keystone/platform/constructs";

const event = buildEvent({
  event: "deployment.succeeded",
  workId: "FIN-123", actor: "ci", repo: "transactionify",
  env: "production", commitSha: "abc123", commitTime: "2026-06-08T10:00:00Z",
});
console.log(serializeEvent(event)); // one NDJSON line → the DORA collector
```

## Develop

```bash
pnpm install
pnpm test          # vitest — telemetry contract tests
pnpm lint          # tsc --noEmit
pnpm build         # emit dist/
```

The telemetry event shape is the **single language-agnostic source** that makes DORA metrics comparable across Python/Go/Clojure/TS teams. See ADR-0002. Implement the workflow + construct generators against `.kiro/specs/platform-framework/tasks.md`.
