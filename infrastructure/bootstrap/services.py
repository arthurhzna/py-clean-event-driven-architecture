# infrastructure/bootstrap/services.py

from domain.services.pricing_service import (
    PricingService,
)


def build_pricing_service():

    return PricingService()
