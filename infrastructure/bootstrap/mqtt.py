from infrastructure.config.device import (
    DeviceConfig,
)

from infrastructure.config.mqtt import (
    MQTTConfig,
)

from infrastructure.messaging.mqtt.mqtt_client import (
    MqttClient,
)


def build_mqtt_client(
    mqtt_config: MQTTConfig,
    device_config: DeviceConfig,
) -> MqttClient:

    return MqttClient(
        broker=mqtt_config.broker,
        port=mqtt_config.port,
        client_id=(
            f"device_client_{device_config.device_id}"
        ),
        username=mqtt_config.username,
        password=mqtt_config.password,
        use_tls=mqtt_config.use_tls,
    )
