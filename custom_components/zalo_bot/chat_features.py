"""Các tính năng gửi tin nhắn, file, hình ảnh và video cho Zalo Bot."""
import logging
import os
import asyncio
from .file_handling import serve_file_temporarily, copy_to_public, get_video_duration_ms
from .file_handling import serve_file_temporarily, get_video_duration_ms, copy_to_public
from .notification import show_result_notification

_LOGGER = logging.getLogger(__name__)

# Biến toàn cục
session = None
zalo_server = None

def set_globals(sess, server):
    """Cập nhật các biến toàn cục."""
    global session, zalo_server
    session = sess
    zalo_server = server

async def async_send_message_service(hass, call, zalo_login):
    """Dịch vụ gửi tin nhắn văn bản."""
    _LOGGER.debug("Dịch vụ async_send_message_service được gọi với dữ liệu: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        msg_type = call.data.get("type", "0")
        
        quote = call.data.get("quote")
        if quote and isinstance(quote, dict):
            import time
            quote["cliMsgId"] = str(int(time.time() * 1000))
        payload = {
            "message": {
                "msg": call.data["message"],
                "ttl": call.data.get("ttl", 0),
                "quote": quote
            },
            "threadId": call.data["thread_id"],
            "accountSelection": call.data["account_selection"],
            "type": 1 if msg_type == "1" else 0
        }
        _LOGGER.debug("Gửi POST đến %s/api/sendMessageByAccount với payload: %s",
                    zalo_server, payload)
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/sendMessageByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi gửi tin nhắn: %s", resp.text)
        await show_result_notification(hass, "gửi tin nhắn", resp)
        try:
            return resp.json()
        except:
            return {"text": resp.text}

    except Exception as e:
        _LOGGER.error("Exception trong async_send_message_service: %s", e, exc_info=True)
        await show_result_notification(hass, "gửi tin nhắn", None, error=e)
        return {"error": str(e)}

async def async_send_file_service(hass, call, zalo_login):
    """Dịch vụ gửi file."""
    _LOGGER.debug("Dịch vụ async_send_file_service được gọi với dữ liệu: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        msg_type = call.data.get("type", "0")
        file_path = call.data["file_path_or_url"]
        public_url = None
        if file_path.startswith("http://") or file_path.startswith("https://"):
            public_url = file_path
        else:
            if not os.path.isfile(file_path):
                error_msg = f"Không tìm thấy tệp: {file_path}"
                await show_result_notification(hass, "gửi file", None, error=error_msg)
                return
            try:
                is_local_server = ("localhost" in zalo_server or "127.0.0.1" in zalo_server)
                if is_local_server:
                    public_url = await hass.async_add_executor_job(copy_to_public, file_path, zalo_server)
                    if not public_url:
                        error_msg = "Không thể copy tệp đến thư mục public"
                        await show_result_notification(hass, "gửi file", None, error=error_msg)
                        return
                    if public_url.startswith("/local/"):
                        filename = os.path.basename(file_path)
                        public_url = f"{zalo_server}/{filename}"
                else:
                    _LOGGER.info(f"Sử dụng máy chủ HTTP tạm thời để phục vụ tệp: {file_path}")
                    public_url = await hass.async_add_executor_job(
                        serve_file_temporarily, file_path, 90
                    )
            except Exception as e:
                error_msg = f"Lỗi khi xử lý tệp: {str(e)}"
                _LOGGER.error(error_msg)
                await show_result_notification(hass, "gửi file", None, error=error_msg)
                return
        if not public_url:
            await show_result_notification(hass, "gửi file", None, error="Không thể tạo URL công khai cho tệp.")
            return
        payload = {
            "fileUrl": public_url,
            "message": call.data.get("message", ""),
            "threadId": call.data["thread_id"],
            "accountSelection": call.data["account_selection"],
            "type": "group" if msg_type == "1" else "user",
            "ttl": call.data.get("ttl", 0)
        }
        _LOGGER.debug("Gửi POST đến %s/api/sendFileByAccount với payload: %s",
                    zalo_server, payload)
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/sendFileByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi gửi file: %s", resp.text)
        await show_result_notification(hass, "gửi file", resp)
        try:
            return resp.json()
        except:
            return {"text": resp.text}
    except Exception as e:
        _LOGGER.error("Exception trong async_send_file_service: %s", e, exc_info=True)
        await show_result_notification(hass, "gửi file", None, error=e)
        return {"error": str(e)}

async def async_send_image_service(hass, call, zalo_login):
    """Dịch vụ gửi hình ảnh."""
    _LOGGER.debug("Dịch vụ async_send_image_service được gọi với dữ liệu: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        msg_type = call.data.get("type", "0")
        image_path = call.data["image_path"]

        if image_path.startswith("http://") or image_path.startswith("https://"):
            public_url = image_path
        else:
            if not os.path.isfile(image_path):
                error_msg = f"Không tìm thấy tệp ảnh: {image_path}"
                await show_result_notification(hass, "gửi ảnh", None, error=error_msg)
                return
            try:
                is_local_server = ("localhost" in zalo_server or "127.0.0.1" in zalo_server)
                if is_local_server:
                    public_url = await hass.async_add_executor_job(copy_to_public, image_path, zalo_server)
                    if not public_url:
                        error_msg = "Không thể copy ảnh đến thư mục public"
                        await show_result_notification(hass, "gửi ảnh", None, error=error_msg)
                        return
                    if public_url.startswith("/local/"):
                        filename = os.path.basename(image_path)
                        public_url = f"{zalo_server}/{filename}"
                else:
                    _LOGGER.info(f"Sử dụng máy chủ HTTP tạm thời để phục vụ ảnh: {image_path}")
                    public_url = await hass.async_add_executor_job(
                        serve_file_temporarily, image_path, 90
                    )
            except Exception as e:
                error_msg = f"Lỗi khi xử lý ảnh: {str(e)}"
                _LOGGER.error(error_msg)
                await show_result_notification(hass, "gửi ảnh", None, error=error_msg)
                return
        payload = {
            "imagePath": public_url,
            "threadId": call.data["thread_id"],
            "accountSelection": call.data["account_selection"],
            "type": "group" if msg_type == "1" else "user",
            "ttl": call.data.get("ttl", 0),
            "message": call.data.get("message", "") 
        }
        _LOGGER.debug("Gửi POST đến %s/api/sendImageByAccount với payload: %s",
                    zalo_server, payload)
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/sendImageByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi gửi ảnh: %s", resp.text)
        await show_result_notification(hass, "gửi ảnh", resp)
        try:
            return resp.json()
        except:
            return {"text": resp.text}
    except Exception as e:
        _LOGGER.error("Exception trong async_send_image_service: %s", e, exc_info=True)
        await show_result_notification(hass, "gửi ảnh", None, error=e)
        return {"error": str(e)}

async def async_send_video_service(hass, call, zalo_login):
    """Dịch vụ gửi video."""
    _LOGGER.debug("Dịch vụ async_send_video được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        msg_type = call.data.get("type", "0")
        video_path = call.data["video_path_or_url"]
        public_url = None
        if video_path.startswith("http://") or video_path.startswith("https://"):
            public_url = video_path
        else:
            if not os.path.isfile(video_path):
                error_msg = f"Không tìm thấy tệp video: {video_path}"
                await show_result_notification(hass, "gửi video", None, error=error_msg)
                return
            try:
                _LOGGER.info(f"Sử dụng máy chủ HTTP tạm thời để phục vụ tệp video: {video_path}")
                public_url = await hass.async_add_executor_job(
                    serve_file_temporarily, video_path, 90
                )
            except Exception as e:
                error_msg = f"Lỗi khi xử lý tệp video: {str(e)}"
                _LOGGER.error(error_msg)
                await show_result_notification(hass, "gửi video", None, error=error_msg)
                return
        if not public_url:
            await show_result_notification(hass, "gửi video", None, error="Không thể tạo URL công khai cho video.")
            return
        thumbnail_url = call.data.get("thumbnail_url", public_url)
        if thumbnail_url and not (thumbnail_url.startswith("http://") or thumbnail_url.startswith("https://")):

            if os.path.isfile(thumbnail_url):
                try:
                    thumbnail_url = await hass.async_add_executor_job(
                        serve_file_temporarily, thumbnail_url, 90
                    )
                except Exception as e:
                    _LOGGER.warning("Không thể xử lý thumbnail file local: %s, dùng URL video làm thumbnail", e)
                    thumbnail_url = public_url
            else:
                _LOGGER.warning("Không tìm thấy thumbnail file: %s, dùng URL video làm thumbnail", thumbnail_url)
                thumbnail_url = public_url

        if video_path.startswith("http://") or video_path.startswith("https://"):
            duration = 10000
        else:
            try:
                duration = get_video_duration_ms(video_path)
                _LOGGER.info(f"Auto-detect video duration: {duration}ms từ file {video_path}")
            except Exception as e:
                _LOGGER.warning(f"Không thể auto-detect duration từ {video_path}: {e}, dùng 10000ms")
                duration = 10000
        options = {
            "videoUrl": public_url,
            "thumbnailUrl": thumbnail_url,
            "msg": call.data.get("message", ""),
            "duration": int(duration),
            "width": int(call.data.get("width", 1280)),
            "height": int(call.data.get("height", 720)),
            "ttl": int(call.data.get("ttl", 0))
        }
        thread_type_num = 1 if msg_type == "1" else 0
        payload = {
            "threadId": str(call.data["thread_id"]),
            "accountSelection": str(call.data["account_selection"]),
            "options": options,
            "type": thread_type_num 
        }
        _LOGGER.info("Video URL để gửi: %s", public_url)
        _LOGGER.info("Thumbnail URL để gửi: %s", thumbnail_url)
        try:
            await asyncio.sleep(0.1)
            test_resp = await hass.async_add_executor_job(
                lambda: session.head(public_url, timeout=10)
            )
            _LOGGER.info("Test video URL accessibility - Status: %s, Headers: %s",
                            test_resp.status_code, dict(test_resp.headers))
            if test_resp.status_code != 200:
                _LOGGER.warning("Video URL không accessible từ backend: %s", test_resp.status_code)
                try:
                    test_resp_get = await hass.async_add_executor_job(
                        lambda: session.get(public_url, timeout=10, stream=True)
                    )
                    _LOGGER.info("Test video URL với GET - Status: %s", test_resp_get.status_code)
                    test_resp_get.close()
                except Exception as get_error:
                    _LOGGER.error("GET test cũng thất bại: %s", get_error)
        except Exception as e:
            _LOGGER.error("Không thể test video URL accessibility: %s", e)
        _LOGGER.debug("Options đầy đủ: %s", options)
        _LOGGER.debug("Gửi payload đến sendVideoByAccount: %s", payload)
        url = f"{zalo_server}/api/sendVideoByAccount"
        _LOGGER.debug("URL đầy đủ: %s", url)
        resp = await hass.async_add_executor_job(
            lambda: session.post(url, json=payload)
        )
        _LOGGER.info("Response status: %s", resp.status_code)
        _LOGGER.info("Response headers: %s", dict(resp.headers))
        _LOGGER.info("Response text: %s", resp.text)
        try:
            response_json = resp.json()
            _LOGGER.info("Response JSON: %s", response_json)
            if not response_json.get('success', False):
                error_detail = response_json.get('error', 'Unknown error')
                _LOGGER.error("Backend trả về lỗi: %s", error_detail)
        except Exception as json_error:
            _LOGGER.error("Không thể parse JSON response: %s", json_error)
        await show_result_notification(hass, "gửi video", resp)
        try:
            return resp.json()
        except:
            return {"text": resp.text}
    except Exception as e:
        _LOGGER.error("Lỗi trong async_send_video: %s", e)
        await show_result_notification(hass, "gửi video", None, error=e)
        return {"error": str(e)}

async def async_send_sticker_service(hass, call, zalo_login):
    """Dịch vụ gửi sticker."""
    _LOGGER.debug("Dịch vụ async_send_sticker được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        msg_type = call.data.get("type", "0")
        sticker_id = int(call.data["sticker_id"])
        sticker = {
            "id": sticker_id,
            "cateId": 526,
            "type": 1
        }
        payload = {
            "accountSelection": call.data["account_selection"],
            "threadId": call.data["thread_id"],
            "sticker": sticker,
            "type": 1 if msg_type == "1" else 0
        }
        _LOGGER.debug("Gửi payload đến sendStickerByAccount: %s", payload)
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/sendStickerByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi gửi sticker: %s", resp.text)
        await show_result_notification(hass, "gửi sticker", resp)
        try:
            return resp.json()
        except:
            return {"text": resp.text}
    except Exception as e:
        _LOGGER.error("Lỗi trong async_send_sticker: %s", e)
        await show_result_notification(hass, "gửi sticker", None, error=e)
        return {"error": str(e)}

async def async_send_voice_service(hass, call, zalo_login):
    """Dịch vụ gửi tin nhắn thoại."""
    _LOGGER.debug("Dịch vụ async_send_voice được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        voice_path = call.data["voice_path"]
        voice_url = voice_path
        local_server = None
        if not voice_path.startswith(("http://", "https://")):
            if os.path.isfile(voice_path):
                voice_url, local_server = await hass.async_add_executor_job(
                    serve_file_temporarily, voice_path
                )
            else:
                raise Exception(f"Không tìm thấy file âm thanh: {voice_path}")
        try:
            payload = {
                "threadId": call.data["thread_id"],
                "accountSelection": call.data["account_selection"],
                "options": {
                    "voiceUrl": voice_url
                }
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/sendVoiceByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi gửi tin nhắn thoại: %s", resp.text)
            await show_result_notification(hass, "gửi tin nhắn thoại", resp)
            try:
              return resp.json()
            except:
              return {"text": resp.text}
        finally:
            if local_server:
                local_server.shutdown()
                local_server.server_close()
    except Exception as e:
        _LOGGER.error("Lỗi trong async_send_voice: %s", e)
        await show_result_notification(hass, "gửi tin nhắn thoại", None, error=e)
        return {"error": str(e)}

async def async_send_typing_event_service(hass, call, zalo_login):
    """Dịch vụ gửi thông báo đang nhập tin nhắn."""
    _LOGGER.debug("Dịch vụ async_send_typing_event được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        payload = {
            "threadId": call.data["thread_id"],
            "accountSelection": call.data["account_selection"]
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/sendTypingEventByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi gửi thông báo typing: %s", resp.text)
        await show_result_notification(hass, "gửi thông báo typing", resp)
        try:
            return resp.json()
        except:
            return {"text": resp.text}
    except Exception as e:
        _LOGGER.error("Lỗi trong async_send_typing_event: %s", e)
        await show_result_notification(hass, "gửi thông báo typing", None, error=e)
        return {"error": str(e)}

async def async_send_image_to_user_service(hass, call, zalo_login):
    """Dịch vụ gửi ảnh cho người dùng."""
    _LOGGER.debug("Dịch vụ async_send_image_to_user được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        image_path = call.data["image_path"]

        if image_path.startswith("http"):
            public_url = image_path
        else:
            if not os.path.isfile(image_path):
                error_msg = f"Không tìm thấy tệp ảnh: {image_path}"
                await show_result_notification(hass, "gửi ảnh cho người dùng", None, error=error_msg)
                return
            try:
                is_local_server = ("localhost" in zalo_server or "127.0.0.1" in zalo_server)
                if is_local_server:
                    public_url = await hass.async_add_executor_job(copy_to_public, image_path, zalo_server)
                    if not public_url:
                        error_msg = "Không thể copy ảnh đến thư mục public"
                        await show_result_notification(hass, "gửi ảnh cho người dùng", None, error=error_msg)
                        return
                    if public_url.startswith("/local/"):
                        public_url = f"{zalo_server}{public_url.replace('/local', '')}"
                else:
                    _LOGGER.info(f"Sử dụng máy chủ HTTP tạm thời để phục vụ ảnh: {image_path}")
                    public_url = await hass.async_add_executor_job(
                        serve_file_temporarily, image_path, 90  # 90 giây là đủ để gửi
                    )
            except Exception as e:
                error_msg = f"Lỗi khi xử lý ảnh: {str(e)}"
                _LOGGER.error(error_msg)
                await show_result_notification(hass, "gửi ảnh cho người dùng", None, error=error_msg)
                return
        payload = {
            "imagePath": public_url,
            "threadId": call.data["thread_id"],
            "accountSelection": call.data["account_selection"]
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/sendImageToUserByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi gửi ảnh cho người dùng: %s", resp.text)
        await show_result_notification(hass, "gửi ảnh cho người dùng", resp)
        try:
            return resp.json()
        except:
            return {"text": resp.text}

    except Exception as e:
        _LOGGER.error("Lỗi trong async_send_image_to_user: %s", e)
        await show_result_notification(hass, "gửi ảnh cho người dùng", None, error=str(e))
        return {"error": str(e)}

async def async_send_image_to_group_service(hass, call, zalo_login):
    """Dịch vụ gửi ảnh cho nhóm."""
    _LOGGER.debug("Dịch vụ async_send_image_to_group được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        image_path = call.data["image_path"]
        if image_path.startswith("http"):
            public_url = image_path
        else:
            if not os.path.isfile(image_path):
                error_msg = f"Không tìm thấy tệp ảnh: {image_path}"
                await show_result_notification(hass, "gửi ảnh cho nhóm", None, error=error_msg)
                return
            try:
                is_local_server = ("localhost" in zalo_server or "127.0.0.1" in zalo_server)
                if is_local_server:
                    public_url = await hass.async_add_executor_job(copy_to_public, image_path, zalo_server)
                    if not public_url:
                        error_msg = "Không thể copy ảnh đến thư mục public"
                        await show_result_notification(hass, "gửi ảnh cho nhóm", None, error=error_msg)
                        return
                    if public_url.startswith("/local/"):
                        public_url = f"{zalo_server}{public_url.replace('/local', '')}"
                else:
                    _LOGGER.info(f"Sử dụng máy chủ HTTP tạm thời để phục vụ ảnh: {image_path}")
                    public_url = await hass.async_add_executor_job(
                        serve_file_temporarily, image_path, 90  # 90 giây là đủ để gửi
                    )
            except Exception as e:
                error_msg = f"Lỗi khi xử lý ảnh: {str(e)}"
                _LOGGER.error(error_msg)
                await show_result_notification(hass, "gửi ảnh cho nhóm", None, error=error_msg)
                return
        payload = {
            "imagePath": public_url,
            "threadId": call.data["thread_id"],
            "accountSelection": call.data["account_selection"]
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/sendImageToGroupByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi gửi ảnh cho nhóm: %s", resp.text)
        await show_result_notification(hass, "gửi ảnh cho nhóm", resp)
        try:
            return resp.json()
        except:
            return {"text": resp.text}
    except Exception as e:
        _LOGGER.error("Lỗi trong async_send_image_to_group: %s", e)
        await show_result_notification(hass, "gửi ảnh cho nhóm", None, error=str(e))
        return {"error": str(e)}

async def async_send_images_to_user_service(hass, call, zalo_login):
    """Dịch vụ gửi nhiều ảnh cho người dùng."""
    _LOGGER.debug("Dịch vụ async_send_images_to_user được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        image_paths = call.data["image_paths"].split(",")
        processed_paths = []
        is_local_server = ("localhost" in zalo_server or "127.0.0.1" in zalo_server)
        for img in image_paths:
            img = img.strip()
            if img.startswith("http"):
                processed_paths.append(img)
            else:
                if not os.path.isfile(img):
                    _LOGGER.warning(f"Không tìm thấy tệp ảnh: {img}, bỏ qua")
                    continue
                try:
                    if is_local_server:
                        public_url = await hass.async_add_executor_job(copy_to_public, img, zalo_server)
                        if public_url:
                            if public_url.startswith("/local/"):
                                fixed_url = f"{zalo_server}{public_url.replace('/local', '')}"
                                processed_paths.append(fixed_url)
                        else:
                            _LOGGER.warning(f"Không thể copy ảnh: {img}, bỏ qua")
                    else:
                        _LOGGER.info(f"Sử dụng máy chủ HTTP tạm thời để phục vụ ảnh: {img}")
                        public_url = await hass.async_add_executor_job(
                            serve_file_temporarily, img, 120  # 120 giây cho nhiều ảnh
                        )
                        processed_paths.append(public_url)
                except Exception as e:
                    _LOGGER.error(f"Lỗi khi xử lý ảnh {img}: {str(e)}")
                    continue
        if not processed_paths:
            error_msg = "Không có ảnh nào được xử lý thành công"
            await show_result_notification(hass, "gửi nhiều ảnh cho người dùng", None, error=error_msg)
            return
        payload = {
            "imagePaths": processed_paths,
            "threadId": call.data["thread_id"],
            "accountSelection": call.data["account_selection"]
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/sendImagesToUserByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi gửi nhiều ảnh cho người dùng: %s", resp.text)
        await show_result_notification(hass, "gửi nhiều ảnh cho người dùng", resp)
        try:
            return resp.json()
        except:
            return {"text": resp.text}
    except Exception as e:
        _LOGGER.error("Lỗi trong async_send_images_to_user: %s", e)
        await show_result_notification(
            hass,
            "gửi nhiều ảnh cho người dùng",
            None,
            error=str(e)
        )
        return {"error": str(e)}

async def async_send_images_to_group_service(hass, call, zalo_login):
    """Dịch vụ gửi nhiều ảnh cho nhóm."""
    _LOGGER.debug("Dịch vụ async_send_images_to_group được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        image_paths = call.data["image_paths"].split(",")
        processed_paths = []
        is_local_server = ("localhost" in zalo_server or "127.0.0.1" in zalo_server)
        for img in image_paths:
            img = img.strip()
            if img.startswith("http"):
                processed_paths.append(img)
            else:
                if not os.path.isfile(img):
                    _LOGGER.warning(f"Không tìm thấy tệp ảnh: {img}, bỏ qua")
                    continue
                try:
                    if is_local_server:
                        public_url = await hass.async_add_executor_job(copy_to_public, img, zalo_server)
                        if public_url:
                            if public_url.startswith("/local/"):
                                fixed_url = f"{zalo_server}{public_url.replace('/local', '')}"
                                processed_paths.append(fixed_url)
                        else:
                            _LOGGER.warning(f"Không thể copy ảnh: {img}, bỏ qua")
                    else:
                        _LOGGER.info(f"Sử dụng máy chủ HTTP tạm thời để phục vụ ảnh: {img}")
                        public_url = await hass.async_add_executor_job(
                            serve_file_temporarily, img, 120
                        )
                        processed_paths.append(public_url)
                except Exception as e:
                    _LOGGER.error(f"Lỗi khi xử lý ảnh {img}: {str(e)}")
                    continue
        if not processed_paths:
            error_msg = "Không có ảnh nào được xử lý thành công"
            await show_result_notification(hass, "gửi nhiều ảnh cho nhóm", None, error=error_msg)
            return
        payload = {
            "imagePaths": processed_paths,
            "threadId": call.data["thread_id"],
            "accountSelection": call.data["account_selection"]
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/sendImagesToGroupByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi gửi nhiều ảnh cho nhóm: %s", resp.text)
        await show_result_notification(hass, "gửi nhiều ảnh cho nhóm", resp)
        try:
            return resp.json()
        except:
            return {"text": resp.text}

    except Exception as e:
        _LOGGER.error("Lỗi trong async_send_images_to_group: %s", e)
        await show_result_notification(hass, "gửi nhiều ảnh cho nhóm", None, error=str(e))
        return {"error": str(e)}
