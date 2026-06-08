import { describe, expect, it } from "vitest";
import { buildEvent, serializeEvent, SCHEMA_VERSION, type BuildEventInput } from "./index.js";

const base: BuildEventInput = {
  event: "deployment.succeeded",
  workId: "FIN-123",
  actor: "mauricio@org.com",
  repo: "transactionify",
  env: "production",
  commitSha: "abc123",
  commitTime: "2026-06-08T10:00:00.000Z",
};

describe("DORA telemetry contract", () => {
  it("stamps schema version and timestamp", () => {
    const e = buildEvent(base);
    expect(e.schemaVersion).toBe(SCHEMA_VERSION);
    expect(e.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T/);
  });

  it("preserves the four W's (who/what/when/why)", () => {
    const e = buildEvent(base);
    expect(e.actor).toBe("mauricio@org.com"); // who
    expect(e.repo).toBe("transactionify"); // what
    expect(e.workId).toBe("FIN-123"); // why
    expect(e.timestamp).toBeDefined(); // when
  });

  it("serializes to a single NDJSON line", () => {
    const line = serializeEvent(buildEvent(base));
    expect(line).not.toContain("\n");
    expect(JSON.parse(line).workId).toBe("FIN-123");
  });
});
