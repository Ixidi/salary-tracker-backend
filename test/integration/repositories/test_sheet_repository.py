from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy import select

from salary_tracker.data.exceptions import DataException
from salary_tracker.data.model import DatabaseUser, DatabaseSheet, DatabaseSheetDuration, DatabaseSheetGroupSize
from salary_tracker.data.repositories.sheet.sheet_repository import SheetRepository
from salary_tracker.domain.pagination import PaginatedRequest, PageParams
from salary_tracker.domain.sheet.models import Sheet


@pytest.fixture
async def database_user(session):
    database_user = DatabaseUser(
        uuid=uuid4(),
        email='test@test.com',
        name='Test User'
    )
    session.add(database_user)
    await session.commit()

    return database_user


@pytest.fixture
def sheet_repository(session):
    return SheetRepository(session=session)


async def test_get_by_uuid_exists(sheet_repository, database_user, session):
    expected = Sheet(
        uuid=uuid4(),
        owner_user_uuid=database_user.uuid,
        title="Test Sheet",
        description="Test Description",
        durations={timedelta(hours=1), timedelta(hours=4)},
        group_sizes={2, 5}
    )

    session.add(DatabaseSheet(
        uuid=expected.uuid,
        owner_user_uuid=expected.owner_user_uuid,
        title=expected.title,
        description=expected.description,
        durations=[DatabaseSheetDuration(duration=duration) for duration in expected.durations],
        group_sizes=[DatabaseSheetGroupSize(group_size=group_size) for group_size in expected.group_sizes]
    ))
    await session.commit()

    result = await sheet_repository.get_by_uuid(expected.uuid)

    assert result == expected


async def test_get_by_uuid_not_exists(sheet_repository):
    result = await sheet_repository.get_by_uuid(uuid4())

    assert result is None


async def test_get_by_owner_paginated(sheet_repository, database_user, session):
    expected = [
        Sheet(
            uuid=uuid4(),
            owner_user_uuid=database_user.uuid,
            title="Test Sheet",
            description="Test Description",
            durations={timedelta(hours=1)},
            group_sizes={2}
        ),
        Sheet(
            uuid=uuid4(),
            owner_user_uuid=database_user.uuid,
            title="Test Sheet 2",
            description="Test Description 2",
            durations={timedelta(hours=3)},
            group_sizes={1}
        ),
        Sheet(
            uuid=uuid4(),
            owner_user_uuid=database_user.uuid,
            title="Test Sheet 3",
            description="Test Description 3",
            durations={timedelta(hours=4)},
            group_sizes={6}
        ),
        Sheet(
            uuid=uuid4(),
            owner_user_uuid=database_user.uuid,
            title="Test Sheet 4",
            description="Test Description 4",
            durations={timedelta(hours=5)},
            group_sizes={7}
        )
    ]

    for sheet in expected:
        session.add(DatabaseSheet(
            uuid=sheet.uuid,
            owner_user_uuid=sheet.owner_user_uuid,
            title=sheet.title,
            description=sheet.description,
            durations=[DatabaseSheetDuration(duration=duration) for duration in sheet.durations],
            group_sizes=[DatabaseSheetGroupSize(group_size=group_size) for group_size in sheet.group_sizes]
        ))
    await session.commit()

    first_page_result = await sheet_repository.get_by_owner_paginated(
        PaginatedRequest(
            filters=database_user.uuid,
            page_params=PageParams(
                page=0,
                per_page=2
            )
        )
    )

    second_page_result = await sheet_repository.get_by_owner_paginated(
        PaginatedRequest(
            filters=database_user.uuid,
            page_params=PageParams(
                page=1,
                per_page=2
            )
        )
    )

    third_page_result = await sheet_repository.get_by_owner_paginated(
        PaginatedRequest(
            filters=database_user.uuid,
            page_params=PageParams(
                page=2,
                per_page=2
            )
        )
    )

    assert first_page_result.items == expected[:2]
    assert second_page_result.items == expected[2:]
    assert third_page_result.items == []


async def test_upsert_create(sheet_repository, database_user, session):
    sheet = Sheet(
        uuid=uuid4(),
        owner_user_uuid=database_user.uuid,
        title="Test Sheet",
        description="Test Description",
        durations={timedelta(hours=1)},
        group_sizes={2}
    )

    result = await sheet_repository.upsert(sheet)
    db_result = (await session.execute(
        select(DatabaseSheet).filter_by(uuid=sheet.uuid)
    )).scalar_one()

    assert result == sheet
    assert db_result.uuid == sheet.uuid
    assert db_result.owner_user_uuid == sheet.owner_user_uuid
    assert db_result.title == sheet.title
    assert db_result.description == sheet.description
    assert {duration.duration for duration in db_result.durations} == sheet.durations
    assert {group_size.group_size for group_size in db_result.group_sizes} == sheet.group_sizes


async def test_upsert_update(sheet_repository, database_user, session):
    sheet = Sheet(
        uuid=uuid4(),
        owner_user_uuid=database_user.uuid,
        title="Test Sheet",
        description="Test Description",
        durations={timedelta(hours=1)},
        group_sizes={2}
    )

    session.add(DatabaseSheet(
        uuid=sheet.uuid,
        owner_user_uuid=sheet.owner_user_uuid,
        title="Old Title",
        description="Old Description",
        durations=[DatabaseSheetDuration(duration=timedelta(hours=2))],
        group_sizes=[DatabaseSheetGroupSize(group_size=3)]
    ))
    await session.commit()

    result = await sheet_repository.upsert(sheet)
    db_result = (await session.execute(
        select(DatabaseSheet).filter_by(uuid=sheet.uuid)
    )).scalar_one()

    assert result == sheet
    assert db_result.uuid == sheet.uuid
    assert db_result.owner_user_uuid == sheet.owner_user_uuid
    assert db_result.title == sheet.title
    assert db_result.description == sheet.description
    assert {duration.duration for duration in db_result.durations} == sheet.durations
    assert {group_size.group_size for group_size in db_result.group_sizes} == sheet.group_sizes


async def test_delete_exists(sheet_repository, session, database_user):
    uuid = uuid4()
    session.add(DatabaseSheet(
        uuid=uuid,
        owner_user_uuid=database_user.uuid,
        title="Test Sheet",
        description="Test Description",
        durations=[DatabaseSheetDuration(duration=timedelta(hours=1))],
        group_sizes=[DatabaseSheetGroupSize(group_size=2)]
    ))
    await session.commit()

    await sheet_repository.delete(uuid)

    result = (await session.execute(select(DatabaseSheet).filter_by(uuid=uuid))).scalar_one_or_none()
    assert result is None


async def test_delete_not_exists(sheet_repository):
    uuid = uuid4()

    with pytest.raises(DataException):
        await sheet_repository.delete(uuid)