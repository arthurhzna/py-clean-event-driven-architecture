from __future__ import annotations

from dataclasses import (
    dataclass,
)

from application.state.state_manager import (
    StateManager,
)

from presentation.messaging.router import (
    MessageRouter,
)

from bootstrap.container import (
    ApplicationContainer,
)

from bootstrap.database import (
    init_database,
)

from bootstrap.event_bus import (
    register_events,
)

from bootstrap.message_router import (
    register_message_handlers,
)

from bootstrap.mqtt import (
    build_mqtt_client,
)

from bootstrap.services import (
    PricingService,
)

from bootstrap.usecase_factories.scoped_factories import (
    build_send_device_online_usecase,
)

from bootstrap.usecase_factories.singleton_factories import (
    build_create_order_usecase,
)

from bootstrap.http import (
    build_fastapi_app,
    build_uvicorn_config,
)

from config.config import (
    load_config,
)

from infrastructure.messaging.event_bus.in_memory_event_bus import (
    InMemoryEventBus,
)

from infrastructure.runner.device_runtime_runner import (
    DeviceRuntimeRunner,
)

@dataclass
class Application:
    device_runtime_runner: (
        DeviceRuntimeRunner
    )
    uvicorn_config: dict

def build_application() -> Application:

    config = load_config()

    pool = init_database(
        config.database,
    )

    state_manager = StateManager()

    event_bus = InMemoryEventBus()

    mqtt_client = build_mqtt_client(
        mqtt_config=config.mqtt,
        device_config=config.device,
    )

    container = ApplicationContainer(
        pool=pool,
        state_manager=state_manager,
        event_bus=event_bus,
        mqtt_client=mqtt_client,
    )

    register_events(
        container,
    )

    pricing_service = PricingService()

    create_order_usecase = (
        build_create_order_usecase(
            pricing_service=pricing_service,
        )
    )

    router = MessageRouter()

    register_message_handlers(
        router=router,
        container=container,
    )

    consumer = MqttConsumer(
        on_message=router.dispatch,
    )

    mqtt_client.on_message = consumer.handle

    mqtt_client.connect()

    mqtt_client.subscribe(
        [
            (
                "device/config",
                0,
            ),
            (
                "device/register",
                1,
            ),
            (
                "device/publish",
                1,
            ),
        ]
    )

    device_runtime_runner = (
        DeviceRuntimeRunner(
            create_usecase=(
                lambda:
                    build_send_device_online_usecase(
                        container=container,
                    )
            ),
            device_id=config.device.device_id,
        )
    )

    app = build_fastapi_app(
        container=container,
        http_config=config.http,
    )
    uvicorn_config = build_uvicorn_config(
        app=app,
        http_config=config.http,
    )

    return Application(
        device_runtime_runner=(
            device_runtime_runner
        ),
        uvicorn_config=uvicorn_config,
    )
