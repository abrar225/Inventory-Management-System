"""Shared domain exceptions.

Services raise these domain-specific exceptions; views translate them into
user-facing responses (inline errors, toasts, or error pages). This keeps
business rules expressed in the service layer rather than as ad-hoc HTTP
handling scattered through views.
"""


class DomainError(Exception):
    """Base class for all domain-level errors."""


class PermissionDeniedError(DomainError):
    """Raised when a user attempts an action they are not authorized for."""


class InactiveUserError(DomainError):
    """Raised when an inactive user attempts to authenticate."""


class ValidationError(DomainError):
    """Raised when a service-layer business rule is violated."""


# --- Inventory / catalog errors (used from Phase 4 onward) -----------------
class InsufficientStockError(DomainError):
    """Raised when a sale or adjustment would drive stock below zero."""


class DuplicateSKUError(DomainError):
    """Raised when creating a product with an already-used SKU."""


class InvalidPriceError(DomainError):
    """Raised when selling price is below purchase price."""


class InvalidPurchaseError(DomainError):
    """Raised when a purchase violates its business rules."""


class InvalidSaleError(DomainError):
    """Raised when a sale violates its business rules."""
