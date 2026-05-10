from __future__ import annotations

from pydantic import BaseModel


class RegisterDeviceData(BaseModel):
    device_id: str
    status: str