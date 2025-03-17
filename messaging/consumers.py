import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection
from .models import Groupchat, Message
from django.contrib.auth.models import User
from channels.exceptions import DenyConnection
import redis

# redis connection, db = 0 using default database for now
redis_connection = redis.Redis(host = "localhost", port = 6379, db =0)

class ChatConsumer(AsyncWebsocketConsumer):
    # async handles multiple tasks at the same time
    async def connect(self):
        # checks to identify which chat room the websocket connection belongs to
        room_name = self.scope["url_route"]["kwargs"]["chat_room"]
        # checking the authentication
        if self.scope["user"].is_authenticated:
            try:
                # checking if the group name starts with "group"
                if room_name.startswith("group_"):
                    group_chat = Groupchat.objects.get(name=room_name)
                    # checking for authorization
                    if self.scope["user"] not in group_chat.members.all():
                        raise DenyConnection("Access denied, you are not authorized to join")
                    # adding user to group
                    await self.channel_layer.group_add(room_name, self.channel_name)

                else:
                    # splits room_name into two parts using underscore, for one-on-one room
                    user_ids = room_name.split("_")
                    # checks if the current user is not one of the two users in the private chat room
                    if int(user_ids[0]) != self.scope["user"].id and int(user_ids[1]) != self.scope["user"].id:
                        raise DenyConnection("Access denied, not authorized to join this private chat")

                    # Fetch the receiver based on the room_name logic
                    receiver_id = int(user_ids[1]) if int(user_ids[0]) == self.scope["user"].id else int(user_ids[0])
                    receiver = User.objects.get(id=receiver_id)

                    # Adding user to private chat room
                    await self.channel_layer.group_add(room_name, self.channel_name)
                    

                    # track users in room 
                    redis_connection.sadd(f'room:{room_name}', self.scope["user"].id)
                    if room_name.startswith("group_"):
                        print(f"Autheticated user {self.scope["user"].username} connected to group {room_name}")
                    else:
                          print(f"Authenticated user {self.scope['user'].username} connected to private chat {room_name}")
                    
                    await self.accept()

            except Groupchat.DoesNotExist:
                raise DenyConnection("Room does not exist")
            
        else:
            print("Unauthenticated user, Access denied.")
            raise DenyConnection("Log in to join the chat.")


    async def receive(self, text_data):
        # recieving the message sent by the user
        message = json.loads(text_data)["message"]
        room_name = self.scope["url_route"]["kwargs"]["chat_room"]

        # saving the message for groupchat to the database
        if room_name.startswith("group_"):
            group_chat = Groupchat.objects.get(name= room_name )
            Message.objects.create(sender = self.scope["user"], content = message, group = group_chat)
       #  saving the message for one on one chat to database
        else:
             user_ids = room_name.split("_")
             receiver_id = int(user_ids[1]) if int(user_ids[0]) == self.scope["user"].id else int(user_ids[0])
             receiver = User.objects.get(id=receiver_id)

             
              # save the message to the database
             Message.objects.create(sender = self.scope["user"], content = message, receiver = receiver)
       
        
     # Respond back with a simple acknowledgment message
        await self.send(text_data=json.dumps({
    'message': 'Message received!'
}))

# Broadcasting the message to all users in the room
        await self.channel_layer.group_send(
    room_name,
    {
        'type': 'chat_message',
        'message': message,
        'sender': self.scope["user"].username
    }
)

    async def disconnect(self, close_code):
        room_name = self.scope["url_route"]["kwargs"]["chat_room"]
        await self.channel_layer.group_discard(room_name, self.channel_name)
        print("WebSocket disconnected")

class DenyConnection(Exception):
    pass