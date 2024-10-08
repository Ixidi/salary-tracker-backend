from datetime import datetime, timedelta, UTC
from decimal import Decimal
from typing import List
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, func, TypeDecorator
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship

from salary_tracker.domain.auth.models import AuthProvider


class TZDateTime(TypeDecorator):
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value == datetime.max:
            return 'infinity'
        if value == datetime.min:
            return '-infinity'
        return value

    def process_result_value(self, value, dialect):
        if value == 'infinity':
            return datetime.max.replace(tzinfo=UTC)
        if value == '-infinity':
            return datetime.min.replace(tzinfo=UTC)
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(type_=TZDateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(type_=TZDateTime, server_default=func.now(),
                                                 server_onupdate=func.now())


class DatabaseUser(Base):
    __tablename__ = 'users'

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(index=True, unique=True)
    name: Mapped[str]


class DatabaseUserRefreshToken(Base):
    __tablename__ = 'user_refresh_tokens'

    user_uuid: Mapped[UUID] = mapped_column(ForeignKey('users.uuid'), primary_key=True)
    token: Mapped[str] = mapped_column(primary_key=True)
    expires_at: Mapped[datetime] = mapped_column(TZDateTime)


class DatabaseUserExternalAccount(Base):
    __tablename__ = 'user_external_accounts'

    provider: Mapped[AuthProvider] = mapped_column(primary_key=True)
    user_uuid: Mapped[UUID] = mapped_column(ForeignKey('users.uuid'), primary_key=True)
    external_id: Mapped[str]


class DatabaseSheetDuration(Base):
    __tablename__ = 'sheet_durations'

    sheet_uuid: Mapped[UUID] = mapped_column(ForeignKey('sheets.uuid'), primary_key=True)
    duration: Mapped[timedelta] = mapped_column(primary_key=True)


class DatabaseSheetGroupSize(Base):
    __tablename__ = 'sheet_group_sizes'

    sheet_uuid: Mapped[UUID] = mapped_column(ForeignKey('sheets.uuid'), primary_key=True)
    group_size: Mapped[int] = mapped_column(primary_key=True)


class DatabaseSheetRecord(Base):
    __tablename__ = 'sheet_records'

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    sheet_uuid: Mapped[UUID] = mapped_column(ForeignKey('sheets.uuid'))
    duration: Mapped[timedelta]
    group_size: Mapped[int]
    group_name: Mapped[str]
    happened_at: Mapped[datetime] = mapped_column(TZDateTime)
    additional_info: Mapped[str | None]


class DatabaseSheetRate(Base):
    __tablename__ = 'sheet_rates'

    rate_table_uuid: Mapped[UUID] = mapped_column(ForeignKey('sheet_rate_tables.uuid'), primary_key=True)
    group_size: Mapped[int] = mapped_column(primary_key=True)
    duration: Mapped[timedelta] = mapped_column(primary_key=True)
    rate: Mapped[Decimal]


class DatabaseSheetRateTable(Base):
    __tablename__ = 'sheet_rate_tables'

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    sheet_uuid: Mapped[UUID] = mapped_column(ForeignKey('sheets.uuid'))
    valid_from: Mapped[datetime] = mapped_column(TZDateTime)
    valid_to: Mapped[datetime] = mapped_column(TZDateTime)

    rates: Mapped[List[DatabaseSheetRate]] = relationship(lazy="selectin", cascade="all, delete-orphan")


class DatabaseSheet(Base):
    __tablename__ = 'sheets'

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    owner_user_uuid: Mapped[UUID] = mapped_column(ForeignKey('users.uuid'))
    title: Mapped[str]
    description: Mapped[str]

    durations: Mapped[List[DatabaseSheetDuration]] = relationship(lazy="selectin", cascade="all, delete-orphan")
    group_sizes: Mapped[List[DatabaseSheetGroupSize]] = relationship(lazy="selectin", cascade="all, delete-orphan")
    rate_tables: Mapped[List[DatabaseSheetRateTable]] = relationship(lazy="selectin", cascade="all, delete-orphan")
    records: Mapped[List[DatabaseSheetRecord]] = relationship(lazy="selectin", cascade="all, delete-orphan")
