from __future__ import annotations

from interface_adapters.messaging.router import (
    MessageRouter,
)
from usecases.detection.process_frame_usecase import (
    ProcessFrameUseCase,
)
from usecases.device.register_device_usecase import (
    RegisterDeviceUseCase,
)


def configure_message_router(
    router: MessageRouter,
    register_device_usecase: RegisterDeviceUseCase,
    process_frame_usecase: ProcessFrameUseCase,
) -> None:

    router.register(
        "device/register",
        register_device_usecase.execute,
    )

    router.register(
        "camera/frame",
        process_frame_usecase.execute,
    )
