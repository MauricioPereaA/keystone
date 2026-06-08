/**
 * Job factories shared by the PR and Integration pipeline generators.
 *
 * The deploy job is where the comparability guarantee is enforced: every deploy
 * stage, for every language, gets the same telemetry steps and the same OIDC
 * auth — by construction, not by convention.
 */

import { NormalJob, expressions } from "@github-actions-workflow-ts/lib";
import type { Environment } from "../telemetry/index.js";
import type { Language } from "./options.js";
import { LANGUAGE_TOOLCHAINS } from "./toolchains.js";
import {
  cdkDeployStep,
  cdkSetupSteps,
  checkoutStep,
  configureAwsCredentialsStep,
  doraReportStep,
  emitTelemetryStep,
  setupUvStep,
  standardsCheckStep,
} from "./steps.js";

/** small-tests: validate conventions (devex) + the language's unit/PBT/contract suite. */
export function smallTestsJob(language: Language): NormalJob {
  const toolchain = LANGUAGE_TOOLCHAINS[language];
  const job = new NormalJob("small-tests", {
    "runs-on": "ubuntu-latest",
    permissions: { contents: "read" },
    // Publish the Work ID so downstream deploy jobs can stamp it into telemetry.
    outputs: { work_id: expressions.expn("steps.standards.outputs.work_id") },
  });
  job.addSteps([checkoutStep(), setupUvStep(), standardsCheckStep(), ...toolchain.setup(), ...toolchain.smallTests()]);
  return job;
}

/**
 * A deploy stage: OIDC auth, then `started → cdk deploy → succeeded/failed`,
 * each wrapped in a framework-emitted telemetry step.
 */
export function deployJob(env: Environment, needs: NormalJob[]): NormalJob {
  const job = new NormalJob(`deploy-${env}`, {
    "runs-on": "ubuntu-latest",
    environment: env,
    // OIDC mints a token (id-token: write); checkout reads the repo (contents: read).
    permissions: { "id-token": "write", contents: "read" },
  });
  job.needs(needs);
  job.addSteps([
    checkoutStep(),
    ...cdkSetupSteps(),
    configureAwsCredentialsStep(),
    emitTelemetryStep({ event: "deployment.started", env }),
    cdkDeployStep(env),
    emitTelemetryStep({ event: "deployment.succeeded", env, if: "success()" }),
    emitTelemetryStep({ event: "deployment.failed", env, if: "failure()" }),
  ]);
  return job;
}

/** Tail job of the integration pipeline: compute the four DORA metrics from the stream. */
export function metricsJob(needs: NormalJob[]): NormalJob {
  const job = new NormalJob("emit-metrics", {
    "runs-on": "ubuntu-latest",
    permissions: { contents: "read" },
  });
  job.needs(needs);
  job.addSteps([checkoutStep(), setupUvStep(), doraReportStep()]);
  return job;
}
