from fastapi import WebSocket

class Player :
    def __init__(self, username: str, websocket: WebSocket) :
        self.username = username
        self.websocket = websocket
