/**
 * PR Pipeline generator (the challenge's "Option B" shared artifact).
 *
 * Shape: small-tests (unit + property-based + api-contract) → deploy-sandbox.
 * Building it from typed `Workflow`/`NormalJob`/`Step` objects means a malformed
 * pipeline fails at compile time, not at runtime in CI.
 */
import { Workflow } from "@github-actions-workflow-ts/lib";
import type { PrPipelineOptions } from "./options.js";
export declare function generatePrPipeline(options: PrPipelineOptions): Workflow;
