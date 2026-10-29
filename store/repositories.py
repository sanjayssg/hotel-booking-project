from django.db import transaction

from domain.dates import DateRange
from domain.entities import Booking, BookingStatus, Owner, Property, RoomType
from domain.errors import NotFound
from domain.payments import Payment, PaymentStatus
from domain.repositories import (
    BookingRepository, OwnerRepository, PaymentRepository, PropertyRepository,
)
from store.models import BookingModel, OwnerModel, PaymentModel, PropertyModel, RoomTypeModel


def fetch(queryset, label, key):
    row = queryset.filter(id=key).first()
    if row is None:
        raise NotFound(f'{label} {key} not found')
    return row


def to_room_type(row):
    return RoomType(
        id=row.id, name=row.name, capacity=row.capacity,
        total_units=row.total_units, base_price=row.base_price,
    )


def to_property(row):
    return Property(
        id=row.id, owner_id=row.owner_id, name=row.name, city=row.city,
        locality=row.locality, star_rating=row.star_rating,
        amenities=frozenset(row.amenities),
        room_types=[to_room_type(r) for r in row.room_types.all()],
    )


def to_booking(row):
    return Booking(
        id=row.id, property_id=row.property_id, room_type_id=row.room_type_id,
        guests=row.guests, dates=DateRange(row.check_in, row.check_out),
        total_price=row.total_price, status=BookingStatus(row.status),
    )


def to_payment(row):
    return Payment(
        id=row.id, booking_id=row.booking_id, amount=row.amount, method=row.method,
        status=PaymentStatus(row.status), reference=row.reference,
        idempotency_key=row.idempotency_key,
    )


class OrmOwnerRepository(OwnerRepository):
    def save(self, owner: Owner):
        OwnerModel.objects.update_or_create(id=owner.id, defaults={'name': owner.name})

    def get(self, owner_id: str):
        row = fetch(OwnerModel.objects, 'owner', owner_id)
        property_ids = row.properties.values_list('id', flat=True)
        return Owner(id=row.id, name=row.name, property_ids=list(property_ids))


class OrmPropertyRepository(PropertyRepository):
    @transaction.atomic
    def save(self, prop: Property):
        PropertyModel.objects.update_or_create(id=prop.id, defaults={
            'owner_id': prop.owner_id,
            'name': prop.name,
            'city': prop.city,
            'locality': prop.locality,
            'star_rating': prop.star_rating,
            'amenities': sorted(prop.amenities),
        })
        for room in prop.room_types:
            RoomTypeModel.objects.update_or_create(id=room.id, defaults={
                'property_id': prop.id,
                'name': room.name,
                'capacity': room.capacity,
                'total_units': room.total_units,
                'base_price': room.base_price,
            })

    def get(self, property_id: str):
        rows = PropertyModel.objects.prefetch_related('room_types')
        return to_property(fetch(rows, 'property', property_id))

    def find_by_city(self, city: str):
        rows = PropertyModel.objects.prefetch_related('room_types').filter(city__iexact=city)
        return [to_property(row) for row in rows]


class OrmBookingRepository(BookingRepository):
    def save(self, booking: Booking):
        BookingModel.objects.update_or_create(id=booking.id, defaults={
            'property_id': booking.property_id,
            'room_type_id': booking.room_type_id,
            'guests': booking.guests,
            'check_in': booking.dates.check_in,
            'check_out': booking.dates.check_out,
            'total_price': booking.total_price,
            'status': booking.status.value,
        })

    def get(self, booking_id: str):
        return to_booking(fetch(BookingModel.objects, 'booking', booking_id))

    def for_room_type(self, room_type_id: str):
        rows = BookingModel.objects.filter(room_type_id=room_type_id)
        return [to_booking(row) for row in rows]


class OrmPaymentRepository(PaymentRepository):
    def save(self, payment):
        PaymentModel.objects.update_or_create(id=payment.id, defaults={
            'booking_id': payment.booking_id,
            'amount': payment.amount,
            'method': payment.method,
            'status': payment.status.value,
            'reference': payment.reference,
            'idempotency_key': payment.idempotency_key,
        })

    def find_by_idempotency_key(self, key):
        row = PaymentModel.objects.filter(idempotency_key=key).first()
        return to_payment(row) if row else None
