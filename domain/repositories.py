from abc import ABC, abstractmethod

from domain.entities import Booking, Owner, Property
from domain.payments import Payment


class OwnerRepository(ABC):
    @abstractmethod
    def save(self, owner: Owner): ...

    @abstractmethod
    def get(self, owner_id: str):
        """Raises NotFound if there is no such owner."""


class PropertyRepository(ABC):
    @abstractmethod
    def save(self, prop: Property): ...

    @abstractmethod
    def get(self, property_id: str):
        """Raises NotFound if there is no such property."""

    @abstractmethod
    def find_by_city(self, city: str):
        """Case-insensitive match on city."""


class BookingRepository(ABC):
    @abstractmethod
    def save(self, booking: Booking): ...

    @abstractmethod
    def get(self, booking_id: str):
        """Raises NotFound if there is no such booking."""

    @abstractmethod
    def for_room_type(self, room_type_id: str):
        """Every booking for this room type, whatever its status."""


class PaymentRepository(ABC):
    @abstractmethod
    def save(self, payment: Payment): ...

    @abstractmethod
    def find_by_idempotency_key(self, key: str):
        """The payment saved with this key, or None. Does not raise."""
