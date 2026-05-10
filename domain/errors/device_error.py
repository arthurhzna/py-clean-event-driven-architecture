from __future__ import annotations

from enum import Enum


class DeviceError(
    str,
    Enum,
):
    DEVICE_ALREADY_REGISTERED = (
        "device_already_registered"
    )

    DEVICE_NOT_FOUND = (
        "device_not_found"
    )