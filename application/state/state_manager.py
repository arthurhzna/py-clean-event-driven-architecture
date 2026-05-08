# application/state/state_manager.py

from threading import Lock

from application.state.device_state import (
    DeviceState,
)

from application.state.screenshot_state import (
    ScreenshotState,
)


class StateManager:

    def __init__(self):

        self._lock = Lock()

        self._device_state = DeviceState()

        self._screenshot_state = (
            ScreenshotState()
        )

    def update_device_registration(
        self,
        is_registered: bool,
    ) -> None:

        with self._lock:

            self._device_state.is_registered = (
                is_registered
            )

    def get_device_registration_state(
        self,
    ) -> bool:

        with self._lock:

            return (
                self._device_state.is_registered
            )

    def get_device_state(
        self,
    ) -> DeviceState:

        with self._lock:

            return DeviceState(
                is_registered=(
                    self._device_state.is_registered
                ),
            )

    def update_screenshot_state(
        self,
        url,
        flag: bool,
    ) -> None:

        with self._lock:

            self._screenshot_state.url = url

            self._screenshot_state.flag = flag

    def get_screenshot_state(
        self,
    ) -> ScreenshotState:

        with self._lock:

            return ScreenshotState(
                url=self._screenshot_state.url,
                flag=self._screenshot_state.flag,
            )

    def reset_screenshot_state(
        self,
    ) -> None:

        with self._lock:

            self._screenshot_state = (
                ScreenshotState()
            )