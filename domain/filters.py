from abc import ABC, abstractmethod
from decimal import Decimal

from domain.errors import ValidationError


def number(params, name, kind):
    raw = params.get(name)
    if raw is None:
        return None
    try:
        value = kind(raw)
    except (ValueError, ArithmeticError):
        raise ValidationError(f'{name} must be a number')
    if isinstance(value, Decimal) and not value.is_finite():
        raise ValidationError(f'{name} must be a number')
    return value


class SearchFilter(ABC):
    @classmethod
    @abstractmethod
    def from_params(cls, params):
        """Build the filter from the query params, or return None if it was not asked for."""

    @abstractmethod
    def matches(self, prop, room):
        """True if this room of this property should stay in the results."""


class PriceRangeFilter(SearchFilter):
    def __init__(self, min_price=None, max_price=None):
        if min_price is not None and max_price is not None and min_price > max_price:
            raise ValidationError('min_price cannot be more than max_price')
        self.min_price = min_price
        self.max_price = max_price

    @classmethod
    def from_params(cls, params):
        low = number(params, 'min_price', Decimal)
        high = number(params, 'max_price', Decimal)
        if low is None and high is None:
            return None
        return cls(low, high)

    def matches(self, prop, room):
        if self.min_price is not None and room.base_price < self.min_price:
            return False
        if self.max_price is not None and room.base_price > self.max_price:
            return False
        return True


class AmenitiesFilter(SearchFilter):
    def __init__(self, required):
        cleaned = (name.strip().lower() for name in required)
        self.required = frozenset(name for name in cleaned if name)

    @classmethod
    def from_params(cls, params):
        raw = params.get('amenities')
        if raw is None:
            return None
        return cls(raw.split(','))

    def matches(self, prop, room):
        return self.required <= prop.amenities


class MinStarRatingFilter(SearchFilter):
    def __init__(self, stars):
        self.stars = stars

    @classmethod
    def from_params(cls, params):
        stars = number(params, 'min_stars', int)
        if stars is None:
            return None
        return cls(stars)

    def matches(self, prop, room):
        return prop.star_rating >= self.stars


FILTERS = [PriceRangeFilter, AmenitiesFilter, MinStarRatingFilter]


def build_filters(params):
    built = (filter_class.from_params(params) for filter_class in FILTERS)
    return [f for f in built if f is not None]