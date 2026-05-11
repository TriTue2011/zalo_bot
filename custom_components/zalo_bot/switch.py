"""Zalo Bot switches."""
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import (
    CONF_ENABLE_NOTIFICATIONS,
    CONF_MARKDOWN_ENABLED,
    DEFAULT_ENABLE_NOTIFICATIONS,
    DEFAULT_MARKDOWN_ENABLED,
    DOMAIN,
    SIGNAL_NOTIFICATION_TOGGLE,
)
from . import get_device_info

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([
        ZaloBotNotificationSwitch(hass, config_entry),
        ZaloBotMarkdownSwitch(hass, config_entry),
    ])


class ZaloBotNotificationSwitch(SwitchEntity):
    """Switch để bật/tắt thông báo từ Zalo Bot."""

    _attr_has_entity_name = True
    _attr_name = "Thông báo"
    _attr_icon = "mdi:bell"

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        self.hass = hass
        self.config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_notifications"
        self._attr_device_info = get_device_info()
        self._is_on = config_entry.data.get(CONF_ENABLE_NOTIFICATIONS, DEFAULT_ENABLE_NOTIFICATIONS)

    @property
    def is_on(self) -> bool:
        return self._is_on

    async def async_turn_on(self, *_) -> None:
        self._is_on = True
        await self._update_config()
        self.async_write_ha_state()

    async def async_turn_off(self, *_) -> None:
        self._is_on = False
        await self._update_config()
        self.async_write_ha_state()

    async def _update_config(self) -> None:
        data = {**self.config_entry.data}
        data[CONF_ENABLE_NOTIFICATIONS] = self._is_on
        self.hass.data[DOMAIN][self.config_entry.entry_id][CONF_ENABLE_NOTIFICATIONS] = self._is_on
        self.hass.config_entries.async_update_entry(self.config_entry, data=data)
        async_dispatcher_send(self.hass, SIGNAL_NOTIFICATION_TOGGLE, self._is_on)


class ZaloBotMarkdownSwitch(SwitchEntity):
    """Switch bật/tắt định dạng markdown (**bold**, *italic*...)."""

    _attr_has_entity_name = True
    _attr_name = "Markdown"
    _attr_icon = "mdi:language-markdown"

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        self.hass = hass
        self.config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_markdown"
        self._attr_device_info = get_device_info()

    @property
    def is_on(self) -> bool:
        return self.config_entry.data.get(CONF_MARKDOWN_ENABLED, DEFAULT_MARKDOWN_ENABLED)

    async def async_turn_on(self, *_) -> None:
        await self._update_config(True)
        self.async_write_ha_state()

    async def async_turn_off(self, *_) -> None:
        await self._update_config(False)
        self.async_write_ha_state()

    async def _update_config(self, enabled: bool) -> None:
        data = {**self.config_entry.data}
        data[CONF_MARKDOWN_ENABLED] = enabled
        self.hass.data[DOMAIN][CONF_MARKDOWN_ENABLED] = enabled
        self.hass.config_entries.async_update_entry(self.config_entry, data=data)
        _LOGGER.info("Markdown formatting %s", "enabled" if enabled else "disabled")
