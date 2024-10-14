from sqlalchemy import BigInteger, Column, String, ForeignKey, Table


from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from db.db_base import Base

user_chat = Table(
    'user_chat',
    Base.metadata,
    Column(
        'user_id',
        BigInteger,
        ForeignKey('user.tg_user_id'),
        primary_key=True
    ),
    Column(
        'chat_id',
        BigInteger,
        ForeignKey('chat.tg_chat_id'),
        primary_key=True
    )
)


class User(Base):
    username: Mapped[str] = mapped_column(String(100))
    first_name: Mapped[str] = mapped_column(String(100))
    tg_user_id: Mapped[BigInteger] = mapped_column(
        BigInteger,
        primary_key=True
    )
    chat: Mapped[list['Chat']] = relationship(
        secondary=user_chat,
        back_populates='user',
        lazy='selectin'
    )

    def __repr__(self) -> str:
        return (
            'создана запись пользователя: '
            f'{self.username} - {self.tg_user_id} '
        )


class Chat(Base):
    title: Mapped[str] = mapped_column(String(100))
    tg_chat_id: Mapped[BigInteger] = mapped_column(
        BigInteger,
        primary_key=True
    )
    user: Mapped[list['User']] = relationship(
        secondary=user_chat,
        back_populates='chat',
        lazy='selectin',
    )

    def __repr__(self) -> str:
        return (
            f'Чат: {self.title} ({self.tg_chat_id}) добавлен.'
        )
