import json

from application.usecase.register_device_usecase import (
    RegisterDeviceUseCase,
)


class RegisterDeviceMessageHandler:
    def __init__(
        self,
        register_device_usecase: RegisterDeviceUseCase,
    ) -> None:

        self._register_device_usecase = register_device_usecase

    def __call__(
        self,
        topic: str,
        payload: bytes,
    ) -> None:

        data = json.loads(
            payload.decode(),
        )

        device_id = int(
            data["device_id"],
        )

        self._register_device_usecase.execute(
            device_id=device_id,
        )
