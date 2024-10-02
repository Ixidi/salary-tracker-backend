from datetime import datetime, UTC
from unittest.mock import MagicMock
from uuid import UUID

import pytest

from salary_tracker.domain.auth.models import RefreshToken, AccessToken, TokenPair
from salary_tracker.domain.auth.services import ITokenService
from salary_tracker.api.exceptions import InvalidTokenException


@pytest.fixture
def token_service():
    return MagicMock(ITokenService)

@pytest.fixture
def use_case(token_service):
    from salary_tracker.usecase.auth.rotate_refresh_token import RotateRefreshTokenUseCase
    return RotateRefreshTokenUseCase(
        token_service=token_service
    )

async def test_rotate_refresh_token_success(
        use_case,
        token_service
):
    user_uuid = MagicMock(UUID)
    user_agent = "Test User Agent"
    expires_at = datetime(2022, 1, 1, tzinfo=UTC)
    refresh_token_str = "Test Token"
    refresh_token = RefreshToken(token=refresh_token_str, user_uuid=user_uuid, user_agent="Test User Agent", expires_at=expires_at)
    access_token = AccessToken(token="Test Access Token", user_uuid=user_uuid, expires_at=expires_at)
    new_refresh_token = RefreshToken(token="New Refresh Token", user_uuid=user_uuid, user_agent=user_agent, expires_at=expires_at)
    new_token_pair = TokenPair(
        access_token=access_token,
        refresh_token=new_refresh_token
    )

    token_service.validate_refresh_token.return_value = refresh_token
    token_service.create_token_pair.return_value = new_token_pair

    result = await use_case(refresh_token_str, user_agent)

    assert result == new_token_pair
    token_service.create_token_pair.assert_awaited_once_with(user_uuid, user_agent)
    token_service.validate_refresh_token.assert_awaited_once_with(refresh_token_str)
    token_service.delete_refresh_token.assert_awaited_once_with(refresh_token_str)
    token_service.save_refresh_token.assert_awaited_once_with(new_refresh_token)

async def test_rotate_refresh_token_invalid_token(
        use_case,
        token_service
):
    user_uuid = MagicMock(UUID)
    refresh_token_str = "Test Token"
    user_agent = "Test User Agent"

    token_service.validate_refresh_token.return_value = None

    with pytest.raises(InvalidTokenException):
        await use_case(refresh_token_str, user_agent)
