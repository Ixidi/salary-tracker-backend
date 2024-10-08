from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import ConfigDict, validate_call

from salary_tracker.domain.exceptions import SheetNotFoundDomainException, DomainException
from salary_tracker.domain.pagination import PaginatedRequest, PageParams
from salary_tracker.domain.sheet.models import Salary, SheetRecordFilters
from salary_tracker.domain.sheet.repositories import ISheetRepository, IRateTableRepository, ISheetRecordRepository
from salary_tracker.domain.sheet.services import ISalaryService


class SalaryService(ISalaryService):
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, sheet_repository: ISheetRepository, sheet_record_repository: ISheetRecordRepository,
                 rate_table_repository: IRateTableRepository):
        self.sheet_repository = sheet_repository
        self.sheet_record_repository = sheet_record_repository
        self.rate_table_repository = rate_table_repository

    async def calculate_salary(self, sheet_uuid: UUID, datetime_from: datetime, datetime_to: datetime) -> Salary:
        sheet = await self.sheet_repository.get_by_uuid(sheet_uuid)
        if sheet is None:
            raise SheetNotFoundDomainException(sheet_uuid)

        page = 0
        per_page = 100
        records_page = await self.sheet_record_repository.get_paginated(PaginatedRequest(
            page_params=PageParams(page=page, per_page=per_page),
            filters=SheetRecordFilters(
                sheet_uuid=sheet_uuid,
                datetime_from=datetime_from,
                datetime_to=datetime_to
            )
        ))

        salary = Decimal(0)
        while records_page.items:
            for record in records_page.items:
                rate_table = await self.rate_table_repository.get_for_datetime(sheet_uuid, record.happened_at)
                if rate_table is None:
                    raise DomainException(f"Rate table not found for datetime {record.happened_at}")

                salary += rate_table.get_salary(record.group_size, record.duration)

            page += 1
            records_page = await self.sheet_record_repository.get_paginated(PaginatedRequest(
                page_params=PageParams(page=page, per_page=per_page),
                filters=SheetRecordFilters(
                    sheet_uuid=sheet_uuid,
                    datetime_from=datetime_from,
                    datetime_to=datetime_to
                )
            ))

        return Salary(
            datetime_from=datetime_from,
            datetime_to=datetime_to,
            salary=salary
        )
