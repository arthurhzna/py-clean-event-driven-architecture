from application.interface.persistence.datastore import (
    DataStore,
)
from application.state.state_manager import (
    StateManager,
)
from domain.entities.device import (
    Device,
)
from domain.interface.persistence.tx import (
    Tx,
)
from domain.interface.repositories.device_repository import (
    DeviceRepository,
)


class RegisterDeviceUseCase:
    def __init__(
        self,
        datastore: DataStore,
        state_manager: StateManager,
        device_repository: DeviceRepository,
    ) -> None:

        self._datastore = datastore

        self._state_manager = state_manager

        self._device_repository = device_repository

    def execute(
        self,
        device_id: int,
    ) -> None:

        def operation(
            tx: Tx,
        ) -> None:

            self._state_manager.update_device_registration(
                True,
            )

            device = Device(
                device_id=device_id,
                is_registered=True,
            )

            self._device_repository.save(
                tx,
                device,
            )

        self._datastore.atomic(
            operation,
        )
