from dataclasses import dataclass
from typing import Optional

@dataclass
class DeviceState:
    is_registered: bool = False