from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import uuid, json, asyncio, random

ws_router = APIRouter()

words = [
    "jellyfish", "castle", "avocado", "thunder", "pencil",
    "submarine", "dragonfly", "coffee", "lighthouse", "zombie",
    "pinecone", "rocket", "sandcastle", "butterfly", "guitar",
    "whirlpool", "elephant", "snowboard", "mirror", "volcano",
    "headphones", "island", "cheetah", "calculator", "fireplace",
    "apple", "skeleton", "raincoat", "telescope", "wizard",
    "hamburger", "moonstone", "parrot", "waterfall", "bicycle",
    "strawberry", "robot", "forest", "spaceship", "anchor",
    "chocolate", "detective", "cactus", "lightning", "penguin",
    "sandwich", "pyramid", "snowflake", "camera", "marshmallow",
    "rainbow", "motorcycle", "garden", "dinosaur", "trumpet",
    "keyboard", "pirate", "firework", "seashell", "umbrella",
    "mountain", "football", "moonlight", "toothbrush", "airplane",
    "treasure", "windmill", "cheesecake", "desert", "stargazer",
    "skateboard", "lantern", "crocodile", "bookstore", "thunderstorm",
    "pineapple", "vampire", "rainforest", "snowman", "spacesuit",
    "newspaper", "volleyball", "wizardry", "timepiece", "helmet",
    "camera", "avocado", "fireball", "strawberry", "lighthouse",
    "backpack", "tornado", "window", "mermaid", "spaceship",
    "diamond", "cactus", "waterfall", "parrot", "volcano"
]

class Player :
    def __init__(self, username: str, websocket: WebSocket) :
        self.username = username
        self.websocket = websocket

class Room :
    def __init__(self, room_id, select_time=5, guess_time=60) :
        self.room_id = room_id
        self.players: dict[str, Player] = {}
        self.owner: str | None = None
        self.select_time = select_time
        self.guess_time = guess_time
        self.timer_task: asyncio.Task | None = None
        self.current_drawer_uid: str | None = None
        self.selectFrom: list | None = None
        self.currentWord: str | None = None

    # uid --> Player (username, websocket) 
    async def connect(self, uid: str, player: Player) : 
        await player.websocket.accept() 
        self.players[uid] = player

        # first player becomes the owner
        if self.owner is None: 
            self.owner = uid

        message = json.dumps({
            "type": "join",
            "new_player": player.username,
            "players": self.get_player_list(),
            "owner": self.owner
        })

        await self.broadcast(message=message) 

    async def disconnect(self, uid: str) :
        leftName = self.players[uid].username ;
        self.players.pop(uid) 
        if (self.owner == uid):
            if(len(self.players) > 0): 
                first_key = next(iter(self.players))
                self.owner = first_key 
            else: 
                self.owner = None

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

    async def broadcast_except(self, exceptPlayer: str | None, message: str): 
        for id, player in self.players.items(): 
            if id != exceptPlayer: 
                await player.websocket.send_text(message)

    def is_empty(self) : 
        return len(self.players) == 0

    def get_player_list(self) : 
        return [
            {"uid": uid, "username": player.username, "is_owner": self.owner == uid} for uid, player in self.players.items() 
        ]

    async def selection_callback(self): 
        if self.selectFrom is not None:
            self.currentWord = self.selectFrom[0]
            print(self.currentWord)
            await self.broadcast(json.dumps({
                "type": "word_to_guess",
                "length": len(self.currentWord)
            }))
             

    async def game_timer(self, callback): 
        try: 
            await asyncio.sleep(self.select_time)
            await callback()

        except asyncio.CancelledError:
            pass 



    async def start_round(self): 
        # create a dict (player_id: hasDrawn) at the beginning of the round, this list will be used to track whether a player has drawn yet or not
        drawerList = {player_id: False for player_id in self.players.keys()}

        print(drawerList)

        # choose a drawer
        self.current_drawer_uid = self.choose_drawer(drawerList)

        print(self.current_drawer_uid)

        # get three words to choose from
        selectFrom = [words[i] for i in (random.randint(0, 99) for _ in range(3))]
        self.selectFrom = selectFrom
        print(self.selectFrom)

        # send drawer the three words
        await self.send_to_one(self.current_drawer_uid, json.dumps({
            "type": "select",
            "words": selectFrom,
            "time_limit": self.select_time
        }))
        # start the timer
        self.timer_task = asyncio.create_task(self.game_timer(self.selection_callback))

        # send everyone else waiting prompt
        await self.broadcast_except(self.current_drawer_uid, json.dumps({
            "type": "wait",
            "drawer_name":  self.players[self.current_drawer_uid].username,
            "duration": self.select_time
        }))


    def choose_drawer(self, drawerList):
        for id, hasDrawn in drawerList.items(): 
            if (id in self.players.keys()) and (hasDrawn is False): 
                return id 
        


class RoomManager :
    def __init__(self) : 
        self.rooms: dict[str, Room] = {}

    def get_or_create_room(self, room_id, owner = None) : 
        if room_id not in self.rooms : 
            self.rooms[room_id] = Room(room_id) 
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

            if data.get("type") == "start-game": 
                print("start") ;

                # start round
                await room.start_round()   


    except WebSocketDisconnect:
        await room.disconnect(uid)
        if room.is_empty() : 
            manager.terminate_room(room.room_id) 
        print(f'{player.username} left the room {room_id}')

