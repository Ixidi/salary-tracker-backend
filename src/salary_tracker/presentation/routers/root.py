from fastapi import APIRouter

from salary_tracker.presentation.responses.error import ErrorResponse


def get_auth_router():
    from salary_tracker.presentation.routers.auth.me import router as me_router
    from salary_tracker.presentation.routers.auth.auth_provider_login import router as auth_provider_login_router
    from salary_tracker.presentation.routers.auth.refresh_token import router as refresh_token_router

    router = APIRouter(prefix="/auth", tags=["Auth"])
    router.include_router(me_router)
    router.include_router(auth_provider_login_router)
    router.include_router(refresh_token_router)
    return router

def get_sheet_router():
    from salary_tracker.presentation.routers.sheet.create import router as create_sheet
    from salary_tracker.presentation.routers.sheet.get import router as get_sheet
    from salary_tracker.presentation.routers.sheet.rate_table.add import router as add_rate_table
    from salary_tracker.presentation.routers.sheet.rate_table.get_for_datetime import router as get_rate_table_for_datetime
    from salary_tracker.presentation.routers.sheet.record.add import router as add_sheet_record
    from salary_tracker.presentation.routers.sheet.record.get_filtered import router as get_paginated_sheet_records
    from salary_tracker.presentation.routers.sheet.salary.calculate import router as calculate_salary
    from salary_tracker.presentation.routers.sheet.record.delete import router as delete_record
    from salary_tracker.presentation.routers.sheet.delete import router as delete_sheet
    from salary_tracker.presentation.routers.sheet.get_user import router as get_user

    router = APIRouter(prefix="/sheets", tags=["Sheet"])
    router.include_router(create_sheet)
    router.include_router(get_user)
    router.include_router(get_sheet)
    router.include_router(delete_sheet)
    router.include_router(add_rate_table)
    router.include_router(get_rate_table_for_datetime)
    router.include_router(get_paginated_sheet_records)
    router.include_router(add_sheet_record)
    router.include_router(delete_record)
    router.include_router(calculate_salary)
    return router

def get_root_router():
    router = APIRouter(
        prefix="/api/v1",
        responses={
            400: {"model": ErrorResponse},
            401: {"model": ErrorResponse},
            403: {"model": ErrorResponse},
        }
    )
    router.include_router(get_auth_router())
    router.include_router(get_sheet_router())
    return router