# Tasks — devex CLI

> `[x]` = scaffolded/working in the PoC. `[ ]` = to implement. Each maps to a requirement.

- [x] 1. Package skeleton: `pyproject.toml` (self-contained, uv, console script), src layout. (R6)
- [x] 2. `conventions.py` loader for bundled `_data/conventions.json`. (R1)
- [x] 3. `validators.py`: `validate_branch` / `validate_commit` / `validate_pr_title`. (R1)
- [x] 4. `standards-check` command wired to validators with Rich output + exit codes. (R1)
- [x] 5. Tests: unit (table-driven) + property-based (Hypothesis). (NFR)
- [ ] 6. `make sync-conventions` + CI drift check (canonical file vs bundled copy). (R6)
- [ ] 7. `init <service>`: scaffold service + PR template + call `@keystone/platform` workflow generator. (R2)
- [ ] 8. `adopt` mode for existing repos (Transactionify case study). (R2)
- [ ] 9. `pr` command: enforce Work ID in title, apply template, open PR via `gh`. (R3)
- [ ] 10. `hooks install`: write pre-commit/pre-push hooks invoking `standards-check`. (R4)
- [ ] 11. `dora` command: parse NDJSON stream, compute the four metrics, Rich table. (R5)
- [ ] 12. Local pipeline simulation: `pipeline run --local`. (R1, bonus)
- [ ] 13. Bring coverage to ≥ 80% and document in README. (NFR)
