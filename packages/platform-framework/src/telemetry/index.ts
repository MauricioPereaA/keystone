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

export const SCHEMA_VERSION = "1.0.0" as const;

export type DeploymentEvent =
  | "deployment.started"
  | "deployment.succeeded"
  | "deployment.failed"
  | "deployment.rolled_back";

export type Environment = "sandbox" | "staging" | "production";

export interface DoraEvent {
  schemaVersion: string;
  event: DeploymentEvent;
  /** Work ID, e.g. "FIN-123" — the "why" link. */
  workId: string;
  /** Actor identity (GitHub actor / IAM principal) — the "who". */
  actor: string;
  /** Service repository — the "what". */
  repo: string;
  env: Environment;
  commitSha: string;
  /** ISO-8601. Used with `timestamp` to derive Lead Time for Changes. */
  commitTime: string;
  /** ISO-8601 emission time — the "when". */
  timestamp: string;
  /** Optional correlation id (workflow run id). */
  runId?: string;
}

export interface BuildEventInput {
  event: DeploymentEvent;
  workId: string;
  actor: string;
  repo: string;
  env: Environment;
  commitSha: string;
  commitTime: string;
  runId?: string;
}

/** Construct a fully-formed, schema-stamped event. */
export function buildEvent(input: BuildEventInput): DoraEvent {
  return { schemaVersion: SCHEMA_VERSION, timestamp: new Date().toISOString(), ...input };
}

/** Serialize as a single NDJSON line for the collector (CloudWatch / S3 / stdout). */
export function serializeEvent(event: DoraEvent): string {
  return JSON.stringify(event);
}
