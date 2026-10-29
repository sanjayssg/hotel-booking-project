from dataclasses import dataclass
from decimal import Decimal

from domain.entities import Owner, Property, RoomType
from domain.repositories import OwnerRepository, PropertyRepository


@dataclass
class RoomTypeSpec:
    name: str
    capacity: int
    total_units: int
    base_price: Decimal


class PropertyService:
    def __init__(self, owners: OwnerRepository, properties: PropertyRepository):
        self.owners = owners
        self.properties = properties

    def register_owner(self, name: str):
        owner = Owner(name=name)
        self.owners.save(owner)
        return owner

    def add_property(self, owner_id: str, name: str, city: str, star_rating: int,
                     amenities: list[str], room_types: list[RoomTypeSpec],
                     locality: str = ''):
        owner = self.owners.get(owner_id)
        prop = Property(
            owner_id=owner.id, name=name, city=city, locality=locality,
            star_rating=star_rating, amenities=frozenset(amenities),
            room_types=[RoomType(r.name, r.capacity, r.total_units, r.base_price) for r in room_types],
        )
        self.properties.save(prop)
        return prop

    def get_property(self, property_id: str):
        return self.properties.get(property_id)