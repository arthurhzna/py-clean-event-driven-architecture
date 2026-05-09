from dataclasses import (
    dataclass,
)

from psycopg2.pool import (
    ThreadedConnectionPool,
)

from application.state.state_manager import (
    StateManager,
)

from domain.interface.messaging.event_bus import (
    BaseEventBus,
)

from infrastructure.messaging.mqtt.mqtt_client import (
    MqttClient,
)


@dataclass
class ApplicationContainer:
    pool: ThreadedConnectionPool
    state_manager: StateManager
    event_bus: BaseEventBus
    mqtt_client: MqttClient