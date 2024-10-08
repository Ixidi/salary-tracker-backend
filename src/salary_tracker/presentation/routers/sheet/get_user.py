from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from salary_tracker.domain.pagination import PaginatedRequest, PageParams
from salary_tracker.presentation.dependencies.auth import get_current_user_uuid
from salary_tracker.presentation.dependencies.usecases import get_get_paginated_user_sheets_use_case
from salary_tracker.presentation.responses.pagination import PaginatedResultResponse
from salary_tracker.presentation.responses.sheet import SheetResponse
from salary_tracker.usecase.sheet.get_user_sheets import GetPaginatedUserSheetsUseCase

router = APIRouter()


@router.get(
    "/",
    description="Get all user sheets",
    response_model=PaginatedResultResponse[SheetResponse],
)
async def get_user_sheets(
        query_params: Annotated[PageParams, Query()],
        current_user_uuid: UUID = Depends(get_current_user_uuid),
        use_case: GetPaginatedUserSheetsUseCase = Depends(get_get_paginated_user_sheets_use_case),
):
    return await use_case(PaginatedRequest[UUID](
        page_params=query_params,
        filters=current_user_uuid
    ))
