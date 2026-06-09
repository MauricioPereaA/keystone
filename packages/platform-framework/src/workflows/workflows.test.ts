import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { SCHEMA_VERSION } from "../telemetry/index.js";
import { generateIntegrationPipeline } from "./integration-pipeline.js";
import { generatePrPipeline } from "./pr-pipeline.js";
import { workflowToYaml } from "./serialize.js";

type Step = { name?: string; id?: string; uses?: string; run?: string; if?: string | boolean };
type Job = { steps?: Step[]; needs?: string | string[]; permissions?: Record<string, string>; outputs?: Record<string, string> };

const jobsOf = (wf: { workflow: { jobs?: Record<string, Job> } }) => wf.workflow.jobs ?? {};
const deployJobsOf = (wf: { workflow: { jobs?: Record<string, Job> } }) =>
  Object.entries(jobsOf(wf)).filter(([name]) => name.startsWith("deploy-"));
const hasTelemetry = (job: Job) => (job.steps ?? []).some((s) => /Emit DORA telemetry/.test(s.name ?? ""));

describe("PR pipeline generator", () => {
  it("has small-tests then deploy-sandbox, triggered on pull_request", () => {
    const wf = generatePrPipeline({ repo: "acme/svc", language: "python" });
    expect(Object.keys(jobsOf(wf))).toEqual(["small-tests", "deploy-sandbox"]);
    expect((wf.workflow.on as { pull_request?: unknown }).pull_request).toBeDefined();
  });

  it("small-tests runs the three categories plus the devex conventions gate", () => {
    const wf = generatePrPipeline({ repo: "acme/svc", language: "python" });
    const names = (jobsOf(wf)["small-tests"].steps ?? []).map((s) => s.name);
    expect(names).toContain("Validate conventions & resolve Work ID (devex)");
    expect(names).toContain("Unit + property-based tests");
    expect(names).toContain("API contract tests");
  });

  it("injects a telemetry step into EVERY deploy job (comparability guarantee)", () => {
    const wf = generatePrPipeline({ repo: "acme/svc", language: "python", environments: ["sandbox", "staging"] });
    const deploys = deployJobsOf(wf);
    expect(deploys.length).toBe(2);
    for (const [, job] of deploys) expect(hasTelemetry(job)).toBe(true);
  });

  it("authenticates with OIDC and never embeds static AWS keys", () => {
    const yaml = workflowToYaml(generatePrPipeline({ repo: "acme/svc", language: "python" }));
    expect(yaml).toContain("aws-actions/configure-aws-credentials");
    expect(yaml).toContain("id-token: write");
    expect(yaml).not.toMatch(/AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY/);
  });

  it("stamps the telemetry schema version from the contract, not a literal", () => {
    expect(workflowToYaml(generatePrPipeline({ repo: "x", language: "go" }))).toContain(SCHEMA_VERSION);
  });

  it("selects the toolchain per language behind one interface", () => {
    expect(workflowToYaml(generatePrPipeline({ repo: "x", language: "python" }))).toContain("uv run --no-project pytest");
    expect(workflowToYaml(generatePrPipeline({ repo: "x", language: "typescript" }))).toContain("pnpm test");
    expect(workflowToYaml(generatePrPipeline({ repo: "x", language: "go" }))).toContain("go test");
    expect(workflowToYaml(generatePrPipeline({ repo: "x", language: "clojure" }))).toContain("lein test");
  });

  it("python toolchain adopts both uv-native (pyproject) and pip (requirements.txt) services", () => {
    const yaml = workflowToYaml(generatePrPipeline({ repo: "x", language: "python" }));
    expect(yaml).toContain("uv sync --extra dev"); // pyproject path
    expect(yaml).toContain("requirements.txt"); // pip path (uv pip install)
  });

  it("pip install loop is exit-status safe (regression: absent requirements-dev.txt must not fail the step)", () => {
    const yaml = workflowToYaml(generatePrPipeline({ repo: "x", language: "python" }));
    // `[ -f "$req" ] && …` leaves status 1 when the loop's LAST candidate is
    // absent — the common requirements.txt-only service — failing the step.
    expect(yaml).not.toContain('[ -f "$req" ] &&');
    expect(yaml).toContain('if [ -f "$req" ]; then');
    // And an empty venv (nothing to install) fails fast with a clear message.
    expect(yaml).toContain("nothing to install");
  });

  it("api-contract step auto-detects the service's OpenAPI spec at runtime by default", () => {
    const yaml = workflowToYaml(generatePrPipeline({ repo: "x", language: "python" }));
    expect(yaml).toContain("for candidate in openapi.yaml openapi.yml openapi.json");
    expect(yaml).toContain("::error::no OpenAPI spec found");
  });

  it("apiSpec option pins the contract step to the service's real spec", () => {
    const yaml = workflowToYaml(generatePrPipeline({ repo: "x", language: "python", apiSpec: "spec/api.yaml" }));
    expect(yaml).toContain('schemathesis run --checks all "spec/api.yaml"');
    expect(yaml).toContain("does not exist in the repo"); // pinned spec still fail-fast checked
    expect(yaml).not.toContain("for candidate in"); // no detection loop when pinned
  });

  it("rejects an apiSpec that is not a plain relative path (generators fail at build, not in CI)", () => {
    // apiSpec is interpolated into a generated shell line; quotes/$/newlines/
    // leading dashes would break out of it, so generation must throw instead.
    for (const bad of ['x"; touch INJECTED; echo "', "-leading-dash.yaml", "a b.yaml", "a\nb.yaml", "$HOME.yaml"]) {
      expect(() => generatePrPipeline({ repo: "x", language: "python", apiSpec: bad })).toThrow(/apiSpec/);
    }
    // non-string junk from a hand-edited keystone.json is rejected too
    expect(() =>
      generatePrPipeline({ repo: "x", language: "python", apiSpec: {} as unknown as string }),
    ).toThrow(/apiSpec/);
  });

  it("generated multi-line shell steps are explicitly fail-fast (set -euo pipefail)", () => {
    const yaml = workflowToYaml(generatePrPipeline({ repo: "x", language: "python" }));
    expect(yaml).toContain("set -euo pipefail");
  });

  it("matches the serialized YAML snapshot", () => {
    expect(workflowToYaml(generatePrPipeline({ repo: "acme/svc", language: "python" }))).toMatchSnapshot();
  });
});

describe("Integration pipeline generator", () => {
  it("promotes staging -> production then emits metrics, on push to main", () => {
    const wf = generateIntegrationPipeline({ repo: "acme/svc", language: "python" });
    expect(Object.keys(jobsOf(wf))).toEqual(["small-tests", "deploy-staging", "deploy-production", "emit-metrics"]);
    expect((wf.workflow.on as { push?: { branches?: string[] } }).push?.branches).toContain("main");
  });

  it("production deploy gates on staging (promotion order)", () => {
    const wf = generateIntegrationPipeline({ repo: "acme/svc", language: "python" });
    expect(jobsOf(wf)["deploy-production"].needs).toContain("deploy-staging");
  });

  it("every deploy job emits telemetry", () => {
    const wf = generateIntegrationPipeline({ repo: "acme/svc", language: "python" });
    for (const [, job] of deployJobsOf(wf)) expect(hasTelemetry(job)).toBe(true);
  });

  it("emit-metrics reports DORA via the devex CLI", () => {
    const wf = generateIntegrationPipeline({ repo: "acme/svc", language: "python" });
    const runs = (jobsOf(wf)["emit-metrics"].steps ?? []).map((s) => s.run ?? "");
    expect(runs.some((r) => /devex dora/.test(r))).toBe(true);
  });

  it("threads apiSpec into its small-tests job too (mutation guard for the production gate)", () => {
    const yaml = workflowToYaml(generateIntegrationPipeline({ repo: "x", language: "python", apiSpec: "spec/api.yaml" }));
    expect(yaml).toContain('schemathesis run --checks all "spec/api.yaml"');
  });
});

describe("telemetry emit step ↔ conventions contract", () => {
  it("emits every conventions.json telemetry.requiredField (audit/comparability guarantee)", () => {
    const conventions = JSON.parse(
      readFileSync(new URL("../../../../conventions/conventions.json", import.meta.url), "utf8"),
    ) as { telemetry: { requiredFields: string[] } };
    const yaml = workflowToYaml(generatePrPipeline({ repo: "acme/svc", language: "python" }));
    for (const field of conventions.telemetry.requiredFields) {
      expect(yaml).toContain(`--arg ${field} `);
    }
  });
});
