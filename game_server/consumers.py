# game_server/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GameSessionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_name = self.scope['url_route']['kwargs']['game_name']
        self.session_group_name = 'game_%s' % self.session_name

        # Join session group
        await self.channel_layer.group_add(
            self.session_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave session group
        await self.channel_layer.group_discard(
            self.session_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to session group
        await self.channel_layer.group_send(
            self.session_group_name,
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