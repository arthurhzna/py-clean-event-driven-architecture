from application.interface.persistence.unit_of_work import (
    UnitOfWork,
)

from application.state.state_manager import (
    StateManager,
)

from domain.entities.device import (
    Device,
)

from domain.interface.repositories.device_repository import (
    DeviceRepository,
)


class RegisterDeviceUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        state_manager: StateManager,
        device_repository: DeviceRepository,
    ) -> None:

        self._uow = uow

        self._state_manager = (
            state_manager
        )

        self._device_repository = (
            device_repository
        )

    def execute(
        self,
        device_id: int,
    ) -> None:

        with self._uow as uow:

            device = Device(
                device_id=device_id,
                is_registered=True,
            )

            self._device_repository.save(
                device,
            )

            uow.commit()

        self._state_manager.update_device_registration(
            True,
        )