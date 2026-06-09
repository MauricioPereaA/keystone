import { App, Aspects, Stack } from "aws-cdk-lib";
import { Annotations, Match, Template } from "aws-cdk-lib/assertions";
import { AwsSolutionsChecks } from "cdk-nag";
import { describe, expect, it } from "vitest";
import { GoldenService } from "./golden-service.js";

function buildStack(): Stack {
  const app = new App();
  const stack = new Stack(app, "TestStack", { env: { account: "123456789012", region: "us-east-1" } });
  new GoldenService(stack, "Svc", { serviceName: "transactionify", env: "sandbox" });
  return stack;
}

describe("GoldenService construct", () => {
  it("provisions a Lambda behind a REST API Gateway", () => {
    const t = Template.fromStack(buildStack());
    t.resourceCountIs("AWS::Lambda::Function", 1);
    t.resourceCountIs("AWS::ApiGateway::RestApi", 1);
  });

  it("enforces retention on EVERY log group (no infinite-retention cost leak)", () => {
    const t = Template.fromStack(buildStack());
    const groups = t.findResources("AWS::Logs::LogGroup");
    // telemetry sink + Lambda log group + API access log group.
    expect(Object.keys(groups).length).toBeGreaterThanOrEqual(3);
    for (const group of Object.values(groups)) {
      expect(group.Properties?.RetentionInDays).toBeDefined();
    }
  });

  it("provisions the DORA/telemetry log group with the standard name + retention", () => {
    const t = Template.fromStack(buildStack());
    t.hasResourceProperties("AWS::Logs::LogGroup", {
      LogGroupName: "/keystone/transactionify/dora",
      RetentionInDays: 30,
    });
  });

  it("tags everything project=keystone + service + env (cost attribution)", () => {
    const t = Template.fromStack(buildStack());
    // Assert each tag independently — arrayWith matches an in-order subsequence,
    // and CDK emits tags sorted alphabetically.
    for (const tag of [
      { Key: "project", Value: "keystone" },
      { Key: "service", Value: "transactionify" },
      { Key: "env", Value: "sandbox" },
    ]) {
      t.hasResourceProperties("AWS::Lambda::Function", { Tags: Match.arrayWith([tag]) });
    }
  });

  it("enables API Gateway access logging (cdk-nag APIG1)", () => {
    const t = Template.fromStack(buildStack());
    t.hasResourceProperties("AWS::ApiGateway::Stage", {
      AccessLogSetting: Match.objectLike({ DestinationArn: Match.anyValue() }),
    });
  });

  it("ships cdk-nag (AwsSolutionsChecks) clean — a passing baseline for consumers", () => {
    const stack = buildStack();
    Aspects.of(stack).add(new AwsSolutionsChecks({ verbose: true }));
    const errors = Annotations.fromStack(stack).findError("*", Match.stringLikeRegexp("AwsSolutions-.*"));
    expect(errors).toHaveLength(0);
  });
});
