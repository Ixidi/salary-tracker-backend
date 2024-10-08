from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, PositiveInt

from salary_tracker.domain.sheet.models import NewSheetData, Rate
from salary_tracker.presentation.dependencies.auth import get_current_user_uuid
from salary_tracker.presentation.dependencies.usecases import get_create_sheet_use_case
from salary_tracker.presentation.responses.sheet import SheetResponse
from salary_tracker.usecase.sheet.create_sheet import CreateSheetUseCase

router = APIRouter()


class NewSheetRequest(BaseModel):
    title: str
    description: str
    durations: set[timedelta]
    group_sizes: set[PositiveInt]
    rates: list[Rate]


@router.post(
    "/",
    description="Create a new sheet",
    response_model=SheetResponse
)
async def create_new_sheet(
        new_sheet_data: NewSheetRequest,
        current_user_uuid: UUID = Depends(get_current_user_uuid),
        use_case: CreateSheetUseCase = Depends(get_create_sheet_use_case)
):
    data = new_sheet_data.model_dump()
    data.update(
        owner_user_uuid=current_user_uuid
    )

    return await use_case(NewSheetData.model_validate(data))
