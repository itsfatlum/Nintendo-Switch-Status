from typing import Any, Optional
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers import entity_registry as er
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    # Migrate entity registry unique_ids from "nintendo_switch_status_*" to
    # "nintendo_switch_presence_*" so existing entities keep their settings.
    ent_reg = er.async_get(hass)
    migration_map = {
        "nintendo_switch_status_status": "nintendo_switch_presence_status",
        "nintendo_switch_status_game": "nintendo_switch_presence_game",
        "nintendo_switch_status_profile": "nintendo_switch_presence_profile",
        "nintendo_switch_status_account_id": "nintendo_switch_presence_account_id",
        "nintendo_switch_status_total_playtime": "nintendo_switch_presence_total_playtime",
        "nintendo_switch_status_platform": "nintendo_switch_presence_platform",
    }
    for old_unique, new_unique in migration_map.items():
        entity_id = ent_reg.async_get_entity_id("sensor", DOMAIN, old_unique)
        if entity_id:
            ent_reg.async_update_entity(entity_id, new_unique_id=new_unique)
            _LOGGER.debug(
                "Migrated entity %s unique_id %s -> %s", entity_id, old_unique, new_unique
            )

    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            NintendoSwitchStatusSensor(coordinator),
            NintendoSwitchGameSensor(coordinator),
            NintendoSwitchProfileSensor(coordinator),
            NintendoSwitchAccountIdSensor(coordinator),
            NintendoSwitchTotalPlaytimeSensor(coordinator),
            NintendoSwitchPlatformSensor(coordinator),
        ],
        True,
    )


class BaseNintendoSwitchSensor(CoordinatorEntity, SensorEntity):
    """Base sensor with shared device info."""

    has_entity_name = True

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def device_info(self) -> DeviceInfo:
        friend = (self.coordinator.data or {}).get("friend", {})
        return DeviceInfo(
            identifiers={(DOMAIN, friend.get("nsaId"))},
            name="Nintendo Switch",
            manufacturer="Nintendo",
            model="Switch",
        )


class NintendoSwitchStatusSensor(BaseNintendoSwitchSensor):
    """Online status sensor renamed to 'Status'."""

    _attr_unique_id = "nintendo_switch_presence_status"
    _attr_name = "Status"
    _attr_icon = "mdi:account-badge-outline"

    @property
    def native_value(self) -> Optional[str]:
        return (self.coordinator.data or {}).get("friend", {}).get(
            "presence", {}
        ).get("state")


class NintendoSwitchGameSensor(BaseNintendoSwitchSensor):
    """
    Current Game sensor.
    - State: game name or None
    - If game image exists -> expose as entity_picture and hide icon (return None in icon property)
    - If no game image -> show fallback mdi:nintendo-switch icon
    """

    _attr_unique_id = "nintendo_switch_presence_game"
    _attr_name = "Current Game"
    _attr_icon = "mdi:nintendo-switch"

    @property
    def native_value(self) -> Optional[str]:
        game = (self.coordinator.data or {}).get("friend", {}).get("presence", {}).get("game")
        return game.get("name") if game else None

    @property
    def extra_state_attributes(self) -> dict:
        """Provide entity_picture when game image is available."""
        game = (self.coordinator.data or {}).get("friend", {}).get("presence", {}).get("game")
        url = game.get("imageUri") if game else None
        return {"entity_picture": url} if url else {}

    @property
    def icon(self) -> Optional[str]:
        """Return None when an entity_picture is available so UI shows the picture; otherwise fallback icon."""
        attrs = self.extra_state_attributes
        if attrs and attrs.get("entity_picture"):
            return None
        return self._attr_icon


class NintendoSwitchProfileSensor(BaseNintendoSwitchSensor):
    """
    Profile sensor (single entity):
    - State: Nintendo account/display name
    - entity_picture: profile image URL (if available)
    - icon fallback: mdi:account-circle
    """

    _attr_unique_id = "nintendo_switch_presence_profile"
    _attr_name = "Profile"
    _attr_icon = "mdi:account-circle"

    @property
    def native_value(self) -> Optional[str]:
        return (self.coordinator.data or {}).get("friend", {}).get("name")

    @property
    def extra_state_attributes(self) -> dict:
        """Expose profile image as entity_picture when present."""
        url = (self.coordinator.data or {}).get("friend", {}).get("imageUri")
        return {"entity_picture": url} if url else {}

    @property
    def icon(self) -> Optional[str]:
        """Hide icon when profile picture exists (so UI shows the pfp); otherwise show fallback."""
        attrs = self.extra_state_attributes
        if attrs and attrs.get("entity_picture"):
            return None
        return self._attr_icon


class NintendoSwitchAccountIdSensor(BaseNintendoSwitchSensor):
    _attr_unique_id = "nintendo_switch_presence_account_id"
    _attr_name = "Nintendo Switch Account ID"
    _attr_icon = "mdi:identifier"

    @property
    def native_value(self) -> Optional[Any]:
        return (self.coordinator.data or {}).get("friend", {}).get("id")


class NintendoSwitchTotalPlaytimeSensor(BaseNintendoSwitchSensor):
    _attr_unique_id = "nintendo_switch_presence_total_playtime"
    _attr_name = "Total Playtime"
    _attr_icon = "mdi:calendar-clock"

    @property
    def native_value(self) -> Optional[int]:
        game = (self.coordinator.data or {}).get("friend", {}).get("presence", {}).get("game")
        if not game:
            return None
        return game.get("totalPlayTime")

    @property
    def native_unit_of_measurement(self) -> str:
        return "min"

    @property
    def extra_state_attributes(self) -> dict:
        minutes = self.native_value
        try:
            if minutes is None:
                return {}
            hours = round(minutes / 60, 2)
            return {"hours": hours}
        except Exception:
            return {}


class NintendoSwitchPlatformSensor(BaseNintendoSwitchSensor):
    _attr_unique_id = "nintendo_switch_presence_platform"
    _attr_name = "Platform"
    _attr_icon = "mdi:console"

    @property
    def native_value(self) -> Optional[str]:
        platform = (self.coordinator.data or {}).get("friend", {}).get("presence", {}).get("platform")
        if platform == 1:
            return "Nintendo Switch 1"
        if platform == 2:
            return "Nintendo Switch 2"
        return f"Platform {platform}" if platform is not None else None

    @property
    def extra_state_attributes(self) -> dict:
        platform_num = (self.coordinator.data or {}).get("friend", {}).get("presence", {}).get("platform")
        return {"platform_number": platform_num} if platform_num is not None else {}