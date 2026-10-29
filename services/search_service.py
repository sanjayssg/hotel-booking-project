from dataclasses import dataclass
from decimal import Decimal

from domain.errors import ValidationError
from services.availability import units_free


@dataclass
class SearchResult:
    property_id: str
    name: str
    city: str
    star_rating: int
    room_type_id: str
    room_type: str
    units_free: int
    price_per_night: Decimal
    total_price: Decimal


class SearchService:
    def __init__(self, properties, bookings, pricing, today):
        self.properties = properties
        self.bookings = bookings
        self.pricing = pricing
        self.today = today

    def search(self, city, dates, guests, filters=(), locality=''):
        self._check_request(city, dates, guests)
        results = []
        for prop in self.properties.find_by_city(city):
            if locality and prop.locality.lower() != locality.lower():
                continue
            for room in prop.room_types:
                if room.capacity < guests:
                    continue
                if not all(f.matches(prop, room) for f in filters):
                    continue
                free = units_free(room, dates, self.bookings)
                if free > 0:
                    results.append(self._result(prop, room, dates, free))
        return results

    def _check_request(self, city, dates, guests):
        if not city.strip():
            raise ValidationError('city is required')
        if guests < 1:
            raise ValidationError('guests must be at least 1')
        if dates.check_in < self.today():
            raise ValidationError('check_in cannot be in the past')

    def _result(self, prop, room, dates, free):
        return SearchResult(
            property_id=prop.id, name=prop.name, city=prop.city,
            star_rating=prop.star_rating, room_type_id=room.id, room_type=room.name,
            units_free=free, price_per_night=room.base_price,
            total_price=self.pricing.quote(room, dates),
        )