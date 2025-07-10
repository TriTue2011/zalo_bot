import logging
import os
import shutil
import requests
from homeassistant.components import webhook
from homeassistant.helpers import device_registry as dr
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from .const import DOMAIN
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)
WEBHOOK_ID = "zalo_bot_webhook"
WWW_DIR = "/config/www"
PUBLIC_DIR = os.path.join(WWW_DIR, "zalo_bot")


def copy_to_public(src_path, zalo_server):
    if not os.path.isfile(src_path):
        _LOGGER.error("Image file not found: %s", src_path)
        return None
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    filename = os.path.basename(src_path)
    dst_path = os.path.join(PUBLIC_DIR, filename)
    shutil.copy(src_path, dst_path)
    url_path = f"/local/zalo_bot/{filename}"
    _LOGGER.info("Đã copy ảnh từ %s đến %s, URL truy cập: %s", src_path, dst_path, url_path)
    return url_path


async def async_setup(hass, config):
    return True


async def async_setup_entry(hass, entry):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    session = requests.Session()
    zalo_server = entry.data["zalo_server"]
    admin_user = entry.data[CONF_USERNAME]
    admin_pass = entry.data[CONF_PASSWORD]

    def zalo_login():
        resp = session.post(f"{zalo_server}/api/login", json={
            "username": admin_user,
            "password": admin_pass
        })
        if resp.status_code == 200 and resp.json().get("success"):
            _LOGGER.info("Zalo admin login success")
        else:
            _LOGGER.error("Zalo admin login failed: %s", resp.text)

    async def handle_webhook(hass, webhook_id, request):
        data = await request.json()
        hass.states.async_set("sensor.zalo_last_message", str(data))
        return {}
    try:
        webhook.async_unregister(hass, WEBHOOK_ID)
    except Exception:
        pass
    webhook.async_register(
        hass, DOMAIN, "Zalo Bot Webhook", WEBHOOK_ID, handle_webhook
    )

    SERVICE_SEND_MESSAGE_SCHEMA = vol.Schema({
        vol.Required("message"): str,
        vol.Required("thread_id"): str,
        vol.Required("account_selection"): str,
        vol.Optional("type", default=0): int,
    })
    SERVICE_SEND_IMAGE_SCHEMA = vol.Schema({
        vol.Required("image_path"): str,
        vol.Required("thread_id"): str,
        vol.Required("account_selection"): str,
        vol.Optional("type", default=0): int,
    })

    async def async_send_message_service(call):
        _LOGGER.debug("ZaloBot async_send_message_service called with data: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            msg_type = call.data.get("type", 0)
            # Sửa lại type: nếu là group thì dùng 1 (số), nếu là user thì 0
            payload = {
                "message": call.data["message"],
                "threadId": call.data["thread_id"],
                "accountSelection": call.data["account_selection"],
                "type": 1 if msg_type == 1 or str(msg_type) == "1" else 0
            }
            _LOGGER.debug("Sending POST to %s/api/sendMessageByAccount with payload: %s",
                          zalo_server, payload)
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/sendMessageByAccount", json=payload)
            )
            _LOGGER.info("Send message resp: %s", resp.text)
        except Exception as e:
            _LOGGER.error("Exception in async_send_message_service: %s", e, exc_info=True)

    async def async_send_image_service(call):
        _LOGGER.debug("ZaloBot async_send_image_service called with data: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            msg_type = call.data.get("type", 0)
            image_path = call.data["image_path"]
            if image_path.startswith("http://") or image_path.startswith("https://"):
                public_url = image_path
            else:
                public_url = await hass.async_add_executor_job(copy_to_public, image_path, zalo_server)
                if not public_url:
                    _LOGGER.error("Failed to copy image to public folder")
                    return
                if public_url.startswith("/local/"):
                    filename = os.path.basename(image_path)
                    public_url = f"{zalo_server}/{filename}"
                    _LOGGER.debug("Converted local path to Zalo server URL: %s", public_url)
            payload = {
                "imagePath": public_url,
                "threadId": call.data["thread_id"],
                "accountSelection": call.data["account_selection"],
                "type": "group" if msg_type == 1 or str(msg_type) == "1" else "user"
            }
            _LOGGER.debug("Sending POST to %s/api/sendImageByAccount with payload: %s",
                          zalo_server, payload)
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/sendImageByAccount", json=payload)
            )
            _LOGGER.info("Send image resp: %s", resp.text)
        except Exception as e:
            _LOGGER.error("Exception in async_send_image_service: %s", e, exc_info=True)
    hass.services.async_register(
        DOMAIN, "send_message", async_send_message_service, schema=SERVICE_SEND_MESSAGE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "send_image", async_send_image_service, schema=SERVICE_SEND_IMAGE_SCHEMA
    )
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, "zalo_bot")},
        manufacturer="Smarthome Black",
        name="Zalo Bot",
        model="Zalo Bot",
        sw_version="2025.7.11"
    )
    return True


async def async_unload_entry(hass, entry):
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
