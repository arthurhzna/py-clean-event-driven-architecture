from dataclasses import dataclass
from datetime import datetime

@dataclass
class DeviceOnlineEvent():
    timestamp: datetime