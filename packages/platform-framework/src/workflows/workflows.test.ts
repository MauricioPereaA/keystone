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
    expect(workflowToYaml(generatePrPipeline({ repo: "x", language: "python" }))).toContain("uv run pytest");
    expect(workflowToYaml(generatePrPipeline({ repo: "x", language: "typescript" }))).toContain("pnpm test");
    expect(workflowToYaml(generatePrPipeline({ repo: "x", language: "go" }))).toContain("go test");
    expect(workflowToYaml(generatePrPipeline({ repo: "x", language: "clojure" }))).toContain("lein test");
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
});
