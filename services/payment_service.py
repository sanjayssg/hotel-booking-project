from dataclasses import dataclass

from domain.entities import Booking, BookingStatus
from domain.errors import Conflict, ValidationError
from domain.payments import Payment, PaymentStatus


@dataclass
class PaymentResult:
    payment: Payment
    booking: Booking


class PaymentService:
    def __init__(self, bookings, payments, gateway, methods, locks):
        self.bookings = bookings
        self.payments = payments
        self.gateway = gateway
        self.methods = {method.name: method for method in methods}
        self.locks = locks

    def pay(self, booking_id, method_name, details, idempotency_key):
        if not idempotency_key.strip():
            raise ValidationError('idempotency_key is required')
        method = self._method(method_name)
        method.validate(details)

        with self.locks.for_key(booking_id):
            replay = self._replay(booking_id, idempotency_key)
            if replay:
                return replay

            booking = self.bookings.get(booking_id)
            if booking.status != BookingStatus.PENDING_PAYMENT:
                raise Conflict(
                    f'booking is {booking.status.value}, only a PENDING_PAYMENT booking can be paid')

            result = self.gateway.charge(booking.total_price, method.name, details)
            payment = Payment(
                booking_id=booking.id, amount=booking.total_price, method=method.name,
                status=PaymentStatus.SUCCESS if result.success else PaymentStatus.FAILED,
                reference=result.reference, idempotency_key=idempotency_key,
            )
            if result.success:
                booking.confirm()
            else:
                booking.fail_payment()
            self.payments.save(payment)
            self.bookings.save(booking)
        return PaymentResult(payment, booking)

    def _method(self, name):
        if name not in self.methods:
            supported = ', '.join(self.methods)
            raise ValidationError(f"unsupported payment method '{name}', use one of: {supported}")
        return self.methods[name]

    def _replay(self, booking_id, idempotency_key):
        stored = self.payments.find_by_idempotency_key(idempotency_key)
        if stored is None:
            return None
        if stored.booking_id != booking_id:
            raise Conflict('idempotency_key was already used for another booking')
        return PaymentResult(stored, self.bookings.get(booking_id))
