from typing import List

from fastapi import WebSocket
from fastapi.websockets import WebSocketState


class ChatManager:
    def __init__(self):
        self.active_connections: dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chat_id: int):
        await websocket.accept()

        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = [websocket]
        else:
            self.active_connections[chat_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, chat_id: int):
        self.active_connections[chat_id].remove(websocket)

        if not self.active_connections[chat_id]:
            del self.active_connections[chat_id]

    async def send_personal_message(self, websocket: WebSocket, message: str):
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_text(message)

    async def broadcast(self, message: str, chats_id: List[int]):
        for to_chat_id in chats_id:
            if to_chat_id in self.active_connections.keys():
                for websocket in self.active_connections[to_chat_id]:
                    if websocket.client_state == WebSocketState.CONNECTED:
                        await websocket.send_text(message)
