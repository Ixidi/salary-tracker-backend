from datetime import datetime, UTC
from typing import Annotated
from uuid import UUID

from fastapi import Request, Response
from fastapi.params import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from salary_tracker.domain.auth.models import RefreshToken
from salary_tracker.presentation.dependencies.presentation import get_settings
from salary_tracker.presentation.dependencies.usecases import get_validate_access_token_use_case
from salary_tracker.presentation.settings import AppSettings
from salary_tracker.usecase.auth.validate_access_token import ValidateAccessTokenUseCase
from salary_tracker.usecase.exceptions import AuthException

_REFRESH_TOKEN_COOKIE_NAME = "refresh_token"


class _RefreshTokenCookieStore:
    def __init__(self,
                 request: Request,
                 response: Response,
                 settings: AppSettings = Depends(get_settings)
                 ):
        self._request = request
        self._response = response
        self._settings = settings

    def get(self) -> str | None:
        return self._request.cookies.get(_REFRESH_TOKEN_COOKIE_NAME)

    def set(self, refresh_token: RefreshToken):
        now = datetime.now(tz=UTC)
        secure_cookies = self._settings.refresh_token_cookie_secure
        path = self._settings.refresh_token_cookie_path
        domain = self._settings.refresh_token_cookie_domain
        same_site = self._settings.refresh_token_cookie_same_site
        http_only = self._settings.refresh_token_cookie_http_only
        self._response.set_cookie(
            key=_REFRESH_TOKEN_COOKIE_NAME,
            value=refresh_token.token,
            max_age=int((refresh_token.expires_at - now).total_seconds()),
            httponly=http_only,
            path=path,
            secure=secure_cookies,
            samesite=same_site,
            domain=domain
        )

    def delete(self):
        secure_cookies = self._settings.refresh_token_cookie_secure
        path = self._settings.refresh_token_cookie_path
        domain = self._settings.refresh_token_cookie_domain
        same_site = self._settings.refresh_token_cookie_same_site
        http_only = self._settings.refresh_token_cookie_http_only
        self._response.delete_cookie(
            key=_REFRESH_TOKEN_COOKIE_NAME,
            httponly=http_only,
            path=path,
            secure=secure_cookies,
            samesite=same_site,
            domain=domain
        )

RefreshTokenStore = Annotated[_RefreshTokenCookieStore, Depends(_RefreshTokenCookieStore)]

security = HTTPBearer(
    auto_error=False
)


async def get_current_user_uuid(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        validate_access_token_use_case: ValidateAccessTokenUseCase = Depends(get_validate_access_token_use_case)
) -> UUID:
    if credentials:
        validated_token = await validate_access_token_use_case(credentials.credentials)
        if validated_token:
            return validated_token.user_uuid

    raise AuthException("Missing access token")
