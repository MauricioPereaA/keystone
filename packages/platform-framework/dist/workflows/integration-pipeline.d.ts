/**
 * Integration Pipeline generator (challenge bonus D).
 *
 * Shape: small-tests → deploy-staging → deploy-production → emit-metrics.
 * Fires on push to `main`. The final job computes the four DORA metrics from
 * the telemetry stream the deploy jobs just emitted.
 */
import { Workflow } from "@github-actions-workflow-ts/lib";
import type { IntegrationPipelineOptions } from "./options.js";
export declare function generateIntegrationPipeline(options: IntegrationPipelineOptions): Workflow;
