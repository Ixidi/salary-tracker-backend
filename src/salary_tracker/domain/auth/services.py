from abc import ABC, abstractmethod
from uuid import UUID

from salary_tracker.domain.auth.models import AccessToken, RefreshToken, \
    AuthProviderUserData, AuthProvider, TokenPair
from salary_tracker.domain.user.models import User


class ITokenService(ABC):

    @abstractmethod
    async def validate_access_token(self, access_token: str) -> AccessToken:
        pass

    @abstractmethod
    async def validate_refresh_token(self, refresh_token: str) -> RefreshToken:
        pass

    @abstractmethod
    async def create_token_pair(self, user_uuid: UUID) -> TokenPair:
        pass

    @abstractmethod
    async def rotate_refresh_token(self, refresh_token: str) -> TokenPair:
        pass

    @abstractmethod
    async def delete_refresh_token(self, refresh_token: str) -> None:
        pass


class IAuthProviderService(ABC):

    @abstractmethod
    async def create_or_retrieve_user(self, external_token: str, auth_provider: AuthProvider) -> User:
        pass


class IAuthProviderUserDataExtractor(ABC):

    @abstractmethod
    async def extract_from_token(self, token: str) -> AuthProviderUserData | None:
        pass
