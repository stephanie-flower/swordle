# game_server/consumers.py
import json
from threading import currentThread
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import redirect
from django.core.cache import cache
from game_model.dto.game_state import Coordinate
from game_model.dto.game_state import GameBoard
from game_model.json_interfaces.view_state import CharState

from .message_type import MessageType
from .game_state import GameState

class GameSessionConsumer(AsyncWebsocketConsumer):
    # room_id -> dict of room to (dict of GameBoard to player)
    room_boards = {}
    message_handlers = {}
    game_state = GameState.NOT_STARTED

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.message_handlers[MessageType.SUBMIT_WORD] = self.word_submit_handler
        self.message_handlers[MessageType.DISCONNECTED] = self.actual_disconnect

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']

        # Make the dictionary completely empty
        board = {}
        for row in range(0, 6):
            for col in range(0, 6):
                board[Coordinate(row, col)] = ''
        gBoard = GameBoard(board)

        # room_id -> player ids
        current_rooms = cache.get('current_rooms')
        if current_rooms is None:
            current_rooms = {}

        print(1)
        print(current_rooms)
        print(self.room_id)
        print(self.channel_name)

        if self.room_id in current_rooms:
            if len(current_rooms[self.room_id]) >= 2:
                return
            current_rooms[self.room_id].append(self.channel_name)
            self.room_boards[self.room_id][self.channel_name] = gBoard

            self.game_state = GameState.IN_GAME
        else:
            current_rooms[self.room_id] = [self.channel_name]
            self.room_boards[self.room_id] = {self.channel_name: gBoard}

            self.game_state = GameState.WAITING_FOR_PLAYERS

        print(2)
        print(current_rooms)
        print(self.room_id)
        print(self.channel_name)

        # Join session group with, giving the room_id and unique channel_name
        await self.channel_layer.group_add(
            self.room_id,
            self.channel_name
        )

        cache.set('current_rooms', current_rooms, None)

        print("!! STATE UPDATE !! - Player Connected!")
        print("GameState: %s" % self.game_state)

        await self.accept()

        await self.send(text_data=json.dumps({
            'payload': {
                'type': MessageType.CONNECTION_OPENED,
                'id': self.channel_name
            }
        }))

        await self.channel_layer.group_send(
            self.room_id,
            {
                'type': "send_to_room",
                'payload': {
                    'type': MessageType.STATE_UPDATE,
                    'state': self.game_state
                }
            }
        )

    async def disconnect(self, close_code):
        pass

    async def actual_disconnect(self, json_data):
        room_id = str(json_data['room'])
        player_id = json_data['id']

        current_rooms = cache.get('current_rooms')

        print(3)
        print(current_rooms)
        print(room_id)
        print(player_id)

        if player_id in current_rooms[room_id]:
            current_rooms[room_id].remove(player_id);
        # Leave session group
        await self.channel_layer.group_discard(
            room_id,
            player_id
        )

        print("!! STATE UPDATE !! - Player Disconnected!")

        current_rooms = cache.get('current_rooms')

        print("Room ID: %s\nPlayer Count: %s" % (room_id, current_rooms[room_id]))

        if len(current_rooms[room_id]) - 1 <= 0:
            del current_rooms[room_id]

        if (room_id in current_rooms):
            print("Room ID: %s\nNew Player Count: %s" % (room_id, current_rooms[room_id]))
        else:
            print("Room deleted!")

        cache.set('current_rooms', current_rooms, None)


    # Receive message from WebSocket
    async def receive(self, text_data):
        json_data = json.loads(text_data)
        print(json_data)
        await self.message_handlers[json_data['type']](json_data)

    async def word_submit_handler(self, json_data):
        payload = json_data['payload']
        room_id = str(json_data['room'])
        player_id = json_data['id']
        row = int(payload['row'])
        word = payload['word'].upper()

        target_word = "HACKER" # TODO: add a bank of words

        # Change the correct board to have the charStates and update
        room = self.room_boards[room_id]
        changedBoard = room[player_id]

        if word == target_word:
            # Send message to session group
            await self.channel_layer.group_send(
                room_id,
                {
                    'type': "send_to_room",
                    'payload': {
                        'type': MessageType.PLAYER_WIN,
                        'player': player_id
                    }
                }
            )
            return

        charStates = []
        for i in range(0, 6):
            if (word[i] == target_word[i]):
                charStates.append(CharState.CORRECT_PLACEMENT)
            elif (target_word[i].__contains__(word[i])):
                charStates.append(CharState.CORRECT_LETTER)
            else:
                charStates.append(CharState.INCORRECT)
            changedBoard.board[Coordinate(row, i)] = word[i]

        room[player_id] = changedBoard

        print(charStates)

        # Send message to session group
        # Does this work lmao?
        await self.channel_layer.group_send(
            room_id,
            {
                'type': "send_to_room",
                'payload': {
                    'type': MessageType.SUBMIT_WORD,
                    'player': player_id,
                    'row': row,
                    'values': charStates
                }
            }
        )

    # Receive message from room group
    async def send_to_room(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'payload': event['payload']
        }))
