from datetime import timedelta
from uuid import UUID

from pydantic import BaseModel, PositiveInt, AwareDatetime, field_validator, conset, conlist, condecimal
from pydantic_core.core_schema import ValidationInfo
from sqlmodel import SQLModel


class Rate(BaseModel):
    rate: condecimal(ge=0)
    group_size: PositiveInt
    duration: timedelta


class RateTable(BaseModel):
    valid_from: AwareDatetime
    valid_to: AwareDatetime | None
    durations: conset(timedelta, min_length=1)
    group_sizes: conset(PositiveInt, min_length=1)
    rates: conlist(Rate, min_length=1)

    @field_validator("valid_to")
    def check_valid_to(cls, v, info: ValidationInfo):
        if v is not None and v < info.data["valid_from"]:
            raise ValueError("valid_to must be greater than or equal to valid_from")
        return v

    @field_validator("rates")
    def check_rates(cls, v, info: ValidationInfo):
        if len(v) != len(info.data["group_sizes"]) * len(info.data["durations"]):
            raise ValueError("Rates must be provided for all group sizes and durations")

        for rate in v:
            if rate.group_size not in info.data["group_sizes"]:
                raise ValueError(f"Group size {rate.group_size} is not in group_sizes")
            if rate.duration not in info.data["durations"]:
                raise ValueError(f"Duration {rate.duration} is not in durations")
        return v


class Record(BaseModel):
    duration: timedelta
    group_size: PositiveInt
    group_name: str
    happened_at: AwareDatetime
    additional_info: str | None


class SheetBase(BaseModel):
    title: str
    description: str
    rate_tables: conlist(RateTable, min_length=1)

    @field_validator("rate_tables")
    def check_rate_tables(cls, v):
        current = [x for x in v if x.valid_to is None]
        if len(current) > 1:
            raise ValueError("Only one rate table can be current (valid_to is None)")

        if len(current) == 0:
            raise ValueError("At least one rate table must be current (valid_to is None)")

        for i in range(len(v)):
            for j in range(i + 1, len(v)):
                if v[i].valid_to is not None and v[j].valid_to is not None:
                    if v[i].valid_from < v[j].valid_to and v[i].valid_to > v[j].valid_from:
                        raise ValueError("Rate tables cannot overlap")

        return v


class Sheet(SheetBase):
    uuid: UUID
    records: list[Record]
    owner_user_uuid: UUID


class NewSheetData(SheetBase):
    owner_user_uuid: UUID
