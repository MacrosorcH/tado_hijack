"""Custom exceptions for Tado Hijack."""

from homeassistant.exceptions import HomeAssistantError


class TadoBridgeError(HomeAssistantError):
    """Base error for Tado Bridge."""


class TadoAuthenticationError(TadoBridgeError):
    """Error indicating auth failure."""


class TadoRateLimitError(TadoBridgeError):
    """Error indicating API rate limit hit."""


class TadoCommunicationError(TadoBridgeError):
    """Error communicating with Tado API."""
