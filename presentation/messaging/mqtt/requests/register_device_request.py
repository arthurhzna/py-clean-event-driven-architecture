from __future__ import annotations

from pydantic import (
    BaseModel,
    Field,
)


class RegisterDeviceRequest(
    BaseModel,
):
    device_id: str = Field(
        min_length=1,
    )