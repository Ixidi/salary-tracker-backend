from fastapi import APIRouter

def get_auth_router():
    from salary_tracker.presentation.routers.auth.me import router as me_router
    from salary_tracker.presentation.routers.auth.auth_provider_login import router as auth_provider_login_router

    router = APIRouter(prefix="/auth", tags=["Auth"])
    router.include_router(me_router)
    router.include_router(auth_provider_login_router)
    return router

def get_sheet_router():
    from salary_tracker.presentation.routers.sheet.create import router as create_sheet

    router = APIRouter(prefix="/sheet", tags=["Sheet"])
    router.include_router(create_sheet)
    return router

def get_root_router():
    router = APIRouter(prefix="/api/v1")
    router.include_router(get_auth_router())
    router.include_router(get_sheet_router())
    return router