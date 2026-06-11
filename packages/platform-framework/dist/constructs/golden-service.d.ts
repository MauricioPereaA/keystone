/**
 * GoldenService — the reusable AWS CDK construct (challenge "Option A").
 *
 * Encodes the org's infrastructure conventions so a team consumes ONE construct
 * instead of re-wiring Lambda + API Gateway + logging by hand. It also provisions
 * the telemetry sink (a log group with ENFORCED retention) where generated deploy
 * workflows ship the DoraEvent stream — so DORA/audit data has a home.
 *
 * Cost guardrails are structural, not optional (see docs/engineering-rules/aws-cdk.md):
 *   - every log group has explicit retention (never the infinite default),
 *   - RemovalPolicy.DESTROY so `cdk destroy` actually cleans PoC stacks,
 *   - standard tags (project/service/env) for cost attribution + teardown,
 *   - no VPC / NAT gateway.
 *
 * The construct ships cdk-nag (AwsSolutionsChecks) clean: it enables API access +
 * execution logging, and carries written NagSuppressions for the findings that
 * are deliberately out of PoC scope (WAF, per-method auth/validation). Consuming
 * teams therefore inherit a passing security/cost baseline.
 */
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as logs from "aws-cdk-lib/aws-logs";
import { Construct } from "constructs";
import type { Environment } from "../telemetry/index.js";
/**
 * Lambda runtimes the golden path supports (AWS-supported, non-EOL tiers).
 * nodejs24.x is the latest Active-LTS Lambda runtime (use async/return handlers —
 * it drops the legacy callback handler signature); nodejs22.x stays available for
 * services that still rely on callback-style handlers.
 */
export type GoldenServiceRuntime = "python3.12" | "nodejs22.x" | "nodejs24.x" | "provided.al2023";
export interface GoldenServiceProps {
    /** Service name — used for resource names, the telemetry log group, and the `service` tag. */
    serviceName: string;
    /** Deployment environment — stamped as the `env` tag (sandbox | staging | production). */
    env: Environment;
    /** Lambda runtime. Defaults to python3.12. */
    runtime?: GoldenServiceRuntime;
    /** Lambda handler entrypoint. Defaults to "index.handler". */
    handler?: string;
    /** Lambda code. Defaults to a tiny inline handler so the construct is demoable/testable. */
    code?: lambda.Code;
    /** CloudWatch Logs retention in days — REQUIRED guardrail; defaults to 30 (ONE_MONTH). */
    logRetentionDays?: number;
}
/** Documented defaults — referenced in docs + tests. */
export declare const GOLDEN_SERVICE_DEFAULTS: {
    runtime: GoldenServiceRuntime;
    handler: string;
    logRetentionDays: number;
};
/**
 * A golden-path service: a Lambda behind a REST API Gateway, with retention-enforced
 * log groups (service, API access, telemetry) and standard cost-attribution tags.
 */
export declare class GoldenService extends Construct {
    /** The service Lambda. */
    readonly handler: lambda.Function;
    /** The REST API fronting the Lambda. */
    readonly api: apigateway.RestApi;
    /** The DORA/audit telemetry sink (NDJSON DoraEvent stream lands here). */
    readonly telemetryLogGroup: logs.LogGroup;
    constructor(scope: Construct, id: string, props: GoldenServiceProps);
    /**
     * Written suppressions for findings deliberately out of PoC scope, so the
     * construct ships cdk-nag clean and consumers inherit a passing baseline.
     * Each suppression names a reason (an unexplained suppression is a review blocker).
     */
    private applyNagSuppressions;
}
