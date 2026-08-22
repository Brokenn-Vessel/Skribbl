from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import uuid

ws_router = APIRouter()

class Player :
    def __init__(self, username: str, websocket: WebSocket) :
        self.username = username
        self.websocket = websocket

class Room : 
    def __init__(self, room_id) : 
        self.room_id = room_id
        self.players = []

    def add_player(self, player: Player) : 
        self.players.append(player) 

    def remove_player(self, player: Player) :
        self.players.remove(player) 

rooms: dict[str, Room] = {}

class SocketManager :
    def __init__(self) :
        self.active: dict[str, Player] = {}

    async def connect(self, player_uid: str, player: Player) :
        await player.websocket.accept()
        self.active[player_uid] = player

    async def disconnect(self, player_uid: str, player: Player) :
        self.active.pop(player_uid) 

    async def send_to_one(self, player_uid: str, message: str) :
        socket = self.active.get(player_uid).websocket
        await socket.send_text(message)

    async def send_to_room(self,room_id,  message: str) :
        for player in rooms[room_id].values() :
            await player.websocket.send_text(message)


manager = SocketManager()

@ws_router.websocket('/{room_id}')
async def websocket_endpoint(room_id: str, websocket: WebSocket, username: str, uid: str) :
    print(username, uid, room_id)

    if room_id not in rooms :
        rooms[room_id] = Room(room_id)

    player = Player(username, websocket)

    print("------------okay-----------------------")
    await manager.connect(uid, player) 

    rooms[room_id].add_player(player) 

    print(f'{player.username} joined the room {room_id}')
    try: 
        while True: 
            await websocket.receive_text()

    except WebSocketDisconnect:
        await manager.disconnect(uid, player)
        print(f'{player.username} left the room {room_id}')
        rooms[room_id].remove_player(player)

