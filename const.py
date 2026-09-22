"""Constants for the OpenLinkHub integration."""

DOMAIN = "openlinkhub"
DEFAULT_PORT = 27003
DEFAULT_SCAN_INTERVAL = 10

CONF_PORT = "port"
CONF_SCAN_INTERVAL = "scan_interval"

PLATFORMS = ["sensor", "fan", "select", "switch", "number"]

TIMEWARP_DIRECTIONS = {
    1: "Static",
    2: "Clockwise",
    3: "Counter-clockwise",
}
TIMEWARP_DIRECTION_VALUES = {v: k for k, v in TIMEWARP_DIRECTIONS.items()}
