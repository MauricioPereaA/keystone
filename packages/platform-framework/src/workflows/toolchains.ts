/**
 * Per-language small-tests toolchains.
 *
 * The challenge requires DORA metrics to be comparable across Python, Go,
 * Clojure, and TypeScript. The way we keep them comparable is by owning the
 * pipeline SHAPE here and only varying the test toolchain behind one interface:
 * every language runs the same three small-test categories (unit +
 * property-based + api-contract), so "small-tests passed" means the same thing
 * for every team. The `/new-language` skill extends this map — and only this
 * map — to onboard a new stack. It must never add a new metric.
 */

import { Step } from "@github-actions-workflow-ts/lib";
import type { Language } from "./options.js";

export interface Toolchain {
  /** Human-readable language label (used in step names). */
  readonly label: string;
  /** Steps that install the language runtime and project dependencies. */
  setup(): Step[];
  /**
   * The small-tests steps: unit + property-based + api-contract.
   * Same three categories for every language — that is the comparability rule.
   */
  smallTests(): Step[];
}

export const LANGUAGE_TOOLCHAINS: Record<Language, Toolchain> = {
  python: {
    label: "Python",
    // uv is already set up by the job's devex (conventions gate) step, so we only
    // install dependencies here — no duplicate setup-uv.
    setup: () => [new Step({ name: "Install dependencies", run: "uv sync --extra dev" })],
    smallTests: () => [
      new Step({ name: "Unit + property-based tests", run: "uv run pytest -q" }),
      // schemathesis generates API-contract cases from the OpenAPI schema and
      // pairs with Hypothesis (see .claude/rules/testing-conventions.md).
      new Step({ name: "API contract tests", run: "uv run schemathesis run --checks all openapi.json" }),
    ],
  },
  typescript: {
    label: "TypeScript",
    setup: () => [
      new Step({ name: "Set up pnpm", uses: "pnpm/action-setup@v4" }),
      new Step({ name: "Set up Node", uses: "actions/setup-node@v4", with: { "node-version": "20", cache: "pnpm" } }),
      new Step({ name: "Install dependencies", run: "pnpm install --frozen-lockfile" }),
    ],
    smallTests: () => [
      new Step({ name: "Unit + property-based tests", run: "pnpm test" }),
      new Step({ name: "API contract tests", run: "pnpm run test:contract" }),
    ],
  },
  go: {
    label: "Go",
    setup: () => [
      new Step({ name: "Set up Go", uses: "actions/setup-go@v5", with: { "go-version": "1.22" } }),
      new Step({ name: "Download modules", run: "go mod download" }),
    ],
    smallTests: () => [
      new Step({ name: "Unit + property-based tests", run: "go test ./..." }),
      new Step({ name: "API contract tests", run: "go test -run Contract ./..." }),
    ],
  },
  clojure: {
    label: "Clojure",
    setup: () => [
      new Step({ name: "Set up Java", uses: "actions/setup-java@v4", with: { distribution: "temurin", "java-version": "21" } }),
      new Step({ name: "Set up Clojure", uses: "DeLaGuardo/setup-clojure@13.0", with: { lein: "latest" } }),
    ],
    smallTests: () => [
      new Step({ name: "Unit + property-based tests", run: "lein test" }),
      new Step({ name: "API contract tests", run: "lein test :contract" }),
    ],
  },
};
