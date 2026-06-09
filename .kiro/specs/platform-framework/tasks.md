# Tasks — @keystone/platform

> `[x]` = scaffolded/working in the PoC. `[ ]` = to implement. Each maps to a requirement.

- [x] 1. Package config: `package.json` (ESM, subpath exports, pnpm), `tsconfig.json`. (R5)
- [x] 2. Telemetry contract: `DoraEvent` type, `buildEvent`, `serializeEvent`, `SCHEMA_VERSION`. (R3)
- [x] 3. Telemetry tests (Vitest): schema stamp, four W's, NDJSON single-line. (NFR)
- [x] 4. Public surface barrel `index.ts` + clean `tsc --noEmit`. (R5)
- [x] 5. Stubs for `generatePrPipeline` (workflows) and `GoldenService` defaults (constructs). (R1, R2)
- [x] 6. Implement `generatePrPipeline` with `@github-actions-workflow-ts/lib`; inject `emitTelemetryStep`. (R1)
- [x] 7. Per-language small-tests selection (python/go/clojure/typescript). (R1)
- [x] 8. `generate:workflows` CLI entry (`tsx src/workflows/generate.ts`) → write YAML. (R1)
- [x] 9. Implement `GoldenService` construct (Lambda + REST API GW + retention-enforced LogGroup + tags + cdk-nag clean). (R2)
- [x] 10. CDK assertion tests (`Template.fromStack`) + cdk-nag-clean assertion. (NFR)
- [x] 11. Workflow snapshot tests asserting telemetry step present in every deploy job. (R1, R3)
- [x] 12. `generateIntegrationPipeline` (staging→production→emit-metrics). (R4, bonus)
- [x] 13. `pnpm build` → `dist/` with `.d.ts`. (R5) — consumer Git-install verification pending (Phase 3).
