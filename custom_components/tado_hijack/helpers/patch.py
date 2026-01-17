"""Monkey-patch utilities for Tado Hijack."""

from __future__ import annotations

import asyncio
import logging
import sys
from typing import Any, cast

from aiohttp import ClientResponseError
from tadoasync import Tado, TadoConnectionError
from tadoasync.const import HttpMethod
from tadoasync.tadoasync import (
    API_URL,
    EIQ_API_PATH,
    EIQ_HOST_URL,
    TADO_API_PATH,
    TADO_HOST_URL,
)
from yarl import URL

from ..const import TADO_USER_AGENT, TADO_VERSION_PATCH
from .parsers import parse_ratelimit_headers

_LOGGER = logging.getLogger(__name__)

# Global storage for hijacked headers
RATE_LIMIT_DATA: dict[str, int] = {"limit": 0, "remaining": 0}


def apply_patch() -> None:
    """Apply global library patches."""
    _LOGGER.debug("Applying tadoasync library patches...")

    _patch_version()
    _patch_zone_state()
    _patch_tado_request()

    _LOGGER.info("tadoasync: patches applied")


def _patch_version() -> None:
    """Inject missing VERSION."""
    try:
        import tadoasync.tadoasync

        tadoasync.tadoasync.VERSION = TADO_VERSION_PATCH
        if "tadoasync" in sys.modules:
            setattr(sys.modules["tadoasync"], "VERSION", TADO_VERSION_PATCH)
    except ImportError as e:
        _LOGGER.error("Failed to patch tadoasync version: %s", e)


def _patch_zone_state() -> None:
    """Fix ZoneState deserialization (nextTimeBlock null issue)."""
    try:
        import tadoasync.models

        def robust_pre_deserialize(cls: Any, d: dict[str, Any]) -> dict[str, Any]:
            if not d.get("sensorDataPoints"):
                d["sensorDataPoints"] = None
            if d.get("nextTimeBlock") is None:
                d["nextTimeBlock"] = {}
            return d

        setattr(
            tadoasync.models.ZoneState,
            "__pre_deserialize__",
            classmethod(robust_pre_deserialize),
        )
    except (ImportError, AttributeError) as e:
        _LOGGER.error("Failed to patch ZoneState model: %s", e)


def _patch_tado_request() -> None:
    """Hijack Tado._request to capture RateLimit headers."""

    async def robust_patched_request(
        self: Tado,
        uri: str | None = None,
        endpoint: str = API_URL,
        data: dict[str, object] | None = None,
        method: HttpMethod = HttpMethod.GET,
    ) -> str:
        await self._refresh_auth()

        url = URL.build(scheme="https", host=TADO_HOST_URL, path=TADO_API_PATH)
        if endpoint == EIQ_HOST_URL:
            url = URL.build(scheme="https", host=EIQ_HOST_URL, path=EIQ_API_PATH)

        if uri:
            url = url.joinpath(uri)

        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "User-Agent": TADO_USER_AGENT,
        }

        if method == HttpMethod.DELETE:
            headers["Content-Type"] = "text/plain;charset=UTF-8"
        elif method == HttpMethod.PUT:
            headers["Content-Type"] = "application/json;charset=UTF-8"
            headers["Mime-Type"] = "application/json;charset=UTF-8"

        try:
            async with asyncio.timeout(self._request_timeout):
                session = self._ensure_session()

                request_kwargs: dict[str, Any] = {
                    "method": method.value,
                    "url": str(url),
                    "headers": headers,
                }
                if method != HttpMethod.GET and data is not None:
                    request_kwargs["json"] = data

                async with session.request(**cast(Any, request_kwargs)) as response:
                    if rl := parse_ratelimit_headers(dict(response.headers)):
                        RATE_LIMIT_DATA["limit"] = rl.limit
                        RATE_LIMIT_DATA["remaining"] = rl.remaining

                    response.raise_for_status()
                    return cast(str, await response.text())
        except TimeoutError as err:
            raise TadoConnectionError("Timeout connecting to Tado") from err
        except ClientResponseError as err:
            await self.check_request_status(err)
            raise

    try:
        import tadoasync.tadoasync

        setattr(tadoasync.tadoasync.Tado, "_request", robust_patched_request)
    except (ImportError, AttributeError) as e:
        _LOGGER.error("Failed to patch Tado request: %s", e)
