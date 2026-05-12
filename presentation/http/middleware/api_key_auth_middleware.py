from __future__ import annotations

from collections.abc import Callable

from fastapi import Header

from presentation.http.exceptions.unauthorized_exception import (
    UnauthorizedException,
)


def make_api_key_auth(
    api_key: str,
) -> Callable:

    async def api_key_auth(
        x_api_key: str | None = Header(
            default=None,
            alias="X-API-Key",
        ),
    ) -> None:
        if x_api_key != api_key:

            raise UnauthorizedException()

    return api_key_auth