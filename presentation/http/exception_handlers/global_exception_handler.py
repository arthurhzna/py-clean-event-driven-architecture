from __future__ import annotations

import traceback

from http import HTTPStatus

from fastapi import (
    Request,
)

from presentation.http.errors.system_error import (
    SystemError,
)

from presentation.http.responses.shared.response_helper import (
    ParamHTTPResp,
    http_response,
)


async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    # traceback.print_exc()

    return http_response(
        ParamHTTPResp(
            code=(
                HTTPStatus
                .INTERNAL_SERVER_ERROR
            ),
            err=SystemError.INTERNAL_SERVER_ERROR,
        )
    )