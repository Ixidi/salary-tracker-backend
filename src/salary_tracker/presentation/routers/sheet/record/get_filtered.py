from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.params import Query

from salary_tracker.domain.pagination import PageParams, PaginatedRequest
from salary_tracker.domain.sheet.models import SheetRecordFilters
from salary_tracker.presentation.dependencies.auth import get_current_user_uuid
from salary_tracker.presentation.dependencies.usecases import get_get_paginated_sheet_records_use_case
from salary_tracker.presentation.responses.pagination import PaginatedResultResponse
from salary_tracker.presentation.responses.sheet import RecordResponse
from salary_tracker.usecase.sheet.record.get_paginated_sheet_records import GetPaginatedSheetRecordsUseCase

router = APIRouter()

class QueryParams(PageParams):
    datetime_from: datetime | None = None
    datetime_to: datetime | None = None

@router.get(
    "/{sheet_uuid}/records/",
    description="Get filtered records of the sheet",
    response_model=PaginatedResultResponse[RecordResponse]
)
async def get_filtered_sheet_records(
        sheet_uuid: UUID,
        query_params: Annotated[QueryParams, Query()],
        current_user_uuid: UUID = Depends(get_current_user_uuid),
        use_case: GetPaginatedSheetRecordsUseCase = Depends(get_get_paginated_sheet_records_use_case)
):
    result = await use_case(PaginatedRequest(
        page_params=query_params,
        filters=SheetRecordFilters(
            sheet_uuid=sheet_uuid,
            datetime_from=query_params.datetime_from,
            datetime_to=query_params.datetime_to
        )
    ), current_user_uuid)

    return result
