# pylint: disable=duplicate-code
"""Creates Number entities for the my-PV Home Assistant integration."""

from typing import Final, override

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import MyPVConfigEntry
from .const import DOMAIN, RESERVED_KEYS
from .entity import MyPVSetupEntity


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
    """my-PV number."""

    @property
    @override
    def native_value(self) -> float | None:
        """Return the value reported by the number."""
        value = self.coordinator.device.get_setup_value(self.entity_description.key)
        return float(value) if value is not None else None

    @override
    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        if not await self.coordinator.set_setup_value(
            self.entity_description.key, value
        ):
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="unknown_error"
            )
