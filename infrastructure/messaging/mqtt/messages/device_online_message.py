import json
from dataclasses import (
    asdict,
    dataclass,
)


@dataclass
class DeviceOnlineMessage:
    device_id: str
    timestamp: str

    def to_bytes(
        self,
    ) -> bytes:

        return json.dumps(
            asdict(self),
        ).encode()
