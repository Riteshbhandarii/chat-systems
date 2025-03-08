# messaging/routing.py
from django.urls import re_path  
from . import consumers

# Defining URL pattern
websocket_urlpatterns = [
    # Connects with the ChatConsumer class to handle the WebSocket connection
    re_path(r'ws/messaging/(?P<chat_room>\w+)/$', consumers.ChatConsumer.as_asgi()),  # Room-based chat
]
