from uuid import UUID

from sqlalchemy import Select, select

from salary_tracker.data.exceptions import DataException
from salary_tracker.data.model import DatabaseSheetRecord
from salary_tracker.data.repositories.mixin.pagination import GetPaginatedMixin, DatabaseModelType, DataType
from salary_tracker.domain.pagination import PaginatedRequest, PaginatedResult
from salary_tracker.domain.sheet.models import Record, SheetRecordFilters
from salary_tracker.domain.sheet.repositories import ISheetRecordRepository


class SheetRecordRepository(GetPaginatedMixin[DatabaseSheetRecord, Record, SheetRecordFilters],
                            ISheetRecordRepository):
    _model = DatabaseSheetRecord

    def _apply_pagination_filters(self, query: Select, filters: SheetRecordFilters) -> Select:
        query = query.filter_by(sheet_uuid=filters.sheet_uuid)

        if filters.datetime_from:
            query = query.filter(DatabaseSheetRecord.happened_at >= filters.datetime_from)

        if filters.datetime_to:
            query = query.filter(DatabaseSheetRecord.happened_at <= filters.datetime_to)

        return query

    def _map_to_domain(self, db_result: DatabaseModelType) -> DataType:
        return Record.model_validate(db_result, from_attributes=True)

    async def get_by_uuid(self, sheet_uuid: UUID, record_uuid: UUID) -> Record | None:
        result = await self._session.execute(
            select(DatabaseSheetRecord)
            .filter_by(sheet_uuid=sheet_uuid, uuid=record_uuid)
        )

        record = result.scalar_one_or_none()
        if not record:
            return None

        return Record.model_validate(record, from_attributes=True)

    async def get_paginated(self, request: PaginatedRequest[SheetRecordFilters]) -> PaginatedResult[Record]:
        return await self._get_paginated(request)

    async def add(self, sheet_uuid: UUID, record: Record) -> Record:
        record_db = DatabaseSheetRecord(
            uuid=record.uuid,
            sheet_uuid=sheet_uuid,
            group_size=record.group_size,
            duration=record.duration,
            group_name=record.group_name,
            happened_at=record.happened_at,
            additional_info=record.additional_info
        )

        self._session.add(record_db)
        await self._session.commit()

        return Record.model_validate(record_db, from_attributes=True)

    async def delete(self, sheet_uuid: UUID, record_uuid: UUID) -> None:
        record = await self._session.execute(
            select(DatabaseSheetRecord)
            .filter_by(sheet_uuid=sheet_uuid, uuid=record_uuid)
        )

        record = record.scalar_one_or_none()
        if not record:
            raise DataException(f"Record with uuid {record_uuid} not found")

        await self._session.delete(record)
        await self._session.commit()
