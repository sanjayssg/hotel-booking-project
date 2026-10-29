import re
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

from domain.entities import new_id
from domain.errors import ValidationError


class PaymentStatus(str, Enum):
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'


@dataclass
class Payment:
    booking_id: str
    amount: Decimal
    method: str
    status: PaymentStatus
    reference: str
    idempotency_key: str
    id: str = field(default_factory=new_id)


@dataclass
class GatewayResult:
    success: bool
    reference: str


def require(details, key, method):
    value = str(details.get(key, '')).strip()
    if not value:
        raise ValidationError(f'{key} is required for {method} payments')
    return value


class PaymentMethod(ABC):
    name = ''

    @abstractmethod
    def validate(self, details):
        """Raise ValidationError if these details cannot pay with this method."""


class CardPayment(PaymentMethod):
    name = 'card'

    def validate(self, details):
        number = require(details, 'card_number', self.name)
        expiry = require(details, 'expiry', self.name)
        if not re.fullmatch(r'[0-9]{12,19}', number):
            raise ValidationError('card_number must be 12 to 19 digits')
        if not re.fullmatch(r'(0[1-9]|1[0-2])/[0-9]{2}', expiry):
            raise ValidationError('expiry must look like MM/YY')


class UpiPayment(PaymentMethod):
    name = 'upi'

    def validate(self, details):
        vpa = require(details, 'vpa', self.name)
        user, at_sign, bank = vpa.partition('@')
        if not (user and at_sign and bank):
            raise ValidationError('vpa must look like name@bank')


class WalletPayment(PaymentMethod):
    name = 'wallet'

    def validate(self, details):
        require(details, 'wallet_id', self.name)


class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount, method, details):
        """Take the money. Returns a GatewayResult."""


class MockGateway(PaymentGateway):
    def __init__(self, decline_suffix):
        self.decline_suffix = decline_suffix

    def charge(self, amount, method, details):
        reference = f'mock-{uuid.uuid4().hex[:10]}'
        declined = bool(self.decline_suffix) and any(
            str(value).endswith(self.decline_suffix) for value in details.values()
        )
        return GatewayResult(success=not declined, reference=reference)
