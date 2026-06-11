/**
 * DORA telemetry contract — the heart of the platform.
 *
 * Because @keystone/platform generates every team's CI workflows, every team
 * emits this identical event shape regardless of the application language
 * (Python, Go, Clojure, TypeScript). That language-agnostic event source is
 * what makes DORA metrics genuinely comparable across teams. See ADR-0002.
 *
 * The same event doubles as the SOC 2 audit record:
 *   who  → actor
 *   what → event + repo + env
 *   when → timestamp
 *   why  → workId (links to the tracked unit of work)
 */
export const SCHEMA_VERSION = "1.0.0";
/** Construct a fully-formed, schema-stamped event. */
export function buildEvent(input) {
    return { schemaVersion: SCHEMA_VERSION, timestamp: new Date().toISOString(), ...input };
}
/** Serialize as a single NDJSON line for the collector (CloudWatch / S3 / stdout). */
export function serializeEvent(event) {
    return JSON.stringify(event);
}
