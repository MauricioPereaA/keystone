/**
 * Reusable AWS CDK constructs (Option A of the challenge).
 *
 * Encodes the org's infrastructure conventions so teams consume a construct
 * instead of reinventing Lambda + API Gateway wiring. The construct also
 * provisions the telemetry sink (log group with enforced retention) so DORA
 * events have a home. Implement against .kiro/specs/platform-framework/tasks.md.
 */

export interface GoldenServiceProps {
  serviceName: string;
  /** Lambda runtime; defaults to the team's app language. */
  runtime?: "python3.12" | "nodejs20.x" | "provided.al2023";
  /** CloudWatch Logs retention in days — REQUIRED to avoid silent cost creep. */
  logRetentionDays?: number;
}

/**
 * A "golden path" service: Lambda behind a REST API Gateway, with a telemetry
 * log group (retention enforced) and standard tags for cost attribution.
 *
 * TODO: extend `constructs.Construct`, wire aws-cdk-lib resources.
 * Kept as an interface-only stub so the package builds without a CDK app.
 */
export const GOLDEN_SERVICE_DEFAULTS: Required<Pick<GoldenServiceProps, "runtime" | "logRetentionDays">> = {
  runtime: "python3.12",
  logRetentionDays: 30,
};
