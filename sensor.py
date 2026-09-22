"""Sensors for OpenLinkHub."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import REVOLUTIONS_PER_MINUTE, UnitOfTemperature

from .entity import OpenLinkHubEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    entities = []
    for serial, hub in coordinator.data["hubs"].items():
        for key, child in hub["children"].items():
            channel = int(child.get("channelId", key))
            if child.get("HasSpeed") or "rpm" in child:
                entities.append(OpenLinkHubRpmSensor(coordinator, serial, channel))
            if child.get("HasTemps") or child.get("IsTemperatureProbe") or "temperature" in child:
                entities.append(OpenLinkHubTemperatureSensor(coordinator, serial, channel))
    async_add_entities(entities)


class OpenLinkHubRpmSensor(OpenLinkHubEntity, SensorEntity):
    _attr_name = "Speed"
    _attr_native_unit_of_measurement = REVOLUTIONS_PER_MINUTE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, serial, channel):
        super().__init__(coordinator, serial, channel)
        self._attr_unique_id = f"{serial}_{self.child_device_id}_rpm"

    @property
    def native_value(self):
        return self.child.get("rpm")


class OpenLinkHubTemperatureSensor(OpenLinkHubEntity, SensorEntity):
    _attr_name = "Temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, serial, channel):
        super().__init__(coordinator, serial, channel)
        self._attr_unique_id = f"{serial}_{self.child_device_id}_temperature"

    @property
    def native_value(self):
        return self.child.get("temperature")
