from pydantic import ConfigDict, validate_call

from salary_tracker.domain.auth.models import TokenPair
from salary_tracker.domain.auth.services import ITokenService
from salary_tracker.domain.exceptions import InvalidTokenDomainException
from salary_tracker.usecase.exceptions import AuthException


class RotateRefreshTokenUseCase:
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, token_service: ITokenService):
        self._token_service = token_service

    async def __call__(self, refresh_token: str) -> TokenPair:
        try:
            return await self._token_service.rotate_refresh_token(refresh_token)
        except InvalidTokenDomainException as e:
            raise AuthException("Invalid token")
