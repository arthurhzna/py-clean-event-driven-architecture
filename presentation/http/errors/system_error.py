from __future__ import annotations

from enum import Enum


class SystemError(
    str,
    Enum,
):

    INTERNAL_SERVER_ERROR = (
        "internal_server_error"
    )