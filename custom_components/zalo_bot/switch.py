"""Zalo Bot switches."""
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
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
        config_data = {**config_entry.data, **config_entry.options}
        self._is_on = config_data.get(CONF_ENABLE_NOTIFICATIONS, DEFAULT_ENABLE_NOTIFICATIONS)

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


class ZaloBotMarkdownSwitch(SwitchEntity, RestoreEntity):
    """Switch bật/tắt định dạng markdown (**bold**, *italic*...)."""

    _attr_has_entity_name = True
    _attr_name = "Markdown"
    _attr_icon = "mdi:language-markdown"

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        self.hass = hass
        self.config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_markdown"
        self._attr_device_info = get_device_info()
        self._is_on = DEFAULT_MARKDOWN_ENABLED

    async def async_added_to_hass(self) -> None:
        """Khôi phục trạng thái markdown đã lưu sau khi restart."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None:
            self._is_on = last_state.state == "on"
        self.hass.data[DOMAIN][CONF_MARKDOWN_ENABLED] = self._is_on

    @property
    def is_on(self) -> bool:
        return self._is_on

    async def async_turn_on(self, *_) -> None:
        self._is_on = True
        self.hass.data[DOMAIN][CONF_MARKDOWN_ENABLED] = True
        self.async_write_ha_state()
        _LOGGER.info("Markdown formatting enabled")

    async def async_turn_off(self, *_) -> None:
        self._is_on = False
        self.hass.data[DOMAIN][CONF_MARKDOWN_ENABLED] = False
        self.async_write_ha_state()
        _LOGGER.info("Markdown formatting disabled")
