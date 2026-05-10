from __future__ import annotations

import os

from dataclasses import (
    dataclass,
)


@dataclass
class MQTTConfig:
    broker: str
    port: int
    username: str
    password: str
    use_tls: bool


def load_mqtt_config() -> MQTTConfig:

    return MQTTConfig(
        broker=os.getenv(
            "MQTT_BROKER",
            "localhost",
        ),

        port=int(
            os.getenv(
                "MQTT_PORT",
                "1883",
            )
        ),

        username=os.getenv(
            "MQTT_USERNAME",
            "",
        ),

        password=os.getenv(
            "MQTT_PASSWORD",
            "",
        ),

        use_tls=os.getenv(
            "MQTT_USE_TLS",
            "false",
        ).lower() == "true",
    )