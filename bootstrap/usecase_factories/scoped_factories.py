from application.usecase.create_order_usecase import (
    CreateOrderUseCase,
)

from application.usecase.register_device_usecase import (
    RegisterDeviceUseCase,
)

from application.usecase.send_device_online_usecase import (
    SendDeviceOnlineUseCase,
)

from domain.services.pricing_service import (
    PricingService,
)

from bootstrap.container import (
    ApplicationContainer,
)

from infrastructure.persistence.database.postgres_unit_of_work import (
    PostgresUnitOfWork,
)

from infrastructure.persistence.repositories.device.postgres_device_repository import (
    PostgresDeviceRepository,
)


def build_create_order_usecase(
    pricing_service: PricingService,
) -> CreateOrderUseCase:

    return CreateOrderUseCase(
        pricing_service=pricing_service,
    )


def build_register_device_usecase(
    container: ApplicationContainer,
) -> RegisterDeviceUseCase:

    uow = PostgresUnitOfWork(
        pool=container.pool,
    )

    device_repository = (
        PostgresDeviceRepository(
            uow=uow,
        )
    )

    return RegisterDeviceUseCase(
        uow=uow,
        state_manager=container.state_manager,
        device_repository=device_repository,
    )


def build_send_device_online_usecase(
    container: ApplicationContainer,
) -> SendDeviceOnlineUseCase:

    uow = PostgresUnitOfWork(
        pool=container.pool,
    )

    return SendDeviceOnlineUseCase(
        uow=uow,
        event_bus=container.event_bus,
    )