from datetime import datetime
import json
from typing import Annotated, List

from fastapi import (
    APIRouter,
    Depends,
    Header,
    status,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
)
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.chats import (
    ChatAddAdminsSchema,
    ChatAddParticipantsSchema,
    ChatAllSchema,
    ChatSchema,
    ChatCreateSchema,
    ChatUpdateSchema,
    MessageCreateSchema,
)
from services.chats import ChatService

from dependencies.commons import get_current_user, get_session
from libs.jwt import (
    decode_token_without_exception,
    get_authorization_header_token,
)
from utils.chats import ChatManager
from utils.commons import Tags

from db import models

router = APIRouter(prefix="/chats", tags=[Tags.chats.value])
service = ChatService()
manager = ChatManager()


@router.get(
    path="/",
    response_model=List[ChatSchema],
    status_code=status.HTTP_200_OK,
    summary="Get all chats",
    dependencies=[Depends(get_current_user)],
)
async def get_all_chats(db: Annotated[AsyncSession, Depends(get_session)]):
    """
    Get chats

    This path operation get all chats in the app.

    Returns a json list with the chat model
    - id: int
    - type: simple | group
    - logo: str | None
    - title: str
    - participants: List[User]
    - admins: List[User]
    """
    return await service.find_all_chats(db=db)


@router.get(
    path="/{chat_id}",
    response_model=ChatAllSchema,
    status_code=status.HTTP_200_OK,
    summary="Get chat",
    dependencies=[Depends(get_current_user)],
)
async def get_chat(
    chat_id: int, db: Annotated[AsyncSession, Depends(get_session)]
):
    """
    Get chat

    This path operation get a chat in the app.

    Parameters
    - Path parameter
        - chat_id: int

    Returns a json list with the chat model
    - id: int
    - type: simple | group
    - logo: str | None
    - title: str
    - participants: List[User]
    - admins: List[User]
    - messages: List[Message]
    """
    return await service.find_one_chat_by_id(
        id=chat_id,
        db=db,
        model_props_relation=[
            models.Chat.admins,
            models.Chat.participants,
            models.Chat.messages,
        ],
    )


@router.post(
    path="/",
    response_model=ChatSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create chat",
    dependencies=[Depends(get_current_user)],
)
async def create_chat(
    chat: ChatCreateSchema,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Post chat

    This path operation post a chat in the app.

    Parameters:
    - Request body parameter
        - chat: Chat

    Returns a json with the chat model
    - id: int
    - type: simple | group
    - logo: str | None
    - title: str
    - participants: List[User]
    - admins: List[User]
    - messages: List[Message]
    """
    return await service.create_chat(data=chat, db=db)


@router.put(
    path="/{chat_id}",
    response_model=ChatSchema,
    status_code=status.HTTP_200_OK,
    summary="Update chat",
    dependencies=[Depends(get_current_user)],
)
async def update_chat(
    chat_id: int,
    chat: ChatUpdateSchema,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Update chat

    This path operation update a chat in the app.

    Parameters
        - Path parameter
            - chat: int
        - Request body parameter
            - chat: Chat

    Returns a json with the chat model
    - id: int
    - type: simple | group
    - logo: str | None
    - title: str
    - participants: List[User]
    - admins: List[User]
    - messages: List[Message]
    """
    return await service.update_chat(id=chat_id, data=chat, db=db)


@router.delete(
    path="/{chat_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete chat",
    dependencies=[Depends(get_current_user)],
)
async def delete_chat(
    chat_id: int, db: Annotated[AsyncSession, Depends(get_session)]
) -> dict:
    """
    Delete chat

    This path operation delete a chat in the app.

    Parameters
    - Path parameter
        - chat_id: int

    Returns a json with the chat id and success property
    - id: int
    - success: bool
    """
    return await service.remove_chat(id=chat_id, db=db)


@router.post(
    path="/chat/{chat_id}/participants",
    status_code=status.HTTP_200_OK,
    summary="Add participants to chat",
    dependencies=[Depends(get_current_user)],
)
async def add_participant(
    chat_id: int,
    participants_data: ChatAddParticipantsSchema,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    return await service.add_participants_to_chat(
        id=chat_id,
        participants=participants_data.participants,
        db=db,
    )


@router.post(
    path="/chat/{chat_id}/admins",
    status_code=status.HTTP_200_OK,
    summary="Add admins to chat",
    dependencies=[Depends(get_current_user)],
)
async def add_admins(
    chat_id: int,
    admins_data: ChatAddAdminsSchema,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    return await service.add_admins_to_chat(
        id=chat_id,
        admins=admins_data.admins,
        db=db,
    )


@router.delete(
    path="/chat/{chat_id}/participants",
    status_code=status.HTTP_200_OK,
    summary="Remove participants from chat",
    dependencies=[Depends(get_current_user)],
)
async def remove_participants(
    chat_id: int,
    participants_data: ChatAddParticipantsSchema,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    return await service.remove_participants_from_chat(
        id=chat_id,
        participants=participants_data.participants,
        db=db,
    )


@router.delete(
    path="/chat/{chat_id}/admins",
    status_code=status.HTTP_200_OK,
    summary="Remove admins from chat",
    dependencies=[Depends(get_current_user)],
)
async def remove_admins(
    chat_id: int,
    admins_data: ChatAddAdminsSchema,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    return await service.remove_admins_from_chat(
        id=chat_id,
        admins=admins_data.admins,
        db=db,
    )


@router.websocket(path="/{chat_id}")
async def ws_chat(
    websocket: WebSocket,
    chat_id: int,
    db: Annotated[AsyncSession, Depends(get_session)],
    authorization: str = Header(...),
):
    token = get_authorization_header_token(authorization_header=authorization)
    if token is None:
        await websocket.close(code=4010, reason="Invalid token")
        return

    acc_tok_data = decode_token_without_exception(token=token)
    if acc_tok_data is None:
        await websocket.close(code=4010, reason="Not authenticated")
        return

    chat = await service.find_one_chat_by_id_without_exceptions(
        id=chat_id, db=db
    )
    if chat is None:
        await websocket.close(code=4040, reason="Chat not found")
        return

    await manager.connect(websocket=websocket, chat_id=chat_id)

    # current_time = datetime.now().strftime("%H:%M:%S")

    while True:
        try:
            data = json.loads(await websocket.receive_text())

            msg_type = data.get("type", "text")
            user_id = data.get("userId", None)
            msg_content = data.get("content", None)
            if user_id is None or msg_content is None:
                await manager.send_personal_message(
                    websocket=websocket,
                    message="Fields userId and content are required",
                )
                continue

            message = await service.create_message(
                data=MessageCreateSchema(
                    type=msg_type,
                    content=msg_content,
                    chat_id=chat.id,
                    owner_id=user_id,
                ),
                db=db,
            )
            await service.add_readed_to_message(
                id=chat_id,
                message_id=message.id,
                participants=[message.owner_id],
                db=db,
            )

            await manager.broadcast(
                message=json.dumps(
                    {
                        "time": message.created_at.strftime("%H:%M:%S"),
                        "chatId": message.chat_id,
                        "userId": message.owner_id,
                        "message": message.content,
                        "type": message.type,
                    }
                ),
                chats_id=[chat_id],
            )

        except json.JSONDecodeError:
            await manager.send_personal_message(
                websocket=websocket,
                message="Error: JSON data is required",
            )

        except WebSocketDisconnect:
            await manager.send_personal_message(
                websocket=websocket,
                message=f"Disconnected from {chat_id}",
            )
            await manager.disconnect(websocket=websocket, chat_id=chat_id)
            break

        except WebSocketException as ex:
            await manager.send_personal_message(
                websocket=websocket,
                message=f"Error: {str(ex)}",
            )
            await manager.disconnect(websocket=websocket, chat_id=chat_id)
            break
