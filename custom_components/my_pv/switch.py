"""Creates Switch entities for the my-PV Home Assistant integration."""

from typing import Any, Final, override

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import MyPVConfigEntry
from .const import DOMAIN
from .entity import MyPVSetupEntity

SWITCH_DESCRIPTIONS: Final[dict[str, dict[str, Any]]] = {
    "boostactive": {
        "translation_key": "boostactive",
        "device_class": SwitchDeviceClass.SWITCH,
    },
    "bstmode": {
        "translation_key": "bstmode",
        "device_class": SwitchDeviceClass.SWITCH,
    },
    "bststrt": {
        "translation_key": "bststrt",
        "device_class": SwitchDeviceClass.SWITCH,
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyPVConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the my-PV switch."""
    coordinator = config_entry.runtime_data
    entities = []

    for key, config in coordinator.setup_configurations:
        if config.get("type") == "boolean" and key in SWITCH_DESCRIPTIONS:
            switch_description: dict = SWITCH_DESCRIPTIONS[key]

            entity_description = SwitchEntityDescription(
                key=key,
                device_class=switch_description.get("device_class"),
                entity_category=switch_description.get("entity_category"),
                translation_key=switch_description.get("translation_key"),
                entity_registry_enabled_default=switch_description.get("enabled", True),
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
    """my-PV switch."""

    @property
    @override
    def is_on(self) -> bool | None:
        """Return if the switch is on."""
        value = self.coordinator.device.get_setup_value(self.entity_description.key)
        return bool(value) if value is not None else None

    @override
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        if not await self.coordinator.set_setup_value(
            self.entity_description.key, True
        ):
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="unknown_error"
            )

    @override
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        if not await self.coordinator.set_setup_value(
            self.entity_description.key, False
        ):
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="unknown_error"
            )
