from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from salary_tracker.data.database import Database
from salary_tracker.data.repositories.auth.refresh_token_repository import RefreshTokenRepository
from salary_tracker.data.repositories.auth.user_external_account_repository import UserExternalAccountRepository
from salary_tracker.data.repositories.sheet.rate_table_repository import RateTableRepository
from salary_tracker.data.repositories.sheet.sheet_record_repository import SheetRecordRepository
from salary_tracker.data.repositories.sheet.sheet_repository import SheetRepository
from salary_tracker.data.repositories.user.user_repository import UserRepository
from salary_tracker.domain.auth.repositories import IRefreshTokenRepository, IUserExternalAccountRepository
from salary_tracker.domain.sheet.repositories import ISheetRepository, IRateTableRepository, ISheetRecordRepository
from salary_tracker.domain.user.repositories import IUserRepository
from salary_tracker.presentation.dependencies.presentation import get_settings
from salary_tracker.presentation.settings import AppSettings


@lru_cache
def get_database(
        settings: AppSettings = Depends(get_settings)
) -> Database:
    return Database(settings.database_url.unicode_string())


async def get_session(
        database: Database = Depends(get_database)
) -> AsyncSession:
    async with database.session() as session:
        yield session


async def get_refresh_token_repository(
        session: AsyncSession = Depends(get_session),
) -> IRefreshTokenRepository:
    return RefreshTokenRepository(session=session)


async def get_user_external_account_repository(
        session: AsyncSession = Depends(get_session),
) -> IUserExternalAccountRepository:
    return UserExternalAccountRepository(session=session)


async def get_user_repository(
        session: AsyncSession = Depends(get_session),
) -> IUserRepository:
    return UserRepository(session=session)


async def get_sheet_repository(
        session: AsyncSession = Depends(get_session),
) -> ISheetRepository:
    return SheetRepository(session=session)


async def get_rate_table_repository(
        session: AsyncSession = Depends(get_session),
) -> IRateTableRepository:
    return RateTableRepository(session=session)


async def get_sheet_record_repository(
        session: AsyncSession = Depends(get_session),
) -> ISheetRecordRepository:
    return SheetRecordRepository(session=session)