"""Fan entities for OpenLinkHub."""

from __future__ import annotations

from homeassistant.components.fan import FanEntity, FanEntityFeature

from .entity import OpenLinkHubEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    entities = []
    for serial, hub in coordinator.data["hubs"].items():
        for key, child in hub["children"].items():
            if not child.get("HasSpeed") and "rpm" not in child:
                continue
            channel = int(child.get("channelId", key))
            entities.append(OpenLinkHubFan(coordinator, serial, channel))
    async_add_entities(entities)


class OpenLinkHubFan(OpenLinkHubEntity, FanEntity):
    _attr_name = None
    _attr_supported_features = FanEntityFeature.SET_SPEED
    _attr_speed_count = 100

    def __init__(self, coordinator, serial, channel):
        super().__init__(coordinator, serial, channel)
        self._attr_unique_id = f"{serial}_{self.child_device_id}_fan"
        self._percentage = None

    @property
    def is_on(self):
        rpm = self.child.get("rpm")
        return bool(rpm and rpm > 0)

    @property
    def percentage(self):
        return self._percentage

    async def async_set_percentage(self, percentage: int) -> None:
        self._percentage = percentage
        await self.coordinator.async_command_refresh(
            self.coordinator.api.set_manual_speed(self.serial, self.channel, percentage)
        )

    async def async_turn_on(self, percentage=None, **kwargs):
        await self.async_set_percentage(percentage or self._percentage or 50)

    async def async_turn_off(self, **kwargs):
        await self.async_set_percentage(0)
