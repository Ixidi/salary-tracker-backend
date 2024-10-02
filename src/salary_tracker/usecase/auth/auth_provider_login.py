from pydantic import BaseModel, ConfigDict

from salary_tracker.domain.auth.models import TokenPair, AuthProvider, UserExternalAccount, AuthProviderUserData
from salary_tracker.domain.auth.services import ITokenService, IAuthProviderService
from salary_tracker.domain.user.services import IUserService
from salary_tracker.usecase.exceptions import InvalidTokenException


class LoginWithAuthProviderUseCase(BaseModel):
    token_service: ITokenService
    user_service: IUserService
    auth_provider_service: IAuthProviderService

    model_config = ConfigDict(arbitrary_types_allowed=True)

    async def __call__(self, external_token: str, auth_provider: AuthProvider, user_agent: str) -> TokenPair:
        # auth_provider_user_data = await self.auth_provider_service.extract_user_data(external_token, auth_provider)
        # if not auth_provider_user_data:
        #     raise InvalidTokenException()
        # TODO testing

        auth_provider_user_data = AuthProviderUserData(
            provider=AuthProvider.GOOGLE,
            external_id="123",
            name="HARD CODED",
            avatar=None,
            email="hard@coded.com"
        )

        user_external_account = await self.auth_provider_service.get_linked_account(auth_provider_user_data.external_id, auth_provider)
        if not user_external_account:
            user = await self.user_service.create_instance(auth_provider_user_data.email, auth_provider_user_data.name)
            await self.user_service.upsert(user)

            user_external_account = UserExternalAccount(
                user_uuid=user.uuid,
                provider=auth_provider,
                external_id=auth_provider_user_data.external_id
            )
            await self.auth_provider_service.link_account(user_external_account)

        token_pair = await self.token_service.create_token_pair(user_external_account.user_uuid, user_agent)
        await self.token_service.save_refresh_token(token_pair.refresh_token)

        return token_pair
