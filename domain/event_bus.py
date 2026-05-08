from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

EventHandler = Callable[[Any], None]


class BaseEventBus(ABC):
    @abstractmethod
    def publish(self, event: object) -> None:
        raise NotImplementedError

    @abstractmethod
    def subscribe(
        self,
        event_type: type,
        handler: EventHandler,
    ) -> None:
        raise NotImplementedError
