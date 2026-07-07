# Official Home Assistant integration for my-PV

## Introduction

The **my-PV** integration is used to integrate with the devices of [my-PV](https://www.my-pv.com/). my-PV produces functional and innovative solutions for housing technology powered by solar electricity.

We are working on bringing this integration into Home Assistant Core. Until that is done this custom integration contains all the functionality that will be in the Core integration.

We're looking forward to hear your experience with the integration, please [create an issue](https://github.com/my-PV/home-assistant-integration/issues) with your feedback and findings.

## Supported devics

The following devices are supported by this integration:
- AC ELWA 2
- AC•THOR range
- HEA•THOR IoT
- SOL•THOR

## Unsupported devices

The following devices are not supported by the integration:
- ELWA immersion heater
- WiFi Meter

## Installation

### HACS

The recommended way to install the **my-PV** Home Assistant integration is by using [HACS](https://hacs.xyz/).
Click the following button to open the integration directly on the HACS integration page.

[![Install my-PV from HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=my-PV&repository=home-assistant-integration&category=integration)

Or follow these instructions:

- Go to your **HACS** view in Home Assistant and search for *my-PV*
- Select **Download**
- Restart Home Assistant

### Manual installation

- Copy the `custom_components/my_pv` directory of this repository into the
`config/custom_components/` directory of your Home Assistant installation
- Restart Home Assistant

## Configuration

**my-PV** can be auto-discovered by Home Assistant. If an instance was found, it will be shown as Discovered. You can then set it up right away.

If it wasn’t discovered automatically, don’t worry! You can set up a manual integration entry:

- Browse to your Home Assistant instance.
- Go to [**Settings > Devices & services**](https://my.home-assistant.io/redirect/integrations).
- In the bottom right corner, select the [+ Add Integration](https://my.home-assistant.io/redirect/config_flow_start?domain=my_pv) button.
- From the list, select **my-PV**.
- Follow the instructions on screen to complete the setup.

### Login to my-PV

Host: The IP address of your my-PV device. You can find it in your router or in the device's web interface.  
Password: Password or device key of your my-PV device.

Older firmware versions of the my-PV hardware do not require a password, this will be added by upcoming firmware updates. When no custom password is set you have to use the **devicekey** which can be found under the ⓘ info menu of your my-PV device. For the HEA•THOR IoT you can find the **devicekey** on the device label.

You can update the password through the web interface of your **my-PV** device.

## Data updates

The **my-PV** integration polls data every 5 seconds.

## Supported functionality

To do...