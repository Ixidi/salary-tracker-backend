import uuid
from datetime import datetime, UTC

import pytest
from sqlalchemy import select

from salary_tracker.domain.auth.models import RefreshToken
from salary_tracker.data.model import DatabaseUserRefreshToken, DatabaseUser
from salary_tracker.data.repositories.auth.refresh_token_repository import RefreshTokenRepository

@pytest.fixture
async def database_user(session):
    database_user = DatabaseUser(
        uuid=uuid.uuid4(),
        email='test@test.com',
        name='Test User'
    )
    session.add(database_user)
    await session.commit()

    return database_user

@pytest.fixture
def refresh_token_repository(session):
    return RefreshTokenRepository(session=session)

async def test_get_refresh_token_exists(refresh_token_repository, session, database_user):
    expected_token = RefreshToken(
        token="Test Token",
        user_uuid=database_user.uuid,
        user_agent="Test User Agent",
        expires_at=datetime(2022, 1, 1, tzinfo=UTC)
    )
    session.add(DatabaseUserRefreshToken(
        token=expected_token.token,
        user_uuid=expected_token.user_uuid,
        user_agent=expected_token.user_agent,
        expires_at=expected_token.expires_at
    ))
    await session.commit()

    result = await refresh_token_repository.get_by_token(expected_token.token)

    assert result == expected_token

async def test_get_refresh_token_does_not_exist(refresh_token_repository):
    token = "Test Token"

    result = await refresh_token_repository.get_by_token(token)

    assert result is None

async def test_upsert_update(refresh_token_repository, session, database_user):
    old_token = RefreshToken(
        token="Token",
        user_uuid=database_user.uuid,
        user_agent="Old User Agent",
        expires_at=datetime(2022, 1, 1, tzinfo=UTC)
    )

    expected_token = RefreshToken(
        token="Token",
        user_uuid=database_user.uuid,
        user_agent=old_token.user_agent,
        expires_at=old_token.expires_at
    )

    session.add(DatabaseUserRefreshToken(
        token=old_token.token,
        user_uuid=old_token.user_uuid,
        user_agent=old_token.user_agent,
        expires_at=old_token.expires_at
    ))
    await session.commit()

    await refresh_token_repository.upsert(expected_token)

    result = await session.execute(select(DatabaseUserRefreshToken).filter_by(token=expected_token.token))
    scalar = result.scalar_one()

    assert scalar.token == expected_token.token
    assert scalar.user_uuid == expected_token.user_uuid
    assert scalar.user_agent == expected_token.user_agent
    assert scalar.expires_at == expected_token.expires_at

async def test_upsert_insert(refresh_token_repository, session, database_user):
    expected_token = RefreshToken(
        token="Token",
        user_uuid=database_user.uuid,
        user_agent="Old User Agent",
        expires_at=datetime(2022, 1, 1, tzinfo=UTC)
    )

    await refresh_token_repository.upsert(expected_token)

    result = await session.execute(select(DatabaseUserRefreshToken).filter_by(token=expected_token.token))
    scalar = result.scalar_one()

    assert scalar.token == expected_token.token
    assert scalar.user_uuid == expected_token.user_uuid
    assert scalar.user_agent == expected_token.user_agent
    assert scalar.expires_at == expected_token.expires_at

async def test_delete(refresh_token_repository, session, database_user):
    session.add(DatabaseUserRefreshToken(
        token="Token",
        user_uuid=database_user.uuid,
        user_agent="User Agent",
        expires_at=datetime(2022, 1, 1, tzinfo=UTC)
    ))
    await session.commit()

    await refresh_token_repository.delete("Token")

    result = (await session.execute(select(DatabaseUserRefreshToken).filter_by(token="Token"))).scalar_one_or_none()

    assert result is None