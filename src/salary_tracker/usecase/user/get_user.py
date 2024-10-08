from uuid import UUID

from pydantic import ConfigDict, validate_call

from salary_tracker.domain.exceptions import DomainException
from salary_tracker.domain.user.models import User
from salary_tracker.domain.user.services import IUserService
from salary_tracker.usecase.exceptions import DomainRuleException


class GetUserUseCase:
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, user_service: IUserService):
        self._user_service = user_service

    async def __call__(self, user_uuid: UUID) -> User:
        try:
            return await self._user_service.get_by_uuid(user_uuid)
        except DomainException as e:
            raise DomainRuleException(str(e))
