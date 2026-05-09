from dataclasses import (
    dataclass,
)

from application.interface.persistence.datastore import (
    DataStore,
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
    uow: UnitOfWork
    state_manager: StateManager
    event_bus: BaseEventBus
    mqtt_client: MqttClient
