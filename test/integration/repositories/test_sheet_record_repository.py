from datetime import timedelta, datetime, UTC
from uuid import uuid4

import pytest
from sqlalchemy import select

from salary_tracker.data.model import DatabaseUser, DatabaseSheet, DatabaseSheetDuration, DatabaseSheetGroupSize, \
    DatabaseSheetRecord
from salary_tracker.data.repositories.sheet.sheet_record_repository import SheetRecordRepository
from salary_tracker.domain.pagination import PaginatedRequest, PageParams
from salary_tracker.domain.sheet.models import Record, SheetRecordFilters


@pytest.fixture
def sheet_record_repository(session):
    return SheetRecordRepository(session=session)


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


async def test_get_by_uuid_exists(sheet_record_repository, database_sheet, session):
    record = Record(
        uuid=uuid4(),
        group_size=2,
        duration=timedelta(hours=1),
        group_name="Test Group",
        happened_at=datetime(2021, 1, 1, 12, 0, tzinfo=UTC),
        additional_info="Test Additional Info"
    )

    session.add(DatabaseSheetRecord(
        uuid=record.uuid,
        sheet_uuid=database_sheet.uuid,
        group_size=record.group_size,
        duration=record.duration,
        group_name=record.group_name,
        happened_at=record.happened_at,
        additional_info=record.additional_info
    ))

    await session.commit()

    result = await sheet_record_repository.get_by_uuid(database_sheet.uuid, record.uuid)

    assert result == record


async def test_get_by_uuid_not_exists(sheet_record_repository, database_sheet):
    result = await sheet_record_repository.get_by_uuid(database_sheet.uuid, uuid4())

    assert result is None


async def test_get_paginated(sheet_record_repository, database_sheet, session):
    records = [
        Record(
            uuid=uuid4(),
            group_size=2,
            duration=timedelta(hours=1),
            group_name="Test Group",
            happened_at=datetime(2021, 1, 1, 12, 0, tzinfo=UTC),
            additional_info="Test Additional Info"
        ),
        Record(
            uuid=uuid4(),
            group_size=5,
            duration=timedelta(hours=4),
            group_name="Test Group 2",
            happened_at=datetime(2021, 1, 2, 12, 0, tzinfo=UTC),
            additional_info="Test Additional Info 2"
        ),
        Record(
            uuid=uuid4(),
            group_size=2,
            duration=timedelta(hours=1),
            group_name="Test Group 3",
            happened_at=datetime(2021, 1, 3, 12, 0, tzinfo=UTC),
            additional_info="Test Additional Info 3"
        )
    ]

    for record in records:
        session.add(DatabaseSheetRecord(
            uuid=record.uuid,
            sheet_uuid=database_sheet.uuid,
            group_size=record.group_size,
            duration=record.duration,
            group_name=record.group_name,
            happened_at=record.happened_at,
            additional_info=record.additional_info
        ))

    await session.commit()

    async def get_paginated(page: int):
        return await sheet_record_repository.get_paginated(
            PaginatedRequest(
                page_params=PageParams(page=page, per_page=2),
                filters=SheetRecordFilters(
                    sheet_uuid=database_sheet.uuid,
                    datetime_from=datetime(2021, 1, 1, 0, 0, tzinfo=UTC),
                    datetime_to=datetime(2021, 2, 2, 0, 0, tzinfo=UTC)
                )
            )
        )

    first_page = await get_paginated(0)
    assert first_page.items == records[:2]

    second_page = await get_paginated(1)
    assert second_page.items == records[2:]

    third_page = await get_paginated(3)
    assert third_page.items == []


async def test_add(sheet_record_repository, database_sheet, session):
    record = Record(
        uuid=uuid4(),
        group_size=2,
        duration=timedelta(hours=1),
        group_name="Test Group",
        happened_at=datetime(2021, 1, 1, 12, 0, tzinfo=UTC),
        additional_info="Test Additional Info"
    )

    result = await sheet_record_repository.add(database_sheet.uuid, record)

    assert result == record

    record_db = (await session.execute(select(DatabaseSheetRecord).filter_by(uuid=record.uuid))).scalar_one()
    assert record_db.sheet_uuid == database_sheet.uuid
    assert record_db.group_size == record.group_size
    assert record_db.duration == record.duration
    assert record_db.group_name == record.group_name
    assert record_db.happened_at == record.happened_at
    assert record_db.additional_info == record.additional_info


async def test_delete_exists(sheet_record_repository, database_sheet, session):
    record = Record(
        uuid=uuid4(),
        group_size=2,
        duration=timedelta(hours=1),
        group_name="Test Group",
        happened_at=datetime(2021, 1, 1, 12, 0, tzinfo=UTC),
        additional_info="Test Additional Info"
    )

    session.add(DatabaseSheetRecord(
        uuid=record.uuid,
        sheet_uuid=database_sheet.uuid,
        group_size=record.group_size,
        duration=record.duration,
        group_name=record.group_name,
        happened_at=record.happened_at,
        additional_info=record.additional_info
    ))
    await session.commit()

    await sheet_record_repository.delete(database_sheet.uuid, record.uuid)

    result = (await session.execute(select(DatabaseSheetRecord).filter_by(uuid=record.uuid))).scalar_one_or_none()

    assert result is None


async def test_delete_not_exists(sheet_record_repository, database_sheet):
    with pytest.raises(Exception):
        await sheet_record_repository.delete(database_sheet.uuid, uuid4())