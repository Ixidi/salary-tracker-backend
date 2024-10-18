from datetime import timedelta, UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import select

from salary_tracker.data.exceptions import DataException
from salary_tracker.data.model import DatabaseUser, DatabaseSheet, DatabaseSheetDuration, DatabaseSheetGroupSize, \
    DatabaseSheetRateTable, DatabaseSheetRate
from salary_tracker.data.repositories.sheet.rate_table_repository import RateTableRepository
from salary_tracker.data.repositories.sheet.sheet_record_repository import SheetRecordRepository
from salary_tracker.domain.sheet.models import RateTable, Rate


@pytest.fixture
async def database_sheet(session):
    database_user = DatabaseUser(
        uuid=uuid4(),
        email='test@test.com',
        name='Test User'
    )
    session.add(database_user)
    await session.commit()

    database_sheet = DatabaseSheet(
        uuid=uuid4(),
        owner_user_uuid=database_user.uuid,
        title="Test Sheet",
        description="Test Description",
        durations=[
            DatabaseSheetDuration(duration=timedelta(hours=1)),
            DatabaseSheetDuration(duration=timedelta(hours=4))
        ],
        group_sizes=[
            DatabaseSheetGroupSize(group_size=2),
            DatabaseSheetGroupSize(group_size=5)
        ],
        rate_tables=[],
        records=[]
    )
    session.add(database_sheet)
    await session.commit()

    return database_sheet


@pytest.fixture
async def rate_table_repository(session):
    return RateTableRepository(session=session)

async def test_get_for_datetime_range(rate_table_repository, database_sheet, session):
    border_date = datetime(2021, 1, 1, 1, 1, 1, tzinfo=UTC)
    rate_tables = [
        RateTable(
            uuid=uuid4(),
            valid_from=datetime.min.replace(tzinfo=UTC),
            valid_to=border_date,
            rates=[Rate(
                rate=Decimal('10.00'),
                group_size=2,
                duration=timedelta(hours=1)
            )]
        ),
        RateTable(
            uuid=uuid4(),
            valid_from=border_date + timedelta(microseconds=1),
            valid_to=datetime.max.replace(tzinfo=UTC),
            rates=[Rate(
                rate=Decimal('10.00'),
                group_size=2,
                duration=timedelta(hours=1)
            )]
        )
    ]

    for rate_table in rate_tables:
        session.add(DatabaseSheetRateTable(
            sheet_uuid=database_sheet.uuid,
            uuid=rate_table.uuid,
            valid_from=rate_table.valid_from,
            valid_to=rate_table.valid_to,
            rates=[
                DatabaseSheetRate(
                    rate=rate.rate,
                    group_size=rate.group_size,
                    duration=rate.duration
                ) for rate in rate_table.rates
            ]
        ))

    await session.commit()

    result = await rate_table_repository.get_for_datetime(database_sheet.uuid, border_date)

    assert result == rate_tables[0]


async def test_get_for_datetime_no_rate_table(rate_table_repository, database_sheet):
    with pytest.raises(DataException):
        await rate_table_repository.get_for_datetime(database_sheet.uuid, datetime(2021, 1, 1, 1, 1, 1, tzinfo=UTC))

async def test_get_for_sheet(rate_table_repository, database_sheet, session):
    rate_tables = [
        RateTable(
            uuid=uuid4(),
            valid_from=datetime.min.replace(tzinfo=UTC),
            valid_to=datetime.max.replace(tzinfo=UTC),
            rates=[Rate(
                rate=Decimal('10.00'),
                group_size=2,
                duration=timedelta(hours=1)
            )]
        )
    ]

    for rate_table in rate_tables:
        session.add(DatabaseSheetRateTable(
            sheet_uuid=database_sheet.uuid,
            uuid=rate_table.uuid,
            valid_from=rate_table.valid_from,
            valid_to=rate_table.valid_to,
            rates=[
                DatabaseSheetRate(
                    rate=rate.rate,
                    group_size=rate.group_size,
                    duration=rate.duration
                ) for rate in rate_table.rates
            ]
        ))

    await session.commit()

    result = await rate_table_repository.get_for_sheet(database_sheet.uuid)

    assert result == rate_tables

async def test_upsert(rate_table_repository, database_sheet, session):
    border_date = datetime(2021, 1, 1, 1, 1, 1, tzinfo=UTC)
    rate_tables = [
        RateTable(
            uuid=uuid4(),
            valid_from=datetime.min.replace(tzinfo=UTC),
            valid_to=border_date,
            rates=[Rate(
                rate=Decimal('10.00'),
                group_size=2,
                duration=timedelta(hours=1)
            )]
        )
    ]

    result = await rate_table_repository.upsert(database_sheet.uuid, rate_tables)
    db_result = (await session.execute(select(DatabaseSheetRateTable).filter_by(sheet_uuid=database_sheet.uuid))).scalars().all()

    assert result == rate_tables
    assert len(db_result) == 1
    assert db_result[0].uuid == rate_tables[0].uuid
    assert db_result[0].valid_from == rate_tables[0].valid_from
    assert db_result[0].valid_to == rate_tables[0].valid_to
    assert len(db_result[0].rates) == 1
    assert db_result[0].rates[0].rate == rate_tables[0].rates[0].rate
    assert db_result[0].rates[0].group_size == rate_tables[0].rates[0].group_size
    assert db_result[0].rates[0].duration == rate_tables[0].rates[0].duration


async def test_upsert_sheet_not_found(rate_table_repository):
    with pytest.raises(DataException):
        await rate_table_repository.upsert(uuid4(), [])