# game_server/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GameSessionConsumer(AsyncWebsocketConsumer):
    room_count = {}

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

        return redirect('room/' + self.room_id);

    async def disconnect(self, close_code):
        # Leave session group
        await self.channel_layer.group_discard(
            self.room_id,
            self.channel_name
        )

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
