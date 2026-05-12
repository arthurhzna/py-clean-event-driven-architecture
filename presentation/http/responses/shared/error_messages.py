from presentation.http.errors.auth_error import (
    AuthError,
)

from presentation.http.errors.system_error import (
    SystemError,
)

from domain.errors.device_error import (
    DeviceError,
)

from presentation.http.errors.system_error import (
    SystemError,
)


ERROR_MAP: dict[str, str] = {

    DeviceError
    .DEVICE_NOT_FOUND
    .value:
        "Device not found",

    SystemError
    .INTERNAL_SERVER_ERROR
    .value:
        "Internal server error",

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