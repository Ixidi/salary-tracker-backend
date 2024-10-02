from unittest.mock import MagicMock

import pytest

from salary_tracker.domain.auth.services import ITokenService
from salary_tracker.api.exceptions import InvalidTokenException


@pytest.fixture
def token_service():
    return MagicMock(ITokenService)


@pytest.fixture
def use_case(token_service):
    from salary_tracker.usecase.auth.validate_access_token import ValidateAccessTokenUseCase
    return ValidateAccessTokenUseCase(token_service=token_service)


async def test_validate_access_token_success(
        use_case,
        token_service
):
    access_token_str = "Test Access Token"
    access_token = MagicMock()

    token_service.validate_access_token.return_value = access_token

    result = await use_case(access_token_str)

    assert result == access_token

    token_service.validate_access_token.assert_called_once_with(access_token_str)


async def test_validate_access_token_invalid_token(
        use_case,
        token_service
):
    access_token_str = "Test Access Token"

    token_service.validate_access_token.return_value = None

    with pytest.raises(InvalidTokenException):
        await use_case(access_token_str)

    token_service.validate_access_token.assert_called_once_with(access_token_str)
