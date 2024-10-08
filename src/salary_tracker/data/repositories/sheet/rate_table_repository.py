from datetime import datetime
from uuid import UUID, uuid4

from pydantic import validate_call, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from salary_tracker.data.exceptions import DataException
from salary_tracker.data.model import DatabaseSheetRateTable, DatabaseSheet, DatabaseSheetRate
from salary_tracker.domain.sheet.models import RateTable
from salary_tracker.domain.sheet.repositories import IRateTableRepository


class RateTableRepository(IRateTableRepository):
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_for_datetime(self, sheet_uuid: UUID, datetime_point: datetime) -> RateTable:
        result = await self.session.execute(
            select(DatabaseSheetRateTable)
            .where(
                (DatabaseSheetRateTable.sheet_uuid == sheet_uuid),
                (DatabaseSheetRateTable.valid_from <= datetime_point),
                (DatabaseSheetRateTable.valid_to >= datetime_point)
            )
        )

        scalar = result.scalar_one_or_none()
        if scalar is None:
            raise DataException("Rate table not found")

        return RateTable.model_validate(scalar, from_attributes=True)

    async def get_for_sheet(self, sheet_uuid: UUID) -> list[RateTable]:
        result = await self.session.execute(
            select(DatabaseSheetRateTable)
            .filter_by(sheet_uuid=sheet_uuid)
        )

        scalars = result.scalars().all()
        return [RateTable.model_validate(scalar, from_attributes=True) for scalar in scalars]

    async def upsert(self, sheet_uuid: UUID, rate_tables: list[RateTable]) -> list[RateTable]:
        result = await self.session.execute(
            select(DatabaseSheet)
            .filter_by(uuid=sheet_uuid)
        )

        sheet = result.scalar_one_or_none()
        if sheet is None:
            raise DataException("Sheet not found")

        rate_tables_db = [
            DatabaseSheetRateTable(
                uuid=rate_table.uuid,
                valid_from=rate_table.valid_from,
                valid_to=rate_table.valid_to,
                rates=[
                    DatabaseSheetRate(
                        rate=rate.rate,
                        group_size=rate.group_size,
                        duration=rate.duration
                    ) for rate in rate_table.rates
                ]
            ) for rate_table in rate_tables
        ]

        sheet.rate_tables = rate_tables_db

        await self.session.commit()

        return [RateTable.model_validate(rate_table, from_attributes=True) for rate_table in sheet.rate_tables]
