from pydantic import validate_call, ConfigDict

from salary_tracker.domain.exceptions import UserNotFoundDomainException, ModelValidationDomainException, \
    DomainException
from salary_tracker.domain.sheet.models import Sheet, NewSheetData
from salary_tracker.domain.sheet.services import ISheetService
from salary_tracker.usecase.exceptions import DomainRuleException


class CreateSheetUseCase:
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, sheet_service: ISheetService):
        self._sheet_service = sheet_service

    async def __call__(self, new_sheet_data: NewSheetData) -> Sheet:
        try:
            return await self._sheet_service.create(new_sheet_data)
        except DomainException as e:
            raise DomainRuleException(str(e))
