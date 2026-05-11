from dataclasses import (
    dataclass,
)

from psycopg2.pool import (
    ThreadedConnectionPool,
)

from application.state.state_manager import (
    StateManager,
)

from application.interfaces.messaging.event_bus import (
    EventBus,
)

from infrastructure.messaging.mqtt.mqtt_client import (
    MqttClient,
)


@dataclass
class ApplicationContainer:
    pool: ThreadedConnectionPool
    state_manager: StateManager
    event_bus: EventBus
    mqtt_client: MqttClient