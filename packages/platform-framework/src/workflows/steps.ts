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

import { Step, expressions } from "@github-actions-workflow-ts/lib";
import { SCHEMA_VERSION, type DeploymentEvent, type Environment } from "../telemetry/index.js";

/** Pinned source for the `devex` CLI (self-contained Git install — ADR-0001). */
const DEVEX_SPEC = "git+https://github.com/MauricioPereaA/keystone#subdirectory=packages/devex-cli";

/** GHA expression for the Work ID resolved by the small-tests job. */
export const WORK_ID_EXPR = expressions.expn("needs.small-tests.outputs.work_id");

export function checkoutStep(): Step {
  return new Step({ name: "Checkout", uses: "actions/checkout@v4" });
}

export function setupUvStep(): Step {
  return new Step({ name: "Set up uv", uses: "astral-sh/setup-uv@v6" });
}

/**
 * Validate branch + commit against `conventions.json` AND publish the Work ID
 * as a step output — both via the `devex` CLI, so CI enforces the exact same
 * rules the developer ran locally (shift-left parity, single source of truth).
 */
export function standardsCheckStep(): Step {
  return new Step({
    name: "Validate conventions & resolve Work ID (devex)",
    id: "standards",
    run: [
      `uvx --from "${DEVEX_SPEC}" devex standards-check`,
      `echo "work_id=$(uvx --from "${DEVEX_SPEC}" devex workid)" >> "$GITHUB_OUTPUT"`,
    ].join("\n"),
  });
}

/** Node setup for the CDK deploy (the infra app is TypeScript regardless of service language). */
export function cdkSetupSteps(): Step[] {
  return [
    new Step({ name: "Set up pnpm", uses: "pnpm/action-setup@v4" }),
    new Step({ name: "Set up Node", uses: "actions/setup-node@v4", with: { "node-version": "24", cache: "pnpm" } }),
    new Step({ name: "Install infra dependencies", run: "pnpm install --frozen-lockfile" }),
  ];
}

/**
 * Authenticate to AWS via GitHub OIDC — never static keys (security.md §4).
 * The role ARN and region are non-sensitive repo Variables, not Secrets.
 */
export function configureAwsCredentialsStep(): Step {
  return new Step({
    name: "Configure AWS credentials (OIDC)",
    uses: "aws-actions/configure-aws-credentials@v4",
    with: {
      "role-to-assume": expressions.var("AWS_DEPLOY_ROLE_ARN"),
      "aws-region": expressions.var("AWS_REGION"),
    },
  });
}

export function cdkDeployStep(env: Environment): Step {
  return new Step({
    name: `Deploy to ${env} (CDK)`,
    id: "deploy",
    run: `pnpm exec cdk deploy --all --require-approval never --context env=${env}`,
  });
}

/**
 * Emit one NDJSON {@link DoraEvent} for a deploy stage. Built with `jq` from the
 * GitHub Actions context so it is language-agnostic; the schema version is
 * sourced from the telemetry contract (not hard-coded). IDs only — no secrets
 * or PII (audit-logging.md §7).
 */
export function emitTelemetryStep(input: {
  event: DeploymentEvent;
  env: Environment;
  /** GHA expression yielding the Work ID. Defaults to the small-tests output. */
  workIdExpr?: string;
  /** Optional step condition, e.g. "success()" / "failure()". */
  if?: string;
}): Step {
  const workId = input.workIdExpr ?? WORK_ID_EXPR;
  const actor = expressions.expn("github.actor");
  const repo = expressions.expn("github.repository");
  const sha = expressions.expn("github.sha");
  const runId = expressions.expn("github.run_id");
  const commitTime = expressions.expn(
    "github.event.head_commit.timestamp || github.event.pull_request.updated_at",
  );
  const run = [
    "jq -nc \\",
    `  --arg schemaVersion "${SCHEMA_VERSION}" \\`,
    `  --arg event "${input.event}" \\`,
    `  --arg workId "${workId}" \\`,
    `  --arg actor "${actor}" \\`,
    `  --arg repo "${repo}" \\`,
    `  --arg env "${input.env}" \\`,
    `  --arg commitSha "${sha}" \\`,
    `  --arg commitTime "${commitTime}" \\`,
    '  --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \\',
    `  --arg runId "${runId}" \\`,
    "  '{schemaVersion:$schemaVersion,event:$event,workId:$workId,actor:$actor," +
      "repo:$repo,env:$env,commitSha:$commitSha,commitTime:$commitTime,timestamp:$timestamp,runId:$runId}' \\",
    '  | tee -a "$GITHUB_STEP_SUMMARY"',
  ].join("\n");
  return new Step({ name: `Emit DORA telemetry (${input.event})`, if: input.if, run });
}

/** Report the four DORA metrics from the telemetry stream (integration pipeline tail). */
export function doraReportStep(): Step {
  return new Step({
    name: "Report DORA metrics (devex dora)",
    run: `uvx --from "${DEVEX_SPEC}" devex dora`,
  });
}
