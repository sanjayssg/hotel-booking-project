from dataclasses import dataclass
from datetime import date, timedelta

from domain.errors import ValidationError


@dataclass(frozen=True)
class DateRange:
    check_in: date
    check_out: date

    def __post_init__(self):
        if self.check_out <= self.check_in:
            raise ValidationError('check_out must be after check_in')

    @property
    def nights(self):
        return (self.check_out - self.check_in).days

    def overlaps(self, other: 'DateRange'):
        # check-out day is free, so ranges that only touch do not overlap
        return self.check_in < other.check_out and other.check_in < self.check_out

    def each_night(self):
        for offset in range(self.nights):
            yield self.check_in + timedelta(days=offset)
