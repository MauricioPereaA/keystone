# Testing Conventions

**Scope:** Both (split — CLI = pytest, Framework = Vitest). "Both stacks" rules apply to everyone.

## When this rule applies

You're writing a test for new code (or fixing a bug that should have had one).

## The rule

### CLI (pytest + Hypothesis)

1. **Location** mirrors source: `src/devex/validators.py` → `tests/test_validators.py`.
2. **Pure logic is unit-tested table-driven** (`@pytest.mark.parametrize`) — valid and invalid cases.
3. **Property-Based Testing (PBT) is mandatory for validators.** Use Hypothesis to assert a *property* over generated inputs, not just examples — e.g. "any well-formed `type/<WORK-ID>-<slug>` passes", "no subject lacking a Work ID passes". The PR pipeline's small-tests stage requires PBT.
4. **Build invalid inputs directly** (`st.from_regex`), don't `.filter()` broadly — broad filters are slow and flaky.
5. **No network.** The CLI shells out to git; isolate that in one helper and test the pure functions around it.
6. **Coverage floor: 80%.** A floor, not a target.

### Framework (Vitest)

7. **Co-locate** `*.test.ts` next to the module (`telemetry/index.ts` → `telemetry/telemetry.test.ts`).
8. **Telemetry contract tests** assert the event shape: schema version stamped, the four W's present (actor/repo/timestamp/workId), single-line NDJSON serialization.
9. **Workflow generators** are snapshot-tested on the emitted YAML, and MUST assert the telemetry step is present in every deploy job.
10. **CDK constructs** use `Template.fromStack(...)` assertions — Lambda + REST API + a LogGroup *with* retention exist.
11. **`tsc --noEmit` is part of the test gate** (types are tests here).

### Both

- **Name tests by behavior**, not by function: `test_returns_only_wellformed_branches` > `test_validate_1`.
- **A fix without a regression test is incomplete** — the test must fail on the unfixed code.
- **Never test the framework itself** (Typer, Vitest, CDK internals). Test our logic.

## Why

The validators and the telemetry contract are the two load-bearing pieces. PBT on the validators proves the convention rules hold for *all* inputs, not the three the author thought of. The "telemetry step present in every deploy job" assertion is what guarantees DORA comparability survives a refactor of the generator.

## Examples

### Good — CLI PBT
```python
@given(work_id=st.from_regex(r"[A-Z]{2,5}-[0-9]{1,6}", fullmatch=True),
       slug=st.from_regex(r"[a-z0-9]+(-[a-z0-9]+)*", fullmatch=True))
def test_any_wellformed_branch_passes(work_id, slug):
    assert validate_branch(f"feature/{work_id}-{slug}").ok is True
```

### Good — framework contract
```ts
it("preserves who/what/when/why", () => {
  const e = buildEvent(base);
  expect([e.actor, e.repo, e.timestamp, e.workId].every(Boolean)).toBe(true);
});
```

### Bad
```python
# ✗ tests the framework, not our code
def test_typer_app_exists(): assert app is not None
```

## API contract validation (PR pipeline "small-tests")

The PR pipeline's small-tests stage requires **unit + property-based + API-contract**. For services exposing the REST API Gateway:

- **Contract-test the OpenAPI spec**, don't hand-write request assertions. Recommended: `schemathesis` (Python — generates cases from the OpenAPI schema, pairs naturally with Hypothesis) or a Pact-style consumer/provider check for cross-service contracts.
- The contract test is **generated/selected by the framework's workflow generator per language**, so "API-contract" means the same thing for every team (the `/new-language` skill adds the mapping).
- A contract test failing on a breaking API change is the point — treat it as a red gate, not a flake.
