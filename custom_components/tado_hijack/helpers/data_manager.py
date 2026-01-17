"""Manages data fetching and caching for Tado Hijack."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

from tadoasync import Tado

if TYPE_CHECKING:
    from ..coordinator import TadoDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class TadoDataManager:
    """Handles fast/slow polling tracks and metadata caching."""

    def __init__(
        self,
        coordinator: TadoDataUpdateCoordinator,
        client: Tado,
        slow_poll_seconds: int,
    ) -> None:
        """Initialize Tado data manager."""
        self.coordinator = coordinator
        self._tado = client
        self._slow_poll_seconds = slow_poll_seconds

        # Caches
        self.zones_meta: dict[int, Any] = {}
        self.devices_meta: dict[str, Any] = {}
        self._last_slow_poll: float = 0

    async def fetch_full_update(self) -> dict[str, Any]:
        """Perform a data fetch using fast/slow track logic."""
        current_time = time.monotonic()

        # 1. SLOW TRACK: Batteries & Metadata
        if (
            not self.zones_meta
            or (current_time - self._last_slow_poll) > self._slow_poll_seconds
        ):
            _LOGGER.info("DataManager: Fetching slow-track metadata")
            zones = await self._tado.get_zones()
            devices = await self._tado.get_devices()
            self.zones_meta = {zone.id: zone for zone in zones}
            self.devices_meta = {dev.short_serial_no: dev for dev in devices}
            self._last_slow_poll = current_time

        # 2. FAST TRACK: States
        _LOGGER.debug("DataManager: Fetching fast-track states")
        home_state = await self._tado.get_home_state()
        zone_states = await self._tado.get_zone_states()

        return {
            "home_state": home_state,
            "zone_states": zone_states,
            "zones": list(self.zones_meta.values()),
            "devices": list(self.devices_meta.values()),
        }

    def invalidate_cache(self) -> None:
        """Force metadata refresh on next poll."""
        self.zones_meta = {}
