# Secret Rotation

Keystone is built so there is very little to rotate: deploys authenticate to AWS
via **GitHub OIDC**, so there is no long-lived cloud key stored anywhere. This
runbook covers the few credentials that do exist.

## AWS deploy role (GitHub OIDC)

**What it is:** an IAM role (`keystone-gh-deployer`) that GitHub Actions assumes
at runtime via OIDC. No access key or secret is stored — the trust is the OIDC
chain itself (see `docs/runbooks/github-aws-oidc.md`).

**When to rotate:** there is no key to rotate. To respond to a suspected
compromise or a scope change:

1. Tighten or correct the trust policy `sub` condition (must stay
   `repo:MauricioPereaA/keystone:*`).
2. Or delete the role and re-create it (re-run the runbook). The next workflow
   run regenerates the trust chain automatically.
3. To revoke all deploy access immediately: detach the role's permission
   policies or delete the role.

**Routine:** not on a schedule. Review the trust policy scope whenever the repo
moves org/owner.

## AWS Secrets Manager (if a service stores app secrets)

For any real service secret (e.g. a third-party API key a Lambda needs):

1. Create/rotate the secret in AWS Secrets Manager (enable automatic rotation
   where the provider supports it).
2. Services read it at runtime via the AWS SDK — never bake it into the image or
   commit it.
3. Confirm the deploy role has only `secretsmanager:GetSecretValue` on the
   specific secret ARN (least privilege, `security.md`).

## Local `.env`

`.env` is gitignored and dev-only. If a value leaks, rotate it at its source and
update your local file. Never commit it; `.env.example` (placeholders) is the only
env file in source.

## Telemetry sink

The DORA/audit collector (CloudWatch/S3) holds no credentials — it receives
non-sensitive events (IDs only, no secrets/PII per `audit-logging.md`). Nothing to
rotate.
