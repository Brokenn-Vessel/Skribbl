from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import secrets
import string

app = FastAPI()
rooms = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=['*'],
)

def generate_roomId() :
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits 
    room_id = "".join(secrets.choice(characters) for _ in range(8)) 
    return room_id

# an endpoint to get a new room created
@app.get('/get_room') 
async def get_room(username: str) :
    room_id = generate_roomId() 

    return {
        "room_id": room_id,
        "owner": username
    }