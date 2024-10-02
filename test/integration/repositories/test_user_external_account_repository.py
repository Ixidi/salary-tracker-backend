from uuid import uuid4

import pytest
from sqlalchemy import select

from salary_tracker.domain.auth.models import UserExternalAccount, AuthProvider
from salary_tracker.data.model import DatabaseUserExternalAccount, DatabaseUser
from salary_tracker.data.repositories.user_external_account_repository import UserExternalAccountRepository


@pytest.fixture
def user_external_account_repository(session):
    return UserExternalAccountRepository(session=session)

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

async def test_get_by_external_id_exists(user_external_account_repository, session, database_user):
    user_external_account = UserExternalAccount(
        external_id="123",
        provider=AuthProvider.GOOGLE,
        user_uuid=database_user.uuid
    )

    session.add(DatabaseUserExternalAccount(
        external_id=user_external_account.external_id,
        provider=user_external_account.provider,
        user_uuid=user_external_account.user_uuid
    ))
    await session.commit()

    result = await user_external_account_repository.get_by_external_id(
        user_external_account.external_id,
        user_external_account.provider
    )

    assert result == user_external_account

async def test_get_by_external_id_does_not_exist(user_external_account_repository):
    external_id = "123"
    provider = AuthProvider.GOOGLE

    result = await user_external_account_repository.get_by_external_id(external_id, provider)

    assert result is None

async def test_create(user_external_account_repository, session, database_user):
    user_external_account = UserExternalAccount(
        external_id="123",
        provider=AuthProvider.GOOGLE,
        user_uuid=database_user.uuid
    )

    result = await user_external_account_repository.create(user_external_account)
    db_result = (await session.execute(
        select(DatabaseUserExternalAccount).filter_by(
            external_id=user_external_account.external_id,
            provider=user_external_account.provider
        )
    )).scalar_one()

    assert result == user_external_account
    assert db_result.external_id == user_external_account.external_id
    assert db_result.provider == user_external_account.provider
    assert db_result.user_uuid == user_external_account.user_uuid