# application/state/state_manager.py

from threading import Lock

from application.state.device_runtime_state import (
    DeviceRuntimeState,
)

from application.state.screenshot_state import (
    ScreenshotState,
)


class StateManager:
    def __init__(
        self,
    ) -> None:

        self._device_lock = Lock()

        self._screenshot_lock = Lock()

        self._device_runtime_state = (
            DeviceRuntimeState()
        )

        self._screenshot_state = (
            ScreenshotState()
        )

    def update_device_publish_permission(
        self,
        can_publish: bool,
    ) -> None:

        with self._device_lock:

            self._device_runtime_state = (
                DeviceRuntimeState(
                    can_publish=can_publish,
                )
            )

    def can_device_publish(
        self,
    ) -> bool:

        with self._device_lock:

            return (
                self._device_runtime_state
                .can_publish
            )

    def get_device_runtime_state(
        self,
    ) -> DeviceRuntimeState:

        with self._device_lock:

            return DeviceRuntimeState(
                can_publish=(
                    self._device_runtime_state
                    .can_publish
                ),
            )

    def update_screenshot_state(
        self,
        url: str | None,
        should_send: bool,
    ) -> None:

        with self._screenshot_lock:

            self._screenshot_state = (
                ScreenshotState(
                    url=url,
                    should_send=should_send,
                )
            )

    def get_screenshot_state(
        self,
    ) -> ScreenshotState:

        with self._screenshot_lock:

            return ScreenshotState(
                url=(
                    self._screenshot_state
                    .url
                ),
                should_send=(
                    self._screenshot_state
                    .should_send
                ),
            )

    def reset_screenshot_state(
        self,
    ) -> None:

        with self._screenshot_lock:

            self._screenshot_state = (
                ScreenshotState()
            )