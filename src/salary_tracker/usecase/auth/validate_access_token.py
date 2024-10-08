from pydantic import ConfigDict, validate_call

from salary_tracker.domain.auth.models import AccessToken
from salary_tracker.domain.auth.services import ITokenService
from salary_tracker.domain.exceptions import InvalidTokenDomainException
from salary_tracker.usecase.exceptions import AuthException


class ValidateAccessTokenUseCase:
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, token_service: ITokenService):
        self._token_service = token_service

    async def __call__(self, access_token: str) -> AccessToken:
        try:
            return await self._token_service.validate_access_token(access_token)
        except InvalidTokenDomainException:
            raise AuthException("Invalid token")
