# Security & AWS cost (Amazon Q review rules)

Distilled from `docs/engineering-rules/security.md` + `aws-cdk.md`. Flag any PR that:

- **Uses static AWS keys.** Generated/CI deploy workflows must authenticate via
  GitHub OIDC (`aws-actions/configure-aws-credentials` + a role ARN from a repo
  Variable). No `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` secrets anywhere.
- **Leaks secrets or PII.** No secrets/tokens/passwords in code, docs, `.env`, logs,
  generated workflows, or telemetry. The `DoraEvent` carries IDs only (actor as a
  principal, Work ID) — never tokens, emails, or raw payloads.
- **Allows shell injection.** Pass argv lists to subprocess; never `shell=True` /
  `os.system` / string-interpolated commands. Untrusted input (e.g. a PR title) must
  flow through an env var in workflows, never inlined into a `run:` command.
- **Skips an AWS cost guardrail.** Every CloudWatch log group has explicit retention
  (never the infinite default). PoC stateful resources use `RemovalPolicy.DESTROY`.
  Resources carry `project=keystone` + `service` + `env` tags. No NAT gateways.
  cdk-nag (`AwsSolutionsChecks`) must be clean; every `NagSuppressions` entry needs a
  written reason.
