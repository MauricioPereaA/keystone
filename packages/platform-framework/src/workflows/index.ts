/**
 * Type-safe GitHub Actions workflow generators (challenge "Option B").
 *
 * Teams do NOT hand-write workflows. They call these generators (directly, or
 * via `devex init`, which shells out to `generate.ts`) to emit the PR Pipeline
 * and Integration Pipeline. Compile-time validation via
 * `@github-actions-workflow-ts/lib` means a malformed pipeline fails at
 * generation, not at runtime in CI.
 *
 * Public surface:
 *   - generatePrPipeline / generateIntegrationPipeline — the two pipelines
 *   - workflowToYaml — serialize a generated workflow to YAML
 *   - LANGUAGE_TOOLCHAINS — per-language test toolchains (extended via the new-language runbook)
 *   - the step factories (emitTelemetryStep, …) for advanced composition
 */

export * from "./options.js";
export * from "./toolchains.js";
export * from "./steps.js";
export * from "./pr-pipeline.js";
export * from "./integration-pipeline.js";
export * from "./serialize.js";
