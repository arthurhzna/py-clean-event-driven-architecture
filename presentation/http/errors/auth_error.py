from enum import Enum


class AuthError(
    str,
    Enum,
):
    UNAUTHORIZED = (
        "unauthorized"
    )

    INVALID_CREDENTIALS = (
        "invalid_credentials"
    )