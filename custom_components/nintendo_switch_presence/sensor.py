from typing import Any, Optional
from datetime import datetime
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    user_id = coordinator.user_id
    include_splatoon3 = coordinator.include_splatoon3

    sensors = [
        NintendoSwitchSensor(coordinator, user_id),
        GameSensor(coordinator, user_id),
    ]
    
    if include_splatoon3:
        sensors.append(Splatoon3Sensor(coordinator, user_id))

    async_add_entities(sensors, True)


class BaseNintendoSwitchSensor(CoordinatorEntity, SensorEntity):
    """Base sensor with shared device info."""

    has_entity_name = False

    def __init__(self, coordinator, user_id: str):
        super().__init__(coordinator)
        self.user_id = user_id

    @property
    def device_info(self) -> DeviceInfo:
        friend = (self.coordinator.data or {}).get("friend", {})
        return DeviceInfo(
            identifiers={(DOMAIN, friend.get("nsaId"))},
            name="Nintendo Switch",
            manufacturer="Nintendo",
            model="Switch",
        )


class NintendoSwitchSensor(BaseNintendoSwitchSensor):
    """Main Nintendo Switch sensor with user status and game info."""

    @property
    def unique_id(self) -> str:
        return f"switch_profile_{self.user_id}"

    @property
    def name(self) -> str:
        return f"switch_profile_{self.user_id}"

    @property
    def icon(self) -> Optional[str]:
        """Always use Nintendo Switch icon."""
        return "mdi:nintendo-switch"

    @property
    def entity_picture(self) -> Optional[str]:
        """Return user profile image."""
        return (self.coordinator.data or {}).get("friend", {}).get("imageUri")

    @property
    def native_value(self) -> Optional[str]:
        """Return the online status/state."""
        return (self.coordinator.data or {}).get("friend", {}).get("presence", {}).get("state")

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        friend = (self.coordinator.data or {}).get("friend", {})
        presence = friend.get("presence", {})
        game = presence.get("game", {})
        
        attrs = {
            "Account Name": friend.get("name"),
            "Status": presence.get("state"),
        }
        
        if game:
            attrs["Game Name"] = game.get("name")
            attrs["Game Image URL"] = game.get("imageUri")
            
            # Total play time in hours
            minutes = game.get("totalPlayTime")
            if minutes is not None:
                attrs["Total Play Time"] = round(minutes / 60, 2)
            
            # First played at - convert timestamp to ISO format
            first_played = game.get("firstPlayedAt")
            if first_played:
                attrs["First Played At"] = datetime.fromtimestamp(first_played).isoformat()
        
        # Platform
        platform_num = presence.get("platform")
        if platform_num == 1:
            attrs["Platform"] = "Nintendo Switch 1"
        elif platform_num == 2:
            attrs["Platform"] = "Nintendo Switch 2"
        elif platform_num is not None:
            attrs["Platform"] = f"Platform {platform_num}"
        
        return attrs


class GameSensor(BaseNintendoSwitchSensor):
    """Game/Title sensor with game details."""

    @property
    def unique_id(self) -> str:
        return f"switch_game_{self.user_id}"

    @property
    def name(self) -> str:
        return f"switch_game_{self.user_id}"

    @property
    def icon(self) -> Optional[str]:
        """Always use Nintendo Switch icon."""
        return "mdi:nintendo-switch"

    @property
    def entity_picture(self) -> Optional[str]:
        """Return game image if game is being played."""
        game = (self.coordinator.data or {}).get("friend", {}).get("presence", {}).get("game")
        if game:
            return game.get("imageUri")
        return None

    @property
    def native_value(self) -> Optional[str]:
        """Return the current game name."""
        game = (self.coordinator.data or {}).get("friend", {}).get("presence", {}).get("game")
        if game:
            return game.get("name")
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        game = (self.coordinator.data or {}).get("friend", {}).get("presence", {}).get("game")
        friend = (self.coordinator.data or {}).get("friend", {})
        attrs = {}
        
        # Add switch name as the first attribute
        attrs["Name"] = friend.get("name")
        
        if not game:
            return attrs
        
        attrs["Game Name"] = game.get("name")
        attrs["Game Image URL"] = game.get("imageUri")
        
        # Total play time in hours
        minutes = game.get("totalPlayTime")
        if minutes is not None:
            attrs["Total Play Time"] = round(minutes / 60, 2)
        
        # First played at - convert timestamp to ISO format
        first_played = game.get("firstPlayedAt")
        if first_played:
            attrs["First Played At"] = datetime.fromtimestamp(first_played).isoformat()
        
        # Platform
        presence = (self.coordinator.data or {}).get("friend", {}).get("presence", {})
        platform_num = presence.get("platform")
        if platform_num == 1:
            attrs["Platform"] = "Nintendo Switch 1"
        elif platform_num == 2:
            attrs["Platform"] = "Nintendo Switch 2"
        elif platform_num is not None:
            attrs["Platform"] = f"Platform {platform_num}"
        
        # Add Splatoon 3 specific attributes if available
        splatoon3 = (self.coordinator.data or {}).get("splatoon3")
        if splatoon3:
            attrs["Nickname"] = splatoon3.get("nickname")
            
            vs_mode = splatoon3.get("vsMode")
            if vs_mode:
                attrs["Battle Mode"] = vs_mode.get("name")
            
            splatoon3_vs_setting = (self.coordinator.data or {}).get("splatoon3_vs_setting")
            if splatoon3_vs_setting:
                vs_rule = splatoon3_vs_setting.get("vsRule")
                if vs_rule:
                    attrs["Game Mode"] = vs_rule.get("name")
        
        return attrs


class Splatoon3Sensor(BaseNintendoSwitchSensor):
    """Splatoon 3 specific sensor with game mode info."""

    @property
    def unique_id(self) -> str:
        return f"switch_splatoon3_{self.user_id}"

    @property
    def name(self) -> str:
        return f"switch_splatoon3_{self.user_id}"

    @property
    def icon(self) -> Optional[str]:
        """Use water icon unless playing Splatoon 3, then show game icon."""
        friend = (self.coordinator.data or {}).get("friend", {})
        game = friend.get("presence", {}).get("game", {})
        game_name = game.get("name", "")
        
        # Show game icon when playing Splatoon 3
        if "Splatoon 3" in game_name and game.get("imageUri"):
            return None
        return "mdi:water"

    @property
    def entity_picture(self) -> Optional[str]:
        """Return Splatoon 3 game icon only if currently playing Splatoon 3."""
        friend = (self.coordinator.data or {}).get("friend", {})
        game = friend.get("presence", {}).get("game", {})
        game_name = game.get("name", "")
        
        # Only show picture if currently playing Splatoon 3
        if "Splatoon 3" in game_name:
            return game.get("imageUri")
        return None

    @property
    def native_value(self) -> Optional[str]:
        """Return the current state based on presence."""
        friend = (self.coordinator.data or {}).get("friend", {})
        presence = friend.get("presence", {})
        game = presence.get("game", {})
        game_name = game.get("name", "")
        state = presence.get("state", "")
        
        # Determine what to display based on state and game
        if "Splatoon 3" in game_name:
            # Check if in battle mode
            splatoon3 = (self.coordinator.data or {}).get("splatoon3")
            if splatoon3:
                vs_mode = splatoon3.get("vsMode")
                if vs_mode:
                    mode_name = vs_mode.get("name")
                    if mode_name:
                        return mode_name
            return "Splatoon 3"
        elif state and state.lower() == "online" and game_name:
            # Playing something other than Splatoon 3
            return "Playing"
        elif state and state.lower() == "online":
            # Online but not playing anything
            return "Online"
        else:
            # Offline
            return "Offline"

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        splatoon3 = (self.coordinator.data or {}).get("splatoon3")
        if not splatoon3:
            return {}
        
        attrs = {}
        attrs["Nickname"] = splatoon3.get("nickname")
        attrs["Player Name"] = splatoon3.get("playerName")
        
        vs_mode = splatoon3.get("vsMode")
        if vs_mode:
            attrs["Battle Mode"] = vs_mode.get("name")
        
        # Add Game Mode from vsRule
        splatoon3_vs_setting = (self.coordinator.data or {}).get("splatoon3_vs_setting")
        if splatoon3_vs_setting:
            vs_rule = splatoon3_vs_setting.get("vsRule")
            if vs_rule:
                attrs["Game Mode"] = vs_rule.get("name")
        
        # Add Platform
        friend = (self.coordinator.data or {}).get("friend", {})
        presence = friend.get("presence", {})
        platform_num = presence.get("platform")
        if platform_num == 1:
            attrs["Platform"] = "Nintendo Switch 1"
        elif platform_num == 2:
            attrs["Platform"] = "Nintendo Switch 2"
        elif platform_num is not None:
            attrs["Platform"] = f"Platform {platform_num}"
        
        return attrs