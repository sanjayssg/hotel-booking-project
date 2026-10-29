from datetime import date

from django.conf import settings

from domain.cancellation import TieredRefundPolicy
from domain.payments import CardPayment, MockGateway, UpiPayment, WalletPayment
from domain.pricing import FlatNightlyPricing
from services.booking_service import BookingService
from services.cancellation_service import CancellationService
from services.locks import KeyedLocks
from services.payment_service import PaymentService
from services.property_service import PropertyService
from services.search_service import SearchService
from store.repositories import (
    OrmBookingRepository, OrmOwnerRepository, OrmPaymentRepository, OrmPropertyRepository,
)

owners = OrmOwnerRepository()
properties = OrmPropertyRepository()
bookings = OrmBookingRepository()
pricing = FlatNightlyPricing()
refund_policy = TieredRefundPolicy()
booking_locks = KeyedLocks()
payments = OrmPaymentRepository()
gateway = MockGateway(settings.MOCK_GATEWAY_DECLINE_SUFFIX)
payment_methods = [CardPayment(), UpiPayment(), WalletPayment()]

property_service = PropertyService(owners, properties)
search_service = SearchService(properties, bookings, pricing, date.today)
booking_service = BookingService(properties, bookings, pricing, date.today)
cancellation_service = CancellationService(bookings, refund_policy, date.today, booking_locks)
payment_service = PaymentService(bookings, payments, gateway, payment_methods, booking_locks)
