from datetime import datetime
from uuid import UUID

from pydantic import validate_call, ConfigDict

from salary_tracker.domain.exceptions import DomainException
from salary_tracker.domain.sheet.models import Salary
from salary_tracker.domain.sheet.services import ISalaryService, ISheetService
from salary_tracker.usecase.exceptions import DomainRuleException, PermissionDeniedException


class CalculateSalaryUseCase:
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, sheet_service: ISheetService, salary_service: ISalaryService):
        self._sheet_service = sheet_service
        self._salary_service = salary_service

    # TODO too many arguments
    async def __call__(self, sheet_uuid: UUID, requesting_user_uuid: UUID, datetime_from: datetime,
                       datetime_to: datetime) -> Salary:
        try:
            sheet = await self._sheet_service.get_by_uuid(sheet_uuid)
            if sheet.owner_user_uuid != requesting_user_uuid:
                raise PermissionDeniedException("You are not allowed to access this sheet")

            return await self._salary_service.calculate_salary(sheet_uuid, datetime_from, datetime_to)
        except DomainException as e:
            raise DomainRuleException(str(e))
