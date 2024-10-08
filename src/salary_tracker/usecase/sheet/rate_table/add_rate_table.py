from uuid import UUID

from pydantic import validate_call, ConfigDict

from salary_tracker.domain.exceptions import DomainException
from salary_tracker.domain.sheet.models import RateTableData, RateTable
from salary_tracker.domain.sheet.services import ISheetService, IRateTableService
from salary_tracker.usecase.exceptions import DomainRuleException, PermissionDeniedException


class AddSheetRateTableUseCase:
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, sheet_service: ISheetService, rate_table_service: IRateTableService):
        self._sheet_service = sheet_service
        self._rate_table_service = rate_table_service

    async def __call__(self, sheet_uuid: UUID, requesting_user_uuid: UUID, rate_table_data: RateTableData) -> list[
        RateTable]:
        try:
            sheet = await self._sheet_service.get_by_uuid(sheet_uuid)
            if sheet.owner_user_uuid != requesting_user_uuid:
                raise PermissionDeniedException("You are not allowed to access this sheet")

            return await self._rate_table_service.insert_rate_table(sheet_uuid, rate_table_data)
        except DomainException as e:
            raise DomainRuleException(str(e))
