"""Cảm biến nhị phân cho Zalo Bot."""
from __future__ import annotations

import logging
import aiohttp
import json
from datetime import timedelta
from typing import Any
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from .const import DOMAIN, CONF_ZALO_SERVER, CONF_USERNAME, CONF_PASSWORD
from . import get_device_info

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=1)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Thiết lập cảm biến nhị phân."""
    config = hass.data[DOMAIN].get(entry.entry_id, {})
    zalo_server = config.get(CONF_ZALO_SERVER)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    coordinator = ZaloLoginCoordinator(hass, zalo_server, username, password)
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([
        ZaloLoginBinarySensor(coordinator, entry),
        ZaloServerBinarySensor(coordinator, entry)
    ], True)


class ZaloLoginCoordinator(DataUpdateCoordinator):
    """Kiểm tra đăng nhập Zalo."""

    def __init__(self, hass: HomeAssistant, zalo_server: str, username: str, password: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Zalo Login",
            update_interval=SCAN_INTERVAL,
        )
        self.zalo_server = zalo_server
        self.username = username
        self.password = password
        self.session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True))
        self.data = {"logged_in": False, "total": 0, "accounts": []}
        self.server_reachable = False
        self.login_success = False

    async def _async_update_data(self) -> dict[str, Any]:
        """Kiểm tra đăng nhập qua API."""
        self.server_reachable = False
        try:
            try:
                async with self.session.get(
                    f"{self.zalo_server}", 
                    timeout=5
                ) as resp:
                    self.server_reachable = True
            except:
                self.login_success = False
                return {"logged_in": False, "total": 0, "accounts": []}
            headers = {"Accept": "application/json", "Content-Type": "application/json"}
            login_data = {"username": self.username, "password": self.password}
            async with self.session.post(
                f"{self.zalo_server}/api/login", 
                json=login_data, 
                headers=headers
            ) as resp:
                if resp.status != 200:
                    self.login_success = False
                    return {"logged_in": False, "total": 0, "accounts": []}
                try:
                    login_resp = json.loads(await resp.text())
                    self.login_success = login_resp.get("success", False) is True
                except:
                    self.login_success = False
            async with self.session.get(
                f"{self.zalo_server}/api/accounts",
                headers={"Accept": "application/json"}
            ) as resp:
                if resp.status != 200:
                    return {"logged_in": False, "total": 0, "accounts": []}
                try:
                    response = json.loads(await resp.text())
                    if response.get("success"):
                        return {
                            "logged_in": response.get("total", 0) > 0,
                            "total": response.get("total", 0),
                            "accounts": response.get("data", [])
                        }
                except:
                    pass
        except Exception:
            self.server_reachable = False
            self.login_success = False
        return {"logged_in": False, "total": 0, "accounts": []}
    async def async_close(self) -> None:
        """Đóng session."""
        await self.session.close()
        await super().async_close()


class ZaloLoginBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Cảm biến nhị phân cho trạng thái đăng nhập Zalo."""
    _attr_has_entity_name = True
    _attr_name = "Zalo Login"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    def __init__(
        self,
        coordinator: ZaloLoginCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_login_status"
        self._attr_device_info = get_device_info()

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("logged_in", False)
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "total_accounts": self.coordinator.data.get("total", 0),
            "accounts": self.coordinator.data.get("accounts", []),
        }
    _attr_icon = "mdi:account"


class ZaloServerBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Cảm biến nhị phân cho trạng thái kết nối Zalo Server."""
    _attr_has_entity_name = True
    _attr_name = "Zalo Server"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    def __init__(
        self,
        coordinator: ZaloLoginCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_server_status"
        self._attr_device_info = get_device_info()
    @property
    def is_on(self) -> bool:
        resp_status = getattr(self.coordinator, "login_success", False)
        return resp_status
    _attr_icon = "mdi:server"
