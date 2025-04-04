import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "global_chat"  # Single room for all users
        self.room_group_name = f"chat_{self.room_name}"

        # Join group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get("message", "").strip()

            if not message:
                return  # Ignore empty messages

            # Get sender's username (fallback to "Anonymous" if not logged in)
            user = self.scope["user"]
            username = user.username if not isinstance(user, AnonymousUser) else "Anonymous"

            # Broadcast to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender": username,  # Include sender
                    "is_authenticated": not isinstance(user, AnonymousUser),
                }
            )

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Invalid JSON"}))
        except Exception as e:
            print(f"Error in receive: {e}")

    async def chat_message(self, event):
        # Send message to WebSocket (frontend)
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "is_authenticated": event["is_authenticated"],
        }))