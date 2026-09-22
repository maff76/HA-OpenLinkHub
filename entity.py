"""Shared OpenLinkHub entity helpers."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


def child_name(child: dict) -> str:
    """Return a useful child device name."""
    label = str(child.get("label") or "").strip()
    model = str(child.get("name") or child.get("description") or "Device").strip()
    channel = child.get("channelId", "?")
    if label and not label.isdigit():
        return label
    if label:
        return f"{model} - {label}"
    return f"{model} - Channel {channel}"


class OpenLinkHubEntity(CoordinatorEntity):
    """Base entity for an OpenLinkHub child channel."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, serial: str, channel: int) -> None:
        super().__init__(coordinator)
        self.serial = serial
        self.channel = channel

    @property
    def hub(self):
        return self.coordinator.data["hubs"][self.serial]

    @property
    def child(self) -> dict:
        children = self.hub["children"]
        return children.get(str(self.channel)) or children.get(self.channel) or {}

    @property
    def child_device_id(self) -> str:
        return str(self.child.get("deviceId") or f"channel-{self.channel}")

    @property
    def device_info(self) -> DeviceInfo:
        hubdev = self.hub["device"]
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self.serial}:{self.child_device_id}")},
            name=child_name(self.child),
            manufacturer=hubdev.get("manufacturer", "Corsair"),
            model=self.child.get("name") or self.child.get("description"),
            via_device_id=self.coordinator.hub_device_ids[self.serial],
        )


class OpenLinkHubHubEntity(CoordinatorEntity):
    """Base entity attached to a hub."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, serial: str) -> None:
        super().__init__(coordinator)
        self.serial = serial

    @property
    def hub(self):
        return self.coordinator.data["hubs"][self.serial]

    @property
    def device_info(self) -> DeviceInfo:
        dev = self.hub["device"]
        return DeviceInfo(
            identifiers={(DOMAIN, self.serial)},
            name=dev.get("product", "OpenLinkHub"),
            manufacturer=dev.get("manufacturer", "Corsair"),
            model=dev.get("product"),
            sw_version=dev.get("firmware"),
        )
