import os
from datetime import timedelta, datetime, UTC
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest
from freezegun import freeze_time

from salary_tracker.domain.auth.repositories import IRefreshTokenRepository
from salary_tracker.domain.auth.impl.token.token_service import TokenService


@pytest.fixture
def private_key():
    return """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDdUX2fy9j7884Q
r45U/LxbhMTbEpEdtllbVdDHPQFhgZCTZ0J09A4B98D9nwFdzX5reN8OvGV4/ms+
SYyUgBSGZ/6cvUGjWRjrJrW/ixEpeawFFa9vvvwjuZCVT4QDrxCFTmbLQ1heirs+
L+VhgUu749V6UJFL2crhpnvEp5YtsEjASHam3ZlqkxzgB04l3rMtTCs6UdkbXEfn
uoJNqvfqr0Q1THO+kJBadlWL753XNCHO6ZAm4ai/ucglmH2hiEQx3F0UTbbB5eHH
D+6xl1U+dgPfITt/yf5MtxodrKBM2LQRW03IC7Xrh7PNQCxNsbKTPSf5MNq/eiEA
Kwbj1senAgMBAAECggEAOdN2et+UuLQJleOA0WTdxB3LH6BYyUYhT9N6wuwGJddo
EpOK0isIU+xLgRjgDwXHr8X7pgqEitoS5EnsUMqsUjfu1z493bPEZoCNQVhRKiCP
2R5C4fQpRh5QkCqgCCRgMSx8gER+3OjrpoJ2MQVK5/NODnDpncNwlofc09Oj0hi+
aNLXsH3lH5/H3gMlciR8rgcwZft4Fjzba21k+iQOfA3g5UdJ8YE5iAqfVNUCy0t1
16DyMQ7z9aBQVhRP1QVRDcNdx/IPXITsCtKjZr05gvORq6OTTwF+cyKYknvWQUJl
n2eAEdl0bRMqhzfRsL6Ca6fP1y2/MIM7LXFXkmE29QKBgQDyo2OzaTPIfIjkdAmO
wAGZyrHqXGI/Hz3jc/o+mdIKUAaLUdkvSy9vHNkCRVJ+f33zVwfWXuBYqVTPsY5G
q0sZD2VoCBC/tMHDcuy0Cfef6G909zkl01PD+1lM5+dCP1aSHz6BeJrlzQxnfec+
84yYQJ6JCWRkuW8rCITXrRN6rQKBgQDpgYrKxVIBG0uwART+8IFnmNQ1gJD87+16
/D/QSzfBZvSvXONacg+wIX+VcE4GxHK/HDuMndnQaVWI9MgNyLSxwK0wPvlc8X5w
dDm9pJZLHp5xb5dPN0FOAV38QdZPVTUQ5eOL79sqKALR+0bxg8sR9o1+1M4EkAMW
MKGxEXNKIwKBgQDNULTs+/h1jevIZOgxgwfXu00Ro1r/TtBvx5PZpQ+26kCfY4ME
Ifrhaue2pDJKGFfbsalQHLh6Tc8WcIiUBB5n9j846JpDnhDX8keZkVWYWnb14rzY
5RncnLPT/+gQhsganZWmuQdZrUjxyfgDrNMrgoKkMu5gzQjkwTCn0CzLgQKBgCKB
31Xp5R1+wCepcUXfmvAJWMrzTfnjJxA2uON6SioNoflMW9jg5EqeGLGn4BAF9gMi
E/bK2QaAmoBb1DidQX7HP5DSrZ07nvjVZDcPXJqLUtTmrdCqFL+HWjFONXKR3/64
SnFCp/vJ3+jSHoDQfjEQY4arwipQcfRUiYCWWJhLAoGAc9X5yMAOTUwVxUDMatXl
VAVDKu8BWK92ipdBrdD+BgUCXnbaFAssQ85v6g3xQtIE/r734VWgwZgkTz2c8dkZ
/0wj3TnlIlXWKp0BcHmYcDrO2/G/CLM08mde3DuI5zQCAG3B3PkzkQa0G3SQCSaX
ADl0uFyaocDR6NQ7QZgP3xI=
-----END PRIVATE KEY-----"""


@pytest.fixture
def user_uuid():
    return UUID("3ed2c45d-7f27-4611-b718-9105517a175a")


@pytest.fixture
def valid_access_token():
    return "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzZWQyYzQ1ZC03ZjI3LTQ2MTEtYjcxOC05MTA1NTE3YTE3NWEiLCJpYXQiOjE3MjcxMDI3NDAsImV4cCI6MTcyNzE4OTE0MCwianRpIjoiYzhlZTYzMDUtMTNiMC00ZjA5LTk5MWYtNGQxZWUyY2QyOTlhIiwiYXVkIjoiaHR0cDovL2xvY2FsaG9zdCIsImlzcyI6Imh0dHA6Ly9sb2NhbGhvc3QifQ.2vmakjF6-RaF4dNrY8w5Hk8Aw0enNU-23H98nYaVpdxejwxYKmEw9lnjvOjmKjVXb5JfPII1aFf7L4DkCZAddB13ZD09F2T8JDPotd77n5JEY3g2uBpDX0nTGHeAWO9f5ve5GqtetCFNYwtZCLOTKLzrs9OCFX5CWh1XjReFnTU-cGNM_ZfJU2nkNJQxp5frpgLhByVYpyY15yI33fTOraoo2EXhEHJqFqyZtkQQdYGKFHRBbnDckjaTLGQ--rc5ntIzCZAHA8B0CI6niMYI-dbp1LFfO6yl73HpMtiVq9F13yXGzHf0RDNDworQCj4ziccu6KcGIsjeWsiOoadXcQ"

@pytest.fixture
def token_expiration_time():
    return datetime(2024, 9, 24, 14, 45, 40, tzinfo=UTC)

@pytest.fixture
def access_token_expiration_time():
    return timedelta(minutes=30)


@pytest.fixture
def access_token_issuer():
    return "http://localhost"


@pytest.fixture
def access_token_audience():
    return "http://localhost"


@pytest.fixture
def refresh_token_expiration_time():
    return timedelta(days=30)


@pytest.fixture
def refresh_token_repository():
    return AsyncMock(IRefreshTokenRepository)


@pytest.fixture
def token_service(private_key, access_token_expiration_time, refresh_token_expiration_time, refresh_token_repository,
                  access_token_audience, access_token_issuer):
    return TokenService(
        access_token_private_key=private_key,
        access_token_expiration_time=access_token_expiration_time,
        access_token_issuer=access_token_issuer,
        access_token_audience=access_token_audience,
        refresh_token_expiration_time=refresh_token_expiration_time,
        refresh_token_repository=refresh_token_repository
    )


@freeze_time(datetime(2024, 9, 23, 14, 50, tzinfo=UTC))
async def test_validate_access_token_valid(
        token_service,
        user_uuid,
        valid_access_token,
        token_expiration_time
):
    token = await token_service.validate_access_token(valid_access_token)

    assert token is not None
    assert token.user_uuid == user_uuid
    assert token.token == valid_access_token
    assert token.expires_at == token_expiration_time


@freeze_time(datetime(2025, 9, 23, 14, 50, tzinfo=UTC))
async def test_validate_access_token_expired(
        token_service,
        valid_access_token,
        user_uuid,
        access_token_expiration_time
):
    token = await token_service.validate_access_token(valid_access_token)

    assert token is None


@freeze_time(datetime(2021, 1, 1))
async def test_validate_access_token_invalid(
        token_service,
        user_uuid,
        access_token_expiration_time
):
    token = await token_service.validate_access_token("Invalid")

    assert token is None


async def test_validate_refresh_token(
        token_service,
        refresh_token_repository
):
    refresh_token = MagicMock()

    refresh_token_repository.get_by_token.return_value = refresh_token

    result = await token_service.validate_refresh_token("Test Token")

    assert result == refresh_token
    refresh_token_repository.get_by_token.assert_awaited_once_with("Test Token")


@freeze_time(datetime(2021, 1, 1))
async def test_create_token_pair(
        token_service,
        user_uuid,
        access_token_expiration_time,
        refresh_token_expiration_time
):
    token_pair = await token_service.create_token_pair(user_uuid, "Test User Agent")

    assert token_pair.access_token.user_uuid == user_uuid
    assert token_pair.access_token.token is not None
    assert token_pair.access_token.expires_at == datetime(2021, 1, 1, tzinfo=UTC) + access_token_expiration_time
    assert token_pair.refresh_token.user_uuid == user_uuid
    assert token_pair.refresh_token.token is not None
    assert token_pair.refresh_token.user_agent == "Test User Agent"
    assert token_pair.refresh_token.expires_at == datetime(2021, 1, 1, tzinfo=UTC) + refresh_token_expiration_time


async def test_save_refresh_token(
        token_service,
        refresh_token_repository
):
    refresh_token = MagicMock()

    await token_service.save_refresh_token(refresh_token)

    refresh_token_repository.upsert.assert_awaited_once_with(refresh_token)

    e = os.environ.get("DATABASE_URL")
    pass


async def test_delete_refresh_token(
        token_service,
        refresh_token_repository
):
    await token_service.delete_refresh_token("Test Token")

    refresh_token_repository.delete.assert_awaited_once_with("Test Token")
