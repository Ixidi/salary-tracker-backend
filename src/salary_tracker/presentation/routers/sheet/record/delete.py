from uuid import UUID

from fastapi import APIRouter, Depends

from salary_tracker.presentation.dependencies.auth import get_current_user_uuid
from salary_tracker.presentation.dependencies.usecases import get_delete_record_use_case
from salary_tracker.usecase.sheet.record.delete_record import DeleteRecordUseCase

router = APIRouter()


@router.delete(
    "/{sheet_uuid}/records/{record_uuid}/",
    description="Delete record by uuid"
)
async def delete_record(
        sheet_uuid: UUID,
        record_uuid: UUID,
        current_user_uuid: UUID = Depends(get_current_user_uuid),
        use_case: DeleteRecordUseCase = Depends(get_delete_record_use_case)
):
    await use_case(sheet_uuid, record_uuid, current_user_uuid)
