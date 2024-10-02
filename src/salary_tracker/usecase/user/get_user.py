from uuid import UUID

from pydantic import BaseModel, ConfigDict

from salary_tracker.domain.exceptions import UserNotFoundDomainException
from salary_tracker.domain.user.models import User
from salary_tracker.domain.user.services import IUserService
from salary_tracker.usecase.exceptions import UserNotFoundException


class GetUserUseCase(BaseModel):
    user_service: IUserService

    model_config = ConfigDict(arbitrary_types_allowed=True)

    async def __call__(self, user_uuid: UUID) -> User:
        try:
            return await self.user_service.get_by_uuid(user_uuid)
        except UserNotFoundDomainException as e:
            raise UserNotFoundException(user_uuid) from e
