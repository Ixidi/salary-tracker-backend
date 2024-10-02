from pydantic import BaseModel, ConfigDict

from salary_tracker.domain.auth.services import ITokenService
from salary_tracker.domain.auth.models import TokenPair
from salary_tracker.usecase.exceptions import InvalidTokenException


class RotateRefreshTokenUseCase(BaseModel):
    token_service: ITokenService

    model_config = ConfigDict(arbitrary_types_allowed=True)

    async def __call__(self, refresh_token: str, user_agent: str) -> TokenPair:
        refresh_token = await self.token_service.validate_refresh_token(refresh_token)
        if not refresh_token:
            raise InvalidTokenException()

        await self.token_service.delete_refresh_token(refresh_token.token)

        user_uuid = refresh_token.user_uuid
        token_pair = await self.token_service.create_token_pair(user_uuid, user_agent)
        await self.token_service.save_refresh_token(token_pair.refresh_token)

        return token_pair
