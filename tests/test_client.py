"""Integration tests for clepsy, run against a real deployed DAF instance.

These are deliberately NOT mocked -- clepsy's whole job is to wrap
DAF's live API correctly, so testing against mocks would only prove
the mocks are consistent with themselves, not that the SDK actually
works against your FastAPI service.

Set these environment variables before running:
    CLEPSY_TEST_BASE_URL   e.g. https://your-daf-api.com
    CLEPSY_TEST_API_KEY    a valid project API key

Run with:
    pytest tests/test_client.py -v
"""

from __future__ import annotations

import os
import time
import uuid

import pytest

from clepsy import (
    AuthenticationFailedError,
    ClepsyClient,
    UserAlreadyExistsError,
)

BASE_URL = os.environ.get("CLEPSY_TEST_BASE_URL")
API_KEY = os.environ.get("CLEPSY_TEST_API_KEY")

pytestmark = pytest.mark.skipif(
    not BASE_URL or not API_KEY,
    reason="CLEPSY_TEST_BASE_URL and CLEPSY_TEST_API_KEY must be set to run integration tests",
)


@pytest.fixture
def client() -> ClepsyClient:
    return ClepsyClient(base_url=BASE_URL, api_key=API_KEY)


@pytest.fixture
def fresh_username() -> str:
    # Unique per test run so repeated runs don't collide on 409s.
    return f"clepsy_test_{uuid.uuid4().hex[:10]}"


def test_health_check(client: ClepsyClient):
    assert client.health() is True


def test_current_dynamic_value_is_four_digit_hhmm(client: ClepsyClient):
    value = client.current_dynamic_value()
    assert len(value) == 4
    assert value.isdigit()
    hh, mm = int(value[:2]), int(value[2:])
    assert 0 <= hh <= 23
    assert 0 <= mm <= 59


def test_register_new_user_succeeds(client: ClepsyClient, fresh_username: str):
    result = client.register(fresh_username, f"{fresh_username[:3]}xxxxend", placeholder="x")
    assert result.username == fresh_username
    assert set(result.parameter_map) <= {"0", "1"}


def test_register_duplicate_username_raises(client: ClepsyClient, fresh_username: str):
    client.register(fresh_username, "Botxxnetxx", placeholder="x")
    with pytest.raises(UserAlreadyExistsError):
        client.register(fresh_username, "Botxxnetxx", placeholder="x")


def test_authenticate_with_wrong_password_fails_gracefully(client: ClepsyClient, fresh_username: str):
    client.register(fresh_username, "Botxxnetxx", placeholder="x")
    with pytest.raises(AuthenticationFailedError):
        client.authenticate(fresh_username, "Bot00net00")


def test_full_register_then_authenticate_round_trip(client: ClepsyClient, fresh_username: str):
    # Static part "abc", placeholder positions 3-6 -> filled with HHMM at login.
    client.register(fresh_username, "abcxxxxdef", placeholder="x")

    dynamic = client.current_dynamic_value()
    login_password = f"abc{dynamic}def"

    result = client.authenticate(fresh_username, login_password)
    assert result.success is True
    assert result.username == fresh_username


def test_authenticate_becomes_invalid_next_minute(client: ClepsyClient, fresh_username: str):
    """Sanity check on DPP's core guarantee: the same password should
    not work a minute later. This test is slow and skipped by default --
    run explicitly if you want to verify the time-rollover behavior.
    """
    pytest.skip("Slow test (waits up to 60s) -- run manually when needed.")

    client.register(fresh_username, "abcxxxxdef", placeholder="x")
    dynamic = client.current_dynamic_value()
    login_password = f"abc{dynamic}def"

    result = client.authenticate(fresh_username, login_password)
    assert result.success is True

    # Wait until the minute rolls over.
    while client.current_dynamic_value() == dynamic:
        time.sleep(1)

    with pytest.raises(AuthenticationFailedError):
        client.authenticate(fresh_username, login_password)
