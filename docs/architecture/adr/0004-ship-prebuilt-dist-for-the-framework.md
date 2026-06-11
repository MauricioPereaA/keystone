---
title: Ship a prebuilt dist for the Git-distributed framework
number: 0004
status: Accepted
authors: [mauriceperea93@gmail.com]
created: 2026-06-10
updated: 2026-06-10
supersedes: null
superseded_by: null
related_prds: []
related_adrs: [ADR-0001]
linear: [FIN-317]
---

## Context

`@keystone/platform` is TypeScript that must be compiled to `dist/` before a
consumer can import it, and — per the no-registry constraint that also governs the
CLI (ADR-0001) — it is distributed **over Git**: consumers run
`pnpm add "MauricioPereaA/keystone#<ref>&path:/packages/platform-framework"`. There is
no npm registry to host a built tarball, so the compiled output has to reach the
consumer some other way.

The original approach (FIN-308) built `dist/` on install via a `prepare` script. A
real clean-room install surfaced why that is fragile: a Git-hosted package that runs
build scripts puts the build on the *consumer's* machine, where it depends on their
toolchain, their network (to fetch the framework's devDependencies), and their
package manager's policy. **pnpm 11.5+ now blocks build scripts for Git
dependencies by default** (`ERR_PNPM_GIT_DEP_PREPARE_NOT_ALLOWED`) — so the
documented `pnpm add` fails until the consumer adds the package to an `allowBuilds`
allowlist. npm and yarn each treat git-dep `prepare` differently again. Build-on-install
is the wrong layer for a registry-less package.

## Decision

We commit the framework's compiled `dist/` to the repository and remove the
build-on-install `prepare` script. The committed artifact is the distribution unit;
a CI gate rebuilds `dist/` on every PR and fails if it differs from what is
committed, so the artifact can never drift from source. Determinism across OSes is
guaranteed by the repo-wide `* text=auto eol=lf` in `.gitattributes` plus
`newLine: "lf"` in the framework `tsconfig.json`.

## Consequences

### Positive

- **Zero-config install for every consumer and package manager** — no build step, no
  toolchain, no network for devDeps, no pnpm `allowBuilds` allowlist. `pnpm add`
  (npm/yarn too), on any version, just resolves the committed files.
- **Faster, more reproducible installs** — the consumer copies prebuilt JS instead of
  compiling on their machine; what they run is exactly what CI built and gated.
- **Honors the no-registry constraint cleanly** — committing the artifact is the
  registry-less equivalent of publishing a built package (ADR-0001).
- **Tag installs are self-contained** — a pinned `framework-vX.Y.Z` tag now includes
  its own build output, so a release is reproducible without a build environment.

### Negative / tradeoffs

- **Build artifacts live in version control** — larger diffs on changes that touch
  generated output, and `dist/` appears in code review noise. Mitigated by treating
  it as generated (review the `src/` diff, trust the CI gate for `dist/`).
- **Contributors must rebuild before committing** — `prepare` no longer auto-builds on
  `pnpm install`. The CI "dist in sync" gate makes a forgotten rebuild a red check,
  not a silent stale ship.

### Follow-ups

- CI `framework-tests` job runs `build` then `git diff --exit-status -- …/dist` (done
  in this PR).
- Consumption guide + releasing doc note that the framework ships prebuilt and needs
  no build/allowlist on install (done in this PR).
- If a registry ever becomes available, publishing a built package supersedes this
  ADR; committed `dist/` is the no-registry stand-in until then.

## Alternatives considered

- **Keep build-on-install (`prepare`) and document the pnpm `allowBuilds` line.**
  Rejected: pushes a build onto every consumer, is package-manager- and
  version-specific, and bakes a known failure into the documented install command for
  pnpm 11.5+. It optimizes for a clean repo at the cost of a broken consumer.
- **Publish to a registry (npm / GitHub Packages).** Rejected here: the platform's
  distribution model is explicitly registry-less (ADR-0001). This is the right
  long-term answer and would supersede this ADR, but it is out of scope for the PoC.
- **A release workflow that builds `dist/` only into tags, keeping `main` artifact-free.**
  Rejected for now: cleaner `main` history, but it needs release automation that
  builds and commits into the tag, and it breaks the common "install from the default
  branch" path. Committed `dist/` with a freshness gate gives the same consumer
  guarantee with far less machinery, and tags inherit the built output for free.

## Change log

- 2026-06-10 — Proposed (PR #27)
- 2026-06-10 — Accepted (PR #27)
