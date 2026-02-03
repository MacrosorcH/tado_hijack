"""Logging utilities for Tado Hijack."""

from __future__ import annotations

import logging
import re
from typing import Any

# Common sensitive URL parameter patterns for Tado
_URL_PARAM_PATTERNS = [
    re.compile(r"user_code=[^& ]+", re.IGNORECASE),
    re.compile(r"access_token=[^& ]+", re.IGNORECASE),
    re.compile(r"refresh_token=[^& ]+", re.IGNORECASE),
    re.compile(r"password=[^& ]+", re.IGNORECASE),
    re.compile(r"username=[^& ]+", re.IGNORECASE),
    re.compile(r"email=[^& ]+", re.IGNORECASE),
]


def redact(data: Any) -> str:
    """Redact sensitive information from the input string or object."""
    if not isinstance(data, str):
        data = str(data)

    # URL Parameters
    for p in _URL_PARAM_PATTERNS:
        data = p.sub(lambda m: m.group(0).split("=")[0] + "=REDACTED", data)

    # Home IDs in URLs
    data = re.sub(r"homes/\d+", "homes/REDACTED", data, flags=re.IGNORECASE)

    # Serial Numbers (Tado format: 2 letters + 10 digits)
    def partial_redact_sn(m: re.Match) -> str:
        sn = m[0]
        prefix = ""
        if sn.startswith("_"):
            prefix = "_"
            sn = sn[1:]
        return f"{prefix}{sn[:2]}...{sn[-4:]}"

    data = re.sub(r"(?:\b|_|^)[A-Z]{2}\d{10}(?=\b|_|$)", partial_redact_sn, data)

    # JSON Keys and Values
    json_keys = "user_code|password|access_token|refresh_token|username|email|serialNo|shortSerialNo"
    data = re.sub(
        r'(["\'])(' + json_keys + r')\1\s*[:=]\s*(["\'])(.*?)\3',
        r"\1\2\1: \3REDACTED\3",
        data,
        flags=re.IGNORECASE,
    )

    return str(data)


_LOGGER = logging.getLogger(__name__)


class TadoRedactionFilter(logging.Filter):
    """Filter to redact sensitive information from logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Redact sensitive info in the log record message and arguments."""
        if isinstance(record.msg, str):
            record.msg = redact(record.msg)

        if record.args and isinstance(record.args, tuple):
            new_args: list[Any] | None = None
            for i, arg in enumerate(record.args):
                if not isinstance(arg, int | float | bool | type(None)):
                    if new_args is None:
                        new_args = list(record.args[:i])
                    new_args.append(redact(arg))
                elif new_args is not None:
                    new_args.append(arg)

            if new_args is not None:
                record.args = tuple(new_args)

        return True


# Global state to track desired log level for newly created loggers
_CURRENT_INTEGRATION_LOG_LEVEL: int = logging.INFO


def get_redacted_logger(name: str) -> logging.Logger:
    """Get a logger with the redaction filter attached."""
    logger = logging.getLogger(name)
    logger.addFilter(TadoRedactionFilter())
    if name.startswith("custom_components.tado_hijack"):
        logger.setLevel(_CURRENT_INTEGRATION_LOG_LEVEL)
    return logger


def set_redacted_log_level(level: str) -> None:
    """Synchronize log levels for all Tado-related loggers."""
    global _CURRENT_INTEGRATION_LOG_LEVEL
    log_level = getattr(logging, level.upper(), logging.INFO)
    _CURRENT_INTEGRATION_LOG_LEVEL = log_level

    # Update root and all existing sub-loggers
    logging.getLogger("custom_components.tado_hijack").setLevel(log_level)
    logging.getLogger("tadoasync").setLevel(log_level)

    for name in logging.root.manager.loggerDict:
        if name.startswith(("custom_components.tado_hijack", "tadoasync")):
            logging.getLogger(name).setLevel(log_level)

    _LOGGER.info("Tado Hijack log level synchronized to: %s", level.upper())
    if log_level == logging.DEBUG:
        _LOGGER.debug("Debug logging is now ACTIVE for Tado Hijack")
