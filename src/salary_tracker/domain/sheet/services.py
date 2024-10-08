from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from salary_tracker.domain.pagination import PaginatedRequest, PaginatedResult
from salary_tracker.domain.sheet.models import Sheet, NewSheetData, RateTableData, RateTable, Record, \
    NewRecordData, SheetRecordFilters, Salary


class ISheetService(ABC):

    @abstractmethod
    async def get_by_uuid(self, sheet_uuid: UUID) -> Sheet:
        pass

    @abstractmethod
    async def get_by_owner_paginated(self, request: PaginatedRequest[UUID]) -> PaginatedResult[Sheet]:
        pass

    @abstractmethod
    async def create(self, new_sheet_data: NewSheetData) -> Sheet:
        pass

    @abstractmethod
    async def delete(self, sheet_uuid: UUID) -> None:
        pass


class IRateTableService(ABC):

    @abstractmethod
    async def insert_rate_table(self, sheet_uuid: UUID, rate_table_data: RateTableData) -> list[RateTable]:
        pass

    @abstractmethod
    async def get_all(self, sheet_uuid: UUID) -> list[RateTable]:
        pass

    @abstractmethod
    async def get_for_datetime(self, sheet_uuid: UUID, datetime_point: datetime) -> RateTable:
        pass


class ISheetRecordService(ABC):

    @abstractmethod
    async def get_paginated(self, request: PaginatedRequest[SheetRecordFilters]) -> PaginatedResult[Record]:
        pass

    @abstractmethod
    async def create(self, sheet_uuid: UUID, new_record_data: NewRecordData) -> Record:
        pass

    @abstractmethod
    async def delete(self, sheet_uuid: UUID, record_uuid: UUID) -> None:
        pass


class ISalaryService(ABC):

    @abstractmethod
    async def calculate_salary(self, sheet_uuid: UUID, datetime_from: datetime, datetime_to: datetime) -> Salary:
        pass
