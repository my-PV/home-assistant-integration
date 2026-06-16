# pylint: disable=duplicate-code
"""Creates Number entities for the my-PV Home Assistant integration."""

import logging
from typing import Final

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import MyPVConfigEntry
from .const import RESERVED_KEYS
from .entity import MyPVSetupEntity

_LOGGER = logging.getLogger(__name__)


DEVICE_CLASSES: Final = {
    "ww_boost_h": NumberDeviceClass.TEMPERATURE,
    "ww_targ_h": NumberDeviceClass.TEMPERATURE,
    "ww1boost": NumberDeviceClass.TEMPERATURE,
    "ww1target": NumberDeviceClass.TEMPERATURE,
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyPVConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the my-PV number."""
    coordinator = config_entry.runtime_data
    entities = []

    for key, config in coordinator.setup_configurations:
        if config.get("type") == "number" and key not in RESERVED_KEYS:
            device_class = DEVICE_CLASSES.get(key)
            entity_description = NumberEntityDescription(
                key=key,
                translation_key=key,
                device_class=device_class,
                native_unit_of_measurement=config.get("unit"),
                native_min_value=config.get("min", 0),
                native_max_value=config.get("max"),
                native_step=config.get("step"),
            )
            entities.append(
                MyPVNumber(
                    coordinator,
                    entity_description,
                    coordinator.device.serial_number,
                )
            )

    async_add_entities(entities)


class MyPVNumber(MyPVSetupEntity, NumberEntity):
    """Base my-PV Number."""

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if not self.coordinator.connected:
            self._attr_available = False
        else:
            value = self.coordinator.get_setup_value(self.entity_description.key)
            self._attr_native_value = float(value) if value is not None else None
            self._attr_available = value is not None

        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        _LOGGER.debug("Setting %s", self.name)

        if not self.coordinator.connected:
            self._attr_available = False
        elif await self.coordinator.set_setup_value(self.entity_description.key, value):
            self._attr_available = True
            self._attr_native_value = value
        else:
            _LOGGER.error("Failed to set %s", self.name)
