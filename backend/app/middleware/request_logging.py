import logging
import time
from collections.abc import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("sf_movies.middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            f"request_completed method={request.method} path={request.url.path} "
            f"status={response.status_code} duration_ms={process_time_ms:.2f}"
        )
        return response
