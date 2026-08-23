import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger("sf_movies.exceptions")


class AppException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class UpstreamServiceException(AppException):
    def __init__(
        self,
        code: str = "UPSTREAM_SERVICE_ERROR",
        message: str = "External service unavailable or returned an error.",
        status_code: int = status.HTTP_502_BAD_GATEWAY,
    ):
        super().__init__(code=code, message=message, status_code=status_code)


class UpstreamTimeoutException(UpstreamServiceException):
    def __init__(
        self,
        code: str = "UPSTREAM_SERVICE_TIMEOUT",
        message: str = "External service request timed out.",
        status_code: int = status.HTTP_504_GATEWAY_TIMEOUT,
    ):
        super().__init__(code=code, message=message, status_code=status_code)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.warning(
        f"AppException: code={exc.code} status={exc.status_code} path={request.url.path} message='{exc.message}'"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        f"Unhandled Exception: path={request.url.path} error={exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
            }
        },
    )
