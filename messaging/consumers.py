import json
import logging
import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.db.models import Q
from asgiref.sync import sync_to_async
from django.core.cache import cache
from .models import Friend, Message, Groupchat, Groupmchatmessage

logger = logging.getLogger(__name__)

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.other_username = self.scope["url_route"]["kwargs"].get("username")

        # Reject unauthenticated users or if username is missing
        if isinstance(self.user, AnonymousUser) or not self.other_username:
            await self.close(code=4001)
            return

        try:
            # Get the other user object
            self.other_user = await sync_to_async(User.objects.get)(username=self.other_username)
        except User.DoesNotExist:
            await self.close(code=4004)  # User not found
            return

        # Validate friendship using the existing Friend model
        if not await self.are_friends():
            await self.close(code=4003)  # Not friends error
            return

        # Create a sorted room name for the chat
        self.room_name = "_".join(sorted([self.user.username, self.other_username]))
        self.room_group_name = f"chat_{self.room_name}"

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Fetch previous messages
        messages = await self.get_previous_messages()
        for message_data in messages:
            await self.send(text_data=json.dumps(message_data))

    @sync_to_async
    def get_previous_messages(self):
        """Fetch previous messages in a sync context and prepare them for sending"""
        messages_data = []

        previous_messages = Message.objects.filter(
            (Q(sender=self.user) & Q(receiver=self.other_user)) |
            (Q(sender=self.other_user) & Q(receiver=self.user))
        ).order_by('timestamp')

        for message in previous_messages:
            messages_data.append({
                'message': message.content,
                'sender': message.sender.username,
                'timestamp': message.timestamp.isoformat(),
                'id': message.id,
                'read': message.read,
            })

        return messages_data

    @sync_to_async
    def are_friends_sync(self):
        """Check if the users are friends using the Friend model (sync version)"""
        return Friend.objects.filter(
            Q(user=self.user, friend=self.other_user) |
            Q(user=self.other_user, friend=self.user)
        ).exists()
        
    async def are_friends(self):
        """Async wrapper for are_friends_sync"""
        return await self.are_friends_sync()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get("action")

            if action == "mark_seen":
                message_id = data.get("message_id")
                success = await self.mark_message_seen(message_id)
                if success:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "message_read",
                            "message_id": message_id,
                        }
                    )
            else:
                message_content = data.get("message", "").strip()
                if not message_content:
                    return

                # Save the new message to the database
                message = await self.create_message(message_content)

                # Broadcast the message to the room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "message": message_content,
                        "sender": self.user.username,
                        "timestamp": message.timestamp.isoformat(),
                        "id": message.id,
                    }
                )

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Invalid JSON"}))
        except Exception as e:
            print(f"Error in receive: {e}")
            await self.send(text_data=json.dumps({"error": "Server error"}))

    @sync_to_async
    def mark_message_seen(self, message_id):
        """Marks a message as read in a synchronous context."""
        try:
            message = Message.objects.get(id=message_id)
            if message.receiver == self.user and not message.read:
                message.read = True
                message.save()
                return True
            return False
        except Message.DoesNotExist:
            return False

    @sync_to_async
    def create_message(self, message_content):
        """Creates a new message in a synchronous context."""
        return Message.objects.create(
            sender=self.user,
            receiver=self.other_user,
            content=message_content,
            timestamp=datetime.datetime.now(),
            read=False
        )

    async def chat_message(self, event):
        """Send a new message to the WebSocket client"""
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "timestamp": event.get("timestamp", datetime.datetime.now().isoformat()),
            "id": event["id"],
        }))

    async def message_read(self, event):
        """Notify the client that a message has been read"""
        await self.send(text_data=json.dumps({
            "type": "message_read",
            "message_id": event["message_id"],
        }))


class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        try:
            # Convert group_id to integer and validate
            self.group_id = int(self.scope["url_route"]["kwargs"]["group_id"])
        except (KeyError, ValueError, TypeError):
            logger.error(f"Invalid group ID format: {self.scope['url_route']['kwargs'].get('group_id')}")
            await self.close(code=4000)  # Invalid group ID format
            return

        # Reject unauthenticated users
        if isinstance(self.user, AnonymousUser):
            logger.warning(f"Anonymous user attempted to connect to group {self.group_id}")
            await self.close(code=4001)
            return

        try:
            # Get group and verify membership
            self.group = await sync_to_async(Groupchat.objects.get)(id=self.group_id)
            
            # Proper membership check
            is_member = await sync_to_async(
                lambda: self.group.members.filter(id=self.user.id).exists()
            )()
            
            if not is_member:
                logger.warning(f"User {self.user.id} is not member of group {self.group_id}")
                await self.close(code=4003)  # Not a member
                return

            self.room_group_name = f"group_chat_{self.group.id}"
            
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            logger.info(f"User {self.user.id} connected to group {self.group_id}")
            
            # Send previous messages
            messages = await self.get_previous_group_messages()
            for message in messages:
                await self.send(text_data=json.dumps(message))
                
        except Groupchat.DoesNotExist:
            logger.error(f"Group {self.group_id} not found")
            await self.close(code=4004)  # Group not found
        except Exception as e:
            logger.error(f"Group connection error: {str(e)}")
            await self.close(code=4000)

    @sync_to_async
    def get_previous_group_messages(self):
        """Fetch previous group messages with read status"""
        messages_data = []
        previous_messages = Groupmchatmessage.objects.filter(
            group_chat=self.group
        ).select_related('sender').prefetch_related('read_by').order_by('timestamp')

        for message in previous_messages:
            messages_data.append({
                'type': 'group_message',
                'message': message.content,
                'sender': message.sender.username,
                'sender_id': message.sender.id,
                'timestamp': message.timestamp.isoformat(),
                'id': message.id,
                'group_id': self.group.id,
                'read_by': [user.id for user in message.read_by.all()],
            })

        return messages_data

    @sync_to_async
    def create_message(self, message_content):
        """Create new group message"""
        message = Groupmchatmessage.objects.create(
            sender=self.user,
            group_chat=self.group,
            content=message_content,
            timestamp=datetime.datetime.now(),
        )
        return message

    @sync_to_async
    def mark_message_seen(self, message_id):
        """Mark message as read by current user"""
        try:
            message = Groupmchatmessage.objects.get(id=message_id)
            if not message.read_by.filter(id=self.user.id).exists():
                message.read_by.add(self.user)
                return True
            return False
        except Groupmchatmessage.DoesNotExist:
            return False

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"User {getattr(self, 'user', None)} disconnected from group {getattr(self, 'group_id', None)}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get("action")

            if action == "mark_seen":
                if message_id := data.get("message_id"):
                    if success := await self.mark_message_seen(message_id):
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                "type": "message_read",
                                "message_id": message_id,
                                "reader_id": self.user.id,
                                "reader_username": self.user.username,
                                "group_id": self.group.id
                            }
                        )
            elif message_content := data.get("message", "").strip():
                message = await self.create_message(message_content)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "group_chat_message",
                        "message": message_content,
                        "sender": self.user.username,
                        "sender_id": self.user.id,
                        "timestamp": message.timestamp.isoformat(),
                        "id": message.id,
                        "group_id": self.group.id
                    }
                )
                    
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Invalid JSON"}))
        except Exception as e:
            logger.error(f"Message handling error: {str(e)}")
            await self.send(text_data=json.dumps({
                "error": "Server error",
                "details": str(e)
            }))

    async def group_chat_message(self, event):
        """Handle sending new group messages"""
        await self.send(text_data=json.dumps({
            "type": "group_message",
            "message": event["message"],
            "sender": event["sender"],
            "sender_id": event["sender_id"],
            "timestamp": event["timestamp"],
            "id": event["id"],
            "group_id": event["group_id"]
        }))

    async def message_read(self, event):
        """Handle read receipts"""
        await self.send(text_data=json.dumps({
            "type": "message_read",
            "message_id": event["message_id"],
            "reader_id": event["reader_id"],
            "reader_username": event["reader_username"],
            "group_id": event["group_id"]
        }))


class StatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if isinstance(self.user, AnonymousUser):
            await self.close(code=4001)  # Unauthenticated user
            return

        # Mark user as online in Redis with a timeout
        await self.set_user_status(self.user, True)

        # Add user to their own group for status notifications
        self.user_group = f"user_{self.user.id}"
        await self.channel_layer.group_add(self.user_group, self.channel_name)

        # Notify friends of online status
        await self.notify_friends(self.user, True)

        await self.accept()

    async def disconnect(self, close_code):
        if not hasattr(self, 'user') or isinstance(self.user, AnonymousUser):
            return

        # Mark user as offline in Redis
        await self.set_user_status(self.user, False)

        # Notify friends of offline status
        await self.notify_friends(self.user, False)

        # Remove from user group
        await self.channel_layer.group_discard(self.user_group, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if data.get("type") == "ping":
                # Handle heartbeat to keep connection alive
                await self.set_user_status(self.user, True)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Invalid JSON"}))

    async def status_update(self, event):
        """Send status update to the WebSocket client"""
        await self.send(text_data=json.dumps({
            "type": "status_update",
            "user_id": event["user_id"],
            "username": event["username"],
            "is_online": event["is_online"]
        }))

    @sync_to_async
    def set_user_status(self, user, is_online):
        """Store user status in Redis cache with a timeout"""
        cache.set(f"user_status_{user.id}", is_online, timeout=30)

    @sync_to_async
    def get_friends(self, user):
        """Fetch user's friends using the Friend model"""
        friends = Friend.objects.filter(
            Q(user=user) | Q(friend=user)
        ).select_related('user', 'friend')
        friend_ids = []
        for f in friends:
            friend_ids.append(f.friend.id if f.user == user else f.user.id)
        return friend_ids

    async def notify_friends(self, user, is_online):
        """Notify all friends of the user's status change"""
        friend_ids = await self.get_friends(user)
        for friend_id in friend_ids:
            await self.channel_layer.group_send(
                f"user_{friend_id}",
                {
                    "type": "status_update",
                    "user_id": user.id,
                    "username": user.username,
                    "is_online": is_online
                }
            )