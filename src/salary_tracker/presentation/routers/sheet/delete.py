from uuid import UUID

from fastapi import APIRouter, Depends

from salary_tracker.presentation.dependencies.auth import get_current_user_uuid
from salary_tracker.presentation.dependencies.usecases import get_delete_sheet_use_case
from salary_tracker.usecase.sheet.delete_sheet import DeleteSheetUseCase

router = APIRouter()


@router.delete(
    "/{sheet_uuid}/",
    description="Delete sheet by uuid"
)
async def delete_sheet(
        sheet_uuid: UUID,
        sheet_title: str,
        current_user_uuid: UUID = Depends(get_current_user_uuid),
        use_case: DeleteSheetUseCase = Depends(get_delete_sheet_use_case)
):
    await use_case(sheet_uuid, sheet_title, current_user_uuid)
