from __future__ import annotations

from starlette.middleware.base import (
    BaseHTTPMiddleware,
)

from starlette.requests import (
    Request,
)


class LoggingMiddleware(
    BaseHTTPMiddleware,
):

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):

        print(
            f"[HTTP] "
            f"{request.method} "
            f"{request.url.path}"
        )

        response = await call_next(
            request,
        )

        return response