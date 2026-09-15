import uuid, json, asyncio, random, time
from .player import Player
from .words import words

class Room :
    def __init__(self, room_id, select_time=2, guess_time=10, maxRounds=3) :
        self.room_id = room_id
        self.players: dict[str, Player] = {}
        self.owner: str | None = None
        self.select_time = select_time
        self.guess_time = guess_time
        self.timer_task: asyncio.Task | None = None
        self.timer_prompt: asyncio.Task | None = None
        self.current_drawer_uid: str | None = None
        self.selectFrom: list | None = None
        self.currentWord: str | None = None
        self.drawer_list: dict[str, bool] | None = None
        self.score_list: dict[str, int] = {}
        self.hasGuessed: dict[str, bool] = {}
        self.guessing: bool | None = False
        self.maxRounds = maxRounds
        self.maxScore = 500
        self.round = 0
        self.starting_time: int | None = None

    # uid --> Player (username, websocket) 
    async def connect(self, uid: str, player: Player) : 
        await player.websocket.accept() 
        self.players[uid] = player
        self.score_list[uid] = 0

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

        self.score_list.pop(uid)

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


    # ------------------------------------------------------------------------------------------------------------------------------------------------

    def is_empty(self) : 
        return len(self.players) == 0

    def get_player_list(self) : 
        return [
            { "uid": uid, "username": player.username, "is_owner": self.owner == uid, "score": self.score_list[uid] } for uid, player in self.players.items() 
        ]

    # -----------------------------------------------------------CALLBACKS----------------------------------------------------------------------------

    async def selection_callback(self): 
        if self.selectFrom is not None:

            self.currentWord = self.selectFrom[0]
            print(self.currentWord)

            await self.send_to_one(self.current_drawer_uid, json.dumps({
                "type": "start-draw",
                "word": self.currentWord,
                "duration": self.guess_time
            }))

            await self.broadcast_except(self.current_drawer_uid, json.dumps({
                "type": "guess-start",
                "word_length": len(self.currentWord),
                "drawer_name": self.players[self.current_drawer_uid].username,
                "duration": self.guess_time
            }))

            self.selectFrom = None
            self.timer_task = None

            self.draw_start()

             
    async def guess_callback(self): 
        self.starting_time = None 
        
        await self.broadcast(json.dumps({
            "type": "stop-draw",
            "drawer": self.current_drawer_uid,
            "word": self.currentWord,
            "players": self.get_player_list()
        }))

        await self.timer(1)

        await self.end_round()

    # -------------------------------------------------------------------------------------------------------------------------------------------------


    #----------------------------------------------TIMER-----------------------------------------------------------------------------------------------

    # if guess = false, timer is being used for selection of word else if guess=True its being used for guessing
    async def game_timer(self, callback, guess=False): 
        try: 
            wait_time = self.select_time if guess is not True else self.guess_time
            if guess: 
                self.starting_time = time.time()
            await asyncio.sleep(wait_time) 
            await callback()

        except asyncio.CancelledError:
            pass 


    # normal timer for prompting
    async def timer(self, time=1): 
        await asyncio.sleep(time)

    #---------------------------------------------------------------------------------------------------------------------------------------------------


    def draw_start(self): 
        self.guessing = True
        self.hasGuessed = {}
        self.timer_task = asyncio.create_task(self.game_timer(self.guess_callback, guess=True))
        # self.timer_task.

    async def start_round(self): 

        if self.round >= self.maxRounds: 

            await self.end_round()
            return 

        await self.broadcast(json.dumps({
            "type": "round-start-prompt",
            "round": self.round + 1,
            "duration": 5
        }))

        await asyncio.sleep(1)

        # create a dict (player_id: hasDrawn) at the beginning of the round, this list will be used to track whether a player has drawn yet or not
        self.drawer_list = {player_id: False for player_id in self.players.keys()}
        print(self.drawer_list)

        await self.select_start()


    async def select_start(self): 
        # choose a drawer
        self.current_drawer_uid = self.choose_drawer(self.drawer_list)

        # no one left to draw case
        if self.current_drawer_uid is None: 
            await self.end_round()

        print(self.current_drawer_uid)

        # get three words to choose from
        selectFrom = [words[i] for i in (random.randint(0, 99) for _ in range(3))]
        self.selectFrom = selectFrom

        print(self.selectFrom)

        # start the timer
        self.timer_task = asyncio.create_task(self.game_timer(self.selection_callback))

        # send drawer the three words
        await self.send_to_one(self.current_drawer_uid, json.dumps({
            "type": "select",
            "words": selectFrom,
            "time_limit": self.select_time
        }))

        # send everyone else waiting prompt
        await self.broadcast_except(self.current_drawer_uid, json.dumps({
            "type": "wait",
            "drawer_name":  self.players[self.current_drawer_uid].username,
            "duration": self.select_time
        }))


    async def end_round(self): 
        if self.current_drawer_uid and self.drawer_list: 
            self.drawer_list[self.current_drawer_uid] = True

        self.current_drawer_uid = None
        self.currentWord = None
        self.selectFrom = None 
        self.guessing = False
        self.hasGuessed = {}
        self.starting_time = None

        if self.drawer_list and False in self.drawer_list.values():
            await self.select_start()  
        else: 
            if self.round < self.maxRounds: 
                self.drawer_list = None
                self.round += 1
                await self.start_round()     
            else: 
                # display Leaderboards  
                await self.broadcast(json.dumps({
                    "type": "game-over",
                    "owner": self.owner
                }))

    async def restart(self): 
        self.reset_room()

        await self.broadcast(json.dumps({
            "type": "restart-prompt"
        }))

        await self.timer(3)

        await self.start_round()


    # -------------------------------------------------HELPERS------------------------------------------------------------------------------------

    def choose_drawer(self, drawerList):
        for id, hasDrawn in drawerList.items(): 
            if (id in self.players.keys()) and (hasDrawn is False): 
                return id 

        return None

    # ccheck whether the guess is correct or not
    def check(self, message: str): 
        to_guess = self.currentWord.strip().lower().split()

        print(to_guess)
        guess = message.strip().lower().split()

        print(guess)

        if len(to_guess) != len(guess): 
            return False

        for i in range(len(to_guess)): 
            if to_guess[i] != guess[i]: 
                return False

        return True

    def score(self, guess_time): 
        if self.starting_time is None: 
            return None
        time_elapsed = guess_time - self.starting_time
        s = int(self.maxScore * (1 - (time_elapsed/self.guess_time)))
        s = s - (s%10)

        return s

    def reset_room(self): 
        self.timer_task = None
        self.timer_prompt = None
        self.current_drawer_uid = None
        self.selectFrom = None
        self.currentWord = None
        self.drawer_list = None
        self.score_list = {}
        self.hasGuessed = {}
        self.guessing = False
        self.round = 0
        self.starting_time = None

