from .room import Room

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