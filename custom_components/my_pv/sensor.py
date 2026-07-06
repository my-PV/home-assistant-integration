"""Creates Sensor entities for the my-PV Home Assistant integration."""

from typing import Final, override

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import MyPVConfigEntry
from .const import RESERVED_KEYS
from .entity import MyPVDataEntity

DEVICE_CLASSES: Final = {
    "curr_l2": SensorDeviceClass.CURRENT,
    "curr_l3": SensorDeviceClass.CURRENT,
    "curr_mains": SensorDeviceClass.CURRENT,
    "freq": SensorDeviceClass.FREQUENCY,
    "power": SensorDeviceClass.POWER,
    "power_ac9": SensorDeviceClass.POWER,
    "power_act": SensorDeviceClass.POWER,
    "power_elwa2": SensorDeviceClass.POWER,
    "power_grid": SensorDeviceClass.POWER,
    "soc": SensorDeviceClass.BATTERY,
    "temp1": SensorDeviceClass.TEMPERATURE,
    "temp2": SensorDeviceClass.TEMPERATURE,
    "temp3": SensorDeviceClass.TEMPERATURE,
    "temp4": SensorDeviceClass.TEMPERATURE,
    "uptime": SensorDeviceClass.DURATION,
    "volt_l2": SensorDeviceClass.VOLTAGE,
    "volt_l3": SensorDeviceClass.VOLTAGE,
    "volt_mains": SensorDeviceClass.VOLTAGE,
    "wifi_signal": SensorDeviceClass.SIGNAL_STRENGTH,
    "wifi_signal_strength": SensorDeviceClass.SIGNAL_STRENGTH,
}

ENTITY_CATEGORIES: Final = {
    "cur_eth_mode": EntityCategory.DIAGNOSTIC,
    "freq": EntityCategory.DIAGNOSTIC,
    "uptime": EntityCategory.DIAGNOSTIC,
    "volt_l2": EntityCategory.DIAGNOSTIC,
    "volt_l3": EntityCategory.DIAGNOSTIC,
    "volt_mains": EntityCategory.DIAGNOSTIC,
    "wifi_signal": EntityCategory.DIAGNOSTIC,
    "wifi_signal_strength": EntityCategory.DIAGNOSTIC,
}

STATE_CLASSES: Final = {
    "uptime": SensorStateClass.TOTAL_INCREASING,
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyPVConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the my-PV sensor."""
    coordinator = config_entry.runtime_data
    entities = []

    for key, config in coordinator.data_configurations:
        if config.get("type") != "boolean" and key not in RESERVED_KEYS:
            options = None
            device_class = None
            state_class = None
            if config.get("type") == "enumeration":
                device_class = SensorDeviceClass.ENUM
                options = list(config.get("options").keys())
            elif config.get("type") == "string":
                device_class = DEVICE_CLASSES.get(key)
            else:
                device_class = DEVICE_CLASSES.get(key)
                state_class = STATE_CLASSES.get(key, SensorStateClass.MEASUREMENT)

            entity_category = ENTITY_CATEGORIES.get(key)

            translation_key = key
            if key == "curr_mains" and coordinator.supports_data("curr_l2"):
                translation_key = "curr_l1"
            elif key == "volt_mains" and coordinator.supports_data("volt_l2"):
                translation_key = "volt_l1"
            elif key == "temp1" and not coordinator.supports_data("temp2"):
                translation_key = "temp"

            entity_description = SensorEntityDescription(
                key=key,
                device_class=device_class,
                entity_category=entity_category,
                translation_key=translation_key,
                native_unit_of_measurement=config.get("unit"),
                options=options,
                state_class=state_class,
            )
            entities.append(
                MyPVSensor(
                    coordinator,
                    entity_description,
                    coordinator.device.serial_number,
                )
            )

    async_add_entities(entities)


class MyPVSensor(MyPVDataEntity, SensorEntity):
    """Base my-PV Sensor."""

    @property
    @override
    def native_value(self) -> Any:
        """Return the value reported by the sensor."""
        return self.coordinator.get_data_value(self.entity_description.key)
