from datetime import timedelta
from uuid import UUID

from pydantic import BaseModel, PositiveInt, AwareDatetime, conset, conlist, condecimal, \
    model_validator

from salary_tracker.domain.exceptions import DomainException


class Rate(BaseModel):
    rate: condecimal(ge=0, decimal_places=2)
    group_size: PositiveInt
    duration: timedelta


class RateTable(BaseModel):
    uuid: UUID
    valid_from: AwareDatetime
    valid_to: AwareDatetime
    rates: conlist(Rate, min_length=1)

    @model_validator(mode='after')
    def check_model(self):
        if self.valid_to <= self.valid_from:
            raise ValueError("valid_to must be greater than or equal to valid_from")
        return self

    def get_salary(self, group_size: PositiveInt, duration: timedelta) -> condecimal(ge=0, decimal_places=2):
        for rate in self.rates:
            if rate.group_size == group_size and rate.duration == duration:
                return rate.rate

        raise DomainException(f"Rate not found for group_size={group_size} and duration={duration}")


class Record(BaseModel):
    uuid: UUID
    duration: timedelta
    group_size: PositiveInt
    group_name: str
    happened_at: AwareDatetime
    additional_info: str | None


class Sheet(BaseModel):
    uuid: UUID
    durations: conset(timedelta, min_length=1)
    group_sizes: conset(PositiveInt, min_length=1)
    owner_user_uuid: UUID
    title: str
    description: str


class RateTableData(BaseModel):
    valid_from: AwareDatetime | None
    valid_to: AwareDatetime | None
    rates: list[Rate]


class NewRecordData(BaseModel):
    duration: timedelta
    group_size: PositiveInt
    group_name: str
    happened_at: AwareDatetime
    additional_info: str | None


class NewSheetData(BaseModel):
    owner_user_uuid: UUID
    title: str
    description: str
    durations: set[timedelta]
    group_sizes: set[PositiveInt]
    rates: list[Rate]


class SheetRecordFilters(BaseModel):
    sheet_uuid: UUID
    datetime_from: AwareDatetime | None
    datetime_to: AwareDatetime | None


class Salary(BaseModel):
    datetime_from: AwareDatetime
    datetime_to: AwareDatetime
    salary: condecimal(ge=0, decimal_places=2)
