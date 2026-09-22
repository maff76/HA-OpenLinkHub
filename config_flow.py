"""Config flow for OpenLinkHub."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OpenLinkHubApi, OpenLinkHubApiError
from .const import CONF_PORT, DEFAULT_PORT, DOMAIN


class OpenLinkHubConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle OpenLinkHub configuration."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = user_input[CONF_PORT]
            try:
                result = await OpenLinkHubApi(
                    async_get_clientsession(self.hass), host, port
                ).get_devices()
                if "devices" not in result:
                    errors["base"] = "invalid_response"
                else:
                    unique = f"{host}:{port}"
                    await self.async_set_unique_id(unique)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"OpenLinkHub ({host})",
                        data={CONF_HOST: host, CONF_PORT: port},
                    )
            except OpenLinkHubApiError:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=65535)
                    ),
                }
            ),
            errors=errors,
        )
