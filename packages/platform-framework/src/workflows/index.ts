/**
 * Type-safe GitHub Actions workflow generators.
 *
 * Teams do NOT hand-write workflows. They call these generators (or run
 * `devex init`, which calls them) to emit the PR Pipeline and Integration
 * Pipeline. Compile-time validation via `github-actions-workflow-ts` means a
 * malformed pipeline fails at generation, not at runtime in CI.
 *
 * PoC scope: the PR Pipeline generator is the shared artifact (Option B of the
 * challenge). Implement against .kiro/specs/platform-framework/tasks.md.
 */

export interface PrPipelineOptions {
  /** Service repo name, stamped into emitted telemetry. */
  repo: string;
  /** App language — selects the small-tests toolchain (uv, go test, lein, vitest). */
  language: "python" | "go" | "clojure" | "typescript";
  environments?: Array<"sandbox" | "staging" | "production">;
}

/**
 * Produce the PR Pipeline workflow object (small-tests → deploy-sandbox).
 * TODO: build with NormalJob/Step from github-actions-workflow-ts and inject
 * the telemetry hook. Returns the workflow AST to be written as YAML.
 */
export function generatePrPipeline(_options: PrPipelineOptions): unknown {
  throw new Error("TODO: implement — see .kiro/specs/platform-framework/tasks.md");
}
