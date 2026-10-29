class DomainError(Exception):
    pass


class ValidationError(DomainError):
    pass


class NotFound(DomainError):
    pass


class Conflict(DomainError):
    pass


class NoInventory(Conflict):
    pass