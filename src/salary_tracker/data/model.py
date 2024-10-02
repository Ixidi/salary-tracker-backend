from datetime import datetime, UTC, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime
from sqlmodel import SQLModel, Field, Relationship

from salary_tracker.domain.auth.models import AuthProvider

TZDateTime = DateTime(timezone=True)


class Base(SQLModel):
    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=TZDateTime
    )

    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=TZDateTime,
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(UTC),
        },
    )


class DatabaseUser(Base, table=True):
    __tablename__ = 'users'

    uuid: UUID = Field(primary_key=True)
    email: str = Field(index=True, unique=True)
    name: str


class DatabaseUserRefreshToken(Base, table=True):
    __tablename__ = 'user_refresh_tokens'

    user_uuid: UUID = Field(primary_key=True, foreign_key='users.uuid')
    token: str = Field(primary_key=True)
    user_agent: str
    expires_at: datetime = Field(sa_type=TZDateTime)


class DatabaseUserExternalAccount(Base, table=True):
    __tablename__ = 'user_external_accounts'

    provider: AuthProvider = Field(primary_key=True)
    user_uuid: UUID = Field(primary_key=True, foreign_key='users.uuid')
    external_id: str


class DatabaseRateTableDuration(Base, table=True):
    __tablename__ = 'sheet_rate_table_durations'

    rate_table_uuid: UUID = Field(foreign_key='sheet_rate_tables.uuid')
    duration: timedelta = Field(primary_key=True)


class DatabaseRateTableGroupSize(Base, table=True):
    __tablename__ = 'sheet_rate_table_group_sizes'

    rate_table_uuid: UUID = Field(foreign_key='sheet_rate_tables.uuid')
    group_size: int = Field(primary_key=True)


class DatabaseRateTableRate(Base, table=True):
    __tablename__ = 'sheet_rate_table_rates'

    rate_table_uuid: UUID = Field(foreign_key='sheet_rate_tables.uuid', primary_key=True)
    group_size: int = Field(primary_key=True)
    duration: timedelta = Field(primary_key=True)

    rate: Decimal


class DatabaseRateTable(Base, table=True):
    __tablename__ = 'sheet_rate_tables'

    uuid: UUID = Field(primary_key=True)
    sheet_uuid: UUID = Field(foreign_key='sheets.uuid')

    valid_from: datetime = Field(sa_type=TZDateTime)
    valid_to: datetime = Field(sa_type=TZDateTime)

    durations: list[DatabaseRateTableDuration] = Relationship(cascade_delete=True)
    group_sizes: list[DatabaseRateTableGroupSize] = Relationship(cascade_delete=True)
    rates: list[DatabaseRateTableRate] = Relationship(cascade_delete=True)


class DatabaseSheetRecord(Base, table=True):
    __tablename__ = 'sheet_records'

    uuid: UUID = Field(primary_key=True)
    sheet_uuid: UUID = Field(foreign_key='sheets.uuid')

    duration: timedelta
    group_size: int
    group_name: str
    happened_at: datetime = Field(sa_type=TZDateTime)
    additional_info: str | None


class DatabaseSheet(Base, table=True):
    __tablename__ = 'sheets'

    uuid: UUID = Field(primary_key=True)
    owner_user_uuid: UUID = Field(foreign_key='users.uuid')
    title: str
    description: str

    rate_tables: list[DatabaseRateTable] = Relationship(cascade_delete=True)
    records: list[DatabaseSheetRecord] = Relationship(cascade_delete=True)
