from pydantic import BaseModel, ConfigDict

from salary_tracker.domain.auth.services import ITokenService
from salary_tracker.domain.auth.models import AccessToken
from salary_tracker.usecase.exceptions import InvalidTokenException


class ValidateAccessTokenUseCase(BaseModel):
    token_service: ITokenService

    model_config = ConfigDict(arbitrary_types_allowed=True)

    async def __call__(self, access_token: str) -> AccessToken:
        access_token = await self.token_service.validate_access_token(access_token)
        if not access_token:
            raise InvalidTokenException()

        return access_token
