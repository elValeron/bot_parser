from telethon import Button
from telethon.tl.types import (
    ReplyInlineMarkup,
    KeyboardButtonRow,
    KeyboardButtonCallback
)

from vars import (
    get_menu,
    parse_with_link,
    parse_without_link,
    parse_with_admin_rights,
    run_parsing_with_added,
    run_parsing_with_link
)


menu_button = Button.inline(text='Меню', data=b'get_menu')

main_menu = ReplyInlineMarkup(
    [
        KeyboardButtonRow(
            [
                KeyboardButtonCallback(
                    text='Спарсить по ссылке',
                    data=parse_with_link
                ),
                KeyboardButtonCallback(
                    text='Спарсить без ссылки',
                    data=parse_without_link
                )
            ],
        ),
        KeyboardButtonRow(
            [
                KeyboardButtonCallback(
                    text='Меню',
                    data=get_menu
                )
            ]
        )
    ]
)


get_link_keyboard = ReplyInlineMarkup(
    [
        KeyboardButtonRow(
            [
                KeyboardButtonCallback(
                    text='Далее',
                    data=run_parsing_with_link
                )
            ]
        ),
        KeyboardButtonRow(
            [
                KeyboardButtonCallback(
                    text='В начало',
                    data=get_menu
                )
            ]
        )
    ]
)

start_parse_chat = ReplyInlineMarkup(
    [
        KeyboardButtonRow(
            [
                KeyboardButtonCallback(
                    text='Выгрузить пользователей',
                    data=run_parsing_with_link
                )
            ]
        ),
        KeyboardButtonRow(
            [
                KeyboardButtonCallback(
                    text='Меню',
                    data=get_menu
                )
            ]
        )
    ]
)

parse_options = ReplyInlineMarkup(
    [
        KeyboardButtonRow(
            [
                KeyboardButtonCallback(
                    text='Без админки',
                    data=run_parsing_with_added
                )
            ]
        ),
        KeyboardButtonRow(
            [
                KeyboardButtonCallback(
                    text='Дать админку',
                    data=parse_with_admin_rights
                )
            ]
        ),
        KeyboardButtonRow(
            [
                KeyboardButtonCallback(
                    text='Меню',
                    data=get_menu
                )
            ]
        )
    ]
)
