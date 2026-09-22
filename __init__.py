"""OpenLinkHub integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import device_registry as dr

from .api import OpenLinkHubApi
from .const import CONF_PORT, CONF_SCAN_INTERVAL, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, PLATFORMS
from .coordinator import OpenLinkHubCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OpenLinkHub from a config entry."""
    api = OpenLinkHubApi(
        async_get_clientsession(hass),
        entry.data[CONF_HOST],
        entry.data.get(CONF_PORT, DEFAULT_PORT),
    )
    coordinator = OpenLinkHubCoordinator(
        hass,
        api,
        entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )
    await coordinator.async_config_entry_first_refresh()

    # Register controller devices before child entities. This is required
    # because child QX devices reference the System Hub as their parent.
    registry = dr.async_get(hass)
    coordinator.hub_device_ids = {}
    for serial, hub in coordinator.data["hubs"].items():
        dev = hub["device"]
        parent = registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={("openlinkhub", serial)},
            name=dev.get("product") or "OpenLinkHub",
            manufacturer=dev.get("manufacturer") or "Corsair",
            model=dev.get("product"),
            sw_version=dev.get("firmware"),
            serial_number=serial,
            configuration_url=f"http://{entry.data[CONF_HOST]}:{entry.data.get(CONF_PORT, DEFAULT_PORT)}",
        )
        coordinator.hub_device_ids[serial] = parent.id

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload OpenLinkHub."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
