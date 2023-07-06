from typing import TYPE_CHECKING

from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.orm import relationship

from db.base import Base
from .commons import Timestamp

if TYPE_CHECKING:
    from .tweets import Tweet

    # from .chats import Chat, Message
    from .chats import Chat
    from .associations import ChatUserParticipant


class User(Base, Timestamp):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String(length=64))
    first_name = Column(String(length=50))
    last_name = Column(String(length=50))
    birth_date = Column(Date, nullable=True)

    tweets = relationship("Tweet", back_populates="by")
    messages = relationship("Message", back_populates="owner")
    chats_as_participant = relationship(
        "Chat",
        secondary="chat_user_participant",
        back_populates="participants",
    )
    chats_as_admin = relationship(
        "Chat",
        secondary="chat_user_admin",
        back_populates="admins",
    )
    messages_read = relationship(
        "Message",
        secondary="user_message_read",
        back_populates="read_by",
    )
