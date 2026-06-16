# pylint: disable=duplicate-code
"""Creates Button entities for the my-PV Home Assistant integration."""

import logging
from typing import Any, Final

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import MyPVConfigEntry
from .const import RESERVED_KEYS
from .entity import MyPVCommandEntity

_LOGGER = logging.getLogger(__name__)

BUTTON_DEVICE_CLASSES: Final = {"reboot_device": ButtonDeviceClass.RESTART}

ENTITY_CATEGORIES: Final = {
    "reboot_device": EntityCategory.DIAGNOSTIC,
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyPVConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the my-PV button."""
    coordinator = config_entry.runtime_data
    entities = []

    for command, configuration in coordinator.command_configurations:
        if (
            configuration.get("type")
            in [
                "any",
                "fixed",
            ]
            and command not in RESERVED_KEYS
        ):
            device_class = BUTTON_DEVICE_CLASSES.get(command)
            entity_category = ENTITY_CATEGORIES.get(command)

            entity_description = ButtonEntityDescription(
                key=command,
                device_class=device_class,
                translation_key=command,
                entity_category=entity_category,
            )
            entities.append(
                MyPVCommandButton(
                    coordinator,
                    entity_description,
                    coordinator.device.serial_number,
                )
            )

    async_add_entities(entities)


class MyPVCommandButton(MyPVCommandEntity, ButtonEntity):
    """Base my-PV Button."""

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if not self.coordinator.connected:
            self._attr_available = False
        else:
            self._attr_available = True

        self.async_write_ha_state()

    async def async_press(self, **kwargs: Any) -> None:
        """Handle the button press."""
        _LOGGER.debug("Pressing %s", self.name)

        if not self.coordinator.connected:
            self._attr_available = False
        elif await self.coordinator.send_command(self.entity_description.key):
            self._attr_available = True
        else:
            _LOGGER.error("Failed to press %s", self.name)
