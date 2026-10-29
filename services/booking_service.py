from domain.entities import Booking
from domain.errors import NoInventory, NotFound, ValidationError
from services.availability import units_free
from services.locks import KeyedLocks


class BookingService:
    def __init__(self, properties, bookings, pricing, today):
        self.properties = properties
        self.bookings = bookings
        self.pricing = pricing
        self.today = today
        self._room_locks = KeyedLocks()

    def book(self, property_id, room_type_id, dates, guests):
        if dates.check_in < self.today():
            raise ValidationError('check_in cannot be in the past')
        room = self._find_room(property_id, room_type_id)
        if guests > room.capacity:
            raise ValidationError(f'{room.name} sleeps at most {room.capacity} guests')

        with self._room_locks.for_key(room.id):
            if units_free(room, dates, self.bookings) < 1:
                raise NoInventory(f'no {room.name} room is free for those dates')
            booking = Booking(
                property_id=property_id, room_type_id=room.id, guests=guests,
                dates=dates, total_price=self.pricing.quote(room, dates),
            )
            self.bookings.save(booking)
        return booking

    def get_booking(self, booking_id):
        return self.bookings.get(booking_id)

    def _find_room(self, property_id, room_type_id):
        prop = self.properties.get(property_id)
        for room in prop.room_types:
            if room.id == room_type_id:
                return room
        raise NotFound(f'room type {room_type_id} not found in property {property_id}')
