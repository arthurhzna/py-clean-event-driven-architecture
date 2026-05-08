from domain.events.device_online_event import (
    DeviceOnlineEvent,
)
from infrastructure.bootstrap.container import (
    ApplicationContainer,
)
from infrastructure.event_handlers.mqtt_send_device_online_handler import (
    MQTTSendDeviceOnlineHandler,
)


def register_events(
    container: ApplicationContainer,
) -> None:

    container.event_bus.subscribe(
        DeviceOnlineEvent,
        MQTTSendDeviceOnlineHandler(
            container.mqtt_client,
        ),
    )
