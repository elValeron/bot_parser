import io
import openpyxl

from telethon.tl.functions.channels import GetFullChannelRequest

from config import bot_client, logger, PHONE, TOKEN, user_client
from exceptions import IncorrectLink
from messages import link_info_message
from vars import link_pattern
from db.models import User


def make_report(users: dict[str, User], file_name: str):
    """Формирование отчета в xlsx."""
    file = openpyxl.Workbook()
    file_bytes = io.BytesIO()
    ws = file.active
    ws.append(['ID', 'USERNAME', 'FIRST_NAME'])
    for value in users.values():
        user = [value.tg_user_id, value.username, value.first_name]
        ws.append(user)
    file.save(file_bytes)
    file_bytes.seek(0)
    file_bytes.name = file_name + '.xlsx'
    return file_bytes


def validate_channel_link(link: str) -> str:
    channel_postfix = link.replace(link_pattern, '')
    if len(channel_postfix.split()) == 1:
        return channel_postfix
    raise IncorrectLink(link_info_message)


def create_user_list(users):
    result = {}
    for sender in users:
        if sender.id not in result:
            user = User(
                tg_user_id=sender.id,
                username=sender.username if sender.username else '',
                first_name=sender.first_name
                )
            result[sender.id] = user
    return result


async def get_users(channel):
    channel_settings = await bot_client(GetFullChannelRequest(channel))
    if not channel_settings.full_chat.participants_hidden:
        return await bot_client.get_participants(channel)
    else:
        channel = await user_client.get_entity(
            channel.id
        )
        logger.debug(
            f'Получение 1000 последних сообщений чата {channel.username}'
        )
        messages = await user_client.get_messages(channel, limit=1000)
        return [message.sender for message in messages]


async def run_bot_client():
    await bot_client.start(bot_token=TOKEN)
    await bot_client.run_until_disconnected()


async def run_user_client():
    await user_client.start(phone=PHONE)
    await user_client.run_until_disconnected()
