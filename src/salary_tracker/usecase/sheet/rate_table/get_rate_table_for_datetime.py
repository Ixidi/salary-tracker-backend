from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, validate_call

from salary_tracker.domain.exceptions import DomainException
from salary_tracker.domain.sheet.models import RateTable
from salary_tracker.domain.sheet.services import IRateTableService, ISheetService
from salary_tracker.usecase.exceptions import DomainRuleException, PermissionDeniedException


class GetRateTableForDatetime:
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, sheet_service: ISheetService, rate_table_service: IRateTableService):
        self._sheet_service = sheet_service
        self._rate_table_service = rate_table_service

    async def __call__(self, sheet_uuid: UUID, requesting_user_uuid: UUID, datetime_point: datetime) -> RateTable:
        try:
            sheet = await self._sheet_service.get_by_uuid(sheet_uuid)

            if sheet.owner_user_uuid != requesting_user_uuid:
                raise PermissionDeniedException("You are not allowed to access this sheet")

            return await self._rate_table_service.get_for_datetime(sheet_uuid, datetime_point)
        except DomainException as e:
            raise DomainRuleException(str(e))
