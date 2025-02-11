"""Custom error classes for tap-jsonplaceholder."""

class TapJSONPlaceholderError(Exception):
    """Base exception for tap-jsonplaceholder."""
    pass

class MetricsCalculationError(TapJSONPlaceholderError):
    """Raised when metrics calculation fails."""
    pass

class InvalidRecordError(TapJSONPlaceholderError):
    """Raised when a record is invalid."""
    pass