from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from salary_tracker.domain.pagination import PaginatedRequest, PaginatedResult
from salary_tracker.domain.sheet.models import Sheet, RateTable, Record, SheetRecordFilters, Salary


class ISheetRepository(ABC):

    @abstractmethod
    async def get_by_uuid(self, sheet_uuid: UUID) -> Sheet | None:
        pass

    @abstractmethod
    async def get_by_owner_paginated(self, request: PaginatedRequest[UUID]) -> PaginatedResult[Sheet]:
        pass

    @abstractmethod
    async def upsert(self, sheet: Sheet) -> Sheet:
        pass

    @abstractmethod
    async def delete(self, sheet_uuid: UUID) -> None:
        pass


class IRateTableRepository(ABC):

    @abstractmethod
    async def get_for_datetime(self, sheet_uuid: UUID, datetime_point: datetime) -> RateTable | None:
        pass

    @abstractmethod
    async def get_for_sheet(self, sheet_uuid: UUID) -> list[RateTable]:
        pass

    @abstractmethod
    async def upsert(self, sheet_uuid: UUID, rate_tables: list[RateTable]) -> list[RateTable]:
        pass


class ISheetRecordRepository(ABC):

    @abstractmethod
    async def get_paginated(self, request: PaginatedRequest[SheetRecordFilters]) -> PaginatedResult[Record]:
        pass

    @abstractmethod
    async def get_by_uuid(self, sheet_uuid: UUID, record_uuid: UUID) -> Record | None:
        pass

    @abstractmethod
    async def add(self, sheet_uuid: UUID, record: Record) -> Record:
        pass

    @abstractmethod
    async def delete(self, sheet_uuid: UUID, record_uuid: UUID) -> None:
        pass


class ISalaryRepository(ABC):

    @abstractmethod
    async def get_salary(self, sheet_uuid: UUID, datetime_from: datetime, datetime_to: datetime) -> Salary:
        pass
