from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger

logger = get_logger("http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        start = time.perf_counter()

        request_id = getattr(
            request.state,
            "request_id",
            None,
        )

        try:
            response = await call_next(request)

            elapsed = time.perf_counter() - start

            logger.info(
                "request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
                request_id,
                request.method,
                request.url.path,
                response.status_code,
                elapsed * 1000,
            )

            return response

        except Exception:
            elapsed = time.perf_counter() - start

            logger.exception(
                "request_id=%s method=%s path=%s duration_ms=%.2f",
                request_id,
                request.method,
                request.url.path,
                elapsed * 1000,
            )

            raise