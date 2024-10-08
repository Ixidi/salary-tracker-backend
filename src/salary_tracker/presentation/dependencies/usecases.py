from fastapi import Depends

from salary_tracker.domain.auth.services import ITokenService, IAuthProviderService
from salary_tracker.domain.sheet.services import ISheetService, IRateTableService, ISheetRecordService, ISalaryService
from salary_tracker.domain.user.services import IUserService
from salary_tracker.presentation.dependencies.services import get_user_service, get_token_service, \
    get_auth_provider_service, get_sheet_service, get_rate_table_service, get_sheet_record_service, get_salary_service
from salary_tracker.usecase.auth.auth_provider_login import LoginWithAuthProviderUseCase
from salary_tracker.usecase.auth.rotate_refresh_token import RotateRefreshTokenUseCase
from salary_tracker.usecase.auth.validate_access_token import ValidateAccessTokenUseCase
from salary_tracker.usecase.sheet.create_sheet import CreateSheetUseCase
from salary_tracker.usecase.sheet.delete_sheet import DeleteSheetUseCase
from salary_tracker.usecase.sheet.get_sheet_for_user import GetSheetForUserUseCase
from salary_tracker.usecase.sheet.get_user_sheets import GetPaginatedUserSheetsUseCase
from salary_tracker.usecase.sheet.rate_table.add_rate_table import AddSheetRateTableUseCase
from salary_tracker.usecase.sheet.rate_table.get_rate_table_for_datetime import GetRateTableForDatetime
from salary_tracker.usecase.sheet.record.add_record import AddSheetRecordUseCase
from salary_tracker.usecase.sheet.record.delete_record import DeleteRecordUseCase
from salary_tracker.usecase.sheet.record.get_paginated_sheet_records import GetPaginatedSheetRecordsUseCase
from salary_tracker.usecase.sheet.salary.calculate_salary import CalculateSalaryUseCase
from salary_tracker.usecase.user.get_user import GetUserUseCase


async def get_auth_provider_login_use_case(
        token_service: ITokenService = Depends(get_token_service),
        auth_provider_service: IAuthProviderService = Depends(get_auth_provider_service),
) -> LoginWithAuthProviderUseCase:
    return LoginWithAuthProviderUseCase(
        token_service=token_service,
        auth_provider_service=auth_provider_service
    )


async def get_rotate_refresh_token_use_case(
        token_service: ITokenService = Depends(get_token_service)
) -> RotateRefreshTokenUseCase:
    return RotateRefreshTokenUseCase(
        token_service=token_service
    )


async def get_validate_access_token_use_case(
        token_service: ITokenService = Depends(get_token_service)
) -> ValidateAccessTokenUseCase:
    return ValidateAccessTokenUseCase(
        token_service=token_service
    )


async def get_user_use_case(
        user_service: IUserService = Depends(get_user_service)
) -> GetUserUseCase:
    return GetUserUseCase(
        user_service=user_service
    )


async def get_create_sheet_use_case(
        sheet_service: ISheetService = Depends(get_sheet_service)
) -> CreateSheetUseCase:
    return CreateSheetUseCase(sheet_service=sheet_service)


async def get_get_sheet_for_user_use_case(
        sheet_service: ISheetService = Depends(get_sheet_service)
) -> GetSheetForUserUseCase:
    return GetSheetForUserUseCase(sheet_service=sheet_service)


async def get_add_sheet_rate_table_use_case(
        sheet_service: ISheetService = Depends(get_sheet_service),
        rate_table_service: IRateTableService = Depends(get_rate_table_service)
) -> AddSheetRateTableUseCase:
    return AddSheetRateTableUseCase(sheet_service=sheet_service, rate_table_service=rate_table_service)


async def get_get_rate_table_for_datetime_use_case(
        sheet_service: ISheetService = Depends(get_sheet_service),
        rate_table_service: IRateTableService = Depends(get_rate_table_service)
) -> GetRateTableForDatetime:
    return GetRateTableForDatetime(sheet_service=sheet_service, rate_table_service=rate_table_service)


async def get_add_sheet_record_use_case(
        sheet_service: ISheetService = Depends(get_sheet_service),
        sheet_record_service: ISheetRecordService = Depends(get_sheet_record_service)
) -> AddSheetRecordUseCase:
    return AddSheetRecordUseCase(sheet_service=sheet_service, sheet_record_service=sheet_record_service)


async def get_get_paginated_sheet_records_use_case(
        sheet_service: ISheetService = Depends(get_sheet_service),
        sheet_record_service: ISheetRecordService = Depends(get_sheet_record_service)
) -> GetPaginatedSheetRecordsUseCase:
    return GetPaginatedSheetRecordsUseCase(sheet_service=sheet_service, sheet_record_service=sheet_record_service)


async def get_calculate_salary_use_case(
        sheet_service: ISheetService = Depends(get_sheet_service),
        salary_service: ISalaryService = Depends(get_salary_service)
) -> CalculateSalaryUseCase:
    return CalculateSalaryUseCase(sheet_service=sheet_service, salary_service=salary_service)


async def get_delete_sheet_use_case(
        sheet_service: ISheetService = Depends(get_sheet_service)
) -> DeleteSheetUseCase:
    return DeleteSheetUseCase(sheet_service=sheet_service)


async def get_delete_record_use_case(
        sheet_record_service: ISheetRecordService = Depends(get_sheet_record_service),
        sheet_service: ISheetService = Depends(get_sheet_service)
) -> DeleteRecordUseCase:
    return DeleteRecordUseCase(sheet_service=sheet_service, sheet_record_service=sheet_record_service)


async def get_get_paginated_user_sheets_use_case(
        sheet_service: ISheetService = Depends(get_sheet_service)
) -> GetPaginatedUserSheetsUseCase:
    return GetPaginatedUserSheetsUseCase(sheet_service=sheet_service)
