# Environment Variables

**Scope:** Both + Infra.

## When this rule applies

You're adding, removing, or renaming any env variable read at runtime by the CLI, the framework's generators, or a deployed service.

## The rule

1. **Add to `.env.example`** at the repo root with a safe default or an obvious placeholder, under the right section (CLI / Framework / AWS / CI).
2. **Read it through one entrypoint, not scattered lookups.**
   - CLI (Python): a single settings/config module reads `os.environ`; the rest of the code imports typed values from it.
   - Framework (TS): a single `env` module validates and exports; don't read `process.env` elsewhere.
3. **Document it** in the consumption guide if a consuming team must set it.
4. **CI** (`.github/workflows/*`): if tests need it, add to the job `env:`. Sensitive → GitHub **Secrets** (`${{ secrets.FOO }}`); non-sensitive → **Variables** (`${{ vars.FOO }}`).
5. **AWS auth values are Variables, not Secrets.** `AWS_DEPLOY_ROLE_ARN` and `AWS_REGION` are non-sensitive repo Variables (OIDC means no key material — `security.md`).

## Naming

- UPPER_SNAKE_CASE, nouns, type-hint suffix when non-obvious (`_SECONDS`, `_ARN`, `_URL`).
- Prefix with the consumer where helpful (`KEYSTONE_*`, `AWS_*`).

## Sensitivity

- Anything that can authenticate or decrypt → **Secret** (CI) / **Secrets Manager** (prod). But prefer OIDC so there's nothing to store.
- Never commit real secrets, even as a dev default. `.env` is gitignored; `.env.example` is the only env file in source.

## Why

Env vars are the most common "setup failed" vector. The single-entrypoint rule means a missing/renamed var surfaces in one place with a clear error, not as a scattered `KeyError` deep in a command. Keeping AWS auth as OIDC Variables (not Secrets) removes the most dangerous secret a CI repo can hold.

## Examples

### Good — framework `env` module
```ts
import { z } from "zod";
const schema = z.object({ AWS_REGION: z.string().default("us-east-1") });
export const env = schema.parse(process.env);
```

### Bad
```ts
// ✗ scattered, unvalidated, no startup failure
const region = process.env.AWS_REGION;   // undefined at the worst moment
```
