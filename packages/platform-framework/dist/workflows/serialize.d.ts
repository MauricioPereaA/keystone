/**
 * Serialize a typed {@link Workflow} to GitHub Actions YAML.
 *
 * Uses the `yaml` package (YAML 1.2 core schema), so the workflow trigger key
 * `on` is preserved as a string key rather than being coerced to the boolean
 * `true` (the classic YAML 1.1 footgun that bites js-yaml users).
 */
import type { Workflow } from "@github-actions-workflow-ts/lib";
export declare function workflowToYaml(workflow: Workflow): string;
