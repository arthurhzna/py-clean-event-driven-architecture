from dataclasses import dataclass


@dataclass()
class Device:
    device_id: int
    is_registered: bool = False
