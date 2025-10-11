"""
Module xử lý service get_login_qr cho Zalo Bot.
"""
import logging

_LOGGER = logging.getLogger(__name__)

session = None
zalo_server = None

def set_globals(sess, server):
    global session, zalo_server
    session = sess
    zalo_server = server

async def async_get_login_qr(hass, call, zalo_login):
    """
    Service: get_login_qr
    Lấy mã QR đăng nhập Zalo và hiển thị lên persistent_notification.
    """
    try:
        await hass.async_add_executor_job(zalo_login)
        url = f"{zalo_server}/zalo-login"
        resp = await hass.async_add_executor_job(session.post, url)
        data = resp.json()
        qr_data = data.get("qrCodeImage")
        if qr_data and qr_data.startswith("data:image"):
            message = f"<b>Quét mã QR để đăng nhập Zalo:</b><br><img src=\"{qr_data}\" width=300>"
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "message": message,
                    "title": "Zalo Bot - Đăng nhập Zalo",
                    "notification_id": f"zalo_bot_login_qr"
                }
            )
            _LOGGER.info("Đã lấy và hiển thị mã QR đăng nhập Zalo thành công.")
        else:
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "message": "Không lấy được mã QR đăng nhập!",
                    "title": "Zalo Bot - Lỗi đăng nhập",
                    "notification_id": f"zalo_bot_login_qr_error"
                }
            )
            _LOGGER.error("Không lấy được mã QR đăng nhập!")
    except Exception as e:
        await hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "message": f"Lỗi khi lấy mã QR: {str(e)}",
                "title": "Zalo Bot - Lỗi đăng nhập",
                "notification_id": f"zalo_bot_login_qr_error"
            }
        )
        _LOGGER.error("Lỗi khi lấy mã QR: %s", e)