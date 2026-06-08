# Telemetry & audit logging (the DORA + SOC 2 source)

**Scope:** Framework (the event contract) + any generated workflow that deploys.

**See also:** [`soc2.md`](soc2.md), [`security.md`](security.md), [`logging-discipline.md`](logging-discipline.md), ADR-0002.

## When this rule applies

You're emitting, shaping, or changing the deployment telemetry event — the single stream that feeds both DORA metrics and the SOC 2 audit trail.

## The rule

1. **One event shape, owned by `@keystone/platform/telemetry`.** Every generated deploy stage emits a `DoraEvent`. Because the framework — not the application — emits it, every team's events are identical regardless of language. This is the comparability guarantee (ADR-0002).

2. **The four W's are mandatory fields:**
   - **who** → `actor` (CI principal / IAM identity, an ID — never a name or email beyond a principal).
   - **what** → `event` + `repo` + `env`.
   - **when** → `timestamp` (ISO-8601), plus `commitTime` for lead-time math.
   - **why** → `workId` (links the deploy to its tracked unit of work).

3. **Constrained event vocabulary:** `deployment.started | succeeded | failed | rolled_back`. Don't invent ad-hoc events; extend the union in `telemetry/` (and bump nothing — additions are additive) if a new one is truly needed.

4. **Schema is versioned and additive-only** within a major `schemaVersion`. A breaking change is a cross-team contract change → ADR + coordinated bump.

5. **DORA metrics derive downstream, never per-language:** deployment frequency (count of `succeeded` in prod), lead time (`timestamp − commitTime`), change failure rate (`failed`+`rolled_back` ÷ total), MTTR (`failed` → next `succeeded`). Computed by `devex dora` over the stream — not instrumented in app code.

6. **The same row is the audit record.** Don't build a second audit mechanism; the DoraEvent stream answers "who deployed what, when, and why" for SOC 2 (`soc2.md`).

7. **Never put secrets or PII in the event.** IDs only. The redaction expectation is the same as `logging-discipline.md` §C.

8. **Emit on deploy, not on read.** Deployments and rollbacks emit; routine reads don't.

## Why

If each team instrumented its own metrics, "deployment frequency" would mean something different per team and comparison would be meaningless. Anchoring the metric to one framework-emitted event makes comparability structural. Reusing that same event as the audit record means SOC 2 evidence is a query over the stream, not a reconstruction.

## Examples

### Good
```ts
import { buildEvent, serializeEvent } from "@keystone/platform/telemetry";
const line = serializeEvent(buildEvent({
  event: "deployment.succeeded", workId: "FIN-123", actor: ctx.actor,
  repo, env: "production", commitSha, commitTime,
}));
// → one NDJSON line to the collector (CloudWatch/S3)
```

### Bad
```python
# ✗ per-language, app-side metric — guarantees drift, defeats comparability
statsd.incr(f"{service}.deploys")
```
