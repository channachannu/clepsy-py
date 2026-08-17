"""ClepsyClient -- the public entry point of the clepsy SDK.

Example:
    from clepsy import ClepsyClient

    client = ClepsyClient(base_url="https://your-daf-api.com", api_key="daf_c_xxxxx")

    client.register("Botnet", "Botxxnetxx", placeholder="x")
    result = client.authenticate("Botnet", "Bot" + client.current_dynamic_value() + "net32")
    if result.success:
        ...
"""

from __future__ import annotations

from datetime import datetime, timezone

from ._http import HttpClient
from .exceptions import ClepsyAuthError
from .models import AuthResult, RegisterResult


class ClepsyClient:
    """Client for a deployed Dynamic Auth Framework (DAF) instance.

    This client never computes hashes, parameter maps, or performs any
    part of the DPP algorithm locally -- it is a thin wrapper over
    DAF's HTTP API, so that identity always stays centralized in the
    one DAF service, even across multiple consuming projects.
    """

    def __init__(self, base_url: str, api_key: str, timeout: int = 10):
        if not api_key:
            raise ClepsyAuthError("An api_key is required to use clepsy.")
        self._http = HttpClient(base_url=base_url, api_key=api_key, timeout=timeout)

    def register(self, username: str, password: str, placeholder: str = "x") -> RegisterResult:
        """Register a new user with DAF.

        `password` is the full pattern (e.g. "Botxxnetxx") -- static
        characters plus placeholder characters marking where the live
        time value will go at login.
        """
        body = self._http.post(
            "/v1/auth/register",
            json_body={"username": username, "password": password, "placeholder": placeholder},
        )
        return RegisterResult(
            username=body["username"],
            parameter_map=body["parameter_map"],
        )

    def authenticate(self, username: str, password: str) -> AuthResult:
        """Authenticate a user with DAF.

        `password` is the fully-formed login password with the current
        dynamic value already filled in (e.g. "Bot21net30"). Use
        `current_dynamic_value()` to build this string.
        """
        body = self._http.post(
            "/v1/auth/authenticate",
            json_body={"username": username, "password": password},
        )
        return AuthResult(
            success=body.get("success", False),
            username=body.get("username", username),
            message=body.get("message", ""),
        )

    def current_dynamic_value(self) -> str:
        """Return the current UTC time as an HHMM string.

        This mirrors DAF's own server-side parameter calculation, so
        that any project embedding clepsy doesn't have to reimplement
        (and potentially get wrong) the UTC-now-as-HHMM logic itself.
        """
        return datetime.now(timezone.utc).strftime("%H%M")

    def health(self) -> bool:
        """Check whether the DAF service is reachable and healthy."""
        try:
            self._http.get("/v1/auth/health")
            return True
        except Exception:
            return False
