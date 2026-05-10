from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from http import HTTPStatus
from typing import Any

from fastapi.responses import JSONResponse

from presentation.http.responses.shared.error_messages import (
    ERROR_MAP,
)

from presentation.http.responses.shared.response_constants import (
    ERROR,
    SUCCESS,
)

from presentation.http.responses.shared.base_response import (
    Response,
)


@dataclass
class ParamHTTPResp:
    code: int

    data: Any = field(
        default=None,
    )

    err: str | None = field(
        default=None,
    )

    message: str | None = field(
        default=None,
    )

    token: str | None = field(
        default=None,
    )


def http_response(
    param: ParamHTTPResp,
) -> JSONResponse:

    if param.err is None:

        return JSONResponse(
            status_code=param.code,
            content=Response(
                status=SUCCESS,
                message=(
                    param.message
                    or HTTPStatus(
                        param.code
                    ).phrase
                ),
                data=param.data,
                token=param.token,
            ).model_dump(
                exclude_none=True,
            ),
        )

    error_code = str(
        param.err,
    )

    message = (
        param.message
        or ERROR_MAP.get(
            error_code,
            HTTPStatus
            .INTERNAL_SERVER_ERROR
            .phrase,
        )
    )

    return JSONResponse(
        status_code=param.code,
        content=Response(
            status=ERROR,
            message=message,
            data=param.data,
        ).model_dump(
            exclude_none=True,
        ),
    )