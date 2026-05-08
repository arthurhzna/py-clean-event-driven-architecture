from dataclasses import dataclass
from datetime import datetime


@dataclass
class DeviceOnlineEvent:
    device_id: str
    timestamp: datetime
