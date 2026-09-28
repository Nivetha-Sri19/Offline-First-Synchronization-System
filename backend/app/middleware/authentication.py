from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Authentication is intentionally resolved at the API dependency layer.

    This middleware only exposes the authenticated request context when
    another upstream component has already populated it. JWT validation
    itself remains in api/deps.py so public endpoints such as login and
    registration are not blocked.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request.state.authenticated = False

        response = await call_next(request)

        return response