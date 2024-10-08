from uuid import UUID

from sqlalchemy import select, Select

from salary_tracker.data.exceptions import DataException
from salary_tracker.data.model import DatabaseSheet, DatabaseSheetDuration, \
    DatabaseSheetGroupSize
from salary_tracker.data.repositories.mixin.pagination import GetPaginatedMixin
from salary_tracker.domain.pagination import PaginatedRequest, PaginatedResult
from salary_tracker.domain.sheet.models import Sheet
from salary_tracker.domain.sheet.repositories import ISheetRepository


def _map(sheet: DatabaseSheet) -> Sheet:
    return Sheet(
        uuid=sheet.uuid,
        owner_user_uuid=sheet.owner_user_uuid,
        title=sheet.title,
        description=sheet.description,
        group_sizes=set([group_size.group_size for group_size in sheet.group_sizes]),
        durations=set([duration.duration for duration in sheet.durations])
    )


class SheetRepository(GetPaginatedMixin[DatabaseSheet, Sheet, UUID], ISheetRepository):
    _model = DatabaseSheet

    def _apply_pagination_filters(self, query: Select, filters: UUID) -> Select:
        return query.filter_by(owner_user_uuid=filters)

    def _map_to_domain(self, db_result: DatabaseSheet) -> Sheet:
        return _map(db_result)

    async def get_by_uuid(self, sheet_uuid: UUID) -> Sheet | None:
        result = await self.session.execute(
            select(DatabaseSheet).filter_by(uuid=sheet_uuid)
        )

        sheet = result.scalar_one_or_none()
        if sheet is None:
            return None

        return _map(sheet)

    async def get_by_owner_paginated(self, request: PaginatedRequest[UUID]) -> PaginatedResult[Sheet]:
        return await self._get_paginated(request)

    async def upsert(self, sheet: Sheet) -> Sheet:
        result = await self.session.execute(
            select(DatabaseSheet).filter_by(uuid=sheet.uuid)
        )

        sheet_db = result.scalar_one_or_none()

        durations = [
            DatabaseSheetDuration(
                duration=duration
            ) for duration in sheet.durations
        ]

        group_sizes = [
            DatabaseSheetGroupSize(
                group_size=group_size
            ) for group_size in sheet.group_sizes
        ]

        if sheet_db is None:
            sheet_db = DatabaseSheet(
                uuid=sheet.uuid,
                owner_user_uuid=sheet.owner_user_uuid,
                title=sheet.title,
                description=sheet.description,
                durations=durations,
                group_sizes=group_sizes,
                records=[]
            )
            self.session.add(sheet_db)
        else:
            sheet_db.owner_user_uuid = sheet.owner_user_uuid
            sheet_db.title = sheet.title
            sheet_db.durations = durations
            sheet_db.group_sizes = group_sizes
            sheet_db.description = sheet.description

        await self.session.commit()

        return _map(sheet_db)

    async def delete(self, sheet_uuid: UUID) -> None:
        result = await self.session.execute(
            select(DatabaseSheet).filter_by(uuid=sheet_uuid)
        )

        sheet_db = result.scalar_one_or_none()
        if sheet_db is None:
            raise DataException(f"Sheet with uuid {sheet_uuid} not found")

        await self.session.delete(sheet_db)
        await self.session.commit()
