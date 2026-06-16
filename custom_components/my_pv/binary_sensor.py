# pylint: disable=duplicate-code
"""Creates Binary Sensor entities for the my-PV Home Assistant integration."""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import MyPVConfigEntry
from .const import RESERVED_KEYS
from .entity import MyPVDataEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyPVConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the my-PV binary sensor."""
    coordinator = config_entry.runtime_data
    entities = []

    for key, config in coordinator.data_configurations:
        if config.get("type") == "boolean" and key not in RESERVED_KEYS:
            entity_description = BinarySensorEntityDescription(
                key=key,
                translation_key=key,
            )
            entities.append(
                MyPVBinarySensor(
                    coordinator,
                    entity_description,
                    coordinator.device.serial_number,
                )
            )

    async_add_entities(entities)


class MyPVBinarySensor(MyPVDataEntity, BinarySensorEntity):
    """Base my-PV Sensor."""

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if not self.coordinator.connected:
            self._attr_available = False
        else:
            value = self.coordinator.get_data_value(self.entity_description.key)
            self._attr_is_on = bool(value) if value is not None else None
            self._attr_available = value is not None

        self.async_write_ha_state()
