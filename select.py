"""Select entities for OpenLinkHub."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity

from .const import TIMEWARP_DIRECTIONS, TIMEWARP_DIRECTION_VALUES
from .entity import OpenLinkHubEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    entities = []
    temp_profiles = sorted(coordinator.data.get("temperature_profiles", {}).keys())

    for serial, hub in coordinator.data["hubs"].items():
        rgb_profiles = []
        rgb = coordinator.data.get("rgb", {}).get(serial, {})
        if isinstance(rgb, dict):
            profiles = rgb.get("profiles", {})
            if isinstance(profiles, dict):
                rgb_profiles = sorted(profiles.keys())

        # Fallback: profile names commonly present in /api/color payloads may not
        # be keyed by hub serial on every OpenLinkHub version.
        if not rgb_profiles:
            names = set()
            for item in coordinator.data.get("rgb", {}).values():
                if isinstance(item, dict) and isinstance(item.get("profiles"), dict):
                    names.update(item["profiles"].keys())
            rgb_profiles = sorted(names)

        for key, child in hub["children"].items():
            channel = int(child.get("channelId", key))
            if child.get("HasSpeed") or "profile" in child:
                entities.append(SpeedProfileSelect(coordinator, serial, channel, temp_profiles))
            if "rgb" in child and rgb_profiles:
                entities.append(RgbProfileSelect(coordinator, serial, channel, rgb_profiles))
            if channel in coordinator.data.get("timewarp", {}).get(serial, {}):
                entities.append(TimeWarpDirectionSelect(coordinator, serial, channel))
                entities.append(TimeWarpSpeedSelect(coordinator, serial, channel))
    async_add_entities(entities)


class SpeedProfileSelect(OpenLinkHubEntity, SelectEntity):
    _attr_name = "Speed profile"

    def __init__(self, coordinator, serial, channel, options):
        super().__init__(coordinator, serial, channel)
        self._attr_unique_id = f"{serial}_{self.child_device_id}_speed_profile"
        self._attr_options = options

    @property
    def current_option(self):
        return self.child.get("profile")

    async def async_select_option(self, option):
        await self.coordinator.async_command_refresh(
            self.coordinator.api.set_speed_profile(self.serial, self.channel, option)
        )


class RgbProfileSelect(OpenLinkHubEntity, SelectEntity):
    _attr_name = "RGB profile"

    def __init__(self, coordinator, serial, channel, options):
        super().__init__(coordinator, serial, channel)
        self._attr_unique_id = f"{serial}_{self.child_device_id}_rgb_profile"
        self._attr_options = options

    @property
    def current_option(self):
        return self.child.get("rgb")

    async def async_select_option(self, option):
        await self.coordinator.async_command_refresh(
            self.coordinator.api.set_rgb_profile(self.serial, self.channel, option)
        )


class TimeWarpDirectionSelect(OpenLinkHubEntity, SelectEntity):
    _attr_name = "Time Warp direction"
    _attr_options = list(TIMEWARP_DIRECTION_VALUES.keys())

    def __init__(self, coordinator, serial, channel):
        super().__init__(coordinator, serial, channel)
        self._attr_unique_id = f"{serial}_{self.child_device_id}_timewarp_direction"

    @property
    def _tw(self):
        return self.coordinator.data["timewarp"][self.serial][self.channel]

    @property
    def current_option(self):
        return TIMEWARP_DIRECTIONS.get(int(self._tw.get("Direction", 1)), "Static")

    async def async_select_option(self, option):
        tw = self._tw
        color = tw.get("Color", {})
        await self.coordinator.async_command_refresh(
            self.coordinator.api.set_timewarp(
                self.serial, self.channel, bool(tw.get("Enabled")),
                {"red": int(color.get("red", 0)), "green": int(color.get("green", 255)), "blue": int(color.get("blue", 255))},
                int(tw.get("Speed", 1)), TIMEWARP_DIRECTION_VALUES[option],
            )
        )


class TimeWarpSpeedSelect(OpenLinkHubEntity, SelectEntity):
    _attr_name = "Time Warp speed"
    _attr_options = ["0", "1", "2"]

    def __init__(self, coordinator, serial, channel):
        super().__init__(coordinator, serial, channel)
        self._attr_unique_id = f"{serial}_{self.child_device_id}_timewarp_speed"

    @property
    def _tw(self):
        return self.coordinator.data["timewarp"][self.serial][self.channel]

    @property
    def current_option(self):
        return str(int(self._tw.get("Speed", 1)))

    async def async_select_option(self, option):
        tw = self._tw
        color = tw.get("Color", {})
        await self.coordinator.async_command_refresh(
            self.coordinator.api.set_timewarp(
                self.serial, self.channel, bool(tw.get("Enabled")),
                {"red": int(color.get("red", 0)), "green": int(color.get("green", 255)), "blue": int(color.get("blue", 255))},
                int(option), int(tw.get("Direction", 1)),
            )
        )
