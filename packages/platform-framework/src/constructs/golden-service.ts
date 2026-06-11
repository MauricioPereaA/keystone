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

import { RemovalPolicy, Tags } from "aws-cdk-lib";
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as logs from "aws-cdk-lib/aws-logs";
import { NagSuppressions } from "cdk-nag";
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
export const GOLDEN_SERVICE_DEFAULTS = {
  runtime: "python3.12" as GoldenServiceRuntime,
  handler: "index.handler",
  logRetentionDays: 30,
};

const RUNTIMES: Record<GoldenServiceRuntime, lambda.Runtime> = {
  "python3.12": lambda.Runtime.PYTHON_3_12,
  "nodejs22.x": lambda.Runtime.NODEJS_22_X,
  "nodejs24.x": lambda.Runtime.NODEJS_24_X,
  "provided.al2023": lambda.Runtime.PROVIDED_AL2023,
};

/** Default inline handler (python) — replaced by the consuming service's real code. */
const DEFAULT_HANDLER_SRC = [
  "def handler(event, context):",
  '    return {"statusCode": 200, "body": "keystone golden service"}',
].join("\n");

/** Map a day count to a valid CloudWatch RetentionDays, defaulting to ONE_MONTH. */
function toRetentionDays(days: number): logs.RetentionDays {
  const valid = Object.values(logs.RetentionDays).filter((v): v is number => typeof v === "number");
  return valid.includes(days) ? (days as logs.RetentionDays) : logs.RetentionDays.ONE_MONTH;
}

/**
 * A golden-path service: a Lambda behind a REST API Gateway, with retention-enforced
 * log groups (service, API access, telemetry) and standard cost-attribution tags.
 */
export class GoldenService extends Construct {
  /** The service Lambda. */
  readonly handler: lambda.Function;
  /** The REST API fronting the Lambda. */
  readonly api: apigateway.RestApi;
  /** The DORA/audit telemetry sink (NDJSON DoraEvent stream lands here). */
  readonly telemetryLogGroup: logs.LogGroup;

  constructor(scope: Construct, id: string, props: GoldenServiceProps) {
    super(scope, id);

    const runtime = props.runtime ?? GOLDEN_SERVICE_DEFAULTS.runtime;
    const retention = toRetentionDays(props.logRetentionDays ?? GOLDEN_SERVICE_DEFAULTS.logRetentionDays);

    // Telemetry / audit sink — the home for the framework-emitted DoraEvent stream.
    this.telemetryLogGroup = new logs.LogGroup(this, "Telemetry", {
      logGroupName: `/keystone/${props.serviceName}/dora`,
      retention,
      removalPolicy: RemovalPolicy.DESTROY,
    });

    // The Lambda's own log group, with enforced retention (Lambda's auto-created
    // group defaults to INFINITE retention — a silent cost leak we never allow).
    const handlerLogGroup = new logs.LogGroup(this, "HandlerLogs", {
      retention,
      removalPolicy: RemovalPolicy.DESTROY,
    });

    this.handler = new lambda.Function(this, "Handler", {
      runtime: RUNTIMES[runtime],
      handler: props.handler ?? GOLDEN_SERVICE_DEFAULTS.handler,
      code: props.code ?? lambda.Code.fromInline(DEFAULT_HANDLER_SRC),
      logGroup: handlerLogGroup,
    });

    // REST API (reference profile) with access + execution logging enabled.
    const apiAccessLogs = new logs.LogGroup(this, "ApiAccessLogs", {
      retention,
      removalPolicy: RemovalPolicy.DESTROY,
    });
    this.api = new apigateway.RestApi(this, "Api", {
      restApiName: `${props.serviceName}-${props.env}`,
      deployOptions: {
        accessLogDestination: new apigateway.LogGroupLogDestination(apiAccessLogs),
        accessLogFormat: apigateway.AccessLogFormat.jsonWithStandardFields(),
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        metricsEnabled: true,
      },
    });
    this.api.root.addProxy({
      anyMethod: true,
      defaultIntegration: new apigateway.LambdaIntegration(this.handler),
    });

    // Cost attribution + clean teardown (docs/engineering-rules/aws-cdk.md §9).
    Tags.of(this).add("project", "keystone");
    Tags.of(this).add("service", props.serviceName);
    Tags.of(this).add("env", props.env);

    this.applyNagSuppressions();
  }

  /**
   * Written suppressions for findings deliberately out of PoC scope, so the
   * construct ships cdk-nag clean and consumers inherit a passing baseline.
   * Each suppression names a reason (an unexplained suppression is a review blocker).
   */
  private applyNagSuppressions(): void {
    NagSuppressions.addResourceSuppressions(
      this,
      [
        {
          id: "AwsSolutions-IAM4",
          reason:
            "The Lambda execution role and the API Gateway CloudWatch role use the minimal AWS-managed " +
            "policies (basic execution / push-to-CloudWatch-logs); they are the least-privilege baseline.",
        },
        {
          id: "AwsSolutions-IAM5",
          reason:
            "Wildcards are confined to CloudWatch Logs stream ARNs under this service's log groups, " +
            "scoped by the managed logging policies.",
        },
        {
          id: "AwsSolutions-APIG2",
          reason:
            "Request validation is defined per-method by the consuming service's API model; the golden " +
            "path ships a proxy integration and does not impose a validation schema.",
        },
        {
          id: "AwsSolutions-APIG3",
          reason: "WAFv2 is out of PoC cost scope; production stacks attach a WebACL via a separate construct.",
        },
        {
          id: "AwsSolutions-APIG4",
          reason: "Authorization is service-specific; the golden path leaves authN/Z to the service's API definition.",
        },
        {
          id: "AwsSolutions-COG4",
          reason: "No Cognito user pool at PoC scale; authorization is the consuming service's responsibility (see APIG4).",
        },
        {
          id: "AwsSolutions-L1",
          reason: "Runtime is pinned to the org's supported tier (e.g. python3.12), upgraded deliberately, not automatically.",
        },
      ],
      true,
    );
  }
}
