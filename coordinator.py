"""Data coordinator for OpenLinkHub."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OpenLinkHubApi, OpenLinkHubApiError


class OpenLinkHubCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate OpenLinkHub polling."""

    def __init__(self, hass, api: OpenLinkHubApi, interval: int) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name="OpenLinkHub",
            update_interval=timedelta(seconds=interval),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            devices_raw, temps_raw, rgb_raw = await asyncio.gather(
                self.api.get_devices(),
                self.api.get_temperature_profiles(),
                self.api.get_rgb_data(),
            )
        except OpenLinkHubApiError as err:
            raise UpdateFailed(str(err)) from err

        hubs: dict[str, Any] = {}
        raw_devices = devices_raw.get("devices", {})
        for serial, wrapper in raw_devices.items():
            device = wrapper.get("GetDevice") or wrapper.get("device") or wrapper
            children = device.get("devices", {}) if isinstance(device, dict) else {}
            hubs[serial] = {
                "summary": wrapper,
                "device": device,
                "children": children,
            }

        profiles = temps_raw.get("data", {})
        rgb_data = rgb_raw.get("data", {})

        # Time Warp is a newer API and is not represented in the documented
        # /api/devices payload. Probe likely LINK fan channels individually.
        timewarp: dict[str, dict[int, Any]] = {}
        probes = []
        keys = []
        for serial, hub in hubs.items():
            for key, child in hub["children"].items():
                if not isinstance(child, dict):
                    continue
                channel = int(child.get("channelId", key))
                name = str(child.get("name", ""))
                # QX is known to expose native Time Warp. If a future payload
                # exposes TimewarpCapable, honor that too.
                capable = bool(child.get("TimewarpCapable")) or "QX" in name.upper()
                if capable:
                    keys.append((serial, channel))
                    probes.append(self.api.get_timewarp(serial, channel))

        if probes:
            results = await asyncio.gather(*probes, return_exceptions=True)
            for (serial, channel), result in zip(keys, results, strict=False):
                if isinstance(result, Exception):
                    continue
                if result.get("status") == 1 and isinstance(result.get("data"), dict):
                    timewarp.setdefault(serial, {})[channel] = result["data"]

        return {
            "hubs": hubs,
            "temperature_profiles": profiles,
            "rgb": rgb_data,
            "timewarp": timewarp,
        }

    async def async_command_refresh(self, coro) -> None:
        """Run a command and refresh state."""
        await coro
        await self.async_request_refresh()
