/**
 * Job factories shared by the PR and Integration pipeline generators.
 *
 * The deploy job is where the comparability guarantee is enforced: every deploy
 * stage, for every language, gets the same telemetry steps and the same OIDC
 * auth — by construction, not by convention.
 */
import { NormalJob } from "@github-actions-workflow-ts/lib";
import type { Environment } from "../telemetry/index.js";
import type { Language } from "./options.js";
import { type ToolchainContext } from "./toolchains.js";
/** small-tests: validate conventions (devex) + the language's unit/PBT/contract suite. */
export declare function smallTestsJob(language: Language, ctx?: ToolchainContext): NormalJob;
/**
 * A deploy stage: OIDC auth, then `started → cdk deploy → succeeded/failed`,
 * each wrapped in a framework-emitted telemetry step.
 */
export declare function deployJob(env: Environment, needs: NormalJob[]): NormalJob;
/** Tail job of the integration pipeline: compute the four DORA metrics from the stream. */
export declare function metricsJob(needs: NormalJob[]): NormalJob;
