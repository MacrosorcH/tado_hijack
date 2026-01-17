"""Sensor platform for Tado Hijack."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant

from .entity import TadoHomeEntity

if TYPE_CHECKING:
    from . import TadoConfigEntry

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class TadoSensorEntityDescription(SensorEntityDescription):
    """Describes Tado sensor entity."""

    value_fn: Callable[[dict[str, Any]], int]


SENSORS: tuple[TadoSensorEntityDescription, ...] = (
    TadoSensorEntityDescription(
        key="api_limit",
        translation_key="api_limit",
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: int(getattr(data.get("rate_limit"), "limit", 0)),
    ),
    TadoSensorEntityDescription(
        key="api_remaining",
        translation_key="api_remaining",
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: int(getattr(data.get("rate_limit"), "remaining", 0)),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TadoConfigEntry,
    async_add_entities: Any,
) -> None:
    """Set up Tado sensors based on a config entry."""
    coordinator = entry.runtime_data
    async_add_entities(
        [TadoRateLimitSensor(coordinator, description) for description in SENSORS]
    )


class TadoRateLimitSensor(TadoHomeEntity, SensorEntity):
    """Sensor for Tado API Rate Limit."""

    entity_description: TadoSensorEntityDescription

    def __init__(
        self,
        coordinator: Any,
        description: TadoSensorEntityDescription,
    ) -> None:
        """Initialize Tado sensor."""
        assert description.translation_key is not None
        super().__init__(coordinator, description.translation_key)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> int:
        """Return native value."""
        try:
            return int(self.entity_description.value_fn(self.coordinator.data))
        except (TypeError, ValueError, AttributeError):
            return 0
