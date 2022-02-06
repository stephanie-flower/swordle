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

class GameSessionConsumer(AsyncWebsocketConsumer):
    # room_id -> dict of room to (dict of GameBoard to player)
    room_boards = {}
    message_handlers = {}

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.message_handlers[MessageType.SUBMIT_WORD] = self.word_submit_handler

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

        if self.room_id in current_rooms:
            if len(current_rooms[self.room_id]) >= 2:
                return
            current_rooms[self.room_id].append(self.channel_name)
            self.room_boards[self.room_id][self.channel_name] = gBoard
        else:
            current_rooms[self.room_id] = [self.channel_name]
            self.room_boards[self.room_id] = {self.channel_name: gBoard}

        # Join session group with, giving the room_id and unique channel_name
        await self.channel_layer.group_add(
            self.room_id,
            self.channel_name
        )

        cache.set('current_rooms', current_rooms, None)

        print("!! STATE UPDATE !! - Player Connected!")

        await self.accept()

        await self.send(text_data=json.dumps({
            'payload': {
                'type': MessageType.CONNECTION_OPENED,
                'id': self.channel_name
            }
        }))

    async def disconnect(self, close_code):
        current_rooms = cache.get('current_rooms')
        if self.channel_name in current_rooms[self.room_id]:
            current_rooms[self.room_id].remove(self.channel_name);
        # Leave session group
        await self.channel_layer.group_discard(
            self.room_id,
            self.channel_name
        )

        print("!! STATE UPDATE !! - Player Disconnected!")

        current_rooms = cache.get('current_rooms')

        print("Room ID: %s\nPlayer Count: %s" % (self.room_id, current_rooms[self.room_id]))

        if len(current_rooms[self.room_id]) - 1 > 0:
            current_rooms[self.room_id] -= 1
        else:
            del current_rooms[self.room_id]

        if (self.room_id in current_rooms):
            print("Room ID: %s\nNew Player Count: %s" % (self.room_id, current_rooms[self.room_id]))
        else:
            print("Room deleted!")

        cache.set('current_rooms', current_rooms, None)


    # Receive message from WebSocket
    async def receive(self, text_data):
        json_data = json.loads(text_data)
        print(json_data)
        await self.message_handlers[MessageType.SUBMIT_WORD](json_data)

    async def word_submit_handler(self, json_data):
        payload = json_data['payload']
        print(payload)

        row = int(payload['row'])
        word = payload['word'].upper()
        target_word = "HACKER"

        # Change the correct board to have the charStates and update
        room = self.room_boards[self.room_id]
        changedBoard = room[self.channel_name]

        charStates = []
        for i in range(0, 6):
            if (word[i] == target_word[i]):
                charStates.append(CharState.CORRECT_PLACEMENT)
            elif (target_word[i].__contains__(word[i])):
                charStates.append(CharState.CORRECT_LETTER)
            else:
                charStates.append(CharState.INCORRECT)
            changedBoard.board[Coordinate(row, i)] = word[i]

        room[self.channel_name] = changedBoard

        print(charStates)

        # Send message to session group
        await self.channel_layer.group_send(
            self.room_id,
            {
                'type': "send_to_room",
                'payload': {
                    'type': MessageType.SUBMIT_WORD,
                    'player': self.channel_name,
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
