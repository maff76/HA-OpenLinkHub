# OpenLinkHub Home Assistant custom integration

Initial test build for OpenLinkHub, focused on iCUE LINK System Hub / QX fans.

## Install

Copy `custom_components/openlinkhub` into your Home Assistant `/config/custom_components/`
directory, then restart Home Assistant.

In Home Assistant go to:

Settings -> Devices & services -> Add integration -> OpenLinkHub

Enter the IP/hostname of the OpenLinkHub server and port (default 27003).

## Initial entities

For compatible child devices:
- Fan entity with manual 0-100% control
- RPM sensor
- Temperature sensor
- Speed profile select
- RGB profile select
- Native QX Time Warp switch
- Time Warp direction select
- Time Warp speed select

## Notes

This is a first test build. OpenLinkHub's documented API does not currently document
the newer Time Warp endpoints, so those controls are based on the working
`/api/color/getTimewarp` and `/api/color/setTimewarp` behavior verified against QX.

Time Warp colour is intentionally not exposed as a Home Assistant colour entity yet.
After the first live test we can add a dedicated colour control cleanly.

The integration polls locally every 10 seconds.


## v0.1.1
- Register the System Hub before its QX child devices.
- Use Home Assistant's current `via_device_id` relationship.
- Improve numeric-only QX device names.
