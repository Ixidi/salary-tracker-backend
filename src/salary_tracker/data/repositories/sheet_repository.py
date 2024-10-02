from uuid import UUID

from pydantic import validate_call, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from salary_tracker.data.model import DatabaseSheet
from salary_tracker.domain.sheet.models import Sheet
from salary_tracker.domain.sheet.repositories import ISheetRepository


class SheetRepository(ISheetRepository):

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_uuid(self, sheet_uuid: UUID) -> Sheet | None:
        result = await self.session.execute(
            select(DatabaseSheet).filter_by(uuid=sheet_uuid)
        )

        sheet = result.scalar_one_or_none()
        if sheet is None:
            return None

        return Sheet.model_validate(sheet, from_attributes=True)

    async def get_by_owner(self, owner_user_uuid: UUID) -> list[Sheet]:
        result = await self.session.execute(
            select(DatabaseSheet).filter_by(owner_user_uuid=owner_user_uuid)
        )

        sheets = result.scalars().all()
        return [Sheet.model_validate(sheet, from_attributes=True) for sheet in sheets]

    async def upsert(self, sheet: Sheet) -> Sheet:
        result = await self.session.execute(
            select(DatabaseSheet).filter_by(uuid=sheet.uuid)
        )

        sheet_db = result.scalar_one_or_none()
        if sheet_db is None:
            sheet_db = DatabaseSheet.model_validate(sheet)
            self.session.add(sheet_db)
        else:
            sheet_db.sqlmodel_update(sheet)

        await self.session.commit()

        return Sheet.model_validate(sheet_db, from_attributes=True)