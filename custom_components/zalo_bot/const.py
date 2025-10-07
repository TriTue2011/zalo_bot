"""Constants for the Zalo Bot integration."""
from homeassistant.const import Platform
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

DOMAIN = "zalo_bot"

# Configuration constants
CONF_ZALO_SERVER = "zalo_server"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_ENABLE_NOTIFICATIONS = "enable_notifications"
DEFAULT_ENABLE_NOTIFICATIONS = True
SIGNAL_NOTIFICATION_TOGGLE = f"{DOMAIN}_notification_toggle"

# Platforms
PLATFORMS = [Platform.SWITCH, Platform.BINARY_SENSOR]

# Signal
SIGNAL_NOTIFICATION_TOGGLE = f"{DOMAIN}_notification_toggle"

# Schema cho các service
SERVICE_SEND_MESSAGE_SCHEMA = vol.Schema({
    vol.Required("message"): cv.string,
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
    vol.Optional("type", default="0"): cv.string,
    vol.Optional("ttl", default=0): vol.All(int, vol.Range(min=0)),
    vol.Optional("quote"): vol.Schema({
        vol.Required("content"): cv.string,
        vol.Required("uidFrom"): cv.string,
    }),
})

SERVICE_SEND_FILE_SCHEMA = vol.Schema({
    vol.Required("file_path_or_url"): cv.string,
    vol.Optional("message"): cv.string,
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
    vol.Optional("type", default="0"): cv.string,
    vol.Optional("ttl", default=0): vol.All(int, vol.Range(min=0)),
})

SERVICE_SEND_IMAGE_SCHEMA = vol.Schema({
    vol.Required("image_path"): cv.string,
    vol.Optional("message"): cv.string,
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
    vol.Optional("type", default="0"): cv.string,
    vol.Optional("ttl", default=0): vol.All(int, vol.Range(min=0)),
})

SERVICE_GET_LOGGED_ACCOUNTS_SCHEMA = vol.Schema({})

SERVICE_GET_ACCOUNT_DETAILS_SCHEMA = vol.Schema({
    vol.Optional("own_id", default=""): cv.string,
})

SERVICE_FIND_USER_SCHEMA = vol.Schema({
    vol.Optional("phone", default=""): cv.string,
    vol.Optional("account_selection", default=""): cv.string,
})

SERVICE_GET_USER_INFO_SCHEMA = vol.Schema({
    vol.Optional("user_id", default=""): cv.string,
    vol.Optional("account_selection", default=""): cv.string,
})

SERVICE_SEND_FRIEND_REQUEST_SCHEMA = vol.Schema({
    vol.Optional("user_id", default=""): cv.string,
    vol.Optional("message", default="Xin chào, hãy kết bạn với tôi!"): cv.string,
    vol.Optional("account_selection", default=""): cv.string,
})

SERVICE_CREATE_GROUP_SCHEMA = vol.Schema({
    vol.Optional("members", default=""): cv.string,
    vol.Optional("name", default=""): cv.string,
    vol.Optional("avatar_path", default=""): cv.string,
    vol.Optional("account_selection", default=""): cv.string,
})

SERVICE_GET_GROUP_INFO_SCHEMA = vol.Schema({
    vol.Optional("group_id", default=""): cv.string,
    vol.Optional("account_selection", default=""): cv.string,
})

SERVICE_ADD_USER_TO_GROUP_SCHEMA = vol.Schema({
    vol.Optional("group_id", default=""): cv.string,
    vol.Optional("member_id", default=""): cv.string,
    vol.Optional("account_selection", default=""): cv.string,
})

SERVICE_REMOVE_USER_FROM_GROUP_SCHEMA = vol.Schema({
    vol.Optional("group_id", default=""): cv.string,
    vol.Optional("member_id", default=""): cv.string,
    vol.Optional("account_selection", default=""): cv.string,
})

SERVICE_SEND_IMAGE_TO_USER_SCHEMA = vol.Schema({
    vol.Optional("image_path", default=""): cv.string,
    vol.Optional("thread_id", default=""): cv.string,
    vol.Optional("account_selection", default=""): cv.string,
})

SERVICE_SEND_IMAGES_TO_USER_SCHEMA = vol.Schema({
    vol.Optional("image_paths", default=""): cv.string,
    vol.Optional("thread_id", default=""): cv.string,
    vol.Optional("account_selection", default=""): cv.string,
})

SERVICE_SEND_IMAGE_TO_GROUP_SCHEMA = vol.Schema({
    vol.Optional("image_path", default=""): cv.string,
    vol.Optional("thread_id", default=""): cv.string,
    vol.Optional("account_selection", default=""): cv.string,
})

SERVICE_SEND_IMAGES_TO_GROUP_SCHEMA = vol.Schema({
    vol.Optional("image_paths", default=""): cv.string,
    vol.Optional("thread_id", default=""): cv.string,
    vol.Optional("account_selection", default=""): cv.string,
})

SERVICE_GET_ACCOUNT_WEBHOOKS_SCHEMA = vol.Schema({})

SERVICE_GET_ACCOUNT_WEBHOOK_SCHEMA = vol.Schema({
    vol.Optional("own_id", default=""): cv.string,
})

SERVICE_SET_ACCOUNT_WEBHOOK_SCHEMA = vol.Schema({
    vol.Optional("own_id", default=""): cv.string,
    vol.Optional("message_webhook_url", default=""): cv.string,
    vol.Optional("group_event_webhook_url", default=""): cv.string,
    vol.Optional("reaction_webhook_url", default=""): cv.string,
})

SERVICE_DELETE_ACCOUNT_WEBHOOK_SCHEMA = vol.Schema({
    vol.Optional("own_id", default=""): cv.string,
})

SERVICE_GET_PROXIES_SCHEMA = vol.Schema({})

SERVICE_ADD_PROXY_SCHEMA = vol.Schema({
    vol.Optional("proxy_url", default=""): cv.string,
})

SERVICE_REMOVE_PROXY_SCHEMA = vol.Schema({
    vol.Optional("proxy_url", default=""): cv.string,
})

SERVICE_ACCEPT_FRIEND_REQUEST_SCHEMA = vol.Schema({
    vol.Required("user_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_BLOCK_USER_SCHEMA = vol.Schema({
    vol.Required("user_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_UNBLOCK_USER_SCHEMA = vol.Schema({
    vol.Required("user_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_SEND_STICKER_SCHEMA = vol.Schema({
    vol.Required("sticker_id"): cv.string,
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
    vol.Optional("type", default="0"): cv.string,
})

SERVICE_UNDO_MESSAGE_SCHEMA = vol.Schema({
    vol.Required("msg_id"): cv.string,
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
    vol.Optional("type", default="0"): cv.string,
})

SERVICE_CREATE_REMINDER_SCHEMA = vol.Schema({
    vol.Required("title"): cv.string,
    vol.Required("content"): cv.string,
    vol.Required("remind_time"): cv.string,
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
    vol.Optional("type", default="0"): cv.string,
})

SERVICE_REMOVE_REMINDER_SCHEMA = vol.Schema({
    vol.Required("reminder_id"): cv.string,
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
    vol.Optional("type", default="0"): cv.string,
})

SERVICE_CHANGE_GROUP_NAME_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("name"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_CHANGE_GROUP_AVATAR_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("image_path"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_SEND_VOICE_SCHEMA = vol.Schema({
    vol.Required("voice_path"): cv.string,
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
    vol.Optional("type", default="0"): cv.string,
})

SERVICE_GET_ALL_FRIENDS_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_RECEIVED_FRIEND_REQUESTS_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_SENT_FRIEND_REQUESTS_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_UNDO_FRIEND_REQUEST_SCHEMA = vol.Schema({
    vol.Required("friend_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_REMOVE_FRIEND_SCHEMA = vol.Schema({
    vol.Required("friend_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_CHANGE_FRIEND_ALIAS_SCHEMA = vol.Schema({
    vol.Required("friend_id"): cv.string,
    vol.Required("alias"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_REMOVE_FRIEND_ALIAS_SCHEMA = vol.Schema({
    vol.Required("friend_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_ALL_GROUPS_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_ADD_GROUP_DEPUTY_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("member_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_REMOVE_GROUP_DEPUTY_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("member_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_CHANGE_GROUP_OWNER_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("member_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_DISPERSE_GROUP_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_ENABLE_GROUP_LINK_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_DISABLE_GROUP_LINK_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_JOIN_GROUP_SCHEMA = vol.Schema({
    vol.Required("link"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_LEAVE_GROUP_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Optional("silent", default=False): cv.boolean,
    vol.Required("account_selection"): cv.string,
})

SERVICE_UPDATE_PROFILE_SCHEMA = vol.Schema({
    vol.Optional("name"): cv.string,
    vol.Optional("dob"): cv.string,
    vol.Optional("gender", default="0"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_UPDATE_SETTINGS_SCHEMA = vol.Schema({
    vol.Required("setting_type"): cv.string,
    vol.Required("status"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_SET_MUTE_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("duration"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_SET_PINNED_CONVERSATION_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("pinned"): cv.boolean,
    vol.Required("account_selection"): cv.string,
})

# Các schema cho API mới bổ sung thêm
SERVICE_GET_UNREAD_MARK_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_ADD_UNREAD_MARK_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_REMOVE_UNREAD_MARK_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_DELETE_CHAT_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_ARCHIVED_CHAT_LIST_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_AUTO_DELETE_CHAT_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_UPDATE_AUTO_DELETE_CHAT_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("ttl"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_HIDDEN_CONVERSATIONS_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_SET_HIDDEN_CONVERSATIONS_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("hidden"): cv.boolean,
    vol.Required("account_selection"): cv.string,
})

SERVICE_UPDATE_HIDDEN_CONVERS_PIN_SCHEMA = vol.Schema({
    vol.Required("pin"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_RESET_HIDDEN_CONVERS_PIN_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_MUTE_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_PIN_CONVERSATIONS_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_ADD_REACTION_SCHEMA = vol.Schema({
    vol.Required("icon"): cv.string,
    vol.Required("thread_id"): cv.string,
    vol.Required("msg_id"): cv.string,
    vol.Required("cli_msg_id"): cv.string,
    vol.Required("type"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_DELETE_MESSAGE_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("msg_id"): cv.string,
    vol.Required("cli_msg_id"): cv.string,
    vol.Required("uid_from"): cv.string,
    vol.Required("type"): cv.string,
    vol.Optional("only_me", default=True): cv.boolean,
    vol.Required("account_selection"): cv.string,
})

SERVICE_FORWARD_MESSAGE_SCHEMA = vol.Schema({
    vol.Required("message"): cv.string,
    vol.Required("thread_ids"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_PARSE_LINK_SCHEMA = vol.Schema({
    vol.Required("link"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_SEND_CARD_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("user_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_SEND_LINK_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("link"): cv.string,
    vol.Optional("message", default=""): cv.string,
    vol.Optional("thumbnail", default=""): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_STICKERS_SCHEMA = vol.Schema({
    vol.Required("query"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_STICKERS_DETAIL_SCHEMA = vol.Schema({
    vol.Required("sticker_album"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_SEND_VIDEO_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("video_path_or_url"): cv.string,
    vol.Optional("thumbnail_url", default=""): cv.string,
    vol.Optional("message", default=""): cv.string,
    vol.Optional("width", default=1280): cv.positive_int,
    vol.Optional("height", default=720): cv.positive_int,
    vol.Optional("ttl", default=0): vol.All(int, vol.Range(min=0)),
    vol.Optional("type", default="0"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_CREATE_NOTE_GROUP_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("title"): cv.string,
    vol.Optional("pin_act", default=True): cv.boolean,
    vol.Required("account_selection"): cv.string,
})

SERVICE_EDIT_NOTE_GROUP_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("topic_id"): cv.string,
    vol.Required("title"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_LIST_BOARD_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_CREATE_POLL_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("question"): cv.string,
    vol.Required("options"): cv.string,
    vol.Optional("allow_multi_choices", default=False): cv.boolean,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_POLL_DETAIL_SCHEMA = vol.Schema({
    vol.Required("poll_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_LOCK_POLL_SCHEMA = vol.Schema({
    vol.Required("poll_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_EDIT_REMINDER_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("topic_id"): cv.string,
    vol.Required("title"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_REMINDER_SCHEMA = vol.Schema({
    vol.Required("reminder_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_LIST_REMINDER_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_REMINDER_RESPONSES_SCHEMA = vol.Schema({
    vol.Required("reminder_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_ADD_QUICK_MESSAGE_SCHEMA = vol.Schema({
    vol.Required("keyword"): cv.string,
    vol.Required("title"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_QUICK_MESSAGE_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_REMOVE_QUICK_MESSAGE_SCHEMA = vol.Schema({
    vol.Required("item_ids"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_UPDATE_QUICK_MESSAGE_SCHEMA = vol.Schema({
    vol.Required("item_id"): cv.string,
    vol.Required("keyword"): cv.string,
    vol.Required("title"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_LABELS_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_BLOCK_VIEW_FEED_SCHEMA = vol.Schema({
    vol.Required("user_id"): cv.string,
    vol.Required("is_block_feed"): cv.boolean,
    vol.Required("account_selection"): cv.string,
})

SERVICE_CHANGE_ACCOUNT_AVATAR_SCHEMA = vol.Schema({
    vol.Required("avatar_source"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_AVATAR_LIST_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_LAST_ONLINE_SCHEMA = vol.Schema({
    vol.Required("user_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_SEND_TYPING_EVENT_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

# Các schema mới cho các dịch vụ bổ sung
SERVICE_GET_LOGGED_ACCOUNTS_SCHEMA = vol.Schema({})
SERVICE_GET_ACCOUNT_DETAILS_SCHEMA = vol.Schema({
    vol.Required("own_id"): str,
})
SERVICE_FIND_USER_SCHEMA = vol.Schema({
    vol.Required("phone"): str,
    vol.Required("account_selection"): str,
})
SERVICE_GET_USER_INFO_SCHEMA = vol.Schema({
    vol.Required("user_id"): str,
    vol.Required("account_selection"): str,
})
SERVICE_SEND_FRIEND_REQUEST_SCHEMA = vol.Schema({
    vol.Required("user_id"): str,
    vol.Required("account_selection"): str,
    vol.Optional("message", default="Xin chào, hãy kết bạn với tôi!"): str,
})
SERVICE_CREATE_GROUP_SCHEMA = vol.Schema({
    vol.Required("members"): str,
    vol.Optional("name"): str,
    vol.Optional("avatar_path"): str,
    vol.Required("account_selection"): str,
})
SERVICE_GET_GROUP_INFO_SCHEMA = vol.Schema({
    vol.Optional("group_id", default=""): str,
    vol.Optional("account_selection", default=""): str,
})
SERVICE_ADD_USER_TO_GROUP_SCHEMA = vol.Schema({
    vol.Required("group_id"): str,
    vol.Required("member_id"): str,
    vol.Required("account_selection"): str,
})
SERVICE_REMOVE_USER_FROM_GROUP_SCHEMA = vol.Schema({
    vol.Required("group_id"): str,
    vol.Required("member_id"): str,
    vol.Required("account_selection"): str,
})
SERVICE_SEND_IMAGE_TO_USER_SCHEMA = vol.Schema({
    vol.Required("image_path"): str,
    vol.Required("thread_id"): str,
    vol.Required("account_selection"): str,
})
SERVICE_SEND_IMAGES_TO_USER_SCHEMA = vol.Schema({
    vol.Required("image_paths"): str,
    vol.Required("thread_id"): str,
    vol.Required("account_selection"): str,
})
SERVICE_SEND_IMAGE_TO_GROUP_SCHEMA = vol.Schema({
    vol.Required("image_path"): str,
    vol.Required("thread_id"): str,
    vol.Required("account_selection"): str,
})
SERVICE_SEND_IMAGES_TO_GROUP_SCHEMA = vol.Schema({
    vol.Required("image_paths"): str,
    vol.Required("thread_id"): str,
    vol.Required("account_selection"): str,
})
SERVICE_GET_ACCOUNT_WEBHOOKS_SCHEMA = vol.Schema({})
SERVICE_GET_ACCOUNT_WEBHOOK_SCHEMA = vol.Schema({
    vol.Required("own_id"): str,
})
SERVICE_SET_ACCOUNT_WEBHOOK_SCHEMA = vol.Schema({
    vol.Required("own_id"): str,
    vol.Optional("message_webhook_url"): str,
    vol.Optional("group_event_webhook_url"): str,
    vol.Optional("reaction_webhook_url"): str,
})
SERVICE_DELETE_ACCOUNT_WEBHOOK_SCHEMA = vol.Schema({
    vol.Required("own_id"): str,
})
SERVICE_GET_PROXIES_SCHEMA = vol.Schema({})
SERVICE_ADD_PROXY_SCHEMA = vol.Schema({
    vol.Required("proxy_url"): str,
})
SERVICE_REMOVE_PROXY_SCHEMA = vol.Schema({
    vol.Required("proxy_url"): str,
})