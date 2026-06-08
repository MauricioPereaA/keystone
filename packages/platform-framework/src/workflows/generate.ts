/**
 * `generate:workflows` entrypoint — writes the golden-path pipelines as YAML.
 *
 * Run via `pnpm --filter @keystone/platform generate:workflows [outDir]`
 * (tsx). `devex init` shells out to this so a freshly bootstrapped service gets
 * its PR + Integration pipelines without hand-writing any YAML.
 *
 * Config via env: KEYSTONE_REPO (owner/name), KEYSTONE_LANGUAGE (python|go|
 * clojure|typescript). Defaults target this repo as a Python reference service.
 */

import { mkdirSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { generateIntegrationPipeline } from "./integration-pipeline.js";
import type { Language } from "./options.js";
import { generatePrPipeline } from "./pr-pipeline.js";
import { workflowToYaml } from "./serialize.js";

const outDir = resolve(process.argv[2] ?? ".github/workflows");
const repo = process.env.KEYSTONE_REPO ?? "MauricioPereaA/keystone";
const language = (process.env.KEYSTONE_LANGUAGE ?? "python") as Language;

mkdirSync(outDir, { recursive: true });

const workflows = [
  generatePrPipeline({ repo, language }),
  generateIntegrationPipeline({ repo, language }),
];

for (const workflow of workflows) {
  const file = join(outDir, `${workflow.filename}.yml`);
  writeFileSync(file, workflowToYaml(workflow), "utf8");
  process.stdout.write(`generated ${file}\n`);
}
