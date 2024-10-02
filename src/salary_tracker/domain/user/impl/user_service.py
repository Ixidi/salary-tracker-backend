from uuid import uuid4

from pydantic import EmailStr, BaseModel, ConfigDict

from salary_tracker.domain.exceptions import DomainException
from salary_tracker.domain.user.models import User
from salary_tracker.domain.user.repositories import IUserRepository
from salary_tracker.domain.user.services import IUserService


class UserService(IUserService, BaseModel):
    user_repository: IUserRepository

    model_config = ConfigDict(arbitrary_types_allowed=True)

    async def create_instance(self, email: EmailStr, name: str) -> User:
        return User(
            uuid=uuid4(),
            name=name,
            email=email
        )

    async def upsert(self, user: User) -> User:
        return await self.user_repository.upsert(user)

    async def get_by_uuid(self, uuid) -> User:
        result = await self.user_repository.get_by_uuid(uuid)
        if result is None:
            raise DomainException(f"User with uuid {uuid} not found")

        return result
