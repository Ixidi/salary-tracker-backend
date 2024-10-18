from urllib.request import Request

from fastapi import FastAPI
from starlette.responses import JSONResponse

from salary_tracker.presentation.responses.error import ErrorResponse
from salary_tracker.usecase.exceptions import UseCaseException, AuthException, PermissionDeniedException


def apply_error_handler(app: FastAPI):
    error_codes = {
        AuthException: 401,
        PermissionDeniedException: 403
    }

    @app.exception_handler(UseCaseException)
    async def exception_handler(request: Request, exc: UseCaseException):
        error_code = error_codes[exc.__class__] if exc.__class__ in error_codes else 400
        return JSONResponse(
            status_code=error_code,
            content=ErrorResponse(error=exc.key, detail=exc.message).model_dump()
        )

    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc: Exception):
        # TODO insert request id
        return JSONResponse(
            status_code=500,
            content={
                "error": "unexpected_error",
                "detail": "An unexpected error occurred, please report this."
            }
        )
