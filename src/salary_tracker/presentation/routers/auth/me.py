from uuid import UUID

from fastapi import APIRouter, Depends

from salary_tracker.presentation.dependencies.auth import get_current_user_uuid
from salary_tracker.presentation.dependencies.usecases import get_user_use_case
from salary_tracker.presentation.responses.user import UserResponse
from salary_tracker.usecase.user.get_user import GetUserUseCase

router = APIRouter()

@router.get(
    "/me/",
    description="Get the current user",
    response_model=UserResponse
)
async def get_me(
        current_user_uuid: UUID = Depends(get_current_user_uuid),
        get_user: GetUserUseCase = Depends(get_user_use_case),
):
    return await get_user(current_user_uuid)