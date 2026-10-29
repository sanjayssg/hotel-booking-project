from dataclasses import dataclass
from decimal import Decimal

from domain.entities import Booking, BookingStatus


@dataclass
class CancellationResult:
    booking: Booking
    refund: Decimal


class CancellationService:
    def __init__(self, bookings, policy, today, locks):
        self.bookings = bookings
        self.policy = policy
        self.today = today
        self.locks = locks

    def cancel(self, booking_id):
        with self.locks.for_key(booking_id):
            booking = self.bookings.get(booking_id)
            paid = booking.total_price if booking.status == BookingStatus.CONFIRMED else Decimal('0')
            refund = self.policy.refund(paid, booking.dates.check_in, self.today())
            booking.cancel()
            self.bookings.save(booking)
        return CancellationResult(booking, refund)
