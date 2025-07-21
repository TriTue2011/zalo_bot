"""Zalo Bot switches."""
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_ENABLE_NOTIFICATIONS, DEFAULT_ENABLE_NOTIFICATIONS, DOMAIN, SIGNAL_NOTIFICATION_TOGGLE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Thiết lập các switch từ config entry."""
    # Thêm switch bật/tắt thông báo
    async_add_entities([ZaloBotNotificationSwitch(hass, config_entry)])


class ZaloBotNotificationSwitch(SwitchEntity):
    """Switch để bật/tắt thông báo từ Zalo Bot."""

    _attr_has_entity_name = True
    _attr_name = "Thông báo"
    _attr_icon = "mdi:bell"

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Khởi tạo switch thông báo."""
        self.hass = hass
        self.config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_notifications"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "zalo_bot")},
            name="Zalo Bot",
            manufacturer="Smarthome Black",
            model="Zalo Bot",
            sw_version="2025.7.11",
        )
        self._is_on = config_entry.data.get(CONF_ENABLE_NOTIFICATIONS, DEFAULT_ENABLE_NOTIFICATIONS)

    @property
    def is_on(self) -> bool:
        """Trả về trạng thái của switch."""
        return self._is_on

    async def async_turn_on(self, *_) -> None:
        """Bật thông báo."""
        self._is_on = True
        await self._update_config()
        self.async_write_ha_state()

    async def async_turn_off(self, *_) -> None:
        """Tắt thông báo."""
        self._is_on = False
        await self._update_config()
        self.async_write_ha_state()

    async def _update_config(self) -> None:
        """Cập nhật cấu hình trong config entry và thông báo cho các thành phần khác."""
        data = {**self.config_entry.data}
        data[CONF_ENABLE_NOTIFICATIONS] = self._is_on

        # Cập nhật dữ liệu trong hass.data
        self.hass.data[DOMAIN][self.config_entry.entry_id][CONF_ENABLE_NOTIFICATIONS] = self._is_on

        # Cập nhật config entry
        self.hass.config_entries.async_update_entry(
            self.config_entry, data=data
        )

        # Gửi tín hiệu để các thành phần khác biết về thay đổi
        async_dispatcher_send(
            self.hass, SIGNAL_NOTIFICATION_TOGGLE, self._is_on
        )
