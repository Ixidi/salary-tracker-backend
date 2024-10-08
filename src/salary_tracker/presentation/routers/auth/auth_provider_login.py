from fastapi import APIRouter, Depends
from pydantic import BaseModel

from salary_tracker.domain.auth.models import AuthProvider
from salary_tracker.presentation.dependencies.auth import RefreshTokenStore
from salary_tracker.presentation.dependencies.usecases import get_auth_provider_login_use_case
from salary_tracker.presentation.responses.auth import AuthResponse
from salary_tracker.usecase.auth.auth_provider_login import LoginWithAuthProviderUseCase

router = APIRouter()


class AuthProviderLoginRequest(BaseModel):
    external_token: str


@router.post(
    '/auth-provider-login/{auth_provider}/',
    description='Login with an external auth provider',
    response_model=AuthResponse
)
async def auth_provider_login(
        auth_provider: AuthProvider,
        request_data: AuthProviderLoginRequest,
        refresh_cookie_store: RefreshTokenStore,
        use_case: LoginWithAuthProviderUseCase = Depends(get_auth_provider_login_use_case)
):
    token_pair = await use_case(
        external_token=request_data.external_token,
        auth_provider=auth_provider
    )

    refresh_cookie_store.set(token_pair.refresh_token)

    return token_pair
