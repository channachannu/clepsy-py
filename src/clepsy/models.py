"""Public data contracts returned by ClepsyClient.

These are plain dataclasses, not raw dicts or booleans, specifically so
new fields (e.g. a future `token` on AuthResult) can be added without
breaking existing callers.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterResult:
    """Returned by ClepsyClient.register() on success."""

    username: str
    parameter_map: str


@dataclass(frozen=True)
class AuthResult:
    """Returned by ClepsyClient.authenticate() on success.

    `success` is kept as a plain bool for v0.1 so callers can do
    `if result.success:`. A `token` field is expected to be added in a
    later version once DAF issues signed session tokens -- that will be
    additive, not a breaking change, because callers are already going
    through this object rather than a raw bool.
    """

    success: bool
    username: str
    message: str
