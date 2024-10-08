from uuid import UUID, uuid4

from pydantic import validate_call, ConfigDict, ValidationError

from salary_tracker.domain.exceptions import SheetNotFoundDomainException, UserNotFoundDomainException, \
    ModelValidationDomainException
from salary_tracker.domain.pagination import PaginatedRequest, PaginatedResult
from salary_tracker.domain.sheet.factories import IRateTableFactory
from salary_tracker.domain.sheet.models import NewSheetData, Sheet, RateTableData
from salary_tracker.domain.sheet.repositories import ISheetRepository, IRateTableRepository
from salary_tracker.domain.sheet.services import ISheetService
from salary_tracker.domain.user.repositories import IUserRepository


class SheetService(ISheetService):
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, user_repository: IUserRepository, sheet_repository: ISheetRepository,
                 rate_table_factory: IRateTableFactory, rate_table_repository: IRateTableRepository):
        self._user_repository = user_repository
        self._sheet_repository = sheet_repository
        self._rate_table_factory = rate_table_factory
        self._rate_table_repository = rate_table_repository

    async def get_by_uuid(self, sheet_uuid: UUID) -> Sheet:
        result = await self._sheet_repository.get_by_uuid(sheet_uuid)
        if result is None:
            raise SheetNotFoundDomainException(sheet_uuid)

        return result

    async def get_by_owner_paginated(self, request: PaginatedRequest[UUID]) -> PaginatedResult[Sheet]:
        return await self._sheet_repository.get_by_owner_paginated(request)

    async def create(self, new_sheet_data: NewSheetData) -> Sheet:
        owner = await self._user_repository.get_by_uuid(new_sheet_data.owner_user_uuid)
        if owner is None:
            raise UserNotFoundDomainException(new_sheet_data.owner_user_uuid)

        try:
            sheet = Sheet(
                uuid=uuid4(),
                owner_user_uuid=new_sheet_data.owner_user_uuid,
                title=new_sheet_data.title,
                description=new_sheet_data.description,
                durations=new_sheet_data.durations,
                group_sizes=new_sheet_data.group_sizes
            )

            rate_table = self._rate_table_factory.create(
                rate_table_data=RateTableData(
                    valid_from=None,
                    valid_to=None,
                    rates=new_sheet_data.rates
                ),
                durations=new_sheet_data.durations,
                group_sizes=new_sheet_data.group_sizes
            )
        except ValidationError as e:
            raise ModelValidationDomainException(e)

        sheet = await self._sheet_repository.upsert(sheet)
        await self._rate_table_repository.upsert(sheet.uuid, [rate_table])

        return sheet

    async def delete(self, sheet_uuid: UUID) -> None:
        sheet = await self._sheet_repository.get_by_uuid(sheet_uuid)
        if sheet is None:
            raise SheetNotFoundDomainException(sheet_uuid)

        await self._sheet_repository.delete(sheet_uuid)
