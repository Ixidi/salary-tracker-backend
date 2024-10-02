from abc import abstractmethod, ABC
from uuid import UUID

from salary_tracker.domain.user.models import User


class IUserRepository(ABC):

    @abstractmethod
    async def get_by_uuid(self, uuid: UUID) -> User | None:
        pass

    @abstractmethod
    async def upsert(self, user: User) -> User:
        pass
