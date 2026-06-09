# Consumption Guide — adopting Keystone in your team's repo

How a service team installs, configures, extends, and upgrades the Keystone
ecosystem. The reference adoption target is **Transactionify**, but these steps
apply to any Python / Go / Clojure / TypeScript service.

---

## 1. Install

Both packages install directly from Git — no registry, no published versions.

### Developer CLI (`devex`)

```bash
uv tool install "git+https://github.com/MauricioPereaA/keystone#subdirectory=packages/devex-cli"
devex version
```

Pin a version for reproducibility (recommended for teams):

```bash
uv tool install "git+https://github.com/MauricioPereaA/keystone@cli-v0.1.0#subdirectory=packages/devex-cli"
```

### Platform framework (`@keystone/platform`)

In your service's infra/CI workspace:

```bash
pnpm add "github:MauricioPereaA/keystone#path:/packages/platform-framework"
# or pinned (also works for forks):
pnpm add "MauricioPereaA/keystone#framework-v0.1.0&path:/packages/platform-framework"
```

---

## 2. Configure (adopt the golden path)

From the root of your service repo:

```bash
devex init        # new service: scaffolds structure + PR template + workflows
# or
devex adopt       # existing service (e.g. a Transactionify fork): adds Keystone
                  # artifacts without touching your application code
```

This drops in:

- the **PR template** (Work ID + two-reviewer rule),
- generated **GitHub Actions workflows** (PR Pipeline; Integration Pipeline),
- **git hooks** (run `devex hooks install` if not auto-installed),
- a reference to the shared `conventions.json` (the CLI bundles its own copy; you don't vendor it).

### One-time AWS auth (per repo)

Set the two repo **Variables** (not secrets) so generated deploy jobs can assume
your role via OIDC — see [`runbooks/github-aws-oidc.md`](runbooks/github-aws-oidc.md):

| Variable | Example |
|---|---|
| `AWS_REGION` | `us-east-1` |
| `AWS_DEPLOY_ROLE_ARN` | `arn:aws:iam::<acct>:role/keystone-gh-deployer` |

---

## 3. Daily use

```bash
git switch -c feature/FIN-123-add-validation   # branch carries the Work ID
devex standards-check                          # validate locally (same rules as CI)
git commit -m "feat(api): FIN-123 add validation"
git push                                        # PR Pipeline runs: small-tests → sandbox
devex dora                                      # see your team's DORA metrics
```

Because the CLI validates with the **same** `conventions.json` the generated CI
uses, "passes locally" means "passes CI".

---

## 4. Extend

You don't fork the platform to customize — you compose it:

- **New CDK resource:** consume the `GoldenService` construct from
  `@keystone/platform/constructs`; pass props (runtime, log retention). Don't
  hand-wire Lambda + API Gateway.
- **New pipeline step:** the framework's workflow generators accept options;
  prefer extending the generator (a PR to Keystone) over editing generated YAML
  by hand — hand-edits drift and lose the telemetry guarantee.
- **New convention:** propose a change to `conventions/conventions.json` via a
  PR to Keystone (see the [Contribution Guide](contributing.md)). It then applies
  to every team at once.
- **New language (Go / Clojure / …):** see the `/new-language` skill and the
  Contribution Guide — you add a test-toolchain mapping, not a new metric.

---

## 5. Upgrade

```bash
# CLI — across all workstations
uv tool upgrade devex-cli
# or re-pin to a new tag
uv tool install --force "git+https://github.com/MauricioPereaA/keystone@cli-v0.2.0#subdirectory=packages/devex-cli"

# Framework
pnpm update "@keystone/platform"
# then regenerate workflows so you pick up new stages/telemetry
pnpm generate:workflows   # re-runs the @keystone/platform generator in your repo
```

Versioning is independent per package (`cli-v*` / `framework-v*`); both are
SemVer. Breaking changes to the telemetry schema are major bumps announced via an
ADR (see [`architecture/adr/`](architecture/adr/)).

---

## 6. Troubleshooting

| Symptom | Fix |
|---|---|
| `uv tool install` marker/resolution error | You're on an old uv; upgrade. The CLI is self-contained, so the subdirectory install must resolve cleanly (ADR-0001). |
| `pnpm add #path:` not found | Requires pnpm ≥ 9 (subdirectory installs). |
| Deploy job can't assume the AWS role | Check the OIDC trust policy `sub` matches your repo and `id-token: write` permission is set. |
| `standards-check` passes locally but CI fails | Your bundled conventions copy is stale — `uv tool upgrade devex-cli`. |
