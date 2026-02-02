# custom_components/nintendo_switch_status/sensor.py
from typing import Any
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            NintendoSwitchOnlineSensor(coordinator),
            NintendoSwitchGameSensor(coordinator),
            NintendoSwitchGameImageSensor(coordinator),
            NintendoSwitchProfileNameSensor(coordinator),
            NintendoSwitchProfileImageSensor(coordinator),
            NintendoSwitchAccountIdSensor(coordinator),
            NintendoSwitchTotalPlaytimeSensor(coordinator),
            NintendoSwitchPlatformSensor(coordinator),
        ],
        True,
    )

class BaseNintendoSwitchSensor(CoordinatorEntity, SensorEntity):
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

def _friend() -> dict:
    """Helper placeholder when used in instance methods (kept for readability)."""
    return {}

class NintendoSwitchOnlineSensor(BaseNintendoSwitchSensor):
    _attr_unique_id = "nintendo_switch_status_online"
    _attr_name = "Online Status"
    _attr_icon = "mdi:account-badge-outline"

    @property
    def native_value(self) -> Any:
        return (self.coordinator.data or {}).get("friend", {}).get("presence", {}).get("state")

class NintendoSwitchGameSensor(BaseNintendoSwitchSensor):
    _attr_unique_id = "nintendo_switch_status_game"
    _attr_name = "Current Game"
    _attr_icon = "mdi:nintendo-switch"

    @property
    def native_value(self) -> Any:
        game = (self.coordinator.data or {}).get("friend", {}).get("presence", {}).get("game")
        return game.get("name") if game else None

class NintendoSwitchGameImageSensor(BaseNintendoSwitchSensor):
    _attr_unique_id = "nintendo_switch_status_game_image"
    _attr_name = "Game Image URL"
    _attr_icon = "mdi:image"

    @property
    def native_value(self) -> Any:
        game = (self.coordinator.data or {}).get("friend", {}).get("presence", {}).get("game")
        return game.get("imageUri") if game else None

    @property
    def extra_state_attributes(self) -> dict:
        url = self.native_value
        return {"entity_picture": url} if url else {}

class NintendoSwitchProfileNameSensor(BaseNintendoSwitchSensor):
    _attr_unique_id = "nintendo_switch_status_profile_name"
    _attr_name = "Profile Name"
    _attr_icon = "mdi:account-circle"

    @property
    def native_value(self) -> Any:
        return (self.coordinator.data or {}).get("friend", {}).get("name")

class NintendoSwitchProfileImageSensor(BaseNintendoSwitchSensor):
    _attr_unique_id = "nintendo_switch_status_profile_image"
    _attr_name = "Profile Image URL"
    _attr_icon = "mdi:image"

    @property
    def native_value(self) -> Any:
        return (self.coordinator.data or {}).get("friend", {}).get("imageUri")

    @property
    def extra_state_attributes(self) -> dict:
        url = self.native_value
        return {"entity_picture": url} if url else {}

class NintendoSwitchAccountIdSensor(BaseNintendoSwitchSensor):
    _attr_unique_id = "nintendo_switch_status_account_id"
    _attr_name = "Nintendo Switch Account ID"
    _attr_icon = "mdi:identifier"

    @property
    def native_value(self) -> Any:
        return (self.coordinator.data or {}).get("friend", {}).get("id")

class NintendoSwitchTotalPlaytimeSensor(BaseNintendoSwitchSensor):
    _attr_unique_id = "nintendo_switch_status_total_playtime"
    _attr_name = "Total Playtime"
    _attr_icon = "mdi:calendar-clock"

    @property
    def native_value(self) -> Any:
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
    _attr_unique_id = "nintendo_switch_status_platform"
    _attr_name = "Platform"
    _attr_icon = "mdi:console"

    @property
    def native_value(self) -> Any:
        platform = (self.coordinator.data or {}).get("friend", {}).get("presence", {}).get("platform")
        # Map numeric platform codes to friendly names
        if platform == 1:
            return "Nintendo Switch 1"
        if platform == 2:
            return "Nintendo Switch 2"
        return f"Platform {platform}" if platform is not None else None

    @property
    def extra_state_attributes(self) -> dict:
        platform_num = (self.coordinator.data or {}).get("friend", {}).get("presence", {}).get("platform")
        return {"platform_number": platform_num} if platform_num is not None else {}