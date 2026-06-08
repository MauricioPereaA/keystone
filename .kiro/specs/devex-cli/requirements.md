# Requirements — devex CLI

## Introduction

The `devex` CLI is the developer-facing interface to the Keystone platform. It moves convention enforcement to the workstation (shift-left), abstracts standardized git workflows, and bootstraps new services onto the golden path. All behavior is driven by `conventions/conventions.json` so local validation matches CI exactly.

## Requirements

### R1 — Local standards validation
**User story:** As an engineer, I want to validate my branch and commit against org conventions locally, so that I get feedback in seconds instead of waiting for CI.

- WHEN `devex standards-check` runs, THE SYSTEM SHALL validate the current branch name and latest commit subject against `conventions.json`.
- WHEN any check fails, THE SYSTEM SHALL print the failing rule with an example and exit non-zero.
- WHEN the branch is protected (e.g. `main`), THE SYSTEM SHALL skip branch-pattern validation.

### R2 — Project bootstrap
**User story:** As an engineer, I want to scaffold a new service onto the golden path, so that I don't reinvent structure, PR template, or workflows.

- WHEN `devex init <service>` runs, THE SYSTEM SHALL generate the service skeleton, PR template, and CI workflows (via `@keystone/platform`), pre-wired with conventions.
- WHERE a service already exists, THE SYSTEM SHALL support an `adopt` mode that adds Keystone artifacts without overwriting app code.

### R3 — Git workflow abstractions
**User story:** As an engineer, I want standardized branch/PR commands, so that conventions are automatic.

- WHEN `devex pr` runs, THE SYSTEM SHALL prepare a PR with the Work ID enforced in the title and the standard template applied.

### R4 — Pre-push validation (shift-left)
**User story:** As an engineer, I want checks to run before push, so that non-conforming work never reaches CI.

- WHEN `devex hooks install` runs, THE SYSTEM SHALL install git hooks that run `standards-check` on pre-commit and pre-push.

### R5 — DORA reporting
**User story:** As a team lead, I want the four DORA metrics from the telemetry stream, so that my team is comparable to others.

- WHEN `devex dora` runs against an event stream, THE SYSTEM SHALL compute deployment frequency, lead time for changes, change failure rate, and MTTR.

### R6 — Distribution
- THE SYSTEM SHALL be installable via `uv tool install git+<url>#subdirectory=packages/devex-cli`, support pinned versions, and upgrade via `uv tool upgrade`.
- THE SYSTEM SHALL be self-contained (no monorepo workspace dependency).

## Non-functional

- Tests: pytest unit + Hypothesis property-based. Coverage floor 80%.
- No secrets or PII in output or logs.
