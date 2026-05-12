from __future__ import annotations

from fastapi import (
    Request,
)

from presentation.http.exceptions.app_exception import (
    AppException,
)

from presentation.http.responses.shared.response_helper import (
    ParamHTTPResp,
    http_response,
)


async def global_exception_handler(
    request: Request,
    exc: Exception,
):

    app_exception = AppException()

    if isinstance(
        exc,
        AppException,
    ):

        app_exception = exc

    return http_response(
        ParamHTTPResp(
            code=app_exception.code,
            err=app_exception.err,
        )
    )