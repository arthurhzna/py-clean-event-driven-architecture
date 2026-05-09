from __future__ import annotations

from dataclasses import (
    dataclass,
)

from application.state.state_manager import (
    StateManager,
)
from infrastructure.bootstrap.container import (
    ApplicationContainer,
)
from infrastructure.bootstrap.database import (
    init_database,
)
from infrastructure.bootstrap.event_bus import (
    register_events,
)
from infrastructure.bootstrap.message_router import (
    configure_message_router,
)
from infrastructure.bootstrap.repository import (
    build_device_repository,
)
from infrastructure.bootstrap.services import (
    PricingService,
)
from infrastructure.bootstrap.usecases import (
    build_create_order_usecase,
    build_register_device_usecase,
    build_send_device_online_usecase,
)
from infrastructure.config.config import (
    load_config,
)
from infrastructure.event_bus.in_memory_event_bus import (
    InMemoryEventBus,
)
from infrastructure.messaging.mqtt.mqtt_client import (
    MqttClient,
)
from infrastructure.runner.device_runtime_runner import (
    DeviceRuntimeRunner,
)
from presentation.messaging.router import (
    MessageRouter,
)


@dataclass
class Application:
    container: ApplicationContainer
    mqtt_client: MqttClient
    device_runtime_runner: DeviceRuntimeRunner


def build_application() -> Application:

    config = load_config()

    # 1. Infrastructure
    pool = init_database(
        config.database,
    )

    uow = UnitOfWork(
        pool=pool,
    )

    state_manager = StateManager()

    event_bus = InMemoryEventBus()

    mqtt_client = MqttClient(
        broker_url="mqtt://localhost:1883",
    )

    # 2. Shared container
    container = ApplicationContainer(
        uow=uow,
        state_manager=state_manager,
        event_bus=event_bus,
        mqtt_client=mqtt_client,
    )

    # 3. Register event handlers
    register_events(container)

    # 4. Repositories
    device_repository = build_device_repository()

    # 5. Services
    pricing_service = PricingService()

    # 6. Use cases
    create_order_usecase = build_create_order_usecase(
        pricing_service=pricing_service,
    )

    register_device_usecase = build_register_device_usecase(
        container=container,
        device_repository=(device_repository),
    )

    send_device_online_usecase = build_send_device_online_usecase(
        container=container,
    )

    # 7. Message router
    router = MessageRouter()

    configure_message_router(
        router=router,
        register_device_usecase=(register_device_usecase),
    )

    # 8. MQTT wiring
    mqtt_client.on_message = router.dispatch

    mqtt_client.connect()

    mqtt_client.subscribe(
        topic="camera/register",
    )

    # 9. Runtime runners
    device_runtime_runner = DeviceRuntimeRunner(
        send_device_online_usecase=(send_device_online_usecase),
        device_id="hardcode",
    )

    return Application(
        container=container,
        mqtt_client=mqtt_client,
        device_runtime_runner=(device_runtime_runner),
    )
