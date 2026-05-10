from dataclasses import dataclass


@dataclass
class DeviceRuntimeState:
    can_publish: bool = False