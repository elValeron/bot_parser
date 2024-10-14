import asyncio

from dotenv import load_dotenv
from prometheus_async.aio.web import start_http_server
from sqlalchemy.exc import IntegrityError
from telethon.sync import events
from telethon.errors.rpcerrorlist import (
    ChatAdminRequiredError,
    ChannelPrivateError
    )
from telethon.errors.rpcbaseerrors import (
    TimedOutError,
    ServerError,
    UnauthorizedError
)

from config import bot_client, logger, SERVER_PORT
from db.crud import chat_crud, user_crud, user_chat_crud
from db.models import Chat, User
from db.db_base import get_async_session
from exceptions import IncorrectLink
from filters import filter_is_chat_user_added
from keyboards import main_menu, menu_button, start_parse_chat, parse_options
from messages import (
    link_info_message,
    start_message,
    parsing_via_adding_to_chat,
    timeout_message,
    private_setting_error

)
from metrics import (
    ADDITION_TO_CHAT,
    CLICKS_ON_THE_STUB,
    CORRECT_LINK,
    INCORRECT_LINK,
    PARSING_FAILED_PERMISSION_DENIED,
    PARSING_FAILED_VALUE_ERROR,
    SUCCESSFULLY_PARSING,
    TIMEOUT_TO_ADD_TO_CHAT,
    TOTAL_FAILED_ATTEMPS
)
from utils import (
    create_user_list,
    get_users,
    make_report,
    run_bot_client,
    run_user_client,
    validate_channel_link,
)
from vars import (
    get_menu,
    link_pattern,
    parse_with_link,
    parse_without_link,
    parse_with_admin_rights,
    run_parsing_with_added,
    run_parsing_with_link
)


load_dotenv()


class UserChat:
    def __init__(self, username: str):
        self.username = username
        self.chat_id = None

    def __repr__(self):
        return f"UserChat(username={self.username}, chat_id={self.chat_id})"


database = {}


@bot_client.on(
        event=events.CallbackQuery(pattern=get_menu)
)
@bot_client.on(
    event=events.NewMessage(
        pattern=r'/start',
        func=lambda e: e.is_private
    )
)
async def start(event: events.NewMessage.Event):
    try:

        username = (
            event.sender.username
            if event.sender.username
            else event.sender.first_name
        )
        logger.debug(
            f'Инициализация пользователя {username}'
        )
        database[event.sender_id] = UserChat(username=username)
        logger.debug(
            f'Отправка меню пользователю {event.sender_id}'
        )
        menu = await event.respond(
            message=start_message,
            buttons=main_menu
        )

        logger.debug(
            f'Меню отправлено пользователю {event.sender_id},'
            f' message_id: {menu.id}'
        )
        await event.delete()
    except AttributeError as error:
        logger.warning(
            f'у пользователя нет username и first_name: {str(error)}'
        )
    except TimedOutError as error:
        logger.critical(f'Соединение разорвано - {str(error)}')


@bot_client.on(events.CallbackQuery(pattern=parse_with_link))
async def parse_with_link(event: events.CallbackQuery.Event):
    await event.delete()
    logger.debug(
        f'Удаление сообщения с выбором типа парсинга {event.message_id}'
                 )
    user_id = event.sender_id
    logger.debug(
        f'Создание контекста диалога с пользователем {user_id}'
    )
    async with bot_client.conversation(user_id) as conv:
        logger.debug(
            f'Отправка сообщения с примером ссылки пользователю {user_id}'
        )
        await conv.send_message(
            link_info_message.format(link=link_pattern),
            buttons=menu_button
        )
        logger.debug(
            f'Сообщение с примером ссылки доставлено пользователю {user_id}'
        )
        while True:
            try:
                logger.debug(
                    'Ожидание ссылки на группу '
                    f' от пользователя {user_id}'
                )
                handle = await conv.wait_event(
                    events.NewMessage(
                        pattern=link_pattern,
                        from_users=user_id
                    ),
                    timeout=300
                )
                logger.debug(
                    f'Ссылка на канал {handle.message.message}'
                    f'от {user_id} получена'
                )
                channel_username = validate_channel_link(
                    handle.message.message
                )
                logger.debug(
                    f'ссылка {channel_username} полученная от '
                    f'{user_id} корректна'
                )
                database[user_id].chat_id = channel_username
                logger.debug(
                    f'Отправка пользователю "{user_id}"'
                    ' сообщения с запросом на выгрузку'
                    )
                request = await conv.send_message(
                    'Выгрузить пользователей',
                    buttons=start_parse_chat
                )
                logger.debug(
                    f'Сообщение {request.id} '
                    f'пользователю {user_id} с запросом доставлено'
                )
                CORRECT_LINK.inc()
                break
            except (ValueError, IncorrectLink) as error:
                logger.critical(f'Не корректная ссылка - {str(error)}')
                await conv.send_message(
                    f'Некорректная ссылка - {handle.message.message}\n'
                    'Пришлите ссылку заново'
                )
                TOTAL_FAILED_ATTEMPS.inc()
                INCORRECT_LINK.inc()
            except TimeoutError:
                TOTAL_FAILED_ATTEMPS.inc()
                logger.warning(
                    'Вышло время ожидания ссылки '
                    f'для пользователя {user_id}')
                await conv.send_message(
                    timeout_message
                )
                await start(event)
                return


@bot_client.on(
    events.CallbackQuery(
        pattern=parse_without_link
    )
)
async def start_parse_without_link(event: events.CallbackQuery.Event):
    logger.debug(
        'Отправка сообщения с инструкцией по добавления в чат'
    )
    await event.respond(message=parsing_via_adding_to_chat)
    logger.debug(f'Сообщение доставлено {event.sender.id}')
    try:
        logger.debug(
            'Ожидание добавления бота в чат пользователем {event.sender_id}'
        )
        async with bot_client.conversation(event.sender_id) as conv:
            handle = conv.wait_event(
                events.ChatAction(
                        func=lambda e: filter_is_chat_user_added(
                            e,
                            event.sender_id
                            )
                ),
                timeout=300
            )
            future = await handle
            logger.debug(
                f'Бот добавлен в чат: {future.chat.title} '
                f'пользователем {future.added_by}'
                )
            database[event.sender_id].chat_id = future.chat_id
            ADDITION_TO_CHAT.inc()
            await conv.send_message(
                message=(
                    f'Добавлен в чат {future.chat.title}\n'
                    'Выберите вариант парсинга.'
                ),
                buttons=parse_options
            )
    except TimeoutError as error:
        TIMEOUT_TO_ADD_TO_CHAT.inc()
        TOTAL_FAILED_ATTEMPS.inc()
        logger.critical(f'Вышло время ожидания{str(error)}')
        await event.respond(timeout_message)
        await start(event)
        await event.delete()
    except AttributeError as error:
        TOTAL_FAILED_ATTEMPS.inc()
        logger.fatal(f'{str(error)}')
    except KeyError as error:
        TOTAL_FAILED_ATTEMPS.inc()
        logger.critical(
            f'Пользователь {str(error)} не инициализирован'
        )
        await start(event)


@bot_client.on(
        events.CallbackQuery(
            pattern=parse_with_admin_rights
        )
)
async def parse_with_admin_rights(
    event: events.CallbackQuery.Event
):
    CLICKS_ON_THE_STUB.inc()
    logger.debug(f'{event.sender.id} - нажал на заглушку')
    await event.respond('Функционал в разработке')


@bot_client.on(
        events.CallbackQuery(
            pattern=run_parsing_with_added
        )
)
@bot_client.on(
    events.CallbackQuery(
        pattern=run_parsing_with_link,
    )
)
async def start_parse_with_link(event: events.CallbackQuery.Event):
    '''Процесс парсинга, ответ должен быть сформированный отчёт в xlsx'''
    chat_id = database[event.sender_id].chat_id
    try:
        logger.debug(f'Получение сущности чата {chat_id}')
        channel = await bot_client.get_entity(chat_id)
        logger.debug(
            f'Сущность чата {channel.username} - {channel.id} получена'
        )
        users = await get_users(channel)
        logger.debug(
            f'Данные пользователей из чата {channel.username} получены'
        )
        to_db = create_user_list(users)
        chat_info = Chat(title=channel.username, tg_chat_id=channel.id)
        logger.debug(
            'Загрузка пользователей в BD'
        )
        await create_chat_with_users(to_db.values(), chat_info)
        logger.debug('Формирование отчёта в xlsx')
        file = make_report(to_db, channel.username)
        logger.debug(
            f'Отправка отчёта по чату {channel.username} '
            f'Пользователю {event.sender_id}'
            )
        await event.respond(channel.username, file=file)

        database[event.sender_id].chat_id = None
        if event.data == run_parsing_with_added:
            logger.debug(
                f'Удаление бота из чата {channel.username}'
            )
            await bot_client.delete_dialog(channel)
        await event.respond(
            message='Выберите действие',
            buttons=main_menu
        )
        SUCCESSFULLY_PARSING.inc()
    except ValueError as e:
        PARSING_FAILED_VALUE_ERROR.inc()
        TOTAL_FAILED_ATTEMPS.inc()
        await event.respond(f'Произошла ошибка {str(e)}')
    except (ChannelPrivateError, ChatAdminRequiredError):
        PARSING_FAILED_PERMISSION_DENIED.inc()
        TOTAL_FAILED_ATTEMPS.inc()
        await event.respond(private_setting_error)


async def create_chat_with_users(users: list[User], chat: Chat):
    try:
        async for session in get_async_session():
            chat_from_db = await chat_crud.add_chat(chat, session)
            users_list = await user_crud.add_user_list(users, session)
            await user_chat_crud.create_relation_multiple(
                users_list,
                chat_from_db,
                session
            )
    except IntegrityError as error:
        logger.critical(
            f'{str(error)}, данные не записаны'
        )
        session.rollback()


async def main():
    try:
        await asyncio.gather(
            start_http_server(port=SERVER_PORT),
            run_bot_client(),
            run_user_client()
        )
    except (
        TimedOutError,
        ServerError,
        UnauthorizedError
    ) as error:
        logger.fatal(
            f'Ошибка соединения {str(error)}'
        )

if __name__ == '__main__':
    try:
        logger.info('Бот запущен')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info('Бот остановлен')
    except ConnectionError as error:
        logger.fatal(f'{str(error)}')
    except EOFError as error:
        logger.fatal(f'{str(error)}')
