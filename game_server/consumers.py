# game_server/consumers.py
import json
from threading import currentThread
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import redirect
from django.core.cache import cache

from .message_type import MessageType

class GameSessionConsumer(AsyncWebsocketConsumer):
    # room_id -> array of GameBoard
    room_boards = {}
    message_handlers = {}

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.message_handlers[MessageType.KEY_INPUT] = self.key_input_handler

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
            self.room_boards[self.room_id].append(gBoard)
        else:
            current_rooms[self.room_id] = [self.channel_name]
            self.room_boards[self.room_id] = [gBoard]

        if self.room_id in current_rooms:
            if current_rooms[self.room_id] >= 2:
                await self.disconnect()
                return
            current_rooms[self.room_id] += 1
        else:
            current_rooms[self.room_id] = 1

        # Join session group with, giving the room_id and unique channel_name
        await self.channel_layer.group_add(
            self.room_id,
            self.channel_name
        )

        cache.set('current_rooms', current_rooms, None)

        print("!! STATE UPDATE !! - Player Connected!")

        await self.accept()

    async def disconnect(self, close_code):
        self.room_count[self.room_id] -= 1;
        # Leave session group
        await self.channel_layer.group_discard(
            self.room_id,
            self.channel_name
        )

        print("!! STATE UPDATE !! - Player Disconnected!")

        current_rooms = cache.get('current_rooms')

        print("Room ID: %s\nPlayer Count: %s" % (self.room_id, current_rooms[self.room_id]))

        if (current_rooms[self.room_id] - 1) > 0:
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
        await self.message_handlers[MessageType.KEY_INPUT](json_data)

    async def key_input_handler(self, json_data):
        message = json_data['message']
        # Send message to session group
        print(message)
        await self.channel_layer.group_send(
            self.room_id,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
