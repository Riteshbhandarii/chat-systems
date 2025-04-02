import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join the same chat room for all users
        self.room_name = 'chat_room'  # One single room for all users
        self.room_group_name = f'chat_{self.room_name}'

        # Join the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group when the WebSocket disconnects
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Receive a message from WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Broadcast the message to the group (all connected users)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from the group (this is sent to all WebSocket clients)
    async def chat_message(self, event):
        message = event['message']

        # Send the message to WebSocket (all connected clients)
        await self.send(text_data=json.dumps({
            'message': message
        }))
