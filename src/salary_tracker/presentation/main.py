from os import environ

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from salary_tracker.presentation.dependencies.presentation import get_settings
from salary_tracker.presentation.error_handler import apply_error_handler
from salary_tracker.presentation.routers.root import get_root_router
from salary_tracker.presentation.settings import AppSettings


def create_app(settings: AppSettings) -> FastAPI:
    app_version = environ.get('APP_VERSION', 'unknown')

    fastapi = FastAPI(
        title='Salary Tracker',
        root_path=settings.root_path,
        servers=[{'url': settings.root_path}] if settings.root_path else None,
        version=app_version
    )

    apply_error_handler(fastapi)

    cors_allow_origins = settings.cors_allow_origins
    fastapi.add_middleware(
        CORSMiddleware,
        allow_origins=cors_allow_origins if cors_allow_origins else ['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    print(cors_allow_origins)

    fastapi.include_router(get_root_router())

    return fastapi


app = create_app(get_settings())

if __name__ == '__main__':
    import uvicorn

    uvicorn.run("src.salary_tracker.presentation.main:app", host='0.0.0.0', port=80, reload=True, reload_dirs=['src'])
