# Security

**Scope:** Both + Infra (sections call out which).

## When this rule applies

You're touching secrets, authentication to AWS, input that crosses a trust boundary, or generated workflows.

## The rule

### Secrets

1. **Never commit secrets** — not in code, docs, or `.env`. `.env.example` with placeholders only.
2. **Read config through documented entrypoints** (`environment-variables.md`), never scattered `os.environ` / `process.env`.
3. **Rotate on suspected compromise.** No long-lived credentials to rotate in the first place if §4 is followed.

### Auth to AWS (Infra)

4. **GitHub OIDC, never static keys.** Generated deploy workflows use `aws-actions/configure-aws-credentials` with a role ARN assumed via OIDC. No `AWS_ACCESS_KEY_ID`/`SECRET` secrets exist. Runbook: `docs/runbooks/github-aws-oidc.md`.
5. **Least-privilege deploy role.** Scope the trust policy `sub` to this repo; scope permissions to the CDK/CloudFormation + service resources actually deployed. No `AdministratorAccess` on anything real.

### Input validation

6. **Validate `conventions.json` against a schema** (Pydantic on the CLI) before use — a malformed conventions file should fail fast with a clear message, not produce silent mis-validation.
7. **Treat any file the CLI reads or generates as untrusted** until validated (size, shape). Don't `eval`/exec generated content.
8. **No `subprocess(..., shell=True)` / `os.system`.** Pass argv lists to git; never interpolate user input into a shell string.

### Generated workflows / telemetry

9. **No secrets in generated workflows** — only OIDC role ARNs (non-sensitive) via repo Variables.
10. **No secrets or PII in telemetry/logs.** The DoraEvent carries IDs (`actor` as principal, `workId`), never tokens, raw payloads, or personal data (`logging-discipline.md`).

## Why

The platform's attack surface is small but real: it generates CI that has cloud credentials. The whole point of OIDC is that a leaked repo can't leak a long-lived AWS key — there isn't one. Schema-validating `conventions.json` prevents a corrupted source-of-truth from silently weakening every team's checks at once.

## Examples

### Good — OIDC in a generated deploy job
```yaml
permissions: { id-token: write, contents: read }
steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with: { role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}, aws-region: ${{ vars.AWS_REGION }} }
```

### Bad — static keys
```yaml
# ✗ long-lived credentials in secrets; exactly what OIDC exists to avoid
env: { AWS_ACCESS_KEY_ID: ${{ secrets.AWS_KEY }}, AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET }} }
```

### Bad — shell injection
```python
# ✗ never
subprocess.run(f"git checkout {branch}", shell=True)
# ✓
subprocess.run(["git", "checkout", branch])
```
