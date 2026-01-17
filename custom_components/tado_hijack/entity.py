"""Base entity for Tado Hijack."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

if TYPE_CHECKING:
    from .coordinator import TadoDataUpdateCoordinator


class TadoEntity(CoordinatorEntity):
    """Base class for Tado Hijack entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TadoDataUpdateCoordinator,
        translation_key: str,
    ) -> None:
        """Initialize Tado entity."""
        super().__init__(coordinator)
        self._attr_translation_key = translation_key

    @property
    def tado_coordinator(self) -> TadoDataUpdateCoordinator:
        """Return the coordinator."""
        return cast("TadoDataUpdateCoordinator", self.coordinator)


class TadoHomeEntity(TadoEntity):
    """Entity belonging to the Tado Home device."""

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for the home."""
        if self.coordinator.config_entry is None:
            raise RuntimeError("Config entry not available")
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name=self.coordinator.config_entry.title,
            manufacturer="Tado",
            model="API Bridge",
            configuration_url="https://app.tado.com",
        )


class TadoZoneEntity(TadoEntity):
    """Entity belonging to a specific Tado Zone device."""

    def __init__(
        self,
        coordinator: TadoDataUpdateCoordinator,
        translation_key: str,
        zone_id: int,
        zone_name: str,
    ) -> None:
        """Initialize Tado zone entity."""
        super().__init__(coordinator, translation_key)
        self._zone_id = zone_id
        self._zone_name = zone_name

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for the zone."""
        if self.coordinator.config_entry is None:
            raise RuntimeError("Config entry not available")
        return DeviceInfo(
            identifiers={(DOMAIN, f"zone_{self._zone_id}")},
            name=self._zone_name,
            manufacturer="Tado",
            model="Heating Zone",
            via_device=(DOMAIN, self.coordinator.config_entry.entry_id),
        )
