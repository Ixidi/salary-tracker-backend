from uuid import UUID

from fastapi import APIRouter, Depends

from salary_tracker.domain.sheet.models import NewRecordData
from salary_tracker.presentation.dependencies.auth import get_current_user_uuid
from salary_tracker.presentation.dependencies.usecases import get_add_sheet_record_use_case
from salary_tracker.presentation.responses.sheet import RecordResponse
from salary_tracker.usecase.sheet.record.add_record import AddSheetRecordUseCase

router = APIRouter()


class NewRecordRequest(NewRecordData):
    pass


@router.post(
    "/{sheet_uuid}/records/",
    description="Add a new record to the sheet",
    response_model=RecordResponse
)
async def add_sheet_record(
        sheet_uuid: UUID,
        new_record_data: NewRecordRequest,
        current_user_uuid: UUID = Depends(get_current_user_uuid),
        use_case: AddSheetRecordUseCase = Depends(get_add_sheet_record_use_case)
):
    return await use_case(sheet_uuid, current_user_uuid, new_record_data)
