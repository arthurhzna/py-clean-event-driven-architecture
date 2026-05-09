from __future__ import annotations

import os

from dataclasses import (
    dataclass,
)


@dataclass
class DeviceConfig:
    device_id: str


def load_device_config() -> DeviceConfig:

    return DeviceConfig(
        device_id=os.getenv(
            "DEVICE_ID",
            "hardcode",
        ),
    )