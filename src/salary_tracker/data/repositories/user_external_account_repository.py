from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from salary_tracker.domain.auth.models import UserExternalAccount, AuthProvider
from salary_tracker.domain.auth.repositories import IUserExternalAccountRepository
from salary_tracker.data.model import DatabaseUserExternalAccount


class UserExternalAccountRepository(IUserExternalAccountRepository, BaseModel):
    session: AsyncSession

    model_config = ConfigDict(arbitrary_types_allowed=True)

    async def get_by_external_id(self, external_id: str, auth_provider: AuthProvider) -> UserExternalAccount | None:
        result = await self.session.execute(
            select(DatabaseUserExternalAccount).filter_by(
                external_id=external_id,
                provider=auth_provider
            )
        )

        result = result.scalar_one_or_none()
        if result is None:
            return None

        return UserExternalAccount.model_validate(result, from_attributes=True)

    async def create(self, user: UserExternalAccount) -> UserExternalAccount:
        result = DatabaseUserExternalAccount.model_validate(user)
        self.session.add(result)
        await self.session.commit()

        return UserExternalAccount.model_validate(result, from_attributes=True)

