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
export {};
