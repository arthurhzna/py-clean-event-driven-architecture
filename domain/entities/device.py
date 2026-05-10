from dataclasses import dataclass


@dataclass()
class Device:
    device_id: str
    is_registered: bool = False
