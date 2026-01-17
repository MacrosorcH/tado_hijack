"""Binary sensor platform for Tado Hijack (Battery)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import TadoZoneEntity

if TYPE_CHECKING:
    from . import TadoConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TadoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tado battery sensors."""
    coordinator = entry.runtime_data
    entities: list[TadoBatterySensor] = []

    for zone in coordinator.zones_meta.values():
        if zone.type != "HEATING":
            continue

        entities.extend(
            TadoBatterySensor(
                coordinator,
                device.device_type,
                device.short_serial_no,
                zone.id,
                zone.name,
            )
            for device in zone.devices
        )
    async_add_entities(entities)


class TadoBatterySensor(TadoZoneEntity, BinarySensorEntity):
    """Representation of a Tado device battery state."""

    _attr_device_class = BinarySensorDeviceClass.BATTERY

    def __init__(
        self, coordinator: Any, dev_id: str, serial: str, zone_id: int, zone_name: str
    ) -> None:
        """Initialize Tado battery sensor."""
        super().__init__(coordinator, "battery_state", zone_id, zone_name)
        self._dev_id = dev_id
        self._serial = serial
        self._attr_name = f"Battery ({serial})"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_bat_{serial}"

    @property
    def is_on(self) -> bool:
        """Return true if battery is low."""
        device = self.coordinator.devices_meta.get(self._serial)
        return bool(device and device.battery_state == "LOW")
