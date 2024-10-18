from pydantic import ConfigDict, BaseModel, validate_call
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from salary_tracker.domain.auth.models import RefreshToken
from salary_tracker.domain.auth.repositories import IRefreshTokenRepository
from salary_tracker.data.model import DatabaseUserRefreshToken


class RefreshTokenRepository(IRefreshTokenRepository):
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_token(self, refresh_token: str) -> RefreshToken | None:
        result = await self._session.execute(
            select(DatabaseUserRefreshToken).filter_by(token=refresh_token)
        )

        user_refresh_token = result.scalar_one_or_none()
        if user_refresh_token is None:
            return None

        return RefreshToken.model_validate(user_refresh_token, from_attributes=True)

    async def insert(self, refresh_token: RefreshToken) -> RefreshToken:
        result = await self._session.execute(
            select(DatabaseUserRefreshToken).filter_by(user_uuid=refresh_token.user_uuid)
        )

        user_refresh_token = DatabaseUserRefreshToken(
            user_uuid=refresh_token.user_uuid,
            token=refresh_token.token,
            expires_at=refresh_token.expires_at
        )

        self._session.add(user_refresh_token)
        await self._session.commit()

        return RefreshToken.model_validate(user_refresh_token, from_attributes=True)

    async def delete(self, refresh_token: str) -> None:
        await self._session.execute(
            delete(DatabaseUserRefreshToken).filter_by(token=refresh_token)
        )
