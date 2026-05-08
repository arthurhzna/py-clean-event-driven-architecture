from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


MessageHandler = Callable[[str, bytes], None]


@dataclass
class MqttConsumer:
    on_message: MessageHandler

    def handle(
        self,
        topic: str,
        payload: bytes,
    ) -> None:

        logger.debug(
            "MQTT message topic=%s",
            topic,
        )

        self.on_message(topic, payload)
