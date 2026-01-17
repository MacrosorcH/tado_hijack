"""Switch platform for Tado Hijack."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import PROTECTION_MODE_TEMP
from .entity import TadoHomeEntity, TadoZoneEntity

if TYPE_CHECKING:
    from . import TadoConfigEntry
    from .coordinator import TadoDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: Any,
    entry: TadoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tado switches based on a config entry."""
    coordinator: TadoDataUpdateCoordinator = entry.runtime_data
    entities: list[SwitchEntity] = [TadoAwaySwitch(coordinator)]

    # Per-Zone Schedule Switches -> Zone Devices
    entities.extend(
        TadoZoneScheduleSwitch(coordinator, zone.id, zone.name)
        for zone in coordinator.zones_meta.values()
        if zone.type == "HEATING"
    )
    async_add_entities(entities)


class TadoAwaySwitch(TadoHomeEntity, SwitchEntity):
    """Switch for Tado Home/Away control."""

    def __init__(self, coordinator: Any) -> None:
        """Initialize Tado away switch."""
        super().__init__(coordinator, "away_mode")
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_away_mode"

    @property
    def is_on(self) -> bool:
        """Return true if in AWAY mode with optimistic fallback."""
        if (
            self.tado_coordinator.optimistic_presence is not None
            and (time.monotonic() - self.tado_coordinator.optimistic_time) < 30
        ):
            return self.tado_coordinator.optimistic_presence == "AWAY"

        home_state = self.tado_coordinator.data.get("home_state")
        if home_state is None:
            return False
        return str(getattr(home_state, "presence", "")) == "AWAY"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn AWAY mode ON."""
        await self.tado_coordinator.async_set_presence_debounced("AWAY")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn AWAY mode OFF (Go HOME)."""
        await self.tado_coordinator.async_set_presence_debounced("HOME")


class TadoZoneScheduleSwitch(TadoZoneEntity, SwitchEntity):
    """Switch to toggle between Smart Schedule and Manual Overlay."""

    def __init__(self, coordinator: Any, zone_id: int, zone_name: str) -> None:
        """Initialize Tado zone schedule switch."""
        super().__init__(coordinator, "auto_mode", zone_id, zone_name)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_sch_{zone_id}"

    @property
    def is_on(self) -> bool:
        """Return true if Smart Schedule is active."""
        opt = self.tado_coordinator.optimistic_zones.get(self._zone_id)
        if opt and (time.monotonic() - opt["time"]) < 30:
            return not bool(opt.get("overlay", False))

        state = self.tado_coordinator.data.get("zone_states", {}).get(
            str(self._zone_id)
        )
        return not bool(getattr(state, "overlay_active", False))

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Resume smart schedule."""
        await self.tado_coordinator.async_set_zone_auto(self._zone_id)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Force manual overlay (Protection mode)."""
        await self.tado_coordinator.async_set_zone_heat(
            self._zone_id, temp=PROTECTION_MODE_TEMP
        )
