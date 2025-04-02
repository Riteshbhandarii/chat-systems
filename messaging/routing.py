# messaging/routing.py
from django.urls import re_path
from . import consumers

# Define a static URL for WebSocket connection
websocket_urlpatterns = [
    # Static path without room name
    re_path(r'ws/messaging/$', consumers.ChatConsumer.as_asgi()),  # Static WebSocket URL
]
