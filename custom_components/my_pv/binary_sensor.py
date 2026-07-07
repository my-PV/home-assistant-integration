# pylint: disable=duplicate-code
"""Creates Binary Sensor entities for the my-PV Home Assistant integration."""

from typing import override

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import MyPVConfigEntry
from .const import RESERVED_KEYS
from .entity import MyPVDataEntity


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
    """my-PV binary sensor."""

    @property
    @override
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        value = self.coordinator.device.get_data_value(self.entity_description.key)
        return bool(value) if value is not None else None
