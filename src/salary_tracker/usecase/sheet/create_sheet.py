from pydantic import validate_call, ConfigDict

from salary_tracker.domain.exceptions import UserNotFoundDomainException
from salary_tracker.domain.sheet.models import Sheet, NewSheetData
from salary_tracker.domain.sheet.services import ISheetService
from salary_tracker.usecase.exceptions import UserNotFoundException


class CreateSheetUseCase:
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, sheet_service: ISheetService):
        self.sheet_service = sheet_service

    async def __call__(self, new_sheet_data: NewSheetData) -> Sheet:
        try:
            return await self.sheet_service.create(new_sheet_data)
        except UserNotFoundDomainException as e:
            raise UserNotFoundException(e.user_uuid) from e
