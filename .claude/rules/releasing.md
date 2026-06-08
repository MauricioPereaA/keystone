# Releasing & versioning

**Scope:** Repo-wide (both packages are independently distributed).

**See also:** [`commit-and-pr.md`](commit-and-pr.md), [`boundaries.md`](boundaries.md), ADR-0001.

## When this rule applies

You're cutting a release of the CLI or the framework, or changing how either is versioned/distributed.

## The rule

1. **Two independent version lines, both SemVer.** Tag the CLI as `cli-vX.Y.Z` and the framework as `framework-vX.Y.Z`. They release on their own cadence — a CLI fix doesn't force a framework bump.
2. **No registry — Git tags are the release artifact.** Consumers install pinned tags:
   - `uv tool install "git+https://github.com/MauricioPereaA/keystone@cli-vX.Y.Z#subdirectory=packages/devex-cli"`
   - `pnpm add "MauricioPereaA/keystone#framework-vX.Y.Z&path:/packages/platform-framework"`
3. **`package.json` / `pyproject.toml` `version` is the source of the tag.** Bump it in the release PR; the tag matches.
4. **SemVer meaning here:**
   - **major** — a breaking change to a public surface: the CLI command contract, a framework export, or the **telemetry `schemaVersion`** (cross-team contract → also needs an ADR).
   - **minor** — additive (new command, new generator option, new construct prop).
   - **patch** — fix, no surface change.
5. **Changelog per package.** Keep `packages/*/CHANGELOG.md`. Conventional-commit history makes this derivable (consider `changesets` for the framework / `release-please` for tag+changelog automation — a future improvement, not required for the PoC).
6. **Conventions changes ripple.** A `conventions.json` change that alters validation is at least a CLI minor (bundled copy changes) and may force a framework minor (generated workflows change). Release them together when they must stay in lockstep.
7. **Never retag.** A published tag is immutable (consumers pin it). To fix a bad release, cut the next patch.

## Why

Independent versioning is what makes "two distributable packages" real rather than cosmetic — it's the property the challenge's "Packaging Maturity" criterion checks. Git-tag releases keep the no-registry constraint while still giving teams reproducible, pinnable installs and a clean upgrade path (`uv tool upgrade` / `pnpm update`).

## Examples

### Good
```bash
# framework minor: new generator option
# 1) bump packages/platform-framework/package.json → 0.2.0
# 2) PR, squash-merge
git tag framework-v0.2.0 && git push origin framework-v0.2.0
```

### Bad
```bash
# ✗ one shared version for both packages — couples unrelated release cadences,
#   forces consumers to re-install the CLI for a framework-only change
git tag v0.2.0
```
