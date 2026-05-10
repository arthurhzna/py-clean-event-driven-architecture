from dataclasses import dataclass


@dataclass
class RegisterDeviceOutput:
    device_id: str
    is_registered: bool