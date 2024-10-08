from pydantic import ConfigDict, validate_call

from salary_tracker.domain.auth.models import TokenPair, AuthProvider
from salary_tracker.domain.auth.services import ITokenService, IAuthProviderService
from salary_tracker.domain.exceptions import InvalidTokenDomainException
from salary_tracker.domain.user.models import User
from salary_tracker.usecase.exceptions import AuthException


class LoginWithAuthProviderUseCase:
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, token_service: ITokenService, auth_provider_service: IAuthProviderService):
        self._token_service = token_service
        self._auth_provider_service = auth_provider_service

    async def __call__(self, external_token: str, auth_provider: AuthProvider) -> TokenPair:
        try:
            user = await self._auth_provider_service.create_or_retrieve_user(external_token, auth_provider)
            token_pair = await self._token_service.create_token_pair(user.uuid)

            return token_pair
        except InvalidTokenDomainException:
            raise AuthException("Invalid token")
