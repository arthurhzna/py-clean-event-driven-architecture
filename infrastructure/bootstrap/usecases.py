# infrastructure/bootstrap/usecases.py

from application.usecases import (
    CreateOrderUseCase,
)

from infrastructure.bootstrap.services import (
    build_pricing_service,
)


def build_create_order_usecase():

    pricing_service = build_pricing_service()

    return CreateOrderUseCase(
        pricing_service=pricing_service,
    )
