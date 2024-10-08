from fastapi import APIRouter, Depends

from salary_tracker.presentation.dependencies.auth import RefreshTokenStore
from salary_tracker.presentation.dependencies.usecases import get_rotate_refresh_token_use_case
from salary_tracker.presentation.responses.auth import AuthResponse
from salary_tracker.usecase.auth.rotate_refresh_token import RotateRefreshTokenUseCase
from salary_tracker.usecase.exceptions import AuthException

router = APIRouter()


@router.post(
    "/refresh-token/",
    description="Refresh access_token using refresh_token",
    response_model=AuthResponse
)
async def refresh_token(
        refresh_token_store: RefreshTokenStore,
        use_case: RotateRefreshTokenUseCase = Depends(get_rotate_refresh_token_use_case)
):
    token = refresh_token_store.get()
    if not token:
        raise AuthException("Refresh token is missing")

    try:
        token_pair = await use_case(token)
        refresh_token_store.set(token_pair.refresh_token)

        return token_pair
    except AuthException as e:
        refresh_token_store.delete()
        raise
