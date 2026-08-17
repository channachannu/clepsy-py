"""Exception hierarchy for the clepsy client.

Every failure the SDK can raise inherits from ClepsyError, so callers
who don't care about the distinction can catch just that one type.
Callers who do care can catch the specific subclass.

    try:
        result = client.authenticate(username, password)
    except AuthenticationFailedError:
        ...  # wrong username/password
    except ClepsyConnectionError:
        ...  # network / DAF unreachable
    except ClepsyError:
        ...  # anything else
"""

from __future__ import annotations


class ClepsyError(Exception):
    """Base class for all errors raised by clepsy."""


class ClepsyConnectionError(ClepsyError):
    """Raised when the DAF service can't be reached (network, timeout, 5xx)."""


class ClepsyAuthError(ClepsyError):
    """Raised when the *project's* API key is missing or invalid.

    This is distinct from a user's login failing -- it means clepsy
    itself isn't authorized to talk to DAF.
    """


class AuthenticationFailedError(ClepsyError):
    """Raised when a user's username/password (dynamic + static) is invalid.

    Deliberately generic, mirroring DAF's own generic 401 response, so
    the SDK never leaks which stage (dynamic vs. static) failed.
    """


class UserAlreadyExistsError(ClepsyError):
    """Raised on register() when the username is already taken."""


class ValidationError(ClepsyError):
    """Raised on malformed input (empty password, no static characters, etc.)."""
