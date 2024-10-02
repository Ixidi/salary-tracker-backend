from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from salary_tracker.domain.auth.models import TokenPair, AccessToken, UserExternalAccount, AuthProvider, RefreshToken, \
    AuthProviderUserData
from salary_tracker.domain.auth.services import ITokenService, IAuthProviderService
from salary_tracker.api.exceptions import InvalidTokenException
from salary_tracker.domain.user.models import User
from salary_tracker.domain.user.services import IUserService


@pytest.fixture
def token_service():
    return AsyncMock(ITokenService)

@pytest.fixture
def user_service():
    return AsyncMock(IUserService)

@pytest.fixture
def auth_provider_service():
    return AsyncMock(IAuthProviderService)

@pytest.fixture
def use_case(token_service, user_service, auth_provider_service):
    from salary_tracker.usecase.auth.auth_provider_login import LoginWithAuthProviderUseCase
    return LoginWithAuthProviderUseCase(
        token_service=token_service,
        user_service=user_service,
        auth_provider_service=auth_provider_service
    )

@pytest.fixture
def user_external_account():
    return UserExternalAccount(
        user_uuid=uuid4(),
        provider=AuthProvider.GOOGLE,
        external_id="Test External ID"
    )

@pytest.fixture
def auth_provider_user_data():
    return AuthProviderUserData(
        email="test@test.com",
        name="Test Name",
        external_id="Test External ID",
        provider=AuthProvider.GOOGLE,
        avatar=None
    )

@pytest.fixture
def token_pair(user_external_account):
    return TokenPair(
        access_token=AccessToken(
            token="Test Access Token",
            user_uuid=user_external_account.user_uuid,
            expires_at=datetime(2022, 1, 1, tzinfo=UTC)
        ),
        refresh_token=RefreshToken(
            token="Test Refresh Token",
            user_uuid=user_external_account.user_uuid,
            user_agent="Test User Agent",
            expires_at=datetime(2022, 1, 1, tzinfo=UTC)
        )
    )

async def test_auth_provider_login_success_link_exists(
        use_case,
        token_service,
        user_service,
        auth_provider_service,
        user_external_account,
        auth_provider_user_data,
        token_pair
):
    external_token = "Test External Token"

    auth_provider_service.extract_user_data.return_value = auth_provider_user_data
    auth_provider_service.get_linked_account.return_value = user_external_account
    token_service.create_token_pair.return_value = token_pair

    result = await use_case(external_token, AuthProvider.GOOGLE, token_pair.refresh_token.user_agent)

    assert result == token_pair
    auth_provider_service.extract_user_data.assert_awaited_once_with(external_token, AuthProvider.GOOGLE)
    auth_provider_service.get_linked_account.assert_awaited_once_with(user_external_account.external_id, AuthProvider.GOOGLE)
    token_service.create_token_pair.assert_awaited_once_with(user_external_account.user_uuid, token_pair.refresh_token.user_agent)
    token_service.save_refresh_token.assert_awaited_once_with(token_pair.refresh_token)

async def test_auth_provider_login_success_link_does_not_exist(
        use_case,
        token_service,
        user_service,
        auth_provider_service,
        user_external_account,
        auth_provider_user_data,
        token_pair
):
    external_token = "Test External Token"
    user = User(
        uuid=uuid4(),
        email=auth_provider_user_data.email,
        name=auth_provider_user_data.name
    )

    auth_provider_service.extract_user_data.return_value = auth_provider_user_data
    auth_provider_service.get_linked_account.return_value = None
    user_service.create_instance.return_value = user

    token_service.create_token_pair.return_value = token_pair

    result = await use_case(external_token, AuthProvider.GOOGLE, token_pair.refresh_token.user_agent)

    assert result == token_pair
    auth_provider_service.extract_user_data.assert_awaited_once_with(external_token, AuthProvider.GOOGLE)
    auth_provider_service.get_linked_account.assert_awaited_once_with(user_external_account.external_id, AuthProvider.GOOGLE)
    user_service.create_instance.assert_awaited_once_with(auth_provider_user_data.email, auth_provider_user_data.name)
    user_service.upsert.assert_awaited_once_with(user)
    token_service.create_token_pair.assert_awaited_once_with(user.uuid, token_pair.refresh_token.user_agent)
    token_service.save_refresh_token.assert_awaited_once_with(token_pair.refresh_token)

async def test_auth_provider_login_invalid_token(
        use_case,
        token_service,
        user_service,
        auth_provider_service
):
    external_token = "Test External Token"

    auth_provider_service.extract_user_data.return_value = None

    with pytest.raises(InvalidTokenException):
        await use_case(external_token, AuthProvider.GOOGLE, "Test User Agent")

    auth_provider_service.extract_user_data.assert_awaited_once_with(external_token, AuthProvider.GOOGLE)