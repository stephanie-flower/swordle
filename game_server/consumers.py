# game_server/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .message_type import MessageType

class GameSessionConsumer(AsyncWebsocketConsumer):
    room_count = {}
    message_handlers = {}

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.message_handlers[MessageType.KEY_INPUT] = self.key_input_handler

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']

        if self.room_id in self.room_count:
            if self.room_count[self.room_id] >= 2:
                return
            self.room_count[self.room_id] += 1;
        else:
            self.room_count[self.room_id] = 1;

        # Join session group with, giving the room_id and unique channel_name
        await self.channel_layer.group_add(
            self.room_id,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        self.room_count[self.room_id] -= 1;
        # Leave session group
        await self.channel_layer.group_discard(
            self.room_id,
            self.channel_name
        )

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
