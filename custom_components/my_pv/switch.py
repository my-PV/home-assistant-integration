"""Creates Switch entities for the my-PV Home Assistant integration."""

import logging
from typing import Any

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import MyPVConfigEntry
from .const import DOMAIN, RESERVED_KEYS
from .entity import MyPVSetupEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyPVConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the my-PV switch."""
    coordinator = config_entry.runtime_data
    entities = []

    for key, config in coordinator.setup_configurations:
        if config.get("type") == "boolean" and key not in RESERVED_KEYS:
            entity_description = SwitchEntityDescription(
                key=key,
                translation_key=key,
                device_class=SwitchDeviceClass.SWITCH,
            )
            entities.append(
                MyPVSwitch(
                    coordinator,
                    entity_description,
                    coordinator.device.serial_number,
                )
            )

    async_add_entities(entities)


class MyPVSwitch(MyPVSetupEntity, SwitchEntity):
    """Base my-PV Switch."""

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if not self.coordinator.connected:
            self._attr_available = False
        else:
            value = self.coordinator.get_setup_value(self.entity_description.key)
            self._attr_is_on = bool(value) if value is not None else None
            self._attr_available = value is not None

        self.async_write_ha_state()

    # @property
    # def is_on(self) -> bool | None:
    #     """Return if the switch is on."""
    #     value = self.coordinator.get_setup_value(self.entity_description.key)
    #     return bool(value) if value is not None else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        _LOGGER.debug("Turning on %s", self.name)

        if await self.coordinator.set_setup_value(self.entity_description.key, True):
            self._attr_is_on = True
            self.async_write_ha_state()
        else:
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="unknown_error"
            )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        _LOGGER.debug("Turning off %s", self.name)

        if await self.coordinator.set_setup_value(self.entity_description.key, False):
            self._attr_is_on = False
            self.async_write_ha_state()
        else:
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="unknown_error"
            )
