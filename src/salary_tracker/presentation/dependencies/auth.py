from datetime import datetime, UTC
from uuid import UUID

from fastapi import Request, Response, HTTPException
from fastapi.params import Depends

from salary_tracker.domain.auth.models import RefreshToken, AccessToken
from salary_tracker.presentation.dependencies.presentation import get_settings
from salary_tracker.presentation.dependencies.usecases import get_rotate_refresh_token_use_case, \
    get_validate_access_token_use_case
from salary_tracker.usecase.auth.rotate_refresh_token import RotateRefreshTokenUseCase
from salary_tracker.usecase.auth.validate_access_token import ValidateAccessTokenUseCase
from salary_tracker.usecase.exceptions import InvalidTokenException

_REFRESH_TOKEN_COOKIE_NAME = "refresh_token"
_ACCESS_TOKEN_COOKIE_NAME = "access_token"


def _get_refresh_token_cookie(request: Request) -> str | None:
    return request.cookies.get(_REFRESH_TOKEN_COOKIE_NAME)


def _get_access_token_cookie(request: Request) -> str | None:
    return request.cookies.get(_ACCESS_TOKEN_COOKIE_NAME)


def _set_auth_cookies(response: Response, key: str, value: str, expires_at: datetime):
    now = datetime.now(tz=UTC)
    settings = get_settings()
    secure_cookies = settings.auth_cookies_secure
    path = settings.auth_cookies_path
    domain = settings.auth_cookies_domain
    same_site = settings.auth_cookies_same_site
    response.set_cookie(
        key=key,
        value=value,
        max_age=int((expires_at - now).total_seconds()),
        httponly=True,
        path=path,
        secure=secure_cookies,
        samesite=same_site,
        domain=domain if domain else None
    )


def set_refresh_token_cookie(response: Response, refresh_token: RefreshToken):
    _set_auth_cookies(response, _REFRESH_TOKEN_COOKIE_NAME, refresh_token.token, refresh_token.expires_at)


def set_access_token_cookie(response: Response, access_token: AccessToken):
    _set_auth_cookies(response, _ACCESS_TOKEN_COOKIE_NAME, access_token.token, access_token.expires_at)


def _delete_auth_cookie(response: Response, key: str):
    path = get_settings().auth_cookies_path
    domain = get_settings().auth_cookies_domain
    response.delete_cookie(
        key=key,
        path=path,
        domain=domain if domain else None
    )


def _delete_access_token_cookie(response: Response):
    _delete_auth_cookie(response, _ACCESS_TOKEN_COOKIE_NAME)


def _delete_refresh_token_cookie(response: Response):
    _delete_auth_cookie(response, _REFRESH_TOKEN_COOKIE_NAME)


async def get_current_user_uuid(
        request: Request,
        response: Response,
        rotate_refresh_token_use_case: RotateRefreshTokenUseCase = Depends(get_rotate_refresh_token_use_case),
        validate_access_token_use_case: ValidateAccessTokenUseCase = Depends(get_validate_access_token_use_case)
) -> UUID:
    user_agent = request.headers.get("User-Agent")
    if not user_agent:
        raise HTTPException(status_code=401, detail="Unauthorized")

    access_token = _get_access_token_cookie(request)
    if access_token:
        validated_token = await validate_access_token_use_case(access_token)
        if validated_token:
            return validated_token.user_uuid

    refresh_token = _get_refresh_token_cookie(request)
    try:
        if refresh_token:
            refreshed_pair = await rotate_refresh_token_use_case(refresh_token, user_agent)
            set_refresh_token_cookie(response, refreshed_pair.refresh_token)
            set_access_token_cookie(response, refreshed_pair.access_token)
            return refreshed_pair.access_token.user_uuid
    except InvalidTokenException:
        pass

    _delete_access_token_cookie(response)
    _delete_refresh_token_cookie(response)

    raise HTTPException(status_code=401, detail="Unauthorized")
