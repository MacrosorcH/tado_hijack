"""Helper for setting up Tado generic entities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from ..const import (
    ZONE_TYPE_AIR_CONDITIONING,
    ZONE_TYPE_HEATING,
    ZONE_TYPE_HOT_WATER,
)
from ..definitions import ENTITY_DEFINITIONS
from .discovery import yield_devices, yield_zones
from .logging_utils import get_redacted_logger

if TYPE_CHECKING:
    from .. import TadoConfigEntry
    from ..coordinator import TadoDataUpdateCoordinator
    from ..models import TadoEntityDefinition

_LOGGER = get_redacted_logger(__name__)

# Default supported zone types if not specified
ALL_ZONE_TYPES = {
    ZONE_TYPE_HEATING,
    ZONE_TYPE_AIR_CONDITIONING,
    ZONE_TYPE_HOT_WATER,
}


async def async_setup_generic_platform(
    hass: HomeAssistant,
    entry: TadoConfigEntry,
    async_add_entities: AddEntitiesCallback,
    platform: str,
    entity_classes: dict[str, Any],  # scope -> class
) -> None:
    """Set up generic Tado entities for a specific platform."""
    coordinator: TadoDataUpdateCoordinator = entry.runtime_data
    entities: list[Any] = []

    for d in ENTITY_DEFINITIONS:
        if d["platform"] != platform:
            continue

        scope = d["scope"]
        cls = entity_classes.get(scope)
        if not cls:
            continue

        if scope == "home":
            _process_home_scope(coordinator, d, cls, entities)
        elif scope == "zone":
            _process_zone_scope(coordinator, d, cls, entities)
        elif scope == "device":
            _process_device_scope(coordinator, d, cls, entities)
        elif scope == "bridge":
            _process_bridge_scope(coordinator, d, cls, entities)

    if entities:
        _LOGGER.debug(
            "Adding %d entities for platform %s: %s",
            len(entities),
            platform,
            [e.unique_id for e in entities],
        )
        async_add_entities(entities)


def _process_home_scope(
    coordinator: TadoDataUpdateCoordinator,
    definition: TadoEntityDefinition,
    cls: Any,
    entities: list[Any],
) -> None:
    """Process entities with Home scope."""
    if (is_supported := definition.get("is_supported_fn")) and not is_supported(
        coordinator
    ):
        return
    entities.append(cls(coordinator, definition))


def _process_zone_scope(
    coordinator: TadoDataUpdateCoordinator,
    definition: TadoEntityDefinition,
    cls: Any,
    entities: list[Any],
) -> None:
    """Process entities with Zone scope."""
    supported_types = definition.get("supported_zone_types") or ALL_ZONE_TYPES
    for zone in yield_zones(coordinator, supported_types):
        if (is_supported := definition.get("is_supported_fn")) and not is_supported(
            coordinator, zone.id
        ):
            continue
        entities.append(cls(coordinator, definition, zone.id, zone.name))


def _process_device_scope(
    coordinator: TadoDataUpdateCoordinator,
    definition: TadoEntityDefinition,
    cls: Any,
    entities: list[Any],
) -> None:
    """Process entities with Device scope."""
    required_caps = definition.get("required_device_capabilities")
    caps_args = required_caps or []

    # Process devices across all zone types
    for device, zone_id in yield_devices(coordinator, ALL_ZONE_TYPES, *caps_args):
        if (is_supported := definition.get("is_supported_fn")) and not is_supported(
            coordinator, device.serial_no
        ):
            continue
        entities.append(cls(coordinator, definition, device, zone_id))


def _process_bridge_scope(
    coordinator: TadoDataUpdateCoordinator,
    definition: TadoEntityDefinition,
    cls: Any,
    entities: list[Any],
) -> None:
    """Process entities with Bridge scope."""
    for bridge in coordinator.bridges:
        if (is_supported := definition.get("is_supported_fn")) and not is_supported(
            coordinator, bridge.serial_no
        ):
            continue
        entities.append(cls(coordinator, definition, bridge))
