from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from uuid import uuid4

from domain.dates import DateRange
from domain.errors import Conflict, ValidationError


def new_id():
    return uuid4().hex


def require_text(value: str, label: str):
    if not value or not value.strip():
        raise ValidationError(f'{label} cannot be blank')


@dataclass
class RoomType:
    name: str
    capacity: int
    total_units: int
    base_price: Decimal
    id: str = field(default_factory=new_id)

    def __post_init__(self):
        require_text(self.name, 'room type name')
        if self.capacity < 1:
            raise ValidationError('capacity must be at least 1')
        if self.total_units < 1:
            raise ValidationError('total_units must be at least 1')
        if self.base_price <= 0:
            raise ValidationError('base_price must be more than 0')


@dataclass
class Property:
    owner_id: str
    name: str
    city: str
    star_rating: int
    amenities: frozenset[str]
    room_types: list[RoomType]
    locality: str = ''
    id: str = field(default_factory=new_id)

    def __post_init__(self):
        require_text(self.name, 'property name')
        require_text(self.city, 'city')
        if not 1 <= self.star_rating <= 5:
            raise ValidationError('star_rating must be between 1 and 5')
        if not self.room_types:
            raise ValidationError('a property needs at least one room type')
        self.amenities = frozenset(a.strip().lower() for a in self.amenities)


@dataclass
class Owner:
    name: str
    property_ids: list[str] = field(default_factory=list)
    id: str = field(default_factory=new_id)

    def __post_init__(self):
        require_text(self.name, 'owner name')

    def add_property(self, property_id: str):
        self.property_ids.append(property_id)


class BookingStatus(str, Enum):
    PENDING_PAYMENT = 'PENDING_PAYMENT'
    CONFIRMED = 'CONFIRMED'
    CANCELLED = 'CANCELLED'
    PAYMENT_FAILED = 'PAYMENT_FAILED'


ALLOWED_MOVES = {
    BookingStatus.PENDING_PAYMENT: {
        BookingStatus.CONFIRMED, BookingStatus.PAYMENT_FAILED, BookingStatus.CANCELLED,
    },
    BookingStatus.CONFIRMED: {BookingStatus.CANCELLED},
    BookingStatus.CANCELLED: set(),
    BookingStatus.PAYMENT_FAILED: set(),
}


@dataclass
class Booking:
    property_id: str
    room_type_id: str
    guests: int
    dates: DateRange
    total_price: Decimal
    status: BookingStatus = BookingStatus.PENDING_PAYMENT
    id: str = field(default_factory=new_id)

    def __post_init__(self):
        if self.guests < 1:
            raise ValidationError('guests must be at least 1')
        if self.total_price < 0:
            raise ValidationError('total_price cannot be negative')

    @property
    def holds_inventory(self):
        return self.status in (BookingStatus.PENDING_PAYMENT, BookingStatus.CONFIRMED)

    def confirm(self):
        self._move_to(BookingStatus.CONFIRMED)

    def fail_payment(self):
        self._move_to(BookingStatus.PAYMENT_FAILED)

    def cancel(self):
        self._move_to(BookingStatus.CANCELLED)

    def _move_to(self, new_status: BookingStatus):
        if new_status not in ALLOWED_MOVES[self.status]:
            raise Conflict(f'cannot move booking from {self.status.value} to {new_status.value}')
        self.status = new_status