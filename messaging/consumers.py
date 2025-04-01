import json
from django.apps import apps
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection
import redis

# Redis connection, db = 0 using the default database for now
redis_connection = redis.Redis(host="localhost", port=6379, db=0)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Lazy load models to avoid app registry issues
        User = apps.get_model('auth', 'User')  # Load User model here
        Groupchat = apps.get_model('messaging', 'Groupchat')
        Message = apps.get_model('messaging', 'Message')
        Groupmchatmessage = apps.get_model('messaging', 'Groupmchatmessage')
        FriendRequest = apps.get_model('messaging', 'FriendRequest')  # Added FriendRequest model
        Friend = apps.get_model('messaging', 'Friend')  # Added Friend model

        room_name = self.scope["url_route"]["kwargs"]["chat_room"]
        
        if not self.scope["user"].is_authenticated:
            print("Unauthenticated user, Access denied.")
            raise DenyConnection("Log in to join the chat.")

        try:
            if room_name.startswith("group_"):
                group_chat = Groupchat.objects.get(name=room_name)
                if self.scope["user"] not in group_chat.members.all():
                    raise DenyConnection("Access denied, you are not authorized to join")
                await self.channel_layer.group_add(room_name, self.channel_name)

            else:
                user_ids = room_name.split("_")
                if int(user_ids[0]) != self.scope["user"].id and int(user_ids[1]) != self.scope["user"].id:
                    raise DenyConnection("Access denied, not authorized to join this private chat")
                
                receiver_id = int(user_ids[1]) if int(user_ids[0]) == self.scope["user"].id else int(user_ids[0])
                receiver = User.objects.get(id=receiver_id)

                await self.channel_layer.group_add(room_name, self.channel_name)
                redis_connection.sadd(f'room:{room_name}', self.scope["user"].id)

            # Log connection
            print(f"Authenticated user {self.scope['user'].username} connected to {room_name}")
            await self.accept()

        except Groupchat.DoesNotExist:
            print(f"Groupchat error: Room {room_name} does not exist")
            raise DenyConnection("Room does not exist")
        except User.DoesNotExist:
            print(f"User error: User not found")
            raise DenyConnection("User does not exist")

    async def receive(self, text_data):
        # Lazy load models to avoid app registry issues
        User = apps.get_model('auth', 'User')  # Load User model here
        Groupchat = apps.get_model('messaging', 'Groupchat')
        Message = apps.get_model('messaging', 'Message')
        Groupmchatmessage = apps.get_model('messaging', 'Groupmchatmessage')
        FriendRequest = apps.get_model('messaging', 'FriendRequest')  # Added FriendRequest model
        Friend = apps.get_model('messaging', 'Friend')  # Added Friend model

        message_data = json.loads(text_data)
        message = message_data["message"]
        room_name = self.scope["url_route"]["kwargs"]["chat_room"]

        try:
            if room_name.startswith("group_"):
                group_chat = Groupchat.objects.get(name=room_name)
                Groupmchatmessage.objects.create(
                    sender=self.scope["user"], 
                    content=message, 
                    group_chat=group_chat
                )
            elif message_data["message_type"] == "send_friend_request":  # New block for sending friend requests
                receiver_username = message_data["receiver"]
                receiver = User.objects.get(username=receiver_username)
                FriendRequest.objects.create(sender=self.scope["user"], receiver=receiver)
                await self.send(text_data=json.dumps({
                    'message': f"Friend request sent to {receiver_username}",
                    'type': 'friend_request'
                }))
            elif message_data["message_type"] == "accept_friend_request":  # New block for accepting friend requests
                friend_request_id = message_data["friend_request_id"]
                friend_request = FriendRequest.objects.get(id=friend_request_id)
                Friend.objects.create(user1=self.scope["user"], user2=friend_request.sender)
                Friend.objects.create(user1=friend_request.sender, user2=self.scope["user"])
                friend_request.delete()  # Remove the request after acceptance
                await self.send(text_data=json.dumps({
                    'message': f"You are now friends with {friend_request.sender.username}",
                    'type': 'friend_accepted'
                }))
            else:  # Normal chat message flow
                user_ids = room_name.split("_")
                receiver_id = int(user_ids[1]) if int(user_ids[0]) == self.scope["user"].id else int(user_ids[0])
                receiver = User.objects.get(id=receiver_id)
                Message.objects.create(
                    sender=self.scope["user"], 
                    content=message, 
                    receiver=receiver
                )

            # Acknowledge the message reception
            await self.send(text_data=json.dumps({
                'message': 'Message received!'
            }))

            # Broadcast the message to all users in the room
            await self.channel_layer.group_send(
                room_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': self.scope["user"].username
                }
            )

        except Groupchat.DoesNotExist:
            print(f"Group chat {room_name} does not exist")
        except User.DoesNotExist:
            print(f"Receiver user for {room_name} does not exist")

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))

    async def disconnect(self, close_code):
        room_name = self.scope["url_route"]["kwargs"]["chat_room"]
        await self.channel_layer.group_discard(room_name, self.channel_name)
        print(f"WebSocket disconnected from {room_name}")
