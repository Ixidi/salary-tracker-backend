from uuid import UUID

from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from salary_tracker.domain.user.models import User
from salary_tracker.domain.user.repositories import IUserRepository
from salary_tracker.data.model import DatabaseUser


class UserRepository(IUserRepository, BaseModel):
    session: AsyncSession

    model_config = ConfigDict(arbitrary_types_allowed=True)

    async def get_by_uuid(self, uuid: UUID) -> User | None:
        result = await self.session.execute(
            select(DatabaseUser).filter_by(uuid=uuid)
        )

        user = result.scalar_one_or_none()
        if user is None:
            return None

        return User.model_validate(user, from_attributes=True)

    async def upsert(self, user: User) -> User:
        result = await self.session.execute(
            select(DatabaseUser).filter_by(uuid=user.uuid)
        )

        db_user = result.scalar_one_or_none()
        if db_user is None:
            db_user = DatabaseUser(
                uuid=user.uuid,
                email=user.email,
                name=user.name
            )
            self.session.add(db_user)
        else:
            db_user.email = user.email
            db_user.name = user.name

        await self.session.commit()

        return User.model_validate(db_user, from_attributes=True)
