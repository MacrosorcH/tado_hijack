"""Services for Tado Hijack."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN, SERVICE_MANUAL_POLL, SERVICE_RESUME_ALL_SCHEDULES

if TYPE_CHECKING:
    from .coordinator import TadoDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_services(
    hass: HomeAssistant, coordinator: TadoDataUpdateCoordinator
) -> None:
    """Set up the services for Tado Hijack."""

    async def handle_manual_poll(call: ServiceCall) -> None:
        """Service to force refresh."""
        _LOGGER.debug("Service call: manual_poll")
        await coordinator.async_manual_poll()

    async def handle_resume_schedules(call: ServiceCall) -> None:
        """Service to resume all schedules."""
        _LOGGER.debug("Service call: resume_all_schedules")
        await coordinator.async_resume_all_schedules()

    hass.services.async_register(DOMAIN, SERVICE_MANUAL_POLL, handle_manual_poll)
    hass.services.async_register(
        DOMAIN, SERVICE_RESUME_ALL_SCHEDULES, handle_resume_schedules
    )


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload Tado Hijack services."""
    hass.services.async_remove(DOMAIN, SERVICE_MANUAL_POLL)
    hass.services.async_remove(DOMAIN, SERVICE_RESUME_ALL_SCHEDULES)
