from __future__ import annotations

from bootstrap.container import (
    ApplicationContainer,
)

from bootstrap.usecase_factories.scoped_factories import (
    build_register_device_usecase,
)

from presentation.messaging.mqtt.handlers.register_device_message_handler import (
    RegisterDeviceMessageHandler,
)

from presentation.messaging.router import (
    MessageRouter,
)


def register_message_handlers(
    router: MessageRouter,
    container: ApplicationContainer,
) -> None:

    router.register(
        "device/register",
        RegisterDeviceMessageHandler(
            create_usecase=(
                lambda: build_register_device_usecase(
                    container=container,
                )
            ),
        ),
    )