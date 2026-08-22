from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import secrets
import string
import uuid

http_router = APIRouter()
rooms = {}

def generate_roomId() :
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits 
    room_id = "".join(secrets.choice(characters) for _ in range(8)) 
    return room_id

# an endpoint to get a new room created
@http_router.get('/get_room') 
async def get_room(username: str) :
    room_id = generate_roomId() 

    return {
        "room_id": room_id,
        "owner": username
    }


@http_router.get('/get_uid')
async def get_uid(username: str) : 
    uid = uuid.uuid4() ;
    return {
        "uid": str(uid)
    }