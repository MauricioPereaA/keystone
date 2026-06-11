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
/**
 * Spec filenames the generated contract step probes at the repo root, in order.
 * Real services name the file either way (Transactionify ships `openapi.yaml`);
 * the golden path adopts them as-is instead of forcing a rename.
 */
const OPENAPI_SPEC_CANDIDATES = ["openapi.yaml", "openapi.yml", "openapi.json"];
/**
 * apiSpec lands inside a generated shell line, so anything but a plain relative
 * path (quotes, `$`, backticks, newlines, a leading dash) would break out of —
 * or inject into — the emitted script. Generators fail at build, never emit a
 * broken workflow (error-handling.md), so the guard throws at generation time.
 */
const SAFE_API_SPEC = /^[A-Za-z0-9][A-Za-z0-9._/-]*$/;
/** Generation-time guard for the apiSpec option (keystone.json is untrusted input). */
export function assertValidApiSpec(apiSpec) {
    if (apiSpec === undefined)
        return;
    if (typeof apiSpec !== "string" || !SAFE_API_SPEC.test(apiSpec)) {
        throw new Error(`invalid apiSpec ${JSON.stringify(apiSpec)} — expected a plain relative path ` +
            `(${String(SAFE_API_SPEC)}); fix the apiSpec value in keystone.json`);
    }
}
/**
 * API-contract step (python), pre-deploy half: validate the OpenAPI schema
 * itself — server-less, fast, and the only contract check that *can* run before
 * the service exists. Live schemathesis fuzzing against the deployed API runs in
 * the deploy stage, where there is a URL to hit (see testing-conventions.md).
 *
 * The validator is brought by `uvx` (like the devex gate), so a consuming
 * service adds nothing to its own dependencies. With an explicit spec the step
 * verifies the file exists; otherwise it probes the candidates at runtime. Either
 * way a missing spec fails with an actionable message.
 */
const VALIDATE_SCHEMA = (spec) => `uvx --from openapi-spec-validator openapi-spec-validator "${spec}"`;
function pythonApiContractStep(ctx) {
    if (ctx.apiSpec) {
        return new Step({
            name: "API contract: validate OpenAPI schema",
            run: [
                "set -euo pipefail",
                `if [ ! -f "${ctx.apiSpec}" ]; then`,
                `  echo "::error::apiSpec '${ctx.apiSpec}' (from keystone.json) does not exist in the repo"`,
                "  exit 1",
                "fi",
                VALIDATE_SCHEMA(ctx.apiSpec),
            ].join("\n"),
        });
    }
    return new Step({
        name: "API contract: validate OpenAPI schema",
        run: [
            "set -euo pipefail",
            'spec=""',
            `for candidate in ${OPENAPI_SPEC_CANDIDATES.join(" ")}; do`,
            '  if [ -f "$candidate" ]; then',
            '    spec="$candidate"',
            "    break",
            "  fi",
            "done",
            'if [ -z "$spec" ]; then',
            `  echo "::error::no OpenAPI spec found (${OPENAPI_SPEC_CANDIDATES.join(", ")}) — add one at the repo root or set apiSpec in keystone.json"`,
            "  exit 1",
            "fi",
            VALIDATE_SCHEMA("$spec"),
        ].join("\n"),
    });
}
export const LANGUAGE_TOOLCHAINS = {
    python: {
        label: "Python",
        // uv is already set up by the job's devex (conventions gate) step. uv is a
        // drop-in for pip, so the golden path adopts both uv-native (pyproject.toml)
        // AND pip-based (requirements.txt) services without forcing a migration.
        setup: () => [
            new Step({
                name: "Install dependencies",
                run: [
                    "set -euo pipefail",
                    "if [ -f pyproject.toml ]; then",
                    "  uv sync --extra dev",
                    "else",
                    "  uv venv",
                    "  # uv pip install auto-targets the .venv just created — no activation needed (uv != pip).",
                    '  deps_found=""',
                    "  for req in requirements.txt requirements-dev.txt; do",
                    // Explicit `if`, not `[ -f ] && …`: an absent file on the loop's last
                    // iteration would otherwise leave a non-zero status and fail the step.
                    '    if [ -f "$req" ]; then',
                    '      uv pip install -r "$req"',
                    "      deps_found=1",
                    "    fi",
                    "  done",
                    '  if [ -z "$deps_found" ]; then',
                    '    echo "::error::no pyproject.toml, requirements.txt or requirements-dev.txt at the repo root — the python toolchain has nothing to install"',
                    "    exit 1",
                    "  fi",
                    "fi",
                ].join("\n"),
            }),
        ],
        // --no-project so the same command works for the uv-native and the pip venv.
        smallTests: (ctx) => [
            new Step({ name: "Unit + property-based tests", run: "uv run --no-project pytest -q" }),
            pythonApiContractStep(ctx),
        ],
    },
    typescript: {
        label: "TypeScript",
        setup: () => [
            new Step({ name: "Set up pnpm", uses: "pnpm/action-setup@v4" }),
            new Step({ name: "Set up Node", uses: "actions/setup-node@v4", with: { "node-version": "24", cache: "pnpm" } }),
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
