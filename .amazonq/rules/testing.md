# Testing (Amazon Q review rules)

Distilled from `docs/engineering-rules/testing-conventions.md`. Flag any PR that:

- **Adds/changes a validator without a property-based test.** The CLI validators
  must have Hypothesis PBT — assert a property over generated inputs, not just a few
  examples.
- **Changes the workflow generator without asserting the telemetry step.** Every
  generated deploy job must contain the framework-emitted telemetry step (the DORA
  comparability guarantee) — keep the snapshot/assertion that proves it.
- **Adds a CDK construct without `Template.fromStack` assertions** (Lambda + REST API
  + retention-enforced LogGroup) or a cdk-nag-clean assertion.
- **Fixes a bug without a regression test** that fails on the unfixed code.
- **Drops CLI coverage below the 80% floor.**
