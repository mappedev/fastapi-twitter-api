import enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.base import Base
from .commons import Timestamp

if TYPE_CHECKING:
    from .users import User


class ChatTypes(str, enum.Enum):
    SIMPLE = "simple"
    GROUP = "group"


class MessageTypes(str, enum.Enum):
    TEXT = "text"
    FILE = "file"


class Chat(Base, Timestamp):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(ChatTypes, length=10), default=ChatTypes.SIMPLE)
    logo = Column(String(length=256), default="")
    title = Column(String(length=256), default="")

    messages = relationship("Message", back_populates="chat")
    participants = relationship(
        "User",
        secondary="chat_user_participant",
        back_populates="chats_as_participant",
    )
    admins = relationship(
        "User",
        secondary="chat_user_admin",
        back_populates="chats_as_admin",
    )


#     def validate(self, *args, **kwargs):
#         if self.type == ChatTypes.SIMPLE:
#             if not len(self.participants) == 2:
#                 raise ValueError(
#                     'Simple chat must have exactly two participants',
#                 )
#             if self.admins or self.title or self.logo:
#                 raise ValueError(
#                     'Simple chat cannot have a title or logo or admins',
#                 )
#         elif self.type == ChatTypes.GROUP:
#             if len(self.participants) < 2:
#                 raise ValueError(
#                     'Group chat must have at least two participants',
#                 )
#             if len(self.admins) < 1:
#                 raise ValueError('Group chat must have at least one admin')
#             if not self.title:
#                 raise ValueError('Group chat must have a title')


class Message(Base, Timestamp):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(MessageTypes, length=10), default=MessageTypes.TEXT)
    content = Column(String(length=256))
    chat_id = Column(Integer, ForeignKey("chat.id"))
    owner_id = Column(Integer, ForeignKey("user.id"))

    chat = relationship("Chat", back_populates="messages")
    owner = relationship("User", back_populates="messages")
    read_by = relationship(
        "User",
        secondary="user_message_read",
        back_populates="messages_read",
    )
