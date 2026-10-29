from abc import ABC, abstractmethod
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal('0.01')
FRIDAY, SATURDAY = 4, 5


class PricingStrategy(ABC):
    @abstractmethod
    def quote(self, room, dates):
        """Total price for the whole stay."""


class FlatNightlyPricing(PricingStrategy):
    def quote(self, room, dates):
        return room.base_price * dates.nights


class WeekendSurchargePricing(PricingStrategy):
    def __init__(self, surcharge_pct):
        self.weekend_rate = 1 + Decimal(surcharge_pct) / 100

    def quote(self, room, dates):
        total = sum((self._night_price(room, night) for night in dates.each_night()), Decimal('0'))
        return total.quantize(CENT, rounding=ROUND_HALF_UP)

    def _night_price(self, room, night):
        if night.weekday() in (FRIDAY, SATURDAY):
            return room.base_price * self.weekend_rate
        return room.base_price
