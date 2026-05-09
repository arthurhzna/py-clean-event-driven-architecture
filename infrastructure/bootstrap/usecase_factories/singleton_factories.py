from application.usecase.create_order_usecase import (
    CreateOrderUseCase,
)

from domain.services.pricing_service import (
    PricingService,
)

def build_create_order_usecase(
    pricing_service: PricingService,
) -> CreateOrderUseCase:

    return CreateOrderUseCase(
        pricing_service=pricing_service,
    )