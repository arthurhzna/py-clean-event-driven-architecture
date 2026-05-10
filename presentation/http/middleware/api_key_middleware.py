from __future__ import annotations

from http import HTTPStatus

from starlette.middleware.base import (
    BaseHTTPMiddleware,
)

from starlette.requests import (
    Request,
)

from presentation.http.errors.auth_error import (
    AuthError,
)

from presentation.http.responses.shared.response_helper import (
    ParamHTTPResp,
    http_response,
)


class ApiKeyMiddleware(
    BaseHTTPMiddleware,
):

    def __init__(
        self,
        app,
        api_key: str,
    ) -> None:

        super().__init__(app)

        self._api_key = api_key

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):

        api_key = request.headers.get(
            "X-API-Key",
        )

        if api_key != self._api_key:

            return http_response(
                ParamHTTPResp(
                    code=(
                        HTTPStatus
                        .UNAUTHORIZED
                    ),
                    err=(
                        AuthError
                        .UNAUTHORIZED
                    ),
                )
            )

        return await call_next(
            request,
        )