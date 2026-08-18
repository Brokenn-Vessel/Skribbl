from fastapi import WebSocket 
from ..http.main import app 

rooms = {}

class socketManager :
    def __init__(self) :
        self.active = dict[str, WebSocket] = {}

    async def connect(self, player_uid: str, websocket: WebSocket) :
        await websocket.accept()
        self.active[player_uid] = websocket

    async def disconnect(self, player_uid: str, websocket: WebSocket) :
        self.active.pop(player_uid) 

    async def send_to_one(self, player_uid: str, message: str) :
        socket = self.active.get(player_uid)
        await socket.send_text(message)

    async def send_to_all(self, message: str) :
        for socket in self.active.values() :
            await socket.send_text(message)


# @app.websocket('/ws/{room_id}')
# async def websocket_endpoint(websocket: WebSocket) 