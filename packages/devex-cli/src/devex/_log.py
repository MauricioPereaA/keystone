"""Minimal structured logger — the project logger helper the rules assume exists.

Emits ``<LEVEL> <event.name> key=value …`` to STDERR. stdout is reserved for
user-facing Rich output and machine-readable command output (e.g. ``devex workid``);
diagnostics never pollute it. Event names are dotted/lowercase and context is
key=value, per docs/engineering-rules/logging-discipline.md §B. Every caught error logs
through this instead of being swallowed (boundaries.md §7, error-handling.md §9).
"""

from __future__ import annotations

import logging
import sys

_logger = logging.getLogger("devex")
if not _logger.handlers:
    _handler = logging.StreamHandler(sys.stderr)
    _handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    _logger.addHandler(_handler)
    _logger.setLevel(logging.WARNING)


def _format(event: str, fields: dict[str, object]) -> str:
    return " ".join([event, *(f"{key}={value}" for key, value in fields.items())])


class StructuredLogger:
    """A tiny structlog-style facade over the stdlib logger."""

    def debug(self, event: str, **fields: object) -> None:
        _logger.debug(_format(event, fields))

    def info(self, event: str, **fields: object) -> None:
        _logger.info(_format(event, fields))

    def warning(self, event: str, **fields: object) -> None:
        _logger.warning(_format(event, fields))

    def error(self, event: str, **fields: object) -> None:
        _logger.error(_format(event, fields))

    def critical(self, event: str, **fields: object) -> None:
        _logger.critical(_format(event, fields))


log = StructuredLogger()
