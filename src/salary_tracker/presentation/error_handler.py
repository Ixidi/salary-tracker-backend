from urllib.request import Request

from fastapi import FastAPI
from starlette.responses import JSONResponse

from salary_tracker.usecase.exceptions import UseCaseException, InvalidTokenException


def apply_error_handler(app: FastAPI):
    error_codes = {
        InvalidTokenException: 401
    }

    @app.exception_handler(UseCaseException)
    async def exception_handler(request: Request, exc: UseCaseException):
        error_name = exc.__class__.__name__.removesuffix('Exception')
        error_code = error_codes[exc.__class__] if exc.__class__ in error_codes else 400
        return JSONResponse(
            status_code=error_code,
            content={
                "error": exc.key,
                "detail": exc.message
            }
        )
