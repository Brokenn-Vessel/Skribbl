from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import uuid, json

ws_router = APIRouter()

class Player :
    def __init__(self, username: str, websocket: WebSocket) :
        self.username = username
        self.websocket = websocket

class Room :
    def __init__(self, room_id) :
        self.room_id = room_id
        self.players: dict[str, Player] = {}

    # uid --> Player (username, websocket) 
    async def connect(self, uid: str, player: Player) : 
        await player.websocket.accept() 
        self.players[uid] = player

        message = json.dumps({
            "type": "join",
            "new_player": player.username,
            "players": self.get_player_list()
        })

        await self.broadcast(message=message) 

    async def disconnect(self, uid: str) :
        leftName = self.players[uid].username ;
        self.players.pop(uid) 

        message = json.dumps({
            "type": "leave",
            "player_left": leftName,
            "players": self.get_player_list()
        })

        await self.broadcast(message=message) 

    async def send_to_one(self, uid: str, message: str) :
        await self.players[uid].websocket.send_text(message)

    async def broadcast(self, message: str) : 
        for player in self.players.values() :
            await player.websocket.send_text(message)

    def is_empty(self) : 
        return len(self.players) == 0

    def get_player_list(self) : 
        return [
            {"uid": uid, "username": player.username} for uid, player in self.players.items() 
        ]



class RoomManager :
    def __init__(self) : 
        self.rooms: dict[str, Room] = {}

    def get_or_create_room(self, room_id, owner = None) : 
        if room_id not in self.rooms : 
            self.rooms[room_id] = Room(room_id) 
            # --------------------------------------------define owner here ;
        return self.rooms[room_id] 

    def is_room_empty(self, room_id: str) : 
        return len(self.rooms[room_id].players) == 0

    def terminate_room(self, room_id: str) : 
        self.rooms.pop(room_id)   


manager = RoomManager()

@ws_router.websocket('/{room_id}')
async def websocket_endpoint(room_id: str, websocket: WebSocket, username: str, uid: str) :
    print(username, uid, room_id)

    # id room doen't exist new room is created
    # if room_id not in manager.rooms :
    room = manager.get_or_create_room(room_id)
    player = Player(username, websocket)



    await room.connect(uid=uid, player=player) 
    print("*********rooms_info******************")



    for r in manager.rooms.values() : 
        print(r.room_id) 
    print("*********rooms_info******************")




    print(f'{player.username} joined the room {room_id}')


    try: 
        while True: 
            data = await websocket.receive_text()

            data = json.loads(data) 

            # print(data.get("type")) 

            if data.get("type") == "guess" : 
                # data will be validated here 
                await room.broadcast(json.dumps(data))

    except WebSocketDisconnect:
        await room.disconnect(uid)
        if room.is_empty() : 
            manager.terminate_room(room.room_id) 
        print(f'{player.username} left the room {room_id}')

