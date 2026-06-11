/**
 * Per-language small-tests toolchains.
 *
 * The challenge requires DORA metrics to be comparable across Python, Go,
 * Clojure, and TypeScript. The way we keep them comparable is by owning the
 * pipeline SHAPE here and only varying the test toolchain behind one interface:
 * every language runs the same three small-test categories (unit +
 * property-based + api-contract), so "small-tests passed" means the same thing
 * for every team. The new-language runbook extends this map — and only this
 * map — to onboard a new stack. It must never add a new metric.
 */
import { Step } from "@github-actions-workflow-ts/lib";
import type { Language } from "./options.js";
/** Per-service knobs a toolchain may honor (threaded from the generator options). */
export interface ToolchainContext {
    /** OpenAPI spec path for the contract step; omitted = runtime auto-detect. */
    readonly apiSpec?: string;
}
export interface Toolchain {
    /** Human-readable language label (used in step names). */
    readonly label: string;
    /** Steps that install the language runtime and project dependencies. */
    setup(): Step[];
    /**
     * The small-tests steps: unit + property-based + api-contract.
     * Same three categories for every language — that is the comparability rule.
     */
    smallTests(ctx: ToolchainContext): Step[];
}
/** Generation-time guard for the apiSpec option (keystone.json is untrusted input). */
export declare function assertValidApiSpec(apiSpec: unknown): void;
export declare const LANGUAGE_TOOLCHAINS: Record<Language, Toolchain>;
