from domain.events import (
    DeviceOnlineEvent,
    PersonDisappearedEvent
)
from infrastructure.event_handlers.redis_publish_handler import (
    RedisPublishHandler,
    PersonDisappearedHandler
)

from domain.interface.messaging.event_bus import BaseEventBus


def register_events(
    event_bus: BaseEventBus,
) -> None:
    event_bus.subscribe(
        DeviceOnlineEvent,
        RedisPublishHandler(),  
    )

def person_disappeared_event(
    event_bus: BaseEventBus,
) -> None:
    event_bus.subscribe(
        PersonDisappearedEvent,
        PersonDisappearedHandler(),
    )
