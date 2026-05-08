class PricingService:
    def calculate_total(
        self,
        items: list[dict],
    ) -> float:

        total = 0

        for item in items:
            total += item["price"] * item["qty"]

        return total
