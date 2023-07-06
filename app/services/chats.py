from typing import List, Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import QueryableAttribute

from db import models
from models.chats import ChatTypes
from schemas.chats import (
    ChatCreateSchema,
    ChatUpdateSchema,
    MessageCreateSchema,
)


class ChatService(object):
    CHAT_EXCEPTION_404 = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Chat not found",
    )

    MESSAGE_EXCEPTION_404 = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Chat not found",
    )

    async def find_all_chats(self, db: AsyncSession) -> Sequence[models.Chat]:
        # chats = db.query(models.Chat).all()
        result = await db.execute(
            select(models.Chat).order_by(models.Chat.id.desc())
        )
        chats = result.scalars().all()
        return chats

    async def find_one_chat_by_id(
        self,
        id: int,
        db: AsyncSession,
        model_props_relation: List[QueryableAttribute] = [],
    ) -> models.Chat:
        # chat = db.query(models.Chat).filter(models.Chat.id == id).first()
        query = select(models.Chat).where(models.Chat.id == id)

        if model_props_relation:
            query_options = []
            for model_prop in model_props_relation:
                query_options.append(selectinload(model_prop))

            query = query.options(*query_options)

        result = await db.execute(query)
        chat = result.scalars().first()
        if chat is None:
            raise self.CHAT_EXCEPTION_404

        return chat

    async def find_one_chat_by_id_without_exceptions(
        self,
        id: int,
        db: AsyncSession,
        model_props_relation: List[QueryableAttribute] = [],
    ) -> models.Chat | None:
        # chat = db.query(models.Chat).filter(models.Chat.id == id).first()
        query = select(models.Chat).where(models.Chat.id == id)

        if model_props_relation:
            query_options = []
            for model_prop in model_props_relation:
                query_options.append(selectinload(model_prop))

            query = query.options(*query_options)

        result = await db.execute(query)
        chat = result.scalars().first()
        return chat

    async def create_chat(
        self,
        data: ChatCreateSchema,
        db: AsyncSession,
    ) -> models.Chat:
        chat = models.Chat(**data.dict())
        db.add(chat)
        await db.commit()
        await db.refresh(chat)
        return chat

    async def update_chat(
        self,
        id: int,
        data: ChatUpdateSchema,
        db: AsyncSession,
    ) -> models.Chat:
        # chat = db.query(models.Chat).filter(models.Chat.id == id).first()
        result = await db.execute(
            select(models.Chat).where(models.Chat.id == id)
        )
        chat = result.scalars().first()
        if chat is None:
            raise self.CHAT_EXCEPTION_404

        update_data = data.filter_fields_to_update()
        for k, v in update_data.items():
            setattr(chat, k, v)

        await db.commit()
        await db.refresh(chat)
        return chat

    async def remove_chat(
        self, id: int, db: AsyncSession
    ) -> dict[str, int | bool]:
        # chat = db.query(models.Chat).filter(models.Chat.id == id).first()
        result = await db.execute(
            select(models.Chat).where(models.Chat.id == id)
        )
        chat = result.scalars().first()
        if chat is None:
            raise self.CHAT_EXCEPTION_404

        await db.delete(chat)
        await db.commit()
        return {"id": id, "success": True}

    async def add_participants_to_chat(
        self,
        id: int,
        participants: List[int],
        db: AsyncSession,
    ) -> dict:
        result = await db.execute(
            select(models.Chat)
            .where(models.Chat.id == id)
            .options(selectinload(models.Chat.participants))
        )
        chat = result.scalars().first()
        if chat is None:
            raise self.CHAT_EXCEPTION_404

        if chat.type == ChatTypes.SIMPLE and len(chat.participants) >= 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Simple chat should have 2 participants",
            )

        users_id_added = []
        for participant_id in participants:
            result = await db.execute(
                select(models.User).where(models.User.id == participant_id)
            )
            user = result.scalars().first()
            if user is not None:
                chat.participants.append(user)
                users_id_added.append(user.id)

        await db.commit()
        await db.refresh(chat)
        return {
            "chat_id": chat.id,
            "participants_added": users_id_added,
            "success": True,
        }

    async def add_admins_to_chat(
        self,
        id: int,
        admins: List[int],
        db: AsyncSession,
    ) -> dict:
        result = await db.execute(
            select(models.Chat)
            .where(models.Chat.id == id)
            .options(
                selectinload(models.Chat.admins),
                selectinload(models.Chat.participants),
            )
        )
        chat = result.scalars().first()
        if chat is None:
            raise self.CHAT_EXCEPTION_404

        if chat.type == ChatTypes.SIMPLE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Simple chat should not have admins",
            )

        users_id_added = []
        for admin_id in admins:
            result = await db.execute(
                select(models.User).where(models.User.id == admin_id)
            )
            user = result.scalars().first()
            if user is not None:
                if user in chat.participants:
                    chat.admins.append(user)
                    users_id_added.append(user.id)

        await db.commit()
        await db.refresh(chat)
        return {
            "chat_id": chat.id,
            "admins_added": users_id_added,
            "success": True,
        }

    async def remove_participants_from_chat(
        self,
        id: int,
        participants: List[int],
        db: AsyncSession,
    ) -> dict:
        result = await db.execute(
            select(models.Chat)
            .where(models.Chat.id == id)
            .options(selectinload(models.Chat.participants))
        )
        chat = result.scalars().first()
        if chat is None:
            raise self.CHAT_EXCEPTION_404

        users_id_removed = []
        for participant_id in participants:
            result = await db.execute(
                select(models.User).where(models.User.id == participant_id)
            )
            user = result.scalars().first()
            if user is not None:
                if user in chat.participants:
                    chat.participants.remove(user)
                    users_id_removed.append(user.id)

        await db.commit()
        await db.refresh(chat)
        return {
            "chat_id": chat.id,
            "participants_removed": users_id_removed,
            "success": True,
        }

    async def remove_admins_from_chat(
        self,
        id: int,
        admins: List[int],
        db: AsyncSession,
    ) -> dict:
        result = await db.execute(
            select(models.Chat)
            .where(models.Chat.id == id)
            .options(selectinload(models.Chat.admins))
        )
        chat = result.scalars().first()
        if chat is None:
            raise self.CHAT_EXCEPTION_404

        users_id_removed = []
        for admin_id in admins:
            result = await db.execute(
                select(models.User).where(models.User.id == admin_id)
            )
            user = result.scalars().first()
            if user is not None:
                if user in chat.admins:
                    chat.admins.remove(user)
                    users_id_removed.append(user.id)

        await db.commit()
        await db.refresh(chat)
        return {
            "chat_id": chat.id,
            "admins_removed": users_id_removed,
            "success": True,
        }

    async def find_all_messages(
        self, db: AsyncSession
    ) -> Sequence[models.Message]:
        result = await db.execute(
            select(models.Message).order_by(models.Message.id.desc())
        )
        messages = result.scalars().all()
        return messages

    async def create_message(
        self,
        data: MessageCreateSchema,
        db: AsyncSession,
    ) -> models.Message:
        message = models.Message(**data.dict())
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message

        # self,
        # id: int,
        # admins: List[int],
        # db: AsyncSession,

    async def add_readed_to_message(
        self,
        id: int,
        message_id: int,
        participants: List[int],
        db: AsyncSession,
    ) -> dict:
        result = await db.execute(
            select(models.Chat)
            .where(models.Chat.id == id)
            .options(selectinload(models.Chat.participants))
        )
        chat = result.scalars().first()
        if chat is None:
            raise self.CHAT_EXCEPTION_404

        result = await db.execute(
            select(models.Message)
            .where(models.Message.id == message_id)
            .options(selectinload(models.Message.read_by))
        )
        message = result.scalars().first()
        if message is None:
            raise self.MESSAGE_EXCEPTION_404

        users_id_added = []
        for participant_id in participants:
            result = await db.execute(
                select(models.User).where(models.User.id == participant_id)
            )
            user = result.scalars().first()
            if user is not None:
                if user in chat.participants:
                    message.read_by.append(user)
                    users_id_added.append(user.id)

        await db.commit()
        await db.refresh(message)
        return {
            "message_id": message.id,
            "participants_added": users_id_added,
            "success": True,
        }
