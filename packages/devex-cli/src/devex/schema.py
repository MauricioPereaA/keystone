"""Pydantic schema for conventions.json — the single source of truth.

Validating the source on load (rather than trusting it) means a malformed or
corrupted conventions file fails fast with a clear message instead of silently
weakening every team's checks at once (see .claude/rules/security.md §6 and
error-handling.md §CLI 3). Regex fields are compiled during validation, so a
broken pattern is caught here, not at the first validation call.
"""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, ValidationError


class ConventionsError(Exception):
    """Raised when conventions.json is missing, unparseable, or schema-invalid."""


def _compile_regex(value: str) -> str:
    try:
        re.compile(value)
    except re.error as exc:
        raise ValueError(f"invalid regex pattern: {exc!s}") from exc
    return value


#: A string that must compile as a regular expression.
RegexStr = Annotated[str, AfterValidator(_compile_regex)]


class _Model(BaseModel):
    model_config = ConfigDict(extra="ignore")


class WorkId(_Model):
    pattern: RegexStr
    examples: list[str] = []
    description: str = ""


class Branch(_Model):
    pattern: RegexStr
    examples: list[str] = []
    protected: list[str] = []
    description: str = ""


class Commit(_Model):
    pattern: RegexStr
    examples: list[str] = []
    subjectMaxLength: int = 72
    description: str = ""


class PullRequest(_Model):
    titlePattern: RegexStr
    examples: list[str] = []
    minReviewers: int = 2
    requireTemplate: bool = True
    description: str = ""


class PrPipeline(_Model):
    triggers: list[str]
    stages: list[str]
    smallTests: list[str]


class IntegrationPipeline(_Model):
    triggers: list[str]
    stages: list[str]


class Pipelines(_Model):
    prPipeline: PrPipeline
    integrationPipeline: IntegrationPipeline
    environments: list[str]


class Telemetry(_Model):
    schemaVersion: str
    events: list[str]
    doraMetrics: list[str]
    requiredFields: list[str]
    description: str = ""


class Conventions(_Model):
    """The full conventions.json contract."""

    workId: WorkId
    branch: Branch
    commit: Commit
    pullRequest: PullRequest
    pipelines: Pipelines
    telemetry: Telemetry


def validate_conventions(data: dict) -> Conventions:
    """Validate a parsed conventions dict, raising ConventionsError on any violation."""
    try:
        return Conventions.model_validate(data)
    except ValidationError as exc:
        raise ConventionsError(str(exc)) from exc
