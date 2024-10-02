from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel

from salary_tracker.domain.auth.models import AuthProvider
from salary_tracker.presentation.dependencies.auth import set_refresh_token_cookie, set_access_token_cookie
from salary_tracker.presentation.dependencies.usecases import get_auth_provider_login_use_case
from salary_tracker.usecase.auth.auth_provider_login import LoginWithAuthProviderUseCase

router = APIRouter()

class AuthProviderLoginRequest(BaseModel):
    external_token: str

@router.post(
    '/auth-provider-login/{auth_provider}',
    description='Login with an external auth provider'
)
async def auth_provider_login(
    auth_provider: AuthProvider,
    request_data: AuthProviderLoginRequest,
    request: Request,
    response: Response,
    auth_provider_login_use_case: LoginWithAuthProviderUseCase = Depends(get_auth_provider_login_use_case)
):
    token_pair = await auth_provider_login_use_case(
        external_token=request_data.external_token,
        auth_provider=auth_provider,
        user_agent=request.headers.get('User-Agent', 'Unknown')
    )

    set_refresh_token_cookie(response, token_pair.refresh_token)
    set_access_token_cookie(response, token_pair.access_token)