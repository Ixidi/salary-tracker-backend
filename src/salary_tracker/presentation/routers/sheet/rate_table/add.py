from uuid import UUID

from fastapi import APIRouter, Depends

from salary_tracker.domain.sheet.models import RateTableData, RateTable
from salary_tracker.presentation.dependencies.auth import get_current_user_uuid
from salary_tracker.presentation.dependencies.usecases import get_add_sheet_rate_table_use_case
from salary_tracker.usecase.sheet.rate_table.add_rate_table import AddSheetRateTableUseCase

router = APIRouter()


class RateTableDataRequest(RateTableData):
    pass


@router.post(
    "/{sheet_uuid}/rate_tables/",
    description="Add a rate table to a sheet",
    response_model=list[RateTable],
)
async def add_rate_table_to_sheet(
        sheet_uuid: UUID,
        rate_table_data: RateTableDataRequest,
        requesting_user_uuid: UUID = Depends(get_current_user_uuid),
        add_sheet_rate_table_use_case: AddSheetRateTableUseCase = Depends(get_add_sheet_rate_table_use_case),
):
    return await add_sheet_rate_table_use_case(sheet_uuid, requesting_user_uuid,
                                        RateTableData.model_validate(rate_table_data, from_attributes=True))
