from uuid import UUID

from pydantic import validate_call, ConfigDict

from salary_tracker.domain.pagination import PaginatedRequest, PaginatedResult
from salary_tracker.domain.sheet.models import Sheet
from salary_tracker.domain.sheet.services import ISheetService


class GetPaginatedUserSheetsUseCase:
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, sheet_service: ISheetService):
        self._sheet_service = sheet_service

    async def __call__(self, request: PaginatedRequest[UUID]) -> PaginatedResult[Sheet]:
        return await self._sheet_service.get_by_owner_paginated(request)
