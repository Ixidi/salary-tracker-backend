import asyncio
from contextlib import asynccontextmanager
from uuid import UUID, uuid4

import pytest
from asgi_lifespan import LifespanManager
from dotenv import load_dotenv
from httpx import AsyncClient, ASGITransport

from salary_tracker.domain.user.models import User
from salary_tracker.data.database import Database
from sqlmodel import SQLModel

from salary_tracker.data.model import DatabaseUser
from salary_tracker.presentation.dependencies.auth import get_current_user_uuid
from salary_tracker.presentation.dependencies.data import get_database
from salary_tracker.presentation.dependencies.presentation import get_settings
from salary_tracker.presentation.main import create_app
from salary_tracker.presentation.settings import AppSettings

@pytest.fixture(scope="session")
def settings():
    load_dotenv(".env.test", override=True, verbose=True)
    return AppSettings()

@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def database(settings):
    database = Database(database_url=settings.database_url.unicode_string())
    async with database.connect() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)
    yield database
    async with database.connect() as connection:
        await connection.run_sync(SQLModel.metadata.drop_all)
    await database.close()

@pytest.fixture
async def session(database):
    async with database.session() as session:
        try:
            yield session
        finally:
            await session.close()

@pytest.fixture
async def app(database, settings):
    app = create_app(settings)
    async with LifespanManager(app=app):
        app.dependency_overrides[get_settings] = lambda: settings
        app.dependency_overrides[get_database] = lambda: database
        yield app

@pytest.fixture
async def client(app):
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
    ) as c:
        yield c


@pytest.fixture
async def provide_logged_in_user(app, session):
    user = User(
        uuid=uuid4(),
        email="test@example.com",
        name="Test User"
    )
    session.add(
        DatabaseUser(
            uuid=user.uuid,
            email=user.email,
            name=user.name
        )
    )
    await session.commit()

    @asynccontextmanager
    async def logged_in_user() -> UUID:
        previous = app.dependency_overrides.get(get_current_user_uuid)
        app.dependency_overrides[get_current_user_uuid] = lambda: user.uuid

        yield user

        app.dependency_overrides[get_current_user_uuid] = previous

    return logged_in_user

