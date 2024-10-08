import datetime
from uuid import UUID, uuid4

from pydantic import validate_call, ConfigDict, ValidationError, BaseModel, model_validator

from salary_tracker.domain.exceptions import SheetNotFoundDomainException, ModelValidationDomainException
from salary_tracker.domain.sheet.factories import IRateTableFactory
from salary_tracker.domain.sheet.models import RateTable, RateTableData
from salary_tracker.domain.sheet.repositories import ISheetRepository, IRateTableRepository
from salary_tracker.domain.sheet.services import IRateTableService


class _RateTablesOverlapValidator(BaseModel):
    rate_tables: list[RateTable]

    @model_validator(mode='after')
    def check_model(self):
        for i in range(len(self.rate_tables)):
            for j in range(i + 1, len(self.rate_tables)):
                if self.rate_tables[i].valid_from < self.rate_tables[j].valid_to and self.rate_tables[i].valid_to > \
                        self.rate_tables[j].valid_from:
                    raise ValueError("Rate tables cannot overlap")

        return self


class RateTableService(IRateTableService):
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, sheet_repository: ISheetRepository, rate_table_repository: IRateTableRepository,
                 rate_table_factory: IRateTableFactory):
        self._sheet_repository = sheet_repository
        self._rate_table_repository = rate_table_repository
        self._rate_table_factory = rate_table_factory

    async def get_all(self, sheet_uuid: UUID) -> list[RateTable]:
        return await self._rate_table_repository.get_for_sheet(sheet_uuid)

    async def get_for_datetime(self, sheet_uuid: UUID, datetime_point: datetime) -> RateTable:
        result = await self._rate_table_repository.get_for_datetime(sheet_uuid, datetime_point)
        if result is None:
            raise SheetNotFoundDomainException(sheet_uuid)

        return result

    async def insert_rate_table(self, sheet_uuid: UUID, rate_table_data: RateTableData) -> list[RateTable]:
        sheet = await self._sheet_repository.get_by_uuid(sheet_uuid)
        if sheet is None:
            raise SheetNotFoundDomainException(sheet_uuid)

        rate_tables = await self._rate_table_repository.get_for_sheet(sheet_uuid)

        try:
            rate_table = self._rate_table_factory.create(
                rate_table_data=rate_table_data,
                durations=sheet.durations,
                group_sizes=sheet.group_sizes,
            )
        except ValidationError as e:
            raise ModelValidationDomainException(e)

        old_rate_tables = sorted(rate_tables, key=lambda x: x.valid_from)
        new_rate_tables = [rate_table]

        for old_rate_table in old_rate_tables:
            if old_rate_table.valid_from >= rate_table.valid_from and old_rate_table.valid_to <= rate_table.valid_to:
                # old within new, drop old
                continue
            elif old_rate_table.valid_to < rate_table.valid_from or old_rate_table.valid_from > rate_table.valid_to:
                # old and new do not overlap
                new_rate_tables.append(old_rate_table)
            elif old_rate_table.valid_from < rate_table.valid_from and old_rate_table.valid_to > rate_table.valid_to:
                # old contains new, split old
                old_rate_table_left = self._rate_table_factory.create(
                    rate_table_data=RateTableData(
                        valid_from=old_rate_table.valid_from,
                        valid_to=rate_table.valid_from - datetime.timedelta(microseconds=1),
                        rates=old_rate_table.rates
                    ),
                    durations=sheet.durations,
                    group_sizes=sheet.group_sizes,
                )
                new_rate_tables.append(old_rate_table_left)

                old_rate_table_right = self._rate_table_factory.create(
                    rate_table_data=RateTableData(
                        valid_from=rate_table.valid_to + datetime.timedelta(microseconds=1),
                        valid_to=old_rate_table.valid_to,
                        rates=old_rate_table.rates
                    ),
                    durations=sheet.durations,
                    group_sizes=sheet.group_sizes,
                )
                new_rate_tables.append(old_rate_table_right)
            elif old_rate_table.valid_from <= rate_table.valid_from <= old_rate_table.valid_to <= rate_table.valid_to:
                # old starts before new and ends within new
                old_rate_table.valid_to = rate_table.valid_from - datetime.timedelta(microseconds=1)
                new_rate_tables.append(old_rate_table)
            elif rate_table.valid_from <= old_rate_table.valid_from <= rate_table.valid_to <= old_rate_table.valid_to:
                # old starts within new and ends after new
                old_rate_table.valid_from = rate_table.valid_to + datetime.timedelta(microseconds=1)
                new_rate_tables.append(old_rate_table)

        new_rate_tables.sort(key=lambda x: x.valid_from)

        try:
            _RateTablesOverlapValidator(rate_tables=new_rate_tables)
        except ValidationError as e:
            raise ModelValidationDomainException(e)

        return await self._rate_table_repository.upsert(sheet_uuid, new_rate_tables)
