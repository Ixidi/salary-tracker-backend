from uuid import UUID

from fastapi import APIRouter, Depends

from salary_tracker.presentation.dependencies.auth import get_current_user_uuid
from salary_tracker.presentation.dependencies.usecases import get_get_sheet_for_user_use_case
from salary_tracker.presentation.responses.sheet import SheetResponse
from salary_tracker.usecase.sheet.get_sheet_for_user import GetSheetForUserUseCase

router = APIRouter()


@router.get(
    "/{sheet_uuid}/",
    description="Get a sheet by UUID",
    response_model=SheetResponse
)
async def get_sheet(
        sheet_uuid: UUID,
        current_user_uuid: UUID = Depends(get_current_user_uuid),
        get_sheet_use_case: GetSheetForUserUseCase = Depends(get_get_sheet_for_user_use_case)
):
    return await get_sheet_use_case(sheet_uuid, current_user_uuid)
