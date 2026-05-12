from __future__ import annotations

from http import HTTPStatus

from presentation.http.errors.system_error import (
    SystemError,
)


class AppException(
    Exception,
):

    def __init__(
        self,
        code=(
            HTTPStatus
            .INTERNAL_SERVER_ERROR
        ),
        err=(
            SystemError
            .INTERNAL_SERVER_ERROR
        ),
    ) -> None:

        self.code = code
        self.err = err