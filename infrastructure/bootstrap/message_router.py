from __future__ import annotations

from application.usecase.register_device_usecase import (
    RegisterDeviceUseCase,
)
from presentation.messaging.mqtt.handlers.register_device_message_handler import (
    RegisterDeviceMessageHandler,
)
from presentation.messaging.router import (
    MessageRouter,
)


def configure_message_router(
    router: MessageRouter,
    register_device_usecase: RegisterDeviceUseCase,
) -> None:

    router.register(
        "camera/register",
        RegisterDeviceMessageHandler(register_device_usecase),
    )
