from __future__ import annotations

from collections.abc import Callable

from pydantic import (
    ValidationError,
)

from application.usecase.register_device_usecase import (
    RegisterDeviceUseCase,
)

from presentation.messaging.mqtt.requests.register_device_request import (
    RegisterDeviceRequest,
)


class RegisterDeviceMessageHandler:
    def __init__(
        self,
        create_usecase: Callable[
            [],
            RegisterDeviceUseCase,
        ],
    ) -> None:

        self._create_usecase = (
            create_usecase
        )

    def __call__(
        self,
        topic: str,
        payload: bytes,
    ) -> None:

        try:

            request = (
                RegisterDeviceRequest.model_validate_json(
                    payload,
                )
            )

        except ValidationError:

            return

        usecase = (
            self._create_usecase()
        )

        usecase.execute(
            device_id=request.device_id,
        )