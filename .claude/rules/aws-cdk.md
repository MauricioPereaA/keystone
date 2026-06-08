# AWS CDK & cloud conventions

**Scope:** Infrastructure (TypeScript CDK in `@keystone/platform/constructs`) + any service that deploys to AWS.

**See also:** [`security.md`](security.md), [`soc2.md`](soc2.md), [`docs/runbooks/github-aws-oidc.md`](../../docs/runbooks/github-aws-oidc.md).

## When this rule applies

You're writing CDK, generating a deploy workflow, or provisioning anything in AWS for Keystone or a consuming service.

## The rule

1. **AWS CDK v2 only.** TypeScript. One construct library in `@keystone/platform/constructs`; teams consume it instead of writing raw Lambda/API Gateway wiring.
2. **Serverless by default.** Lambda + API Gateway (REST, per the reference profile) + DynamoDB + CloudWatch/S3. These sit in the AWS always-free tier at PoC scale.
3. **Environments are promoted, never hand-built.** `sandbox -> staging -> production` as CDK stages/stacks. The PR pipeline deploys `sandbox`; the integration pipeline promotes `staging -> production`.
4. **Auth via GitHub OIDC - never static keys.** Generated workflows use `aws-actions/configure-aws-credentials` with a role ARN assumed through OIDC. No `AWS_ACCESS_KEY_ID` secrets. See the runbook.
5. **Telemetry sink is part of the construct.** The `GoldenService` construct provisions the DORA/audit log group itself, so every service has a place to emit the standard event.

## Cost guardrails (trial account ~ \$100 - non-negotiable)

The compute is ~\$0; cost leaks come from forgotten or misconfigured resources. Every one of these is mandatory:

6. **CloudWatch Logs retention is set on EVERY log group.** Default is *forever*. Use `retention: logs.RetentionDays.ONE_MONTH`. A log group without explicit retention is a bug.
7. **No NAT Gateways.** ~\$32/month each, charged hourly even when idle. Keep Lambdas out of private subnets that require NAT; use VPC endpoints only if truly needed.
8. **`cdk destroy` after every demo / test run.** Nothing is left running overnight. Treat all PoC stacks as ephemeral.
9. **Tag everything** `project=keystone`, plus `service` and `env`. Enables cost attribution and a clean teardown.
10. **Set an AWS Budgets alarm** at \$25 and \$50 with email alerts before any deploy.
11. **Prefer HTTP API (\$1/M) over REST (\$3.50/M)** where the design allows - the reference profile uses REST API Gateway, so match it there but know the cheaper option for new services.
12. **`RemovalPolicy.DESTROY` on PoC stateful resources** (log groups, demo tables) so `cdk destroy` actually cleans them up - never on anything holding real data.

## Why

An AWS trial account closes when its credit is exhausted. At PoC scale the only realistic way to burn \$100 is an idle NAT gateway, an unbounded log group, or a stack nobody tore down. These guardrails make "demoable on \$100" a property of the platform, not luck - and that's a deliberate interview talking point.

## Examples

### Good
```ts
new logs.LogGroup(this, "Telemetry", {
  retention: logs.RetentionDays.ONE_MONTH,     // never infinite
  removalPolicy: RemovalPolicy.DESTROY,        // cdk destroy cleans it
});
Tags.of(this).add("project", "keystone");
```

### Bad
```ts
// inf retention (silent cost), no tags, lives in a NAT'd private subnet
new lambda.Function(this, "Fn", { vpc, vpcSubnets: { subnetType: PRIVATE_WITH_EGRESS } });
```

## Policy-as-code: cdk-nag (security + cost lint)

13. **Apply `cdk-nag`'s `AwsSolutionsChecks` aspect to every stack** and run it on `cdk synth` in CI. It catches the exact failure modes our guardrails care about — log groups without retention, over-permissive IAM, public resources — before they reach an account.

```ts
import { Aspects } from "aws-cdk-lib";
import { AwsSolutionsChecks } from "cdk-nag";
Aspects.of(app).add(new AwsSolutionsChecks({ verbose: true }));
```

- **Suppress only with a written reason** (`NagSuppressions.addResourceSuppressions(..., [{ id, reason }])`). An unexplained suppression is a review blocker.
- The `GoldenService` construct should ship cdk-nag-clean by default, so consuming teams inherit a passing baseline.
