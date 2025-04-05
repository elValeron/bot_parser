
###
![Bot parser](https://github.com/elValeron/bot_parser)

## Бот для парсинга пользователей из Telegram чата


# Описание: 
    - Бот парсер позволяет собрать username и user_id из открытых Telegram групп и получить данные в xlsx файле.

# Стэк:
```
    - Язык программирования - Python 3.11.
    - Фреймворк работы с TG API и TG Bot API - Telethon 1.36
    - Библиотека работы с БД - SQLAlchemy 2.0
    - Миграции БД - Alembic 1.13
    - Сервер сбора метрик prometheus - prometheus-async 22.2
    - Метрики prometheus - prometheus-client 0.21
```

Проект реализован с помощью сервиса контейниризации Docker.

1. ### Запуск сервиса в докер контейнерах:
    Для запуска бота необходимо получить API_ID и API_HASH в личном кабинете ![Telegram](https://my.telegram.org/)

    - На виртуальной машине, сервере или локально создайте директорию в которой будет хранится проект
        
        - Перейдите в каталог, в котором хранится проект, командой:
            ```
            - cd <dir_name>/
            ```
        - Склонируйте репозиторий командой:
            ```
            - git clone https://github.com/elValeron/bot_parser.git
            ```
        - Создайте по шаблону env_example собственный файл (.env), с данными для создания сессии и подключения к бд.

        - Загрузите контейнеры командой: 
            ```
            docker compose -f docker-compose.yaml pull
            ```
        - Для создания файла сессии запустите контейнер bot командой:
            ```
            docker compose -f docker-compose.yaml run bot
            ```
        После чего в терминале появится предложение для ввода короткого кода для авторизации в ТГ, так же вам придёт служебное уведомление в телеграм с коротким кодом.
        ВВедите код в терминале, и остановите контейнер нажав ctrl+c
        - Запустите docker-compose.yaml командой:
        ```
            docker compose -f docker-compose.yaml up -d
        ```

        ### Поздравляю! Можно приступить к работе с ботом! :+1:
        
2. ### Запуск бота для отладки: 
    - На локальной машине создайте директорию в которой будет хранится проект
        - Перейдите в каталог, в котором хранится проект, командой:
            ```
            - cd <dir_name>/
            ```
        - Склонируйте репозиторий командой:
            ```
            - git clone https://github.com/elValeron/bot_parser.git
            ```
        - Перейдите в директорию bot_parser/ и установите виртуальное окружение командами:
            ```
            - cd bot_parser
            ```
            Виртуальное окружение для win:
            ```
            - python -m venv venv 
            ```
            Виртуальное окружение для Linux\Mac:
            ```
            - python3.9 -m venv venv
            ```
        - Активируйте виртуальное окружение и установите зависимости командами:
            Для Linux/Mac:
            ```
            - source venv/bin/activate
            - pip install -r requirements.txt
            ```
            Для win:
            ```
            - source venv/Script/activate
            - pip install -r requirements.txt
            ```
        - создать файл .env по шаблону, для использования sqlite заполните переменную:
            **При работе с sqlite не заполняйте переменные связанные с postgresql
        ```
            DATABASE_URL=sqlite:///./test.db
        ```
        - Выполните команду:
        ```
            alembic upgrade head
        ```
        Запустите бота командой:
        ```
            python main.py
        ```
        Терминал предложит ввести короткий код отправленный системным уведомлением в Телеграм, введите этот код.
        ### Поздравляю, проект готов к дебагу, удачи! :+1:


Автор [elValeron](https://github.com/elValeron/)