from application.dto.input.register_device_input import (
    RegisterDeviceInput,
)

from application.dto.output.register_device_output import (
    RegisterDeviceOutput,
)

from application.interface.persistence.unit_of_work import (
    UnitOfWork,
)

from application.result import (
    Err,
    Ok,
    Result,
)

from application.state.state_manager import (
    StateManager,
)

from domain.entities.device import (
    Device,
)

from domain.errors.device_error import (
    DeviceError,
)

from domain.ports.repositories.device_repository import (
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
        input_dto: RegisterDeviceInput,
    ) -> Result[
        RegisterDeviceOutput,
        DeviceError,
    ]:

        existing_device = (
            self._device_repository
            .get_by_id(
                input_dto.device_id,
            )
        )

        if existing_device is not None:

            return Err(
                DeviceError
                .DEVICE_ALREADY_REGISTERED,
            )

        device = Device(
            device_id=input_dto.device_id,
            is_registered=True,
        )

        with self._uow as uow:

            self._device_repository.save(
                device,
            )

            uow.commit()

        self._state_manager.update_device_publish_permission(
            True,
        )

        output = RegisterDeviceOutput(
            device_id=device.device_id,
            is_registered=(
                device.is_registered
            ),
        )

        return Ok(
            output,
        )