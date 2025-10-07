"""Zalo Bot integration."""
import logging
import os
import requests
from homeassistant.helpers import config_validation as cv, device_registry as dr
from .const import (
    CONF_ENABLE_NOTIFICATIONS,
    CONF_ZALO_SERVER,
    CONF_USERNAME,
    CONF_PASSWORD,
    DEFAULT_ENABLE_NOTIFICATIONS,
    DOMAIN,
    PLATFORMS,
    SERVICE_ADD_PROXY_SCHEMA,
    SERVICE_REMOVE_PROXY_SCHEMA,
    SERVICE_GET_PROXIES_SCHEMA,
    SERVICE_RESET_HIDDEN_CONVERS_PIN_SCHEMA,
    SERVICE_GET_MUTE_SCHEMA,
    SERVICE_GET_PIN_CONVERSATIONS_SCHEMA,
    SERVICE_ADD_REACTION_SCHEMA,
    SERVICE_DELETE_MESSAGE_SCHEMA,
    SERVICE_FORWARD_MESSAGE_SCHEMA,
    SERVICE_PARSE_LINK_SCHEMA,
    SERVICE_SEND_CARD_SCHEMA,
    SERVICE_SEND_LINK_SCHEMA,
    SERVICE_GET_LABELS_SCHEMA,
    SERVICE_BLOCK_VIEW_FEED_SCHEMA,
    SERVICE_CHANGE_ACCOUNT_AVATAR_SCHEMA,
    SERVICE_SEND_MESSAGE_SCHEMA,
    SERVICE_SEND_FILE_SCHEMA,
    SERVICE_SEND_IMAGE_SCHEMA,
    SERVICE_SEND_VIDEO_SCHEMA,
    SERVICE_GET_LOGGED_ACCOUNTS_SCHEMA,
    SERVICE_GET_ACCOUNT_DETAILS_SCHEMA,
    SERVICE_FIND_USER_SCHEMA,
    SERVICE_GET_USER_INFO_SCHEMA,
    SERVICE_SEND_FRIEND_REQUEST_SCHEMA,
    SERVICE_CREATE_GROUP_SCHEMA,
    SERVICE_GET_GROUP_INFO_SCHEMA,
    SERVICE_ADD_USER_TO_GROUP_SCHEMA,
    SERVICE_REMOVE_USER_FROM_GROUP_SCHEMA,
    SERVICE_SEND_IMAGE_TO_USER_SCHEMA,
    SERVICE_SEND_IMAGE_TO_GROUP_SCHEMA,
    SERVICE_UPDATE_HIDDEN_CONVERS_PIN_SCHEMA,
    SERVICE_GET_STICKERS_SCHEMA,
    SERVICE_GET_STICKERS_DETAIL_SCHEMA,
    SERVICE_CREATE_NOTE_GROUP_SCHEMA,
    SERVICE_EDIT_NOTE_GROUP_SCHEMA,
    SERVICE_GET_LIST_BOARD_SCHEMA,
    SERVICE_CREATE_POLL_SCHEMA,
    SERVICE_GET_POLL_DETAIL_SCHEMA,
    SERVICE_LOCK_POLL_SCHEMA,
    SERVICE_EDIT_REMINDER_SCHEMA,
    SERVICE_GET_REMINDER_SCHEMA,
    SERVICE_GET_LIST_REMINDER_SCHEMA,
    SERVICE_GET_REMINDER_RESPONSES_SCHEMA,
    SERVICE_ADD_QUICK_MESSAGE_SCHEMA,
    SERVICE_GET_QUICK_MESSAGE_SCHEMA,
    SERVICE_REMOVE_QUICK_MESSAGE_SCHEMA,
    SERVICE_UPDATE_QUICK_MESSAGE_SCHEMA,
    SERVICE_GET_AVATAR_LIST_SCHEMA,
    SERVICE_LAST_ONLINE_SCHEMA,
    SERVICE_SEND_TYPING_EVENT_SCHEMA,
    SERVICE_SEND_IMAGES_TO_USER_SCHEMA,
    SERVICE_SEND_IMAGES_TO_GROUP_SCHEMA,
    SERVICE_GET_ACCOUNT_WEBHOOKS_SCHEMA,
    SERVICE_GET_ACCOUNT_WEBHOOK_SCHEMA,
    SERVICE_SET_ACCOUNT_WEBHOOK_SCHEMA,
    SERVICE_DELETE_ACCOUNT_WEBHOOK_SCHEMA,
    SERVICE_ACCEPT_FRIEND_REQUEST_SCHEMA,
    SERVICE_BLOCK_USER_SCHEMA,
    SERVICE_UNBLOCK_USER_SCHEMA,
    SERVICE_SEND_STICKER_SCHEMA,
    SERVICE_UNDO_MESSAGE_SCHEMA,
    SERVICE_CREATE_REMINDER_SCHEMA,
    SERVICE_REMOVE_REMINDER_SCHEMA,
    SERVICE_CHANGE_GROUP_NAME_SCHEMA,
    SERVICE_CHANGE_GROUP_AVATAR_SCHEMA,
    SERVICE_SEND_VOICE_SCHEMA,
    SERVICE_GET_ALL_FRIENDS_SCHEMA,
    SERVICE_GET_RECEIVED_FRIEND_REQUESTS_SCHEMA,
    SERVICE_GET_SENT_FRIEND_REQUESTS_SCHEMA,
    SERVICE_UNDO_FRIEND_REQUEST_SCHEMA,
    SERVICE_REMOVE_FRIEND_SCHEMA,
    SERVICE_CHANGE_FRIEND_ALIAS_SCHEMA,
    SERVICE_REMOVE_FRIEND_ALIAS_SCHEMA,
    SERVICE_GET_ALL_GROUPS_SCHEMA,
    SERVICE_ADD_GROUP_DEPUTY_SCHEMA,
    SERVICE_REMOVE_GROUP_DEPUTY_SCHEMA,
    SERVICE_CHANGE_GROUP_OWNER_SCHEMA,
    SERVICE_DISPERSE_GROUP_SCHEMA,
    SERVICE_ENABLE_GROUP_LINK_SCHEMA,
    SERVICE_DISABLE_GROUP_LINK_SCHEMA,
    SERVICE_JOIN_GROUP_SCHEMA,
    SERVICE_LEAVE_GROUP_SCHEMA,
    SERVICE_UPDATE_PROFILE_SCHEMA,
    SERVICE_UPDATE_SETTINGS_SCHEMA,
    SERVICE_SET_MUTE_SCHEMA,
    SERVICE_SET_PINNED_CONVERSATION_SCHEMA,
    SERVICE_GET_UNREAD_MARK_SCHEMA,
    SERVICE_ADD_UNREAD_MARK_SCHEMA,
    SERVICE_REMOVE_UNREAD_MARK_SCHEMA,
    SERVICE_DELETE_CHAT_SCHEMA,
    SERVICE_GET_ARCHIVED_CHAT_LIST_SCHEMA,
    SERVICE_GET_AUTO_DELETE_CHAT_SCHEMA,
    SERVICE_UPDATE_AUTO_DELETE_CHAT_SCHEMA,
    SERVICE_GET_HIDDEN_CONVERSATIONS_SCHEMA,
    SERVICE_SET_HIDDEN_CONVERSATIONS_SCHEMA,

)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

session = requests.Session()
zalo_server = None
WWW_DIR = None
PUBLIC_DIR = None

async def async_setup(hass, config):
    return True

async def async_setup_entry(hass, entry):
    hass.data.setdefault(DOMAIN, {})
    config = dict(entry.data)

    # Đảm bảo có cài đặt enable_notifications
    if CONF_ENABLE_NOTIFICATIONS not in config:
        config[CONF_ENABLE_NOTIFICATIONS] = DEFAULT_ENABLE_NOTIFICATIONS

    # Khởi tạo session và các biến toàn cục
    global session, zalo_server, WWW_DIR, PUBLIC_DIR
    session = requests.Session()

    # Lấy thông tin cấu hình
    zalo_server = config.get(CONF_ZALO_SERVER)
    admin_user = config.get(CONF_USERNAME, "admin")
    admin_pass = config.get(CONF_PASSWORD, "admin")

    # Cập nhật dữ liệu trong hass.data
    hass.data[DOMAIN][entry.entry_id] = config

    # Kiểm tra xem zalo_server có giá trị không
    if not zalo_server:
        _LOGGER.error("Không tìm thấy URL máy chủ Zalo Bot. Vui lòng kiểm tra cấu hình.")
        return False

    # Thiết lập đường dẫn thư mục
    config_dir = hass.config.path()
    WWW_DIR = os.path.join(config_dir, "www")
    PUBLIC_DIR = os.path.join(WWW_DIR, "zalo_bot")
    
    # Cập nhật biến PUBLIC_DIR trong file_handling.py
    from . import file_handling
    file_handling.PUBLIC_DIR = PUBLIC_DIR
    
    # Cập nhật biến toàn cục trong chat_features.py
    from . import chat_features
    chat_features.set_globals(session, zalo_server)
    
    # Cập nhật biến toàn cục trong group_features.py
    from . import group_features
    group_features.set_globals(session, zalo_server)

    # Cập nhật biến toàn cục trong user_features.py
    from . import user_features
    user_features.set_globals(hass, session, zalo_server)
    
    # Cập nhật biến toàn cục trong account_features.py
    from . import account_features
    account_features.set_globals(hass, session, zalo_server)
    
    # Cập nhật biến toàn cục trong misc_features.py
    from . import misc_features
    misc_features.set_globals(session, zalo_server)
    
    # Cập nhật biến toàn cục trong sticker_features.py
    from . import sticker_features
    sticker_features.set_globals(session, zalo_server)
    
    # Cập nhật biến toàn cục trong reminder_features.py
    from . import reminder_features
    reminder_features.set_globals(session, zalo_server)

    # Cập nhật biến toàn cục trong quickmsg_features.py
    from . import quickmsg_features
    quickmsg_features.set_globals(session, zalo_server)

    # Khởi tạo các platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    def zalo_login():
        resp = session.post(f"{zalo_server}/api/login", json={
            "username": admin_user,
            "password": admin_pass
        })
        if resp.status_code == 200 and resp.json().get("success"):
            _LOGGER.info("Đăng nhập quản trị viên Zalo thành công")
        else:
            _LOGGER.error("Đăng nhập quản trị viên Zalo thất bại: %s", resp.text)

    try:
        pass

    except Exception:
        pass

    async def send_message(call):
        await chat_features.async_send_message_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN,
        "send_message",
        send_message,
        schema=SERVICE_SEND_MESSAGE_SCHEMA,
    )
    
    async def send_file(call):
        await chat_features.async_send_file_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN,
        "send_file",
        send_file,
        schema=SERVICE_SEND_FILE_SCHEMA,
    )

    async def send_image(call):
        await chat_features.async_send_image_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN,
        "send_image",
        send_image,
        schema=SERVICE_SEND_IMAGE_SCHEMA,
    )
    
    async def send_video(call):
        await chat_features.async_send_video_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "send_video",
        send_video,
        schema=SERVICE_SEND_VIDEO_SCHEMA,
    )

    async def get_logged_accounts(call):
        return await account_features.async_get_logged_accounts_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_logged_accounts",
        get_logged_accounts,
        schema=SERVICE_GET_LOGGED_ACCOUNTS_SCHEMA,
        supports_response=True
    )

    async def get_account_details(call):
        await account_features.async_get_account_details_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_account_details",
        get_account_details,
        schema=SERVICE_GET_ACCOUNT_DETAILS_SCHEMA,
    )

    async def find_user(call):
        await user_features.async_find_user_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "find_user",
        find_user,
        schema=SERVICE_FIND_USER_SCHEMA,
    )

    async def get_user_info(call):
        await user_features.async_get_user_info_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_user_info",
        get_user_info,
        schema=SERVICE_GET_USER_INFO_SCHEMA,
    )

    async def send_friend_request(call):
        await user_features.async_send_friend_request_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "send_friend_request",
        send_friend_request,
        schema=SERVICE_SEND_FRIEND_REQUEST_SCHEMA,
    )

    async def create_group(call):
        await group_features.async_create_group_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "create_group",
        create_group,
        schema=SERVICE_CREATE_GROUP_SCHEMA,
    )

    async def get_group_info(call):
        await group_features.async_get_group_info_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_group_info",
        get_group_info,
        schema=SERVICE_GET_GROUP_INFO_SCHEMA,
    )

    async def add_user_to_group(call):
        await group_features.async_add_user_to_group_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "add_user_to_group",
        add_user_to_group,
        schema=SERVICE_ADD_USER_TO_GROUP_SCHEMA,
    )

    async def remove_user_from_group(call):
        await group_features.async_remove_user_from_group_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "remove_user_from_group",
        remove_user_from_group,
        schema=SERVICE_REMOVE_USER_FROM_GROUP_SCHEMA,
    )

    async def send_image_to_user(call):
        await chat_features.async_send_image_to_user_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "send_image_to_user",
        send_image_to_user,
        schema=SERVICE_SEND_IMAGE_TO_USER_SCHEMA,
    )

    async def send_image_to_group(call):
        await chat_features.async_send_image_to_group_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "send_image_to_group",
        send_image_to_group,
        schema=SERVICE_SEND_IMAGE_TO_GROUP_SCHEMA
    )

    async def get_proxies(call):
        await account_features.async_get_proxies_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_proxies", 
        get_proxies, 
        schema=SERVICE_GET_PROXIES_SCHEMA
    )

    async def add_proxy(call):
        await account_features.async_add_proxy_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "add_proxy", 
        add_proxy, 
        schema=SERVICE_ADD_PROXY_SCHEMA
    )

    async def remove_proxy(call):
        await account_features.async_remove_proxy_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "remove_proxy", 
        remove_proxy, 
        schema=SERVICE_REMOVE_PROXY_SCHEMA
    )

    async def accept_friend_request(call):
        await user_features.async_accept_friend_request_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "accept_friend_request",
        accept_friend_request,
        schema=SERVICE_ACCEPT_FRIEND_REQUEST_SCHEMA
    )

    async def block_user(call):
        await user_features.async_block_user_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "block_user", 
        block_user, 
        schema=SERVICE_BLOCK_USER_SCHEMA
    )

    async def unblock_user(call):
        await user_features.async_unblock_user_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "unblock_user", 
        unblock_user, 
        schema=SERVICE_UNBLOCK_USER_SCHEMA
    )

    async def send_sticker(call):
        await chat_features.async_send_sticker_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, 
        "send_sticker", 
        send_sticker,
        schema=SERVICE_SEND_STICKER_SCHEMA
    )

    async def undo_message(call):
        await misc_features.async_undo_message_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, 
        "undo_message", 
        undo_message, 
        schema=SERVICE_UNDO_MESSAGE_SCHEMA
    )

    async def create_reminder(call):
        await misc_features.async_create_reminder_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_sent_friend_requests",
        create_reminder,
        schema=SERVICE_GET_SENT_FRIEND_REQUESTS_SCHEMA
    )

    async def undo_friend_request(call):
        await user_features.async_undo_friend_request_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "undo_friend_request",
        undo_friend_request,
        schema=SERVICE_UNDO_FRIEND_REQUEST_SCHEMA
    )

    async def remove_friend(call):
        await user_features.async_remove_friend_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "remove_friend",
        remove_friend,
        schema=SERVICE_REMOVE_FRIEND_SCHEMA
    )

    async def change_friend_alias(call):
        await user_features.async_change_friend_alias_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "change_friend_alias",
        change_friend_alias,
        schema=SERVICE_CHANGE_FRIEND_ALIAS_SCHEMA
    )

    async def remove_friend_alias(call):
        await user_features.async_remove_friend_alias_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "remove_friend_alias",
        remove_friend_alias,
        schema=SERVICE_REMOVE_FRIEND_ALIAS_SCHEMA
    )

    async def get_all_groups(call):
        await group_features.async_get_all_groups_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_all_groups",
        get_all_groups,
        schema=SERVICE_GET_ALL_GROUPS_SCHEMA
    )

    async def add_group_deputy(call):
        await group_features.async_add_group_deputy_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "add_group_deputy",
        add_group_deputy,
        schema=SERVICE_ADD_GROUP_DEPUTY_SCHEMA
    )

    async def remove_group_deputy(call):
        await group_features.async_remove_group_deputy_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "remove_group_deputy",
        remove_group_deputy,
        schema=SERVICE_REMOVE_GROUP_DEPUTY_SCHEMA
    )

    async def change_group_owner(call):
        await group_features.async_change_group_owner_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "change_group_owner",
        change_group_owner,
        schema=SERVICE_CHANGE_GROUP_OWNER_SCHEMA
    )

    async def disperse_group(call):
        await group_features.async_disperse_group_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "disperse_group",
        disperse_group,
        schema=SERVICE_DISPERSE_GROUP_SCHEMA
    )

    async def enable_group_link(call):
        await group_features.async_enable_group_link_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "enable_group_link",
        enable_group_link,
        schema=SERVICE_ENABLE_GROUP_LINK_SCHEMA
    )

    async def disable_group_link(call):
        await group_features.async_disable_group_link_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "disable_group_link",
        disable_group_link,
        schema=SERVICE_DISABLE_GROUP_LINK_SCHEMA
    )

    async def join_group(call):
        await group_features.async_join_group_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "join_group",
        join_group,
        schema=SERVICE_JOIN_GROUP_SCHEMA
    )

    async def leave_group(call):
        await group_features.async_leave_group_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "leave_group",
        leave_group,
        schema=SERVICE_LEAVE_GROUP_SCHEMA
    )

    async def update_profile(call):
        await user_features.async_update_profile_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "update_profile",
        update_profile,
        schema=SERVICE_UPDATE_PROFILE_SCHEMA
    )

    async def update_settings(call):
        await misc_features.async_update_settings_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "update_settings",
        update_settings,
        schema=SERVICE_UPDATE_SETTINGS_SCHEMA
    )

    async def set_mute(call):
        await misc_features.async_set_mute_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "set_mute",
        set_mute,
        schema=SERVICE_SET_MUTE_SCHEMA
    )

    async def set_pinned_conversation(call):
        await misc_features.async_set_pinned_conversation_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "set_pinned_conversation",
        set_pinned_conversation,
        schema=SERVICE_SET_PINNED_CONVERSATION_SCHEMA
    )

    async def get_unread_mark(call):
        await misc_features.async_get_unread_mark_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_unread_mark",
        get_unread_mark,
        schema=SERVICE_GET_UNREAD_MARK_SCHEMA
    )

    async def add_unread_mark(call):
        await misc_features.async_add_unread_mark_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "add_unread_mark",
        add_unread_mark,
        schema=SERVICE_ADD_UNREAD_MARK_SCHEMA
    )

    async def remove_unread_mark(call):
        await misc_features.async_remove_unread_mark_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "remove_unread_mark",
        remove_unread_mark,
        schema=SERVICE_REMOVE_UNREAD_MARK_SCHEMA
    )

    async def delete_chat(call):
        await misc_features.async_delete_chat_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "delete_chat",
        delete_chat,
        schema=SERVICE_DELETE_CHAT_SCHEMA
    )

    async def get_archived_chat_list(call):
        await misc_features.async_get_archived_chat_list_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_archived_chat_list",
        get_archived_chat_list,
        schema=SERVICE_GET_ARCHIVED_CHAT_LIST_SCHEMA
    )

    async def get_auto_delete_chat(call):
        await misc_features.async_get_auto_delete_chat_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_auto_delete_chat",
        get_auto_delete_chat,
        schema=SERVICE_GET_AUTO_DELETE_CHAT_SCHEMA
    )

    async def update_auto_delete_chat(call):
        await misc_features.async_update_auto_delete_chat_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "update_auto_delete_chat",
        update_auto_delete_chat,
        schema=SERVICE_UPDATE_AUTO_DELETE_CHAT_SCHEMA
    )

    async def get_hidden_conversations(call):
        await misc_features.async_get_hidden_conversations_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_hidden_conversations",
        get_hidden_conversations,
        schema=SERVICE_GET_HIDDEN_CONVERSATIONS_SCHEMA
    )

    async def set_hidden_conversations(call):
        await misc_features.async_set_hidden_conversations_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "set_hidden_conversations",
        set_hidden_conversations,
        schema=SERVICE_SET_HIDDEN_CONVERSATIONS_SCHEMA
    )

    async def update_hidden_convers_pin(call):
        await misc_features.async_update_hidden_convers_pin_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "update_hidden_convers_pin",
        update_hidden_convers_pin,
        schema=SERVICE_UPDATE_HIDDEN_CONVERS_PIN_SCHEMA
    )

    async def reset_hidden_convers_pin(call):
        await misc_features.async_reset_hidden_convers_pin_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "reset_hidden_convers_pin",
        reset_hidden_convers_pin,
        schema=SERVICE_RESET_HIDDEN_CONVERS_PIN_SCHEMA
    )

    async def get_mute(call):
        await misc_features.async_get_mute_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_mute",
        get_mute,
        schema=SERVICE_GET_MUTE_SCHEMA
    )

    async def get_pin_conversations(call):
        await misc_features.async_get_pin_conversations_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_pin_conversations",
        get_pin_conversations,
        schema=SERVICE_GET_PIN_CONVERSATIONS_SCHEMA
    )

    async def add_reaction(call):
        await misc_features.async_add_reaction_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "add_reaction",
        add_reaction,
        schema=SERVICE_ADD_REACTION_SCHEMA
    )

    async def delete_message(call):
        await misc_features.async_delete_message_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "delete_message",
        delete_message,
        schema=SERVICE_DELETE_MESSAGE_SCHEMA
    )

    async def forward_message(call):
        await misc_features.async_forward_message_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "forward_message",
        forward_message,
        schema=SERVICE_FORWARD_MESSAGE_SCHEMA
    )

    async def parse_link(call):
        await misc_features.async_parse_link_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "parse_link",
        parse_link,
        schema=SERVICE_PARSE_LINK_SCHEMA
    )

    async def send_card(call):
        await misc_features.async_send_card_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "send_card",
        send_card,
        schema=SERVICE_SEND_CARD_SCHEMA
    )

    async def send_link(call):
        await misc_features.async_send_link_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "send_link",
        send_link,
        schema=SERVICE_SEND_LINK_SCHEMA
    )

    async def get_stickers(call):
        await sticker_features.async_get_stickers_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_stickers",
        get_stickers,
        schema=SERVICE_GET_STICKERS_SCHEMA
    )

    async def get_stickers_detail(call):
        await sticker_features.async_get_stickers_detail_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_stickers_detail",
        get_stickers_detail,
        schema=SERVICE_GET_STICKERS_DETAIL_SCHEMA
    )

    async def create_note_group(call):
        await group_features.async_create_note_group_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "create_note_group",
        create_note_group,
        schema=SERVICE_CREATE_NOTE_GROUP_SCHEMA
    )

    async def edit_note_group(call):
        await group_features.async_edit_note_group_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "edit_note_group",
        edit_note_group,
        schema=SERVICE_EDIT_NOTE_GROUP_SCHEMA
    )

    async def get_list_board(call):
        await group_features.async_get_list_board_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_list_board",
        get_list_board,
        schema=SERVICE_GET_LIST_BOARD_SCHEMA
    )

    async def create_poll(call):
        await group_features.async_create_poll_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "create_poll",
        create_poll,
        schema=SERVICE_CREATE_POLL_SCHEMA
    )

    async def get_poll_detail(call):
        await group_features.async_get_poll_detail_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_poll_detail",
        get_poll_detail,
        schema=SERVICE_GET_POLL_DETAIL_SCHEMA
    )

    async def lock_poll(call):
        await group_features.async_lock_poll_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "lock_poll",
        lock_poll,
        schema=SERVICE_LOCK_POLL_SCHEMA
    )

    async def edit_reminder(call):
        await reminder_features.async_edit_reminder_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "edit_reminder",
        edit_reminder,
        schema=SERVICE_EDIT_REMINDER_SCHEMA
    )

    async def get_reminder(call):
        await reminder_features.async_get_reminder_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_reminder",
        get_reminder,
        schema=SERVICE_GET_REMINDER_SCHEMA
    )

    async def get_list_reminder(call):
        await reminder_features.async_get_list_reminder_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_list_reminder",
        get_list_reminder,
        schema=SERVICE_GET_LIST_REMINDER_SCHEMA
    )

    async def get_reminder_responses(call):
        await reminder_features.async_get_reminder_responses_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_reminder_responses",
        get_reminder_responses,
        schema=SERVICE_GET_REMINDER_RESPONSES_SCHEMA
    )

    async def add_quick_message(call):
        await quickmsg_features.async_add_quick_message_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "add_quick_message",
        add_quick_message,
        schema=SERVICE_ADD_QUICK_MESSAGE_SCHEMA
    )

    async def get_quick_message(call):
        await quickmsg_features.async_get_quick_message_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_quick_message",
        get_quick_message,
        schema=SERVICE_GET_QUICK_MESSAGE_SCHEMA
    )

    async def remove_quick_message(call):
        await quickmsg_features.async_remove_quick_message_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "remove_quick_message",
        remove_quick_message,
        schema=SERVICE_REMOVE_QUICK_MESSAGE_SCHEMA
    )

    async def update_quick_message(call):
        await quickmsg_features.async_update_quick_message_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "update_quick_message",
        update_quick_message,
        schema=SERVICE_UPDATE_QUICK_MESSAGE_SCHEMA
    )

    async def get_labels(call):
        await misc_features.async_get_labels_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_labels",
        get_labels,
        schema=SERVICE_GET_LABELS_SCHEMA
    )

    async def block_view_feed(call):
        await misc_features.async_block_view_feed_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "block_view_feed",
        block_view_feed,
        schema=SERVICE_BLOCK_VIEW_FEED_SCHEMA
    )

    async def change_account_avatar(call):
        await misc_features.async_change_account_avatar_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "change_account_avatar",
        change_account_avatar,
        schema=SERVICE_CHANGE_ACCOUNT_AVATAR_SCHEMA
    )

    async def get_avatar_list(call):
        await user_features.async_get_avatar_list_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_avatar_list",
        get_avatar_list,
        schema=SERVICE_GET_AVATAR_LIST_SCHEMA
    )

    async def last_online(call):
        await user_features.async_last_online_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "last_online",
        last_online,
        schema=SERVICE_LAST_ONLINE_SCHEMA
    )

    async def send_typing_event(call):
        await chat_features.async_send_typing_event_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "send_typing_event",
        send_typing_event,
        schema=SERVICE_SEND_TYPING_EVENT_SCHEMA
    )

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, "zalo_bot")},
        manufacturer="Smarthome Black",
        name="Zalo Bot",
        model="Zalo Bot",
        sw_version="2025.8.30a"
    )

    async def send_images_to_user(call):
        await chat_features.async_send_images_to_user_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "send_images_to_user",
        send_images_to_user,
        schema=SERVICE_SEND_IMAGES_TO_USER_SCHEMA
    )

    async def get_account_webhooks(call):
        await account_features.async_get_account_webhooks_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_account_webhooks",
        get_account_webhooks,
        schema=SERVICE_GET_ACCOUNT_WEBHOOKS_SCHEMA
    )

    async def get_account_webhook(call):
        await account_features.async_get_account_webhook_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_account_webhook",
        get_account_webhook,
        schema=SERVICE_GET_ACCOUNT_WEBHOOK_SCHEMA
    )

    async def set_account_webhook(call):
        await account_features.async_set_account_webhook_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "set_account_webhook",
        set_account_webhook,
        schema=SERVICE_SET_ACCOUNT_WEBHOOK_SCHEMA
    )

    async def delete_account_webhook(call):
        await account_features.async_delete_account_webhook_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "delete_account_webhook",
        delete_account_webhook,
        schema=SERVICE_DELETE_ACCOUNT_WEBHOOK_SCHEMA
    )

    async def send_images_to_group(call):
        await chat_features.async_send_images_to_group_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "send_images_to_group",
        send_images_to_group,
        schema=SERVICE_SEND_IMAGES_TO_GROUP_SCHEMA
    )

    async def create_reminder(call):
        await misc_features.async_create_reminder_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "create_reminder",
        create_reminder,
        schema=SERVICE_CREATE_REMINDER_SCHEMA
    )

    async def remove_reminder(call):
        await misc_features.async_remove_reminder_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "remove_reminder",
        remove_reminder,
        schema=SERVICE_REMOVE_REMINDER_SCHEMA
    )

    async def change_group_name(call):
        await group_features.async_change_group_name_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "change_group_name",
        change_group_name,
        schema=SERVICE_CHANGE_GROUP_NAME_SCHEMA
    )

    async def change_group_avatar(call):
        await group_features.async_change_group_avatar_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "change_group_avatar",
        change_group_avatar,
        schema=SERVICE_CHANGE_GROUP_AVATAR_SCHEMA
    )

    async def send_voice(call):
        await chat_features.async_send_voice_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "send_voice",
        send_voice,
        schema=SERVICE_SEND_VOICE_SCHEMA
    )

    async def get_all_friends(call):
        await user_features.async_get_all_friends_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_all_friends",
        get_all_friends,
        schema=SERVICE_GET_ALL_FRIENDS_SCHEMA
    )

    async def get_received_friend_requests(call):
        await user_features.async_get_received_friend_requests_service(hass, call, zalo_login)
    hass.services.async_register(
        DOMAIN, "get_received_friend_requests",
        get_received_friend_requests,
        schema=SERVICE_GET_RECEIVED_FRIEND_REQUESTS_SCHEMA
    )

    return True
async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    # Unload các platform
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    # Xóa dữ liệu entry
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
