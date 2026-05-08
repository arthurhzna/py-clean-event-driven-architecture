from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

RouteHandler = Callable[..., Any]


@dataclass
class MessageRouter:
    _handlers: dict[str, RouteHandler] = field(default_factory=dict)

    def register(
        self,
        route: str,
        handler: RouteHandler,
    ) -> None:

        self._handlers[route] = handler

    def dispatch(
        self,
        route: str,
        payload: bytes,
    ) -> None:

        handler = self._handlers.get(route)

        if handler is None:
            return

        handler(payload)
