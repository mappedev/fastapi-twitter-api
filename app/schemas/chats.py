from datetime import datetime
from typing import List
from pydantic import BaseModel, root_validator

from models.chats import ChatTypes, MessageTypes
from schemas.users import UserSchema


class ChatSchema(BaseModel):
    id: int
    type: ChatTypes
    logo: str
    title: str
    created_at: datetime

    class Config:
        orm_mode = True


class ChatCreateSchema(BaseModel):
    type: ChatTypes = ChatTypes.SIMPLE
    title: str = ""
    logo: str = ""
    # participants: List[int]
    # admins: List[int] = []

    @root_validator
    def check_chat_by_type(cls, values):
        if values["type"] == ChatTypes.SIMPLE:
            # if len(values["participants"]) != 2:
            #     raise ValueError("Simple chat should have 2 participants")

            del values["title"]
            del values["logo"]
        else:
            if values["title"] == "":
                raise ValueError("Group chat should have a title")
            # if len(values["participants"]) < 2:
            #     raise ValueError(
            #         "Group chat should have at least 2 participants"
            #     )
            # if len(values["admins"]) < 1:
            #     raise ValueError("Group chat should have at least 1 admin")

        return values

    class Config:
        schema_extra = {"example": {"type": "simple"}}


class ChatAddParticipantsSchema(BaseModel):
    participants: List[int]


class ChatAddAdminsSchema(BaseModel):
    admins: List[int]


class ChatUpdateSchema(BaseModel):
    logo: str | None
    title: str | None

    def filter_fields_to_update(self):
        values = {}
        for k, v in self.dict().items():
            values[k] = v

        return values

    class Config:
        schema_extra = {"example": {"title": "New title"}}


# class Message(Base, Timestamp):
#     __tablename__ = "message"

#     id = Column(Integer, primary_key=True, index=True)
#     type = Column(Enum(MessageTypes, length=10), default=MessageTypes.TEXT)
#     content = Column(String(length=256))
#     chat_id = Column(Integer, ForeignKey("chat.id"))
#     owner_id = Column(Integer, ForeignKey("user.id"))

#     chat = relationship("Chat", back_populates="messages")
#     owner = relationship("User", back_populates="messages")
#     read_by = relationship(
#         "User",
#         secondary="user_message_read",
#         back_populates="messages_read",


class MessageCreateSchema(BaseModel):
    type: MessageTypes
    content: str
    chat_id: int
    owner_id: int


class MessageSchema(MessageCreateSchema):
    id: int
    readed_by: List[int] = []

    class Config:
        orm_mode = True


class ChatAllSchema(ChatSchema):
    messages: List[MessageSchema]
    participants: List[UserSchema]
    admins: List[UserSchema]
