from uuid import UUID

from pydantic import validate_call, ConfigDict

from salary_tracker.domain.exceptions import DomainException
from salary_tracker.domain.sheet.models import NewRecordData, Record
from salary_tracker.domain.sheet.services import ISheetService, ISheetRecordService
from salary_tracker.usecase.exceptions import PermissionDeniedException, DomainRuleException


class AddSheetRecordUseCase:
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, sheet_service: ISheetService, sheet_record_service: ISheetRecordService):
        self._sheet_service = sheet_service
        self._sheet_record_service = sheet_record_service

    async def __call__(self, sheet_uuid: UUID, requesting_user_uuid: UUID,
                       record_data: NewRecordData) -> Record:
        try:
            sheet = await self._sheet_service.get_by_uuid(sheet_uuid)
            if sheet.owner_user_uuid != requesting_user_uuid:
                raise PermissionDeniedException("You are not allowed to access this sheet")

            return await self._sheet_record_service.create(sheet_uuid, record_data)
        except DomainException as e:
            raise DomainRuleException(str(e))
