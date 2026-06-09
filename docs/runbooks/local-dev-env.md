# Local dev environment (offline demo)

> **Challenge bonus A.** Run the whole golden path — service scaffold, CDK deploy,
> and DORA telemetry — **100% locally, no AWS account, no cost**, using LocalStack
> as the AWS emulator. This is the "demoable on \$0" property the platform aims for.

## Prerequisites

- Docker + Docker Compose (LocalStack runs as a container).
- `uv` (the `devex` CLI) and Node 24 + `pnpm` (the `@keystone/platform` framework).
- `aws-cdk-local` + `awslocal` for the CDK path: `npm i -g aws-cdk-local aws-cdk` and `pip install awscli-local` (or use `npx`/`uvx`).

## 1. Start the emulator

```bash
make localstack-up          # docker compose up -d localstack  (edge gateway on :4566)
curl -s localhost:4566/_localstack/health   # services should report "available"
```

LocalStack emulates Lambda, API Gateway, CloudWatch Logs, S3, IAM/STS, and
CloudFormation — everything the `GoldenService` construct provisions.

## 2. Telemetry → DORA, fully local (no deploy needed)

The DORA reporting loop runs offline against a local NDJSON stream — the same
`DoraEvent` shape the generated deploy workflow emits:

```bash
# point the CLI at a local stream (instead of CloudWatch/S3)
export KEYSTONE_TELEMETRY_STREAM=./telemetry.ndjson

# (deploys append DoraEvent lines here; for a quick demo, write a few by hand,
#  or copy the example below)
devex dora --stream ./telemetry.ndjson
```

This is the part you can demo immediately — `devex dora` computes deployment
frequency, lead time, change-failure-rate, and MTTR from the stream.

## 3. The CDK path (deploy GoldenService to LocalStack)

A service created with `devex init <service>` (plus its CDK app instantiating the
`GoldenService` construct) deploys to the emulator exactly like real AWS, but the
endpoint is LocalStack:

```bash
export AWS_ENDPOINT_URL=http://localhost:4566
export AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_REGION=us-east-1

cdklocal bootstrap            # one-time, against LocalStack
cdklocal deploy --all --require-approval never --context env=sandbox

# exercise the API + read the telemetry log group LocalStack created
awslocal apigateway get-rest-apis
awslocal logs tail /keystone/<service>/dora --format short
```

Because LocalStack is the only target, the cost guardrails (`RemovalPolicy.DESTROY`,
log retention) and OIDC-vs-keys distinctions don't cost anything to exercise.

## 4. Tear down

```bash
make localstack-down         # docker compose down -v  (removes the volume)
```

## Example telemetry stream

```ndjson
{"schemaVersion":"1.0.0","event":"deployment.succeeded","workId":"FIN-101","actor":"ci","repo":"transactionify","env":"production","commitSha":"a1","commitTime":"2026-06-08T09:00:00Z","timestamp":"2026-06-08T11:00:00Z"}
{"schemaVersion":"1.0.0","event":"deployment.failed","workId":"FIN-102","actor":"ci","repo":"transactionify","env":"production","commitSha":"a2","commitTime":"2026-06-08T12:00:00Z","timestamp":"2026-06-08T13:00:00Z"}
{"schemaVersion":"1.0.0","event":"deployment.succeeded","workId":"FIN-102","actor":"ci","repo":"transactionify","env":"production","commitSha":"a3","commitTime":"2026-06-08T12:30:00Z","timestamp":"2026-06-08T13:30:00Z"}
```

## Notes

- Pin the LocalStack image to a specific version in `docker-compose.yml` for
  reproducible CI; `:latest` is fine for local exploration.
- The Lambda runtime is `nodejs22.x`/`nodejs24.x` or `python3.12` — all available
  in LocalStack's Lambda emulation.
