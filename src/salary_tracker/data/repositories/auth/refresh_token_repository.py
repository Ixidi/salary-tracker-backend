from pydantic import ConfigDict, BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from salary_tracker.domain.auth.models import RefreshToken
from salary_tracker.domain.auth.repositories import IRefreshTokenRepository
from salary_tracker.data.model import DatabaseUserRefreshToken


class RefreshTokenRepository(IRefreshTokenRepository, BaseModel):
    session: AsyncSession

    model_config = ConfigDict(arbitrary_types_allowed=True)

    async def get_by_token(self, refresh_token: str) -> RefreshToken | None:
        result = await self.session.execute(
            select(DatabaseUserRefreshToken).filter_by(token=refresh_token)
        )

        user_refresh_token = result.scalar_one_or_none()
        if user_refresh_token is None:
            return None

        return RefreshToken.model_validate(user_refresh_token, from_attributes=True)

    async def insert(self, refresh_token: RefreshToken) -> RefreshToken:
        result = await self.session.execute(
            select(DatabaseUserRefreshToken).filter_by(user_uuid=refresh_token.user_uuid)
        )

        user_refresh_token = DatabaseUserRefreshToken(
            user_uuid=refresh_token.user_uuid,
            token=refresh_token.token,
            expires_at=refresh_token.expires_at
        )

        self.session.add(user_refresh_token)
        await self.session.commit()

        return RefreshToken.model_validate(user_refresh_token, from_attributes=True)

    async def delete(self, refresh_token: str) -> None:
        await self.session.execute(
            delete(DatabaseUserRefreshToken).filter_by(token=refresh_token)
        )
