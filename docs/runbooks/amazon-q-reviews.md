# Amazon Q Developer — AI-assisted PR reviews (bonus C)

Keystone layers AI code review on top of its deterministic gates: the dogfooded
`ci.yml` enforces conventions/tests/drift (pass/fail), and Amazon Q Developer adds
semantic, context-aware review of each PR — checking against the **same** Keystone
rules. No GitHub Action, no secrets, no AWS account required.

## Install (repo owner, one-time)

1. Open the Marketplace app: <https://github.com/marketplace/amazon-q-developer>
2. Click **Install** (free) and grant it access to `MauricioPereaA/keystone`
   (and any adopting fork, e.g. a Transactionify fork).
3. Accept the AWS Customer Agreement / Service Terms shown on install.

That's the whole setup — it's a GitHub App, not a workflow you maintain.

## How it reviews against Keystone's rules

Amazon Q reads **`.amazonq/rules/*.md`** as project rules and applies them to every
review (and to `/q dev` code generation). Those files are distilled from the
canonical `.claude/rules/`, so Q reviews PRs against the exact conventions the CLI
and CI enforce — the single source of truth, extended to AI review:

| `.amazonq/rules/` file | Covers |
|---|---|
| `keystone-conventions.md` | Work ID, single source of truth, no hard-coded patterns, PRD-first |
| `security-and-cost.md` | OIDC (no static keys), no secrets/PII, no shell injection, AWS cost guardrails + cdk-nag |
| `errors-and-telemetry.md` | errors visible / structured logging, the single `DoraEvent` source, SOC 2 |
| `testing.md` | PBT for validators, telemetry-step-in-every-deploy-job, CDK assertions, coverage floor |

Keep these in step with `.claude/rules/` when a rule changes (a future improvement
is to generate them from the canonical set).

## Usage

- **Automatic** — Q reviews each PR on open/update.
- **On demand** — comment `/q review` on a PR; `/q dev` to draft a change; `/q help`.

## Where it fits in the feedback loop

| Layer | Tool | Nature |
|---|---|---|
| Local shift-left | `devex standards-check` + `devex hooks install` | deterministic, pre-push |
| CI gates | `ci.yml` (tests + conventions drift) + `pr-title.yml` | deterministic, blocking |
| AI review | **Amazon Q Developer** (this) | semantic, advisory |

The first two are the source of truth (a PR can't merge without them); Q is an
extra, AI-powered reviewer that reasons about intent and our written rules.

## Local Amazon Q (optional — a different product)

For terminal AI (not PR review), install the **Amazon Q Developer CLI**, which logs
in with a free **AWS Builder ID** (no AWS account): <https://github.com/aws/amazon-q-developer-cli>
— macOS/Linux natively, Windows via WSL. (Now also distributed as "Kiro CLI".)
