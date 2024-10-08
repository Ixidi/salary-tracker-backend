from uuid import uuid4

from pydantic import validate_call, ConfigDict

from salary_tracker.domain.exceptions import DomainException
from salary_tracker.domain.user.models import User, NewUserData
from salary_tracker.domain.user.repositories import IUserRepository
from salary_tracker.domain.user.services import IUserService


class UserService(IUserService):
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, user_repository: IUserRepository):
        self._user_repository = user_repository

    async def create(self, new_user_data: NewUserData) -> User:
        data = new_user_data.model_dump()
        data.update(
            uuid=uuid4()
        )

        user = User.model_validate(data)

        return await self._user_repository.upsert(user)

    async def get_by_uuid(self, uuid) -> User:
        result = await self._user_repository.get_by_uuid(uuid)
        if result is None:
            raise DomainException(f"User with uuid {uuid} not found")

        return result
