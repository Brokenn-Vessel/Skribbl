from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import uuid, json, asyncio, random
from .room import Room
from .player import Player
from .words import words
from .manager import manager

ws_router = APIRouter()


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


            if data.get("type") == "guess" : 
                # data will be validated here 
                await room.broadcast(json.dumps(data))

            if data.get("type") == "start-game": 
                print("start") ;
                # check whether its the owner of the room or not
                if data.get("id") == room.owner: 
                # start round
                    await room.start_round()   
                else: 
                    print("This message didn't come from the owner of the room") 

            if data.get("type") == "word-select": 
                if data.get("id") == room.current_drawer_uid: 
                    print(f"selected word is {data.get("word")}") 

                    if room.timer_task is not None: 
                        room.timer_task.cancel() 
                        room.timer_task = None 

                    room.selectFrom = None
                    room.currentWord = data.get("word") 

                    await room.send_to_one(room.current_drawer_uid, json.dumps({
                        "type": "start-draw",
                        "word": room.currentWord,
                        "duration": room.guess_time
                    }))
                    await room.broadcast_except(room.current_drawer_uid, json.dumps({
                        "type": "guess-start",
                        "word_length": len(data.get("word")),
                        "drawer_name": room.players[room.current_drawer_uid].username,
                        "duration": room.guess_time
                    }))

                    # start-drawing
                    await room.draw_start()

                else: 
                    print("message didnt come from the original drawer")

            if data.get("type") == "draw-begin": 
                # print(data.get("x"), data.get("y"))
                if room.current_drawer_uid and room.current_drawer_uid == data.get("uid"): 
                    await room.broadcast(json.dumps({
                        "type": "draw-begin",
                        "clientX": data.get("clientX"),
                        "clientY": data.get("clientY"),
                    })) 

            if data.get("type") == "draw-cont": 
                # print(data.get("x"), data.get("y")) 
                if room.current_drawer_uid and room.current_drawer_uid == data.get("uid"): 
                    await room.broadcast(json.dumps({
                        "type": "draw-cont",
                        "clientX": data.get("clientX"),
                        "clientY": data.get("clientY"),
                    })) 

            if data.get("type") == "draw-end": 
                # print(data.get("x"), data.get("y"))
                if room.current_drawer_uid and (room.current_drawer_uid in room.players) and (room.current_drawer_uid == data.get("uid")): 
                    await room.broadcast(json.dumps({
                        "type": "draw-end",
                        "clientX": data.get("clientX"),
                        "clientY": data.get("clientY"),
                    })) 


    except WebSocketDisconnect:
        await room.disconnect(uid)
        if room.is_empty() : 
            manager.terminate_room(room.room_id) 
        print(f'{player.username} left the room {room_id}')