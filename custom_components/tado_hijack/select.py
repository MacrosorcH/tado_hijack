"""Select platform for Tado Hijack."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import TadoGenericEntityMixin, TadoZoneEntity
from .helpers.entity_setup import async_setup_generic_platform
from .helpers.logging_utils import get_redacted_logger
from .models import TadoEntityDefinition

if TYPE_CHECKING:
    from . import TadoConfigEntry
    from .coordinator import TadoDataUpdateCoordinator

_LOGGER = get_redacted_logger(__name__)


async def async_setup_entry(
    hass: Any,
    entry: TadoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tado select entities based on a config entry."""
    await async_setup_generic_platform(
        hass,
        entry,
        async_add_entities,
        "select",
        {
            "zone": TadoGenericZoneSelect,
        },
    )


class TadoGenericZoneSelect(TadoZoneEntity, TadoGenericEntityMixin, SelectEntity):
    """Generic select for Zone scope."""

    def __init__(
        self,
        coordinator: TadoDataUpdateCoordinator,
        definition: TadoEntityDefinition,
        zone_id: int,
        zone_name: str,
    ) -> None:
        """Initialize the generic zone select."""
        TadoZoneEntity.__init__(
            self,
            coordinator,
            cast(str, definition["translation_key"]),
            zone_id,
            zone_name,
        )
        TadoGenericEntityMixin.__init__(self, definition)
        self._attr_options: list[str] = []
        self._option_map: dict[str, str] = {}
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{self._get_unique_id_suffix()}_{zone_id}"

    async def async_added_to_hass(self) -> None:
        """Fetch options on startup."""
        await super().async_added_to_hass()
        if options_fn := self._definition.get("options_fn"):
            # Ensure capabilities are loaded
            await self.coordinator.async_get_capabilities(self._zone_id)
            if source_options := options_fn(self.coordinator, self._zone_id):
                self._option_map = {opt.lower(): opt for opt in source_options}
                self._attr_options = sorted(self._option_map.keys())
                self.async_write_ha_state()

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        val = self._get_actual_value()
        if val is not None:
            val_lower = str(val).lower()
            if val_lower in self._attr_options:
                return val_lower
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        api_value = self._option_map.get(option)
        if api_value is None:
            _LOGGER.error("Invalid option selected: %s", option)
            return

        await self._async_select_option(api_value)
        self.async_write_ha_state()
