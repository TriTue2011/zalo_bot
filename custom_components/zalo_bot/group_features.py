"""Các tính năng quản lý nhóm cho Zalo Bot."""
import logging
import os
from .file_handling import serve_file_temporarily, copy_to_public
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

async def async_create_group_service(hass, call, zalo_login):
    """Dịch vụ tạo nhóm mới."""
    _LOGGER.debug("Dịch vụ async_create_group được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        
        # Xử lý danh sách thành viên giống file gốc
        members_list = call.data["members"].split(",") if call.data["members"] else []
        
        # Tạo payload giống hệt file gốc
        payload = {
            "members": members_list,
            "name": call.data.get("name"),
            "avatarPath": call.data.get("avatar_path"),
            "accountSelection": call.data["account_selection"]
        }
        
        _LOGGER.debug("Gửi payload đến createGroupByAccount: %s", payload)
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/createGroupByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi tạo nhóm: %s", resp.text)
        await show_result_notification(hass, "tạo nhóm", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_create_group: %s", e)
        await show_result_notification(hass, "tạo nhóm", None, error=e)

async def async_get_group_info_service(hass, call, zalo_login):
    """Dịch vụ lấy thông tin nhóm."""
    _LOGGER.debug("Dịch vụ async_get_group_info được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        # Logic xử lý giống file gốc
        group_id = call.data.get("group_id", "")
        account_selection = call.data.get("account_selection", "") or "default"  # Logic mặc định
        group_id_list = (
            group_id.split(",") if group_id else []
        )
        payload = {
            "groupId": group_id_list,
            "accountSelection": account_selection
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/getGroupInfoByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi lấy thông tin nhóm: %s", resp.text)
        await show_result_notification(hass, "lấy thông tin nhóm", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_get_group_info: %s", e)
        await show_result_notification(hass, "lấy thông tin nhóm", None, error=e)

async def async_add_user_to_group_service(hass, call, zalo_login):
    """Dịch vụ thêm người dùng vào nhóm."""
    _LOGGER.debug("Dịch vụ async_add_user_to_group được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        
        # Xử lý member_id_list: luôn trả về list, kể cả khi chỉ có 1 ID
        member_id_list = (
            call.data["member_id"].split(",")
            if "," in call.data["member_id"]
            else [call.data["member_id"]]
        )
        
        payload = {
            "groupId": call.data["group_id"],
            "memberId": member_id_list,
            "accountSelection": call.data["account_selection"]
        }
        
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/addUserToGroupByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi thêm người dùng vào nhóm: %s", resp.text)
        await show_result_notification(hass, "thêm người dùng vào nhóm", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_add_user_to_group: %s", e)
        await show_result_notification(hass, "thêm người dùng vào nhóm", None, error=e)

async def async_remove_user_from_group_service(hass, call, zalo_login):
    """Dịch vụ xóa người dùng khỏi nhóm."""
    _LOGGER.debug("Dịch vụ async_remove_user_from_group được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        
        # Xử lý member_id_list: luôn trả về list, kể cả khi chỉ có 1 ID
        member_id_list = (
            call.data["member_id"].split(",")
            if "," in call.data["member_id"]
            else [call.data["member_id"]]
        )
        
        payload = {
            "groupId": call.data["group_id"],
            "memberId": member_id_list,
            "accountSelection": call.data["account_selection"]
        }
        
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/removeUserFromGroupByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi xóa người dùng khỏi nhóm: %s", resp.text)
        await show_result_notification(hass, "xóa người dùng khỏi nhóm", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_remove_user_from_group: %s", e)
        await show_result_notification(hass, "xóa người dùng khỏi nhóm", None, error=e)

async def async_change_group_name_service(hass, call, zalo_login):
    """Dịch vụ đổi tên nhóm."""
    _LOGGER.debug("Dịch vụ async_change_group_name được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        payload = {
            "accountSelection": call.data["account_selection"],
            "groupId": call.data["group_id"],
            "name": call.data["name"]
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/changeGroupNameByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi đổi tên nhóm: %s", resp.text)
        await show_result_notification(hass, "đổi tên nhóm", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_change_group_name: %s", e)
        await show_result_notification(hass, "đổi tên nhóm", None, error=e)

async def async_change_group_avatar_service(hass, call, zalo_login):
    """Dịch vụ đổi ảnh đại diện nhóm."""
    _LOGGER.debug("Dịch vụ async_change_group_avatar được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        
        # Trong API mới phải dùng imagePath thay vì avatar_path
        image_path = call.data["image_path"] if "image_path" in call.data else call.data["avatar_path"]
        
        if image_path.startswith("http"):
            public_url = image_path
        else:
            # Kiểm tra tệp tồn tại
            if not os.path.isfile(image_path):
                error_msg = f"Không tìm thấy tệp ảnh: {image_path}"
                await show_result_notification(hass, "đổi ảnh đại diện nhóm", None, error=error_msg)
                return

            # Thử copy vào thư mục public hoặc sử dụng máy chủ tạm thời
            try:
                # Kiểm tra nếu zalo_server chạy trên cùng máy (localhost)
                is_local_server = ("localhost" in zalo_server or "127.0.0.1" in zalo_server)

                if is_local_server:
                    # Sử dụng phương pháp cũ khi server chạy cùng máy
                    public_url = await hass.async_add_executor_job(copy_to_public, image_path, zalo_server)
                    if not public_url:
                        error_msg = "Không thể copy ảnh đến thư mục public"
                        await show_result_notification(hass, "đổi ảnh đại diện nhóm", None, error=error_msg)
                        return

                    if public_url.startswith("/local/"):
                        public_url = f"{zalo_server}{public_url.replace('/local', '')}"
                else:
                    # Sử dụng máy chủ HTTP tạm thời khi server chạy trên máy khác
                    _LOGGER.info(f"Sử dụng máy chủ HTTP tạm thời để phục vụ ảnh: {image_path}")
                    public_url = await hass.async_add_executor_job(
                        serve_file_temporarily, image_path, 90  # 90 giây là đủ để gửi
                    )
            except Exception as e:
                error_msg = f"Lỗi khi xử lý ảnh: {str(e)}"
                _LOGGER.error(error_msg)
                await show_result_notification(hass, "đổi ảnh đại diện nhóm", None, error=error_msg)
                return
        
        payload = {
            "groupId": call.data["group_id"],
            "imagePath": public_url,
            "accountSelection": call.data["account_selection"]
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/changeGroupAvatarByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi đổi ảnh đại diện nhóm: %s", resp.text)
        await show_result_notification(hass, "đổi ảnh đại diện nhóm", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_change_group_avatar: %s", e)
        await show_result_notification(hass, "đổi ảnh đại diện nhóm", None, error=e)

async def async_get_all_groups_service(hass, call, zalo_login):
    """Dịch vụ lấy danh sách tất cả các nhóm."""
    _LOGGER.debug("Dịch vụ async_get_all_groups được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        payload = {
            "accountSelection": call.data["account_selection"]
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/getAllGroupsByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi lấy danh sách tất cả các nhóm: %s", resp.text)
        await show_result_notification(hass, "lấy danh sách tất cả các nhóm", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_get_all_groups: %s", e)
        await show_result_notification(hass, "lấy danh sách tất cả các nhóm", None, error=e)

async def async_add_group_deputy_service(hass, call, zalo_login):
    """Dịch vụ thêm phó nhóm."""
    _LOGGER.debug("Dịch vụ async_add_group_deputy được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        # API cần memberId thay vì userId
        member_id = call.data["member_id"] if "member_id" in call.data else call.data["user_id"]
        
        payload = {
            "accountSelection": call.data["account_selection"],
            "groupId": call.data["group_id"],
            "memberId": member_id
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/addGroupDeputyByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi thêm phó nhóm: %s", resp.text)
        await show_result_notification(hass, "thêm phó nhóm", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_add_group_deputy: %s", e)
        await show_result_notification(hass, "thêm phó nhóm", None, error=e)

async def async_remove_group_deputy_service(hass, call, zalo_login):
    """Dịch vụ xóa phó nhóm."""
    _LOGGER.debug("Dịch vụ async_remove_group_deputy được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        # API cần memberId thay vì userId
        member_id = call.data["member_id"] if "member_id" in call.data else call.data["user_id"]
        
        payload = {
            "accountSelection": call.data["account_selection"],
            "groupId": call.data["group_id"],
            "memberId": member_id
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/removeGroupDeputyByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi xóa phó nhóm: %s", resp.text)
        await show_result_notification(hass, "xóa phó nhóm", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_remove_group_deputy: %s", e)
        await show_result_notification(hass, "xóa phó nhóm", None, error=e)

async def async_change_group_owner_service(hass, call, zalo_login):
    """Dịch vụ chuyển quyền trưởng nhóm."""
    _LOGGER.debug("Dịch vụ async_change_group_owner được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        # API cần memberId thay vì userId
        member_id = call.data["member_id"] if "member_id" in call.data else call.data["user_id"]
        
        payload = {
            "accountSelection": call.data["account_selection"],
            "groupId": call.data["group_id"],
            "memberId": member_id
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/changeGroupOwnerByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi chuyển quyền sở hữu nhóm: %s", resp.text)
        await show_result_notification(hass, "chuyển quyền sở hữu nhóm", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_change_group_owner: %s", e)
        await show_result_notification(hass, "chuyển quyền sở hữu nhóm", None, error=e)

async def async_disperse_group_service(hass, call, zalo_login):
    """Dịch vụ giải tán nhóm."""
    _LOGGER.debug("Dịch vụ async_disperse_group được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        payload = {
            "accountSelection": call.data["account_selection"],
            "groupId": call.data["group_id"]
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/disperseGroupByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi giải tán nhóm: %s", resp.text)
        await show_result_notification(hass, "giải tán nhóm", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_disperse_group: %s", e)
        await show_result_notification(hass, "giải tán nhóm", None, error=e)

async def async_enable_group_link_service(hass, call, zalo_login):
    """Dịch vụ bật liên kết nhóm."""
    _LOGGER.debug("Dịch vụ async_enable_group_link được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        payload = {
            "accountSelection": call.data["account_selection"],
            "groupId": call.data["group_id"]
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/enableGroupLinkByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi bật liên kết nhóm: %s", resp.text)
        await show_result_notification(hass, "bật liên kết nhóm", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_enable_group_link: %s", e)
        await show_result_notification(hass, "bật liên kết nhóm", None, error=e)

async def async_disable_group_link_service(hass, call, zalo_login):
    """Dịch vụ tắt liên kết nhóm."""
    _LOGGER.debug("Dịch vụ async_disable_group_link được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        payload = {
            "accountSelection": call.data["account_selection"],
            "groupId": call.data["group_id"]
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/disableGroupLinkByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi tắt liên kết nhóm: %s", resp.text)
        await show_result_notification(hass, "tắt liên kết nhóm", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_disable_group_link: %s", e)
        await show_result_notification(hass, "tắt liên kết nhóm", None, error=e)

async def async_join_group_service(hass, call, zalo_login):
    """Dịch vụ tham gia nhóm."""
    _LOGGER.debug("Dịch vụ async_join_group được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        payload = {
            "accountSelection": call.data["account_selection"],
            "link": call.data["link"]
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/joinGroupByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi tham gia nhóm: %s", resp.text)
        await show_result_notification(hass, "tham gia nhóm", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_join_group: %s", e)
        await show_result_notification(hass, "tham gia nhóm", None, error=e)

async def async_leave_group_service(hass, call, zalo_login):
    """Dịch vụ rời khỏi nhóm."""
    _LOGGER.debug("Dịch vụ async_leave_group được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        payload = {
            "accountSelection": call.data["account_selection"],
            "groupId": call.data["group_id"],
            "silent": call.data.get("silent", False)
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/leaveGroupByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi rời nhóm: %s", resp.text)
        await show_result_notification(hass, "rời nhóm", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_leave_group: %s", e)
        await show_result_notification(hass, "rời nhóm", None, error=e)

async def async_create_note_group_service(hass, call, zalo_login):
    """Dịch vụ tạo ghi chú nhóm."""
    _LOGGER.debug("Dịch vụ async_create_note_group được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        payload = {
            "groupId": call.data["group_id"],
            "accountSelection": call.data["account_selection"],
            "options": {
                "title": call.data["title"],
                "pinAct": call.data.get("pin_act", True)
            }
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/createNoteGroupByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi tạo ghi chú nhóm: %s", resp.text)
        await show_result_notification(hass, "tạo ghi chú nhóm", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_create_note_group: %s", e)
        await show_result_notification(hass, "tạo ghi chú nhóm", None, error=e)

async def async_edit_note_group_service(hass, call, zalo_login):
    """Dịch vụ sửa ghi chú nhóm."""
    _LOGGER.debug("Dịch vụ async_edit_note_group được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        payload = {
            "groupId": call.data["group_id"],
            "accountSelection": call.data["account_selection"],
            "options": {
                "topicId": call.data["topic_id"],
                "title": call.data["title"]
            }
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/editNoteGroupByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi sửa ghi chú nhóm: %s", resp.text)
        await show_result_notification(hass, "sửa ghi chú nhóm", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_edit_note_group: %s", e)
        await show_result_notification(hass, "sửa ghi chú nhóm", None, error=e)

async def async_get_list_board_service(hass, call, zalo_login):
    """Dịch vụ lấy danh sách bảng tin nhóm."""
    _LOGGER.debug("Dịch vụ async_get_list_board được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        payload = {
            "accountSelection": call.data["account_selection"],
            "groupId": call.data["group_id"]
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/getListBoardByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi lấy danh sách bảng tin nhóm: %s", resp.text)
        await show_result_notification(hass, "lấy danh sách bảng tin nhóm", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_get_list_board: %s", e)
        await show_result_notification(hass, "lấy danh sách bảng tin nhóm", None, error=e)

async def async_create_poll_service(hass, call, zalo_login):
    """Dịch vụ tạo bình chọn."""
    _LOGGER.debug("Dịch vụ async_create_poll được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        options_list = call.data["options"].split(",")
        options_list = [opt.strip() for opt in options_list]

        payload = {
            "groupId": call.data["group_id"],
            "accountSelection": call.data["account_selection"],
            "options": {
                "question": call.data["question"],
                "options": options_list,
                "allowMultiChoices": call.data.get("allow_multi_choices", False)
            }
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/createPollByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi tạo bình chọn: %s", resp.text)
        await show_result_notification(hass, "tạo bình chọn", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_create_poll: %s", e)
        await show_result_notification(hass, "tạo bình chọn", None, error=e)

async def async_get_poll_detail_service(hass, call, zalo_login):
    """Dịch vụ lấy chi tiết bình chọn."""
    _LOGGER.debug("Dịch vụ async_get_poll_detail được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        payload = {
            "accountSelection": call.data["account_selection"],
            "pollId": call.data["poll_id"]
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/getPollDetailByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi lấy chi tiết bình chọn: %s", resp.text)
        await show_result_notification(hass, "lấy chi tiết bình chọn", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_get_poll_detail: %s", e)
        await show_result_notification(hass, "lấy chi tiết bình chọn", None, error=e)

async def async_lock_poll_service(hass, call, zalo_login):
    """Dịch vụ khóa bình chọn."""
    _LOGGER.debug("Dịch vụ async_lock_poll được gọi với: %s", call.data)
    try:
        await hass.async_add_executor_job(zalo_login)
        # Đảm bảo pollId là số nguyên
        try:
            poll_id = int(call.data["poll_id"])
        except ValueError:
            poll_id = call.data["poll_id"]
            
        payload = {
            "accountSelection": call.data["account_selection"],
            "pollId": poll_id
        }
        resp = await hass.async_add_executor_job(
            lambda: session.post(f"{zalo_server}/api/lockPollByAccount", json=payload)
        )
        _LOGGER.info("Phản hồi khóa bình chọn: %s", resp.text)
        await show_result_notification(hass, "khóa bình chọn", resp)
    except Exception as e:
        _LOGGER.error("Lỗi trong async_lock_poll: %s", e)
        await show_result_notification(hass, "khóa bình chọn", None, error=e)
