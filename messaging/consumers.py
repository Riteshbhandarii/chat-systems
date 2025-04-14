import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Friend  # Import your existing Friend model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.other_username = self.scope["url_route"]["kwargs"].get("username")

        # Reject unauthenticated or missing username
        if isinstance(self.user, AnonymousUser) or not self.other_username:
            await self.close(code=4001)
            return

        try:
            # Get other user object
            self.other_user = await User.objects.aget(username=self.other_username)
        except User.DoesNotExist:
            await self.close(code=4004)  # User not found
            return

        # Validate friendship using your existing Friend model
        if not await self.are_friends():
            await self.close(code=4003)  # Not friends error
            return

        # Create sorted room name
        self.room_name = "_".join(sorted([self.user.username, self.other_username]))
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def are_friends(self):
        """Check friendship using your existing Friend model structure"""
        return await Friend.objects.filter(
            Q(user=self.user, friend=self.other_user) |
            Q(user=self.other_user, friend=self.user)
        ).aexists()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get("message", "").strip()

            if not message:
                return

            # Broadcast message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender": self.user.username,
                }
            )

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Invalid JSON"}))
        except Exception as e:
            print(f"Error in receive: {e}")
            await self.send(text_data=json.dumps({"error": "Server error"}))

    async def chat_message(self, event):
        """Send message to WebSocket"""
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
        }))

        