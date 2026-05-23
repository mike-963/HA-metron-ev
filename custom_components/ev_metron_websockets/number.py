"""Number entities for Metron EV Station."""

from homeassistant.components.number import (
    NumberEntity,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import MetronEVBaseEntity
from .hub import MetronEVHub


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add number entities for setup hub object."""
    hub = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        [
            ChargeDelayTimer(hub),
            DynamicCurrentLimit(hub)
        ]
    )


class ChargeDelayTimer(MetronEVBaseEntity, NumberEntity):
    """Number entity for setting the charge delay timer."""

    def __init__(self, hub: MetronEVHub) -> None:
        """Initialize the number entity."""
        super().__init__(hub)
        self._attr_unique_id = f"{hub._name}_set_charge_delay"
        self._attr_name = f"{hub._name} charge delay"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 720
        self._attr_native_step = 5
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        self._attr_mode = NumberMode.BOX
        self._attr_icon = "mdi:timer-outline"

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        try:
            return int(self._hub.ESP32_timer_delay)
        except (ValueError, TypeError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the charge delay timer."""
        int_value = int(value)
        payload = f"TIMER{int_value}"
        await self._hub.perform_action(payload)


MAX_VALUE = "32"

class DynamicCurrentLimit(MetronEVBaseEntity, NumberEntity):
    """Number entity for setting the dynamic charging current limit."""

    def __init__(self, hub: MetronEVHub) -> None:
        """Initialize the number entity."""
        super().__init__(hub)

        self._attr_unique_id = f"{hub._name}_current_limit"
        self._attr_name = f"{hub._name} current limit"

        self._attr_native_min_value = 0
        self._attr_native_max_value = MAX_VALUE
        self._attr_native_step = 1

        self._attr_native_unit_of_measurement = (
            UnitOfElectricCurrent.AMPERE
        )

        self._attr_mode = "slider"
        self._attr_icon = "mdi:current-ac"

    @property
    def native_value(self) -> float | None:
        """Return the current charging current limit."""
        try:
            value = int(self._hub.dynamic_charging_current_limit)

            if value < 0:
                return MAX_VALUE

            if value > MAX_VALUE:
                return MAX_VALUE

            return value

        except (ValueError, TypeError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the charging current limit."""
        value = int(value)

        if value < 0:
            value = MAX_VALUE

        if value > MAX_VALUE:
            value = MAX_VALUE

        payload = f"SLIDE{value}"

        await self._hub.perform_action(payload)
