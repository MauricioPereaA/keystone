# Design — @keystone/platform

## Module layout

```
src/
├── telemetry/   # DoraEvent type, buildEvent, serializeEvent, SCHEMA_VERSION  (the contract)
├── workflows/   # generatePrPipeline / generateIntegrationPipeline (github-actions-workflow-ts)
├── constructs/  # GoldenService CDK construct (Lambda + REST API GW + telemetry log group)
└── index.ts     # public surface: re-exports the three subpaths
```

Subpath exports (`@keystone/platform/telemetry|workflows|constructs`) keep consumers' bundles lean.

## Telemetry (the differentiator) — ADR-0002

A single `DoraEvent` interface, schema-versioned. `buildEvent` stamps `schemaVersion` + `timestamp`; `serializeEvent` emits one NDJSON line. The four W's map to fields: actor (who), event+repo+env (what), timestamp (when), workId (why). Because workflow generation lives here, every team emits this exact shape → DORA comparability is structural, not enforced by convention.

Collector (PoC): NDJSON appended to CloudWatch Logs / S3. `devex dora` reads it. Production swap (DynamoDB/Kinesis/Datadog) changes only the sink, not the contract.

## Workflow generation — R1

`generatePrPipeline(options)` builds a workflow AST with `NormalJob`/`Step` from `github-actions-workflow-ts`, then serializes to YAML. A `language` switch selects the small-tests job (`uv run pytest` / `go test` / `lein test` / `pnpm test`). A shared `emitTelemetryStep` is appended to every deploy job. Compile-time types catch malformed jobs before commit.

## CDK construct — R2

`GoldenService` extends `constructs.Construct`: a `lambda.Function` (runtime from props), a `apigateway.RestApi`, and a `logs.LogGroup` with `retention` **required** (defaults to 30 days — cost guardrail per `docs/engineering-rules/aws-cdk.md`). Standard tags (`project=keystone`, `service`, `env`) for cost attribution and teardown.

## Multi-environment promotion

`sandbox → staging → production` as CDK stages/stacks. PR pipeline deploys sandbox; integration pipeline promotes staging→production with the metric-emit step last.

## Testing strategy

- Telemetry: Vitest unit tests on `buildEvent`/`serializeEvent` (schema stamp, four W's, NDJSON single-line). **Done.**
- Workflows: snapshot the generated YAML; assert the telemetry step is present in every deploy job.
- Constructs: CDK assertions (`Template.fromStack`) — Lambda + RestApi + LogGroup-with-retention exist.

## Security

Generated workflows authenticate to AWS via **GitHub OIDC** (`aws-actions/configure-aws-credentials` with a role ARN), never static keys. See `docs/runbooks/github-aws-oidc.md`.
