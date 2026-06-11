/**
 * Reusable AWS CDK constructs (challenge "Option A").
 *
 * Public surface: the GoldenService construct + its props/defaults. Teams consume
 * it instead of hand-wiring Lambda + API Gateway, and inherit the cost guardrails
 * and a cdk-nag-clean baseline. See ./golden-service.ts and docs/engineering-rules/aws-cdk.md.
 */

export * from "./golden-service.js";
