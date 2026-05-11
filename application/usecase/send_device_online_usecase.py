from __future__ import annotations

from datetime import (
    UTC,
    datetime,
)

from application.interfaces.persistence.unit_of_work import (
    UnitOfWork,
)

from domain.events.device_online_event import (
    DeviceOnlineEvent,
)

from application.interfaces.messaging.event_bus import (
    EventBus,
)


class SendDeviceOnlineUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        event_bus: EventBus,
    ) -> None:

        self._uow = uow

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