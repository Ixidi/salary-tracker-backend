from fastapi import Depends

from salary_tracker.domain.auth.services import ITokenService, IAuthProviderService
from salary_tracker.domain.sheet.services import ISheetService
from salary_tracker.domain.user.services import IUserService
from salary_tracker.presentation.dependencies.services import get_user_service, get_token_service, \
    get_auth_provider_service, get_sheet_service
from salary_tracker.usecase.auth.auth_provider_login import LoginWithAuthProviderUseCase
from salary_tracker.usecase.auth.rotate_refresh_token import RotateRefreshTokenUseCase
from salary_tracker.usecase.auth.validate_access_token import ValidateAccessTokenUseCase
from salary_tracker.usecase.sheet.create_sheet import CreateSheetUseCase
from salary_tracker.usecase.user.get_user import GetUserUseCase


async def get_auth_provider_login_use_case(
        user_service: IUserService = Depends(get_user_service),
        token_service: ITokenService = Depends(get_token_service),
        auth_provider_service: IAuthProviderService = Depends(get_auth_provider_service)
) -> LoginWithAuthProviderUseCase:
    return LoginWithAuthProviderUseCase(
        user_service=user_service,
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