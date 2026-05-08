from __future__ import annotations

from presentation.messaging.router import (
    MessageRouter,
)

from presentation.messaging.mqtt.handlers import (
    RegisterDeviceMessageHandler,
)

from application.usecase.register_device_usecase import (
    RegisterDeviceUseCase,
)

def configure_message_router(
    router: MessageRouter,
    register_device_usecase: RegisterDeviceUseCase,
) -> None:

    router.register(
        "camera/register",
        RegisterDeviceMessageHandler(register_device_usecase),
    )
