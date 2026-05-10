from presentation.http.errors.auth_error import (
    AuthError,
)

from domain.errors.device_error import (
    DeviceError,
)


ERROR_MAP: dict[str, str] = {

    DeviceError
    .DEVICE_NOT_FOUND
    .value:
        "Device not found",

    DeviceError
    .DEVICE_ALREADY_REGISTERED
    .value:
        "Device already registered",

    AuthError
    .UNAUTHORIZED
    .value:
        "Unauthorized access",

    AuthError
    .INVALID_CREDENTIALS
    .value:
        "Invalid credentials",
}