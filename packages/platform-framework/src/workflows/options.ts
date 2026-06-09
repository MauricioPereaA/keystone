/**
 * Public option types for the workflow generators.
 *
 * The environment vocabulary is sourced from the telemetry contract's
 * `Environment` union (single source of truth for env names — see ADR-0002),
 * never re-typed here.
 */

import type { Environment } from "../telemetry/index.js";

/** Application languages the golden path supports today. */
export type Language = "python" | "go" | "clojure" | "typescript";

/** Options for {@link generatePrPipeline}. */
export interface PrPipelineOptions {
  /** Service repo (`owner/name`), stamped into emitted telemetry. */
  repo: string;
  /** App language — selects the small-tests toolchain (uv / go / lein / pnpm). */
  language: Language;
  /**
   * Environments the PR pipeline deploys to, in order.
   * Defaults to `["sandbox"]` (the challenge's PR-pipeline contract).
   */
  environments?: Environment[];
  /**
   * Path to the service's OpenAPI spec, used by the API-contract step.
   * When omitted, the generated step auto-detects `openapi.yaml|yml|json` at
   * the repo root at runtime. Set it (via `keystone.json` `apiSpec`) for
   * services that keep the spec elsewhere. Currently honored by the python
   * toolchain (OpenAPI schema validation); the other toolchains delegate the
   * contract step to a project script and ignore this option.
   */
  apiSpec?: string;
}

/** Options for {@link generateIntegrationPipeline}. */
export interface IntegrationPipelineOptions {
  /** Service repo (`owner/name`), stamped into emitted telemetry. */
  repo: string;
  /** App language — selects the small-tests toolchain. */
  language: Language;
  /**
   * Promotion targets, in order. Defaults to `["staging", "production"]`.
   * A final `emit-metrics` job always runs after the last deploy.
   */
  environments?: Environment[];
  /**
   * Path to the service's OpenAPI spec, used by the API-contract step.
   * When omitted, the generated step auto-detects `openapi.yaml|yml|json` at
   * the repo root at runtime. Set it (via `keystone.json` `apiSpec`) for
   * services that keep the spec elsewhere. Currently honored by the python
   * toolchain (OpenAPI schema validation); the other toolchains delegate the
   * contract step to a project script and ignore this option.
   */
  apiSpec?: string;
}
