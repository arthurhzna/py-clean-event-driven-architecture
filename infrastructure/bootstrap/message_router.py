from __future__ import annotations

from collections.abc import (
    Callable,
)

from application.usecase.register_device_usecase import (
    RegisterDeviceUseCase,
)

from presentation.messaging.mqtt.handlers.register_device_message_handler import (
    RegisterDeviceMessageHandler,
)

from presentation.messaging.router import (
    MessageRouter,
)


def register_message_handlers(
    router: MessageRouter,
    register_device_usecase_factory: Callable[
        [],
        RegisterDeviceUseCase,
    ],
) -> None:

    router.register(
        "device/register",
        RegisterDeviceMessageHandler(
            create_usecase=(
                register_device_usecase_factory
            ),
        ),
    )