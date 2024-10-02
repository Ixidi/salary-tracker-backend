from fastapi import Depends

from salary_tracker.domain.auth.impl.provider.auth_provider_service import AuthProviderService
from salary_tracker.domain.auth.impl.provider.auth_provider_user_data_extractor_factory import \
    AuthProviderUserDataExtractorFactory
from salary_tracker.domain.auth.impl.token.token_service import TokenService
from salary_tracker.domain.auth.repositories import IRefreshTokenRepository, IUserExternalAccountRepository
from salary_tracker.domain.auth.services import ITokenService, IAuthProviderService, \
    IAuthProviderUserDataExtractorFactory
from salary_tracker.domain.sheet.impl.sheet_service import SheetService
from salary_tracker.domain.sheet.repositories import ISheetRepository
from salary_tracker.domain.sheet.services import ISheetService
from salary_tracker.domain.user.impl.user_service import UserService
from salary_tracker.domain.user.repositories import IUserRepository
from salary_tracker.domain.user.services import IUserService
from salary_tracker.presentation.dependencies.data import get_user_repository, get_refresh_token_repository, \
    get_user_external_account_repository, get_sheet_repository
from salary_tracker.presentation.dependencies.presentation import get_settings
from salary_tracker.presentation.settings import AppSettings


async def get_user_service(
        user_repository: IUserRepository = Depends(get_user_repository),
) -> IUserService:
    return UserService(user_repository=user_repository)


async def get_token_service(
        refresh_token_repository: IRefreshTokenRepository = Depends(get_refresh_token_repository),
        settings: AppSettings = Depends(get_settings),
) -> ITokenService:
    return TokenService(
        refresh_token_repository=refresh_token_repository,
        access_token_private_key=settings.access_token_private_key,
        access_token_expiration_time=settings.access_token_expiration_time,
        access_token_issuer=settings.access_token_issuer,
        access_token_audience=settings.access_token_audience,
        refresh_token_expiration_time=settings.refresh_token_expiration_time
    )


async def get_auth_provider_user_data_extractor_factory(
        settings: AppSettings = Depends(get_settings),
) -> IAuthProviderUserDataExtractorFactory:
    return AuthProviderUserDataExtractorFactory(google_app_client_id=settings.google_app_client_id)


async def get_auth_provider_service(
        auth_provider_user_data_extractor_factory: AuthProviderUserDataExtractorFactory = Depends(
            get_auth_provider_user_data_extractor_factory),
        user_external_account_repository: IUserExternalAccountRepository = Depends(
            get_user_external_account_repository),
) -> IAuthProviderService:
    return AuthProviderService(
        auth_provider_user_data_extractor_factory=auth_provider_user_data_extractor_factory,
        user_external_account_repository=user_external_account_repository
    )


async def get_sheet_service(
        sheet_repository: ISheetRepository = Depends(get_sheet_repository),
        user_repository: IUserRepository = Depends(get_user_repository),
) -> ISheetService:
    return SheetService(
        sheet_repository=sheet_repository,
        user_repository=user_repository
    )
