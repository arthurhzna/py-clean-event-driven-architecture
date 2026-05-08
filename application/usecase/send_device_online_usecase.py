from __future__ import annotations

from datetime import (
    UTC,
    datetime,
)

from domain.events.device_online_event import (
    DeviceOnlineEvent,
)
from domain.interface.messaging.event_bus import (
    BaseEventBus,
)


class SendDeviceOnlineUseCase:
    def __init__(
        self,
        event_bus: BaseEventBus,
    ) -> None:

        self._event_bus = event_bus

    def execute(
        self,
        device_id: str,
    ) -> None:

        event = DeviceOnlineEvent(
            device_id=device_id,
            timestamp=datetime.now(
                UTC,
            ),
        )

        self._event_bus.publish(
            event,
        )
