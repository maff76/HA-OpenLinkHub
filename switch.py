"""Switches for OpenLinkHub."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity

from .entity import OpenLinkHubEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    entities = []
    for serial, channels in coordinator.data.get("timewarp", {}).items():
        for channel in channels:
            entities.append(TimeWarpSwitch(coordinator, serial, int(channel)))
    async_add_entities(entities)


class TimeWarpSwitch(OpenLinkHubEntity, SwitchEntity):
    _attr_name = "Time Warp"

    def __init__(self, coordinator, serial, channel):
        super().__init__(coordinator, serial, channel)
        self._attr_unique_id = f"{serial}_{self.child_device_id}_timewarp"

    @property
    def _tw(self):
        return self.coordinator.data["timewarp"][self.serial][self.channel]

    @property
    def is_on(self):
        return bool(self._tw.get("Enabled"))

    async def _set(self, enabled):
        tw = self._tw
        color = tw.get("Color", {})
        await self.coordinator.async_command_refresh(
            self.coordinator.api.set_timewarp(
                self.serial, self.channel, enabled,
                {"red": int(color.get("red", 0)), "green": int(color.get("green", 255)), "blue": int(color.get("blue", 255))},
                int(tw.get("Speed", 1)), int(tw.get("Direction", 1)),
            )
        )

    async def async_turn_on(self, **kwargs):
        await self._set(True)

    async def async_turn_off(self, **kwargs):
        await self._set(False)
