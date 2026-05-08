from domain.events.detection_triggered_event import (
    DetectionTriggeredEvent,
)
from infrastructure.event_handlers.redis_publish_handler import (
    RedisPublishHandler,
)

from domain.event_bus import BaseEventBus


def register_events(
    event_bus: BaseEventBus,
) -> None:
    event_bus.subscribe(
        DetectionTriggeredEvent,
        RedisPublishHandler(),
    )

    event_bus.subscribe(
        DetectionTriggeredEvent,
        RedisPublishHandler(),
    )
