"""Creates Sensor entities for the my-PV Home Assistant integration."""

from datetime import UTC, datetime
from typing import Any, Final, override

from my_pv.exceptions import MyPVNotSupportedError

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import MyPVConfigEntry
from .coordinator import MyPVCoordinator
from .entity import MyPVBaseEntity, MyPVDataEntity

SENSOR_DESCRIPTIONS: Final[dict[str, dict[str, Any]]] = {
    "cur_eth_mode": {
        "enabled": False,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "translation_key": "cur_eth_mode",
    },
    "curr_l1": {
        "device_class": SensorDeviceClass.CURRENT,
        "translation_key": "curr_l1",
    },
    "curr_l2": {
        "device_class": SensorDeviceClass.CURRENT,
        "translation_key": "curr_l2",
    },
    "curr_l3": {
        "device_class": SensorDeviceClass.CURRENT,
        "translation_key": "curr_l3",
    },
    "curr_mains": {
        "device_class": SensorDeviceClass.CURRENT,
        "translation_key": "curr_l1",
    },
    "freq": {
        "device_class": SensorDeviceClass.FREQUENCY,
        "enabled": False,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "translation_key": "freq",
    },
    "power": {"device_class": SensorDeviceClass.POWER},
    "power_ac9": {"device_class": SensorDeviceClass.POWER},
    "power_act": {"device_class": SensorDeviceClass.POWER},
    "power_elwa2": {"device_class": SensorDeviceClass.POWER},
    "power_grid": {"device_class": SensorDeviceClass.POWER},
    "power_solar": {
        "device_class": SensorDeviceClass.POWER,
        "translation_key": "power_solar",
    },
    "screen_mode_flag": {"translation_key": "screen_mode_flag"},
    "temp_ps": {
        "device_class": SensorDeviceClass.TEMPERATURE,
        "enabled": False,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "translation_key": "temp_ps",
    },
    "temp1": {
        "device_class": SensorDeviceClass.TEMPERATURE,
        "translation_key": "temp1",
    },
    "temp2": {
        "device_class": SensorDeviceClass.TEMPERATURE,
        "translation_key": "temp2",
    },
    "temp3": {
        "device_class": SensorDeviceClass.TEMPERATURE,
        "translation_key": "temp3",
    },
    "temp4": {
        "device_class": SensorDeviceClass.TEMPERATURE,
        "translation_key": "temp4",
    },
    "uptime": {
        "device_class": SensorDeviceClass.DURATION,
        "enabled": False,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "translation_key": "uptime",
    },
    "volt_l1": {
        "device_class": SensorDeviceClass.VOLTAGE,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "translation_key": "volt_l1",
    },
    "volt_l2": {
        "device_class": SensorDeviceClass.VOLTAGE,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "translation_key": "volt_l2",
    },
    "volt_l3": {
        "device_class": SensorDeviceClass.VOLTAGE,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "translation_key": "volt_l3",
    },
    "volt_mains": {
        "device_class": SensorDeviceClass.VOLTAGE,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "translation_key": "volt_l1",
    },
    "volt_mains_l1": {
        "device_class": SensorDeviceClass.VOLTAGE,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "translation_key": "volt_l1",
    },
    "volt_mains_l2": {
        "device_class": SensorDeviceClass.VOLTAGE,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "translation_key": "volt_l2",
    },
    "volt_mains_l3": {
        "device_class": SensorDeviceClass.VOLTAGE,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "translation_key": "volt_l3",
    },
    "volt_solar": {
        "device_class": SensorDeviceClass.VOLTAGE,
        "translation_key": "volt_solar",
    },
    "wifi_signal": {
        "device_class": SensorDeviceClass.SIGNAL_STRENGTH,
        "enabled": False,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "translation_key": "wifi_signal",
    },
    "wifi_signal_strength": {
        "device_class": SensorDeviceClass.SIGNAL_STRENGTH,
        "enabled": False,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "translation_key": "wifi_signal_strength",
    },
}

POWER_KEYS: Final = [
    "power",
    "power_ac9",
    "power_act",
    "power_elwa2",
    "power_grid",
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyPVConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the my-PV sensor."""
    coordinator = config_entry.runtime_data
    entities = []

    for key, config in coordinator.data_configurations:
        if config.get("type") != "boolean" and key in SENSOR_DESCRIPTIONS:
            sensor_description: dict = SENSOR_DESCRIPTIONS[key]

            device_class = None
            options = None
            state_class = None
            if config.get("type") == "enumeration":
                device_class = SensorDeviceClass.ENUM
                options = list(config.get("options").keys())
            elif config.get("type") == "string":
                device_class = sensor_description.get("device_class")
            else:
                device_class = sensor_description.get("device_class")
                state_class = sensor_description.get(
                    "state_class", SensorStateClass.MEASUREMENT
                )

            translation_key: str | None = sensor_description.get("translation_key")
            if key in (
                "curr_mains",
                "curr_l1",
            ) and not coordinator.device.supports_data("curr_l2"):
                translation_key = None
            elif (
                key in ("volt_mains", "volt_l1")
                and not coordinator.device.supports_data("volt_l2")
                and not coordinator.device.supports_data("volt_mains_l2")
            ):
                translation_key = None
            elif key == "temp1" and not coordinator.device.supports_data("temp2"):
                translation_key = None

            suggested_display_precision = None
            divider = config.get("divider")
            if divider == 10:
                suggested_display_precision = 1
            elif divider:
                suggested_display_precision = 2

            entity_description = SensorEntityDescription(
                key=key,
                device_class=device_class,
                entity_category=sensor_description.get("entity_category"),
                translation_key=translation_key,
                native_unit_of_measurement=config.get("unit"),
                options=options,
                state_class=state_class,
                suggested_display_precision=suggested_display_precision,
                entity_registry_enabled_default=sensor_description.get("enabled", True),
            )
            entities.append(
                MyPVSensor(
                    coordinator,
                    entity_description,
                    coordinator.device.serial_number,
                )
            )

    power_key = next(
        (key for key in POWER_KEYS if coordinator.device.supports_data(key)), None
    )
    if power_key is not None:
        entities.append(
            MyPVEnergySensor(
                coordinator,
                SensorEntityDescription(
                    key="energy",
                    device_class=SensorDeviceClass.ENERGY,
                    state_class=SensorStateClass.TOTAL_INCREASING,
                    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
                    translation_key="energy",
                    suggested_display_precision=3,
                ),
                coordinator.device.serial_number,
                power_key,
            )
        )

    async_add_entities(entities)


class MyPVEnergySensor(MyPVBaseEntity, SensorEntity, RestoreEntity):
    """Energy sensor calculated from power readings."""

    _last_update: datetime | None = None
    _accumulated_energy: float = 0.0
    _power_key: str

    def __init__(
        self,
        coordinator: MyPVCoordinator,
        entity_description: SensorEntityDescription,
        serial_number: str,
        power_key: str,
    ) -> None:
        """Initialize the energy sensor."""
        super().__init__(coordinator, entity_description, serial_number)
        self._power_key = power_key

    @property
    @override
    def available(self) -> bool:
        """Return if entity is available."""
        if (
            not self.coordinator.device.connected
            or self.coordinator.device.is_on is None
        ):
            return False
        if not self.coordinator.device.supports_data(self._power_key):
            return False
        try:
            if self.coordinator.device.get_data_value(self._power_key) is None:
                return False
        except MyPVNotSupportedError:
            return False
        return super().available

    @override
    async def async_added_to_hass(self) -> None:
        """Restore previous accumulated energy."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state and last_state.state not in ("unknown", "unavailable"):
            try:
                self._accumulated_energy = float(last_state.state)
            except (ValueError, TypeError):
                pass

    @property
    @override
    def native_value(self) -> float:
        """Return accumulated energy in kWh."""
        return self._accumulated_energy

    @override
    def _handle_coordinator_update(self) -> None:
        """Accumulate energy from power readings on each update."""
        now = datetime.now(UTC)
        if self._last_update is not None:
            time_delta_hours = (now - self._last_update).total_seconds() / 3600
            if time_delta_hours <= 1:
                try:
                    power = self.coordinator.device.get_data_value(self._power_key)
                except MyPVNotSupportedError:
                    power = None
                if power is not None:
                    self._accumulated_energy += power * time_delta_hours / 1000
        self._last_update = now
        super()._handle_coordinator_update()


class MyPVSensor(MyPVDataEntity, SensorEntity):
    """Base my-PV Sensor."""

    @property
    @override
    def native_value(self) -> Any:
        """Return the value reported by the sensor."""
        return self.coordinator.device.get_data_value(self.entity_description.key)
