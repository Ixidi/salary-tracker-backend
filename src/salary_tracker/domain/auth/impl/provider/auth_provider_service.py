from uuid import uuid4

from pydantic import ConfigDict, validate_call

from salary_tracker.domain.auth.factories import IAuthProviderUserDataExtractorFactory
from salary_tracker.domain.auth.models import AuthProvider, AuthProviderUserData, UserExternalAccount
from salary_tracker.domain.auth.repositories import IUserExternalAccountRepository
from salary_tracker.domain.auth.services import IAuthProviderService
from salary_tracker.domain.user.models import User
from salary_tracker.domain.user.repositories import IUserRepository


class AuthProviderService(IAuthProviderService):
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, auth_provider_user_data_extractor_factory: IAuthProviderUserDataExtractorFactory,
                 user_external_account_repository: IUserExternalAccountRepository, user_repository: IUserRepository):
        self._auth_provider_user_data_extractor_factory = auth_provider_user_data_extractor_factory
        self._user_external_account_repository = user_external_account_repository
        self._user_repository = user_repository

    async def create_or_retrieve_user(self, external_token: str, auth_provider: AuthProvider) -> User:
        auth_provider_user_data = AuthProviderUserData(
            provider=AuthProvider.GOOGLE,
            external_id="123",
            name="HARD CODED",
            avatar=None,
            email="hard@coded.com"
        )
        # TODO implement the logic to extract the user data from the external token, for now we are hard coding the data

        user_external_account = await self._user_external_account_repository.get_by_external_id(
            auth_provider_user_data.external_id, auth_provider)
        if not user_external_account:
            user = await self._user_repository.upsert(User(
                uuid=uuid4(),
                email=auth_provider_user_data.email,
                name=auth_provider_user_data.name
            ))

            user_external_account = UserExternalAccount(
                user_uuid=user.uuid,
                provider=auth_provider,
                external_id=auth_provider_user_data.external_id
            )
            await self._user_external_account_repository.insert(user_external_account)
        else:
            user = await self._user_repository.get_by_uuid(user_external_account.user_uuid)

        return user
