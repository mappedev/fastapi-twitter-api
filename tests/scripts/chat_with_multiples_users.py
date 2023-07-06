import asyncio
import json
import random
import websockets

USERS_ID = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
TEXT_MESSAGES = [
    {"id": 1, "content": "Hola!"},
    {"id": 2, "content": "Cómo estás?"},
    {"id": 3, "content": "Qué planes tienes para hoy?"},
    {"id": 4, "content": "Te gustaría salir a caminar?"},
    {"id": 5, "content": "Qué opinas de la nueva película de Marvel?"},
    {"id": 6, "content": "Te gusta la pizza?"},
    {"id": 7, "content": "Qué música te gusta?"},
    {"id": 8, "content": "Cómo te fue en el trabajo hoy?"},
    {"id": 9, "content": "Qué deportes te gustan?"},
    {"id": 10, "content": "Te gusta viajar?"},
    {"id": 11, "content": "Qué libros te gustan?"},
    {"id": 12, "content": "Te gusta ir al cine?"},
    {"id": 13, "content": "Qué opinas del cambio climático?"},
    {"id": 14, "content": "Te gusta la playa?"},
    {"id": 15, "content": "Qué tal si nos encontramos mañana?"},
    {"id": 16, "content": "Te gusta la cerveza?"},
    {"id": 17, "content": "Qué opinas de la política actual?"},
    {"id": 18, "content": "Te gusta cocinar?"},
    {"id": 19, "content": "Qué planes tienes para el fin de semana?"},
    {"id": 20, "content": "Te gusta el fútbol?"}
]

async def test():
    async with websockets.connect('ws://localhost:8000/api/v1/chats/1') as ws:
        for i, msg in enumerate(TEXT_MESSAGES):
            await ws.send(json.dumps({
                'userId': random.randint(1, 20),
                'content': msg['content']
            }))
            response = await ws.recv()
            print(i + 1, msg['id'], response)

asyncio.get_event_loop().run_until_complete(test())
