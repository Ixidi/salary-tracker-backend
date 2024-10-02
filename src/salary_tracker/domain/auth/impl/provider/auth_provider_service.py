from pydantic import BaseModel, ConfigDict

from salary_tracker.domain.auth.models import AuthProvider, AuthProviderUserData, UserExternalAccount
from salary_tracker.domain.auth.repositories import IUserExternalAccountRepository
from salary_tracker.domain.auth.services import IAuthProviderService, IAuthProviderUserDataExtractorFactory


class AuthProviderService(IAuthProviderService, BaseModel):
    auth_provider_user_data_extractor_factory: IAuthProviderUserDataExtractorFactory
    user_external_account_repository: IUserExternalAccountRepository

    model_config = ConfigDict(arbitrary_types_allowed=True)

    async def extract_user_data(self, token: str, provider: AuthProvider) -> AuthProviderUserData | None:
        extractor = self.auth_provider_user_data_extractor_factory.create(provider)
        data = await extractor.extract_from_token(token)
        return data

    async def link_account(self, user_external_account: UserExternalAccount) -> None:
        await self.user_external_account_repository.create(user_external_account)

    async def get_linked_account(self, external_id: str, provider: AuthProvider) -> AuthProviderUserData | None:
        return await self.user_external_account_repository.get_by_external_id(external_id, provider)
