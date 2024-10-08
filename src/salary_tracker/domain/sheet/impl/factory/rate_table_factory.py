import datetime
from uuid import uuid4

from asyncpg.pgproto.pgproto import timedelta
from pydantic import BaseModel, model_validator

from salary_tracker.domain.sheet.factories import IRateTableFactory
from salary_tracker.domain.sheet.models import RateTable, RateTableData


class _RateTableValidator(BaseModel):
    rate_table: RateTable
    durations: set[timedelta]
    group_sizes: set[int]

    @model_validator(mode='after')
    def check_model(self):
        if len(self.rate_table.rates) != len(self.group_sizes) * len(self.durations):
            raise ValueError("Rates must be provided for all group sizes and durations")

        for rate in self.rate_table.rates:
            if rate.group_size not in self.group_sizes:
                raise ValueError(f"Group size {rate.group_size} is not in group_sizes")
            if rate.duration not in self.durations:
                raise ValueError(f"Duration {rate.duration} is not in durations")

        return self


_MIN_DATETIME = datetime.datetime(datetime.MINYEAR, 1, 1, tzinfo=datetime.UTC)
_MAX_DATETIME = datetime.datetime(datetime.MAXYEAR, 12, 31, 23, 59, 59, 999999, tzinfo=datetime.UTC)


class RateTableFactory(IRateTableFactory):

    def create(self,
               rate_table_data: RateTableData,
               durations: set[timedelta],
               group_sizes: set[int]) -> RateTable:
        rate_table = RateTable(
            uuid=uuid4(),
            valid_from=rate_table_data.valid_from if rate_table_data.valid_from else _MIN_DATETIME,
            valid_to=rate_table_data.valid_to if rate_table_data.valid_to else _MAX_DATETIME,
            rates=rate_table_data.rates,
        )

        _RateTableValidator(
            rate_table=rate_table,
            durations=durations,
            group_sizes=group_sizes
        )

        return rate_table
