from domain.events import (
    DeviceOnlineEvent,
)
from infrastructure.event_handlers.redis_publish_handler import (
    RedisPublishHandler,
)

from domain.interface.messaging.event_bus import BaseEventBus


def register_events(
    event_bus: BaseEventBus,
) -> None:
    event_bus.subscribe(
        DeviceOnlineEvent,
        RedisPublishHandler(),
    )

