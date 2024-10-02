from abc import ABC, abstractmethod
from uuid import UUID

from salary_tracker.domain.sheet.models import Sheet, NewSheetData


class ISheetService(ABC):

    @abstractmethod
    async def get_by_uuid(self, sheet_uuid: UUID) -> Sheet:
        pass

    @abstractmethod
    async def get_by_owner(self, owner_user_uuid: UUID) -> list[Sheet]:
        pass

    @abstractmethod
    async def create(self, new_sheet_data: NewSheetData) -> Sheet:
        pass
