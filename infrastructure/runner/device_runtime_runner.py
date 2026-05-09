from __future__ import annotations

import time

from collections.abc import (
    Callable,
)

from application.usecase.send_device_online_usecase import (
    SendDeviceOnlineUseCase,
)


class DeviceRuntimeRunner:
    def __init__(
        self,
        create_usecase: Callable[
            [],
            SendDeviceOnlineUseCase,
        ],
        device_id: str,
        interval_seconds: int = 5,
    ) -> None:

        self._create_usecase = (
            create_usecase
        )

        self._device_id = device_id

        self._interval_seconds = (
            interval_seconds
        )

    def run(
        self,
    ) -> None:

        while True:

            try:

                usecase = (
                    self._create_usecase()
                )

                usecase.execute(
                    device_id=self._device_id,
                )

            except Exception:
                pass

            time.sleep(
                self._interval_seconds,
            )