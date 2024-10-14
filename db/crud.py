from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Chat, User, user_chat

"""Написать CRUD"""


class CRUDBase:

    def __init__(self, model):
        self.model = model

    async def get(
            self,
            obj_id,
            session: AsyncSession
    ):
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id
            )
        )
        return db_obj.scalar().first()


class UserCRUD(CRUDBase):

    async def add_user_list(
            self,
            objects_to_db: list[User],
            session: AsyncSession
    ):
        users = await session.execute(
            select(
                self.model.tg_user_id
            )
        )
        users = users.scalars().all()
        for obj in objects_to_db:
            if obj.tg_user_id not in users:
                session.add(obj)
        await session.commit()
        return objects_to_db


class ChatCRUD(CRUDBase):

    async def add_chat(
            self,
            object_to_db: Chat,
            session: AsyncSession
    ):

        chat = await session.get(self.model, object_to_db.tg_chat_id)
        if not chat:
            session.add(object_to_db)
        await session.commit()
        return object_to_db


class UserChatCRUD(CRUDBase):
    async def create_relation_multiple(
            self,
            users: list[User],
            chat_id: Chat,
            session: AsyncSession
    ):
        ids = [user.tg_user_id for user in users]
        user_ids = await session.execute(
            select(
                User.tg_user_id
            ).where(
                User.tg_user_id.in_(ids)
            )
        )
        user_ids = user_ids.scalars().all()
        chat_id = await session.execute(
            select(
                Chat
            ).where(
                Chat.tg_chat_id == chat_id.tg_chat_id
            )
        )
        chat = chat_id.scalar()
        for user in users:
            if user not in chat.user and user.tg_user_id not in user_ids:
                chat.user.append(user)
            else:
                user_from_db = await session.execute(
                    select(User).filter_by(tg_user_id=user.tg_user_id)
                )
                chat.user.append(user_from_db.scalar())
        await session.commit()
        return chat_id


user_crud = UserCRUD(User)
chat_crud = ChatCRUD(Chat)
user_chat_crud = UserChatCRUD(user_chat)
