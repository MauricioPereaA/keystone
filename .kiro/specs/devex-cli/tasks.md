# Tasks — devex CLI

> `[x]` = scaffolded/working in the PoC. `[ ]` = to implement. Each maps to a requirement.

- [x] 1. Package skeleton: `pyproject.toml` (self-contained, uv, console script), src layout. (R6)
- [x] 2. `conventions.py` loader for bundled `_data/conventions.json`. (R1)
- [x] 3. `validators.py`: `validate_branch` / `validate_commit` / `validate_pr_title`. (R1)
- [x] 4. `standards-check` command wired to validators with Rich output + exit codes. (R1)
- [x] 5. Tests: unit (table-driven) + property-based (Hypothesis). (NFR)
- [ ] 6. `make sync-conventions` + CI drift check (canonical file vs bundled copy). (R6)
- [x] 7. `init <service>`: scaffold service + PR template + call `@keystone/platform` workflow generator (shell-out + fallback). (R2)
- [x] 8. `adopt` mode for existing repos (Transactionify case study) — never overwrites app code. (R2)
- [x] 9. `pr` command: enforce Work ID in title (from the last commit), apply template, open PR via `gh` (`--dry-run` for safety). (R3)
- [x] 10. `hooks install`: write pre-commit/pre-push hooks invoking `standards-check` (native, no pre-commit framework dep). (R4)
- [x] 11. `dora` command: parse NDJSON stream, compute the four metrics, Rich table. (R5) — plus `workid` (extracts the Work ID for generated CI telemetry).
- [x] 12. Local pipeline simulation: `pipeline run --local` (conventions gate + per-language small-tests). (R1, bonus)
- [ ] 13. Bring coverage to ≥ 80% and document in README. (NFR)
