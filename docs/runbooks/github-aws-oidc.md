# GitHub Actions ↔ AWS via OIDC (no static keys)

One-time setup so generated deploy workflows can assume an AWS role through
GitHub's OIDC provider — no `AWS_ACCESS_KEY_ID` secrets stored anywhere. This
is the auth model the platform framework emits (see `docs/engineering-rules/aws-cdk.md`
and the platform-framework design spec).

## 1. Register GitHub as an OIDC identity provider in AWS (once per account)

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

## 2. Create a deploy role trusting only this repo

Trust policy (`trust.json`) — scope `sub` to the repo so no other repo can assume it:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Federated": "arn:aws:iam::<ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com" },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": { "token.actions.githubusercontent.com:aud": "sts.amazonaws.com" },
      "StringLike": { "token.actions.githubusercontent.com:sub": "repo:MauricioPereaA/keystone:*" }
    }
  }]
}
```

```bash
aws iam create-role --role-name keystone-gh-deployer \
  --assume-role-policy-document file://trust.json

# Attach least-privilege deploy permissions (scope to the CDK/CloudFormation +
# service resources you deploy — avoid AdministratorAccess in anything real).
aws iam attach-role-policy --role-name keystone-gh-deployer \
  --policy-arn arn:aws:iam::aws:policy/PowerUserAccess   # tighten for prod
```

## 3. GitHub repo settings

### Variables (`Settings → Secrets and variables → Actions → Variables`)
| Name | Example |
|---|---|
| `AWS_REGION` | `us-east-1` |
| `AWS_DEPLOY_ROLE_ARN` | `arn:aws:iam::<ACCOUNT_ID>:role/keystone-gh-deployer` |

No secrets needed — the OIDC token is exchanged at runtime.

## 4. Workflow step (emitted by the framework)

```yaml
permissions:
  id-token: write        # REQUIRED for OIDC
  contents: read
steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}
      aws-region: ${{ vars.AWS_REGION }}
  - run: npx cdk deploy --require-approval never
```

## 5. Validate

Trigger the PR pipeline; the `configure-aws-credentials` step should print the
assumed role ARN. Confirm with `aws sts get-caller-identity` in a debug step.

## Rotation

Nothing to rotate — there is no key material. To revoke access, delete the role
or tighten the trust-policy `sub` condition. The OIDC trust chain regenerates on
every workflow run.

## Cost note

After any demo, `cdk destroy` all stacks and confirm no NAT gateways or
unbounded log groups remain (`docs/engineering-rules/aws-cdk.md`).
