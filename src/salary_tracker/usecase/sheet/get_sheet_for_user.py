from uuid import UUID

from pydantic import validate_call, ConfigDict

from salary_tracker.domain.exceptions import DomainException
from salary_tracker.domain.sheet.models import Sheet
from salary_tracker.domain.sheet.services import ISheetService
from salary_tracker.usecase.exceptions import DomainRuleException, PermissionDeniedException


class GetSheetForUserUseCase:
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, sheet_service: ISheetService):
        self._sheet_service = sheet_service

    async def __call__(self, sheet_uuid: UUID, requesting_user_uuid: UUID) -> Sheet:
        try:
            sheet = await self._sheet_service.get_by_uuid(sheet_uuid)
        except DomainException as e:
            raise DomainRuleException(str(e))

        if sheet.owner_user_uuid != requesting_user_uuid:
            raise PermissionDeniedException("You are not allowed to access this sheet")

        return sheet
