"""Core domain behavior for Pyronear Analytics."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class InvalidNameError(ValueError):
    """Raised when greeting name input is empty."""

    def __init__(self) -> None:
        """Build a specific actionable error message."""
        super().__init__("name must be non-empty after trimming whitespace.")


def build_greeting(name: str, *, include_excitement: bool = False) -> str:
    """Build a deterministic greeting string.

    Args:
        name: Name to include in the greeting.
        include_excitement: Whether to end the greeting with an exclamation mark.

    Returns:
        A greeting string such as ``"Hello, Ada."``.

    Raises:
        ValueError: If ``name`` is empty after trimming whitespace.

    Examples:
        >>> build_greeting("Ada")
        'Hello, Ada.'
        >>> build_greeting("Ada", include_excitement=True)
        'Hello, Ada!'
    """
    normalized_name = name.strip()
    if not normalized_name:
        raise InvalidNameError()

    suffix = "!" if include_excitement else "."
    message = f"Hello, {normalized_name}{suffix}"
    logger.debug(f"Generated greeting for {normalized_name}")
    return message
