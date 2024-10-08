from uuid import uuid4

import pytest
from sqlalchemy import select

from salary_tracker.domain.user.models import User
from salary_tracker.data.model import DatabaseUser
from salary_tracker.data.repositories.user.user_repository import UserRepository


@pytest.fixture
def user_repository(session):
    return UserRepository(session=session)

async def test_get_by_uuid_exists(user_repository, session):
    user = User(
        uuid=uuid4(),
        name="John Doe",
        email="mail@example.com"
    )

    session.add(DatabaseUser(
        uuid=user.uuid,
        name=user.name,
        email=user.email
    ))
    await session.commit()

    result = await user_repository.get_by_uuid(user.uuid)

    assert result == user

async def test_get_by_uuid_not_exists(user_repository):
    result = await user_repository.get_by_uuid(uuid4())

    assert result is None

async def test_upsert_create(user_repository, session):
    user = User(
        uuid=uuid4(),
        name="John Doe",
        email="maile@example.com"
    )

    result = await user_repository.upsert(user)
    db_result = (await session.execute(select(DatabaseUser).filter_by(uuid=user.uuid))).scalar_one()

    assert result == user
    assert db_result.uuid == user.uuid
    assert db_result.name == user.name
    assert db_result.email == user.email

async def test_upsert_update(user_repository, session):
    user = User(
        uuid=uuid4(),
        name="John Doe",
        email="mail@example.com"
    )

    session.add(DatabaseUser(
        uuid=user.uuid,
        name="Another Joe",
        email="old@example.com"
    ))
    await session.commit()

    result = await user_repository.upsert(user)
    db_result = (await session.execute(select(DatabaseUser).filter_by(uuid=user.uuid))).scalar_one()

    assert result == user
    assert db_result.uuid == user.uuid
    assert db_result.name == user.name
    assert db_result.email == user.email