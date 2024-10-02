from abc import ABC, abstractmethod
from uuid import UUID

from pydantic import EmailStr

from salary_tracker.domain.user.models import User


class IUserService(ABC):

    @abstractmethod
    async def create_instance(self, email: EmailStr, name: str) -> User:
        pass

    @abstractmethod
    async def upsert(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_by_uuid(self, uuid: UUID) -> User:
        pass
