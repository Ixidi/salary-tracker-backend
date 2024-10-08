from abc import ABC, abstractmethod
from uuid import UUID

from salary_tracker.domain.user.models import User, NewUserData


class IUserService(ABC):
    @abstractmethod
    async def get_by_uuid(self, uuid: UUID) -> User:
        pass

    @abstractmethod
    async def create(self, new_user_data: NewUserData) -> User:
        pass
