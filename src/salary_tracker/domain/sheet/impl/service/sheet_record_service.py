from uuid import UUID, uuid4

from pydantic import validate_call, ConfigDict, BaseModel, model_validator, ValidationError

from salary_tracker.domain.exceptions import SheetNotFoundDomainException, ModelValidationDomainException, \
    RecordNotFoundDomainException
from salary_tracker.domain.pagination import PaginatedRequest, PaginatedResult
from salary_tracker.domain.sheet.models import NewRecordData, Record, Sheet, SheetRecordFilters
from salary_tracker.domain.sheet.repositories import ISheetRecordRepository, ISheetRepository
from salary_tracker.domain.sheet.services import ISheetRecordService


class _SheetRecordValidator(BaseModel):
    sheet: Sheet
    record: Record

    @model_validator(mode='after')
    def check_model(self):
        if self.record.group_size not in self.sheet.group_sizes:
            raise ValueError(f"Group size {self.record.group_size} is not in sheet group_sizes")
        if self.record.duration not in self.sheet.durations:
            raise ValueError(f"Duration ({self.record.duration}) is not in sheet durations")
        return self


class SheetRecordService(ISheetRecordService):
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, sheet_record_repository: ISheetRecordRepository, sheet_repository: ISheetRepository):
        self._sheet_record_repository = sheet_record_repository
        self._sheet_repository = sheet_repository

    async def get_paginated(self, request: PaginatedRequest[SheetRecordFilters]) -> PaginatedResult[Record]:
        return await self._sheet_record_repository.get_paginated(request)

    async def create(self, sheet_uuid: UUID, new_record_data: NewRecordData) -> Record:
        sheet = await self._sheet_repository.get_by_uuid(sheet_uuid)
        if sheet is None:
            raise SheetNotFoundDomainException(sheet_uuid)

        record_data = new_record_data.model_dump()
        record_data.update(
            uuid=uuid4()
        )

        try:
            record = Record.model_validate(record_data)
            _SheetRecordValidator(
                sheet=sheet,
                record=record
            )
        except ValidationError as e:
            raise ModelValidationDomainException(e)

        return await self._sheet_record_repository.add(sheet.uuid, record)

    async def delete(self, sheet_uuid: UUID, record_uuid: UUID) -> None:
        sheet = await self._sheet_repository.get_by_uuid(sheet_uuid)
        if sheet is None:
            raise SheetNotFoundDomainException(sheet_uuid)

        record = await self._sheet_record_repository.get_by_uuid(sheet_uuid, record_uuid)
        if record is None:
            raise RecordNotFoundDomainException(record_uuid)

        await self._sheet_record_repository.delete(sheet_uuid, record_uuid)
