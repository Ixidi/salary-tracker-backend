from pydantic import BaseModel, ConfigDict, validate_call
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from salary_tracker.domain.auth.models import UserExternalAccount, AuthProvider
from salary_tracker.domain.auth.repositories import IUserExternalAccountRepository
from salary_tracker.data.model import DatabaseUserExternalAccount


class UserExternalAccountRepository(IUserExternalAccountRepository):
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_external_id(self, external_id: str, auth_provider: AuthProvider) -> UserExternalAccount | None:
        result = await self._session.execute(
            select(DatabaseUserExternalAccount).filter_by(
                external_id=external_id,
                provider=auth_provider
            )
        )

        result = result.scalar_one_or_none()
        if result is None:
            return None

        return UserExternalAccount.model_validate(result, from_attributes=True)

    async def insert(self, user: UserExternalAccount) -> UserExternalAccount:
        result = DatabaseUserExternalAccount(
            provider=user.provider,
            user_uuid=user.user_uuid,
            external_id=user.external_id
        )
        self._session.add(result)
        await self._session.commit()

        return UserExternalAccount.model_validate(result, from_attributes=True)

