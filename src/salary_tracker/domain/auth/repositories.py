from abc import abstractmethod, ABC

from salary_tracker.domain.auth.models import RefreshToken, UserExternalAccount, AuthProvider


class IRefreshTokenRepository(ABC):

    @abstractmethod
    async def get_by_token(self, refresh_token: str) -> RefreshToken | None:
        pass

    @abstractmethod
    async def insert(self, refresh_token: RefreshToken) -> RefreshToken:
        pass

    @abstractmethod
    async def delete(self, refresh_token: str) -> None:
        pass


class IUserExternalAccountRepository(ABC):

    @abstractmethod
    async def get_by_external_id(self, external_id: str, auth_provider: AuthProvider) -> UserExternalAccount | None:
        pass

    @abstractmethod
    async def insert(self, user: UserExternalAccount) -> UserExternalAccount:
        pass