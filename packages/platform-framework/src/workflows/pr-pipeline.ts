/**
 * PR Pipeline generator (the challenge's "Option B" shared artifact).
 *
 * Shape: small-tests (unit + property-based + api-contract) → deploy-sandbox.
 * Building it from typed `Workflow`/`NormalJob`/`Step` objects means a malformed
 * pipeline fails at compile time, not at runtime in CI.
 */

import { Workflow } from "@github-actions-workflow-ts/lib";
import { deployJob, smallTestsJob } from "./jobs.js";
import type { PrPipelineOptions } from "./options.js";

export function generatePrPipeline(options: PrPipelineOptions): Workflow {
  const environments = options.environments ?? ["sandbox"];
  const workflow = new Workflow("pr-pipeline", {
    name: "PR Pipeline",
    on: { pull_request: { types: ["opened", "synchronize", "reopened"] } },
  });

  const tests = smallTestsJob(options.language);
  workflow.addJob(tests);

  let previous = tests;
  for (const env of environments) {
    // Every deploy needs small-tests (for the Work ID output) plus the prior stage (ordering).
    const needs = previous === tests ? [tests] : [tests, previous];
    const deploy = deployJob(env, needs);
    workflow.addJob(deploy);
    previous = deploy;
  }

  return workflow;
}
