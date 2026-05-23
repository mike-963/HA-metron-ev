"""Select entities for Metron EV Station."""

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import MetronEVBaseEntity
from .hub import MetronEVHub

CURRENT_OPTIONS = ["0", "6", "8", "10", "12", "14", "16"]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add select entities for setup hub object."""
    hub = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        [
            DynamicCurrentLimit(hub),
        ]
    )


class DynamicCurrentLimit(MetronEVBaseEntity, SelectEntity):
    """Select entity for setting the dynamic charging current limit."""

    def __init__(self, hub: MetronEVHub) -> None:
        """Initialize the select entity."""
        super().__init__(hub)
        self._attr_unique_id = f"{hub._name}_set_current_limit"
        self._attr_name = f"{hub._name} current limit"
        self._attr_options = CURRENT_OPTIONS
        self._attr_icon = "mdi:current-ac"

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        try:
            value = int(self._hub.dynamic_charging_current_limit)
            # Map any value not in options to closest valid option
            if value < 6:
                return "0"
            elif value > 16:
                return "16"
            elif str(value) in CURRENT_OPTIONS:
                return str(value)
            else:
                # Round to nearest even number
                return str((value // 2) * 2)
        except (ValueError, TypeError):
            return None

    async def async_select_option(self, option: str) -> None:
        """Set the charging current limit."""
        payload = f"SLIDE{option}"
        await self._hub.perform_action(payload)
