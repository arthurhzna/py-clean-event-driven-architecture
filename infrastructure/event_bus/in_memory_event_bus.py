from __future__ import annotations

from collections import defaultdict

from domain.interface.messaging.event_bus import (
    BaseEventBus,
    EventHandler,
)

class InMemoryEventBus(BaseEventBus):
    def __init__(self) -> None:
        self._handlers: dict[type, list[EventHandler]] = defaultdict[type, list[EventHandler]](list)

    def publish(self, event: object) -> None:
        handlers = self._handlers.get(type(event), [])

        for handler in handlers:
            handler(event)

    def subscribe(
        self,
        event_type: type,
        handler: EventHandler,
    ) -> None:
        self._handlers[event_type].append(handler)
