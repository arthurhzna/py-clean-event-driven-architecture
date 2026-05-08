# application/usecases/create_order_usecase.py

from domain.services.pricing_service import (
    PricingService,
)


class CreateOrderUseCase:
    def __init__(
        self,
        pricing_service: PricingService,
    ):
        self.pricing_service = pricing_service

    def execute(
        self,
        items: list[dict],
    ):

        total = self.pricing_service.calculate_total(items)

        return {
            "total": total,
        }
