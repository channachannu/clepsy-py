"""Internal HTTP transport for clepsy.

This is the only module in the package that imports `requests` or
knows about HTTP status codes. Every other module works with plain
Python objects and clepsy exceptions. If the transport ever needs to
change (e.g. requests -> httpx, or adding retries), this is the only
file that should need to change.
"""

from __future__ import annotations

from typing import Any

import requests

from .exceptions import (
    AuthenticationFailedError,
    ClepsyAuthError,
    ClepsyConnectionError,
    ClepsyError,
    UserAlreadyExistsError,
    ValidationError,
)

DEFAULT_TIMEOUT_SECONDS = 10


class HttpClient:
    """Thin wrapper around `requests` that speaks clepsy exceptions."""

    def __init__(self, base_url: str, api_key: str, timeout: int = DEFAULT_TIMEOUT_SECONDS):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(
            {
                "X-API-Key": api_key,
                "Content-Type": "application/json",
            }
        )

    def post(self, path: str, json_body: dict[str, Any]) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        try:
            response = self._session.post(url, json=json_body, timeout=self._timeout)
        except requests.Timeout as exc:
            raise ClepsyConnectionError(f"Request to {path} timed out") from exc
        except requests.ConnectionError as exc:
            raise ClepsyConnectionError(f"Could not reach DAF at {self._base_url}") from exc
        except requests.RequestException as exc:
            raise ClepsyConnectionError(f"Unexpected transport error calling {path}") from exc

        return self._handle_response(response)

    def get(self, path: str) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        try:
            response = self._session.get(url, timeout=self._timeout)
        except requests.Timeout as exc:
            raise ClepsyConnectionError(f"Request to {path} timed out") from exc
        except requests.ConnectionError as exc:
            raise ClepsyConnectionError(f"Could not reach DAF at {self._base_url}") from exc
        except requests.RequestException as exc:
            raise ClepsyConnectionError(f"Unexpected transport error calling {path}") from exc

        return self._handle_response(response)

    @staticmethod
    def _handle_response(response: requests.Response) -> dict[str, Any]:
        if response.status_code in (200, 201):
            try:
                return response.json()
            except ValueError as exc:
                raise ClepsyConnectionError("DAF returned a non-JSON response") from exc

        # Try to pull a message out of the body, but don't fail if it's not JSON.
        detail = None
        try:
            detail = response.json().get("detail")
        except ValueError:
            pass

        if response.status_code == 401:
            # Ambiguous by design on the server (project key vs. user creds),
            # so we disambiguate using the endpoint's known semantics at the
            # call site (see client.py) rather than here.
            raise AuthenticationFailedError(detail or "Invalid credentials.")
        if response.status_code == 403:
            raise ClepsyAuthError(detail or "Invalid or missing API key.")
        if response.status_code == 409:
            raise UserAlreadyExistsError(detail or "Username already exists.")
        if response.status_code == 422:
            raise ValidationError(detail or "Invalid request.")
        if response.status_code >= 500:
            raise ClepsyConnectionError(detail or f"DAF returned {response.status_code}")

        raise ClepsyError(detail or f"Unexpected response: {response.status_code}")

    def close(self) -> None:
        """Close the underlying requests.Session and release its connections."""
        self._session.close()
