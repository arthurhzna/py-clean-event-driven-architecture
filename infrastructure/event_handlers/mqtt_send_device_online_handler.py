from __future__ import annotations

from domain.events.device_online_event import (
    DeviceOnlineEvent,
)
from infrastructure.messaging.mqtt.messages.device_online_message import (
    DeviceOnlineMessage,
)
from infrastructure.messaging.mqtt.mqtt_client import (
    MqttClient,
)


class MQTTSendDeviceOnlineHandler:
    def __init__(
        self,
        mqtt_client: MqttClient,
    ) -> None:

        self._mqtt_client = mqtt_client

    def __call__(
        self,
        event: DeviceOnlineEvent,
    ) -> None:

        message = DeviceOnlineMessage(
            device_id=event.device_id,
            timestamp=event.timestamp.isoformat(),
        )

        self._mqtt_client.publish(
            topic="device/online",
            payload=message.to_bytes(),
        )