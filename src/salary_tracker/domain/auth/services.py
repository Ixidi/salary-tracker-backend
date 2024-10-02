from abc import ABC, abstractmethod
from uuid import UUID

from pydantic import BaseModel

from salary_tracker.domain.auth.models import AccessToken, RefreshToken, \
    AuthProviderUserData, AuthProvider, TokenPair, UserExternalAccount


class ITokenService(ABC):

    @abstractmethod
    async def validate_access_token(self, access_token: str) -> AccessToken | None:
        pass

    @abstractmethod
    async def validate_refresh_token(self, refresh_token: str) -> RefreshToken | None:
        pass

    @abstractmethod
    async def create_token_pair(self, user_uuid: UUID, user_agent: str) -> TokenPair:
        pass

    @abstractmethod
    async def save_refresh_token(self, refresh_token: RefreshToken) -> RefreshToken:
        pass

    @abstractmethod
    async def delete_refresh_token(self, refresh_token: str) -> None:
        pass


class IAuthProviderService(ABC):

    @abstractmethod
    async def extract_user_data(self, token: str, provider: AuthProvider) -> AuthProviderUserData | None:
        pass

    @abstractmethod
    async def link_account(self, user_external_account: UserExternalAccount) -> None:
        pass

    @abstractmethod
    async def get_linked_account(self, external_id: str, provider: AuthProvider) -> AuthProviderUserData | None:
        pass


class IAuthProviderUserDataExtractor(ABC):

    @abstractmethod
    async def extract_from_token(self, token: str) -> AuthProviderUserData | None:
        pass


class IAuthProviderUserDataExtractorFactory(ABC, BaseModel):

    @abstractmethod
    def create(self, provider: AuthProvider) -> IAuthProviderUserDataExtractor:
        pass
