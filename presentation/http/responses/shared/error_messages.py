from application.errors.auth_error import (
    AuthError,
)

from application.errors.device_error import (
    DeviceError,
)


ERROR_MAP: dict[str, str] = {

    DeviceError.DEVICE_NOT_FOUND:
        "Device not found",

    DeviceError
    .DEVICE_ALREADY_REGISTERED:
        "Device already registered",

    AuthError.UNAUTHORIZED:
        "Unauthorized access",

    AuthError.INVALID_CREDENTIALS:
        "Invalid credentials",
}