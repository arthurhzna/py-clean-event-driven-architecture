from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field


class RegisterDeviceRequest(BaseModel):
    device_id: str = Field(min_length=1)