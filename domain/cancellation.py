from abc import ABC, abstractmethod
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal('0.01')


class CancellationPolicy(ABC):
    @abstractmethod
    def refund(self, paid, check_in, today):
        """How much of what the guest paid goes back to them."""


class TieredRefundPolicy(CancellationPolicy):
    # (days before check-in, share refunded), checked from the most generous down
    TIERS = ((7, Decimal('1.00')), (2, Decimal('0.50')))

    def refund(self, paid, check_in, today):
        days_left = (check_in - today).days
        for min_days, share in self.TIERS:
            if days_left >= min_days:
                return (paid * share).quantize(CENT, rounding=ROUND_HALF_UP)
        return Decimal('0.00')
