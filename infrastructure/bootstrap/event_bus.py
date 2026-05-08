from domain.events import (
    DeviceOnlineEvent,
)
from domain.interface.messaging.event_bus import BaseEventBus
from infrastructure.event_handlers.redis_publish_handler import (
    MQTTPublishHandler,
)


def register_events(
    event_bus: BaseEventBus,
) -> None:
    event_bus.subscribe(
        DeviceOnlineEvent,
        MQTTPublishHandler(),
    )
