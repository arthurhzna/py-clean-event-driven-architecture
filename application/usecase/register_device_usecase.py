from application.state.state_manager import (
    StateManager,
)
from domain.interface.repositories.device_repository import (
    DeviceRepository,
)


class RegisterDeviceUseCase:
    def __init__(
        self,
        state_manager: StateManager,
        device_repository: DeviceRepository,
    ):

        self.state_manager = state_manager

        self.device_repository = device_repository

    def execute(
        self,
        device_id: int,
    ) -> None:

        self.state_manager.update_device_registration(True)

        self.device_repository.save(device_id)
