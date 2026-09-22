"""Number entities for OpenLinkHub."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.const import PERCENTAGE

from .entity import OpenLinkHubHubEntity


async def async_setup_entry(hass, entry, async_add_entities):
    # Reserved for hub-level controls in the next release.
    # Keeping the platform present makes expansion non-breaking.
    async_add_entities([])
