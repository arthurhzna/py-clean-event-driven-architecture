from application.usecase.create_order_usecase import (
    CreateOrderUseCase,
)
from application.usecase.register_device_usecase import (
    RegisterDeviceUseCase,
)
from domain.interface.repositories.device_repository import (
    DeviceRepository,
)
from domain.services.pricing_service import (
    PricingService,
)
from infrastructure.bootstrap.container import (
    ApplicationContainer,
)


def build_create_order_usecase(
    pricing_service: PricingService,
) -> CreateOrderUseCase:

    return CreateOrderUseCase(
        pricing_service=pricing_service,
    )


def build_register_device_usecase(
    container: ApplicationContainer,
    device_repository: DeviceRepository,
) -> RegisterDeviceUseCase:

    return RegisterDeviceUseCase(
        datastore=container.datastore,
        state_manager=container.state_manager,
        device_repository=device_repository,
    )
