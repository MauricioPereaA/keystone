/**
 * Shared step factories used by both pipeline generators.
 *
 * The single most important one is {@link emitTelemetryStep}: because the
 * FRAMEWORK (not the application) emits the DoraEvent, every generated deploy
 * job ships the identical event shape regardless of language. That is the
 * structural guarantee behind DORA comparability (ADR-0002). Convention
 * validation and Work ID resolution are delegated to the `devex` CLI so the
 * regex lives in exactly one place (`conventions.json`), never in this YAML.
 */
import { Step } from "@github-actions-workflow-ts/lib";
import { type DeploymentEvent, type Environment } from "../telemetry/index.js";
/** GHA expression for the Work ID resolved by the small-tests job. */
export declare const WORK_ID_EXPR: string;
export declare function checkoutStep(): Step;
export declare function setupUvStep(): Step;
/**
 * Validate branch + commit against `conventions.json` AND publish the Work ID
 * as a step output — both via the `devex` CLI, so CI enforces the exact same
 * rules the developer ran locally (shift-left parity, single source of truth).
 */
export declare function standardsCheckStep(): Step;
/**
 * Node setup for the CDK deploy (the infra app is TypeScript regardless of the
 * service's language). The consumer owns the CDK app, so we must NOT assume one
 * package manager: detect it from the committed lockfile and fall back to npm,
 * which is always on the runner. corepack ships the pnpm/yarn shims with Node, so
 * no extra setup action is needed — a hard `pnpm/action-setup` step broke every
 * npm/yarn service (it failed before a single resource was deployed).
 */
export declare function cdkSetupSteps(): Step[];
/**
 * Authenticate to AWS via GitHub OIDC — never static keys (security.md §4).
 * The role ARN and region are non-sensitive repo Variables, not Secrets.
 */
export declare function configureAwsCredentialsStep(): Step;
export declare function cdkDeployStep(env: Environment): Step;
/**
 * Emit one NDJSON {@link DoraEvent} for a deploy stage. Built with `jq` from the
 * GitHub Actions context so it is language-agnostic; the schema version is
 * sourced from the telemetry contract (not hard-coded). IDs only — no secrets
 * or PII (audit-logging.md §7).
 */
export declare function emitTelemetryStep(input: {
    event: DeploymentEvent;
    env: Environment;
    /** GHA expression yielding the Work ID. Defaults to the small-tests output. */
    workIdExpr?: string;
    /** Optional step condition, e.g. "success()" / "failure()". */
    if?: string;
}): Step;
/** Report the four DORA metrics from the telemetry stream (integration pipeline tail). */
export declare function doraReportStep(): Step;
