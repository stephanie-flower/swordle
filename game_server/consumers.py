# game_server/consumers.py
import json
from threading import currentThread
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import redirect
from django.core.cache import cache

class GameSessionConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']

        current_rooms = cache.get('current_rooms')

        if current_rooms is None:
            current_rooms = {}

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
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to session group
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
