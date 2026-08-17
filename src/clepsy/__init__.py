"""clepsy -- a thin client SDK for the Dynamic Auth Framework (DAF).

    from clepsy import ClepsyClient

    client = ClepsyClient(base_url="https://your-daf-api.com", api_key="daf_c_xxxxx")
    client.register("Botnet", "Botxxnetxx")

clepsy never runs DPP logic locally -- it only talks to your deployed
DAF service, so identity stays centralized across every project that
uses it (this is what makes cross-project login possible).
"""

from .client import ClepsyClient
from .exceptions import (
    AuthenticationFailedError,
    ClepsyAuthError,
    ClepsyConnectionError,
    ClepsyError,
    UserAlreadyExistsError,
    ValidationError,
)
from .models import AuthResult, RegisterResult

__all__ = [
    "ClepsyClient",
    "AuthResult",
    "RegisterResult",
    "ClepsyError",
    "ClepsyConnectionError",
    "ClepsyAuthError",
    "AuthenticationFailedError",
    "UserAlreadyExistsError",
    "ValidationError",
]

__version__ = "0.1.3"
