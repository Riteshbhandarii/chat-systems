import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WebSocket connected")
        await self.accept()

    async def disconnect(self, close_code):
        print("WebSocket disconnected")
        pass

    async def receive(self, text_data):
        print("Message received:", text_data)
        await self.send(text_data=json.dumps({
            'message': 'Hello, this is a response!'
        }))
