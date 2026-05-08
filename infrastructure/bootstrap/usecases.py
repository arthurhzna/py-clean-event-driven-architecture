# infrastructure/bootstrap/usecases.py

from application.usecase.create_order_usecase import (
    CreateOrderUseCase,
)
from application.usecase.mark_person_disappeared_usecase import (
    MarkPersonDisappearedUseCase,
)
from application.usecase.register_device_usecase import (
    RegisterDeviceUseCase,
)
from application.state.state_manager import (
    StateManager,
)

from infrastructure.bootstrap.services import (
    build_device_repository,
    build_person_repository,
    build_pricing_service,
    build_state_manager,
)


def build_create_order_usecase():

    pricing_service = build_pricing_service()

    return CreateOrderUseCase(
        pricing_service=pricing_service,
    )


def build_mark_person_disappeared_usecase():

    person_repository = build_person_repository()

    return MarkPersonDisappearedUseCase(
        PersonRepository=person_repository,
    )


def build_register_device_usecase(
    state_manager: StateManager | None = None,
):

    sm = state_manager or build_state_manager()
    device_repository = build_device_repository()

    return RegisterDeviceUseCase(
        state_manager=sm,
        device_repository=device_repository,
    )