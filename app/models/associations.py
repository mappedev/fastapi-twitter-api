from sqlalchemy import Column, ForeignKey, Integer, Table

from db.base import Base


class ChatUserParticipant(Base):
    __tablename__ = "chat_user_participant"

    chat_id = Column(Integer, ForeignKey("chat.id"), primary_key=True)
    participant_id = Column(Integer, ForeignKey("user.id"), primary_key=True)


class ChatUserAdmin(Base):
    __tablename__ = "chat_user_admin"
    chat_id = Column(Integer, ForeignKey("chat.id"), primary_key=True)
    admin_id = Column(Integer, ForeignKey("user.id"), primary_key=True)


class UserMessageRead(Base):
    __tablename__ = "user_message_read"
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    message_id = Column(Integer, ForeignKey("message.id"), primary_key=True)
