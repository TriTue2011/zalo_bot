"""Các tính năng liên quan đến reminder (nhắc nhở) cho Zalo Bot."""
import logging
from .notification import show_result_notification

_LOGGER = logging.getLogger(__name__)

# Biến toàn cục để lưu trữ các thông tin cần thiết
session = None
zalo_server = None

def set_globals(sess, server):
    """Cập nhật các biến toàn cục."""
    global session, zalo_server
    session = sess
    zalo_server = server

async def async_edit_reminder_service(hass, call, zalo_login):
    """Sửa lời nhắc."""
    _LOGGER.debug("Dịch vụ async_edit_reminder được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        payload = {
            "threadId": call.data["thread_id"],
            "accountSelection": call.data["account_selection"],
            "options": {
                "topicId": call.data["topic_id"],
                "title": call.data["title"]
            }
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/editReminderByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi sửa lời nhắc: %s", resp.text)
        await show_result_notification(hass, "sửa lời nhắc", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_edit_reminder: %s", e)
        await show_result_notification(hass, "sửa lời nhắc", None, error=e)

async def async_get_reminder_service(hass, call, zalo_login):
    """Lấy thông tin nhắc hẹn."""
    _LOGGER.debug("Dịch vụ async_get_reminder được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        payload = {
            "accountSelection": call.data["account_selection"],
            "reminderId": call.data["reminder_id"]
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/getReminderByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi lấy thông tin nhắc hẹn: %s", resp.text)
        await show_result_notification(hass, "lấy thông tin nhắc hẹn", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_get_reminder: %s", e)
        await show_result_notification(hass, "lấy thông tin nhắc hẹn", None, error=e)

async def async_get_list_reminder_service(hass, call, zalo_login):
    """Lấy danh sách lời nhắc."""
    _LOGGER.debug("Dịch vụ async_get_list_reminder được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)

        # Chuyển đổi type từ chuỗi sang số (0 cho user, 1 cho group)
        reminder_type = call.data.get("type", "0")
        reminder_type_num = 1 if reminder_type.lower() == "group" else 0

        payload = {
            "accountSelection": call.data["account_selection"],
            "threadId": call.data["thread_id"],
            "type": reminder_type_num
        }

        # Thêm options nếu có
        if "options" in call.data:
            payload["options"] = call.data["options"]

        _LOGGER.debug("Gửi payload đến getListReminderByAccount: %s", payload)
        url = f"{zalo_server}/api/getListReminderByAccount"
        _LOGGER.debug("URL đầy đủ: %s", url)

        resp = await hass.async_add_executor_job(
            lambda: session.post(url, json=payload)
        )
        _LOGGER.info("Phản hồi lấy danh sách lời nhắc: %s", resp.text)
        await show_result_notification(hass, "lấy danh sách lời nhắc", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_get_list_reminder: %s", e)
        await show_result_notification(hass, "lấy danh sách lời nhắc", None, error=e)

async def async_get_reminder_responses_service(hass, call, zalo_login):
    """Lấy danh sách phản hồi nhắc hẹn."""
    _LOGGER.debug("Dịch vụ async_get_reminder_responses được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        payload = {
            "accountSelection": call.data["account_selection"],
            "reminderId": call.data["reminder_id"]
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/getReminderResponsesByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi lấy danh sách phản hồi nhắc hẹn: %s", resp.text)
        await show_result_notification(hass, "lấy danh sách phản hồi nhắc hẹn", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_get_reminder_responses: %s", e)
        await show_result_notification(hass, "lấy danh sách phản hồi nhắc hẹn", None, error=e)
