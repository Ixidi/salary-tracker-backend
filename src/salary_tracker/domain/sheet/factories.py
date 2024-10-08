from abc import ABC, abstractmethod

from asyncpg.pgproto.pgproto import timedelta

from salary_tracker.domain.sheet.models import RateTable, RateTableData


class IRateTableFactory(ABC):

    @abstractmethod
    def create(
            self,
            rate_table_data: RateTableData,
            durations: set[timedelta],
            group_sizes: set[int]
    ) -> RateTable:
        pass
