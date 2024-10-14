from telethon.sync import events
from telethon.tl.types import MessageActionChatAddUser


def filter_is_chat_user_added(
        event: events.ChatAction.Event,
        sender_id
) -> bool:
    return (
        event.action_message
        and isinstance(
            event.action_message.action, MessageActionChatAddUser
        ) and event.added_by.id == sender_id
    )
