from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import AwareDatetime

from salary_tracker.domain.sheet.models import RateTable
from salary_tracker.presentation.dependencies.auth import get_current_user_uuid
from salary_tracker.presentation.dependencies.usecases import get_get_rate_table_for_datetime_use_case
from salary_tracker.usecase.sheet.rate_table.get_rate_table_for_datetime import GetRateTableForDatetime

router = APIRouter()


@router.get(
    "/{sheet_uuid}/rate_tables/{datetime_point}/",
    response_model=RateTable,
)
async def get_rate_table_for_datetime(
        sheet_uuid: UUID,
        datetime_point: AwareDatetime,
        current_user_uuid: UUID = Depends(get_current_user_uuid),
        get_rate_table_for_datetime_usecase: GetRateTableForDatetime = Depends(
            get_get_rate_table_for_datetime_use_case),
):
    return await get_rate_table_for_datetime_usecase(sheet_uuid, current_user_uuid, datetime_point)
