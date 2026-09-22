"""Small asynchronous client for the OpenLinkHub HTTP API."""

from __future__ import annotations

import asyncio
from typing import Any

from aiohttp import ClientError, ClientSession, ClientTimeout


class OpenLinkHubApiError(Exception):
    """Base API error."""


class OpenLinkHubConnectionError(OpenLinkHubApiError):
    """Raised when OpenLinkHub cannot be reached."""


class OpenLinkHubResponseError(OpenLinkHubApiError):
    """Raised for an invalid OpenLinkHub response."""


class OpenLinkHubApi:
    """OpenLinkHub API client."""

    def __init__(self, session: ClientSession, host: str, port: int) -> None:
        self._session = session
        self._base_url = f"http://{host}:{port}"

    async def _request(
        self, method: str, path: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        try:
            async with asyncio.timeout(10):
                async with self._session.request(
                    method,
                    f"{self._base_url}{path}",
                    json=payload,
                    timeout=ClientTimeout(total=10),
                ) as response:
                    response.raise_for_status()
                    data = await response.json(content_type=None)
        except (TimeoutError, ClientError, ValueError) as err:
            raise OpenLinkHubConnectionError(str(err)) from err

        if not isinstance(data, dict):
            raise OpenLinkHubResponseError("OpenLinkHub returned a non-object response")
        return data

    async def get_devices(self) -> dict[str, Any]:
        return await self._request("GET", "/api/devices/")

    async def get_rgb_data(self) -> dict[str, Any]:
        return await self._request("GET", "/api/color/")

    async def get_temperature_profiles(self) -> dict[str, Any]:
        return await self._request("GET", "/api/temperatures/")

    async def set_speed_profile(self, serial: str, channel: int, profile: str) -> None:
        await self._request(
            "POST", "/api/speed",
            {"deviceId": serial, "channelId": channel, "profile": profile},
        )

    async def set_manual_speed(self, serial: str, channel: int, value: int) -> None:
        await self._request(
            "POST", "/api/speed/manual",
            {"deviceId": serial, "channelId": channel, "value": value},
        )

    async def set_rgb_profile(self, serial: str, channel: int, profile: str) -> None:
        await self._request(
            "POST", "/api/color",
            {"deviceId": serial, "channelId": channel, "profile": profile},
        )

    async def get_timewarp(self, serial: str, channel: int) -> dict[str, Any]:
        return await self._request(
            "POST", "/api/color/getTimewarp",
            {"deviceId": serial, "channelId": channel, "subDeviceId": 0},
        )

    async def set_timewarp(
        self,
        serial: str,
        channel: int,
        enabled: bool,
        color: dict[str, int],
        speed: int,
        direction: int,
    ) -> None:
        await self._request(
            "POST", "/api/color/setTimewarp",
            {
                "deviceId": serial,
                "channelId": channel,
                "enabled": enabled,
                "startColor": color,
                "speed": speed,
                "direction": direction,
            },
        )
