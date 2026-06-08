/**
 * Integration Pipeline generator (challenge bonus D).
 *
 * Shape: small-tests → deploy-staging → deploy-production → emit-metrics.
 * Fires on push to `main`. The final job computes the four DORA metrics from
 * the telemetry stream the deploy jobs just emitted.
 */

import { Workflow } from "@github-actions-workflow-ts/lib";
import { deployJob, metricsJob, smallTestsJob } from "./jobs.js";
import type { IntegrationPipelineOptions } from "./options.js";

export function generateIntegrationPipeline(options: IntegrationPipelineOptions): Workflow {
  const environments = options.environments ?? ["staging", "production"];
  const workflow = new Workflow("integration-pipeline", {
    name: "Integration Pipeline",
    on: { push: { branches: ["main"] } },
  });

  const tests = smallTestsJob(options.language);
  workflow.addJob(tests);

  let previous = tests;
  for (const env of environments) {
    const needs = previous === tests ? [tests] : [tests, previous];
    const deploy = deployJob(env, needs);
    workflow.addJob(deploy);
    previous = deploy;
  }

  // Metrics run after the last promotion; they need small-tests for the Work ID.
  workflow.addJob(metricsJob(previous === tests ? [tests] : [tests, previous]));

  return workflow;
}
