from __future__ import annotations

import time

from application.usecase.send_device_online_usecase import (
    SendDeviceOnlineUseCase,
)


class DeviceRuntimeRunner:
    def __init__(
        self,
        send_device_online_usecase: SendDeviceOnlineUseCase,
        device_id: str,
        interval_seconds: int = 5,
    ) -> None:

        self._send_device_online_usecase = send_device_online_usecase
        self._device_id = device_id
        self._interval_seconds = interval_seconds

    def run(
        self,
    ) -> None:

        while True:
            try:
                self._send_device_online_usecase.execute(
                    device_id=self._device_id,
                )

            except Exception:
                pass

            time.sleep(
                self._interval_seconds,
            )
