from uuid import UUID, uuid4

from pydantic import validate_call, ConfigDict

from salary_tracker.domain.exceptions import SheetNotFoundDomainException, UserNotFoundDomainException
from salary_tracker.domain.sheet.models import NewSheetData, Sheet
from salary_tracker.domain.sheet.repositories import ISheetRepository
from salary_tracker.domain.sheet.services import ISheetService
from salary_tracker.domain.user.repositories import IUserRepository


class SheetService(ISheetService):
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, user_repository: IUserRepository, sheet_repository: ISheetRepository):
        self.user_repository = user_repository
        self.sheet_repository = sheet_repository

    async def get_by_uuid(self, sheet_uuid: UUID) -> Sheet:
        result = await self.sheet_repository.get_by_uuid(sheet_uuid)
        if result is None:
            raise SheetNotFoundDomainException(sheet_uuid)

        return result

    async def get_by_owner(self, owner_user_uuid: UUID) -> list[Sheet]:
        return await self.sheet_repository.get_by_owner(owner_user_uuid)

    async def create(self, new_sheet_data: NewSheetData) -> Sheet:
        owner = await self.user_repository.get_by_uuid(new_sheet_data.owner_user_uuid)
        if owner is None:
            raise UserNotFoundDomainException(new_sheet_data.owner_user_uuid)

        sheet_data = new_sheet_data.model_dump()
        sheet_data.update(
            uuid=uuid4(),
            owner_user_uuid=owner.uuid,
            records=[]
        )
        sheet = Sheet.model_validate(sheet_data)

        return await self.sheet_repository.upsert(sheet)
