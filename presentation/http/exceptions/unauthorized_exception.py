from __future__ import annotations

from http import HTTPStatus

from presentation.http.errors.auth_error import (
    AuthError,
)

from presentation.http.exceptions.app_exception import (
    AppException,
)


class UnauthorizedException(
    AppException,
):

    def __init__(
        self,
    ) -> None:

        super().__init__(
            code=(
                HTTPStatus
                .UNAUTHORIZED
            ),
            err=(
                AuthError
                .UNAUTHORIZED
            ),
        )