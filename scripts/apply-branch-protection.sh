#!/usr/bin/env bash
# Apply the main-branch protection ruleset: PR required, two approving reviews,
# no force-push, no branch deletion (admin role retains bypass for emergencies).
#
# GitHub gates branch protection AND rulesets behind a paid plan for PRIVATE
# repos, so this is a no-op there (HTTP 403). Run it once after the repo is made
# public OR upgraded to GitHub Pro/Team. The ruleset lives as code in
# .github/rulesets/main-protection.json — see ADR-0003.
#
# Usage: scripts/apply-branch-protection.sh [owner/repo]
set -euo pipefail

REPO="${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"
RULESET_FILE="$(cd "$(dirname "$0")/.." && pwd)/.github/rulesets/main-protection.json"

if [[ ! -f "${RULESET_FILE}" ]]; then
  echo "✗ ruleset file not found: ${RULESET_FILE}" >&2
  exit 1
fi

echo "Applying main-branch ruleset to ${REPO} …"
gh api --method POST "repos/${REPO}/rulesets" --input "${RULESET_FILE}"
echo "✓ Ruleset applied. Verify with: gh api repos/${REPO}/rulesets"
