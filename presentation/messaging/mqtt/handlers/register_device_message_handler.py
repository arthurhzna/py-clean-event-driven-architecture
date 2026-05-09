from __future__ import annotations

import json

from collections.abc import (
    Callable,
)

from application.usecase.register_device_usecase import (
    RegisterDeviceUseCase,
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

        data = json.loads(
            payload.decode(),
        )

        device_id = int(
            data["device_id"],
        )

        usecase = (
            self._create_usecase()
        )

        usecase.execute(
            device_id=device_id,
        )