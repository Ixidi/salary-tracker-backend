from datetime import timedelta, datetime, UTC
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from freezegun import freeze_time

from salary_tracker.domain.auth.impl.token.token_service import TokenService
from salary_tracker.domain.auth.models import TokenSettings, AccessToken
from salary_tracker.domain.auth.repositories import IRefreshTokenRepository
from salary_tracker.domain.exceptions import InvalidTokenDomainException
from salary_tracker.domain.user.models import User
from salary_tracker.domain.user.repositories import IUserRepository


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
def token_settings(private_key):
    return TokenSettings(
        access_token_private_key=private_key,
        access_token_expiration_time=timedelta(minutes=3),
        access_token_issuer="test_issuer",
        access_token_audience="test_audience",
        refresh_token_expiration_time=timedelta(days=365),
    )


@pytest.fixture
def refresh_token_repository():
    return AsyncMock(IRefreshTokenRepository)


@pytest.fixture
def user_repository():
    return AsyncMock(IUserRepository)


@pytest.fixture
def token_service(token_settings, user_repository, refresh_token_repository):
    return TokenService(
        token_settings=token_settings,
        user_repository=user_repository,
        refresh_token_repository=refresh_token_repository,
    )


@freeze_time(datetime(2021, 1, 1, 0, 4, tzinfo=UTC))
async def test_validate_access_token_valid(token_service):
    token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjNlNDU2Ny1lODliLTEyZDMtYTQ1Ni00MjY2MTQxNzQwMDAiLCJpYXQiOjE2MDk0NTkyMDAsImV4cCI6MTYwOTQ1OTUwMCwianRpIjoiMzIxZTQ1NjctZTg5Yi0xM2QzLWE0NTYtNDI2NjE0MTc0MDEwIiwiYXVkIjoidGVzdF9hdWRpZW5jZSIsImlzcyI6InRlc3RfaXNzdWVyIn0.UGIpNm590kEG96HfkAXGNdSQ1w4GCJrjax_BhmyzXRVzkITaMHDuBZf04Xaks9Qmv2EeISM2nIBiYrkCikQzMRhG8SLjEHor4SHNQEft8WUtuddqLPRDquN5krn58ZA1HG0asupJdIwML3nYqdLYZ4UIpORpTQeah0cMrJAJMFBWnVOSxIBv5gosx2BVFm3xhGRYzUe-o2xXNKC50uwOIbk9WoMg2IuhtHjRhqWrlyLRhSCSH8AmZ0ZvgS6QAnwSU_DijfZnKqYZUs5SxedXPAndaR_xWJ2yrF_ko5lNUdioJC5B-jRP9sjGZU1A7lF_yTDFjPMo8OycBHLcAL0BSw"

    result = await token_service.validate_access_token(token)

    assert result == AccessToken(
        user_uuid=UUID("123e4567-e89b-12d3-a456-426614174000"),
        token=token,
        expires_at=datetime(2021, 1, 1, 0, 5, tzinfo=UTC),
    )


@pytest.mark.parametrize("token", [
    # expired
    "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjNlNDU2Ny1lODliLTEyZDMtYTQ1Ni00MjY2MTQxNzQwMDAiLCJpYXQiOjE2MDk0NTkyMDAsImV4cCI6MTYwOTQ1OTUwMCwianRpIjoiMzIxZTQ1NjctZTg5Yi0xM2QzLWE0NTYtNDI2NjE0MTc0MDEwIiwiYXVkIjoidGVzdF9hdWRpZW5jZSIsImlzcyI6InRlc3RfaXNzdWVyIn0.UGIpNm590kEG96HfkAXGNdSQ1w4GCJrjax_BhmyzXRVzkITaMHDuBZf04Xaks9Qmv2EeISM2nIBiYrkCikQzMRhG8SLjEHor4SHNQEft8WUtuddqLPRDquN5krn58ZA1HG0asupJdIwML3nYqdLYZ4UIpORpTQeah0cMrJAJMFBWnVOSxIBv5gosx2BVFm3xhGRYzUe-o2xXNKC50uwOIbk9WoMg2IuhtHjRhqWrlyLRhSCSH8AmZ0ZvgS6QAnwSU_DijfZnKqYZUs5SxedXPAndaR_xWJ2yrF_ko5lNUdioJC5B-jRP9sjGZU1A7lF_yTDFjPMo8OycBHLcAL0BSw",
    # invalid issuer
    "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjNlNDU2Ny1lODliLTEyZDMtYTQ1Ni00MjY2MTQxNzQwMDAiLCJpYXQiOjE2MDk0NTkyMDAsImV4cCI6MTYwOTQ1OTUwMCwianRpIjoiMzIxZTQ1NjctZTg5Yi0xM2QzLWE0NTYtNDI2NjE0MTc0MDEwIiwiYXVkIjoidGVzdF9hdWRpZW5jZSIsImlzcyI6ImludmFsaWQifQ.MeL-tHOvBDKCA-k3A06l5XGETKWL5XgmfKkztGtwNXM0NSQagadNmP1i4jQChcGQd5ixxnanhr5hbkCTnUn8IhGmMk51HMpVYQnyCDRIUx7sd6-Sgg0Hux5dRIRpWD53y9Kyu_xheWupBuZJ9STlm5d2zoalRmUOadFcHjcS0P89yaZQyfxml8TeV3VFupvdjTR9XvxslD1tl7SbBb-K0XdyXbd1-o0qjr8gR8_IeU-OESiVJCFEfFc2hYKHdL6R41nJLJKCgmAOg8ZPUYYBkjnXI0PWMiekXFc_-hrRyNlCLrp3mfw1ZtNpUlZ4unFXr2S9hvj-kcea64Ew8N9E8Q",
    # invalid audience
    "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjNlNDU2Ny1lODliLTEyZDMtYTQ1Ni00MjY2MTQxNzQwMDAiLCJpYXQiOjE2MDk0NTkyMDAsImV4cCI6MTYwOTQ1OTUwMCwianRpIjoiMzIxZTQ1NjctZTg5Yi0xM2QzLWE0NTYtNDI2NjE0MTc0MDEwIiwiYXVkIjoiaW52YWxpZCIsImlzcyI6InRlc3RfaXNzdWVyIn0.wKWPdSlc9qhSGVR86R6KkS3vCHdq0TlelH1n3SlQK8TeLGBfIopWNNzoCUpjWcYipzzQuX2dshub9fGDPkdjsHHYwWkNtQIFGQ8zCyugQBSOUIE8o4SIz1NrTu7dMrZiQCHWMEoII_mo8mamG1pp9v5rncrrN3ctqj9K95Tsj0dm5NsqmLXf2eOc45Bdi85xoJcumSm1CHkvvuH0-yFsF6DIdh5Inpe1QSdIqIuUgCdEEpXiGJOqjE15QZh8QzgepxvC7EqkOqOKRCQLo3NO6ND-Qnpxz0KQLvYyW8SCy8bNRyZSr4PLjDNLCjZF14v140vM_-0dGLHo--OP4XligA",
    # invalid signature
    "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjNlNDU2Ny1lODliLTEyZDMtYTQ1Ni00MjY2MTQxNzQwMDAiLCJpYXQiOjE2MDk0ODgwNjAsImV4cCI6MTYwOTQ4ODM2MCwianRpIjoiMzIxZTQ1NjctZTg5Yi0xM2QzLWE0NTYtNDI2NjE0MTc0MDEwIiwiYXVkIjoidGVzdF9hdWRpZW5jZSIsImlzcyI6InRlc3RfaXNzdWVyIn0.Kb0zMvToxHFyUhWwQxxtyGHZfBnZzlofTkKstOMeXmIeYTSWnwwGgm46PzsUcruyG78KJoIyxChuWc6yVD5iLLWvk5_rHvSsBqcKu8M-FYNt452SIYE317RFsXSRBQ0nhfUwjVLM3N4WmcxFwoy3mmC4CLGCDfZnyt4LjwF6j3-o3v7EChqlPj0hMkduRDWFyGXzVpoF8YCmDNDwV66pjVGQzXAbffkmD-EioSOGKjNybqEk0_lviR-9g5t9f2SeBjEi_P87ygC8lfp5hfxL5JfUKiDux1DHvEEwTq7zh0tKXO9jHZUsChh8Il-fIyoQllh_ZiS_3Cv6cyl090WgpQ"
])
@freeze_time(datetime(2021, 1, 1, 0, 8, tzinfo=UTC))
async def test_validate_access_token_invalid(token_service, token):
    with pytest.raises(InvalidTokenDomainException):
        await token_service.validate_access_token(token)


async def test_create_token_pair(token_service, user_repository, refresh_token_repository):
    user_uuid = UUID("123e4567-e89b-12d3-a456-426614174000")
    user_repository.get_by_uuid.return_value = User(
        uuid=user_uuid,
        name="Test User",
        email="email@example.com",
    )