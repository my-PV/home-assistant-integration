"""Creates Select entities for the my-PV Home Assistant integration."""

import logging

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import MyPVConfigEntry
from .const import DOMAIN
from .entity import MyPVSetupEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyPVConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the my-PV select."""
    coordinator = config_entry.runtime_data
    entities = []

    config = coordinator.get_setup_configuration("bstmode")
    if config and config.get("type") == "enumeration":
        entity_description = SelectEntityDescription(
            key="bstmode",
            translation_key="bstmode",
            options=list(config["options"].keys()),
        )
        entities.append(
            MyPVSelect(
                coordinator,
                entity_description,
                coordinator.device.serial_number,
            )
        )

    async_add_entities(entities)


class MyPVSelect(MyPVSetupEntity, SelectEntity):
    """Base my-PV Select."""

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if not self.coordinator.connected:
            self._attr_available = False
        else:
            value = self.coordinator.get_setup_value(self.entity_description.key)
            self._attr_current_option = str(value) if value is not None else None
            self._attr_available = value is not None

        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        _LOGGER.debug("Setting %s", self.name)

        if await self.coordinator.set_setup_value(self.entity_description.key, option):
            self._attr_current_option = option
        else:
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="unknown_error"
            )
